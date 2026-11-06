---
title: "Anti-patterns and pattern misuse"
order: 32
layout: tutorial
sectionid: docs
part: "patterns-in-the-wild"
description: "A pattern kept after its forces have gone is an anti-pattern. Price the same consignments with a function and with a class for every role, and count what the structure costs."
---

## Learning objectives

By the end of this chapter you can:

- Measure a design against the plain function on the same table: classes, functions, lines, calls, and how many definitions one rule lives in.
- Say what a Visitor costs when a new charge kind arrives.
- Replace getter and setter pairs with fields, frozen dataclasses and properties.
- Explain how a service locator moves a missing dependency from mypy to run time, and pass the dependency instead.
- Write a prompt that keeps generated code to the shape the forces justify.

## Why this matters

A pattern is a structure with a reason. It resolves forces, and its Consequences are the price of doing so. When the forces leave and the structure stays, the price is still paid on each change. That's the working meaning of an anti-pattern here: a recurring structure whose costs outweigh its benefits in the context it sits in. The test comes from [Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}), which argues the one-carrier rating case in prose and counts what one change has to edit. Here both forms are written and run against the same consignments, and what each costs is counted.

The tools can't do the counting. mypy and ruff pass both forms of the rating code below, so a design several times larger gives no warning. Three failures show what the extra structure buys instead.

A new charge kind breaks the engine's visitor at run time (`test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`). A setter lets a consignment that was already quoted change its quote (`test_a_setter_lets_a_quoted_consignment_change_its_quote`). A located engine with nothing registered constructs, and fails at its first quote (`test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`).

{% include excalidraw.html name="32-anti-patterns-and-pattern-misuse" caption="Figure 32.1: The same quote from one function and from a factory, strategy and visitor. They pass the same table and the same type check, but the engine spreads the fuel surcharge across five definitions where the function holds it in one." %}

Read the figure in two columns. On the left, an accent box `quote(consignment, tariff)` ("flat fee, fuel surcharge and tax in one definition", "0 classes, 1 function, 8 lines, 1 call") has one arrow down to `RateQuote`. On the right, a dashed chain runs down from `_PricingStrategyFactory` to `_RateEngine.quote` ("9 classes, 17 functions, 57 lines, 11 calls"), `_FlatFeeStrategy.charges`, `_FlatFeeCharge` and `_FuelSurcharge`, `accept`, and `_NetTotalVisitor.visit_flat_fee`, then to a second `RateQuote`. A dashed box, "a new charge kind", points at the visitor box: "a new class and a visit method the visitor does not yet have". A bar across the bottom reads "same table of quotes; mypy and ruff pass both".

## The rating function and its overbuilt twin

Patterns as decisions under forces recommends one function when a single carrier is the whole case. Here it is written for the first time, with a flat fee per zone, a fuel fee and a tax rate held in a frozen `Tariff`:

```python
def quote(consignment: Consignment, tariff: Tariff) -> RateQuote:
    """Price a consignment: its zone's flat fee, the fuel fee, then tax rounded to the cent."""
    try:
        flat_fee = tariff.flat_fee_by_zone[consignment.zone]
    except KeyError:
        raise RatingError(f"no flat fee for zone {consignment.zone!r}") from None
    net = flat_fee + tariff.fuel_fee
    tax = (net * tariff.tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, Money(net + tax, tariff.currency))
```

The 1994 catalogue assumed that behaviour reached a call site inside an object of a declared class, so each role in this calculation gets a class: one that chooses the pricing, one that builds the charges, one per charge kind, and a visitor that adds them up. Python passes a callable where those objects were passed, and [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) and [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) show the two roles that dissolve. The comparison form, which lives in the test fixtures, keeps all of them:

<!-- fmt:off -->
```python
    def quote(self, consignment: Consignment) -> RateQuote:
        visitor = _NetTotalVisitor()
        for charge in self._strategy.charges(consignment):
            charge.accept(visitor)
        net = visitor.total
        tax = (net * self.get_tariff().tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, Money(net + tax, self.get_tariff().currency))
```
<!-- fmt:on -->

