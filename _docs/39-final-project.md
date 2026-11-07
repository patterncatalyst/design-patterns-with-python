---
title: "Final project"
order: 39
layout: tutorial
sectionid: docs
part: "putting-it-together"
description: "One booking through all seven domain areas: an acceptance test written first, undo in reverse on an ExitStack, publishing after the commit and a single composition root."
---

## Learning objectives

By the end of this chapter you can:

- Write the acceptance test for a slice before the slice exists, and make it name each stage it needs.
- Wire seven domain areas through one composition root, the only module outside `carriers.py` that names a concrete carrier.
- Undo completed steps in reverse when a later step refuses, with `ExitStack.callback` and `pop_all`.
- Order effects so that nothing a step can't take back happens before the commit.
- Say which earlier pattern each part is, and where a pattern left out would attach.

## Why this matters

A booking is several steps that each change something outside the desk. Rating only produces a number, but reserving a slot changes a sailing, booking the carrier changes the carrier's books, and a tracking event changes what its subscribers know. Rating, the carrier booking and tracking are each a pattern the book has covered on its own. What happens between the steps is the new question: a booking that customs holds has already taken a slot and a carrier booking, and the desk has to give both back.

Two failures follow when nothing answers it. Without an undo, a held booking leaves the slot reserved and the carrier holding a receipt nobody pays for. Taking the `cancel` callback out of the desk fails `test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking`, and taking the `release` callback out fails three tests, among them `test_the_next_request_takes_the_slot_a_rollback_freed`. With an eager publisher, tracking reports a booking that never happened (`test_an_eager_publisher_reports_a_booking_that_was_rolled_back`).

The slice is one booking through the seven domain areas (Consignment, Rating, Routing, Carrier, Documentation, Billing and Tracking), with an in-memory stand-in for the carrier's SDK. The patterns in it are the book's own. The new questions sit where they meet: which steps can be undone and in what order, which effect has to wait for the commit, and which single function chooses the concrete parts.

{% include excalidraw.html name="39-final-project" caption="Figure 39.1: One booking through the desk's steps. A completed step registers its undo on an exit stack, a held declaration unwinds them in reverse, and the tracking event is published after the commit." %}

Read the figure from the top. A column of boxes runs down the left: `BookingRequest`, an accent box `BookingDesk.ship (Facade)`, then `quote: PricingRule`, `StowagePlan.reserve, undo: release`, `CarrierGateway.book, undo: cancel`, `clear: ClearanceStage chain`, `undo.pop_all(): commit`, `Invoice from LineItems` and `Signal.publish(BOOKED) to TrackingHistory`, each joined to the next by a downward arrow. Two arrows in the accent colour run from the reserve and book boxes to an accent box on the right, `ExitStack holds the undo callbacks`. A dashed arrow runs from the clear box to a dashed box, `Held: cancel, then release; nothing published`. A bar across the bottom reads `build_desk: the one place that chooses FastlineGateway`, with no arrow to it.

## The slice and its acceptance test

An acceptance test says when the slice is whole, and it comes first: it fixes one request and the shipment that request has to produce, and the parts are built until it passes. The request is CN-1, 12.5 kg of green coffee (HS code `0901.21`, valued at 400.00 euros) from the EU zone to `SGSIN`. The rates are illustrative. The shipment it expects has freight of 5.63 (12.5 kg at 0.45 a kilogram is 5.625, rounded half up), duty of 30.00, an invoice of 35.63, the slot `SlotId(1, 1, 1)`, one open carrier receipt holding 12,500 grams and one `BOOKED` event for `NLRTM`. The expectations live in a helper that collects what is missing instead of stopping at the first miss:

