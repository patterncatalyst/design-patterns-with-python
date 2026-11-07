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

A tracking system has one source of truth, the handling events that arrive as cargo moves, and several parties that want to hear about them: a history per consignment, a customer notification, a billing trigger. The handling code shouldn't name any of them, and a new party shouldn't mean an edit to it. That's the force behind Observer, and a Python list of callables resolves it without an interface. Three things go wrong in the obvious version.

A subscriber that writes to a history store raises because the store is down. The subscribers registered after it don't hear the event, and the caller of `publish` sees the store's error and nothing else.

A `TrackingHistory` the application has finished with is still in the subscriber list. It stays alive and keeps being called.

A subscriber reacts to `CLEARED` by publishing `DELIVERED`. The history is registered after it, so it records `DELIVERED` first and `CLEARED` second.

The fix for each is a decision about delivery, and Observer survives because those decisions remain after the interface is gone.

{% include excalidraw.html name="22-observer" caption="Figure 22.1: What a signal decides. Each event reaches a snapshot of subscribers in order, nested events wait their turn, failures are gathered and raised afterwards, and bound methods are held weakly so abandoned subscribers can go." %}

Read the figure from the top down. An accent box, `Signal.publish(event)`, is labelled "queued: nested events wait their turn" and points to `subscribers`, "a snapshot, in subscription order". That box fans out to three: `TrackingHistory.record` ("bound method: held through WeakMethod"), `lambda` ("held strongly") and "a failing subscriber" ("error collected, delivery continues"). Only the failing subscriber has an arrow to `ExceptionGroup`, "raised after every subscriber has run"; the other two run to completion and add nothing to it. Below sits a muted, dashed box, "plain list", with "stops at a failure, keeps every subscriber alive".

## A subscriber is a callable

The *Design Patterns* catalogue by Gamma, Helm, Johnson and Vlissides (1994) gives Observer to a subject whose changes other parties care about and which mustn't be coupled to what those parties are. The subject keeps a list of interested parties and tells each of them when something happens. In that book the parties implement an observer interface with an update method.

Python removes the interface. Anything that takes the event is a subscriber, and the type says so:

```python
type Subscriber[E] = Callable[[E], None]
type Unsubscribe = Callable[[], None]
```

`Subscriber[E]` is a callable from an event of type `E` to nothing, and `Unsubscribe` is the call that removes one. A function, a lambda and a bound method all fit. `test_mypy_refuses_a_subscriber_for_another_event_type` passes a function typed for `str` to a `Signal[HandlingEvent]` and `test_mypy_refuses_publishing_the_wrong_event` publishes a `str`. Both run through the test's own helper and print:

```text
<string>:10: error: Argument 1 to "subscribe" of "Signal" has incompatible type "Callable[[str], None]"; expected "Callable[[HandlingEvent], None]"  [arg-type]
<string>:6: error: Argument 1 to "publish" of "Signal" has incompatible type "str"; expected "HandlingEvent"  [arg-type]
```

The event is one class, `HandlingEvent`, with a `HandlingKind` enum for what happened. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers callback Protocols for subscribers that need more than a call.

A bus keyed by strings gives up that check. `test_mypy_accepts_a_typo_in_a_string_topic_bus` runs a reduced model, a bus keyed by topic strings with `Any` payloads, which isn't part of the example. mypy exits 0 with empty output on a publish to a misspelled topic and on a payload of `42` to a handler that expects a dictionary. A signal per event source has no topic string to misspell, and a wrong payload is an error.

The bucket is survives, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it. The interface dissolves into a callable. A list of callables decides nothing about delivery order, failure, re-entry or lifetime, and `Signal` decides each.

## Order and failure

Order and failure are the first two decisions a list of callables leaves open: who hears an event first, and whether one subscriber that raises costs the others the event. The comparison form is the list a first draft would use, written as a test fixture so it runs the same delivery table as `Signal`:

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

Both forms pass `test_subscribers_are_called_in_subscription_order` and `test_an_unsubscribed_subscriber_gets_no_more_events`. They part at failure. `test_a_plain_list_stops_at_the_first_failing_subscriber` has a store that raises between two labelled subscribers: the error reaches the caller and the later subscriber isn't called. `Signal` delivers to each subscriber and reports afterwards:

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