The engine is nine classes: the engine itself, a factory that its constructor calls, an abstract strategy and the flat-fee one, an abstract charge and two concrete charges, an abstract visitor and the concrete one that totals. Both forms run one table of quotes. `EU` quotes 35.70 and `ASIA` quotes 78.05 through each of them (`test_every_rating_form_quotes_the_same_table`), and an unknown zone raises the same `RatingError` with the same message (`test_every_rating_form_refuses_an_unknown_zone`). The behaviour is identical, so what differs is the cost of the structure.

## Measuring what the structure costs

The first measure is size, taken with the `ast` module. The tests parse the function's source and the nine engine class definitions from the fixture file, strip docstrings, and count classes, functions and the non-blank lines of `ast.unparse` output. The function has 0 classes, 1 function and 8 lines. The engine has 9 classes, 17 functions and 57 lines (`test_the_engine_needs_more_classes_functions_and_lines_than_the_function`).

The second measure is where one rule lives. The fuel surcharge is one decision, and the test finds every definition whose own name or own statements mention `fuel`. In the function that is `quote`. In the engine it is five definitions: `_ChargeVisitor.visit_fuel`, `_FlatFeeStrategy.charges`, `_FuelSurcharge`, `_FuelSurcharge.accept` and `_NetTotalVisitor.visit_fuel` (`test_the_fuel_surcharge_lives_in_one_definition_of_the_function`). Changing how the surcharge is applied means reading five places to find the one that decides.

The third measure is calls. `sys.setprofile` records each Python-level call into code defined in the rating module or the fixture file during one quote, and the tests compare the ordered names. A quote through the function enters one Python function, `quote` itself. Through the engine it enters eleven, and two of them are `_RateEngine.get_tariff`, a getter that the engine calls to read a tariff it already holds (`test_one_engine_quote_makes_more_python_calls_than_the_function`). Generated dataclass `__init__` methods and the test's own frames are filtered out, so the count is of the code you wrote.

mypy `--strict` and ruff pass both forms. `mypy --strict src tests` covers the fixture engine and `ruff check` covers the example, and both finish clean. A type checker verifies that calls fit signatures, and a linter verifies style; neither is asked whether nine classes were needed. That question needs the count.

## What a new charge costs

The count matters because the structure is meant to make something cheaper. A remote-area fee is the next charge a carrier adds. In the engine it needs a charge class whose `accept` calls a visit method, and the fixture models the step in which that method doesn't exist yet. The quote then fails when it runs: `'_NetTotalVisitor' object has no attribute 'visit_remote_area'` (`test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`). mypy sees it before the run, as `"Visitor" has no attribute "visit_remote_area"` with code `[attr-defined]` (`test_mypy_reports_a_visitor_missing_a_new_visit_method`, a reduced model that restates the visitor shape in a self-contained snippet).

Declaring the method on the visitor base is the fix, and it moves the failure. The fixture models it with `_NetTotalWithRemoteArea`, the concrete visitor over a base that declares the method, and building it raises a `TypeError` for the unimplemented `visit_remote_area` (`test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract`). Experiment one below declares it on the real base. The same reduced model gets `[abstract]` from mypy for that instantiation. A Visitor suits a fixed set of kinds that gains operations. Here the change that arrives is a new kind, which is the edit this structure makes expensive.

In the function the same change touches one definition, `quote`, and a field on `Tariff`. The experiments below run both.

## Getters and setters

A getter and setter pair is a promise that the field might need behaviour later. Python makes the promise unnecessary. PEP 8, by Guido van Rossum, Barry Warsaw and Alyssa Coghlan, says "For simple public data attributes, it is best to expose just the attribute name, without complicated accessor/mutator methods." It adds that if an attribute later needs behaviour, "use properties to hide functional implementation behind simple data attribute access syntax." Start with the field.

The fixture shows what the pair costs:

<!-- fmt:off -->
```python
    def get_zone(self) -> str:
        return self._zone

    def set_zone(self, zone: str) -> None:
        self._zone = zone
```
<!-- fmt:on -->

