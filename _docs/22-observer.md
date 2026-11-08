---
title: "Observer"
order: 22
layout: tutorial
sectionid: docs
part: "coordinating-traversing"
description: "An Observer is a callable, but the delivery contract is still a design: subscription order, failure isolation, events published during delivery, and how long a signal keeps a subscriber alive."
---

## Learning objectives

By the end of this chapter you can:

- Say which part of Observer Python removes, the interface, and which part survives, the delivery contract and subscriber lifetime.
- Write a typed `Signal` that delivers in subscription order and raises one `ExceptionGroup` after every subscriber has run.
- Deliver safely when a subscriber subscribes, unsubscribes or publishes during delivery.
- Hold bound methods weakly and functions and lambdas strongly, and say what a lambda, a reference cycle and a slotted class do to that choice.
- Name what mypy checks in a signal and what it can't.

## Why this matters

A tracking system has one source of truth, the handling events that arrive as cargo moves, and several parties that want to hear about them: a history per consignment, a customer notification, a billing trigger. The handling code shouldn't name any of them, and a new party shouldn't mean an edit to it. A list of callables does that, and fails three ways:

- A subscriber that writes to a history store raises because the store is down. Later subscribers don't hear the event, and the caller sees only the store's error.
- A `TrackingHistory` the application has finished with is still in the list. It stays alive and keeps being called.
- A subscriber reacts to `CLEARED` by publishing `DELIVERED`. The history, registered after it, records `DELIVERED` first and `CLEARED` second.

