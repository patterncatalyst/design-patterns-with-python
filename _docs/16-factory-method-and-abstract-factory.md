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
- Explain why Abstract Factory survives: the force is a family of products that must match, and no language feature chooses the family for you.
- Write one frozen kit per family, choose it once, and tie the products that exchange values with a type parameter.
- State what that tie does not cover, from a measured run.

## Why this matters

A booking service talks to two carriers. Fastline needs an endpoint and issues references that start `FL-`. Airco needs an account and issues references that start `AC-`. Three failures turn up in the obvious versions.

A second carrier is added to two of the three functions that branch on the carrier code. The booking for Airco is quoted at Fastline's rate, 12.00 where 48.00 was due. mypy accepts the code.

A registry is typed `type[CarrierGateway]` so that it can hold classes. It type-checks. The first Airco booking fails at run time, because Airco's class needs an account and the registry calls it with nothing.

Someone assembles a family by hand, with Fastline's gateway and Airco's label printer. A Fastline reference prints on an Airco label, and nothing raises.

{% include excalidraw.html name="16-factory-method-and-abstract-factory" caption="Figure 16.1: Factories as values. A read-only registry maps a carrier code to one kit per family. The reference type ties the gateway to the label printer, while the rate source stays consistent only because the whole kit is chosen once." %}

Read the figure from the top down. An accent box, `ship(code, ...)`, feeds `KITS`, labelled "read-only: carrier code to kit". It forks to `FASTLINE_KIT` and `AIRCO_KIT`. Each kit leads to its gateway, `FastlineGateway` or `AircoGateway`, and each gateway has an arrow to its label printer, labelled with the reference type that travels along it, `FastlineReference` or `AircoReference`. Below, two dashed boxes, `FastlineRates` and `AircoRates`, say "not tied: one kit value keeps it consistent", and no arrow reaches them. On the left, with no arrows, stand `GATEWAYS`, "Factory Method: a constructor in a Callable slot, per code", a registry separate from the kits, and a note, "mypy ties the gateway to the label printer by the reference type".

## Factory Method dissolves

The *Design Patterns* catalogue by Gamma, Helm, Johnson and Vlissides (1994) introduces Factory Method for code that has to create an object without naming the class it creates. In the book's design, the creating code calls a method it leaves abstract, and a subclass supplies that method and, with it, the concrete gateway. The force is real: the caller wants a gateway for a carrier and shouldn't know which gateway class that is.