```python
def acceptance_failures(
    shipment: Shipment, history: TrackingHistory, client: FastlineClient, plan: StowagePlan
) -> list[str]:
    """What is missing from the slice, in a fixed order; an empty list means it is whole."""
    failures: list[str] = []
    if shipment.quote.total != Money(Decimal("5.63")):
        failures.append(f"freight {shipment.quote.total.amount}")
    if shipment.declaration.duty != Money(Decimal("30.00")):
        failures.append(f"duty {shipment.declaration.duty.amount}")
    if shipment.invoice.total != Money(Decimal("35.63")):
        failures.append(f"invoice {shipment.invoice.total.amount}")
    if shipment.slot != SlotId(1, 1, 1) or list(plan.reservations) != [SlotId(1, 1, 1)]:
        failures.append("slot")
    if dict(client.open) != {1001: 12500}:
        failures.append(f"carrier {dict(client.open)}")
    booked = HandlingEvent(ConsignmentId("CN-1"), HandlingKind.BOOKED, "NLRTM")
    if history.events != (booked,):
        failures.append("tracking")
    return failures
```

The test that uses it builds the desk with `build_desk`, the composition root described below, ships the request and expects an empty list:

```python
def test_a_booking_request_ships_end_to_end(world: World, coffee_request: BookingRequest) -> None:
    client, plan, history = world
    shipment = build_desk(client=client, plan=plan, history=history).ship(coffee_request)

    assert acceptance_failures(shipment, history, client, plan) == []
```

Because the helper returns a list in a fixed order, a failing run says which stage is absent, not only that something is. `test_the_acceptance_test_fails_when_a_stage_is_left_out` shows it. For each of four stages it composes the desk with that stage replaced by a stand-in that does nothing useful, ships the request and compares the helper's list with a literal:

| Stage left out | Stand-in | The helper reports |
| --- | --- | --- |
| `rating` | a rule that returns 0.00 | `['freight 0.00', 'invoice 30.00']` |
| `carrier` | a gateway that books nothing | `['carrier {}']` |
| `clearance` | a clearance that returns zero duty | `['duty 0.00', 'invoice 5.63']` |
| `tracking` | a signal nothing subscribes to | `['tracking']` |

A missing rating shows twice, in the freight and in the invoice total built from it. Delete the helper's tracking check and the `tracking` case fails, because the helper no longer reports what that stage's absence causes.

Harry Percival and Bob Gregory's *Architecture Patterns with Python* weighs the trade-offs of tests at different levels in the chapter "TDD in High Gear and Low Gear". Here one acceptance test sits above a test per part, and the rows of the next table name them. When the acceptance test goes red it says which stage; the part's own test says why.

## The parts, each from an earlier chapter

Each part is a pattern the book has already taught, so each gets a row and a pointer. The table also names three patterns the slice leaves out and the chapter where each would attach.

| Part | Pattern | Module | Test | Chapter |
| --- | --- | --- | --- | --- |
| `PricingRule`, `per_kg` | Strategy | `rating.py` | `test_the_pricing_rule_is_chosen_at_the_composition_root` | [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) |
| `FastlineGateway` | Adapter | `carriers.py` | `test_the_adapter_sends_fastline_grams_and_returns_its_reference` | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| `ClearanceStage` chain | Chain of Responsibility | `clearance.py` | `test_clearance_stops_at_the_first_stage_that_holds` | [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) |
| `Signal`, `TrackingHistory` | Observer | `tracking.py` | `test_a_booking_request_ships_end_to_end` | [Observer]({{ '/docs/22-observer/' | relative_url }}) |
| `BookingDesk.ship` | Facade | `desk.py` | `test_a_booking_request_ships_end_to_end` | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| `Money`, `Weight` | Value object | `domain.py` | `test_an_invoice_in_two_currencies_has_no_total`, `test_a_weight_must_be_positive` | [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) |
| Status moving through a consignment's life | State, left out | none | none | [State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}) |
| A caching wrapper around the carrier gateway | Proxy, left out | none | none | [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) |
| Amending a booking, with undo | Command, left out | none | none | [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) |

None of the parts needed a framework. The pricing rule and the clearance stages are callables, the carrier is a Protocol with one adapter over the SDK stand-in, and the signal is a list of subscribers. Removing the subscription from `build_desk` fails `test_a_booking_request_ships_end_to_end` and no other test, so that is the test the Observer and Facade rows credit.

## Undo in reverse with ExitStack

