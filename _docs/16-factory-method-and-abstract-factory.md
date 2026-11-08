---
title: "Factory Method and Abstract Factory"
order: 16
layout: tutorial
sectionid: docs
part: "creating-objects-under-control"
description: "Factory Method dissolves into a class or a Self classmethod in a Callable slot, while Abstract Factory survives as one frozen kit per carrier family, with mypy tying only the products that pass values to each other."
---

## Learning objectives

By the end of this chapter you can:

- Say why Factory Method dissolves in Python and what stands in for the creator subclass: a class or a `Self` classmethod in a `Callable` slot, held in a read-only registry.
- Choose between a `Callable` slot and a `type[...]` slot, and say what mypy checks in each.
- Explain why Abstract Factory survives: a family of products must match, and no language feature chooses the family for you.
- Write one frozen kit per family, choose it once, and tie the products that exchange values with a type parameter.
- State what that tie doesn't cover.

## Why this matters

A booking service talks to two carriers. Fastline needs an endpoint and issues references that start `FL-`. Airco needs an account and issues references that start `AC-`. The obvious versions fail three ways:

- A second carrier is added to two of the three functions that branch on the carrier code. An Airco booking is quoted at Fastline's rate, 12.00 where 48.00 was due, and mypy accepts the code.
- A registry typed `type[CarrierGateway]` type-checks, and the first Airco booking fails at run time because Airco's class needs an account and the registry calls it with nothing.
- A family assembled by hand pairs Fastline's gateway with Airco's label printer. A Fastline reference prints on an Airco label, and nothing raises.

