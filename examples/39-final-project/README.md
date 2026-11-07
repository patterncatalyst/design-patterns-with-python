# Final project

One booking request, shipped through every domain area. A request is rated, a slot is reserved on a
sailing, the carrier booking is placed, customs clears the declaration, an invoice is raised and a
tracking event is published. Weights, rates and duties are illustrative, and the carrier is an
in-memory stand-in with no I/O.

## What it witnesses

`desk.py` holds `BookingDesk`, whose `ship` is the one call a caller makes. Inside a
`contextlib.ExitStack`, each step registers its inverse with `callback`: `release` for the slot,
`cancel` for the carrier booking. When customs holds the declaration, the stack runs the inverses in
reverse order, so the carrier booking is cancelled first and then the slot is released. `pop_all()`
transfers the callbacks away once clearance has passed, and the exit then runs none of them. The
`BOOKED` event is published after that.

`app.py` holds `build_desk`, the composition root. It wraps the `FastlineClient` in a
`FastlineGateway`, subscribes the `TrackingHistory`, and takes the pricing rule as a parameter. No
other module names the concrete carrier classes.

`rating.py` holds `PricingRule`, a callable type, and `per_kg`, which rounds half up to the cent.
`carriers.py` holds the `CarrierGateway` Protocol, the stand-in `FastlineClient` and the
`FastlineGateway` adapter, which sends the client grams and returns the receipt as a `FL-` reference.
`stowage.py` holds `StowagePlan`, which reserves a free tier and raises `StowageFullError`
when none is left. `clearance.py` holds `declare`, the stages `has_commodities` and `known_codes`,
and `clear`, which stops at the first stage that holds. `tracking.py` holds `Signal` and
`TrackingHistory`. `billing.py` holds `LineItem`, `Invoice`, `Settlement` and `settle`, which accepts
exactly the invoice total.

The acceptance helper `acceptance_failures` lists what a shipment is missing. Each of four stages,
replaced in turn by a stand-in that does nothing useful, produces its own exact list.

`tests/conftest.py` holds the one comparison form: `_EagerBookingDesk` publishes `BOOKED` before
clearance, so a held booking leaves a tracking event behind. The `publish_form` fixture selects it.

Two mypy checks run over small snippets: a gateway without `cancel` is refused where the desk
expects a `CarrierGateway`, and the same gateway with `cancel` is accepted.

## Layout

- `src/final_project/domain.py`: `ConsignmentId`, `Money`, `Weight`, `Commodity`, `Consignment`,
  `BookingRequest`, `Sailing`, `HandlingKind`, `HandlingEvent`.
- `src/final_project/rating.py`: `PricingRule`, `CENT`, `ZONE_RATES`, `RatingError`, `RateQuote`,
  `per_kg`, `quote`.
- `src/final_project/carriers.py`: `CarrierGateway`, `FastlineClient`, `FastlineGateway`.
- `src/final_project/stowage.py`: `SlotId`, `StowageFullError`, `SlotPlan`, `StowagePlan`.
- `src/final_project/clearance.py`: `CustomsDeclaration`, `Held`, `ClearanceHeldError`,
  `ClearanceStage`, `declare`, `has_commodities`, `known_codes`, `STAGES`, `clear`.
- `src/final_project/tracking.py`: `Signal`, `Subscriber`, `TrackingHistory`.
- `src/final_project/billing.py`: `LineItem`, `Invoice`, `Settlement`, `SettlementError`, `settle`.
- `src/final_project/desk.py`: `Shipment`, `BookingDesk`.
- `src/final_project/app.py`: `build_desk`.
- `tests/conftest.py`: the requests, a fresh world, the recording wrappers over the real plan and
  gateway, and the eager desk used for comparison.

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

`tests/test_acceptance.py`

- `test_a_booking_request_ships_end_to_end`: freight 5.63, duty 30.00, invoice 35.63, slot
  `SlotId(1, 1, 1)`, carrier receipt 1001 holding 12500 grams, and one `BOOKED` event.
- `test_the_acceptance_test_fails_when_a_stage_is_left_out`: for rating, carrier, clearance and
  tracking, with the exact list of failures for each.
- `test_the_shipment_settles_for_the_invoice_total`

`tests/test_rollback.py`

- `test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking`
- `test_the_undo_runs_in_reverse_order_of_the_steps`
- `test_a_full_sailing_books_nothing_with_the_carrier`: the next receipt is still 1001.
- `test_the_next_request_takes_the_slot_a_rollback_freed`

`tests/test_tracking.py`

- `test_a_held_booking_publishes_no_tracking_event`
- `test_an_eager_publisher_reports_a_booking_that_was_rolled_back`: the comparison form.

`tests/test_parts.py`

- `test_the_adapter_sends_fastline_grams_and_returns_its_reference`
- `test_clearance_stops_at_the_first_stage_that_holds`: for an empty declaration and for an
  unknown HS code, with a stage after the built-in ones that is never reached.
- `test_the_pricing_rule_is_chosen_at_the_composition_root`: two different rules give two different
  totals.
- `test_a_short_payment_does_not_settle`
- `test_an_overpayment_does_not_settle`
- `test_an_invoice_in_two_currencies_has_no_total`
- `test_a_weight_must_be_positive`
- `test_an_unknown_zone_has_no_rate`

`tests/test_structure.py`

- `test_only_the_composition_root_names_a_concrete_carrier`

`tests/test_static.py`

- `test_mypy_refuses_a_gateway_without_cancel`

The tests use no mocks and no patching, and none sleeps or reads a clock. A hold is forced by a
declaration that carries an unknown HS code, and the undo order is read from a log that the
recording wrappers append to before they delegate to the real classes.
