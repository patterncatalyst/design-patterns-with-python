---
title: "Strategy: the callable"
order: 12
layout: tutorial
sectionid: docs
part: "selecting-varying-behavior"
description: "Strategy's force survives while its structure dissolves into a callable type, a read-only mapping and a call, which leaves selection, configuration and what a quote records about the rule that priced it."
---

## Learning objectives

By the end of this chapter you can:

- Say which part of Strategy survives in Python, and which part dissolves into a callable type, a mapping and a call.
- Select a rule by name from a read-only registry, raise an unknown name as a domain error, and record the key on the quote.
- Choose between a function, a `partial`, a closure and a frozen dataclass with `__call__` for a configured rule, and say what each lets an audit recover.
- Read what mypy checks on each registry entry, and name a configuration mistake it accepts.
- Recognise the point where a strategy has to be an object, and the prompt that keeps assistant-written code from over-structuring it.

## Why this matters

A pricing rule is a value in a slot. Treat it as anything else and the quote can't name its rule, the registry holds the wrong thing, or a review approves a class hierarchy that a mapping of three callables replaces. What a caller can rely on once it holds a rule is short: it calls the rule with a consignment and gets money back.

{% include excalidraw.html name="12-strategy-the-callable" described="true" caption="Figure 12.1: One quote, three rules in a slot. The caller names a rule, the read-only RATE_RULES registry returns a callable, and quote records the name with the price, whether the rule is a function, a partial or a frozen dataclass." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-12-strategy-the-callable" markdown="1">
The accent box at the top is the call, `quote(consignment, "zone")`, where the caller names a rule. The `RATE_RULES` box below it is read-only and selected by name, and a side arrow leaves it for the box marked "unknown name", which is the `RatingError`. Below the registry three boxes sit side by side: `flat_rate`, a function; `partial(per_kg, rate=...)`, a bound configuration; and `ZoneRate(TARIFF)`, a rule object that is equal and hashable. All three converge on `RateQuote`, which records the rule name and the price.
</div>
</details>

The figure shows three forms of rule filling one slot, and the quote recording which one priced it.

## Pattern: Strategy

### The problem

A rating service prices consignments by a flat fee, by weight or by zone tariff. The force: a caller must choose among several ways of computing one result without depending on which one it holds. Three things go wrong in the obvious versions:

- A quote records `rule.__name__` so a disputed invoice can name its rule, and it crashes on the first rule built with `partial`.
- A registry holds the class `ZoneRate` where an instance belongs, and every zone quote comes back priced as a `ZoneRate` object.
- A pull request adds an abstract `PricingStrategy`, three subclasses and a factory to do what a mapping of three callables does, and nothing shows that the extra structure buys anything.

### The solution

A **Strategy** puts each way of computing a result behind one interface, so the caller holds whichever one it was given and calls it.

**Bucket: dissolves.** A callable type is the interface, a function is the concrete strategy, and the call is the context's only job.

Use a callable strategy when:

- several rules compute the same kind of result from the same input;
- the caller picks the rule by name or receives it from configuration;
- each rule has one operation.

### How Python models it

The slot is a type alias:

```python
type PricingRule = Callable[[Consignment], Money]
```

A `def`, a `lambda` and a `partial` all fill it; [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) shows each. The selection is a mapping and a call:

```python
RATE_RULES: Mapping[str, PricingRule] = frozendict(
    {
        "flat": flat_rate,
        "per-kg": partial(per_kg, rate=Decimal("1.20")),
        "zone": ZoneRate(TARIFF),
    }
)


def quote(
    consignment: Consignment, rule_name: str, *, rules: Mapping[str, PricingRule] = RATE_RULES
) -> RateQuote:
    """Price a consignment with the rule registered under rule_name and record the name."""
    try:
        rule = rules[rule_name]
    except KeyError:
        raise RatingError(f"no pricing rule named {rule_name!r}") from None
    return RateQuote(consignment.id, rule_name, rule(consignment))
```

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) builds Strategy from a strategy interface, a concrete class per algorithm and a context that holds one. Luciano Ramalho's *Fluent Python*, second edition, in "Design Patterns with First-Class Functions", puts functions where the one-method classes were, and the treatment here starts from his.

### The class-per-strategy comparison

The class design still works. Its base class and one of three subclasses:

<!-- fmt:off -->
```python
class _PricingStrategy(ABC):
    @abstractmethod
    def price(self, consignment: Consignment) -> Money: ...


class _PerKgStrategy(_PricingStrategy):
    def price(self, consignment: Consignment) -> Money:
        amount = consignment.weight.kilograms * Decimal("1.20")
        return Money(amount.quantize(_CENT, rounding=ROUND_HALF_UP), "EUR")
```
<!-- fmt:on -->