{% include excalidraw.html name="16-factory-method-and-abstract-factory" described="true" caption="Figure 16.1: Factories as values. A read-only registry maps a carrier code to one kit per family. The reference type ties the gateway to the label printer, while the rate source stays consistent only because the whole kit is chosen once." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-16-factory-method-and-abstract-factory" markdown="1">
From the top: an accent box, `ship(code, ...)`, feeds `KITS`, labelled "read-only: carrier code to kit". It forks to `FASTLINE_KIT` and `AIRCO_KIT`. Each kit leads to its gateway, `FastlineGateway` or `AircoGateway`, and each gateway has an arrow to its label printer, labelled with the reference type that travels along it, `FastlineReference` or `AircoReference`. Below, two dashed boxes, `FastlineRates` and `AircoRates`, say "not tied: one kit value keeps it consistent", and no arrow reaches them. On the left, with no arrows, stand `GATEWAYS`, "Factory Method: a constructor in a Callable slot, per code", a registry separate from the kits, and a note, "mypy ties the gateway to the label printer by the reference type".
</div>
</details>

The figure shows the kits as values in a read-only registry, and which products the reference type ties together.

## Pattern: Factory Method

### The problem

Booking code needs a gateway for a carrier code. The force is real: the caller wants a gateway for a carrier and shouldn't know which gateway class that is.

### The solution

A **Factory Method** lets code create an object without naming its class, by calling an operation that a subclass or a supplied value fills in.

**Bucket: dissolves.** A class is a callable and a classmethod is a named constructor, so Factory Method dissolves into a value in a slot.

In the *Design Patterns* catalogue by Gamma, Helm, Johnson and Vlissides (1994), the creating code calls a method it leaves abstract, and a subclass supplies it. Brandon Rhodes, on [python-patterns.guide](https://python-patterns.guide/gang-of-four/factory-method/), reaches the same verdict: the pattern exists for languages in which a class or a function isn't a value that code can hand around. [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) shows the class-in-a-dict move, and [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers where the registry is built.

### How Python models it

The registry maps a code to a constructor:

<!-- fmt:off -->
```python
type GatewayFactory = Callable[[CarrierSettings], CarrierGateway[str]]

GATEWAYS: Mapping[str, GatewayFactory] = frozendict(
    {
        "FASTLINE": FastlineGateway.from_settings,
        "AIRCO": AircoGateway.from_settings,
    }
)
```
<!-- fmt:on -->

Each entry is a classmethod annotated `-> Self`, so it builds whatever class it's called on:

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True)
class AircoGateway:
    account: str

    @classmethod
    def from_settings(cls, settings: CarrierSettings) -> Self:
        return cls(settings.account)
```
<!-- fmt:on -->

A subclass of either gateway gets back the subclass from `from_settings`, with the account read from the settings. A `from_settings` that built the parent by name would lose that.

- **Read-only.** The registry is a `frozendict`, the builtin that Python 3.15 adds under [PEP 814](https://peps.python.org/pep-0814/), typed as a `Mapping`. Item assignment raises `TypeError`.
- **Unknown codes.** An unknown code raises `UnknownCarrierError`, which names the code, with the original `KeyError` suppressed.
- **Configuration.** A sandbox or live choice is a settings value: `from_settings` picks the sandbox endpoint from it.

The GoF shape, kept as a comparison, needs a creator class and a subclass per carrier:

<!-- fmt:off -->
```python
class _BookingDesk(ABC):
    """The GoF shape, kept as a comparison: a creator whose subclasses choose the gateway."""

    @abstractmethod
    def create_gateway(self, settings: CarrierSettings) -> CarrierGateway[str]: ...

    def book(self, consignment_id: ConsignmentId, settings: CarrierSettings) -> str:
        return self.create_gateway(settings).book(consignment_id)


class _FastlineDesk(_BookingDesk):
    def create_gateway(self, settings: CarrierSettings) -> CarrierGateway[str]:
        return FastlineGateway.from_settings(settings)


class _AircoDesk(_BookingDesk):
    def create_gateway(self, settings: CarrierSettings) -> CarrierGateway[str]:
        return AircoGateway.from_settings(settings)
```
<!-- fmt:on -->

Both forms book `FL-CN-1` for Fastline and `AC-ACC-7-CN-1` for Airco. The creator form declares three classes and `factories.py` declares none. The behaviour is the same, so the classes are the cost.

### The slot type decides what mypy checks

The slot can be typed two ways, and they don't check the same thing. Results are from mypy 2.4.1.

| Slot type | `AircoGateway` (needs an account) | `functools.partial` of it | The Protocol itself |
| --- | --- | --- | --- |
| `Callable[[], CarrierGateway[str]]` | rejected | accepted | n/a |
| `type[CarrierGateway[str]]` | accepted, then `TypeError` at the call | rejected | rejected |

A `Callable[[], ...]` slot asks for something callable with no arguments. `FastlineGateway` fits because its endpoint has a default, and `AircoGateway` doesn't:

```text
<string>:8: error: Dict entry 1 has incompatible type "str": "type[AircoGateway]"; expected "str": "Callable[[], CarrierGateway[str]]"  [dict-item]
```

A classmethod with another signature, such as `from_env(cls, env: Mapping[str, str])`, fails the `GatewayFactory` slot the same way:

```text
<string>:15: error: Dict entry 0 has incompatible type "str": "Callable[[Mapping[str, str]], EnvAircoGateway]"; expected "str": "Callable[[CarrierSettings], CarrierGateway[str]]"  [dict-item]
```

A `type[CarrierGateway[str]]` slot says "a class". `CarrierGateway` is a Protocol, which gives mypy no constructor signature to check, so `BY_TYPE["AIRCO"]()` passes and then raises `TypeError` ending "missing 1 required positional argument: 'account'". The same slot rejects a `partial`, which works as a factory, and rejects the Protocol with `Only concrete class can be given`. The `type` slot refuses things that work and accepts a call that fails, so use the `Callable` slot. [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) covers how mypy checks each entry of a registry of callables.

## Pattern: Abstract Factory

### The problem

A booking needs a gateway, a label printer and a rate source, and the three have to agree on the carrier. The tempting design branches on the code wherever a product is needed: `_make_gateway`, `_make_label` and `_make_rates`, each an `if code == "FASTLINE"` chain. Airco reached the first two. The third returns Fastline's rates as its default. An Airco consignment of 10 kg gets the label `AIRCO AC-ACC-7-CN-1` and a quote of 12.00 EUR where the kit's is 48.00 EUR.

mypy has nothing to say while the code is a `str`. Typing the code as a `Literal` and writing a `match` helps:

```text
<string>:12: error: Argument 1 to "assert_never" has incompatible type "Literal['AIRCO']"; expected "Never"  [arg-type]
```

[State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}) covers `assert_never`. It catches the missing arm in each of three places, and the family still has no single home.

### The solution

An **Abstract Factory** makes products that only work in matching sets through one object, so the set stays matched.

**Bucket: survives.** For Factory Method a feature resolved the problem: a callable in a slot. The force is that products must come from the same family, and a language that stores callables doesn't choose the family.

Rhodes treats this pattern as a workaround too, and his [Abstract Factory page](https://python-patterns.guide/gang-of-four/abstract-factory/) shows a parser handed a callable for numbers. That case is the callable in a slot. Several products that must agree with each other is a different problem.

### How Python models it

The family is a value, and a value can be a frozen dataclass:

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True, kw_only=True)
class CarrierKit[R: str]:
    """The constructors of one family. The reference type R ties gateway to label printer."""

    gateway: Callable[[CarrierSettings], CarrierGateway[R]]
    label_printer: Callable[[], LabelPrinter[R]]
    rates: Callable[[], RateSource]
```
<!-- fmt:on -->

`R` is the reference type: the gateway returns an `R` from `book`, and the label printer takes an `R` in `label`. There are two kits:

<!-- fmt:off -->
```python
FASTLINE_KIT = CarrierKit(
    gateway=FastlineGateway.from_settings,
    label_printer=FastlineLabelPrinter,
    rates=FastlineRates,
)
AIRCO_KIT = CarrierKit(
    gateway=AircoGateway.from_settings,
    label_printer=AircoLabelPrinter,
    rates=AircoRates,
)

KITS: Mapping[str, Shipper] = frozendict({"FASTLINE": FASTLINE_KIT, "AIRCO": AIRCO_KIT})
```
<!-- fmt:on -->

The kit is the unit the caller chooses. `CarrierKit.ship` books with the gateway, prints with the label printer and quotes with the rates. The module-level `ship(code, ...)` looks the kit up in `KITS` and turns an unknown code into the same `UnknownCarrierError`. Everything after that lookup uses one kit, so the products can't come from different carriers unless someone builds a kit that mixes them. Kits are frozen: assigning to a field raises, a kit rebuilt from the same constructors is equal and hashes the same, and the two kits differ.

### What the type parameter ties

The reference types are `NewType`s over `str`: `FastlineReference` and `AircoReference`. Hand `CarrierKit` a Fastline gateway and an Airco label printer, and mypy can't solve for one `R`:

```text
<string>:5: error: Cannot infer value of type parameter "R" of "CarrierKit"  [misc]
```

The registry hides `R` behind a one-method `Shipper` Protocol, because `KITS` holds kits of different `R`. A registry typed by one family is rejected: `Dict entry 0 has incompatible type "str": "CarrierKit[FastlineReference]"; expected "str": "CarrierKit[str]"`. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers the Protocol machinery.

The tie has limits:

| Mixed kit | mypy | At run time |
| --- | --- | --- |
| Fastline gateway, Airco label printer | rejected | label `AIRCO FL-CN-1` under `# type: ignore[misc]` |
| Fastline gateway and printer, `AircoRates` | exit 0 | Airco's rates on a Fastline booking |
| Airco gateway, a `PlainLabelPrinter` taking `str` | exit 0 | any reference prints |

The rate source passes no value to the other products, so there's nothing for a type to hold. Tie what exchanges values and choose the kit once, at the composition root. For everything else the kit is the design: nothing keeps the rates with the gateway except that one lookup picked a whole kit.

### Adding a carrier, adding a product

A new carrier is one kit value and one registry entry, plus its product classes. A new kind of product is a field on `CarrierKit` and a change to each kit value. Adding a family is cheap, and adding a product touches each family.

## When not to use it

- **Factory Method.** With one product, a registry of constructors in a `Callable` slot is enough. With one carrier, call the class. If the choice is a configuration value, such as sandbox or live, put it in a settings value.
- **Abstract Factory.** If the products don't have to match, pass them separately.

> **🤖 Explore with your agent**
>
> "Register constructors in a read-only `frozendict` of `GatewayFactory`, each a `from_settings` classmethod returning `Self`, and raise an unknown code as `UnknownCarrierError`. Put each carrier's gateway, label printer and rate source in one frozen `CarrierKit[R]`, choose the kit once by carrier code, and tie the gateway to the label printer through the reference type `R`. No `type[...]` slot and no if-chain."
>
> If two modules branch on the carrier code, ask for the kit.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/16-factory-method-and-abstract-factory
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 28 cases pass and mypy is clean. Two experiments, each in a fresh scratch copy:

- **Give the Airco kit the Fastline label printer.** Change `label_printer=AircoLabelPrinter` to `label_printer=FastlineLabelPrinter` in `AIRCO_KIT`. mypy reports `Cannot infer value of type parameter "R" of "CarrierKit"` at `src/factories/kits.py`, and two tests fail on the label `FASTLINE AC-ACC-7-CN-1`.
- **Loosen the Airco printer.** Change `AircoLabelPrinter.label` to take `reference: str`. The tie is gone: `AIRCO_KIT` still builds, the shipping tests pass, mypy only reports an unused `type: ignore`, and the one failure is the check that expects mypy to reject a mixed kit. The tie lasts as long as the printer's parameter keeps the reference type.

## What you can do now

- Put `from_settings` classmethods in a read-only `GATEWAYS` registry, each returning the class it's called on.
- Type the slot as `Callable`, so mypy checks each entry, rather than `type`, which accepts a class that fails at run time.
- Replace carrier if-chains, which quoted an Airco consignment at 12.00 where 48.00 was due, with a kit chosen once.
- Write `CarrierKit[R]` so mypy rejects a kit that mixes reference types.
- Name what the tie leaves out: a mixed rate source and a printer that takes plain `str`.

## For deeper coverage

*Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson and Vlissides) is the source for Factory Method and Abstract Factory. Brandon Rhodes's [Factory Method](https://python-patterns.guide/gang-of-four/factory-method/) and [Abstract Factory](https://python-patterns.guide/gang-of-four/abstract-factory/) pages read both through Python. The [`typing` documentation](https://docs.python.org/3/library/typing.html#typing.Self) covers `Self`, and [PEP 544](https://peps.python.org/pep-0544/) specifies Protocols. [PEP 814](https://peps.python.org/pep-0814/) covers `frozendict`, which backs both registries. [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}) takes the other creational patterns. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
