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

A tracking feed carries five kinds of handling event: booked, loaded, departed, cleared and delivered. Several operations run over them, a line of text for the feed and the status a consignment holds afterwards, and a new operation shouldn't mean editing five classes. That's the force behind Visitor. A booking is amended in batches (attach a document, reweigh, redirect), and a batch that fails halfway has to leave the booking as it was. That's the force behind Memento. And a pricing team writes tariff rules that the system must price and also read back to a customer. That's the force behind Interpreter. Three things go wrong in the obvious versions.

A delivered event reaches a function that doesn't handle it, and a fallback answers "unrecognised event". Nothing raises, and mypy doesn't complain.

An amendment batch fails on a refused destination, the booking is rolled back, and the dangerous goods declaration attached inside the batch is still there.

A tariff is written as nested closures. It prices correctly, and nobody can print it as a sentence or compare it with last year's.

{% include excalidraw.html name="25-visitor-memento-interpreter" caption="Figure 25.1: Each operation over the closed event union is one match, and mypy reports a kind it leaves out. A booking rolls back from a frozen snapshot that leaves the audit alone, and one tariff tree is both priced and explained." %}

The figure has three columns. In the left one, `HandlingEvent` leads down to `describe`, "match, assert_never: a missing kind is a type error". Below it are two muted boxes: "an open registry of functions" ("an unregistered kind gets the fallback") and "a method on every event class". In the middle, `Booking` ("request, documents, audit") leads to `snapshot()` ("captures request, documents") and then `BookingSnapshot` ("frozen: request, documents"), which leads to `rollback` ("the caretaker"). An arrow labelled "restores on error" runs from `rollback` back up to `Booking`, and a note reads "audit: not captured". On the right, `Expr` ("a tariff as a tree") leads to `OverWeight` ("then, otherwise"), which leads to `Add` and `Max`, each with `PerKg` and `Flat` leaves. Below the tree, with no arrows, are `evaluate` ("reads the whole tree, gives Money") and `explain` ("reads the whole tree, gives text").

## Visitor: one function per operation

Visitor is for a fixed family of kinds that gets new operations over time. In *Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994), each element class carries an `accept` method that passes the element to a visitor object, and the visitor has one method per element class. The operation that runs depends on two types at once, the element's and the visitor's. Python dissolves that machinery. An operation becomes a function with one `match` over a closed union, and the `accept` method and the visitor class disappear. The bucket is dissolves, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it. [Composite and Flyweight]({{ '/docs/21-composite-and-flyweight/' | relative_url }}) introduces the closed union and `assert_never` on a tree of shipments, and they carry over unchanged.

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

The five events are frozen dataclasses, and `type HandlingEvent` is the closed set. Adding an operation is writing another function: `status_after` maps each event to a `ConsignmentStatus` in its own `match` (`test_status_after_maps_each_event_to_a_consignment_status`), and no event class changes. Adding a kind is the expensive direction, and that's where the closed set pays. The typing documentation describes `assert_never` as a way to "Ask a static type checker to confirm that a line of code is unreachable." If a function leaves `Delivered` out, mypy 2.4.1 reports it at that call. `test_mypy_reports_an_event_left_out_of_a_match` type-checks a function that handles four of the five events, and through the test's own helper prints:

```text
<string>:18: error: Argument 1 to "assert_never" has incompatible type "Delivered"; expected "Never"  [arg-type]
```

An object outside the union is a run-time failure instead: `test_describe_refuses_an_object_outside_the_union` passes a string, with the type error silenced, and gets an `AssertionError` that says "Expected code to be unreachable".

The comparison is the form the book draws, written as a test fixture so that it describes the same journey as `describe`. Three forms, `match`, `singledispatch` and `accept`, produce the same five lines for the journey of `CN-1` (`test_every_visitor_form_describes_a_journey_the_same_way`). The accept form needs a twin of each event with the extra method:

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

The real events don't gain the method: `test_the_accept_form_puts_an_accept_method_on_every_event_class` finds `accept` on all five twins and on none of the five classes in `src`. The cost is a dispatch method on each kind. The form does catch one mistake the `match` catches differently. A visitor that lacks a `visit_` method is refused by mypy, and `test_mypy_reports_a_visitor_class_missing_a_visit_method` shows it on a reduced model, a self-contained snippet with two event classes and a describer that has one method:

