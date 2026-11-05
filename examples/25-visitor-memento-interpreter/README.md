# Visitor, Memento, and Interpreter

Three patterns over one shipping domain: tracking events, booking amendments and tariff rules. The
chapter's thesis is that Visitor dissolves while Memento and Interpreter survive. Python removes
the `accept` method on every element class and the visitor class per operation: an operation is a
function with a `match` over a closed union. What remains is a choice the language does not make
for you, closed set or open set. A frozen snapshot is the memento and a context manager is the
caretaker, and two decisions remain: what to capture, and what must not roll back. Frozen node
dataclasses are the grammar, and a grammar with more than one reading stays design. Port codes,
consignment ids, rates and fees are illustrative.

## What it witnesses

The visitor.

- `type HandlingEvent = Booked | Loaded | Departed | Cleared | Delivered`, frozen slotted events.
  `describe` and `status_after` are each one `match` ending in `assert_never`. mypy reports an event
  left out of a `match`, and at run time an object outside the union raises `AssertionError`.
- `visitor_form` is `match`, `singledispatch` or `accept`, all describing the same five-event
  journey of `CN-1`. The `accept` form uses twins in `tests/conftest.py`: frozen slotted subclasses
  of the events that add `accept`, an `EventVisitor[T]` Protocol and a describing visitor.
- A singledispatch visitor answers an event with no registration with its fallback, and mypy exits
  0. It dispatches on the first argument only. An accept visitor missing a visit method is a mypy
  error (a reduced model).

The memento.

- `Booking` is an entity with a frozen `BookingRequest`, a working `documents` set and an
  append-only `audit` list. `BookingSnapshot(request, documents: frozenset[DocumentKind])` is frozen.
  `rollback(booking)` restores on an exception, appends `"rolled back"` and re-raises. The audit is
  left out of the snapshot, so a refused amendment survives the rollback.
- `memento_form` is `snapshot`, `shallow` (`copy.copy`) or `deepcopy`, all run on one failed
  amendment. The shallow form shares the document set and keeps a document attached inside the failed
  block. The deep form restores the audit too, which erases the refused attempt, and copies the
  frozen request a snapshot shares.
- mypy refuses to change a snapshot, and the run time refuses too.

The interpreter.

- `type Expr = PerKg | Flat | Add | Max | OverWeight`, frozen slotted nodes. With deferred
  annotations the recursive fields name `Expr` before it is defined. `evaluate` and `explain` are
  two readings of one tree, each a `match` ending in `assert_never`.
- `STANDARD_TARIFF`: over 1,000 kg, 1.10 EUR per kg plus 25.00 EUR; otherwise the larger of
  1.20 EUR per kg and 45.00 EUR.
- `rule_form` is `tree` or `closure`, pricing the same consignments. Equal trees compare and hash
  equal, and two closures built the same way are not equal. Currencies do not mix. mypy reports a
  node left out of `evaluate` and a child that is not an expression. Parsing a rule language is a
  separate problem and is not built here.

## Layout

- `src/visitor_memento_interpreter/domain.py`: `ConsignmentId`, `ConsignmentStatus`,
  `DocumentKind`, `AmendmentError`, `Money`, `Weight`, `Consignment`.
- `src/visitor_memento_interpreter/events.py`: `Booked`, `Loaded`, `Departed`, `Cleared`,
  `Delivered`, `HandlingEvent`, `describe`, `status_after`.
- `src/visitor_memento_interpreter/memento.py`: `BookingRequest`, `BookingSnapshot`, `Booking`,
  `rollback`.
- `src/visitor_memento_interpreter/tariff.py`: `PerKg`, `Flat`, `Add`, `Max`, `OverWeight`, `Expr`,
  `evaluate`, `explain`, `STANDARD_TARIFF`.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

## What the tests verify

`tests/test_visitor.py`

- `test_every_visitor_form_describes_a_journey_the_same_way`: `match`, `singledispatch` and `accept`.
- `test_status_after_maps_each_event_to_a_consignment_status`: one case per event.
- `test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback`: `Delivered` gets the
  fallback's answer.
- `test_describe_refuses_an_object_outside_the_union`: `AssertionError`.
- `test_singledispatch_dispatches_on_the_first_argument_only`: a second argument does not dispatch.
- `test_the_accept_form_puts_an_accept_method_on_every_event_class`: five twins have it, no `src`
  class does.

`tests/test_memento.py`

- `test_rollback_restores_the_request_after_a_failed_amendment`: all three memento forms.
- `test_rollback_restores_the_attached_documents`: the snapshot form.
- `test_a_shallow_memento_keeps_a_document_attached_after_rollback`: the shared set.
- `test_rollback_keeps_the_audit_trail`: four entries, including the refusal.
- `test_rollback_re_raises_the_amendment_error`: `not a UN/LOCODE`.
- `test_a_block_that_succeeds_keeps_its_changes`: no restore on success.
- `test_a_deepcopy_memento_erases_the_audit_trail_on_rollback`: only `rolled back` remains.
- `test_a_snapshot_shares_the_frozen_request_and_a_deepcopy_copies_it`: identity of the request.
- `test_a_snapshot_cannot_be_changed_at_run_time`: `FrozenInstanceError`.

`tests/test_tariff.py`

- `test_every_rule_form_prices_the_same_consignments`: tree and closure at 10, 100, 100.333, 1,000
  and 2,000 kg.
- `test_explain_writes_the_tariff_as_text`: the tariff as one sentence.
- `test_equal_tariff_trees_compare_and_hash_equal`: and a different tree does not.
- `test_closures_built_the_same_way_are_not_equal`: a closure equals only itself.
- `test_a_rule_in_another_currency_is_refused`: `cannot add USD to EUR`.
- `test_the_larger_of_two_rules_in_different_currencies_is_refused`: `cannot compare USD with EUR`.
- `test_a_weight_must_be_positive_and_finite_for_a_priced_consignment`: zero, negative, NaN, infinity.

`tests/test_static.py`

- `test_mypy_reports_an_event_left_out_of_a_match`: `[arg-type]`, expected `Never`.
- `test_mypy_accepts_a_singledispatch_visitor_that_misses_an_event`: clean.
- `test_mypy_reports_a_visitor_class_missing_a_visit_method`: `[arg-type]` (a reduced model).
- `test_mypy_refuses_to_change_a_snapshot`: `[misc]` and `[attr-defined]`.
- `test_mypy_reports_a_tariff_node_left_out_of_evaluate`: `[arg-type]`, expected `Never`.
- `test_mypy_refuses_a_node_whose_child_is_not_an_expression`: `[arg-type]`.

Classes and functions named with a leading underscore in `tests/conftest.py` are test fixtures and
aren't part of the model code.