[PEP 654](https://peps.python.org/pep-0654/), by Irit Katriel, Yury Selivanov and Guido van Rossum, introduces the type to "allow programs to raise and handle multiple unrelated exceptions simultaneously", and subscriber failures fit that description: the store being down and the notifier timing out have no relation to each other. `test_one_failing_subscriber_does_not_stop_the_rest` checks that the subscribers before and after the failure both ran and that the group holds one `RuntimeError`. `test_every_failure_is_reported_after_delivery` runs one failure and two, and the group's `exceptions` tuple equals the errors in order.

Raising after delivery moves the decision to the caller. It can log the group or retry, and the other subscribers have already done their work. The signal doesn't undo what earlier subscribers did.

Two smaller rules sit in the same method. Subscribing a function twice delivers once, and so does subscribing the same bound method twice, because the registry is a `dict` keyed by the callable, or by its `WeakMethod` for a bound method, and `setdefault` keeps the first entry (`test_subscribing_twice_delivers_once`). The `except Exception` clause doesn't collect a `BaseException` subclass. One raised by a subscriber leaves the loop and propagates, and the `finally` resets the delivering flag. `test_the_signal_accepts_new_events_after_an_interrupted_delivery` is the one test that witnesses that `finally`: an ordinary failure is caught inside the loop, so `test_the_signal_accepts_new_events_after_a_failed_delivery` passes with or without it. After the interrupted delivery the next event reaches the history and the interrupted one doesn't.

`TrackingHistory` is the ordinary subscriber, a plain class whose `record` method appends. `test_tracking_history_records_events_in_order` publishes booked, loaded and departed, and the history holds them in that order.

## How long a subscriber lives

A signal holds its subscribers, and holding something decides how long it lives. The plain list holds each subscriber until it is removed. A test makes the cost visible, then the `Signal` behaves differently:

```python
def test_a_bound_method_subscriber_is_dropped_when_its_owner_goes(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    history = TrackingHistory()
    signal.subscribe(history.record)
    history_ref = weakref.ref(history)
    assert len(signal) == 1
    del history

    gc.collect()

    assert history_ref() is None
    assert len(signal) == 0
    signal.publish(event(HandlingKind.LOADED))  # reaches no one, and raises nothing
```

`del history` removes the application's name for the history. The test collects before asserting because the language doesn't promise immediate reclamation; the reference-cycle case below shows why. In the plain list the same sequence leaves the history alive and still called: `test_a_plain_list_keeps_an_abandoned_subscriber_alive` finds the object through its weak reference and publishes to it. In `Signal` the history is gone, and `len(signal)`, the number of entries, is 0.

The rule is in `subscribe`:

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

The `weakref` documentation explains why a plain weak reference won't do: "A weak reference to an object is not enough to keep the object alive: when the only remaining references to a referent are weak references, garbage collection is free to destroy the referent and reuse its memory for something else." A bound method is a temporary object made on each attribute access, so a plain weak reference to `history.record` is dead at once. The documentation says of `WeakMethod`: "Since a bound method is ephemeral, a standard weak reference cannot keep hold of it." `WeakMethod` "has special code to recreate the bound method until either the object or the original function dies". When the owner goes, its callback, `_forget`, removes the entry.

A function or a lambda is the opposite case. A run on Python 3.15.2 of `weakref.ref(lambda: None)()` returns `None`: nothing else holds the lambda, so it is gone before the call. A signal that held lambdas weakly would drop an inline lambda before its first event. So they are held strongly, and `test_a_lambda_subscriber_is_held_strongly` checks that the lambda is still called after a collection.

Strong and weak have trade-offs, and each has a test:

- A bound method whose owner nobody else holds is dropped. `signal.subscribe(TrackingHistory().record)` leaves the signal empty after a collection (`test_a_subscriber_nobody_else_holds_is_dropped`). The caller keeps the object that owns the method.
- A lambda that closes over its owner keeps the owner alive. `lambda e: history.record(e)` is held strongly, so the history is too (`test_a_lambda_that_closes_over_its_owner_keeps_it_alive`). Subscribing the bound method is the form that lets the history go.
- An owner with `__slots__` and no weak-reference slot is refused when it subscribes. The documentation says "When `__slots__` are defined for a given type, weak reference support is disabled unless a `'__weakref__'` string is also present in the sequence of strings in the `__slots__` declaration." `test_a_slotted_subscriber_without_a_weakref_slot_is_refused` finds a `TypeError` matching "cannot create weak reference" and a signal with no entries. mypy sees nothing: `test_mypy_cannot_see_a_subscriber_that_refuses_weak_references` runs the same subscription and gets exit status 0. The slotted-dataclass version of this finding, and `weakref_slot=True`, belong to [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}).
- A subscriber in a reference cycle outlives its last name. `test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs` subscribes a history that refers to itself, with automatic collection paused. The weak reference is still live and the signal still has an entry until `gc.collect()` runs, then both are gone.

