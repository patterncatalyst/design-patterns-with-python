---
title: "Visitor, Memento, and Interpreter"
order: 25
layout: tutorial
sectionid: docs
part: "coordinating-traversing"
description: "Visitor dissolves into a match over a closed union, while a snapshot and a tariff tree stay design: what to capture, what mustn't roll back, and the readings of one grammar."
---

## Learning objectives

By the end of this chapter you can:

- Choose between a `match` over a closed union and `singledispatch` over an open set of kinds.
- Say what an `accept` method costs, and what it catches that a `match` also catches.
- Snapshot a booking and roll back a failed batch of amendments with a context manager.
- Decide what a memento captures and what must not roll back.
- Write a tariff as a tree of frozen nodes, then evaluate it and explain it.

## Why this matters

A tracking feed carries five kinds of handling event, and several operations run over them. A booking is amended in batches, and a batch that fails halfway has to leave the booking as it was. A pricing team writes tariff rules that the system must price and also read back to a customer. Visitor, Memento and Interpreter answer those three needs, and each obvious version fails quietly.

{% include excalidraw.html name="25-visitor-memento-interpreter" described="true" caption="Figure 25.1: Each operation over the closed event union is one match, and mypy reports a kind it leaves out. A booking rolls back from a frozen snapshot that leaves the audit alone, and one tariff tree is both priced and explained." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-25-visitor-memento-interpreter" markdown="1">
The figure has three columns. In the left one, `HandlingEvent` leads down to `describe`, "match, assert_never: a missing kind is a type error". Below it are two muted boxes: "an open registry of functions" ("an unregistered kind gets the fallback") and "a method on every event class". In the middle, `Booking` ("request, documents, audit") leads to `snapshot()` ("captures request, documents") and then `BookingSnapshot` ("frozen: request, documents"), which leads to `rollback` ("the caretaker"). An arrow labelled "restores on error" runs from `rollback` back up to `Booking`, and a note reads "audit: not captured". On the right, `Expr` ("a tariff as a tree") leads to `OverWeight` ("then, otherwise"), which leads to `Add` and `Max`, each with `PerKg` and `Flat` leaves. Below the tree, with no arrows, are `evaluate` ("reads the whole tree, gives Money") and `explain` ("reads the whole tree, gives text").
</div>
</details>

The figure puts the three patterns side by side: one function per operation, one snapshot per rollback and one tree with two readings.

## Pattern: Visitor

### The problem

Visitor is for a fixed family of kinds that gets new operations over time. The tracking feed's events are booked, loaded, departed, cleared and delivered. One operation writes a line of text for the feed, another gives the status a consignment holds afterwards, and a new operation shouldn't mean editing five classes.

The obvious version is a function with an `isinstance` chain and a fallback. A delivered event reaches a function that doesn't handle it, and the fallback answers "unrecognised event". Nothing raises, and mypy doesn't complain.

### The solution

A **Visitor** moves each operation over a family of element classes into an object with one method per class, so a new operation is a new visitor rather than an edit to every class.

**Bucket: dissolves.** An operation becomes a function with one `match` over a closed union, and the `accept` method and the visitor class disappear.

In *Design Patterns* (1994), each element class carries an `accept` method that passes the element to a visitor object, so the operation that runs depends on two types at once, the element's and the visitor's. [The three-way split]({{ '/docs/03-the-three-way-split/' | relative_url }}) explains the buckets, and [Composite and Flyweight]({{ '/docs/21-composite-and-flyweight/' | relative_url }}) introduces the closed union and `assert_never`.

### How Python models it

```python
type HandlingEvent = Booked | Loaded | Departed | Cleared | Delivered


def describe(event: HandlingEvent, /) -> str:
    """One line for a tracking feed. A kind left out is a type error."""
    match event:
        case Booked(consignment_id, port):
            return f"{consignment_id} booked at {port}"
        case Loaded(consignment_id, port):
            return f"{consignment_id} loaded at {port}"
        case Departed(consignment_id, port):
            return f"{consignment_id} departed {port}"
        case Cleared(consignment_id, port):
            return f"{consignment_id} cleared customs at {port}"
        case Delivered(consignment_id, port):
            return f"{consignment_id} delivered at {port}"
        case _:
            assert_never(event)
```

The five events are frozen dataclasses, and `type HandlingEvent` is the closed set. A new operation is another function: `status_after` maps each event to a `ConsignmentStatus` in its own `match`, and no event class changes. A new kind is the expensive direction, and that's where the closed set pays. The typing documentation describes `assert_never` as a way to "Ask a static type checker to confirm that a line of code is unreachable." A function that leaves `Delivered` out gets this from mypy:

```text
<string>:18: error: Argument 1 to "assert_never" has incompatible type "Delivered"; expected "Never"  [arg-type]
```

An object outside the union fails at run time instead, with an `AssertionError` that says "Expected code to be unreachable".

### What `accept` costs

The 1994 form needs an `accept` method on each kind. Written beside the real events, it uses a twin of each event class:

```python
class EventVisitor[T](Protocol):
    """The GoF visitor: one visit method per element class."""

    def visit_booked(self, event: Booked, /) -> T: ...
    def visit_loaded(self, event: Loaded, /) -> T: ...
    def visit_departed(self, event: Departed, /) -> T: ...
    def visit_cleared(self, event: Cleared, /) -> T: ...
    def visit_delivered(self, event: Delivered, /) -> T: ...


@dataclass(frozen=True, slots=True)
class _AcceptingBooked(Booked):
    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_booked(self)
```

The `match`, `singledispatch` and `accept` forms produce the same five lines for the journey of `CN-1`. The accept form buys one check: mypy refuses a visitor that lacks a `visit_` method.

```text
<string>:33: error: Argument 1 to "accept" of "Booked" has incompatible type "Describer"; expected "EventVisitor[Never]"  [arg-type]
<string>:33: error: Argument 1 to "accept" of "Delivered" has incompatible type "Describer"; expected "EventVisitor[Never]"  [arg-type]
```

That's the protection `assert_never` already gives, bought with a method on each class and a class per operation.

### Closed or open

What survives of Visitor is a question the language doesn't answer: is the set of kinds closed or open?

| Set of kinds | Tool | A kind left out |
| --- | --- | --- |
| Closed: one team owns the union | `match` with `assert_never` | mypy error |
| Open: other code adds kinds | `functools.singledispatch` | the fallback runs; mypy is silent |

With `Booked`, `Loaded`, `Departed` and `Cleared` registered on a fallback that takes any `object`, a `Delivered` event returns "unrecognised event" and nothing raises. An open set trades that check for extensibility. [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}) covers the open form.

