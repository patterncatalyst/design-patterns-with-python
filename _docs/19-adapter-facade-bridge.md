---
title: "Adapter, Facade, and Bridge"
order: 19
layout: tutorial
sectionid: docs
part: "composing-adapting-structure"
description: "Duck typing removes an adapter only where shapes and units already agree; a facade is often a module function, and a bridge separates two axes of variation behind a narrow Protocol."
---

## Learning objectives

By the end of this chapter you can:

- Say when structural typing removes an adapter, and what an object adapter still has to translate when the shape, the unit or the error differs.
- Show how pounds passed as kilograms through a `float` get past mypy, and how a `Weight` parameter stops them.
- Choose between an object adapter and a class adapter by what each leaks to its callers.
- Write a facade as a module function that names no SDK type.
- Split two axes of variation with a Bridge, count the classes saved, and name the cost that lands on the implementor.

## Why this matters

A shipping desk books consignments with two carriers. Their SDKs disagree about almost everything, and three failures follow.

A caller branches on the carrier code and reaches into each SDK. For Fastline it sends the consignment's weight, 10 kg, in a field that Fastline reads as pounds. The booking succeeds and the carrier holds a 4.54 kg consignment.

A client whose parameter is a plain `float` is accepted wherever a kilogram `float` is expected, because mypy sees two floats. The unit is in a parameter name, and mypy doesn't read names.

Booking kinds multiply with carriers. A standard booking and an insured booking, times two carriers, is four classes, and the two Fastline ones repeat Fastline's translation.

{% include excalidraw.html name="19-adapter-facade-bridge" caption="Figure 19.1: One call, two axes, one translation. The facade picks a gateway and a booking kind; each kind works through the narrow gateway Protocol, which one client already satisfies and the other reaches through an adapter that converts units." %}

Read the figure from the top down. An accent box, `ship(consignment, carrier, ...)`, is labelled "Facade: one call, domain types only". It forks to `StandardBooking` and `InsuredBooking`, each labelled "Bridge: each kind holds a gateway". Both lead to `CarrierGateway`, "book, insure: the narrow Protocol". That box forks again, to `AircoClient`, "shape already matches: no adapter", and to `FastlineGateway`, "Adapter: shape, pounds, errors". An arrow runs down from `FastlineGateway` to a dashed `FastlineClient`, "carrier SDK". A dashed `Weight.pounds`, "units converted in one place", has a dashed arrow into `FastlineGateway`.

## When no adapter is needed

The sorting question from [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) is whether a pattern dissolves, survives or shares its name with something else. All three patterns in this chapter survive. Each is lighter than in 1994, and each gets lighter in a different place: the adapter where the shapes already match, the facade in where it lives, the bridge in how the link is written.

The *Design Patterns* catalogue by Gamma, Helm, Johnson and Vlissides (1994) describes Adapter for two parts that disagree about shape: one calls, the other supplies, and an object between them translates. The book gives two forms, one that subclasses the supplier and one that holds it. The force survives in Python. What 1994 assumed about nominal interfaces, and what Python dissolves, is covered in [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}), and it applies here: when the supplier already has the shape, the adapter has nothing to do.

`AircoClient` has `book` and `insure` with the shape of the `CarrierGateway` Protocol, so the desk registers it as it is. `test_a_client_whose_shape_matches_needs_no_adapter` checks that `type(gateways["AIRCO"]) is AircoClient` and that a booking through it succeeds. `test_mypy_accepts_a_client_whose_shape_matches_the_protocol` assigns an `AircoClient()` to a `CarrierGateway` and mypy 2.4.1 prints nothing. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers the mechanism, including why the Protocol's parameters are positional-only.

The check runs against the Protocol and not against a base class. `AircoClient` doesn't import `CarrierGateway` or know it exists, and that's why a vendor's client can sit in the registry unchanged.

A client with a different shape is refused. `FastlineClient` has `submit_shipment` and `add_cover`, and `test_mypy_rejects_a_client_with_a_different_shape` assigns one to a `CarrierGateway`. The test's own snippet, run through the test's own helper, prints:

```text
<string>:5: error: Incompatible types in assignment (expression has type "FastlineClient", variable has type "CarrierGateway")  [assignment]
```

