---
title: "SRP, OCP, and LSP in Python"
order: 5
layout: tutorial
sectionid: docs
part: "principles"
description: "Single responsibility, open-closed and Liskov substitution on one rate quote: three collaborators, a tax rule that arrives as data, and a contract suite for what mypy cannot see."
---

## Learning objectives

By the end of this chapter you can:

- Separate a rate calculation into pricing, tax and audit, and say which stakeholder's change touches which part.
- Add a destination tax rule as an entry in a mapping, without editing the code that quotes.
- State the Liskov substitution principle as a rule about contracts, and name the half of it that `mypy --strict` enforces and the half it cannot.
- Write one contract suite that each `RateCalculator` has to pass.
- Judge when a split, an extension point or a contract suite costs more than the change it prepares for.

## Why this matters

A rate quote has three owners. The carrier contract sets the tariff and changes when it's renegotiated. Tax law sets what a destination country adds, on its own calendar. Compliance decides what's recorded about a finished quote. When one function does all three, a tax change for one country is an edit to the function that prices every consignment, and the pricing tests have to be rerun and believed again.

The three principles are the old answers to that cost, and the force behind each is still there in Python. The mechanism changes: a `Protocol` instead of an interface hierarchy, a mapping of callables instead of a subclass per variant, and a contract suite for the part of Liskov that no signature expresses.