`singledispatch` reads one argument. The [functools documentation](https://docs.python.org/3/library/functools.html) says "note that the dispatch happens on the type of the first argument", and [PEP 443](https://peps.python.org/pep-0443/), by Łukasz Langa, defines the term: "When the implementation is chosen based on the type of a single argument, this is known as single dispatch." With `Booked` registered as the first parameter, `two(booked, 1)` and `two(booked, "x")` pick the same implementation and `two(1, booked)` falls back. When an operation depends on two values, a `match` on a tuple reads both. [PEP 634](https://peps.python.org/pep-0634/), by Brandt Bucher and Guido van Rossum, specifies it: "A fixed-length sequence pattern matches the subpatterns to corresponding items of the subject sequence, from left to right."

## Pattern: Memento

### The problem

Memento is for putting an object back the way it was after a change fails, when the code that asks for the undo shouldn't reach into the object's fields. A booking is amended in batches: attach a document, reweigh, redirect. The batch fails on a refused destination, the booking is rolled back, and the dangerous goods declaration attached inside the batch is still there.

A booking is the case undo by inverse can't handle. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) restores a frozen request; a booking spreads its state over fields, some of them mutable, and no single inverse exists.

### The solution

A **Memento** is an opaque token of an object's state, produced by the object and kept by a separate holder that gives it back without opening it.

**Bucket: survives.** Two decisions stay with you: what to capture, and what must not roll back.

### How Python models it

The token is a frozen dataclass, and the holder is a context manager that restores when the block raises an `Exception`:

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True)
class BookingSnapshot:
    """What a rollback needs: the request and an immutable copy of the documents."""

    request: BookingRequest
    documents: frozenset[DocumentKind]


    def snapshot(self) -> BookingSnapshot:
        return BookingSnapshot(self.request, frozenset(self.documents))

    def restore(self, snapshot: BookingSnapshot) -> None:
        self.request = snapshot.request
        self.documents = set(snapshot.documents)


