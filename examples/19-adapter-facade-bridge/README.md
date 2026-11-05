# Adapter, Facade, and Bridge

Two carrier SDKs of different shapes behind one `CarrierGateway`, a desk function
over them, and booking kinds that vary independently of the carriers. The chapter's thesis is
that all three patterns survive, each lighter than in 1994: structural typing removes an adapter
only where the shapes and the units already agree, a module function is a facade, and a Bridge is
the decision about two axes of variation joined by a narrow Protocol. Rates, limits, tracking
numbers and SDK shapes are illustrative.

## What it witnesses

Adapter.

- `AircoClient` has the shape of the `CarrierGateway` Protocol and is registered as it is.
  `FastlineClient` does not: it takes a payload of strings in pounds and returns a numeric
  receipt, and its cover call takes cents. mypy rejects it where a `CarrierGateway` is expected.
- `FastlineGateway` is an object adapter. It sends the weight in pounds, quantised to hundredths,
  builds the `FL-` reference, turns `FastlineRejectedError` into `CarrierError` and converts cover
  to cents. The pound comes from `POUND_IN_KILOGRAMS`, the international pound of 1959
  (0.45359237 kg, exact), through `Weight.from_pounds` and `Weight.pounds`.
- A class adapter (`_FastlineClassAdapter(FastlineClient)`) is a fixture in `tests/conftest.py`.
  It passes the same booking table as the object adapter and leaves `submit_shipment` reachable
  on the adapter.
- A client with the right shape but its units in a `float` is accepted by mypy. Typing the
  parameter as `Weight` makes the same client an `[assignment]` error. The `float` snippet in
  `test_static.py` is a reduced model and does not import the package.

Facade.

- `desk.ship` is one call that picks the gateway from a read-only `frozendict`, chooses
  `StandardBooking` or `InsuredBooking`, and turns an unknown code into `UnknownCarrierError`.
  `desk.__all__` and the type hints of its functions name no type from `sdks`.
- `_book_by_branching`, a fixture, is the caller that branches on the carrier code. It sends the
  kilogram figure as pounds, so a 10 kg consignment books as 10 lb.

Bridge.

- `StandardBooking` and `InsuredBooking` are frozen dataclasses that hold a gateway and use its
  two primitives, `book` and `insure`. Every kind works with every carrier. A class per kind and
  carrier is a fixture (`_CarrierBooking` and four subclasses) that passes the same table, and a
  test counts the classes with `ast`: two in `bookings.py`, five in the fixture.
- An insured booking records the declared value and refuses one that is not positive. A gateway
  without `insure` is an `[assignment]` error, which is the cost of widening or narrowing the
  implementor's Protocol.

## Layout

- `src/adapter_facade_bridge/domain.py`: `ConsignmentId`, `POUND_IN_KILOGRAMS`, `Weight`, `Money`,
  `Consignment`, `Booking`, `BookingError`, `CarrierError`, `UnknownCarrierError`.
- `src/adapter_facade_bridge/sdks.py`: `AircoClient`, `FastlineClient`, `FastlineReceipt`,
  `FastlineRejectedError`.
- `src/adapter_facade_bridge/gateways.py`: the `CarrierGateway` Protocol and `FastlineGateway`.
- `src/adapter_facade_bridge/bookings.py`: `StandardBooking` and `InsuredBooking`.
- `src/adapter_facade_bridge/desk.py`: `default_gateways` and `ship`.

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

`tests/test_adapter.py`

- `test_a_client_whose_shape_matches_needs_no_adapter`: the Airco client sits in the registry unwrapped and books.
- `test_the_fastline_adapter_translates_the_booking_call`: both adapter forms send `{"ref": "CN-1", "weight_lb": "22.05"}`.
- `test_a_class_adapter_still_exposes_the_clients_own_methods`: `submit_shipment` is on the class adapter and not on `FastlineGateway`.
- `test_weight_converts_between_kilograms_and_pounds_exactly`: one pound is the exact factor, and 10 kg reads 22.05 lb.
- `test_a_pounds_api_called_with_kilograms_books_the_wrong_weight`: the branching caller sends "10", which reads back as 4.54 kg.
- `test_an_unknown_carrier_is_refused_at_the_desk`: `UnknownCarrierError` with the original `KeyError` suppressed.
- `test_the_desk_registry_is_read_only`: item assignment raises `TypeError` and the registry is not a `dict`.
- `test_a_consignment_weight_must_be_positive_and_finite`: zero, negative and NaN.

`tests/test_facade.py`

- `test_ship_books_each_carrier_through_one_call`: the booking and what each SDK recorded, for both carriers.
- `test_the_desk_names_no_sdk_type_in_its_public_surface`: `__all__` and the resolved type hints.
- `test_a_carrier_rejection_becomes_a_carrier_error`: the cause is the `FastlineRejectedError`.

`tests/test_bridge.py`

- `test_every_booking_kind_works_with_every_carrier`: bridge and class-per-pair, two kinds, two carriers.
- `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`: an `ast` count.
- `test_an_insured_booking_records_the_declared_value_with_the_carrier`: Airco's `insure` record and Fastline's cover in cents.
- `test_an_insured_booking_without_a_declared_value_is_a_booking_error`: zero and negative.

`tests/test_static.py`

- `test_mypy_accepts_a_client_whose_shape_matches_the_protocol`: clean.
- `test_mypy_rejects_a_client_with_a_different_shape`: `[assignment]` for `FastlineClient`.
- `test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float`: clean (a reduced model).
- `test_mypy_rejects_a_float_where_a_weight_belongs`: `[assignment]`, with `Weight` in the output.
- `test_mypy_reports_an_implementor_missing_a_primitive`: `[assignment]`, naming the protocol member.

Classes and functions named with a leading underscore in `tests/conftest.py` are test fixtures
and aren't part of the model code.