Python meets the force with what it already has. A class is a callable, so `FastlineGateway(...)` is a factory. When construction needs a different shape of input, a classmethod is the named constructor, and a classmethod annotated `-> Self` builds whatever class it was called on. The creator subclass becomes a value in a slot. Brandon Rhodes, on [python-patterns.guide](https://python-patterns.guide/gang-of-four/factory-method/), reaches the same verdict from the other direction: the pattern exists for languages in which a class or a function isn't a value that code can hand around, and in Python any callable, a classmethod among them, can be the thing a caller supplies. [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) shows the class-in-a-dict move, and [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers where the registry is built.

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

Each entry in `GATEWAYS` is a classmethod:

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

`test_a_classmethod_constructor_returns_the_subclass_it_is_called_on` subclasses both gateways and finds that `from_settings` returns the subclass, with the account read from the settings. A `from_settings` that built the parent by name would fail this test. The registry is a `frozendict`, the builtin that Python 3.15 adds under [PEP 814](https://peps.python.org/pep-0814/), typed as a `Mapping`. `test_the_carrier_registries_are_read_only` finds that item assignment raises a `TypeError` for `GATEWAYS` and for `KITS`, and that neither is a `dict`. `test_an_unknown_carrier_code_is_an_unknown_carrier_error` finds that an unknown code gives an `UnknownCarrierError` that names the code, with the original `KeyError` suppressed.

The comparison is the GoF shape, kept in the tests as a fixture. A creator class declares the operation and each carrier gets a subclass:

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

`test_a_registered_constructor_builds_each_carrier_gateway` runs one table of two carriers through both forms, and each form books the reference the table expects: `FL-CN-1` for Fastline and `AC-ACC-7-CN-1` for Airco. `test_the_creator_design_declares_three_classes_where_the_registry_declares_none` parses the sources with `ast` and finds three creator classes in the fixture and no class definition in `factories.py`. The behaviour is the same, so the classes are the cost.

## The slot type decides what mypy checks

The registry's slot can be typed two ways, and the two don't check the same thing. Each result below is mypy 2.4.1, run through the test's own helper.

A slot typed `Callable[[], CarrierGateway[str]]` asks for something callable with no arguments. `FastlineGateway` fits, because its endpoint has a default. `AircoGateway` needs an account:

```text
<string>:8: error: Dict entry 1 has incompatible type "str": "type[AircoGateway]"; expected "str": "Callable[[], CarrierGateway[str]]"  [dict-item]
```

The same holds for a classmethod with another signature. A `from_env(cls, env: Mapping[str, str])` placed in the `GatewayFactory` slot gives:

```text
<string>:15: error: Dict entry 0 has incompatible type "str": "Callable[[Mapping[str, str]], EnvAircoGateway]"; expected "str": "Callable[[CarrierSettings], CarrierGateway[str]]"  [dict-item]
```

Those are `test_mypy_checks_a_constructor_slot_but_not_a_type_slot` (the `callable-slot` case) and `test_mypy_checks_a_classmethod_constructor_against_the_slot`.

A slot typed `type[CarrierGateway[str]]` says "a class", and the same two classes exit clean, including the call `BY_TYPE["AIRCO"]()` with no argument. `CarrierGateway` is a Protocol, and a Protocol has no constructor signature for mypy to check the call against. `test_a_type_registry_accepts_a_class_that_cannot_be_called_without_arguments` makes the call and gets a `TypeError` whose message ends "missing 1 required positional argument: 'account'". The same slot rejects a `functools.partial` of the Airco class, which works as a factory (`Dict entry 0 has incompatible type "str": "partial[AircoGateway]"`), and it rejects the Protocol itself with `Only concrete class can be given`. The `type` slot refuses things that work and accepts a call that fails, so the `Callable` slot is the one to use. [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) covers how mypy checks each entry of a registry of callables.

## When creation comes in families

A gateway is rarely the sole product that depends on the carrier. Here a booking needs a gateway, a label printer and a rate source, and the three have to agree on the carrier.

The tempting design branches on the code wherever a product is needed. The fixture in `tests/test_if_chains.py` has three functions, `_make_gateway`, `_make_label` and `_make_rates`, each an `if code == "FASTLINE"` chain. Airco reached the first two. The third returns Fastline's rates as its default, with a comment that says so. `test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate` books an Airco consignment of 10 kg both ways. The label reads `AIRCO AC-ACC-7-CN-1` in both, and the chain's quote is 12.00 EUR where the kit's is 48.00 EUR.

mypy has nothing to say while the code is a `str`. The reduced model in `test_mypy_cannot_see_a_carrier_missing_from_an_if_chain` has two `if` arms and a `raise` for the rest, and exits 0. Typing the code as a `Literal` and writing a `match` helps, and the same test's `literal-code` case shows it:

```text
<string>:12: error: Argument 1 to "assert_never" has incompatible type "Literal['AIRCO']"; expected "Never"  [arg-type]
```

[State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}) covers `assert_never`. It would catch the missing arm in each of three places, and the family would still have no single home. Both snippets are reduced models of the fixture.

Ask whether a feature resolves the force without the pattern's structure. For Factory Method one did: a callable in a slot. For this force none does. The force is that products must come from the same family, and a language that stores callables doesn't choose the family. The GoF catalogue calls this Abstract Factory: products that only work in matching sets, made through one object so the set stays matched. The bucket is survives.

Rhodes treats this pattern as a workaround too, and his [Abstract Factory page](https://python-patterns.guide/gang-of-four/abstract-factory/) shows a parser that is handed a callable for numbers. That case is the callable in a slot, the Factory Method answer above. The force here is different: several products that must agree with each other.

## The family as one frozen value

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

`R` is the reference type: the gateway returns an `R` from `book`, and the label printer takes an `R` in `label`. A kit has two instances:

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

The kit is the unit the caller chooses. `CarrierKit` has a `ship` method that books with the gateway, prints with the label printer and quotes with the rates, and `ship(code, ...)` at module level looks the kit up in `KITS`, turning an unknown code into the same `UnknownCarrierError` that the gateway registry raises. Everything after that lookup uses one kit, so the gateway, the printer and the rates can't come from different carriers unless someone builds a kit that mixes them. `test_each_kit_ships_with_its_own_carriers_products` runs both carriers and compares the whole `Shipment` with the expected reference, label and quote. `test_every_kit_is_a_frozen_value` shows that assigning to a field raises, that a kit rebuilt from the same constructors is equal and hashes the same, and that the two kits differ.

The reference types are `NewType`s over `str`: `FastlineReference` and `AircoReference`. A Fastline gateway returns the first, and `FastlineLabelPrinter.label` takes it. Hand `CarrierKit` a Fastline gateway and an Airco label printer, and mypy can't solve for one `R`:

```text
<string>:5: error: Cannot infer value of type parameter "R" of "CarrierKit"  [misc]
```

That's `test_mypy_rejects_a_kit_that_mixes_reference_types`. The registry hides the type parameter behind a one-method `Shipper` Protocol, because `KITS` holds kits of different `R`. A registry typed by one family is rejected, as `test_mypy_rejects_a_kit_registry_typed_by_one_family` shows: `Dict entry 0 has incompatible type "str": "CarrierKit[FastlineReference]"; expected "str": "CarrierKit[str]"`. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers the Protocol machinery.

The tie has limits, and two tests measure them. In `test_mypy_accepts_kits_that_mix_untied_products`, a kit with Fastline's gateway and label printer and Airco's `AircoRates` exits 0 with no output. The rate source passes no value to the other products, so there is nothing for a type to hold. The second case defines a `PlainLabelPrinter` whose `label` takes a plain `str` and pairs it with the Airco gateway. That exits 0 too, because a printer that accepts any `str` takes whatever reference the gateway returns. `test_a_hand_mixed_kit_prints_one_carriers_reference_on_anothers_label` builds the mixed-reference kit under a `# type: ignore[misc]` and finds the shipment's label is `AIRCO FL-CN-1`.

The rule is that you tie what exchanges values and choose the kit once, at the composition root. The tie is a measured, partial check. For everything else the kit is the design: nothing else keeps the rates with the gateway except that a whole kit was picked by one lookup.

## Adding a carrier, adding a product

A new carrier is one kit value and one registry entry, plus the product classes it needs. A new kind of product is a field on each kit and a change to each kit value. That's the trade-off of the pattern, here in one frozen dataclass: adding a family is cheap, and adding a product touches each family.

## When not to use it

With one product, a registry of constructors in a `Callable` slot is enough. With one carrier, call the class. If the products don't have to match, pass them separately. If the choice is a configuration value, such as sandbox or live, it belongs in a settings value, and `test_a_sandbox_setting_selects_the_sandbox_endpoint` shows `from_settings` choosing the endpoint from one.

<blockquote class="ai-sidebar" markdown="1">
**Specifying factories.** "A factory" leaves open whether the carrier is chosen once or on every call, how an unknown code fails and what ties a gateway to its label printer. Paste a prompt that states the form:

> Register constructors in a read-only `frozendict` of `GatewayFactory`, each a `from_settings` classmethod returning `Self`, and raise an unknown code as `UnknownCarrierError`. Put each carrier's gateway, label printer and rate source in one frozen `CarrierKit[R]`, choose the kit once by carrier code, and tie the gateway to the label printer through the reference type `R`. No `type[...]` slot and no if-chain.

If two modules branch on the carrier code, ask for the kit.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/16-factory-method-and-abstract-factory
uv run pytest -v --no-header
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
collecting ... collected 28 items

tests/test_factory_method.py::test_a_registered_constructor_builds_each_carrier_gateway[FASTLINE-registry] PASSED [  3%]
tests/test_factory_method.py::test_a_registered_constructor_builds_each_carrier_gateway[FASTLINE-creator] PASSED [  7%]
tests/test_factory_method.py::test_a_registered_constructor_builds_each_carrier_gateway[AIRCO-registry] PASSED [ 10%]
tests/test_factory_method.py::test_a_registered_constructor_builds_each_carrier_gateway[AIRCO-creator] PASSED [ 14%]
tests/test_factory_method.py::test_a_classmethod_constructor_returns_the_subclass_it_is_called_on PASSED [ 17%]
tests/test_factory_method.py::test_a_sandbox_setting_selects_the_sandbox_endpoint PASSED [ 21%]
tests/test_factory_method.py::test_an_unknown_carrier_code_is_an_unknown_carrier_error[gateways] PASSED [ 25%]
tests/test_factory_method.py::test_an_unknown_carrier_code_is_an_unknown_carrier_error[kits] PASSED [ 28%]
tests/test_factory_method.py::test_the_carrier_registries_are_read_only[gateways] PASSED [ 32%]
tests/test_factory_method.py::test_the_carrier_registries_are_read_only[kits] PASSED [ 35%]
tests/test_factory_method.py::test_the_creator_design_declares_three_classes_where_the_registry_declares_none PASSED [ 39%]
tests/test_factory_method.py::test_a_type_registry_accepts_a_class_that_cannot_be_called_without_arguments PASSED [ 42%]
tests/test_if_chains.py::test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate PASSED [ 46%]
tests/test_kits.py::test_each_kit_ships_with_its_own_carriers_products[FASTLINE] PASSED [ 50%]
tests/test_kits.py::test_each_kit_ships_with_its_own_carriers_products[AIRCO] PASSED [ 53%]
tests/test_kits.py::test_a_hand_mixed_kit_prints_one_carriers_reference_on_anothers_label PASSED [ 57%]
tests/test_kits.py::test_every_kit_is_a_frozen_value PASSED              [ 60%]
tests/test_static.py::test_mypy_checks_a_constructor_slot_but_not_a_type_slot[callable-slot] PASSED [ 64%]
tests/test_static.py::test_mypy_checks_a_constructor_slot_but_not_a_type_slot[type-slot] PASSED [ 67%]
tests/test_static.py::test_mypy_checks_a_constructor_slot_but_not_a_type_slot[partial-in-type-slot] PASSED [ 71%]
tests/test_static.py::test_mypy_checks_a_constructor_slot_but_not_a_type_slot[protocol-in-type-slot] PASSED [ 75%]
tests/test_static.py::test_mypy_checks_a_classmethod_constructor_against_the_slot PASSED [ 78%]
tests/test_static.py::test_mypy_cannot_see_a_carrier_missing_from_an_if_chain[str-code] PASSED [ 82%]
tests/test_static.py::test_mypy_cannot_see_a_carrier_missing_from_an_if_chain[literal-code] PASSED [ 85%]
tests/test_static.py::test_mypy_rejects_a_kit_that_mixes_reference_types PASSED [ 89%]
tests/test_static.py::test_mypy_accepts_kits_that_mix_untied_products[mixed-rates] PASSED [ 92%]
tests/test_static.py::test_mypy_accepts_kits_that_mix_untied_products[plain-printer] PASSED [ 96%]
tests/test_static.py::test_mypy_rejects_a_kit_registry_typed_by_one_family PASSED [100%]

============================== 28 passed in 4.98s ==============================
Success: no issues found in 10 source files
```

The suite has 17 test functions and 28 cases.

**Experiment one: give the Airco kit the Fastline label printer.** In a fresh scratch copy, change `label_printer=AircoLabelPrinter` to `label_printer=FastlineLabelPrinter` in `AIRCO_KIT`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then the member's mypy run gives:

```text
E       AssertionError: assert 'AIRCO AC-ACC-7-CN-1' == 'FASTLINE AC-ACC-7-CN-1'
tests/test_if_chains.py:65: AssertionError
E       AssertionError: assert Shipment(refe...rency='EUR'))) == Shipment(refe...rency='EUR')))
tests/test_kits.py:19: AssertionError
FAILED tests/test_if_chains.py::test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate
FAILED tests/test_kits.py::test_each_kit_ships_with_its_own_carriers_products[AIRCO]
2 failed, 26 passed in 4.88s
src/factories/kits.py:54: error: Cannot infer value of type parameter "R" of "CarrierKit"  [misc]
Found 1 error in 1 file (checked 10 source files)
```

mypy reports the mixed kit in the source, and two tests fail. The kit test finds the wrong label on the Airco shipment, and the if-chain test, which compares the chain's label with the kit's, sees `FASTLINE` where it expects `AIRCO`.

**Experiment two: loosen the Airco printer.** In a fresh scratch copy, change `AircoLabelPrinter.label` to take `reference: str`. The same filtered run, then mypy, gives:

```text
E       assert 0 == 1
tests/test_static.py:179: AssertionError
FAILED tests/test_static.py::test_mypy_rejects_a_kit_that_mixes_reference_types
1 failed, 27 passed in 5.05s
tests/test_kits.py:25: error: Unused "type: ignore" comment  [unused-ignore]
Found 1 error in 1 file (checked 10 source files)
```

The tie is gone. `AIRCO_KIT` still builds without a complaint, and the mixed kit in the hand-mixed test now type-checks, so mypy's sole report is that the `# type: ignore[misc]` is unused. The one failing test is the witness that expects mypy to reject the mixed kit. Nothing in `src` reports the loss, and the shipping tests still pass. The tie lasts as long as the printer's parameter keeps the reference type.