A step that succeeded has to be taken back when a later step refuses, and the desk gets the means from a stack of inverses: each step registers the function that reverses it as soon as it succeeds, and a refusal runs them newest first. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) pairs each amendment with the amendment that reverses it. Here the inverse is a function and its argument, kept on a stack, with no command class. `contextlib.ExitStack` holds the stack. [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) uses it for resources; `callback` and `pop_all` are new here.

<!-- fmt:off -->
```python
    def ship(self, request: BookingRequest, /) -> Shipment:
        consignment = request.consignment
        rate = quote(consignment, rule=self._rule)
        with ExitStack() as undo:
            slot = self._plan.reserve(consignment.id)
            undo.callback(self._plan.release, slot)
            reference = self._gateway.book(consignment)
            undo.callback(self._gateway.cancel, reference)
            declaration = self._clear(declare(consignment))
            undo.pop_all()
        invoice = Invoice(
            consignment.id,
            (LineItem("freight", rate.total), LineItem("duty", declaration.duty)),
        )
        self._events.publish(
            HandlingEvent(consignment.id, HandlingKind.BOOKED, self._plan.sailing.origin)
        )
        return Shipment(rate, slot, reference, declaration, invoice)
```
<!-- fmt:on -->

The [`contextlib` documentation](https://docs.python.org/3/library/contextlib.html) gives the three facts the method relies on. For the stack: "Each instance maintains a stack of registered callbacks that are called in reverse order when the instance is closed (either explicitly or implicitly at the end of a with statement)." For `callback`: "Accepts an arbitrary callback function and arguments and adds it to the callback stack." For `pop_all`: "Transfers the callback stack to a fresh ExitStack instance and returns it." and "No callbacks are invoked by this operation". In `ship`, `pop_all()` is the commit. It moves the callbacks to a fresh stack that nothing closes, so leaving the `with` block runs none of them. The page adds that callbacks aren't run on collection either: "Note that callbacks are not invoked implicitly when the context stack instance is garbage collected." It also says "Unlike the other methods, callbacks added this way cannot suppress exceptions (as they are never passed the exception details)." The refusal therefore reaches the caller as the `ClearanceHeldError` it was.

Four tests pin the rule. A held declaration, CN-2 with the unknown HS code `9999.99`, raises `ClearanceHeldError`, and afterwards the plan holds no reservation and the client no open receipt (`test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking`). Recording wrappers around the real plan and gateway append to one log before they delegate, and after the same refusal the log reads `["cancel", "release"]`:

```python
def test_the_undo_runs_in_reverse_order_of_the_steps(
    recording_parts: RecordingParts, held_request: BookingRequest
) -> None:
    """The slot is reserved, then the carrier booked: the carrier is cancelled first."""
    with pytest.raises(ClearanceHeldError):
        _desk(recording_parts).ship(held_request)

    assert recording_parts.log == ["cancel", "release"]
```

The slot was reserved first and the carrier booked second, so the carrier is cancelled first. With these stand-ins either order leaves the same final state, and that's why this test is the one that pins the rule: replace the `ExitStack` with a `try/except` that releases and then cancels, and it is the only test that fails.

A full sailing refuses at `reserve`, before the carrier is asked. `client.open` is empty and the next receipt is still `FL-1001`, so the booking was never made, rather than made and cancelled (`test_a_full_sailing_books_nothing_with_the_carrier`). That is why `reserve` comes before `book`: swap them and that test fails along with the order test. Once a rollback has run, the slot is free again, and the next request takes `SlotId(1, 1, 1)` (`test_the_next_request_takes_the_slot_a_rollback_freed`).

## Publish after the commit

An event can't be taken back. The desk can undo the steps it owns because it holds a function that reverses each, but `Signal` offers `subscribe` and `publish` and nothing to retract an event, and a subscriber that has received an event keeps it. So the desk publishes once, after `pop_all()` has committed the booking and the invoice is built: the last statements of `ship` above.

A held booking then leaves no event. After the same refusal as before, `history.events` is `()` (`test_a_held_booking_publishes_no_tracking_event`). The comparison form is `_EagerBookingDesk` in `tests/conftest.py`. It runs the same steps and publishes inside the `with` block, before clearance:

<!-- fmt:off -->
```python
        with ExitStack() as undo:
            slot = self._plan.reserve(consignment.id)
            undo.callback(self._plan.release, slot)
            reference = self._gateway.book(consignment)
            undo.callback(self._gateway.cancel, reference)
            self._events.publish(
                HandlingEvent(consignment.id, HandlingKind.BOOKED, self._plan.sailing.origin)
            )
            declaration = clear(declare(consignment))
            undo.pop_all()
```
<!-- fmt:on -->

The `publish_form` fixture selects the form for each test, and both get the same held request. With the eager form the history holds one `BOOKED` event for CN-2 while the client has no open receipt: tracking reports a booking the carrier doesn't have (`test_an_eager_publisher_reports_a_booking_that_was_rolled_back`). The rule is that effects other parts can see go after `pop_all()`. The second experiment below moves the line in the real desk and shows the other test fail.

## One composition root

The desk takes its collaborators as keyword parameters, so it never decides which carrier or which pricing rule it has. Something has to decide, and the fewer places that do, the fewer places change when a carrier does. In this slice that place is `build_desk`:

```python
def build_desk(
    *,
    client: FastlineClient,
    plan: SlotPlan,
    history: TrackingHistory,
    rule: PricingRule = per_kg,
) -> BookingDesk:
    """Choose the carrier, the pricing rule and the subscriber, then hand the desk its parts."""
    events = Signal[HandlingEvent]()
    events.subscribe(history.record)
    return BookingDesk(rule=rule, plan=plan, gateway=FastlineGateway(client), events=events)
```

Two tests keep the choice there. `test_only_the_composition_root_names_a_concrete_carrier` parses each module of the package except `carriers.py` with `ast` and lists the ones that import or use `FastlineGateway` or `FastlineClient`. The list is `["app.py"]`, and importing the gateway into `desk.py` adds that module to it. `test_the_pricing_rule_is_chosen_at_the_composition_root` sends the same request through `build_desk` with a flat rule of 10.00 and then with a rule of two euros a kilogram. The freight is 10.00 and then 25.0, and the invoices are 40.00 and then 55.0.

mypy guards the other seam. A gateway class with `book` and no `cancel`, passed as `gateway=`, is reported as `[arg-type]` with a message that names `CarrierGateway`, and the same class with `cancel` passes (`test_mypy_refuses_a_gateway_without_cancel`). The check depends on the annotation: with `gateway` annotated as `object`, that test fails and `mypy --strict src` reports two `[attr-defined]` errors in `desk.py` instead. A `cancel` that has no effect satisfies mypy, and the held-declaration test is what sees it: with `FastlineClient.void` emptied, that test and the eager-publisher test fail.

[ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) teaches the principle. *Architecture Patterns with Python* gives it a chapter, "Dependency Injection (and Bootstrapping)", which adds a `bootstrap.py` to take charge of dependency injection and links it to the composition root idea.

## Billing closes the slice

No earlier example builds an invoice, so Billing is built here. An `Invoice` holds `LineItem`s, for freight and for duty, and its `total` adds them through `Money.__add__`, which refuses to add two currencies. An invoice with a euro line and a dollar line has no total: reading it raises `ValueError` with `cannot add USD to EUR` (`test_an_invoice_in_two_currencies_has_no_total`). `settle` accepts a payment equal to the total. 35.63 settles CN-1's invoice (`test_the_shipment_settles_for_the_invoice_total`), 35.00 raises `SettlementError` with `35.00 does not settle 35.63` (`test_a_short_payment_does_not_settle`) and 36.00 raises it with `36.00 does not settle 35.63` (`test_an_overpayment_does_not_settle`).

## When the composition is the wrong shape

A stack of undo callbacks fits a handful of steps in one process. With one step there's nothing to unwind in order, and a plain context manager is enough. When the steps cross a process or a network, the `ExitStack` holds its callbacks in the memory of the process that runs it, and the stand-in plan and client keep their state in memory too. A booking that has to survive a restart would need the record of what to undo stored somewhere that outlives the process. *Architecture Patterns with Python* covers the Unit of Work pattern, its abstraction over atomic operations, in the chapter "Unit of Work Pattern". When a step can't be undone, a callback doesn't help. `CarrierGateway` asks for `cancel`, and a carrier that can't cancel needs a different design, because the callback would have nothing to call.

<blockquote class="ai-sidebar" markdown="1">

**Adding a stage to the booking.** "Add an insurance step" names no place for the undo or for the event. Paste a prompt that keeps the slice's rules:

> Add the step inside the `ExitStack` in `BookingDesk.ship`, after the carrier booking and before clearance, and register its inverse with `undo.callback`. Publish nothing before `undo.pop_all()`. Take the new collaborator as a keyword parameter of `BookingDesk` and choose it only in `build_desk`. Extend `acceptance_failures` with the step's expected result, and add a held-declaration test that shows the step undone.

If the diff imports a concrete class outside `app.py`, ask why the composition root didn't choose it.

</blockquote>

## Build, run, observe

From the repository root, run `uv sync --locked --all-packages` once. Then, in `examples/39-final-project`, `uv run pytest -v` runs 19 test functions as 23 cases, and `uv run mypy --strict src tests` checks the example:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 23 items

tests/test_acceptance.py::test_a_booking_request_ships_end_to_end PASSED [  4%]
tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[rating] PASSED [  8%]
tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[carrier] PASSED [ 13%]
tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[clearance] PASSED [ 17%]
tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[tracking] PASSED [ 21%]
tests/test_acceptance.py::test_the_shipment_settles_for_the_invoice_total PASSED [ 26%]
tests/test_parts.py::test_the_adapter_sends_fastline_grams_and_returns_its_reference PASSED [ 30%]
tests/test_parts.py::test_clearance_stops_at_the_first_stage_that_holds[empty] PASSED [ 34%]
tests/test_parts.py::test_clearance_stops_at_the_first_stage_that_holds[unknown] PASSED [ 39%]
tests/test_parts.py::test_the_pricing_rule_is_chosen_at_the_composition_root PASSED [ 43%]
tests/test_parts.py::test_a_short_payment_does_not_settle PASSED         [ 47%]
tests/test_parts.py::test_an_overpayment_does_not_settle PASSED          [ 52%]
tests/test_parts.py::test_an_invoice_in_two_currencies_has_no_total PASSED [ 56%]
tests/test_parts.py::test_a_weight_must_be_positive PASSED               [ 60%]
tests/test_parts.py::test_an_unknown_zone_has_no_rate PASSED             [ 65%]
tests/test_rollback.py::test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking PASSED [ 69%]
tests/test_rollback.py::test_the_undo_runs_in_reverse_order_of_the_steps PASSED [ 73%]
tests/test_rollback.py::test_a_full_sailing_books_nothing_with_the_carrier PASSED [ 78%]
tests/test_rollback.py::test_the_next_request_takes_the_slot_a_rollback_freed PASSED [ 82%]
tests/test_static.py::test_mypy_refuses_a_gateway_without_cancel PASSED  [ 86%]
tests/test_structure.py::test_only_the_composition_root_names_a_concrete_carrier PASSED [ 91%]
tests/test_tracking.py::test_a_held_booking_publishes_no_tracking_event[after-commit] PASSED [ 95%]
tests/test_tracking.py::test_an_eager_publisher_reports_a_booking_that_was_rolled_back[eager] PASSED [100%]

============================== 23 passed in 0.90s ==============================
```

```text
Success: no issues found in 17 source files
```

Each experiment below runs in a scratch copy of the repository: delete the copy's `.venv`, run `uv sync --locked --all-packages` from its root and check that `final_project.__file__` points into the copy. Both use this filter, then mypy:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'
uv run mypy --strict src tests
```

The first removes the commit. In `src/final_project/desk.py`, delete the line `undo.pop_all()`. The two commands print:

```text
E       AssertionError: assert ['slot', 'carrier {}'] == []
E         Left contains 2 more items, first extra item: 'slot'
E         Use -v to get more diff
tests/test_acceptance.py:102: AssertionError
E       AssertionError: assert ['freight 0.0... 'carrier {}'] == ['freight 0.0...nvoice 30.00']
E         Left contains 2 more items, first extra item: 'slot'
E         Use -v to get more diff
tests/test_acceptance.py:120: AssertionError
E       AssertionError: assert ['slot', 'carrier {}'] == ['carrier {}']
E         At index 0 diff: 'slot' != 'carrier {}'
E         Left contains one more item: 'carrier {}'
E         Use -v to get more diff
tests/test_acceptance.py:120: AssertionError
E       AssertionError: assert ['duty 0.00',... 'carrier {}'] == ['duty 0.00', 'invoice 5.63']
E         Left contains 2 more items, first extra item: 'slot'
E         Use -v to get more diff
tests/test_acceptance.py:120: AssertionError
E       AssertionError: assert ['slot', 'car...', 'tracking'] == ['tracking']
E         At index 0 diff: 'slot' != 'tracking'
E         Left contains 2 more items, first extra item: 'carrier {}'
E         Use -v to get more diff
tests/test_acceptance.py:120: AssertionError
FAILED tests/test_acceptance.py::test_a_booking_request_ships_end_to_end - As...
FAILED tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[rating]
FAILED tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[carrier]
FAILED tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[clearance]
FAILED tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out[tracking]
5 failed, 18 passed in 0.99s
Success: no issues found in 17 source files
```

Five cases fail and 18 pass: the end-to-end test and the four cases of the left-out test. The booking is made and then undone: with no `pop_all()`, leaving the `with` block closes the stack normally and runs both callbacks, so the helper finds no slot and no carrier receipt. The first failure shows it, `['slot', 'carrier {}']` where `[]` was expected. The four stage cases fail the same way: each list gains `slot` and, in every case but `carrier`, whose stand-in never booked anything, `carrier {}`. The rollback and tracking tests all pass. mypy exits 0, because removing the call is type-correct.

The second restores that file and moves the `self._events.publish(...)` statement, all three lines of it, to just after `slot = self._plan.reserve(consignment.id)`, inside the `with` block. The same two commands print:

```text
E       AssertionError: assert (HandlingEven...ion='NLRTM'),) == ()
E         Left contains one more item: HandlingEvent(consignment_id='CN-2', kind=<HandlingKind.BOOKED: 1>, location='NLRTM')
E         Use -v to get more diff
tests/test_tracking.py:33: AssertionError
FAILED tests/test_tracking.py::test_a_held_booking_publishes_no_tracking_event[after-commit]
1 failed, 22 passed in 0.94s
Success: no issues found in 17 source files
```

One test fails: a held booking now leaves a `BOOKED` event for CN-2 in the history. Everything else passes, including the eager-publisher test, which already expected the early event, and mypy exits 0 again, because publish order isn't a type.

## What you can do now

- Write the acceptance test first: `acceptance_failures` collects what a shipment lacks, and `test_the_acceptance_test_fails_when_a_stage_is_left_out` shows it naming each of four missing stages.
- Wire the areas through one root: `build_desk` chooses the carrier, the subscriber and the pricing rule, and `test_only_the_composition_root_names_a_concrete_carrier` lists only `app.py`.
- Undo in reverse: `ExitStack`, `undo.callback` and `pop_all` in `BookingDesk.ship`, with `test_the_undo_runs_in_reverse_order_of_the_steps` pinning the order.
- Order the effects: `test_a_held_booking_publishes_no_tracking_event` holds the desk to publishing after the commit, and `_EagerBookingDesk` shows the report of a booking that never happened.
- Place each part: the parts table names the pattern, the module and the test for each, and the three left-out rows say where State, Proxy and Command would attach.

## For deeper coverage

The [`contextlib` documentation](https://docs.python.org/3/library/contextlib.html) describes `ExitStack`, `callback` and `pop_all`. Harry Percival and Bob Gregory's *Architecture Patterns with Python* (2020) has three chapters that bear on this one: "TDD in High Gear and Low Gear" for the levels of test, "Dependency Injection (and Bootstrapping)" for the composition root and "Unit of Work Pattern" for the persistent form of commit and rollback. [Working with AI and LLM tools]({{ '/docs/40-working-with-ai-and-llm-tools/' | relative_url }}) is the related title. The book is listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