The cycle case is the reason the tests collect explicitly. The data model says "Do not depend on immediate finalization of objects when they become unreachable", and CPython's reference counting "collects most objects as soon as they become unreachable, but is not guaranteed to collect garbage containing circular references". The `gc` documentation adds: "Since the collector supplements the reference counting already used in Python, you can disable the collector if you are sure your program does not create reference cycles." The entry stays until the collector reaches the cycle. Unsubscribing is safe after the owner has gone: `test_unsubscribe_is_safe_after_the_owner_has_gone` calls it twice without an error.

## Subscribing and publishing during delivery

A subscriber is code, and code can call back into the signal. A subscriber may add another subscriber, remove itself, or publish a new event, and the list or dict being iterated changes under the loop. The contract has two rules.

The first is that delivery iterates a snapshot, `tuple(self._subscribers.values())`, as the `publish` excerpt shows. A subscriber added during delivery gets the next event and not the current one (`test_a_subscriber_added_during_delivery_gets_the_next_event`). A subscriber that removes itself skips no one: the log reads remover, a, b (`test_unsubscribing_during_delivery_does_not_skip_another_subscriber`). The plain list removes an item from the list it is walking, and the log reads remover, b, so `a` was never told (`test_a_plain_list_skips_a_subscriber_when_one_unsubscribes_during_delivery`). The snapshot holds the `WeakMethod` for a bound method, not the method, so a subscriber whose owner dies mid-delivery is skipped, not called. `test_a_subscriber_that_dies_during_delivery_is_skipped` has one subscriber release the owner of the next and collect; the test then finds that the next subscriber's `record` was never called.

The second is that an event published during delivery waits. `publish` appends to a queue, and a nested call returns at once when delivery is already running; the outer call drains the queue after the current event. The test builds the failure from the start of the chapter:

<!-- fmt:off -->
```python
def _history_behind_a_releaser(form: _Form, event: MakeEvent) -> TrackingHistory:
    """A releaser that publishes DELIVERED when it sees CLEARED, then a history, in that order."""

    def releaser(received: HandlingEvent, /) -> None:
        if received.kind is HandlingKind.CLEARED:
            form.publish(event(HandlingKind.DELIVERED))

    history = TrackingHistory()
    form.subscribe(releaser)
    form.subscribe(history.record)
    return history
```
<!-- fmt:on -->

Publishing `CLEARED` through `Signal` leaves the history reading `CLEARED`, `DELIVERED` (`test_an_event_published_during_delivery_waits_its_turn`). The plain list delivers the nested event immediately, and the history reads `DELIVERED`, `CLEARED` (`test_an_immediately_delivered_nested_event_arrives_out_of_order`). Subscribers see events in publication order, and a subscriber that publishes can't reorder what later ones see.

`Signal` is single-threaded: it assumes one caller at a time and says so in its module docstring. Publishing from several threads is outside this chapter.

## When not to use it

Call the parties directly when the set is fixed at the time the subject is built. A tuple of callables is enough, and a signal's subscribe and unsubscribe are machinery nobody uses. With one subscriber, pass a callable. If the parties must reply to each other, so that who acts depends on what the others did, a mediator decides, and an observer can't. If delivery has to survive a crash, an in-memory signal isn't the tool: the subscribers and the queue vanish with the process, and a durable queue is.