So duck typing removes an adapter where the shapes already match, and the type checker says where they don't. Whether the units inside the shapes match is a separate question.

## An adapter translates shape, units and errors

`FastlineGateway` is an object adapter. It holds a `FastlineClient`, offers the two Protocol methods with the SDK in its `client` field, and does three kinds of translation:

<!-- fmt:off -->
```python
class CarrierGateway(Protocol):
    """The two primitives that every booking kind is built from."""

    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str: ...

    def insure(self, reference: str, value: Money, /) -> None: ...


@dataclass(frozen=True, slots=True)
class FastlineGateway:
    """An object adapter: translates shape, units and errors behind the two Protocol methods."""

    client: FastlineClient

    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str:
        payload = {
            "ref": consignment_id,
            "weight_lb": str(weight.pounds.quantize(_HUNDREDTH, rounding=ROUND_HALF_UP)),
        }
        try:
            receipt = self.client.submit_shipment(payload)
        except FastlineRejectedError as error:
            raise CarrierError(f"FASTLINE rejected {consignment_id}: {error}") from error
        return f"{_FASTLINE_PREFIX}{receipt.tracking_number}"

    def insure(self, reference: str, value: Money, /) -> None:
        cents = int(value.amount.scaleb(2))
        number = int(reference.removeprefix(_FASTLINE_PREFIX))
        self.client.add_cover(number, cents, value.currency)
```
<!-- fmt:on -->

Callers see two methods and a `Weight`, and everything particular to Fastline stays behind `client`.

The shape: Fastline takes a payload of strings and returns a numeric receipt, and the adapter turns that into the `FL-` reference string the Protocol promises. `test_the_fastline_adapter_translates_the_booking_call` records the payload the SDK received, `{"ref": "CN-1", "weight_lb": "22.05"}`, and a second booking of 1.005 lb that rounds half up to `1.01`.

The unit: the pound is converted in one place, on the value type. `Weight` holds kilograms as a `Decimal`, a frozen value that refuses zero, negative and non-finite amounts, and `test_a_consignment_weight_must_be_positive_and_finite` checks all three. Pounds have one way in, `from_pounds`, and one way out, the `pounds` property.

<!-- fmt:off -->
```python
    @classmethod
    def from_pounds(cls, pounds: Decimal) -> Self:
        return cls(pounds * POUND_IN_KILOGRAMS)

    @property
    def pounds(self) -> Decimal:
        return self.kilograms / POUND_IN_KILOGRAMS
```
<!-- fmt:on -->

`test_weight_converts_between_kilograms_and_pounds_exactly` checks the factor, 0.45359237 kg to the pound, and that 10 kg reads 22.05 lb. `test_a_pounds_api_called_with_kilograms_books_the_wrong_weight` runs the branching caller from the opening: it sends `"10"` as `weight_lb`, and `Weight.from_pounds` reads that back as 4.54 kg.

The error: Fastline raises its own `FastlineRejectedError` for a shipment over its limit. The adapter raises `CarrierError` from it, so a caller depends on the domain's error and the SDK's stays as `__cause__`. `test_a_carrier_rejection_becomes_a_carrier_error` books 600 kg, which is about 1,323 lb against an illustrative limit of 1,000, and finds the cause attached. Cover goes the same way: `insure` turns a `Money` into integer cents, and `test_an_insured_booking_records_the_declared_value_with_the_carrier` sees `(1001, 25000, "EUR")` arrive at the SDK for 250.00 EUR.

The `float` case is where static checking runs out. `test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float` type-checks a client whose `book` takes `pounds: float` against a Protocol whose `book` takes `kilograms: float`. Exit status 0, no output. That snippet is a reduced model: it declares its own small Protocol and doesn't import the package, because the point is the two `float` parameters. When the Protocol says `Weight`, the same client is refused. `test_mypy_rejects_a_float_where_a_weight_belongs` prints:

```text
<string>:13: error: Incompatible types in assignment (expression has type "PoundsClient", variable has type "CarrierGateway")  [assignment]
<string>:13: note: Following member(s) of "PoundsClient" have conflicts:
<string>:13: note:     Expected:
<string>:13: note:         def book(self, ConsignmentId, Weight, /) -> str
<string>:13: note:     Got:
<string>:13: note:         def book(self, str, float, /) -> str
```

