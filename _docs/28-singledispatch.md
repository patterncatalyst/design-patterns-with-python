---
title: "singledispatch: the Visitor the language gives you"
order: 28
layout: tutorial
sectionid: docs
part: "idiomatic-python"
description: "Dispatch on the type of the first argument without a visitor class, and the choices that matter once registrations can live in other modules."
---

## Learning objectives

By the end of this chapter you can:

- Register an implementation per class by annotation, and predict which one runs for a subclass.
- Choose what the fallback does for a kind nobody registered.
- Say what fails when a registration is made and what mypy checks about it.
- Extend a generic function from another module, and test that in isolation.
- Dispatch a method on the argument after `self`.

## Why this matters

A customs declaration needs a tariff code for each kind of commodity, such as coffee or a T-shirt. The customs team owns most of the kinds, and the dangerous goods team adds others that the customs team doesn't own, such as a lithium-ion battery. The headings and rates here are illustrative. Visitor, in *Design Patterns* (1994), gives each class an `accept` method and puts each operation in a visitor object. For an open set of kinds like this one it dissolves into a single generic function, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it. The closed-set form, a `match` over a union that one team owns, is in [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}). What stays design is what the fallback does, where the registrations live and who imports them. The obvious versions fail three ways:

- A fallback that returns a default writes "unclassified" on a battery declaration, and nothing raises.
- Instant coffee has its own heading. Without its own registration it takes the code of the class it extends, and the declaration goes out under the wrong heading.
- A class imported only for the type checker passes mypy and breaks the module that registers it, when that module is imported.