`_AccessorConsignment` compares by identity, so two accessor consignments with the same id and zone are unequal, while two frozen `Consignment` values with the same fields are equal (`test_an_accessor_consignment_has_no_value_equality`). The setter also changes a consignment after it has been quoted. Quoting `CN-1` in zone `EU` gives 35.70, calling `set_zone("ASIA")` and quoting the same object gives 78.05 (`test_a_setter_lets_a_quoted_consignment_change_its_quote`). That breaks the reproducibility force from [Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}): a disputed quote can't be recomputed from the consignment on file if the consignment moved.

The domain type is a frozen dataclass, and assigning to it fails:

```python
@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str
```

The error is `FrozenInstanceError`, "cannot assign to field 'zone'" (`test_a_frozen_consignment_refuses_assignment`). A change of zone becomes a new value. [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers `frozen` and equality, and [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) covers the property PEP 8 points to for a field that grows behaviour.

## A service locator

A service locator is a registry that a class asks for its collaborators, by name, when it needs them. It answers a real need: a collaborator is found by name and isn't passed down through each signature. Martin Fowler's article "Inversion of Control Containers and the Dependency Injection pattern" describes it: "The basic idea behind a service locator is to have an object that knows how to get hold of all of the services that an application might need." It then names the cost: "The key difference is that with a Service Locator every user of a service has a dependency to the locator." Mark Seemann's post "Service Locator is an Anti-Pattern" says the locator "hides a class' dependencies, causing run-time errors instead of compile-time errors". In this book the compile-time check is mypy.

The fixture's `_ServiceLocator` keeps services in a dictionary of `object`, and the engine reads its tariff from it when it quotes:

<!-- fmt:off -->
```python
    def quote(self, consignment: Consignment) -> RateQuote:
        tariff = self._locator.get("tariff")
        if not isinstance(tariff, Tariff):
            raise TypeError(f"expected a Tariff, got {type(tariff).__name__}")
        return quote(consignment, tariff)
```
<!-- fmt:on -->

Construction succeeds with nothing registered, and the first quote raises `KeyError` for `tariff` (`test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`). Once a tariff is registered the engine quotes what `quote` quotes (`test_a_located_engine_quotes_once_its_tariff_is_registered`). Three mypy results mark the edges. Each of the first two uses a reduced model, a self-contained snippet with its own locator, because the point is the shape. Without the `isinstance` narrowing, using what `get` returns is an error: `"object" has no attribute "price_for"` with `[attr-defined]` and `[no-any-return]` (`test_mypy_needs_a_type_check_to_use_a_located_service`). With the narrowing in place, mypy exits 0 on a program that constructs an empty locator and quotes, and the run-time `KeyError` still happens (`test_mypy_does_not_see_a_missing_registration`). A missing argument is a different case. Calling `quote(consignment)` without a tariff is reported as `Missing positional argument "tariff"` with `[call-arg]` (`test_mypy_reports_a_missing_tariff_argument`).

Passing the tariff as a parameter turns the unseen failure into the seen one. [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) shows how to hand dependencies in without a container.

## When the structure is justified

The function wins on the forces in the one-carrier case: one owner and one tariff schedule, so the arithmetic reads in one place. It stops winning when the forces change, and the shapes from [Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}) then apply. A Protocol is the right participant when it holds state or offers several operations, such as a rating service with a loaded table. A Visitor-like split fits many operations over a stable set of kinds, and in Python that usually means a `match` over a closed union, as [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) shows. An interface with one implementation adds a name and no seam. Each of these answers to a force, and the question for any class in a design is which change it makes cheaper.

<blockquote class="ai-sidebar" markdown="1">

**Specifying the shape the forces justify.** A request for "a flexible rating engine" leaves the structure open, and a factory, a strategy and a visitor for one flat fee all type-check. Paste a prompt that states the forces:

> Price a consignment with one function, `quote(consignment, tariff)`, over a frozen `Tariff`. Use frozen dataclasses with public fields, no `get_` or `set_` methods, and pass every dependency as a parameter. Add a class or a Protocol only when it holds state, offers several operations or has a second implementation today, and name the change it makes cheaper.

If the reply adds a class, ask which change it makes cheaper. For reviewing generated code in general, see [Working with AI and LLM tools]({{ '/docs/40-working-with-ai-and-llm-tools/' | relative_url }}).

</blockquote>

## Build, run, observe