@contextmanager
def rollback(booking: Booking) -> Iterator[None]:
    """Undo a failed block. The audit is not captured, so a refusal survives."""
    saved = booking.snapshot()
    try:
        yield
    except Exception:
        booking.restore(saved)
        booking.audit.append("rolled back")
        raise
```
<!-- fmt:on -->

`Booking` holds a frozen `BookingRequest`, a working set of documents and an append-only audit list. The snapshot's `frozenset` is a different object from the live set. The audit stays out, because a record that an amendment was refused must survive the rollback of that amendment.

A batch attaches a dangerous goods declaration, reweighs to 1,200 kg and redirects to "Hamburg", which isn't a five-letter UN/LOCODE and is refused. After the rollback:

- the request is back to 100 kg and `SGSIN`;
- the documents are the commercial invoice alone;
- the `AmendmentError` still leaves the block, so the caller learns the batch failed;
- the audit holds four entries: the attachment, the reweigh, the refusal and `"rolled back"`.

A batch that succeeds keeps its changes.

### What to capture

The two copy functions each capture the wrong amount:

| Memento | Documents after rollback | Audit after rollback |
| --- | --- | --- |
| `BookingSnapshot` | restored | four entries |
| `copy.copy(booking)` | the declaration stays attached | four entries |
| `copy.deepcopy(booking)` | restored | `["rolled back"]` |

A shallow copy shares the live `documents` set. A deep copy copies the audit list too, and restoring it throws away the refused attempt. The [copy module documentation](https://docs.python.org/3/library/copy.html) states the general risk: "Because deep copy copies everything it may copy too much, such as data which is intended to be shared between copies." The request is such data: a snapshot shares the frozen request with the booking, since a value that can't change is safe to share, and a deep copy makes a new equal one.

The snapshot can't be changed afterwards. Assigning to a field raises `FrozenInstanceError`, and mypy refuses the same edit:

```text
<string>:8: error: Property "request" defined in "BookingSnapshot" is read-only  [misc]
<string>:9: error: "frozenset[DocumentKind]" has no attribute "add"  [attr-defined]
```

## Pattern: Interpreter

### The problem

Interpreter is for rules that people write down and the program must apply. A pricing team writes tariff rules, and the system must price consignments under them and read them back to a customer. Written as nested closures, a tariff prices correctly, and nobody can print it as a sentence or compare it with last year's.

### The solution

An **Interpreter** represents a rule as a tree of objects, one class per kind of node, and evaluates the rule by walking the tree.

**Bucket: survives.** The grammar and its readings are still design.

In *Design Patterns* each node class carries the method that evaluates it. The node classes stay in Python, as a small grammar of frozen dataclasses. What dissolves is the method on each node: a reading is a function with one `match`, the same move as Visitor.

### How Python models it

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True)
class Add:
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class OverWeight:
    """Use `then` above the limit and `otherwise` at or below it."""

    kilograms: Decimal
    then: Expr
    otherwise: Expr


type Expr = PerKg | Flat | Add | Max | OverWeight


def evaluate(expr: Expr, consignment: Consignment, /) -> Money:
    """Price a consignment under the rule."""
    match expr:
        case PerKg(rate):
            return rate.times(consignment.weight.kilograms)
        case Flat(amount):
            return amount
        case Add(left, right):
            return evaluate(left, consignment) + evaluate(right, consignment)
        case Max(left, right):
            return max(evaluate(left, consignment), evaluate(right, consignment))
        case OverWeight(kilograms, then, otherwise):
            chosen = then if consignment.weight.kilograms > kilograms else otherwise
            return evaluate(chosen, consignment)
        case _:
            assert_never(expr)
```
<!-- fmt:on -->