{% include excalidraw.html name="28-singledispatch" described="true" caption="Figure 28.1: tariff_code picks the most specific registered class and falls back to a function that raises. A registration made in another module exists only after that module is imported, and a method dispatches on the argument after self." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-28-singledispatch" markdown="1">
From the top down, `tariff_code`, "one generic function", sends an arrow labelled `dispatch(InstantCoffee)` into a panel named "registry". The panel holds five boxes from left to right: `TShirt`, `InstantCoffee` ("a subclass of Coffee"), `Coffee`, `object` ("fallback: raises TariffCodeError") and `LithiumIonBattery` ("after the import"), and its caption reads "most specific class first". The arrow lands on `InstantCoffee`, which is registered, so dispatch stops there. Amber arrows run from it to `Coffee` and on to `object`; a note beneath the panel says they are next in the MRO when the class before is unregistered. At the top right, `dangerous_goods` ("a separate module") has an arrow into the `LithiumIonBattery` box, labelled "registers LithiumIonBattery when imported". Lower down, `SurchargeSchedule.surcharge` ("dispatch on the argument after self") has an arrow to each of `DryContainer`, `ReeferContainer` and `TankContainer`. A dashed box at the bottom, titled "mypy", reads "checks calls against the fallback, not which kinds are registered".
</div>
</details>

The figure follows one dispatch through the registry, with the extension module and the method form beside it.

## One function, one implementation per kind

A generic function is one name with an implementation per class, and the language picks the implementation from the class of the first argument. The commodity classes don't change: `Coffee` and `TShirt` are frozen dataclasses with no `accept` method, and the operation lives beside the function.

```python
@singledispatch
def tariff_code(commodity: object) -> str:
    raise TariffCodeError(f"no tariff code for {type(commodity).__name__}")


@tariff_code.register
def _coffee(commodity: Coffee) -> str:
    roast = 2 if commodity.roasted else 1
    decaf = 2 if commodity.decaffeinated else 1
    return f"0901.{roast}{decaf}"


@tariff_code.register
def _instant_coffee(commodity: InstantCoffee) -> str:
    return "2101.11"
```

The registrations carry no class argument because the annotation supplies it. The [functools documentation](https://docs.python.org/3/library/functools.html) says "For functions annotated with types, the decorator will infer the type of the first argument automatically". A class and its parameter can't disagree when one place names the class. The seven commodities in `COMMODITY_CODES` get their codes.

The choice among registrations follows the class hierarchy. The same page says "Where there is no registered implementation for a specific type, its method resolution order is used to find a more generic implementation." `InstantCoffee` extends `Coffee`, and with both registered the more specific one wins. Take the `InstantCoffee` registration away and an instant coffee gets `0901.21`, the `Coffee` code. Nothing complains, because a base class answering for its subclasses is the rule working.

The decorated function takes the last place in that order. The page says "The original function decorated with @singledispatch is registered for the base object type, which means it is used if no better implementation is found." A `bool`, which has no registration, lands on it. Two attributes say which implementation will run without calling it: `dispatch(cls)` returns it, and the read-only `registry` maps each registered class (`object`, `Coffee`, `InstantCoffee`, `TShirt`) to its function.

Two more registration forms exist:

- **A union annotation** registers each member. `_beverage_or_garment(commodity: Coffee | TShirt)` answers for both classes and for `InstantCoffee`, which extends one of them. Union annotations have been accepted since 3.11.
- **The functional form**, `register(TShirt, fn)`, returns `fn`. The page describes it as "To enable registering lambdas and pre-existing functions, the register() attribute can also be used in a functional form".

Prefer the annotation form, for the reason in the mypy section below.

## The fallback is a decision

An unregistered kind reaches the `object` implementation, so what that function does is a design choice. `tariff_code` raises. The alternative answers:

<!-- fmt:off -->
```python
    @singledispatch
    def classify(commodity: object) -> str:
        return "unclassified"
```
<!-- fmt:on -->

With the same registrations, both give the seven commodities the same codes. They part on a kind with no registration:

| Fallback | A `LithiumIonBattery` |
| --- | --- |
| raising | `TariffCodeError`: "no tariff code for LithiumIonBattery" |
| defaulting | `"unclassified"`, and nothing else happens |

For a customs declaration the raising form is right: a declaration without a heading shouldn't be filed, and the error names the kind that needs a registration. A defaulting fallback fits where an unknown kind has a sensible general answer, such as a log line that describes any object. Typing the fallback's parameter as `object` keeps the set open; the mypy section shows what a narrower type does.

## What fails when the module loads

A registration runs when its module is imported, and an annotation is resolved at that moment, so the class it names has to exist by then. Here a class is defined after the decorator that names it:

<!-- fmt:off -->
```python
@tariff_code.register
def _(commodity: Banana) -> str:
    return "0803.90"


class Banana: ...
```
<!-- fmt:on -->

At registration this raises `TypeError`: "Invalid annotation for 'commodity'. ForwardRef('Banana', owner=<function _ at 0x...>) is an unresolved forward reference." Define or import the class at run time before the decorator. That includes a class imported only under `if TYPE_CHECKING:`, which the second experiment below tries.

A generic alias is refused too. A function annotated `list[int]` raises `TypeError` matching "is not a class" and leaves the registry holding `object` alone. Pass the class to `register` when the annotation can't name it.

## What mypy checks, and what it can't

mypy types the generic function by its fallback's signature, so calls and registrations are held to the fallback's annotations:

| Against `tariff_code` | mypy |
| --- | --- |
| a registration returning `int` | `[arg-type]`: `register` expects `Callable[..., str]` |
| using the result as an `int` | `[assignment]` |
| a second argument | `[call-arg]`, `Too many arguments for "tariff_code"` |
| `tariff_code(42)` | accepted: the fallback takes any `object` |

A union fallback is what closes the set. A function whose fallback takes `Coffee | Tea | Garment` refuses a registration for `int` with `[misc]`, "must be subtype of fallback function first argument", and refuses the call `strict_code(1)` with `[arg-type]`. A closed set owned by one team is what the `match` form handles, where a missing kind is a type error. With an `object` fallback mypy can't report one, which is the price of an open set.

mypy passes three things the run rejects:

- **The functional form.** `register(Tea, garment_code)` pairs a class with a function whose parameter is a `Garment`. mypy exits 0, and `tariff_code(Tea())` fails with `AttributeError`, no attribute `cotton`. Annotating the parameter and using bare `register` removes the case.
- **A forward reference.** The `Banana` registration above type-checks and fails at import.
- **`singledispatchmethod` arguments,** covered at the end.

## Another module extends the set

The dangerous goods team registers its kind in its own module, and the customs team's module doesn't know about it.

```python
from singledispatch_visitor.commodities import LithiumIonBattery
from singledispatch_visitor.tariff import tariff_code


@tariff_code.register
def _lithium_ion_battery(commodity: LithiumIonBattery) -> str:
    return "8507.60"
```

PEP 443, by Łukasz Langa, says what to expect of a registration made away from the function and the type: "As a result, the vast majority of registered implementations can be found adjacent to either the function being overloaded, or to a newly-defined type for which the implementation is adding support." It continues "It is only in rather infrequent cases that one will have implementations registered in a module that contains neither the function nor the type(s) for which the implementation is added." This is the infrequent case. `tariff.py` imports nothing from `dangerous_goods`, so the registration exists once something imports it. In a fresh interpreter a battery raises `TariffCodeError` before the import and gets `8507.60` after it. The registration is on the function object, so every later call in that process gets the new answer. The design question is who imports the extension: the application's start-up has to.

The registry is read-only: assigning to it raises `TypeError`, and there's no `unregister`. A registration made on `tariff_code` in a test stays for the rest of the pytest process. So test registrations against a fresh dispatcher per test, and check another module's registration in a fresh `python -I` interpreter, where import order and test order can't change what it sees. Module-level state carried between tests is the subject of [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}).

## singledispatchmethod

A method dispatches on its first argument after `self`, and `functools.singledispatchmethod` is the decorator for that. The surcharge for a container depends on its kind.

<!-- fmt:off -->
```python
    @singledispatchmethod
    def surcharge(self, container: object, days: int) -> Money:
        raise SurchargeError(f"no surcharge rule for {type(container).__name__}")

    @surcharge.register
    def _dry(self, container: DryContainer, days: int) -> Money:
        return Money(Decimal("0.00"), self.reefer_per_day.currency)

    @surcharge.register
    def _reefer(self, container: ReeferContainer, days: int) -> Money:
        return self.reefer_per_day.times(days)
```
<!-- fmt:on -->

A dry container costs nothing, a reefer is charged per day and a tank has a cleaning fee. The page says "the dispatch happens on the type of the first non-self or non-cls argument", and a `5` in that position goes to the fallback and raises `SurchargeError`. Combined with another decorator, it goes on top: "singledispatchmethod must be the outer most decorator". mypy doesn't check the method's arguments: `"three"` for the days passes mypy and fails at run time with `TypeError`, "can't multiply sequence". A plain typed method would get `[arg-type]` there.

## When not to use it

- **A closed set.** A closed set that one team owns wants a `match` with `assert_never`, because mypy then reports a missing kind and a registry can't.
- **Dispatch on a value,** such as a service level, is a lookup in a mapping; see [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}).
- **A single kind** is a function.
- **Uncertain imports.** A kind that depends on an import its caller never makes meets the fallback.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a generic function.** "A lookup per commodity type" leaves open what an unknown kind gets, how implementations are registered and where their classes come from. State those in the prompt:

> Write `tariff_code` with `functools.singledispatch` and an `object` fallback that raises `TariffCodeError`. Register each commodity kind with an annotated implementation, not `register(cls, fn)`, and import every class an annotation names at run time. In tests, don't register on `tariff_code`: use a fresh dispatcher, and check another module's registrations in a fresh interpreter.

If the fallback returns a default code, ask which test catches an unregistered kind.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/28-singledispatch
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 33 cases pass and mypy is clean. For how the mypy checks run from pytest, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}). Two experiments:

