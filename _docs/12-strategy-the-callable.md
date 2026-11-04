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
- Recognise the point where a strategy has to be an object, and the review checks that catch assistant-written over-structure.

## Why this matters

Three failures come from treating a rule as something other than a value in a slot. A quote records `rule.__name__` so that a disputed invoice can name its rule, and it crashes on the first rule built with `partial`. A registry holds the class `ZoneRate` where an instance belongs, and every zone quote comes back priced as a `ZoneRate` object. A pull request adds an abstract `PricingStrategy`, three subclasses and a factory to do what a mapping of three callables does, and the reviewer has no test that says the extra structure buys anything.

Each is a question about what a caller can rely on once it holds a rule: whether it can be named, and whether a second quote from it matches the first.

{% include excalidraw.html name="12-strategy-the-callable" caption="Figure 12.1: One quote, three rules in a slot. The caller names a rule, the read-only RATE_RULES registry returns a callable, and quote records the name with the price, whether the rule is a function, a partial or a frozen dataclass." %}

Read the figure from the top. The accent box is the call, `quote(consignment, "zone")`, where the caller names a rule. The `RATE_RULES` box below it is read-only and selected by name, and a side arrow leaves it for the box marked "unknown name", which is the `RatingError`. Below the registry three boxes sit side by side: `flat_rate`, a function; `partial(per_kg, rate=...)`, a bound configuration; and `ZoneRate(TARIFF)`, a rule object that is equal and hashable. All three converge on `RateQuote`, which records the rule name and the price.

## The force that remains

*Design Patterns*, by Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides, catalogues Strategy for the case where a caller must choose among several ways of computing one result without depending on which one it holds. The catalogue's solution is a strategy interface, a concrete class per algorithm, and a context that holds one. Luciano Ramalho's *Fluent Python*, second edition, in the chapter titled "Design Patterns with First-Class Functions", works through the same pattern with functions where the one-method classes were, and this chapter starts from that treatment.

The force is intact: a caller chooses an algorithm at run time and must not depend on which one it got. The structure is what goes. This pattern dissolves, because a feature resolves the force without the pattern's structure. A callable type is the interface, a function is the concrete strategy, and the call is the context's only job. The chapter titled [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) shows the `PricingRule` alias and the slot that a `def`, a `lambda` and a `partial` fill, and this chapter doesn't repeat it.

What the earlier chapter doesn't measure is the cost of the structure. The example keeps a class-per-strategy design as a test fixture: an abstract `_PricingStrategy`, a subclass per rule and a registry of instances. Two of its four classes, beside the callables:

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

It isn't wrong. `test_a_class_per_strategy_passes_the_same_table` runs it against the same behaviour table as `test_each_registered_rule_prices_the_behaviour_table`, and both pass for the flat, per-kilogram and zone rows. The difference is declaration: `test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one` parses both modules with `ast` and counts the classes that define `__call__` or `price`. The rules module has one, `ZoneRate`. The fixture has four. The count is of declarations, not lines, because line counts move with formatting. The one class that remains is justified below: it holds a configuration in a form that an audit can compare, which a function can't. Why the slot is called `PricingRule` and not `RateStrategy` is argued in [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}).

## Choosing a rule by name

A caller that picks a rule needs three things: a registry, a failure that belongs to the domain, and a record of what it picked.

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