{% include excalidraw.html name="22-observer" described="true" caption="Figure 22.1: What a signal decides. Each event reaches a snapshot of subscribers in order, nested events wait their turn, failures are gathered and raised afterwards, and bound methods are held weakly so abandoned subscribers can go." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-22-observer" markdown="1">
From the top: an accent box, `Signal.publish(event)`, is labelled "queued: nested events wait their turn" and points to `subscribers`, "a snapshot, in subscription order". That box fans out to three: `TrackingHistory.record` ("bound method: held through WeakMethod"), `lambda` ("held strongly") and "a failing subscriber" ("error collected, delivery continues"). Only the failing subscriber has an arrow to `ExceptionGroup`, "raised after every subscriber has run"; the other two run to completion and add nothing to it. Below sits a muted, dashed box, "plain list", with "stops at a failure, keeps every subscriber alive".
</div>
</details>

The figure shows the four decisions a signal makes about each event.

## Pattern: Observer

### The problem

The subject must tell an open set of parties about each event without being coupled to what those parties are. Then it has to decide who hears first, what one failure costs the others, what happens when a subscriber calls back into the subject, and how long a subscriber lives.

### The solution

An **Observer** lets a subject keep a list of interested parties and tell each of them when something happens, without knowing what they are.

**Bucket: survives.** The interface dissolves into a callable, and the delivery contract remains: a list of callables decides nothing about order, failure, re-entry or lifetime, and `Signal` decides each.

In *Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994), the parties implement an observer interface with an update method. [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts the pattern.

### How Python models it

Anything that takes the event is a subscriber:

```python
type Subscriber[E] = Callable[[E], None]
type Unsubscribe = Callable[[], None]
```

A function, a lambda and a bound method all fit. The event is one class, `HandlingEvent`, with a `HandlingKind` enum. mypy checks both ends:

```text
<string>:10: error: Argument 1 to "subscribe" of "Signal" has incompatible type "Callable[[str], None]"; expected "Callable[[HandlingEvent], None]"  [arg-type]
<string>:6: error: Argument 1 to "publish" of "Signal" has incompatible type "str"; expected "HandlingEvent"  [arg-type]
```

A bus keyed by topic strings with `Any` payloads gives that up: mypy accepts a misspelled topic and a payload of `42` for a handler that expects a dictionary. A signal per event source has no topic to misspell. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers callback Protocols for subscribers that need more than a call.

### Order and failure

The comparison form is the list a first draft would use:

```python
# Comparison: a plain list of callables, iterated live, with no `try` around the calls.
class _ListSignal:
    def __init__(self) -> None:
        self._subscribers: list[Subscriber[HandlingEvent]] = []

    def subscribe(self, subscriber: Subscriber[HandlingEvent], /) -> Unsubscribe:
        self._subscribers.append(subscriber)

        def remove() -> None:
            self._subscribers.remove(subscriber)

        return remove

    def publish(self, event: HandlingEvent, /) -> None:
        for subscriber in self._subscribers:
            subscriber(event)
```

It delivers in subscription order and unsubscribes correctly. A store that raises between two subscribers stops it: the error reaches the caller and the later subscriber isn't called. `Signal` delivers to each subscriber and reports afterwards:

<!-- fmt:off -->
```python
    def publish(self, event: E, /) -> None:
        """Deliver the event to every subscriber, then raise one group for the failures.

        An event published during delivery waits in a queue, so every subscriber sees events in
        publication order. Each event goes to a snapshot of the subscribers.
        """
        self._pending.append(event)
        if self._delivering:
            return
        self._delivering = True
        errors: list[Exception] = []
        try:
            while self._pending:
                current = self._pending.popleft()
                for reference in tuple(self._subscribers.values()):
                    subscriber = reference()
                    if subscriber is None:
                        continue
                    try:
                        subscriber(current)
                    except Exception as error:
                        errors.append(error)
        finally:
            self._delivering = False
        if errors:
            raise ExceptionGroup("subscribers failed", errors)
```
<!-- fmt:on -->

[PEP 654](https://peps.python.org/pep-0654/), by Irit Katriel, Yury Selivanov and Guido van Rossum, introduces exception groups to "allow programs to raise and handle multiple unrelated exceptions simultaneously". A store that's down and a notifier that times out are unrelated. The group's `exceptions` tuple holds the errors in order. Raising after delivery moves the decision to the caller, which can log or retry; the signal doesn't undo what earlier subscribers did.

- **Duplicates.** The registry is a `dict` keyed by the callable, or by its `WeakMethod` for a bound method, and `setdefault` keeps the first entry, so subscribing twice delivers once.
- **`BaseException`.** `except Exception` doesn't collect it. It propagates, and the `finally` resets the delivering flag so the next event is delivered.

### How long a subscriber lives

A signal holds its subscribers, and holding something decides how long it lives. The plain list keeps an abandoned `TrackingHistory` alive and still called. `Signal` drops it once the application lets go:

<!-- fmt:off -->
```python
    def subscribe(self, subscriber: Subscriber[E], /) -> Unsubscribe:
        """Add a subscriber and return the call that removes it.

        A bound method is held through `weakref.WeakMethod`, so the signal does not keep its
        owner alive. Every other callable is held strongly. A duplicate is ignored.
        """
        key: object
        if inspect.ismethod(subscriber):
            method = weakref.WeakMethod(subscriber, self._forget)
            key = method
            reference: Callable[[], Subscriber[E] | None] = method
        else:
            key = subscriber
            reference = _strong(subscriber)
        self._subscribers.setdefault(key, reference)

        def unsubscribe() -> None:
            self._forget(key)

        return unsubscribe
```
<!-- fmt:on -->

A bound method is a temporary object made on each attribute access, so a plain weak reference to `history.record` is dead at once. The [`weakref` documentation](https://docs.python.org/3/library/weakref.html): "Since a bound method is ephemeral, a standard weak reference cannot keep hold of it." `WeakMethod` "has special code to recreate the bound method until either the object or the original function dies", and its callback, `_forget`, removes the entry when the owner goes.

Functions and lambdas are held strongly. A run on Python 3.15.2 of `weakref.ref(lambda: None)()` returns `None`: nothing else holds the lambda, so a signal holding it weakly would drop an inline lambda before its first event.

| Subscriber | Outcome |
| --- | --- |
| `history.record`, history still named | delivered |
| `history.record`, last name deleted | dropped after collection; `len(signal)` is 0 |
| `TrackingHistory().record`, nobody holds the owner | dropped; the caller must keep the owner |
| `lambda e: history.record(e)` | held strongly, and so is the history |
| owner with `__slots__` and no `__weakref__` | `TypeError` "cannot create weak reference"; mypy accepts it |
| owner in a reference cycle | stays until `gc.collect()` runs |

The `weakref` documentation states the slots rule: "When `__slots__` are defined for a given type, weak reference support is disabled unless a `'__weakref__'` string is also present". [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers `weakref_slot=True`. Unsubscribing after the owner has gone is safe, twice over.

The cycle is why collection is explicit before asserting. The data model says "Do not depend on immediate finalization of objects when they become unreachable", and CPython's reference counting "is not guaranteed to collect garbage containing circular references". The [`gc` documentation](https://docs.python.org/3/library/gc.html) adds: "Since the collector supplements the reference counting already used in Python, you can disable the collector if you are sure your program does not create reference cycles."

### Subscribing and publishing during delivery

A subscriber can add a subscriber, remove itself or publish, while the signal is iterating. Two rules cover it.

**Delivery iterates a snapshot**, `tuple(self._subscribers.values())`:

- A subscriber added during delivery gets the next event, not the current one.
- A subscriber that removes itself skips no one: remover, a, b. The plain list, removing from the list it walks, gives remover, b, and `a` is never told.
- The snapshot holds the `WeakMethod`, so a subscriber whose owner dies mid-delivery is skipped, not called.

**An event published during delivery waits.** `publish` appends to a queue, a nested call returns at once, and the outer call drains the queue. With a releaser that publishes `DELIVERED` on `CLEARED`, registered before the history, `Signal` leaves the history reading `CLEARED`, `DELIVERED`. The plain list delivers the nested event immediately: `DELIVERED`, `CLEARED`. Subscribers see events in publication order, and a subscriber that publishes can't reorder what later ones see.

`Signal` is single-threaded and says so in its module docstring.

## When not to use it

- **Observer.** Call the parties directly when the set is fixed at the time the subject is built. A tuple of callables is enough. With one subscriber, pass a callable. If the parties must reply to each other, so that who acts depends on what the others did, a mediator decides. If delivery has to survive a crash, use a durable queue: an in-memory signal's subscribers and queue vanish with the process.

<blockquote class="ai-sidebar" markdown="1">
**Specifying an observer.** "An event system" leaves open how a subscriber is typed, what a failing subscriber does to the rest, and who keeps a subscriber alive. Paste a prompt that states the contract:

> Write a generic `Signal[E]` with `subscribe(subscriber) -> Unsubscribe`, where a subscriber is a typed callable and not a base class. Deliver in subscription order over a snapshot. Run every subscriber, then raise one `ExceptionGroup` for the failures. Queue events published during delivery. Hold bound methods through `weakref.WeakMethod` and functions and lambdas strongly. Say in the docstring that it is single-threaded.

If the reply holds every bound method strongly or iterates the live list, ask for the check that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/22-observer
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 31 cases pass and mypy is clean. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers how the mypy checks are built. Two experiments, each in a fresh scratch copy:

- **Iterate the live dict.** In `Signal.publish`, change `tuple(self._subscribers.values())` to `self._subscribers.values()`. Three cases fail with `RuntimeError: dictionary changed size during iteration`: adding a subscriber, removing one, and an owner dying mid-delivery, whose callback also changes the dict. mypy is clean: a live view is a valid iterable.
- **Hold every subscriber strongly.** Replace the `inspect.ismethod` branch of `subscribe` with `key: object = subscriber` and `reference = _strong(subscriber)`. Six lifetime cases fail: nothing is dropped, the cyclic history survives collection, and the slotted owner is accepted (`DID NOT RAISE TypeError`). mypy is clean again.

## What you can do now

- Type a subscriber as `Subscriber[E]`, a callable, and let `Signal` own the delivery contract.
- Deliver in subscription order and raise one `ExceptionGroup` after every subscriber has run.
- Iterate a snapshot and queue nested events, so subscribing, unsubscribing and publishing during delivery are safe.
- Hold bound methods through `WeakMethod` and functions and lambdas strongly, and know what a closing lambda, a cycle and a slotted owner do.
- Rely on mypy for the event type at both ends, not for a string topic or a slotted owner.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Observer. The [`weakref` documentation](https://docs.python.org/3/library/weakref.html) covers `ref`, `WeakMethod` and the `__slots__` note, the [`gc` documentation](https://docs.python.org/3/library/gc.html) covers `collect` and `disable`, and the [data model](https://docs.python.org/3/reference/datamodel.html) covers object lifetime. [PEP 654](https://peps.python.org/pep-0654/) specifies exception groups, and the [built-in exceptions documentation](https://docs.python.org/3/builtins/exceptions.html) covers `ExceptionGroup` and its `exceptions` attribute. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
