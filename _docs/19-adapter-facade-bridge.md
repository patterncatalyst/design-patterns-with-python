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

A shipping desk books consignments with two carriers whose SDKs disagree about almost everything. The obvious versions fail three ways:

- A caller branches on the carrier code and reaches into each SDK. For Fastline it sends 10 kg in a field Fastline reads as pounds, and the carrier holds a 4.54 kg consignment.
- A client whose parameter is a plain `float` is accepted wherever a kilogram `float` is expected. The unit is in a parameter name, and mypy doesn't read names.
- Booking kinds multiply with carriers. Standard and insured, times two carriers, is four classes, and the two Fastline ones repeat Fastline's translation.

{% include excalidraw.html name="19-adapter-facade-bridge" described="true" caption="Figure 19.1: One call, two axes, one translation. The facade picks a gateway and a booking kind; each kind works through the narrow gateway Protocol, which one client already satisfies and the other reaches through an adapter that converts units." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-19-adapter-facade-bridge" markdown="1">
From the top: an accent box, `ship(consignment, carrier, ...)`, is labelled "Facade: one call, domain types only". It forks to `StandardBooking` and `InsuredBooking`, each labelled "Bridge: each kind holds a gateway". Both lead to `CarrierGateway`, "book, insure: the narrow Protocol". That box forks again, to `AircoClient`, "shape already matches: no adapter", and to `FastlineGateway`, "Adapter: shape, pounds, errors". An arrow runs down from `FastlineGateway` to a dashed `FastlineClient`, "carrier SDK". A dashed `Weight.pounds`, "units converted in one place", has a dashed arrow into `FastlineGateway`.
</div>
</details>

The figure stacks the three patterns: the facade on top, the bridge's two kinds in the middle, and the adapter at the SDK boundary.

## Pattern: Adapter

### The problem

The desk wants every carrier behind one `CarrierGateway` Protocol with `book` and `insure`. Airco's client already has that shape. Fastline's has `submit_shipment` and `add_cover`, takes pounds as strings, and raises its own error.

### The solution

An **Adapter** sits between two parts that disagree about shape: one calls, the other supplies, and an object between them translates.

**Bucket: survives.** Duck typing removes the adapter where the shapes already match, and the unit and error translation still need an object.

*Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994) gives two forms, one that subclasses the supplier and one that holds it. [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) defines the buckets, and [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) covers the nominal interfaces the catalogue assumed.

### How Python models it

`AircoClient` has `book` and `insure` with the Protocol's shape, so the desk registers it as it is, and mypy 2.4.1 accepts it as a `CarrierGateway`. `AircoClient` doesn't import `CarrierGateway` or know it exists, so a vendor's client can sit in the registry unchanged. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers the mechanism. A client with a different shape is refused:

```text
<string>:5: error: Incompatible types in assignment (expression has type "FastlineClient", variable has type "CarrierGateway")  [assignment]
```

`FastlineGateway` is an object adapter. It holds the SDK in its `client` field and translates shape, units and errors:

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

| Translation | Fastline side | Domain side |
| --- | --- | --- |
| Shape | a payload of strings, a numeric receipt | `book` returns an `FL-` reference |
| Unit | `"weight_lb": "22.05"` for 10 kg; 1.005 lb rounds half up to `1.01` | `Weight` in kilograms |
| Error | `FastlineRejectedError` over its limit | `CarrierError`, the SDK's error kept as `__cause__` |
| Cover | integer cents: `(1001, 25000, "EUR")` | `Money`, 250.00 EUR |

The pound is converted in one place, on the value type. `Weight` holds kilograms as a `Decimal` and refuses zero, negative and non-finite amounts. Pounds have one way in and one way out, with 0.45359237 kg to the pound:

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

The branching caller from the opening sends `"10"` as `weight_lb`, which `Weight.from_pounds` reads back as 4.54 kg. A 600 kg booking, about 1,323 lb against an illustrative limit of 1,000, raises `CarrierError` with the cause attached.

### Units and the type checker

Static checking runs out at a `float`. A client whose `book` takes `pounds: float` type-checks against a Protocol whose `book` takes `kilograms: float`, with no output. When the Protocol says `Weight`, the same client is refused:

```text
<string>:13: error: Incompatible types in assignment (expression has type "PoundsClient", variable has type "CarrierGateway")  [assignment]
<string>:13: note: Following member(s) of "PoundsClient" have conflicts:
<string>:13: note:     Expected:
<string>:13: note:         def book(self, ConsignmentId, Weight, /) -> str
<string>:13: note:     Got:
<string>:13: note:         def book(self, str, float, /) -> str
```

### Object adapter or class adapter

The class adapter subclasses `FastlineClient` and adds the two Protocol methods. It passes the same booking table, and it leaks: `submit_shipment` is on the class adapter and not on `FastlineGateway`. A caller holding the class adapter can call `submit_shipment` with a payload it builds itself and skip the translation. With the object adapter, it would have to reach through the public `client` field.

## Pattern: Facade

### The problem

Callers want to ship a consignment with a carrier. They shouldn't learn Fastline's units, build payloads, or see an SDK type, and the desk should be able to replace an SDK without touching them.

### The solution

A **Facade** puts one object in front of a subsystem with many parts and a caller that wants a few operations, so callers learn its few calls and not the parts.

**Bucket: survives.** In Python a module already is that object, and what survives is the choice of calls and the translation behind them.

### How Python models it