`Max` has the same two fields as `Add`, and `PerKg` and `Flat` carry a `Money`. The recursive fields name `Expr` before the alias exists, and need no quotes because annotations are evaluated lazily since 3.14, as [PEP 649](https://peps.python.org/pep-0649/) by Larry Hastings specifies and [PEP 749](https://peps.python.org/pep-0749/) by Jelle Zijlstra refines.

`STANDARD_TARIFF` is one tree: over 1,000 kg, 1.10 EUR per kg plus 25.00 EUR, and otherwise the larger of 1.20 EUR per kg and 45.00 EUR. The rates are illustrative.

| Weight (kg) | 10 | 100 | 100.333 | 1,000 | 2,000 |
| --- | --- | --- | --- | --- | --- |
| Price (EUR) | 45.00 | 120.00 | 120.40 | 1,200.00 | 2,225.00 |

At 10 kg the minimum charge applies. At 1,000 kg the limit isn't passed, because `OverWeight` compares with `>`.

### A tree or closures

Closures built from the same rules give the same five prices, and lose two things:

| | Tariff tree | Closures |
| --- | --- | --- |
| Price | `evaluate` | call it |
| Read back as text | `explain` | no |
| Equal when built the same way | yes, and hash equal | no; each equals only itself |

`explain` writes the standard tariff as:

```text
over 1000 kg: 1.10 EUR per kg + 25.00 EUR; otherwise the larger of 1.20 EUR per kg and 45.00 EUR
```

The rules are data with more than one reading, and a closure has one reading baked in. `evaluate` is a visitor over a closed grammar, so a node left out is a type error:

```text
<string>:19: error: Argument 1 to "assert_never" has incompatible type "OverWeight"; expected "Never"  [arg-type]
```

A child that isn't an expression is refused when the node is built:

```text
<string>:7: error: Argument 2 to "Add" has incompatible type "str"; expected "PerKg | Flat | Add | Max | OverWeight"  [arg-type]
```

Currencies don't mix: adding a USD rule to a EUR one raises `cannot add USD to EUR`, and taking the larger raises `cannot compare USD with EUR`. Parsing a rule language into a tree is a separate problem, not covered here.

## When not to use it

- **Visitor.** With one operation over the kinds, write the `match` where it's needed.
- **Memento.** With a booking that is itself an immutable value, keep the old value and skip the snapshot class. When undo has a cheap inverse, use a command.
- **Interpreter.** With a rule set that doesn't change and that nobody reads back, a plain function is enough.

> **🤖 Explore with your agent**
>
> "Over the closed `HandlingEvent` union, write each operation as one function using `match` that ends in `case _: assert_never(event)`. Snapshot a `Booking` into a frozen `BookingSnapshot` holding the request and a `frozenset` of documents, leave the audit out, and restore it in a `rollback` context manager that re-raises. Write tariff rules as frozen node dataclasses under `type Expr`, with `evaluate` and `explain` each a single `match`."
>
> If the reply adds an `accept` method or snapshots with `copy.copy`, ask for the test that fails.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/25-visitor-memento-interpreter
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 48 cases pass and mypy is clean. For how the mypy checks are run from pytest, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}). Two experiments:

- **Capture the audit.** In a scratch copy, add `audit: tuple[str, ...]` to `BookingSnapshot`, pass `tuple(self.audit)` in `snapshot()` and set `self.audit = list(snapshot.audit)` in `restore()`. One test fails: the audit ends as `['rolled back']`, because the refusal is restored away. mypy stays green, because the change is type-correct.
- **Delete the `Delivered` arm.** In a scratch copy, delete the `Delivered` case from `describe`. The `match` form fails with `Expected code to be unreachable, but got: Delivered(...)`, and mypy reports the `assert_never` error in `events.py`. The accept form still passes, because it never calls `describe`.

## What you can do now

- Choose by the set: `describe` is a `match` over a closed union, and a `singledispatch` function answers an unregistered `Delivered` with its fallback.
- Count what `accept` costs: a method on each event class, for the same missing-kind check `assert_never` gives.
- Roll back a failed batch with `rollback`, which restores the request and the documents from a `BookingSnapshot`.
- Decide what a memento captures: the request and a `frozenset`, and not the audit, which a deep copy would erase.
- Read one tariff two ways, with `evaluate` and `explain` over `STANDARD_TARIFF`, and compare two trees, which closures can't do.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Visitor, Memento and Interpreter. [PEP 634](https://peps.python.org/pep-0634/) specifies structural pattern matching, and [PEP 636](https://peps.python.org/pep-0636/), by Daniel F Moisset, is its tutorial. The typing documentation covers [`assert_never`](https://docs.python.org/3/library/typing.html). The site python-patterns.guide, by Brandon Rhodes, has no page on any of the three patterns in its index. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
