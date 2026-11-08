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

A booking is several steps that each change something outside the desk. Rating only produces a number, but reserving a slot changes a sailing, booking the carrier changes the carrier's books, and a tracking event changes what its subscribers know. Each step on its own is a pattern you've already met. What happens between the steps is the new question: a booking that customs holds has already taken a slot and a carrier booking, and the desk has to give both back.

When nothing answers it, two things go wrong:

- **No undo.** A held booking leaves the slot reserved and the carrier holding a receipt nobody pays for.
- **An eager publisher.** Tracking reports a booking that never happened.

The slice is one booking through the seven domain areas (Consignment, Rating, Routing, Carrier, Documentation, Billing and Tracking), with an in-memory stand-in for the carrier's SDK. The new questions sit where the parts meet: which steps can be undone and in what order, which effect waits for the commit, and which single function chooses the concrete parts.

{% include excalidraw.html name="39-final-project" described="true" caption="Figure 39.1: One booking through the desk's steps. A completed step registers its undo on an exit stack, a held declaration unwinds them in reverse, and the tracking event is published after the commit." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-39-final-project" markdown="1">
From the top. A column of boxes runs down the left: `BookingRequest`, an accent box `BookingDesk.ship (Facade)`, then `quote: PricingRule`, `StowagePlan.reserve, undo: release`, `CarrierGateway.book, undo: cancel`, `clear: ClearanceStage chain`, `undo.pop_all(): commit`, `Invoice from LineItems` and `Signal.publish(BOOKED) to TrackingHistory`, each joined to the next by a downward arrow. Two arrows in the accent colour run from the reserve and book boxes to an accent box on the right, `ExitStack holds the undo callbacks`. A dashed arrow runs from the clear box to a dashed box, `Held: cancel, then release; nothing published`. A bar across the bottom reads `build_desk: the one place that chooses FastlineGateway`, with no arrow to it.
</div>
</details>

The figure follows one booking down the desk's steps, with the undo stack beside them and the publish after the commit.

## The slice and its acceptance test

An acceptance test says when the slice is whole, and it comes first: it fixes one request and the shipment that request has to produce, and the parts are built until it passes. The request is CN-1, 12.5 kg of green coffee (HS code `0901.21`, valued at 400.00 euros) from the EU zone to `SGSIN`. The rates are illustrative. The expected shipment:

| Field | Expected |
| --- | --- |
| Freight | 5.63 (12.5 kg at 0.45 a kilogram is 5.625, rounded half up) |
| Duty | 30.00 |
| Invoice | 35.63 |
| Slot | `SlotId(1, 1, 1)` |
| Carrier | one open receipt holding 12,500 grams |
| Tracking | one `BOOKED` event for `NLRTM` |

The expectations live in a helper that collects what's missing instead of stopping at the first miss:

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

The desk built by `build_desk`, the composition root below, ships the request and the list comes back empty. Because the list has a fixed order, a failing run says which stage is absent. Replace one stage with a stand-in that does nothing useful and the helper reports:

| Stage left out | Stand-in | The helper reports |
| --- | --- | --- |
| `rating` | a rule that returns 0.00 | `['freight 0.00', 'invoice 30.00']` |
| `carrier` | a gateway that books nothing | `['carrier {}']` |
| `clearance` | a clearance that returns zero duty | `['duty 0.00', 'invoice 5.63']` |
| `tracking` | a signal nothing subscribes to | `['tracking']` |

A missing rating shows twice, in the freight and in the invoice total built from it.

Harry Percival and Bob Gregory's *Architecture Patterns with Python* weighs tests at different levels in "TDD in High Gear and Low Gear". Here one acceptance test sits above a test per part. When the acceptance test goes red it says which stage; the part's own test says why.

## The parts, each from an earlier chapter

Each part is a pattern already taught, so each gets a row and a pointer. The last three rows are patterns the slice leaves out, and where each would attach.

| Part | Pattern | Module | Covered in |
| --- | --- | --- | --- |
| `PricingRule`, `per_kg` | Strategy | `rating.py` | [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) |
| `FastlineGateway` | Adapter | `carriers.py` | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| `ClearanceStage` chain | Chain of Responsibility | `clearance.py` | [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) |
| `Signal`, `TrackingHistory` | Observer | `tracking.py` | [Observer]({{ '/docs/22-observer/' | relative_url }}) |
| `BookingDesk.ship` | Facade | `desk.py` | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| `Money`, `Weight` | Value object | `domain.py` | [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) |
| Status moving through a consignment's life | State, left out | none | [State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}) |
| A caching wrapper around the carrier gateway | Proxy, left out | none | [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) |
| Amending a booking, with undo | Command, left out | none | [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) |

None of the parts needs a framework. The pricing rule and the clearance stages are callables, the carrier is a Protocol with one adapter over the SDK stand-in, and the signal is a list of subscribers.

## Undo in reverse with ExitStack

A step that succeeded has to be taken back when a later step refuses. Each step registers the function that reverses it as soon as it succeeds, and a refusal runs them newest first. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) pairs each amendment with its reverse; here the inverse is a function and its argument on a stack, with no command class. `contextlib.ExitStack` holds the stack. [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) uses it for resources; `callback` and `pop_all` are new here.

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