The registry is a `frozendict`, new in 3.15 ([PEP 814](https://peps.python.org/pep-0814/)), typed as a `Mapping` so that callers see only the read side. `test_the_rule_registry_is_read_only` assigns a new key and gets `TypeError` with "does not support item assignment", and asserts that the registry isn't a `dict`. The mapping is the selection mechanism and nothing in it knows about the rules' types beyond the slot. For dispatch tables as a general technique, see the chapter titled [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}). For adding a rule as data without editing the registry's callers, see [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}).

An unknown name is a `RatingError`, not a `KeyError`. `test_an_unknown_rule_name_is_a_rating_error` asks for `"express"` and matches the message `no pricing rule named 'express'`, and it checks that the original `KeyError` is suppressed, so the caller sees one error at the level of the rating domain. The quote records the key it was given. `test_a_quote_records_the_rule_that_priced_it` runs all three names and asserts that `RateQuote.rule` equals the name, with the consignment id and the price beside it. A disputed invoice can then say which rule priced it, and the evidence doesn't depend on introspecting the rule.

## Configured rules: a partial, a closure, or a rule object

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

Both fill the slot, and they differ in what an audit can recover afterwards. A run of the five forms side by side, with the example's `per_kg` and `ZoneRate`, gives:

| Form | `__name__` | Equal when built the same way | Repr free of an address |
| --- | --- | --- | --- |
| function | `flat_rate` | same object | no |
| lambda | `<lambda>` | no | no |
| closure | `rule` | no | no |
| `partial` | absent | no | no |
| frozen dataclass with `__call__` | absent | yes, and the hashes match | yes |

The `functools` documentation on [partial objects](https://docs.python.org/3/library/functools.html) says why the `partial` row has no name: "the `__name__` and `__doc__` attributes are not created automatically." A rule object is an instance, so it has none either. `test_partials_and_rule_objects_have_no_name` asks for `__name__` on the `per-kg` and `zone` entries and gets `AttributeError` for each, while `flat_rate.__name__` is `"flat_rate"` and a lambda's is `"<lambda>"`.

Equality splits the same way. `test_a_partial_has_no_value_equality` builds two partials of `per_kg` with the same rate and finds them unequal, while their `func` and `keywords` attributes are equal. `test_a_rule_object_compares_and_hashes_by_value` builds a second `ZoneRate` from an equal tariff and finds the two equal, with equal hashes and a repr that starts `ZoneRate(tariff=Tariff(`. The repr of a partial carries the address of the function it wraps, so no test asserts it, and the table's last column rests on the run, not on an assertion.

Two consequences follow. Record the registry key, as `quote` does, because the key survives where a name can't. And use a rule object when two quotes have to be compared by the rule that priced them: two quotes priced by equal `ZoneRate` instances were priced by the same configuration, and two partials can be compared only attribute by attribute, through `func` and `keywords`. For injecting a `partial` where a collaborator is expected, see [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}).

Both configured rules round half up to the cent. `test_rules_round_half_up_to_cents` picks cases that sit on a half cent: 0.1875 kg at 1.20 is 0.225, which rounds to 0.23 half up and 0.22 half even, and 28.85 kg at 0.50 is 14.425, which gives 14.43 and 14.42. The test computes both modes and asserts the rules return the half-up cent.

## What mypy checks in a strategy slot

A registry entry is checked against `PricingRule` where the dictionary is built. The tests run five snippets through `mypy --strict`, using the member's own `_run` helper, and the output below is what that helper returns for each failing one. The valid registry exits 0 with no output. A function with the wrong return type:

```text
<string>:13: error: Dict entry 0 has incompatible type "str": "Callable[[Consignment], Decimal]"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
```

`per_kg` registered unbound, so that its extra required keyword-only parameter shows:

```text
<string>:9: error: Dict entry 0 has incompatible type "str": "def per_kg(consignment: Consignment, *, rate: Decimal) -> Money"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
```

A lambda whose body returns the wrong type draws a second error from inside the lambda:

```text
<string>:9: error: Dict entry 0 has incompatible type "str": "Callable[[Consignment], Decimal]"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
<string>:9: error: Incompatible return value type (got "Decimal", expected "Money")  [return-value]
```

And the class registered where an instance belongs:

```text
<string>:9: error: Dict entry 0 has incompatible type "str": "type[ZoneRate]"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
```

That last case is the failure from the opening, caught before any quote runs. The class `ZoneRate` is itself a callable that takes a tariff and returns a `ZoneRate`, so it doesn't fit a slot that takes a consignment and returns money. `test_mypy_checks_each_registry_entry` asserts the exit status, the exact set of error codes and the expected-type text for each case.

A configured rule is checked less well. `partial(per_kg, rat=Decimal("1.20"))` is rejected, and `test_mypy_checks_partial_keywords_but_not_a_missing_binding` asserts it:

```text
<string>:9: error: Unexpected keyword argument "rat" for "per_kg"; did you mean "rate"?  [call-arg]
<string>:9: note: "per_kg" defined in "strategy_callable.rules"
```

A `partial` that binds nothing is accepted where it is assigned to the typed `PricingRule` slot, as a registry entry is. The same test asserts exit 0 and empty output for `partial(per_kg)`, and `test_an_unbound_partial_fails_only_when_called` shows the runtime end of it: `TypeError`, "missing 1 required keyword-only argument: 'rate'". The check does apply when the partial is called directly. A snippet that returns `partial(per_kg)(c)` from a function reports `Missing named argument "rate" for "per_kg"  [call-arg]`. The gap is in the assignment, which is the one the chapter titled [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) documents. Read a registry's `partial` entries by eye.

When a rule needs keyword parameters, overloads or attributes the callable type can't express, the callback Protocol with a positional-only `/` is the form to use. The chapter titled [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers it.

## When a strategy has to be an object

The callable type promises one thing: a consignment goes in and money comes out. It doesn't promise that the same consignment gives the same money twice. `_make_loyalty_discount` in the test module is a closure that counts its calls and subtracts the count from 25.00:

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

`test_a_rule_with_hidden_state_is_not_reproducible` calls it twice on one consignment and gets 24.00 and then 23.00. mypy accepts it, because the signature fits the slot. A quote that records the key `"loyalty"` can no longer be reproduced from that key. State belongs in an argument or in a configuration that doesn't change, such as the frozen `Tariff` that `ZoneRate` holds.

A rule that has to do more than price, such as explain its price or validate a consignment before pricing, has several operations, and a callable type no longer describes it. That's the `RateCalculator` case in the chapter titled [Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}). The class is still optional there, because anything with the right methods satisfies a Protocol, but the Protocol becomes the contract.

## When not to use it

A single rule called from one place is a function, with no registry. A registry consulted with a literal key everywhere, `RATE_RULES["zone"](c)`, is a dispatch table in disguise and a plain call would read better. Rules that need different inputs are a signature problem, and no registry fixes it: a rule that wants the carrier as well as the consignment doesn't fit `PricingRule`, and the slot changes before any registry does. A rule object written where a function would do, with no configuration to hold and no value comparison to make, adds a class without adding anything an audit can use.

<blockquote class="ai-sidebar" markdown="1">

**Reviewing assistant-written strategies.** An assistant asked for "the Strategy pattern" may propose an abstract `PricingStrategy` with a subclass per rule and a factory, record `rule.__name__` in a quote, register a class where an instance belongs, or keep a running counter inside a rule. Check that each rule fills a `PricingRule` slot as a callable and that no hierarchy stands in for it, that the registry is read-only and an unknown key is raised as a domain error, that the quote records the key rather than an introspected name, that every `partial` binds what its rule needs, and that a rule's result depends only on its argument.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then from the example directory:

```bash
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
collecting ... collected 31 items

tests/test_behaviour_table.py::test_each_registered_rule_prices_the_behaviour_table[flat] PASSED [  3%]
tests/test_behaviour_table.py::test_each_registered_rule_prices_the_behaviour_table[per-kg] PASSED [  6%]
tests/test_behaviour_table.py::test_each_registered_rule_prices_the_behaviour_table[zone] PASSED [  9%]
tests/test_behaviour_table.py::test_a_class_per_strategy_passes_the_same_table[flat] PASSED [ 12%]
tests/test_behaviour_table.py::test_a_class_per_strategy_passes_the_same_table[per-kg] PASSED [ 16%]
tests/test_behaviour_table.py::test_a_class_per_strategy_passes_the_same_table[zone] PASSED [ 19%]
tests/test_behaviour_table.py::test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one PASSED [ 22%]
tests/test_configured.py::test_partials_and_rule_objects_have_no_name PASSED [ 25%]
tests/test_configured.py::test_a_partial_has_no_value_equality PASSED    [ 29%]
tests/test_configured.py::test_a_rule_object_compares_and_hashes_by_value PASSED [ 32%]
tests/test_configured.py::test_a_rule_with_hidden_state_is_not_reproducible PASSED [ 35%]
tests/test_configured.py::test_an_unbound_partial_fails_only_when_called PASSED [ 38%]
tests/test_rules.py::test_rules_round_half_up_to_cents[per-kg] PASSED    [ 41%]
tests/test_rules.py::test_rules_round_half_up_to_cents[zone] PASSED      [ 45%]
tests/test_rules.py::test_zone_rate_refuses_a_zone_without_a_tariff PASSED [ 48%]
tests/test_rules.py::test_a_rated_weight_must_be_positive_and_finite[0] PASSED [ 51%]
tests/test_rules.py::test_a_rated_weight_must_be_positive_and_finite[-1] PASSED [ 54%]
tests/test_rules.py::test_a_rated_weight_must_be_positive_and_finite[NaN] PASSED [ 58%]
tests/test_rules.py::test_a_rated_weight_must_be_positive_and_finite[Infinity] PASSED [ 61%]
tests/test_selection.py::test_a_quote_records_the_rule_that_priced_it[flat] PASSED [ 64%]
tests/test_selection.py::test_a_quote_records_the_rule_that_priced_it[per-kg] PASSED [ 67%]
tests/test_selection.py::test_a_quote_records_the_rule_that_priced_it[zone] PASSED [ 70%]
tests/test_selection.py::test_an_unknown_rule_name_is_a_rating_error PASSED [ 74%]
tests/test_selection.py::test_the_rule_registry_is_read_only PASSED      [ 77%]
tests/test_static.py::test_mypy_checks_each_registry_entry[valid] PASSED [ 80%]
tests/test_static.py::test_mypy_checks_each_registry_entry[wrong-return] PASSED [ 83%]
tests/test_static.py::test_mypy_checks_each_registry_entry[extra-parameter] PASSED [ 87%]
tests/test_static.py::test_mypy_checks_each_registry_entry[lambda-body] PASSED [ 90%]
tests/test_static.py::test_mypy_checks_each_registry_entry[class-not-instance] PASSED [ 93%]
tests/test_static.py::test_mypy_checks_partial_keywords_but_not_a_missing_binding[missing] PASSED [ 96%]
tests/test_static.py::test_mypy_checks_partial_keywords_but_not_a_missing_binding[misspelt] PASSED [100%]

============================== 31 passed in 3.09s ==============================
```

```text
Success: no issues found in 9 source files
```

The suite has 16 test functions and 31 cases. The proof method behind the experiments, deleting a check in a scratch copy and watching the named test fail, is described in the chapter titled [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: register the class.** In a scratch copy, replace `ZoneRate(TARIFF)` in `RATE_RULES` with `ZoneRate`. `uv run mypy --strict src tests` reports:

```text
src/strategy_callable/rules.py:54: error: Dict entry 2 has incompatible type "str": "type[ZoneRate]"; expected "str": "Callable[[Consignment], Money]"  [dict-item]
Found 1 error in 1 file (checked 9 source files)
```

`uv run pytest -q`, filtered with `grep -E '^(FAILED|[0-9]+ (passed|failed))'`, gives:

```text
FAILED tests/test_behaviour_table.py::test_each_registered_rule_prices_the_behaviour_table[zone]
FAILED tests/test_configured.py::test_partials_and_rule_objects_have_no_name
FAILED tests/test_rules.py::test_rules_round_half_up_to_cents[zone] - Asserti...
FAILED tests/test_selection.py::test_a_quote_records_the_rule_that_priced_it[flat]
FAILED tests/test_selection.py::test_a_quote_records_the_rule_that_priced_it[per-kg]
FAILED tests/test_selection.py::test_a_quote_records_the_rule_that_priced_it[zone]
6 failed, 25 passed in 3.13s
```

The class takes the consignment as its `tariff` field, so calling it builds a `ZoneRate` holding a consignment and returns that. Nothing raises, and the price is the wrong type. `test_each_registered_rule_prices_the_behaviour_table[zone]` fails on the comparison with `Money`. `test_partials_and_rule_objects_have_no_name` fails because asking the registered class for `__name__` no longer raises. The quote test fails in all three cases, because it also asserts the zone price. mypy has named the entry before any of them run. The rounding test fails on its zone case for the same reason.

**Experiment two: bind nothing.** Revert, then replace `partial(per_kg, rate=Decimal("1.20"))` with `partial(per_kg)`. `uv run mypy --strict src tests` reports `Success: no issues found in 9 source files`, and the same filtered pytest run gives:

```text
FAILED tests/test_behaviour_table.py::test_each_registered_rule_prices_the_behaviour_table[per-kg]
FAILED tests/test_rules.py::test_rules_round_half_up_to_cents[per-kg] - TypeE...
FAILED tests/test_selection.py::test_a_quote_records_the_rule_that_priced_it[per-kg]
3 failed, 28 passed in 3.19s
```

The checker passed the registry, and the failure shows up at call time, in the per-kilogram rows, as the `TypeError` that `test_an_unbound_partial_fails_only_when_called` predicts.

## For deeper coverage

Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software*, is the source for Strategy, and Luciano Ramalho's *Fluent Python*, second edition, the chapter "Design Patterns with First-Class Functions", is the treatment this chapter builds on. Both are on the [bibliography page]({{ '/bibliography/' | relative_url }}), where Brett Slatkin's *Effective Python*, third edition, is also listed for closures and `functools.partial`.

The language sources are the `functools` documentation on [partial objects](https://docs.python.org/3/library/functools.html), [PEP 695](https://peps.python.org/pep-0695/) for the `type` statement behind `PricingRule`, [PEP 814](https://peps.python.org/pep-0814/) for `frozendict`, and the [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) for `frozen` and the generated `__eq__` and `__hash__`.