The facade is a module function:

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

- **Narrow surface.** `ship` takes a consignment and a carrier code and returns a `Booking`. `desk.__all__` lists `default_gateways` and `ship`, and their resolved type hints name no class from the `sdks` module. A facade that returned `FastlineReceipt` would narrow the calls and keep the leak.
- **Intent, not mechanism.** Declared value is an optional keyword, and its presence selects the booking kind.
- **Domain errors.** An unknown code raises `UnknownCarrierError`, "unknown carrier 'NOSUCH'", and `from None` keeps the `KeyError` out of the report.
- **Read-only registry.** `gateways` is a `frozendict` typed as a `Mapping`; assigning into it raises `TypeError`.

[ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers the composition root that builds `gateways`.

## Pattern: Bridge

### The problem

Two things vary: the booking kind (standard or insured) and the carrier. A class per pair needs N×M classes, and each carrier's translation is repeated in every kind.

### The solution

A **Bridge** splits a design with two things that vary, such as what an operation means and how it's carried out, so each can change without disturbing the other.

**Bucket: survives.** The link between the two sides is a Protocol-typed attribute, and the decision is which narrow set of primitives the implementor side promises.

Brandon Rhodes reads it the same way in [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/), where a logger subclassed once per output and once per filter multiplies, and he resolves it with Adapter, Bridge and Decorator in turn. He quotes the Gang of Four: "Favor object composition over class inheritance." python-patterns.guide has no page named Adapter, Facade or Bridge; that page is where it treats Adapter and Bridge.

### How Python models it

The booking kind is the abstraction, and each kind holds a gateway:

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

The `gateway` field is the mechanism [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers. Insurance is the second primitive: `InsuredBooking` calls `book` and then `insure`, so the carrier's way of recording cover stays inside the gateway. Airco keeps the `Money` it was given, and Fastline's adapter turns it into cents. Zero and negative declared values are refused at construction.

### What the bridge saves and costs

Two kinds against two carriers pass in both designs. The class counts differ:

| Change | Bridge | Class per kind and carrier |
| --- | --- | --- |
| Today | 2 classes in `bookings.py` | 5: an abstract base and four pairs |
| A third kind | 1 class | 1 per carrier |
| A third carrier | 1 gateway | 1 per kind |
| A new primitive | each gateway owes it | each class owes it |

A new booking kind calls the same two primitives, and no gateway changes. A new primitive is a promise every gateway has to keep, and mypy names an implementor that misses one:

```text
<string>:11: error: Incompatible types in assignment (expression has type "BookOnly", variable has type "CarrierGateway")  [assignment]
<string>:11: note: "BookOnly" is missing following "CarrierGateway" protocol member:
<string>:11: note:     insure
```

The cost sits on the implementor, and the benefit on the abstraction, so keep the Protocol small. Which kind to build is a creation question; [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) takes it up.

## When not to use it

- **Adapter.** Call the client when there's one carrier and the SDK already fits. An adapter that only renames parameters isn't needed, because the Protocol's parameters are positional-only.
- **Facade.** A facade over a subsystem with one caller can be inlined.
- **Bridge.** A bridge where one axis doesn't vary is a parameter, and the second hierarchy is a cost with no return.

<blockquote class="ai-sidebar" markdown="1">
**Specifying an adapter.** "Integrate a carrier" leaves open which clients need an adapter, what units cross the boundary and what the caller sees of the SDK. Paste a prompt that states the form:

> Register a client that already satisfies `CarrierGateway` as it is. For one that doesn't, write an object adapter that holds the client, converts units through `Weight.pounds` and `Weight.from_pounds`, and raises `CarrierError` from the SDK's error. Write the facade as a module function, `ship`, whose signature names only domain types. Make booking kinds a bridge over the narrow Protocol, not a class per kind and carrier.

If a weight crosses as a `float`, ask for a `Weight` parameter.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/19-adapter-facade-bridge
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 35 cases pass and mypy is clean. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers how the mypy checks are built. Two experiments, each in a fresh scratch copy:

- **Send kilograms.** In `FastlineGateway.book`, replace `weight.pounds` with `weight.kilograms`. Three tests fail: the payload reads `0.46` and `10.00` where `1.01` and `22.05` were due, and 600 kg sent as 600.00 lb passes under the 1,000 lb limit, so no `CarrierError` is raised. The class adapter, with its own copy of the conversion, still passes, and mypy is clean: kilograms and pounds are both `Decimal`.
- **Widen the Protocol.** Add `def cancel(self, reference: str, /) -> None: ...` to `CarrierGateway`. Booking behaviour is unchanged, two static checks fail, and mypy reports nine errors: the registry in `desk.py`, the fixtures and the class adapter all owe `cancel`.

## What you can do now

- Register a client whose shape matches the Protocol as it is, and let mypy refuse one that doesn't.
- Put units in a `Weight` parameter, because a `float` lets pounds pass as kilograms.
- Prefer an object adapter, which doesn't expose `submit_shipment` as a class adapter does.
- Write a facade, `ship`, whose public surface names no SDK type.
- Split two axes with a Bridge, two classes against five, and keep the implementor's Protocol small.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Adapter, Facade and Bridge. Brandon Rhodes's [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/) gives the Python view of Adapter and Bridge where they meet. [PEP 544](https://peps.python.org/pep-0544/) specifies Protocols, and the [typing documentation](https://docs.python.org/3/library/typing.html) covers them. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