```text
<string>:33: error: Argument 1 to "accept" of "Booked" has incompatible type "Describer"; expected "EventVisitor[Never]"  [arg-type]
<string>:33: error: Argument 1 to "accept" of "Delivered" has incompatible type "Describer"; expected "EventVisitor[Never]"  [arg-type]
```

That's the same protection, bought with a method on each class and a class per operation.

## Closed or open

What survives of Visitor is a question the language doesn't answer for you: is the set of kinds closed or open? A closed set is a union that one team owns, and `match` with `assert_never` makes each function notice a new kind. An open set is one that other code extends, and there `functools.singledispatch` is the tool. A function registers one implementation per class, and callers that add a kind register their own. The open form has its own chapter, [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}). Two tests show its cost.

`test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback` registers `Booked`, `Loaded`, `Departed` and `Cleared` on a fallback that takes any `object`. `Delivered` has no registration, so the call falls to the fallback and returns "unrecognised event", and nothing raises. mypy says nothing either: `test_mypy_accepts_a_singledispatch_visitor_that_misses_an_event` checks the same four registrations and exits 0 with empty output. An open set trades that check for extensibility.

The functools documentation also says the dispatch is by one argument: "note that the dispatch happens on the type of the first argument". [PEP 443](https://peps.python.org/pep-0443/), by Łukasz Langa, defines the term: "When the implementation is chosen based on the type of a single argument, this is known as single dispatch." `test_singledispatch_dispatches_on_the_first_argument_only` registers `Booked` as the first parameter of a two-parameter function and shows that the second argument doesn't take part: `two(booked, 1)` and `two(booked, "x")` pick the same implementation, and `two(1, booked)` falls back. When an operation depends on two values, a `match` on a tuple reads both. [PEP 634](https://peps.python.org/pep-0634/), by Brandt Bucher and Guido van Rossum, specifies it: "A fixed-length sequence pattern matches the subpatterns to corresponding items of the subject sequence, from left to right." The [functools documentation](https://docs.python.org/3.15/library/functools.html) is the reference for the decorator.

## Memento: a frozen snapshot and a rollback

Memento is for putting an object back the way it was after a change fails, when the code that asks for the undo shouldn't reach into the object's fields. *Design Patterns* has the object produce an opaque token of its own state, and a separate holder keeps the token and gives it back; the holder doesn't open it. Python shrinks the arrangement to two parts. The token is a frozen dataclass, and the holder is a context manager that restores when the block raises an `Exception`. The bucket is survives, because two decisions stay with you: what to capture, and what must not roll back. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) covers undo by inverse, where a frozen request is already a safe snapshot. A booking is the case that chapter hands over: state spread over fields, some of them mutable, where no single inverse exists.

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

`Booking` holds a frozen `BookingRequest`, a working set of documents and an append-only audit list. The snapshot captures the request and a `frozenset` of the documents, so the live set and the saved one are different objects. It leaves the audit out, because a record that an amendment was refused must survive the rollback of that amendment.

The test batch attaches a dangerous goods declaration, reweighs to 1,200 kg and redirects to "Hamburg", which isn't a five-letter UN/LOCODE and is refused. After the rollback the request is back to 100 kg and `SGSIN`, in all three forms of the restore table (`test_rollback_restores_the_request_after_a_failed_amendment`), and with the snapshot the documents are the commercial invoice alone (`test_rollback_restores_the_attached_documents`). The `AmendmentError` leaves the block, so the caller still learns the batch failed (`test_rollback_re_raises_the_amendment_error`). A batch that succeeds keeps its changes (`test_a_block_that_succeeds_keeps_its_changes`). The audit holds four entries: the attachment, the reweigh, the refusal and `"rolled back"` (`test_rollback_keeps_the_audit_trail`).

Two other ways to take the memento fail differently. Saving `copy.copy(booking)` is shallow, so the copy's `documents` is the live set. A document attached inside the failed block stays attached after the restore (`test_a_shallow_memento_keeps_a_document_attached_after_rollback`). Saving `copy.deepcopy(booking)` copies the audit list as well, and restoring it throws away the refused attempt: the audit ends as `["rolled back"]` (`test_a_deepcopy_memento_erases_the_audit_trail_on_rollback`). The copy documentation puts the risk in general terms: "Because deep copy copies everything it may copy too much, such as data which is intended to be shared between copies." Here the request is such data. A snapshot shares the frozen request with the booking, since a value that can't change is safe to share, and a deep copy makes a new equal one (`test_a_snapshot_shares_the_frozen_request_and_a_deepcopy_copies_it`). The [copy module documentation](https://docs.python.org/3.15/library/copy.html) describes both functions.

The snapshot can't be changed afterwards. At run time, assigning to a field raises `FrozenInstanceError` (`test_a_snapshot_cannot_be_changed_at_run_time`). mypy refuses the same edit, and a `frozenset` has no `add`. `test_mypy_refuses_to_change_a_snapshot` prints:

```text
<string>:8: error: Property "request" defined in "BookingSnapshot" is read-only  [misc]
<string>:9: error: "frozenset[DocumentKind]" has no attribute "add"  [attr-defined]
```

## Interpreter: a tariff as a tree

Interpreter is for rules that people write down and the program must apply. In *Design Patterns* a rule is a tree of objects with one class per kind of node, and each class carries the method that evaluates it. The classes stay in Python, as a small grammar of frozen nodes. What dissolves is a method on each node: a reading is a function with one `match`, the same move as the visitor above. The bucket is survives, because the grammar and its readings are still design. The question is how many readings one rule gets.

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

`Max` has the same two fields as `Add`, and `PerKg` and `Flat` carry a `Money`. The recursive fields name `Expr` before the alias exists. Annotations are evaluated lazily since 3.14, as [PEP 649](https://peps.python.org/pep-0649/) by Larry Hastings specifies and [PEP 749](https://peps.python.org/pep-0749/) by Jelle Zijlstra refines, so the fields need no quotes. The standard tariff, `STANDARD_TARIFF`, is one tree: over 1,000 kg, 1.10 EUR per kg plus 25.00 EUR, and otherwise the larger of 1.20 EUR per kg and 45.00 EUR. The rates are illustrative.

A tree and a set of closures built from the same rules price the same consignments. `test_every_rule_form_prices_the_same_consignments` runs both at 10, 100, 100.333, 1,000 and 2,000 kg and gets 45.00, 120.00, 120.40, 1,200.00 and 2,225.00 EUR. At 10 kg the minimum charge of 45.00 applies. At 1,000 kg the limit isn't passed, because `OverWeight` compares with `>`, so the second branch prices it at 1,200.00. The closure form agrees on all five weights and loses two things. The first is that only the tree has a second reading. `explain` writes the same tree as a sentence (`test_explain_writes_the_tariff_as_text`):

```text
over 1000 kg: 1.10 EUR per kg + 25.00 EUR; otherwise the larger of 1.20 EUR per kg and 45.00 EUR
```

The second is that a closure can't be compared. Two trees built from equal parts are equal and hash equal, and a tree with one different rate isn't equal (`test_equal_tariff_trees_compare_and_hash_equal`). Two closures built the same way aren't equal, and each equals itself but not its twin (`test_closures_built_the_same_way_are_not_equal`). So the rules are data with more than one reading: `evaluate` and `explain` each read the whole tree, one to a `Money` and one to text. A closure has a single reading baked in. `evaluate` is itself a visitor over a closed grammar, which is why a node left out is a type error. `test_mypy_reports_a_tariff_node_left_out_of_evaluate` prints:

```text
<string>:19: error: Argument 1 to "assert_never" has incompatible type "OverWeight"; expected "Never"  [arg-type]
```

A child that isn't an expression is refused when the node is built, and `test_mypy_refuses_a_node_whose_child_is_not_an_expression` shows it:

```text
<string>:7: error: Argument 2 to "Add" has incompatible type "str"; expected "PerKg | Flat | Add | Max | OverWeight"  [arg-type]
```

Currencies don't mix. Adding a USD rule to a EUR one raises `cannot add USD to EUR` (`test_a_rule_in_another_currency_is_refused`), and taking the larger of the two raises `cannot compare USD with EUR` (`test_the_larger_of_two_rules_in_different_currencies_is_refused`). Parsing a rule language into a tree is a separate problem, and the example doesn't build one.

## When not to use it

With one operation over the kinds, write the `match` where it's needed. With a booking that is itself an immutable value, keep the old value and skip the snapshot class. When undo has a cheap inverse, use a command. With a rule set that doesn't change and that nobody reads back, a plain function is enough.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a visitor, a memento and an interpreter.** A request for "a visitor" or "a memento" names a 1994 shape and leaves open whether the kinds are closed, what a snapshot captures and what it must leave alone. State those in the prompt:

> Over the closed `HandlingEvent` union, write each operation as one function using `match` that ends in `case _: assert_never(event)`. Snapshot a `Booking` into a frozen `BookingSnapshot` holding the request and a `frozenset` of documents, leave the audit out, and restore it in a `rollback` context manager that re-raises. Write tariff rules as frozen node dataclasses under `type Expr`, with `evaluate` and `explain` each a single `match`.

If the reply adds an `accept` method or snapshots with `copy.copy`, ask for the test that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/25-visitor-memento-interpreter
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
collecting ... collected 48 items

tests/test_memento.py::test_rollback_restores_the_request_after_a_failed_amendment[snapshot] PASSED [  2%]
tests/test_memento.py::test_rollback_restores_the_request_after_a_failed_amendment[shallow] PASSED [  4%]
tests/test_memento.py::test_rollback_restores_the_request_after_a_failed_amendment[deepcopy] PASSED [  6%]
tests/test_memento.py::test_rollback_restores_the_attached_documents PASSED [  8%]
tests/test_memento.py::test_a_shallow_memento_keeps_a_document_attached_after_rollback PASSED [ 10%]
tests/test_memento.py::test_rollback_keeps_the_audit_trail PASSED        [ 12%]
tests/test_memento.py::test_rollback_re_raises_the_amendment_error PASSED [ 14%]
tests/test_memento.py::test_a_block_that_succeeds_keeps_its_changes PASSED [ 16%]
tests/test_memento.py::test_a_deepcopy_memento_erases_the_audit_trail_on_rollback PASSED [ 18%]
tests/test_memento.py::test_a_snapshot_shares_the_frozen_request_and_a_deepcopy_copies_it PASSED [ 20%]
tests/test_memento.py::test_a_snapshot_cannot_be_changed_at_run_time PASSED [ 22%]
tests/test_static.py::test_mypy_reports_an_event_left_out_of_a_match PASSED [ 25%]
tests/test_static.py::test_mypy_accepts_a_singledispatch_visitor_that_misses_an_event PASSED [ 27%]
tests/test_static.py::test_mypy_reports_a_visitor_class_missing_a_visit_method PASSED [ 29%]
tests/test_static.py::test_mypy_refuses_to_change_a_snapshot PASSED      [ 31%]
tests/test_static.py::test_mypy_reports_a_tariff_node_left_out_of_evaluate PASSED [ 33%]
tests/test_static.py::test_mypy_refuses_a_node_whose_child_is_not_an_expression PASSED [ 35%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[tree-10] PASSED [ 37%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[tree-100] PASSED [ 39%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[tree-100.333] PASSED [ 41%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[tree-1000] PASSED [ 43%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[tree-2000] PASSED [ 45%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[closure-10] PASSED [ 47%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[closure-100] PASSED [ 50%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[closure-100.333] PASSED [ 52%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[closure-1000] PASSED [ 54%]
tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments[closure-2000] PASSED [ 56%]
tests/test_tariff.py::test_explain_writes_the_tariff_as_text PASSED      [ 58%]
tests/test_tariff.py::test_equal_tariff_trees_compare_and_hash_equal PASSED [ 60%]
tests/test_tariff.py::test_closures_built_the_same_way_are_not_equal PASSED [ 62%]
tests/test_tariff.py::test_a_rule_in_another_currency_is_refused PASSED  [ 64%]
tests/test_tariff.py::test_the_larger_of_two_rules_in_different_currencies_is_refused PASSED [ 66%]
tests/test_tariff.py::test_a_weight_must_be_positive_and_finite_for_a_priced_consignment[0] PASSED [ 68%]
tests/test_tariff.py::test_a_weight_must_be_positive_and_finite_for_a_priced_consignment[-1] PASSED [ 70%]
tests/test_tariff.py::test_a_weight_must_be_positive_and_finite_for_a_priced_consignment[NaN] PASSED [ 72%]
tests/test_tariff.py::test_a_weight_must_be_positive_and_finite_for_a_priced_consignment[Infinity] PASSED [ 75%]
tests/test_visitor.py::test_every_visitor_form_describes_a_journey_the_same_way[match] PASSED [ 77%]
tests/test_visitor.py::test_every_visitor_form_describes_a_journey_the_same_way[singledispatch] PASSED [ 79%]
tests/test_visitor.py::test_every_visitor_form_describes_a_journey_the_same_way[accept] PASSED [ 81%]
tests/test_visitor.py::test_status_after_maps_each_event_to_a_consignment_status[booked] PASSED [ 83%]
tests/test_visitor.py::test_status_after_maps_each_event_to_a_consignment_status[loaded] PASSED [ 85%]
tests/test_visitor.py::test_status_after_maps_each_event_to_a_consignment_status[departed] PASSED [ 87%]
tests/test_visitor.py::test_status_after_maps_each_event_to_a_consignment_status[cleared] PASSED [ 89%]
tests/test_visitor.py::test_status_after_maps_each_event_to_a_consignment_status[delivered] PASSED [ 91%]
tests/test_visitor.py::test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback PASSED [ 93%]
tests/test_visitor.py::test_describe_refuses_an_object_outside_the_union PASSED [ 95%]
tests/test_visitor.py::test_singledispatch_dispatches_on_the_first_argument_only PASSED [ 97%]
tests/test_visitor.py::test_the_accept_form_puts_an_accept_method_on_every_event_class PASSED [100%]

============================== 48 passed in 3.00s ==============================
Success: no issues found in 10 source files
```

The suite has 28 test functions and 48 cases. `tests/test_visitor.py` holds the three visitor forms and the dispatch witnesses, `tests/test_memento.py` the restore table and its two copy forms, `tests/test_tariff.py` the pricing table with the closure form, and `tests/test_static.py` the mypy witnesses. For how those are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: capture the audit.** In a scratch copy, add `audit: tuple[str, ...]` to `BookingSnapshot`, pass `tuple(self.audit)` in `snapshot()` and set `self.audit = list(snapshot.audit)` in `restore()`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` prints:

```text
E       AssertionError: assert ['rolled back'] == ['attached da...'rolled back']
tests/test_memento.py:54: AssertionError
FAILED tests/test_memento.py::test_rollback_keeps_the_audit_trail - Assertion...
1 failed, 47 passed in 2.86s
Success: no issues found in 10 source files
```

Only the audit test fails: the restore returns the audit as it was before the batch, so the refusal disappears and `"rolled back"` is all that remains. The tests for the request, the documents and re-raising don't read the audit, and the successful block never restores it. mypy exits 0, because the change is type-correct.

**Experiment two: delete the `Delivered` arm.** In a fresh scratch copy, delete the two lines of the `Delivered` case from `describe`. The same filter, then mypy, prints:

```text
E       AssertionError: Expected code to be unreachable, but got: Delivered(consignment_id='CN-1', port='SGSIN')
FAILED tests/test_visitor.py::test_every_visitor_form_describes_a_journey_the_same_way[match]
1 failed, 47 passed in 2.97s
src/visitor_memento_interpreter/events.py:54: error: Argument 1 to "assert_never" has incompatible type "Delivered"; expected "Never"  [arg-type]
Found 1 error in 1 file (checked 10 source files)
```

The `match` form fails with the `AssertionError` for a `Delivered` event. The accept form's `Delivered` twin still passes, because it reaches the describer through `accept` and doesn't call `describe`, and `status_after` is a separate function. mypy finds the gap in `src`.

## What you can do now

- Choose by the set: `describe` is a `match` for a closed union, and a `singledispatch` function answers an unregistered `Delivered` with its fallback, as `test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback` shows.
- Count what `accept` costs: a method on each event class, as `test_the_accept_form_puts_an_accept_method_on_every_event_class` finds, and mypy refuses a describer missing a `visit_` method, as `test_mypy_reports_a_visitor_class_missing_a_visit_method` shows, which is the same gap it finds in a `match` (`test_mypy_reports_an_event_left_out_of_a_match`).
- Roll back a failed batch: `rollback` restores the request and the documents from a `BookingSnapshot`, and `test_rollback_restores_the_attached_documents` checks it.
- Decide what a memento captures: the request and a `frozenset`, and not the audit, as `test_a_deepcopy_memento_erases_the_audit_trail_on_rollback` and experiment one show.
- Read one tariff two ways: `evaluate` and `explain` over `STANDARD_TARIFF`, with `test_closures_built_the_same_way_are_not_equal` showing what closures can't do.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Visitor, Memento and Interpreter. [PEP 634](https://peps.python.org/pep-0634/) specifies structural pattern matching, and [PEP 636](https://peps.python.org/pep-0636/), by Daniel F Moisset, is its tutorial. The typing documentation covers [`assert_never`](https://docs.python.org/3.15/library/typing.html). The site python-patterns.guide, by Brandon Rhodes, has no page on any of the three patterns in its index. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