The [`contextlib` documentation](https://docs.python.org/3/library/contextlib.html) gives the facts `ship` relies on:

- **The stack:** "Each instance maintains a stack of registered callbacks that are called in reverse order when the instance is closed (either explicitly or implicitly at the end of a with statement)."
- **`callback`:** "Accepts an arbitrary callback function and arguments and adds it to the callback stack."
- **`pop_all`:** "Transfers the callback stack to a fresh ExitStack instance and returns it." and "No callbacks are invoked by this operation".
- **Collection:** "Note that callbacks are not invoked implicitly when the context stack instance is garbage collected."
- **Exceptions:** "Unlike the other methods, callbacks added this way cannot suppress exceptions (as they are never passed the exception details)."

`pop_all()` is the commit: it moves the callbacks to a fresh stack that nothing closes, so leaving the `with` block runs none of them. A refusal reaches the caller as the `ClearanceHeldError` it was.

What the rule gives:

- **A held declaration** (CN-2, unknown HS code `9999.99`) raises `ClearanceHeldError`, and afterwards the plan holds no reservation and the client no open receipt.
- **Reverse order.** The slot was reserved first and the carrier booked second, so the carrier is cancelled first: a recording log reads `["cancel", "release"]`. With these stand-ins either order leaves the same final state, so only the log pins it; a `try/except` that releases then cancels changes nothing else.
- **A full sailing** refuses at `reserve`, before the carrier is asked. `client.open` is empty and the next receipt is still `FL-1001`, so the booking was never made, rather than made and cancelled. That's why `reserve` comes before `book`.
- **A freed slot** is taken by the next request as `SlotId(1, 1, 1)`.

## Publish after the commit

An event can't be taken back. The desk can undo the steps it owns because it holds a function that reverses each, but `Signal` offers `subscribe` and `publish` and nothing to retract an event, and a subscriber keeps what it received. So the desk publishes once, after `pop_all()` has committed the booking and the invoice is built: the last statements of `ship` above. A held booking leaves `history.events` as `()`.

The comparison form, `_EagerBookingDesk` in `tests/conftest.py`, runs the same steps and publishes inside the `with` block, before clearance:

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

Given the same held request, its history holds one `BOOKED` event for CN-2 while the client has no open receipt: tracking reports a booking the carrier doesn't have. Effects other parts can see go after `pop_all()`.

## One composition root

The desk takes its collaborators as keyword parameters, so it never decides which carrier or pricing rule it has. Something has to decide, and the fewer places that do, the fewer change when a carrier does. Here that place is `build_desk`:

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

An `ast` scan of every module except `carriers.py` for `FastlineGateway` or `FastlineClient` finds only `app.py`; importing the gateway into `desk.py` adds that module to the list. The same request through `build_desk` with a flat rule of 10.00 quotes freight 10.00 and invoices 40.00; with two euros a kilogram, 25.0 and 55.0.

mypy guards the other seam. A gateway class with `book` and no `cancel`, passed as `gateway=`, is `[arg-type]` with a message naming `CarrierGateway`. The check depends on the annotation: with `gateway` annotated as `object`, `mypy --strict src` reports two `[attr-defined]` errors in `desk.py` instead. A `cancel` that does nothing satisfies mypy; only the held-declaration behaviour catches it.

[ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) teaches the principle. *Architecture Patterns with Python* gives it a chapter, "Dependency Injection (and Bootstrapping)", which adds a `bootstrap.py` to take charge of dependency injection and links it to the composition root idea.

## Billing closes the slice

Billing is built here. An `Invoice` holds `LineItem`s, for freight and for duty, and its `total` adds them through `Money.__add__`, which refuses to add two currencies: an invoice with a euro line and a dollar line raises `ValueError`, `cannot add USD to EUR`, when its total is read. `settle` accepts only a payment equal to the total:

| Payment on CN-1's 35.63 | Result |
| --- | --- |
| 35.63 | settled |
| 35.00 | `SettlementError`, `35.00 does not settle 35.63` |
| 36.00 | `SettlementError`, `36.00 does not settle 35.63` |

## When the composition is the wrong shape

- **One step.** There's nothing to unwind in order, and a plain context manager is enough.
- **Steps across processes or a network.** The `ExitStack` holds its callbacks in the memory of the process that runs it, as the stand-in plan and client hold their state. A booking that must survive a restart needs the record of what to undo stored somewhere that outlives the process. *Architecture Patterns with Python* covers that abstraction over atomic operations in "Unit of Work Pattern".
- **A step that can't be undone.** `CarrierGateway` asks for `cancel`; a carrier that can't cancel needs a different design, because the callback would have nothing to call.

<blockquote class="ai-sidebar" markdown="1">

**Adding a stage to the booking.** "Add an insurance step" names no place for the undo or for the event. Keep the slice's rules:

> Add the step inside the `ExitStack` in `BookingDesk.ship`, after the carrier booking and before clearance, and register its inverse with `undo.callback`. Publish nothing before `undo.pop_all()`. Take the new collaborator as a keyword parameter of `BookingDesk` and choose it only in `build_desk`. Extend `acceptance_failures` with the step's expected result, and add a held-declaration test that shows the step undone.

If the diff imports a concrete class outside `app.py`, ask why the composition root didn't choose it.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/39-final-project
uv run pytest -q
uv run mypy --strict src tests
```

All 23 cases pass and mypy is clean. Run each experiment in a scratch copy of the repository with its own `.venv`, and check that `final_project.__file__` points into the copy:

- **Remove the commit.** In `src/final_project/desk.py`, delete `undo.pop_all()`. Five acceptance cases fail: leaving the `with` block closes the stack and runs both callbacks, so the booking is made and then undone, and the helper reports `['slot', 'carrier {}']`. The rollback and tracking cases pass. mypy exits 0.
- **Publish early.** Restore the file and move the `self._events.publish(...)` statement to just after `slot = self._plan.reserve(consignment.id)`. One case fails: a held booking leaves a `BOOKED` event for CN-2 in the history. mypy exits 0, because publish order isn't a type.

## What you can do now

- Write the acceptance test first: `acceptance_failures` collects what a shipment lacks and names each of four missing stages.
- Wire the areas through one root: `build_desk` chooses the carrier, the subscriber and the pricing rule, and only `app.py` names a concrete carrier.
- Undo in reverse: `ExitStack`, `undo.callback` and `pop_all` in `BookingDesk.ship`.
- Order the effects: publish after the commit; `_EagerBookingDesk` shows the report of a booking that never happened.
- Place each part: the parts table names the pattern and module for each, and where State, Proxy and Command would attach.

## For deeper coverage

The [`contextlib` documentation](https://docs.python.org/3/library/contextlib.html) describes `ExitStack`, `callback` and `pop_all`. Harry Percival and Bob Gregory's *Architecture Patterns with Python* (2020) has three chapters that bear on this one: "TDD in High Gear and Low Gear" for the levels of test, "Dependency Injection (and Bootstrapping)" for the composition root and "Unit of Work Pattern" for the persistent form of commit and rollback. [Working with AI and LLM tools]({{ '/docs/40-working-with-ai-and-llm-tools/' | relative_url }}) is the related title. The book is listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