<blockquote class="ai-sidebar" markdown="1">
**Reviewing assistant-written observers.** Asked for "an event system", an assistant may write an `Observer` base class with `update`, a bus keyed by strings, or a callback list that stops at the first failure and keeps abandoned subscribers alive. Paste a prompt that states the contract:

> Write a generic `Signal[E]` with `subscribe(subscriber) -> Unsubscribe`, where a subscriber is a typed callable and not a base class. Deliver in subscription order over a snapshot. Run every subscriber, then raise one `ExceptionGroup` for the failures. Queue events published during delivery. Hold bound methods through `weakref.WeakMethod` and functions and lambdas strongly. Say in the docstring that it is single-threaded.

If the reply holds every bound method strongly or iterates the live list, ask it to add the test that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/22-observer
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 31 items

tests/test_delivery.py::test_subscribers_are_called_in_subscription_order[signal] PASSED [  3%]
tests/test_delivery.py::test_subscribers_are_called_in_subscription_order[plain-list] PASSED [  6%]
tests/test_delivery.py::test_an_unsubscribed_subscriber_gets_no_more_events[signal] PASSED [  9%]
tests/test_delivery.py::test_an_unsubscribed_subscriber_gets_no_more_events[plain-list] PASSED [ 12%]
tests/test_delivery.py::test_subscribing_twice_delivers_once PASSED      [ 16%]
tests/test_delivery.py::test_one_failing_subscriber_does_not_stop_the_rest PASSED [ 19%]
tests/test_delivery.py::test_a_plain_list_stops_at_the_first_failing_subscriber PASSED [ 22%]
tests/test_delivery.py::test_every_failure_is_reported_after_delivery[one] PASSED [ 25%]
tests/test_delivery.py::test_every_failure_is_reported_after_delivery[two] PASSED [ 29%]
tests/test_delivery.py::test_tracking_history_records_events_in_order PASSED [ 32%]
tests/test_delivery.py::test_the_signal_accepts_new_events_after_a_failed_delivery PASSED [ 35%]
tests/test_delivery.py::test_the_signal_accepts_new_events_after_an_interrupted_delivery PASSED [ 38%]
tests/test_lifetime.py::test_a_plain_list_keeps_an_abandoned_subscriber_alive PASSED [ 41%]
tests/test_lifetime.py::test_a_bound_method_subscriber_is_dropped_when_its_owner_goes PASSED [ 45%]
tests/test_lifetime.py::test_a_subscriber_nobody_else_holds_is_dropped PASSED [ 48%]
tests/test_lifetime.py::test_a_lambda_subscriber_is_held_strongly PASSED [ 51%]
tests/test_lifetime.py::test_a_lambda_that_closes_over_its_owner_keeps_it_alive PASSED [ 54%]
tests/test_lifetime.py::test_a_slotted_subscriber_without_a_weakref_slot_is_refused PASSED [ 58%]
tests/test_lifetime.py::test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs PASSED [ 61%]
tests/test_lifetime.py::test_a_subscriber_that_dies_during_delivery_is_skipped PASSED [ 64%]
tests/test_lifetime.py::test_unsubscribe_is_safe_after_the_owner_has_gone PASSED [ 67%]
tests/test_reentrancy.py::test_a_subscriber_added_during_delivery_gets_the_next_event PASSED [ 70%]
tests/test_reentrancy.py::test_unsubscribing_during_delivery_does_not_skip_another_subscriber PASSED [ 74%]
tests/test_reentrancy.py::test_a_plain_list_skips_a_subscriber_when_one_unsubscribes_during_delivery PASSED [ 77%]
tests/test_reentrancy.py::test_an_event_published_during_delivery_waits_its_turn PASSED [ 80%]
tests/test_reentrancy.py::test_an_immediately_delivered_nested_event_arrives_out_of_order PASSED [ 83%]
tests/test_static.py::test_mypy_refuses_a_subscriber_for_another_event_type PASSED [ 87%]
tests/test_static.py::test_mypy_refuses_publishing_the_wrong_event PASSED [ 90%]
tests/test_static.py::test_mypy_accepts_a_typo_in_a_string_topic_bus[typo-topic] PASSED [ 93%]
tests/test_static.py::test_mypy_accepts_a_typo_in_a_string_topic_bus[wrong-payload] PASSED [ 96%]
tests/test_static.py::test_mypy_cannot_see_a_subscriber_that_refuses_weak_references PASSED [100%]

