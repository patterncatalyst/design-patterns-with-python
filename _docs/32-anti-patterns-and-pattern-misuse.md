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

A pattern is a structure with a reason. It resolves forces, and its Consequences are the price of doing so. When the forces leave and the structure stays, the price is still paid on each change. That's the working meaning of an anti-pattern here: a recurring structure whose costs outweigh its benefits in the context it sits in. [Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}) sets the measure: count what one change has to edit.

The tools can't do the counting. mypy and ruff pass both forms of the rating code below, so a design several times larger gives no warning. What the extra structure buys instead is three failures:

- A new charge kind breaks the engine's visitor at run time.
- A setter lets a consignment that was already quoted change its quote.
- A located engine with nothing registered constructs, then fails at its first quote.

{% include excalidraw.html name="32-anti-patterns-and-pattern-misuse" described="true" caption="Figure 32.1: The same quote from one function and from a factory, strategy and visitor. They pass the same table and the same type check, but the engine spreads the fuel surcharge across five definitions where the function holds it in one." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-32-anti-patterns-and-pattern-misuse" markdown="1">
Two columns. On the left, an accent box `quote(consignment, tariff)` ("flat fee, fuel surcharge and tax in one definition", "0 classes, 1 function, 8 lines, 1 call") has one arrow down to `RateQuote`. On the right, a dashed chain runs down from `_PricingStrategyFactory` to `_RateEngine` ("9 classes, 17 functions, 57 lines, 11 calls"), `_FlatFeeStrategy.charges`, `_FlatFeeCharge` and `_FuelSurcharge`, `accept`, and `_NetTotalVisitor.visit_flat_fee`, then to a second `RateQuote`. A dashed box, "a new charge kind", points at the visitor box: "a new class and a visit method the visitor does not yet have". A bar across the bottom reads "same table of quotes; mypy and ruff pass both".
</div>
</details>

The figure puts the two forms side by side: the same quote, one definition against a chain of nine classes.

## The rating function and its overbuilt twin

For a single carrier, one function is the whole case: a flat fee per zone, a fuel fee and a tax rate held in a frozen `Tariff`.

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

The 1994 catalogue assumed behaviour reached a call site inside an object of a declared class, so each role gets a class: one that chooses the pricing, one that builds the charges, one per charge kind, and a visitor that adds them up. Python passes a callable where those objects were passed; [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) and [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) cover the two roles that dissolve. The comparison form keeps all of them:

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

The engine is nine classes: the engine, a factory its constructor calls, an abstract strategy and the flat-fee one, an abstract charge and two concrete charges, an abstract visitor and the concrete one that totals. Both forms quote `EU` at 35.70 and `ASIA` at 78.05, and both raise the same `RatingError` with the same message for an unknown zone. The behaviour is identical, so what differs is the cost of the structure.

## Measuring what the structure costs

| Measure | How it's taken | Function | Engine |
| --- | --- | --- | --- |
| Size | `ast`, docstrings stripped, non-blank lines of `ast.unparse` | 0 classes, 1 function, 8 lines | 9 classes, 17 functions, 57 lines |
| Where the fuel rule lives | definitions whose name or statements mention `fuel` | 1 | 5 |
| Calls per quote | `sys.setprofile`, own code only | 1 | 11 |

The five fuel definitions are `_ChargeVisitor.visit_fuel`, `_FlatFeeStrategy.charges`, `_FuelSurcharge`, `_FuelSurcharge.accept` and `_NetTotalVisitor.visit_fuel`. Changing how the surcharge applies means reading five places to find the one that decides. Two of the engine's eleven calls are `_RateEngine.get_tariff`, a getter for a tariff the engine already holds. The call count excludes generated dataclass `__init__` methods, so it counts only code you wrote.

`mypy --strict src tests` and `ruff check` both finish clean on both forms. A type checker verifies that calls fit signatures and a linter verifies style; neither asks whether nine classes were needed. That question needs the count.

## What a new charge costs

The structure is meant to make something cheaper. A remote-area fee is the next charge a carrier adds. In the engine it needs a charge class whose `accept` calls a visit method, and until that method exists the quote fails when it runs: `'_NetTotalVisitor' object has no attribute 'visit_remote_area'`. mypy reports the same shape before the run as `"Visitor" has no attribute "visit_remote_area"` with code `[attr-defined]`.

Declaring the method on the visitor base fixes that and moves the failure. Every concrete visitor becomes abstract, so building one raises `TypeError` for the unimplemented `visit_remote_area`, and mypy reports `[abstract]` at the instantiation. A Visitor suits a fixed set of kinds that gains operations. Here the change that arrives is a new kind, which is the edit this structure makes expensive.

In the function the same change touches one definition, `quote`, and a field on `Tariff`.

## Getters and setters

A getter and setter pair is a promise that the field might need behaviour later. Python makes the promise unnecessary. PEP 8, by Guido van Rossum, Barry Warsaw and Alyssa Coghlan, says "For simple public data attributes, it is best to expose just the attribute name, without complicated accessor/mutator methods." If an attribute later needs behaviour, it adds, "use properties to hide functional implementation behind simple data attribute access syntax." Start with the field.

<!-- fmt:off -->
```python
    def get_zone(self) -> str:
        return self._zone

    def set_zone(self, zone: str) -> None:
        self._zone = zone
```
<!-- fmt:on -->

The pair costs two things:

- **Equality.** `_AccessorConsignment` compares by identity, so two with the same id and zone are unequal. Two frozen `Consignment` values with the same fields are equal.
- **Reproducibility.** Quoting `CN-1` in zone `EU` gives 35.70; after `set_zone("ASIA")` the same object quotes 78.05. A disputed quote can't be recomputed from the consignment on file if the consignment moved.

The domain type is a frozen dataclass:

```python
@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str
```

Assigning to it raises `FrozenInstanceError`, "cannot assign to field 'zone'", so a change of zone becomes a new value. [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers `frozen` and equality, and [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) covers the property PEP 8 points to for a field that grows behaviour.

## A service locator

A service locator is a registry that a class asks for its collaborators, by name, when it needs them. It answers a real need: a collaborator is found by name instead of being passed down through each signature. Martin Fowler's "Inversion of Control Containers and the Dependency Injection pattern" describes it: "The basic idea behind a service locator is to have an object that knows how to get hold of all of the services that an application might need." He names the cost: "The key difference is that with a Service Locator every user of a service has a dependency to the locator." Mark Seemann's "Service Locator is an Anti-Pattern" says the locator "hides a class' dependencies, causing run-time errors instead of compile-time errors". In Python the compile-time check is mypy.

`_ServiceLocator` keeps services in a dictionary of `object`, and the engine reads its tariff from it when it quotes:

<!-- fmt:off -->
```python
    def quote(self, consignment: Consignment) -> RateQuote:
        tariff = self._locator.get("tariff")
        if not isinstance(tariff, Tariff):
            raise TypeError(f"expected a Tariff, got {type(tariff).__name__}")
        return quote(consignment, tariff)
```
<!-- fmt:on -->

Construction succeeds with nothing registered, and the first quote raises `KeyError` for `tariff`. Once a tariff is registered the engine quotes what `quote` quotes. mypy sees it this way:

| Code | mypy |
| --- | --- |
| Uses what `get` returns, no `isinstance` | `"object" has no attribute "price_for"`, `[attr-defined]` and `[no-any-return]` |
| Narrows, then quotes with an empty locator | exits 0; the `KeyError` still happens at run time |
| Calls `quote(consignment)` with no tariff | `Missing positional argument "tariff"`, `[call-arg]` |

Passing the tariff as a parameter turns the unseen failure into the seen one. [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) hands dependencies in without a container.

## When the structure is justified

The function wins in the one-carrier case: one owner and one tariff schedule, so the arithmetic reads in one place. When the forces change, other shapes apply:

- **A Protocol** when the participant holds state or offers several operations, such as a rating service with a loaded table.
- **A Visitor-like split** for many operations over a stable set of kinds; in Python, usually a `match` over a closed union, as in [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}).
- **No interface** with one implementation: it adds a name and no seam.

The question for any class in a design is which change it makes cheaper.

> **🤖 Explore with your agent**
>
> "Price a consignment with one function, `quote(consignment, tariff)`, over a frozen `Tariff`. Use frozen dataclasses with public fields, no `get_` or `set_` methods, and pass every dependency as a parameter. Add a class or a Protocol only when it holds state, offers several operations or has a second implementation today, and name the change it makes cheaper."
>
> If the reply adds a class, ask which change it makes cheaper. For reviewing generated code in general, see [Working with AI and LLM tools]({{ '/docs/40-working-with-ai-and-llm-tools/' | relative_url }}).

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/32-anti-patterns-and-pattern-misuse
uv run pytest -q
uv run mypy --strict src tests
```

All 20 cases pass and mypy is clean. Two experiments, each in a scratch copy, run the count-the-edits measure:

- **Add a charge kind to the engine.** In the fixture file, add an abstract `visit_remote_area(self, charge: _RemoteAreaCharge)` to the visitor base after `visit_fuel`. Seven cases fail: every engine quote, because the concrete visitor is now abstract, and the size count, which rises to 18 functions and 60 lines. The function cases still pass. mypy exits 1 with `[abstract]`, `[unused-ignore]` and `[type-abstract]`.
- **Add it to the function.** Restore the fixture, add `remote_area_fee: Decimal = Decimal("0.00")` to `Tariff` and `+ tariff.remote_area_fee` to the `net` line in `quote`. All 20 pass, mypy exits 0, and the function is still 8 lines in one definition.

## What you can do now

- Measure a design against the plain function: 0 classes, 1 function and 8 lines against 9, 17 and 57, and one definition for the fuel rule against five.
- Say what a Visitor costs when a charge kind arrives: every concrete visitor turns abstract, while the function takes one edit.
- Replace getters and setters with fields: `_AccessorConsignment` changes a quote after the fact, and the frozen `Consignment` refuses.
- Pass the dependency: `_ServiceLocator` fails at the first quote, while a missing `tariff` parameter is a mypy error.
- Write the prompt: name the function, and ask which change each class makes cheaper.

## For deeper coverage

Martin Fowler's [Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html) compares injection styles with a service locator, and Mark Seemann's [Service Locator is an Anti-Pattern](https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/) argues the case against it. [PEP 8](https://peps.python.org/pep-0008/) gives the guidance on accessors and properties. *Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994) is the source for Visitor. It's listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