The class adapter is the other form. It subclasses the client and adds the two Protocol methods:

```python
# Comparison: a class adapter. Inheriting from the SDK client makes the client's own methods part
# of the adapter's public surface.
class _FastlineClassAdapter(FastlineClient):
    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str:
```

It passes the same booking table, because the `gateway_form` fixture runs the adapter test against both forms. It also leaks: `test_a_class_adapter_still_exposes_the_clients_own_methods` finds `submit_shipment` on the class adapter and not on `FastlineGateway`. So a caller holding the class adapter can call `submit_shipment` with a payload it builds itself and skip the translation. The object adapter has no `submit_shipment` of its own; a caller would have to reach through its public `client` field to skip the translation.

## A Facade is a function with a narrow surface

The *Design Patterns* catalogue gives Facade to a subsystem with many parts and a caller that wants a few operations. One object stands in front, so callers learn its few calls and not the parts. In Python a module already is that object. What survives is the choice of calls and the translation behind them.

<!-- fmt:off -->
```python
def ship(
    consignment: Consignment,
    carrier: str,
    *,
    gateways: Mapping[str, CarrierGateway],
    declared_value: Money | None = None,
) -> Booking:
    try:
        gateway = gateways[carrier]
    except KeyError:
        raise UnknownCarrierError(f"unknown carrier {carrier!r}") from None
    kind: StandardBooking | InsuredBooking
    if declared_value is None:
        kind = StandardBooking(gateway)
    else:
        kind = InsuredBooking(gateway, declared_value)
    return kind.place(consignment, carrier)
```
<!-- fmt:on -->

`test_ship_books_each_carrier_through_one_call` runs it for both carriers and compares the booking with what each SDK recorded. An unknown code is refused with the domain's own error, `test_an_unknown_carrier_is_refused_at_the_desk` matching `unknown carrier 'NOSUCH'`, and `from None` keeps the `KeyError` out of the report. The registry is a `frozendict` typed as a `Mapping`, so `test_the_desk_registry_is_read_only` finds that assigning into it raises `TypeError`.

`ship` takes a consignment and a carrier code and returns a `Booking`. It doesn't take a client or a payload, so a caller can't learn Fastline's units by using it, and the desk can replace an SDK without touching its callers. Declared value is an optional keyword, and its presence selects the booking kind, so the caller says what they want and the desk decides how it's carried out. A facade that returned `FastlineReceipt` would have narrowed the calls and kept the leak. `desk.__all__` lists `default_gateways` and `ship`, and `test_the_desk_names_no_sdk_type_in_its_public_surface` resolves their type hints and finds no class from the `sdks` module in them. The branching caller from the opening is what a desk looks like without that surface. For where `gateways` comes from, [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers the composition root.

## Bridge: two axes, one narrow Protocol

Gamma, Helm, Johnson and Vlissides give Bridge to a design with two things that vary, such as what an operation means and how it's carried out, so each can change without disturbing the other. Brandon Rhodes uses the same reading in [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/). His example subclasses a logger once per output and once per filter, which multiplies, and he resolves it with Adapter, Bridge and Decorator in turn. He quotes the Gang of Four principle as "Favor object composition over class inheritance." and concludes that the principle matters more than any one pattern. python-patterns.guide has no page named Adapter, Facade or Bridge, and The Composition Over Inheritance Principle is where it treats Adapter and Bridge.

Here the two axes are the booking kind and the carrier:

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True)
class StandardBooking:
    """Books the consignment and nothing else."""

    gateway: CarrierGateway

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        reference = self.gateway.book(consignment.id, consignment.weight)
        return Booking(carrier, reference)


@dataclass(frozen=True, slots=True)
class InsuredBooking:
    """Books the consignment, then insures it for the declared value."""

    gateway: CarrierGateway
    declared_value: Money

    def __post_init__(self) -> None:
        if self.declared_value.amount <= 0:
            raise BookingError(f"declared value must be positive, got {self.declared_value.amount}")

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        reference = self.gateway.book(consignment.id, consignment.weight)
        self.gateway.insure(reference, self.declared_value)
        return Booking(carrier, reference, self.declared_value)
