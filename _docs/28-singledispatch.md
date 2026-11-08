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

A customs declaration needs a tariff code for each kind of commodity, such as coffee or a T-shirt. The customs team owns most of the kinds, and the dangerous goods team adds others that the customs team doesn't own, such as a lithium-ion battery. The headings and rates here are illustrative. Visitor, in *Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994), gives each class an `accept` method and puts each operation in a visitor object. For an open set of kinds like this one it dissolves into a single generic function, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it. The closed-set form, a `match` over a union that one team owns, is in [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}). What stays design is what the fallback does, where the registrations live and who imports them. Three things go wrong in the obvious versions.

A fallback that returns a default writes "unclassified" on a battery declaration, and nothing raises (`test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently`).

Instant coffee has its own heading. Without its own registration it takes the code of the class it extends (`test_an_unregistered_subclass_gets_its_base_class_code`), and the declaration goes out under the wrong heading.

A class imported only for the type checker passes mypy and breaks the module that registers it, when that module is imported.

{% include excalidraw.html name="28-singledispatch" caption="Figure 28.1: tariff_code picks the most specific registered class and falls back to a function that raises. A registration made in another module exists only after that module is imported, and a method dispatches on the argument after self." %}

Read the figure from the top down. `tariff_code`, "one generic function", sends an arrow labelled `dispatch(InstantCoffee)` into a panel named "registry". The panel holds five boxes from left to right: `TShirt`, `InstantCoffee` ("a subclass of Coffee"), `Coffee`, `object` ("fallback: raises TariffCodeError") and `LithiumIonBattery` ("after the import"), and its caption reads "most specific class first". The arrow lands on `InstantCoffee`, which is registered, so dispatch stops there. Amber arrows run from it to `Coffee` and on to `object`, a note beneath the panel says they are next in the MRO when the class before is unregistered. At the top right, `dangerous_goods` ("a separate module") has an arrow into the `LithiumIonBattery` box, labelled "registers LithiumIonBattery when imported". Lower down, `SurchargeSchedule.surcharge` ("dispatch on the argument after self") has an arrow to each of `DryContainer`, `ReeferContainer` and `TankContainer`. A dashed box at the bottom, titled "mypy", reads "checks calls against the fallback, not which kinds are registered".

## One function, one implementation per kind

A generic function is one name with an implementation per class, and the language picks the implementation from the class of the first argument. Nothing about the commodity classes changes: `Coffee` and `TShirt` are frozen dataclasses with no `accept` method, and the operation lives beside the function.

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