============================== 31 passed in 2.27s ==============================
Success: no issues found in 9 source files
```

The suite has 27 test functions and 31 cases. The delivery, lifetime and re-entrancy tests run on `Signal` and the plain list; `test_static.py` holds the mypy witnesses. For how the tests and the mypy witnesses are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: iterate the live dict.** In a scratch copy, change `for reference in tuple(self._subscribers.values()):` in `Signal.publish` to `for reference in self._subscribers.values():`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E +RuntimeError|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` gives:

```text
E               RuntimeError: dictionary changed size during iteration
E               RuntimeError: dictionary changed size during iteration
E               RuntimeError: dictionary changed size during iteration
FAILED tests/test_lifetime.py::test_a_subscriber_that_dies_during_delivery_is_skipped
FAILED tests/test_reentrancy.py::test_a_subscriber_added_during_delivery_gets_the_next_event
FAILED tests/test_reentrancy.py::test_unsubscribing_during_delivery_does_not_skip_another_subscriber
3 failed, 28 passed in 2.41s
Success: no issues found in 9 source files
```

A subscriber that adds an entry to the dict being walked changes its size, and Python raises. The self-removing subscriber fails the same way. So does the test where the owner dies during delivery, because the callback that removes a dead bound method also changes the dict mid-loop. mypy stays green: a live view is a valid iterable.

**Experiment two: hold every subscriber strongly.** In a fresh scratch copy, replace the `inspect.ismethod` branch of `subscribe` with `key: object = subscriber` and `reference = _strong(subscriber)`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E +Failed|[0-9]+ (passed|failed))'` and then mypy gives:

```text
E       Failed: DID NOT RAISE TypeError
FAILED tests/test_lifetime.py::test_a_bound_method_subscriber_is_dropped_when_its_owner_goes
FAILED tests/test_lifetime.py::test_a_subscriber_nobody_else_holds_is_dropped
FAILED tests/test_lifetime.py::test_a_slotted_subscriber_without_a_weakref_slot_is_refused
FAILED tests/test_lifetime.py::test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs
FAILED tests/test_lifetime.py::test_a_subscriber_that_dies_during_delivery_is_skipped
FAILED tests/test_lifetime.py::test_unsubscribe_is_safe_after_the_owner_has_gone
6 failed, 25 passed in 2.45s
Success: no issues found in 9 source files
```

Nothing is dropped, so the history survives its last name, the entry count stays at 1, and the cyclic history survives the collection. The slotted owner is accepted, so the expected `TypeError` never comes (`DID NOT RAISE TypeError`). mypy reports success again, because holding a subscriber strongly is type-correct.

## What you can do now

- State what survives of Observer: `Signal` and its docstring decide order, failure, re-entrancy and lifetime, and the interface is an alias, `Subscriber`.
- Deliver in order and survive a failure: `publish` and the `ExceptionGroup` it raises, witnessed against the plain list by `test_a_plain_list_stops_at_the_first_failing_subscriber`.
- Subscribe and publish during delivery: the snapshot and the queue, witnessed by the five re-entrancy tests and experiment one.
- Choose weak or strong: `subscribe` with `WeakMethod` for bound methods, witnessed by the lifetime tests and experiment two.
- Know what mypy checks: a subscriber's event type and the published event, and not a typo in a string topic or a slotted owner.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Observer. The [`weakref` documentation](https://docs.python.org/3/library/weakref.html) covers `ref`, `WeakMethod` and the `__slots__` note, the [`gc` documentation](https://docs.python.org/3/library/gc.html) covers `collect` and `disable`, and the [data model](https://docs.python.org/3/reference/datamodel.html) covers object lifetime. [PEP 654](https://peps.python.org/pep-0654/) specifies exception groups, and the [built-in exceptions documentation](https://docs.python.org/3/library/exceptions.html) covers `ExceptionGroup` and its `exceptions` attribute. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