```
<!-- fmt:on -->

The `gateway` field is a Protocol-typed attribute, the mechanism [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers. The decision is which axis is the abstraction and which narrow set of primitives the other side promises.

`test_every_booking_kind_works_with_every_carrier` runs two kinds against two carriers, in two designs, the bridge and a class per kind and carrier, as eight cases. Both designs pass. The difference is the class count. `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier` parses `bookings.py` with `ast` and finds two classes, and parses the fixture and finds five: an abstract base and four pairs, the two Fastline ones repeating its translation. That's N×M against N+M. A third kind adds one class to the bridge and one per carrier to the other design, and a third carrier adds one gateway to the bridge and one class per kind to the other. Which kind to build is a creation question, and [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) takes it up.

Insurance is the second primitive. `InsuredBooking` calls `book` and then `insure` on whichever gateway it holds, so the carrier's way of recording cover stays inside the gateway: Airco keeps the `Money` it was given, and Fastline's adapter turns it into cents. The bridge's two sides don't know each other's details.

An insured booking records the declared value with the carrier, and `test_an_insured_booking_without_a_declared_value_is_a_booking_error` shows zero and negative amounts refused at construction.

The cost sits on the implementor, and the benefit sits on the abstraction. A new booking kind is a class that calls the same two primitives, and no gateway changes: `test_a_new_booking_kind_needs_no_gateway_change` defines one in the test and runs it over both real gateways. A new primitive is a promise that each gateway has to keep. `test_mypy_reports_an_implementor_missing_a_primitive` assigns a class with `book` alone and prints:

```text
<string>:11: error: Incompatible types in assignment (expression has type "BookOnly", variable has type "CarrierGateway")  [assignment]
<string>:11: note: "BookOnly" is missing following "CarrierGateway" protocol member:
<string>:11: note:     insure
```

Keep the set small. The experiments below widen it by one method.

## When not to use it

Call the client when there's one carrier and the SDK already fits. An adapter that only renames parameters isn't needed, because the Protocol's parameters are positional-only. A facade over a subsystem with one caller can be inlined. A bridge where one axis doesn't vary is a parameter, and the second hierarchy is a cost with no return.

<blockquote class="ai-sidebar" markdown="1">
**Specifying an adapter.** "Integrate a carrier" leaves open which clients need an adapter, what units cross the boundary and what the caller sees of the SDK. Paste a prompt that states the form:

> Register a client that already satisfies `CarrierGateway` as it is. For one that doesn't, write an object adapter that holds the client, converts units through `Weight.pounds` and `Weight.from_pounds`, and raises `CarrierError` from the SDK's error. Write the facade as a module function, `ship`, whose signature names only domain types. Make booking kinds a bridge over the narrow Protocol, not a class per kind and carrier.

If a weight crosses as a `float`, ask for a `Weight` parameter.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/19-adapter-facade-bridge
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
collecting ... collected 35 items

tests/test_adapter.py::test_a_client_whose_shape_matches_needs_no_adapter PASSED [  2%]
tests/test_adapter.py::test_the_fastline_adapter_translates_the_booking_call[object-adapter] PASSED [  5%]
tests/test_adapter.py::test_the_fastline_adapter_translates_the_booking_call[class-adapter] PASSED [  8%]
tests/test_adapter.py::test_a_class_adapter_still_exposes_the_clients_own_methods PASSED [ 11%]
tests/test_adapter.py::test_weight_converts_between_kilograms_and_pounds_exactly PASSED [ 14%]
tests/test_adapter.py::test_a_pounds_api_called_with_kilograms_books_the_wrong_weight PASSED [ 17%]
tests/test_adapter.py::test_an_unknown_carrier_is_refused_at_the_desk PASSED [ 20%]
tests/test_adapter.py::test_the_desk_registry_is_read_only PASSED        [ 22%]
tests/test_adapter.py::test_a_consignment_weight_must_be_positive_and_finite[zero] PASSED [ 25%]
tests/test_adapter.py::test_a_consignment_weight_must_be_positive_and_finite[negative] PASSED [ 28%]
tests/test_adapter.py::test_a_consignment_weight_must_be_positive_and_finite[nan] PASSED [ 31%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[bridge-standard-FASTLINE] PASSED [ 34%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[bridge-standard-AIRCO] PASSED [ 37%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[bridge-insured-FASTLINE] PASSED [ 40%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[bridge-insured-AIRCO] PASSED [ 42%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[class-per-pair-standard-FASTLINE] PASSED [ 45%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[class-per-pair-standard-AIRCO] PASSED [ 48%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[class-per-pair-insured-FASTLINE] PASSED [ 51%]
tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier[class-per-pair-insured-AIRCO] PASSED [ 54%]
tests/test_bridge.py::test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier PASSED [ 57%]
tests/test_bridge.py::test_an_insured_booking_records_the_declared_value_with_the_carrier[FASTLINE] PASSED [ 60%]
tests/test_bridge.py::test_an_insured_booking_records_the_declared_value_with_the_carrier[AIRCO] PASSED [ 62%]
tests/test_bridge.py::test_an_insured_booking_without_a_declared_value_is_a_booking_error[zero] PASSED [ 65%]
tests/test_bridge.py::test_an_insured_booking_without_a_declared_value_is_a_booking_error[negative] PASSED [ 68%]
tests/test_bridge.py::test_a_new_booking_kind_needs_no_gateway_change[FASTLINE] PASSED [ 71%]
tests/test_bridge.py::test_a_new_booking_kind_needs_no_gateway_change[AIRCO] PASSED [ 74%]
tests/test_facade.py::test_ship_books_each_carrier_through_one_call[FASTLINE] PASSED [ 77%]
tests/test_facade.py::test_ship_books_each_carrier_through_one_call[AIRCO] PASSED [ 80%]
tests/test_facade.py::test_the_desk_names_no_sdk_type_in_its_public_surface PASSED [ 82%]
tests/test_facade.py::test_a_carrier_rejection_becomes_a_carrier_error PASSED [ 85%]
tests/test_static.py::test_mypy_accepts_a_client_whose_shape_matches_the_protocol PASSED [ 88%]
tests/test_static.py::test_mypy_rejects_a_client_with_a_different_shape PASSED [ 91%]
tests/test_static.py::test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float PASSED [ 94%]
tests/test_static.py::test_mypy_rejects_a_float_where_a_weight_belongs PASSED [ 97%]
tests/test_static.py::test_mypy_reports_an_implementor_missing_a_primitive PASSED [100%]

============================== 35 passed in 2.28s ==============================
Success: no issues found in 11 source files
```