The registrations carry no class argument because the annotation supplies it. The [functools documentation](https://docs.python.org/3/library/functools.html) says "For functions annotated with types, the decorator will infer the type of the first argument automatically". A class and its parameter can't disagree when there is one place that names the class. The seven commodities in `COMMODITY_CODES` get their codes (`test_every_fallback_form_gives_registered_commodities_their_codes`).

The choice among registrations follows the class hierarchy. The same page says "Where there is no registered implementation for a specific type, its method resolution order is used to find a more generic implementation." `InstantCoffee` extends `Coffee`, and with both registered the more specific one wins: `dispatch(InstantCoffee)` returns the `InstantCoffee` implementation and not the `Coffee` one (`test_the_most_specific_registration_wins`). Take the registration away and the subclass is answered by its base class. On a fresh dispatcher with `Coffee` registered and `InstantCoffee` not, an instant coffee gets `0901.21` (`test_an_unregistered_subclass_gets_its_base_class_code`). Nothing complains, because a base class answering for its subclasses is the rule working.

The function you decorate takes the last place in that order. The page says "The original function decorated with @singledispatch is registered for the base object type, which means it is used if no better implementation is found." A `bool`, which has no registration, lands on it (`test_dispatch_and_registry_show_the_chosen_implementation`). The same test reads the `dispatch()` attribute and the read-only `registry` attribute, the two ways to ask which implementation will run without calling it, and finds `object`, `Coffee`, `InstantCoffee` and `TShirt` in the registry.

Two more registration forms exist, and the tests use both on a fresh dispatcher. An annotation that is a union registers each member. `_beverage_or_garment(commodity: Coffee | TShirt)` answers for both classes and for the `InstantCoffee` that extends one of them (`test_a_union_annotation_registers_each_member`). Union annotations have been accepted since 3.11, and the test writes the union with `|`. The second form passes a class and a function, `register(TShirt, fn)`. The page describes it as "To enable registering lambdas and pre-existing functions, the register() attribute can also be used in a functional form", and the call returns the function it was given (`test_register_with_a_class_and_a_function_registers_the_function`). The annotation form is the one to prefer, as the mypy section shows.

## The fallback is a decision

An unregistered kind reaches the `object` implementation, so what that function does is a design choice. The example raises. The comparison is a dispatcher with the same three implementations and a fallback that answers.

<!-- fmt:off -->
```python
    @singledispatch
    def classify(commodity: object) -> str:
        return "unclassified"
```
<!-- fmt:on -->

It's a fixture beside the idiomatic form, and both run one table. `fallback_form` is a parameter with two values, `raising` and `defaulting`, and the defaulting dispatcher registers the implementations it reads out of `tariff_code.registry`. The seven commodities get the same codes from both (`test_every_fallback_form_gives_registered_commodities_their_codes`). The forms part on a kind with no registration. The raising form refuses a battery with `TariffCodeError` and names it, "no tariff code for LithiumIonBattery" (`test_a_raising_fallback_names_an_unregistered_kind`). The defaulting form returns "unclassified" and nothing else happens (`test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently`).

For a customs declaration the raising form is the right one, because a declaration without a heading shouldn't be filed, and the error names the kind that needs a registration. A defaulting fallback fits where an unknown kind has a sensible general answer, such as a log line that describes any object. Typing the fallback's parameter as `object` keeps the set open: the mypy section shows what a narrower type does.

## What fails when the module loads

A registration runs when its module is imported, and an annotation is resolved at that moment. The class it names has to exist by then. A reduced model in the tests, with its own `tariff_code` dispatcher, names a class that is defined after the decorator.

<!-- fmt:off -->
```python
@tariff_code.register
def _(commodity: Banana) -> str:
    return "0803.90"


class Banana: ...
```
<!-- fmt:on -->

At registration this raises `TypeError`: "Invalid annotation for 'commodity'. ForwardRef('Banana', owner=<function _ at 0x...>) is an unresolved forward reference." The test masks the address with `re.sub(r"0x[0-9a-f]+", "0x...", ...)` before it compares the text (`test_mypy_accepts_a_forward_reference_that_fails_at_registration`). The fix is to define or import the class at run time before the decorator. That includes a class imported only under `if TYPE_CHECKING:`, which the experiment below tries.

A generic alias is refused as well. A function annotated `list[int]` raises `TypeError` matching "is not a class" and leaves the registry as it was, holding `object` alone (`test_a_generic_alias_is_refused_at_registration`). Pass the class to `register` when the annotation can't name it.

## What mypy checks, and what it can't

mypy types the generic function by its fallback's signature, so the fallback's annotations are what calls and registrations are held to. Three lines break that signature in the test's snippet, which imports the example. A registration returning `int` is refused, `[arg-type]` on the call to `register` that expects `Callable[..., str]`. Using the result as an `int` is `[assignment]`, and a second argument is `[call-arg]`, `Too many arguments for "tariff_code"`. The snippet's last line, `tariff_code(42)`, passes, because the fallback takes any `object` and mypy doesn't say a number has no registration (`test_mypy_checks_calls_and_registrations_against_the_fallback`). Retyping that fallback as a union of the kinds would add the `Argument 1` message to the output and fail the test.

A union fallback is what closes the set. In a reduced model, a snippet inside the test that stands for code and isn't part of the example, a function typed to take `Coffee | Tea | Garment` refuses a registration for `int`, `[misc]` with the message "must be subtype of fallback function first argument", and refuses the call `strict_code(1)`, `[arg-type]` (`test_mypy_refuses_a_kind_outside_a_union_fallback`). A closed set owned by one team is what the `match` form handles, and [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) shows how a missing kind is reported there. With an `object` fallback mypy can't report one, which is the price of an open set.

The functional form gets no check. In a second reduced model, `register(Tea, garment_code)` pairs a class with a function whose parameter is a `Garment`. mypy exits 0 with no output, and the call `tariff_code(Tea())` fails at run time with `AttributeError`, no attribute `cotton` (`test_mypy_accepts_a_registered_class_that_differs_from_the_parameter`). Annotating the parameter with the class and using bare `register` removes the case, which is why the annotation form is the one to use. The forward reference from the last section is the third reduced model: mypy exits 0 on it, and the run fails.

## Another module extends the set

The dangerous goods team registers its kind in its own module, and the customs team's module doesn't know about it.

```python
from singledispatch_visitor.commodities import LithiumIonBattery
from singledispatch_visitor.tariff import tariff_code


@tariff_code.register
def _lithium_ion_battery(commodity: LithiumIonBattery) -> str:
    return "8507.60"
```

PEP 443, by Łukasz Langa, says what to expect of a registration made away from the function and the type: "As a result, the vast majority of registered implementations can be found adjacent to either the function being overloaded, or to a newly-defined type for which the implementation is adding support." It continues "It is only in rather infrequent cases that one will have implementations registered in a module that contains neither the function nor the type(s) for which the implementation is added." This is the infrequent case. `tariff.py` imports nothing from `dangerous_goods`, so the registration exists once something imports it. In a fresh interpreter a battery raises `TariffCodeError` before the import and gets `8507.60` after it, and the registry gains `LithiumIonBattery` (`test_another_module_extends_the_set_when_it_is_imported`). The registration is on the function object, so later calls to `tariff_code` in that process get the new answer. If `tariff.py` imported `dangerous_goods` at its foot, the "before" half of the test would fail. The design question is who imports the extension: the application's start-up has to do it.

The registry is read-only: assigning to it raises `TypeError`, and the function has no `unregister` (`test_the_registry_is_read_only`). A registration that a test makes on `tariff_code` would therefore stay for the rest of the test process. The registration tests use a `fresh_dispatcher` fixture, a new raising dispatcher for each test. The cross-module claim runs in a fresh `python -I` interpreter through a helper, so import order and test order can't change what it sees. Module-level state carried between tests is the subject of [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}).

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

A dry container costs nothing, a reefer is charged per day and a tank has a cleaning fee (`test_surcharge_dispatches_on_the_container_kind`). The page says "the dispatch happens on the type of the first non-self or non-cls argument", and a call with a `5` in that position goes to the fallback and raises `SurchargeError` (`test_singledispatchmethod_dispatches_on_the_first_argument_after_self`). When it's combined with another decorator, it goes on top: "singledispatchmethod must be the outer most decorator". mypy 2.4.1 doesn't check the method's arguments. A call with `"three"` for the days passes with exit 0 and no output, and fails at run time with `TypeError`, "can't multiply sequence" (`test_mypy_does_not_check_the_arguments_of_a_singledispatchmethod`). A plain typed method would make mypy report `[arg-type]` there.

## When not to use it

A closed set that one team owns wants a `match` with `assert_never`, because mypy then reports a missing kind and a registry can't. Dispatch on a value, such as a service level, is a lookup in a mapping, and [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) is the place to look. A single kind is a function. And registrations that nobody is sure will be imported are a risk: a kind that depends on an import its caller never makes meets the fallback.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a generic function.** "A lookup per commodity type" leaves open what an unknown kind gets, how implementations are registered and where their classes come from. State those in the prompt:

> Write `tariff_code` with `functools.singledispatch` and an `object` fallback that raises `TariffCodeError`. Register each commodity kind with an annotated implementation, not `register(cls, fn)`, and import every class an annotation names at run time. In tests, don't register on `tariff_code`: use a fresh dispatcher, and check another module's registrations in a fresh interpreter.

If the fallback returns a default code, ask which test catches an unregistered kind.
</blockquote>

## Build, run, observe

The run shows the registrations answering the seven commodities and the two fallback forms side by side, then a module that extends the set in a fresh interpreter. From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/28-singledispatch
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
collecting ... collected 33 items

tests/test_registration.py::test_a_union_annotation_registers_each_member PASSED [  3%]
tests/test_registration.py::test_register_with_a_class_and_a_function_registers_the_function PASSED [  6%]
tests/test_registration.py::test_a_generic_alias_is_refused_at_registration PASSED [  9%]
tests/test_registration.py::test_another_module_extends_the_set_when_it_is_imported PASSED [ 12%]
tests/test_static.py::test_mypy_checks_calls_and_registrations_against_the_fallback PASSED [ 15%]
tests/test_static.py::test_mypy_refuses_a_kind_outside_a_union_fallback PASSED [ 18%]
tests/test_static.py::test_mypy_accepts_a_registered_class_that_differs_from_the_parameter PASSED [ 21%]
tests/test_static.py::test_mypy_accepts_a_forward_reference_that_fails_at_registration PASSED [ 24%]
tests/test_static.py::test_mypy_does_not_check_the_arguments_of_a_singledispatchmethod PASSED [ 27%]
tests/test_surcharges.py::test_surcharge_dispatches_on_the_container_kind[dry] PASSED [ 30%]
tests/test_surcharges.py::test_surcharge_dispatches_on_the_container_kind[reefer] PASSED [ 33%]
tests/test_surcharges.py::test_surcharge_dispatches_on_the_container_kind[tank] PASSED [ 36%]
tests/test_surcharges.py::test_singledispatchmethod_dispatches_on_the_first_argument_after_self PASSED [ 39%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[raising-coffee-green] PASSED [ 42%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[raising-coffee-green-decaf] PASSED [ 45%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[raising-coffee-roasted] PASSED [ 48%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[raising-coffee-roasted-decaf] PASSED [ 51%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[raising-instant] PASSED [ 54%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[raising-tshirt-cotton] PASSED [ 57%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[raising-tshirt-other] PASSED [ 60%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[defaulting-coffee-green] PASSED [ 63%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[defaulting-coffee-green-decaf] PASSED [ 66%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[defaulting-coffee-roasted] PASSED [ 69%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[defaulting-coffee-roasted-decaf] PASSED [ 72%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[defaulting-instant] PASSED [ 75%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[defaulting-tshirt-cotton] PASSED [ 78%]
tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes[defaulting-tshirt-other] PASSED [ 81%]
tests/test_tariff.py::test_a_raising_fallback_names_an_unregistered_kind PASSED [ 84%]
tests/test_tariff.py::test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently PASSED [ 87%]
tests/test_tariff.py::test_the_most_specific_registration_wins PASSED    [ 90%]
tests/test_tariff.py::test_an_unregistered_subclass_gets_its_base_class_code PASSED [ 93%]
tests/test_tariff.py::test_dispatch_and_registry_show_the_chosen_implementation PASSED [ 96%]
tests/test_tariff.py::test_the_registry_is_read_only PASSED              [100%]

============================== 33 passed in 2.26s ==============================
Success: no issues found in 11 source files
```

The suite has 18 test functions and 33 cases. For how the mypy tests are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

- `tests/test_tariff.py` holds the commodity table, the two fallback forms and the registry tests.
- `tests/test_registration.py` holds the union and functional forms, the generic alias and the fresh-interpreter run.
- `tests/test_surcharges.py` holds the method.
- `tests/test_static.py` holds the mypy witnesses: three reduced models and two that import the example.

**Experiment one: delete the `InstantCoffee` registration.** In a fresh scratch copy, delete the `_instant_coffee` function and its decorator from `tariff.py`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|E {9}TypeError|tests/test_.*Error$|[0-9]+ (passed|failed))' | sed -E 's/0x[0-9a-f]+/0x.../g'` and then `uv run mypy --strict src tests` prints:

```text
E       AssertionError: assert ['Coffee', 'TShirt', 'object'] == ['Coffee', 'I...rt', 'object']
tests/test_registration.py:107: AssertionError
E       KeyError: <class 'singledispatch_visitor.commodities.InstantCoffee'>
tests/test_tariff.py:47: KeyError
E       AssertionError: assert ['Coffee', 'TShirt', 'object'] == ['Coffee', 'I...rt', 'object']
tests/test_tariff.py:61: AssertionError
FAILED tests/test_registration.py::test_another_module_extends_the_set_when_it_is_imported
FAILED tests/test_tariff.py::test_the_most_specific_registration_wins - KeyEr...
FAILED tests/test_tariff.py::test_dispatch_and_registry_show_the_chosen_implementation
3 failed, 15 passed, 15 errors in 2.31s
Success: no issues found in 11 source files
```

Three tests fail. The registry no longer holds `InstantCoffee`, so `test_the_most_specific_registration_wins` raises `KeyError` and the key set in `test_dispatch_and_registry_show_the_chosen_implementation` is short. The fresh-interpreter run lists three registry entries where it expects four. The 15 errors are in fixture setup, because the defaulting dispatcher reads `registry[InstantCoffee]` to build itself, so the table cases that use it stop before their assertions. mypy exits 0: nothing in the types names the missing registration.

**Experiment two: import the class only for the type checker.** In a fresh scratch copy, move the `LithiumIonBattery` import in `dangerous_goods.py` under `if TYPE_CHECKING:`. The same filter, then mypy, prints:

```text
E       AssertionError: Traceback (most recent call last):
E         TypeError: Invalid annotation for 'commodity'. ForwardRef('LithiumIonBattery', owner=<function _lithium_ion_battery at 0x...>) is an unresolved forward reference.
E       assert 1 == 0
tests/test_registration.py:56: AssertionError
FAILED tests/test_registration.py::test_another_module_extends_the_set_when_it_is_imported
1 failed, 32 passed in 2.20s
Success: no issues found in 11 source files
```

One test fails, and it's the fresh-interpreter run: importing the module raises the `TypeError` from the forward reference, and the test's assertion carries that interpreter's output, `Traceback` first and the message last, with the address masked by the sed. Every other test passes, because none of them imports `dangerous_goods`. mypy exits 0, since the annotation is valid to it.

## What you can do now

- Register by annotation and predict the winner: `tariff_code` with `_coffee` and `_instant_coffee`, where `test_the_most_specific_registration_wins` shows the subclass answered by its own implementation and `test_an_unregistered_subclass_gets_its_base_class_code` shows the base class answering without one.
- Choose the fallback: the raising `object` implementation, with `test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently` showing what the other form does to a battery.
- Say what fails and what mypy checks: the forward reference at registration, and `test_mypy_accepts_a_registered_class_that_differs_from_the_parameter` for the functional form that mypy passes and the run rejects.
- Extend from another module: `dangerous_goods`, with `test_another_module_extends_the_set_when_it_is_imported` running before and after the import in a fresh interpreter.
- Dispatch a method: `SurchargeSchedule.surcharge`, with `test_singledispatchmethod_dispatches_on_the_first_argument_after_self` showing the argument after `self` choosing the rule.

## For deeper coverage

[PEP 443](https://peps.python.org/pep-0443/), by Łukasz Langa, introduced single-dispatch generic functions, and the [functools](https://docs.python.org/3/library/functools.html) documentation is the reference for `singledispatch`, `register`, `dispatch`, `registry` and `singledispatchmethod`. *Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Visitor. *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for the data model and decorators that singledispatch builds on. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