It passes the same behaviour table as the registry, for the flat, per-kilogram and zone rows. The difference is declaration. Counting the classes that define `__call__` or `price`, parsed with `ast`, the rules module declares one, `ZoneRate`, and the class design declares four. That one remaining class holds a configuration in a form an audit can compare, which a function can't. Why the slot is called `PricingRule` and not `RateStrategy` is argued in [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}).

### Choosing a rule by name

A caller that picks a rule needs a registry, a failure that belongs to the domain and a record of what it picked.

The registry is a `frozendict`, new in 3.15 ([PEP 814](https://peps.python.org/pep-0814/)), typed as a `Mapping` so callers see only the read side. Assigning a key raises `TypeError` ("does not support item assignment"). For dispatch tables in general, see [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}); for adding a rule as data without editing callers, see [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}).

An unknown name is a `RatingError` (`no pricing rule named 'express'`), not a `KeyError`, and `from None` suppresses the original, so the caller sees one error at the level of the rating domain. The quote records the key it was given, beside the consignment id and the price. A disputed invoice can then say which rule priced it without introspecting the rule.

### Configured rules: a partial, a closure, or a rule object

`per_kg` needs a rate, so the registry binds one with `partial`. `ZoneRate` needs a tariff, so it's a frozen dataclass whose `__call__` reads the tariff:

```python
@dataclass(frozen=True, slots=True)
class ZoneRate:
    """A rule object: configured by a tariff, equal and hashable by value."""

    tariff: Tariff

    def __call__(self, consignment: Consignment, /) -> Money:
        try:
            rate = self.tariff.per_kg_by_zone[consignment.zone]
        except KeyError:
            raise RatingError(f"no tariff for zone {consignment.zone!r}") from None
        amount = (consignment.weight.kilograms * rate).quantize(_CENT, rounding=ROUND_HALF_UP)
        return Money(amount, self.tariff.currency)
```

Both fill the slot. They differ in what an audit can recover afterwards:

| Form | `__name__` | Equal when built the same way | Repr free of an address |
| --- | --- | --- | --- |
| function | `flat_rate` | same object | no |
| lambda | `<lambda>` | no | no |
| closure | `rule` | no | no |
| `partial` | absent | no | no |
| frozen dataclass with `__call__` | absent | yes, and the hashes match | yes |

The `functools` documentation on [partial objects](https://docs.python.org/3/library/functools.html) says why the `partial` row has no name: "the `__name__` and `__doc__` attributes are not created automatically." A rule object is an instance, so it has none either. Two partials of `per_kg` with the same rate are unequal, though their `func` and `keywords` attributes are equal. Two `ZoneRate` instances from equal tariffs are equal, hash equal and print as `ZoneRate(tariff=Tariff(...`. The repr of a partial carries the address of the function it wraps, so the last column is from a recorded run, not an assertion.

Two consequences follow:

- **Record the registry key**, as `quote` does, because the key survives where a name can't.
- **Use a rule object when quotes must be compared by the rule that priced them.** Equal `ZoneRate` instances mean the same configuration; two partials compare only attribute by attribute, through `func` and `keywords`. For injecting a `partial` where a collaborator is expected, see [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}).

Both configured rules round half up to the cent. 0.1875 kg at 1.20 is 0.225, which is 0.23 half up and 0.22 half even; 28.85 kg at 0.50 is 14.425, which is 14.43 and 14.42. The rules return the half-up cent.

### What mypy checks in a strategy slot

A registry entry is checked against `PricingRule` where the dictionary is built. A valid registry is clean. A function with the wrong return type:

```text
<string>:13: error: Dict entry 0 has incompatible type "str": "Callable[[Consignment], Decimal]"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
```

`per_kg` registered unbound, so its required keyword-only parameter shows:

```text
<string>:9: error: Dict entry 0 has incompatible type "str": "def per_kg(consignment: Consignment, *, rate: Decimal) -> Money"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
```

A lambda whose body returns the wrong type draws a second error from inside the lambda:

```text
<string>:9: error: Dict entry 0 has incompatible type "str": "Callable[[Consignment], Decimal]"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
<string>:9: error: Incompatible return value type (got "Decimal", expected "Money")  [return-value]
```

And the class registered where an instance belongs, the failure from the opening, caught before any quote runs:

```text
<string>:9: error: Dict entry 0 has incompatible type "str": "type[ZoneRate]"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
```

The class `ZoneRate` is itself a callable that takes a tariff and returns a `ZoneRate`, so it doesn't fit a slot that takes a consignment and returns money.

A configured rule is checked less well. A misspelt keyword is rejected:

```text
<string>:9: error: Unexpected keyword argument "rat" for "per_kg"; did you mean "rate"?  [call-arg]
<string>:9: note: "per_kg" defined in "strategy_callable.rules"
```

A `partial` that binds nothing is accepted in the typed `PricingRule` slot, as a registry entry is, and fails only when called: `TypeError`, "missing 1 required keyword-only argument: 'rate'". [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) documents the same gap. Read a registry's `partial` entries by eye.

When a rule needs keyword parameters, overloads or attributes the callable type can't express, use a callback Protocol with a positional-only `/`; see [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}).

### When a strategy has to be an object

The callable type promises that a consignment goes in and money comes out. It doesn't promise the same money twice for the same consignment. This closure counts its calls:

```python
def _make_loyalty_discount() -> PricingRule:
    """A closure that counts its own calls, so its answer depends on history."""
    calls = 0

    def rule(consignment: Consignment) -> Money:
        nonlocal calls
        calls += 1
        return Money(Decimal("25.00") - Decimal(calls), "EUR")

    return rule
```

Called twice on one consignment, it returns 24.00 and then 23.00, and mypy accepts it, because the signature fits the slot. A quote that records the key `"loyalty"` can no longer be reproduced from that key. State belongs in an argument or in a configuration that doesn't change, such as the frozen `Tariff` that `ZoneRate` holds.

A rule that has to do more than price, such as explain its price or validate a consignment first, has several operations, and a callable type no longer describes it. That's the `RateCalculator` case in [Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}). The class is still optional there, because anything with the right methods satisfies a Protocol, but the Protocol becomes the contract.

## When not to use it

- **Strategy.** A single rule called from one place is a function, with no registry. A registry consulted with a literal key everywhere, `RATE_RULES["zone"](c)`, is a dispatch table in disguise, and a plain call reads better. Rules that need different inputs are a signature problem: a rule that wants the carrier as well as the consignment doesn't fit `PricingRule`, and the slot changes before any registry does. A rule object with no configuration to hold and no value comparison to make adds a class an audit can't use.

> **🤖 Explore with your agent**
>
> "Type the slot as `type PricingRule = Callable[[Consignment], Money]`. Register rules in a read-only `frozendict` typed `Mapping[str, PricingRule]`: a function, a `partial` that binds every parameter its rule needs, or a frozen dataclass with `__call__` when the configuration must compare by value. Raise an unknown name as `RatingError`. Record the registry key on `RateQuote`, not `__name__`. A rule's result depends only on its argument. No base class."
>
> If a `partial` entry binds nothing, ask for the call that fails.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/12-strategy-the-callable
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 31 cases pass, and mypy reports `Success: no issues found in 9 source files`. Two experiments, each in a scratch copy:

- **Register the class.** Replace `ZoneRate(TARIFF)` in `RATE_RULES` with `ZoneRate`. mypy reports the `type[ZoneRate]` dict entry on `rules.py`. Six tests fail: calling the class builds a `ZoneRate` holding the consignment as its tariff, so every zone price is the wrong type, and asking the entry for `__name__` no longer raises.
- **Bind nothing.** Replace `partial(per_kg, rate=Decimal("1.20"))` with `partial(per_kg)`. mypy stays green, and the three per-kilogram cases fail at call time with the missing `rate` `TypeError`.

## What you can do now

- Say what survives of Strategy, the `PricingRule` slot, and what dissolves: four strategy classes become one.
- Select a rule by name from `RATE_RULES`, raise `RatingError` for an unknown name, and record the key on the quote.
- Choose the form of a configured rule from the five-form table: `partial` for `per_kg`, a frozen `ZoneRate` where an audit must compare values.
- Read the mypy errors for each bad registry entry, and remember the unbound `partial` it accepts.
- Recognise when a strategy must be an object: a rule with hidden state can't be reproduced, and a rule with several operations needs the `RateCalculator` Protocol.

## For deeper coverage

Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software*, is the source for Strategy, and Luciano Ramalho's *Fluent Python*, second edition, "Design Patterns with First-Class Functions", is the treatment followed here. Both are on the [bibliography page]({{ '/bibliography/' | relative_url }}), where Brett Slatkin's *Effective Python*, third edition, is also listed for closures and `functools.partial`.

The language sources are the `functools` documentation on [partial objects](https://docs.python.org/3/library/functools.html), [PEP 695](https://peps.python.org/pep-0695/) for the `type` statement behind `PricingRule`, [PEP 814](https://peps.python.org/pep-0814/) for `frozendict`, and the [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) for `frozen` and the generated `__eq__` and `__hash__`.