{% include excalidraw.html name="05-srp-ocp-lsp" described="true" caption="Figure 5.1: One quote, three responsibilities. Pricing sits behind the RateCalculator Protocol and hands its net to tax rules keyed by destination country; the finished quote goes to an audit callable. Each changes for its own reason, and one contract suite checks every calculator." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-05-srp-ocp-lsp" markdown="1">
The figure reads top to bottom. `quote`, the coordinator, takes one consignment and returns one `RateQuote`. It asks the `RateCalculator` (`BaseRate` or `FlatRate`; pricing changes with the tariff) for a net price, and passes that net to the rule from `TAX_RULES`, a percentage chosen by destination country (tax changes with tax law). The `RateQuote` holds the net from pricing and the tax computed on that net, and goes to the `AuditSink` callable (audit changes with compliance). The contract suite stands beside the calculator and checks every calculator, because pricing is the collaborator whose contract has clauses no signature states.
</div>
</details>

The coordinator calls pricing, then tax, then audit, and the contract suite checks pricing.

## Three reasons to change in one rate calculation

A single `price` function looks up the zone rate, multiplies by weight, adds destination tax and appends the result to an audit log. Then three requests arrive in one quarter:

| Request | From | Should change |
| --- | --- | --- |
| Move the Asia zone to a new per-kilogram rate | The carrier | Prices, not audit |
| Revise one country's tax rate | Tax law | Tax, not pricing |
| Record who requested each quote | Compliance | No number on the quote |

In one function, nothing in the signature shows that, and a reviewer reads the whole body to check it. Robert C. Martin states the single responsibility principle as "a class should have only one reason to change" in *Agile Software Development: Principles, Patterns, and Practices* (2002). A reason to change is a person or process that will ask for the edit. Three reasons mean three places. The principle separates the code, not the data flow, which still runs from pricing into tax.

## Single responsibility: three collaborators and a coordinator

Pricing sits behind a `Protocol`, because the quote needs a behaviour and doesn't care which class supplies it:

```python
class RateCalculator(Protocol):
    """Prices one consignment.

    Contract, which no type signature states:

    - accepts every consignment whose zone is in ``ZONES``;
    - returns ``Money`` in the tariff currency (EUR), non-negative, quantised to cents;
    - a heavier consignment in the same zone is never cheaper;
    - a zone outside ``ZONES`` raises ``RatingError``.
    """

    def price(self, consignment: Consignment, /) -> Money: ...
```

Tax and audit are narrower. A tax rule is `type TaxRule = Callable[[Money], Money]`, and an audit sink is `type AuditSink = Callable[[RateQuote], None]`. Neither carries state the caller manages, so neither needs a class. The coordinator is one function:

```python
def quote(
    consignment: Consignment,
    *,
    calculator: RateCalculator,
    tax_rules: Mapping[str, TaxRule],
    audit: AuditSink,
) -> RateQuote:
    """Price the consignment, tax it by destination country, audit once and return the quote."""
    country = consignment.destination[:2]
    try:
        rule = tax_rules[country]
    except KeyError:
        raise RatingError(f"no tax rule for destination country {country!r}") from None
    net = calculator.price(consignment)
    result = RateQuote(consignment.id, net, rule(net))
    audit(result)
    return result
```

Replace one collaborator at a time on an Asia consignment and compare the quotes:

| Replaced | Fields that change |
| --- | --- |
| The tariff | `net` and `tax` |
| The `"SG"` tax rule | `tax` |
| The audit sink | None; the new sink gets the quote and the old one doesn't |

The tariff row changes `tax` because tax is a percentage of the net: the change reaches tax through the data, and the tax code is untouched. The sink receives the same object `quote` returns, once. `BaseRate` and a `percent` rule run alone, with no sink and no rule table, and give exact amounts.

## Open for extension: a new tax rule is data

Bertrand Meyer introduced the open-closed principle in *Object-Oriented Software Construction* (first edition 1988), resting on inheritance: a module in use stays closed, and a new variant is a subclass. Martin's 2002 restatement rests on abstraction: a module depends on an abstract contract, and new behaviour arrives behind it. Either way, the aim is to take a change you've already seen, here a new destination, without reopening tested code.

In Python the extension point is often a callable in a mapping the caller passes in:

```python
def percent(rate: Decimal) -> TaxRule:
    """A rule that taxes a net amount at ``rate`` percent, rounded half up to cents."""

    def rule(net: Money) -> Money:
        tax = net.amount * rate / Decimal(100)
        return Money(tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), net.currency)

    return rule


# Illustrative rates for the example, not statutory ones.
TAX_RULES: Mapping[str, TaxRule] = MappingProxyType(
    {
        "SG": percent(Decimal("9")),
        "NL": percent(Decimal("21")),
    }
)
```

The rates are invented and say nothing about any country's law. `percent` is a closure that fixes a rate. `TAX_RULES` is a read-only view: `TAX_RULES["HK"] = exempt` raises `TypeError`, and mypy reports `[index]` on that line because `Mapping` has no `__setitem__`.

A new rule arrives as data. Passing `{**TAX_RULES, "HK": exempt}` to `quote`, where `exempt` returns zero, taxes a Hong Kong consignment at `0.00`, and `"HK"` is still absent from `TAX_RULES` afterwards. `quote` is unchanged and the shared default is untouched.

A destination with no entry raises `RatingError` naming the country, and nothing reaches the audit sink. Treating a missing rule as zero tax would quote cheaper than the law allows, silently. The mapping protects against the change you've seen, a new country. A change in what a rule needs to know, such as the shipper's status as well as the net, alters the `TaxRule` signature, and no mapping absorbs that.

## Liskov substitution: the contract the type does not state

Barbara Liskov introduced the idea in her OOPSLA '87 keynote, "Data Abstraction and Hierarchy" (*SIGPLAN Notices* 23(5), 1988). Liskov and Wing gave the behavioural definition in "A Behavioral Notion of Subtyping" (*ACM TOPLAS* 16(6), 1994): properties provable of the supertype's objects must hold for the subtype's. In practice, a subtype may accept more and promise more, never less.

Half of that is a type signature, and mypy checks it. A subclass of `BaseRate` whose `price` accepts only a subtype of `Consignment`:

```python
class SeaConsignment(Consignment):
    pass


class Narrowed(BaseRate):
    @override
    def price(self, consignment: SeaConsignment, /) -> Money:
        return Money(Decimal("0.00"), "EUR")
```

```text
<string>:15: error: Argument 1 of "price" is incompatible with supertype "srp_ocp_lsp.pricing.BaseRate"; supertype defines the argument type as "Consignment"  [override]
<string>:15: note: This violates the Liskov substitution principle
<string>:15: note: See https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
```

A narrowed parameter is a stronger precondition: a caller holding a `BaseRate` may pass any `Consignment`. The other cases under `mypy --strict`:

| Override | mypy |
| --- | --- |
| Return widened to `Money \| None` (weaker postcondition) | `[override]`, `Return type "Money \| None" of "price" incompatible with return type "Money" in supertype`; no Liskov note |
| Method spelled `prcie` under `@override` | `[misc]`, `Method "prcie" is marked as an override, but no base method was found with this name` |
| Argument widened to `Consignment \| None` (weaker precondition) | Accepted, no output |

`@override`, from PEP 698, turns a silent new method into an error. A Protocol moves the check to the place of use: a class with `price(...) -> Decimal`, not declared a `RateCalculator`, is accepted until it's passed as `calculator=` to `quote`, where mypy reports `[arg-type]` under `Following member(s) of "DecimalRate" have conflicts`.

The other half is behaviour. A calculator that refuses a zone the contract accepts, or prices in dollars, has the right types. The contract suite checks the docstring: every zone at 0.5 kg and at 1200 kg, EUR, non-negative, quantised to cents, heavier never cheaper, and a zone outside `ZONES` raising `RatingError`. Three negative fixtures break it. One strengthens a precondition:

```python
class AsiaOnlyRate(BaseRate):
    """Negative fixture: strengthens the precondition by rejecting zones the contract accepts."""

    def price(self, consignment: Consignment, /) -> Money:
        if consignment.zone != "ASIA":
            raise RatingError(f"only ASIA is served, got {consignment.zone!r}")
        return super().price(consignment)
```

| Fixture | Breaks | mypy | Contract suite |
| --- | --- | --- | --- |
| `AsiaOnlyRate` | Precondition strengthened | Exit 0, no output | `rejected zone EU` |
| `DollarRate`, returning `Money(Decimal("10.00"), "USD")` | Postcondition weakened | Exit 0, no output | `priced in USD` |
| `AnyZoneRate`, pricing `POLAR` at zero | Accepts a zone it should reject | Not run | `accepted zone POLAR that the contract rejects` |

The suite also runs against `BaseRate` and `FlatRate`, and a new calculator joins it with one more entry in the parametrize list.

## Where Python changes how the principles apply

- **Structural typing.** `FlatRate` subclasses nothing and satisfies `RateCalculator` by having the right `price`. That removes the hierarchy, not the contract: a class that matches by shape still has to keep the docstring's promises, so the contract suite takes any `RateCalculator`, not any `BaseRate`. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) develops shape against promise.
- **The narrowest abstraction is a callable.** Tax and audit have one operation and no shared state, so a lambda, a closure, a bound method such as `records.append` or a `functools.partial` fits. Pricing has a contract with several clauses, so it keeps a named `Protocol`.
- **The extension point is data.** A dict of callables replaces a subclass-per-variant hierarchy.

## When the principle costs more than it buys

- **A tax rule that never varies doesn't need a mapping.** Shipping to one country at a constant rate, a function that multiplies by it is the right size; the table is indirection for readers and tests.
- **Split on a request you've received.** Pulling audit out of `price` before a second reason to change exists adds a parameter and a name for one caller.
- **A contract suite pays off with two implementations.** With one calculator, the contract is a docstring and its own tests. With two, a shared suite is the only place the second is held to the first's promises.

> **🤖 Explore with your agent**
>
> "Split `quote` into pricing, tax and audit. Pricing is a `RateCalculator` Protocol, tax a `TaxRule` looked up by destination country in a read-only mapping, audit an `AuditSink` callable. Add no Protocol or base class without a second implementation. An override may accept more and promise more, never less. Write one parametrised contract test that every `RateCalculator` must pass."
>
> If an override narrows `price`, ask for the contract case it fails.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/05-srp-ocp-lsp
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 19 cases pass, and mypy reports no issues in 10 source files. Make each experiment in a scratch copy:

- **Price in dollars.** Make `FlatRate.price` return `Money(Decimal("10.00"), "USD")`. mypy stays clean, because the signature is unchanged. pytest reports `1 failed, 18 passed`: the `FlatRate` contract case fails with `AssertionError: priced in USD, contract requires EUR`, and `BaseRate` stays green.
- **Accept `None`.** Widen `FlatRate.price` to take `Consignment | None` and raise `RatingError` on `None`. mypy and pytest both stay green: a weaker precondition is allowed, and the contract suite never passes `None`.

## What you can do now

- Separate pricing, tax and audit behind `RateCalculator`, `TaxRule` and `AuditSink`, coordinated by one `quote`, and say which change moves which field.
- Add a destination tax rule as data, with `{**TAX_RULES, "HK": exempt}` passed to an unchanged `quote`.
- State Liskov as a contract: mypy enforces the `[override]` half, and `AsiaOnlyRate` and `DollarRate` pass it while breaking the other half.
- Write one contract suite that every `RateCalculator` runs, and watch it catch a `FlatRate` that prices in dollars.
- Judge the cost: a one-country table and a one-calculator suite are indirection without a second case to pay for it.

## For deeper coverage

Martin's *Agile Software Development: Principles, Patterns, and Practices* is the source for the single responsibility formulation and for the restatement of open-closed on abstraction. Meyer's *Object-Oriented Software Construction*, second edition, is the book where open-closed and Design by Contract are developed; the contract vocabulary of preconditions and postconditions comes from that tradition. *Python Object-Oriented Programming* by Steven F. Lott and Dusty Phillips (fifth edition) treats inheritance and composition in Python, and the books are listed on the [bibliography page]({{ '/bibliography/' | relative_url }}).

The behavioural definition of substitution is in Liskov and Wing, "A Behavioral Notion of Subtyping", *ACM Transactions on Programming Languages and Systems* 16(6), 1994, and the original statement is in Liskov's OOPSLA '87 keynote, "Data Abstraction and Hierarchy". The Python references are [PEP 544](https://peps.python.org/pep-0544/) on Protocols, [PEP 698](https://peps.python.org/pep-0698/) on `typing.override`, the typing specification's chapter on protocols, and the mypy documentation on [incompatible overrides](https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides). [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) picks up how the collaborators reach the coordinator.