- **Delete the `InstantCoffee` registration.** In a scratch copy, delete `_instant_coffee` and its decorator from `tariff.py`. Three tests fail on the shorter registry, and 15 table cases error in setup because the defaulting dispatcher reads `registry[InstantCoffee]`. mypy stays green: nothing in the types names the missing registration.
- **Import the class only for the type checker.** In a scratch copy, move the `LithiumIonBattery` import in `dangerous_goods.py` under `if TYPE_CHECKING:`. Only the fresh-interpreter run fails, with the unresolved forward reference `TypeError`, because nothing else imports `dangerous_goods`. mypy stays green.

## What you can do now

- Register by annotation and predict the winner: `_instant_coffee` answers for its class, and without it `_coffee` does.
- Choose the fallback: the raising `object` implementation names a battery nobody registered, where a default would file it as "unclassified".
- Say what fails and what mypy checks: a forward reference fails at registration, and the functional form passes mypy and fails at run time.
- Extend from another module with `dangerous_goods`, and check it before and after the import in a fresh interpreter.
- Dispatch a method with `SurchargeSchedule.surcharge`, on the argument after `self`.

## For deeper coverage

[PEP 443](https://peps.python.org/pep-0443/), by Łukasz Langa, introduced single-dispatch generic functions, and the [functools](https://docs.python.org/3/library/functools.html) documentation is the reference for `singledispatch`, `register`, `dispatch`, `registry` and `singledispatchmethod`. *Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Visitor. *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for the data model and decorators that singledispatch builds on. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
