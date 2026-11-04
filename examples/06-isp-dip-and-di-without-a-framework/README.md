# ISP, DIP and dependency injection without a framework

One booking service and one tracking function, thirteen tests. Each test witnesses a claim about
the interface-segregation and dependency-inversion principles and about wiring collaborators
without a container. The carriers are in-memory adapters for the fictional codes `FASTLINE` and
`AIRCO`.

## What it witnesses

Interface segregation: a consumer depends on the smallest Protocol it uses.

- `BookingGateway` (`book`, `cancel`) and `TrackingGateway` (`track`) are each declared by the
  module that consumes them. `CarrierGateway` combines both for the code that wires a whole carrier.
- `FastlineGateway` and `AircoGateway` have no base class and name no Protocol, yet satisfy all
  three, which the member's `mypy --strict` run checks on typed assignments.
- A fake that implements only `track` is rejected where `CarrierGateway` is required, listing
  `book, cancel` as missing, and accepted by `tracking_history`.

Dependency inversion: the policy names the abstraction, not the adapter.

- `BookingService` runs against an injected fake, with no carrier built.
- `booking` and `tracking` import neither `carriers` nor `app`, and `carriers` imports neither
  policy module nor `app`. The tests read each module's imports with `ast`.
- An autospec of the wrong Protocol is accepted by `mypy --strict` because a mock is `Any`; at
  runtime the autospec rejects the missing method and the wrong call shape.

Composition root: one plain function chooses the adapter.

- `build_app` builds one gateway and gives it to `BookingService` as a field and to
  `tracking_history` through `functools.partial`.
- mypy checks the argument bound into a `partial` and the call through it, but not the
  assignment of a `partial` to a `Callable` annotation.
- Switching carrier changes no consumer, a substitute mapping replaces the adapters without
  patching, and an unknown carrier code fails at start-up with `ValueError`.

`HandlingEvent` is one class with a `HandlingKind` enum, because nothing here dispatches on the
kind and a union of five classes would add names without adding a check.

## Layout

- `src/isp_dip_di/domain.py`: `ConsignmentId`, `Weight`, `Consignment`, `BookingRequest`,
  `HandlingKind`, `HandlingEvent`, `TrackingHistory`.
- `src/isp_dip_di/booking.py`: `BookingGateway`, `AuditSink`, `BookingService`.
- `src/isp_dip_di/tracking.py`: `TrackingGateway`, `tracking_history`.
- `src/isp_dip_di/carriers.py`: `FastlineGateway`, `AircoGateway`.
- `src/isp_dip_di/app.py`: `CarrierGateway`, `GATEWAYS`, `App`, `build_app`.

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

`tests/test_isp.py`

- `test_adapters_satisfy_every_role_without_naming_one`: both adapters are assigned to
  `BookingGateway`, `TrackingGateway` and `CarrierGateway`, no Protocol is in their MRO, and a
  booking is then visible through tracking as one BOOKED event at the origin.
- `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`: a track-only class passed as a
  `CarrierGateway` fails with `[arg-type]` naming `book, cancel`, the same class passes to
  `tracking_history`, and the function returns the fake's events.

`tests/test_dip.py`

- `test_booking_service_runs_against_an_injected_fake`: the reference, the recorded request and
  the audit record all come from the fake and the service, with no adapter built.
- `test_policy_modules_do_not_import_the_adapters`: neither `booking` nor `tracking` imports
  `carriers` or `app`.
- `test_adapters_import_neither_policy_nor_protocols`: `carriers` imports none of `booking`,
  `tracking` or `app`.
- `test_autospec_bypasses_mypy`: an autospec of `TrackingGateway` passed as the booking gateway
  type-checks with no output.
- `test_autospec_enforces_the_protocol_shape_at_runtime`: the wrong autospec raises
  `AttributeError` for `cancel` and `TypeError` for a call missing its argument, and a
  `BookingGateway` autospec records the `cancel` call.
- `test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment`: binding a non-gateway
  and calling with an `int` give `[arg-type]`, and assigning to `Callable[[int], TrackingHistory]`
  is clean. That last result records a current mypy limitation.

`tests/test_composition_root.py`

- `test_build_app_shares_one_gateway_between_booking_and_tracking`: the service and the bound
  `gateway=` argument are the same object.
- `test_partial_injects_a_collaborator_into_a_function`: the tracking function is a `partial` of
  `tracking_history`, and it reports the booking made through the service.
- `test_swapping_the_carrier_changes_no_consumer`: `FASTLINE` and `AIRCO` produce prefixed
  references through the same `BookingService` and `tracking_history`.
- `test_composition_root_accepts_a_substitute_without_patching`: a `gateways=` mapping wires a
  fake carrier and leaves `GATEWAYS` unchanged.
- `test_unknown_carrier_fails_at_the_composition_root`: an unknown code raises `ValueError`
  naming it.

The fakes are defined in the test module that uses them and are not part of the model code.