From the example directory, `uv run pytest` runs 16 test functions as 20 cases, and `uv run mypy --strict src tests` checks the example. The two experiments below make the count-the-edits test a run. Each one changes a scratch copy and nothing else. The first adds a charge kind's visit method to the engine's visitor base, in the fixture file, by adding

<!-- fmt:off -->
```python
    @abstractmethod
    def visit_remote_area(self, charge: _RemoteAreaCharge) -> None: ...
```
<!-- fmt:on -->

after `visit_fuel`. Then:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|errors?))'
uv run mypy --strict src tests
```

```text
E       TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'
tests/conftest.py:102: TypeError
E       TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'
tests/conftest.py:102: TypeError
E       TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'
tests/conftest.py:102: TypeError
E       assert (9, 18, 60) == (9, 17, 57)
E         At index 1 diff: 18 != 17
E         Use -v to get more diff
tests/test_measure.py:119: AssertionError
E       TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'
tests/conftest.py:102: TypeError
E       TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'
tests/conftest.py:102: TypeError
E       TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'
tests/test_measure.py:168: TypeError
FAILED tests/test_forms.py::test_every_rating_form_quotes_the_same_table[engine-eu]
FAILED tests/test_forms.py::test_every_rating_form_quotes_the_same_table[engine-asia]
FAILED tests/test_forms.py::test_every_rating_form_refuses_an_unknown_zone[engine]
FAILED tests/test_measure.py::test_the_engine_needs_more_classes_functions_and_lines_than_the_function
FAILED tests/test_measure.py::test_one_engine_quote_makes_more_python_calls_than_the_function
FAILED tests/test_measure.py::test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time
FAILED tests/test_measure.py::test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract
7 failed, 13 passed in 1.77s
tests/conftest.py:102: error: Cannot instantiate abstract class "_NetTotalVisitor" with abstract attribute "visit_remote_area"  [abstract]
tests/conftest.py:114: error: Unused "type: ignore" comment  [unused-ignore]
tests/conftest.py:214: error: Only concrete class can be given where "type[_NetTotalVisitor]" is expected  [type-abstract]
Found 3 errors in 1 file (checked 7 source files)
```

Seven tests fail. The three engine cases in the forms tests and the call-count and run-time visitor tests fail because the engine can't build its visitor. The size test fails because the engine now has 18 functions and 60 lines. The abstract-visitor test fails earlier than it means to: its first line builds the plain concrete visitor, which is now abstract too. The function cases still pass. mypy exits 1 with three errors: `[abstract]` where the concrete visitor is built, `[unused-ignore]` on the comment that silenced the missing method, which exists now, and `[type-abstract]` where the class is passed as a type.

The second experiment restores the fixture file and changes `src` instead: add `remote_area_fee: Decimal = Decimal("0.00")` to `Tariff`, and add `+ tariff.remote_area_fee` to the `net` line in `quote`. The same two commands print:

```text
20 passed in 1.70s
Success: no issues found in 7 source files
```

All 20 pass and mypy exits 0. The size test still sees 8 lines in the function, because the fee fits on the existing line. The function's footprint stays one definition.

## What you can do now

- Measure a design against the plain function: `test_the_engine_needs_more_classes_functions_and_lines_than_the_function` counts 0, 1 and 8 against 9, 17 and 57, and `test_the_fuel_surcharge_lives_in_one_definition_of_the_function` counts one definition against five.
- Say what a Visitor costs when a charge arrives: `test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract` fails the build of the concrete visitor, and the experiment's change to `quote` is one edit.
- Replace getters and setters with fields: `_AccessorConsignment` changes a quote after the fact, and the frozen `Consignment` in `test_a_frozen_consignment_refuses_assignment` doesn't.
- Pass the dependency: `_ServiceLocator` fails at the first quote in `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`, while `test_mypy_reports_a_missing_tariff_argument` names the missing parameter.
- Write the prompt: the sidebar's request names the function and the question to ask of any class.

## For deeper coverage

Martin Fowler's [Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html) compares injection styles with a service locator, and Mark Seemann's [Service Locator is an Anti-Pattern](https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/) argues the case against it. [PEP 8](https://peps.python.org/pep-0008/) gives the guidance on accessors and properties. *Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994) is the source for Visitor. It's listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