The suite has 21 test functions and 35 cases. The shared method for the tests and the mypy witnesses is in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: send kilograms.** In a fresh scratch copy with its `.venv` removed and `uv sync --locked --all-packages` run, in `FastlineGateway.book` replace `weight.pounds` with `weight.kilograms`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` gives:

```text
E       AssertionError: assert [{'ref': 'CN-..._lb': '0.46'}] == [{'ref': 'CN-..._lb': '1.01'}]
tests/test_adapter.py:34: AssertionError
E       AssertionError: assert [{'ref': 'CN-...lb': '10.00'}] == [{'ref': 'CN-...lb': '22.05'}]
tests/test_facade.py:24: AssertionError
E       Failed: DID NOT RAISE CarrierError
FAILED tests/test_adapter.py::test_the_fastline_adapter_translates_the_booking_call[object-adapter]
FAILED tests/test_facade.py::test_ship_books_each_carrier_through_one_call[FASTLINE]
FAILED tests/test_facade.py::test_a_carrier_rejection_becomes_a_carrier_error
3 failed, 32 passed in 2.31s
Success: no issues found in 11 source files
```

Three tests fail. The object adapter's payload test sees `0.46` for the 1.005 lb booking, and the desk test sees `10.00` where it expected `22.05`. The third failure is less obvious: 600 kg sent as pounds is 600.00 lb, under the 1,000 lb limit, so Fastline accepts it and the rejection test finds nothing raised. The class adapter, which has its own copy of the conversion, keeps passing. mypy stays green, because a `Decimal` of kilograms and a `Decimal` of pounds have the same type.

**Experiment two: widen the Protocol.** In another fresh scratch copy, add `def cancel(self, reference: str, /) -> None: ...` to `CarrierGateway`. The same pytest filter, then the same mypy command, gives:

```text
E       assert 1 == 0
tests/test_static.py:96: AssertionError
E       assert 'note:     insure' in '<string>:11: error: Incompatible types in assignment (expression has type "BookOnly", variable has type "CarrierGatew...:11: note: "BookOnly" is missing following "CarrierGateway" protocol members:\n<string>:11: note:     cancel, insure\n'
tests/test_static.py:129: AssertionError
FAILED tests/test_static.py::test_mypy_accepts_a_client_whose_shape_matches_the_protocol
FAILED tests/test_static.py::test_mypy_reports_an_implementor_missing_a_primitive
2 failed, 33 passed in 2.48s
src/adapter_facade_bridge/desk.py:14: error: Dict entry 0 has incompatible type "str": "AircoClient"; expected "str": "CarrierGateway"  [dict-item]
src/adapter_facade_bridge/desk.py:14: error: Dict entry 1 has incompatible type "str": "FastlineGateway"; expected "str": "CarrierGateway"  [dict-item]
tests/test_adapter.py:22: error: Non-overlapping identity check (left operand type: "type[CarrierGateway]", right operand type: "type[AircoClient]")  [comparison-overlap]
tests/test_adapter.py:23: error: Statement is unreachable  [unreachable]
tests/conftest.py:54: error: Dict entry 0 has incompatible type "str": "AircoClient"; expected "str": "CarrierGateway"  [dict-item]
tests/conftest.py:54: error: Dict entry 1 has incompatible type "str": "FastlineGateway"; expected "str": "CarrierGateway"  [dict-item]
tests/conftest.py:115: error: Incompatible return value type (got "_FastlineClassAdapter", expected "CarrierGateway")  [return-value]
tests/conftest.py:115: note: "_FastlineClassAdapter" is missing following "CarrierGateway" protocol member:
tests/conftest.py:115: note:     cancel
tests/conftest.py:123: error: Incompatible return value type (got "tuple[FastlineGateway, FastlineClient]", expected "tuple[CarrierGateway, FastlineClient]")  [return-value]
tests/conftest.py:125: error: Incompatible return value type (got "tuple[_FastlineClassAdapter, _FastlineClassAdapter]", expected "tuple[CarrierGateway, FastlineClient]")  [return-value]
Found 9 errors in 3 files (checked 11 source files)
```

pytest has two failures. The test that assigns an `AircoClient` to a `CarrierGateway` now sees mypy exit 1, because Airco has no `cancel`. In `test_mypy_reports_an_implementor_missing_a_primitive`, the snippet's implementor lacks `cancel` as well as `insure`, so mypy lists both members on one note line and the test's `note:     insure` assertion no longer matches. Booking behaviour is unchanged. mypy reports the registry in `desk.py`, three test fixtures and the test that reads the registry, and the class adapter fixture reports the member `cancel` as missing. Each implementor owes the new method, and the checker finds the ones in this example.

## What you can do now

- Say when structural typing removes an adapter: `AircoClient` is registered as it is, and `FastlineClient` is refused for its different shape.
- Show how a `float` gets pounds past mypy: `test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float` exits 0, and `test_mypy_rejects_a_float_where_a_weight_belongs` refuses the same client once the Protocol takes a `Weight`.
- Choose between the two adapters: the class adapter exposes `submit_shipment`, and `FastlineGateway` doesn't.
- Write a facade that names no SDK type: `ship` passes `test_the_desk_names_no_sdk_type_in_its_public_surface`.
- Split two axes with a Bridge: the class-count test finds two classes against five, and `test_mypy_reports_an_implementor_missing_a_primitive` names the cost on the implementor.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Adapter, Facade and Bridge. Brandon Rhodes's [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/) gives the Python view of Adapter and Bridge where they meet. [PEP 544](https://peps.python.org/pep-0544/) specifies Protocols, and the [typing documentation](https://docs.python.org/3.15/library/typing.html) covers them. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