## What you can do now

- Say why Factory Method dissolves: `GATEWAYS` holds `from_settings` classmethods in a read-only registry, and the subclass test shows each returns the class it is called on.
- Choose the slot: a `Callable` slot makes mypy check each entry, and a `type` slot accepts a class that fails at run time.
- Explain why Abstract Factory survives: the if-chain fixture quotes an Airco consignment at 12.00 where 48.00 was due.
- Write one frozen kit per family: `CarrierKit[R]` is chosen once, and `test_mypy_rejects_a_kit_that_mixes_reference_types` shows the tie holding.
- State what the tie leaves out: `test_mypy_accepts_kits_that_mix_untied_products` exits 0 for a mixed rate source and a plain printer.

## For deeper coverage

*Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson and Vlissides) is the source for Factory Method and Abstract Factory. Brandon Rhodes's [Factory Method](https://python-patterns.guide/gang-of-four/factory-method/) and [Abstract Factory](https://python-patterns.guide/gang-of-four/abstract-factory/) pages read both through Python. The [`typing` documentation](https://docs.python.org/3/library/typing.html#typing.Self) covers `Self`, and [PEP 544](https://peps.python.org/pep-0544/) specifies Protocols. [PEP 814](https://peps.python.org/pep-0814/) covers `frozendict`, which backs both registries. [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}) takes the other creational patterns. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
