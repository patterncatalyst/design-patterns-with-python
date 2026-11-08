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

A rate quote has three owners. The carrier contract sets the tariff, and it changes when the contract is renegotiated. Tax law sets what a destination country adds, on its own calendar. Compliance decides what must be recorded about a finished quote. When one function does all three, a change to the tax rate for one country is a change to the function that prices every consignment, and the pricing tests have to be rerun and believed again. The cost is the review and the retest that follow an edit in a place that had no reason to change.

The three principles in this chapter are the old answers to that cost, and the force behind each is still present in modern Python. What changes is the mechanism: a `Protocol` instead of an interface hierarchy, a mapping of callables instead of a subclass per variant, and a contract suite for the part of the Liskov principle that no signature can express. The example is one rate quote, and its fourteen test functions, nineteen cases in all, witness each claim below.

{% include excalidraw.html name="05-srp-ocp-lsp" caption="Figure 5.1: One quote, three responsibilities. Pricing sits behind the RateCalculator Protocol and hands its net to tax rules keyed by destination country; the finished quote goes to an audit callable. Each changes for its own reason, and one contract suite checks every calculator." %}

The figure reads top to bottom. The coordinator asks the calculator for a net price, passes that net to the tax rule chosen by the destination country, builds the quote and hands it to the audit callable. The contract suite stands beside the calculator because pricing is the collaborator whose contract has clauses no signature states.

## Three reasons to change in one rate calculation

Picture a single `price` function that looks up the zone rate, multiplies by weight, adds destination tax and appends the result to an audit log. It's short and it works. Then three requests arrive in the same quarter. The carrier moves the Asia zone to a new per-kilogram rate. A destination country revises its tax rate. Compliance asks that every quote also record who requested it.

Each request has a different author and a different test that ought to move. The tariff change should alter prices and nothing about audit. The tax change should alter tax and nothing about pricing. The audit change should alter no number on the quote. In the single function, a reader can't see that from the signature, and a reviewer has to read the whole body to check it.

This is the situation the single responsibility principle describes. Robert C. Martin states it as "a class should have only one reason to change" in *Agile Software Development: Principles, Patterns, and Practices* (2002). A reason to change is a person or a process that will ask for the edit. Pricing, tax and audit have three, so the code that serves them belongs in three places. The principle separates the reasons to change in the code. It doesn't say the data flows separately, and in this example it doesn't, as the next section shows.

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

Tax and audit are narrower still. A tax rule is a callable from a net amount to a tax amount, `type TaxRule = Callable[[Money], Money]`, and an audit sink is a callable from a finished quote to nothing, `type AuditSink = Callable[[RateQuote], None]`. Neither needs a class, because neither carries state the caller has to manage. The coordinator is one function over the three:

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

The witness is `test_each_change_moves_only_the_fields_it_feeds`. It quotes an Asia consignment as a baseline, replaces one collaborator at a time and compares the fields of the two `RateQuote` values. Replacing the tariff changes `net` and `tax`. Replacing the `"SG"` tax rule changes `tax` alone. Replacing the audit sink changes no field, and the new sink receives the quote while the old one does not. The first row looks like a violation until you recall that tax is a percentage of the net: a new tariff reaches the tax through the data. The code that computes the tax is untouched. The test states the expected set for each case, so a collaborator that started reaching into another's output would fail it.

Two more tests check the edges of the split. `test_audit_receives_exactly_the_quote_returned` checks that the sink gets the same object `quote` returns, once. `test_pricing_and_tax_run_alone` builds a `BaseRate` and a `percent` rule with no sink and no rule table, and checks exact amounts: pricing and tax can be exercised without constructing the rest.

## Open for extension: a new tax rule is data

Bertrand Meyer introduced the open-closed principle in *Object-Oriented Software Construction*, whose first edition appeared in 1988. His version rested on inheritance: a module stays closed once it is in use, and a new variant is a subclass that extends it. Martin's restatement, collected in his 2002 book, rests on abstraction instead, so that a module depends on an abstract contract and new behaviour arrives behind it. In both, the aim is to take a change you have already seen, a new destination in this case, without reopening code that is tested and in service.

In Python the extension point is often a callable in a mapping that the caller passes in. The rule constructor and the default table are short:

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

The rates are invented for the example and say nothing about any country's law. `percent` is a closure that fixes a rate, and `TAX_RULES` is a read-only view over a dict, so no module can add to it by assignment. `test_default_tax_table_is_read_only` asserts that `TAX_RULES["HK"] = exempt` raises `TypeError`. The assertion line needs one `# type: ignore[index]`, because `Mapping` has no `__setitem__`, so mypy reports `[index]` on the line.

A new rule arrives as data. `test_a_new_tax_rule_is_added_without_editing_quote` passes `{**TAX_RULES, "HK": exempt}` to `quote`, where `exempt` is a function defined in the test module that returns zero. A Hong Kong consignment is taxed at `0.00`, and afterwards `"HK"` is still not in `TAX_RULES`. The new rule lives in the caller's mapping, `quote` is unchanged, and the shared default is untouched.

The failure mode is the missing rule. A destination with no entry is a `RatingError` naming the country, and `test_missing_tax_rule_is_a_rating_error` checks that nothing reaches the audit sink. The alternative, treating a missing rule as zero tax, would quote a consignment cheaper than the law allows and say nothing. A mapping of rules has a limit: it protects against the change you have seen, a new country. A change in what a rule needs to know, such as the shipper's status as well as the net, isn't a data change: it alters the `TaxRule` signature, which no mapping absorbs.

## Liskov substitution: the contract the type does not state

Barbara Liskov introduced the idea in her OOPSLA '87 keynote, "Data Abstraction and Hierarchy", published in *SIGPLAN Notices* 23(5) in 1988. Liskov and Wing gave the behavioural definition in "A Behavioral Notion of Subtyping" (*ACM TOPLAS* 16(6), 1994): properties that can be proved of the supertype's objects have to hold for the subtype's objects. Martin's 2002 book lists it among the principles of object-oriented design. In practice, a subtype may accept more than its supertype and promise more, and it may not accept less or promise less.

Half of that rule is a type signature, and mypy checks it. Each snippet below is a string in `tests/test_lsp.py`, run through `mypy --strict` with the package importable, and the output is as the run printed it. A subtype of `Consignment`, and a subclass of `BaseRate` whose `price` accepts only that subtype:

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

mypy names the principle, because a narrowed parameter, one that accepts only a subtype, is a stronger precondition: a caller holding a `BaseRate` may pass any `Consignment`. Widening the return type to `Money | None` gives `[override]` with `Return type "Money | None" of "price" incompatible with return type "Money" in supertype`. That is a weaker postcondition, and mypy prints the Liskov note only for argument errors, not for return types. Spelling the method `prcie` under `@override` gives `[misc]`: `Method "prcie" is marked as an override, but no base method was found with this name`. `@override`, from PEP 698, turns a silent new method into an error. The opposite direction is accepted: a `price` that takes `Consignment | None` passes `mypy --strict` with no output, which is the weaker precondition that the rule allows.

A Protocol moves the check to the place of use. A class with `price(...) -> Decimal` that is not declared a `RateCalculator` is accepted until it is passed as `calculator=` to `quote`, where mypy reports `[arg-type]` with the expected and actual signatures under `Following member(s) of "DecimalRate" have conflicts`.

The other half is behaviour, and no signature carries it. A calculator that refuses a zone the contract accepts, or that prices in dollars, has the right types. The contract helper in the test module checks the docstring above: every zone at 0.5 kg and at 1200 kg, EUR, non-negative, quantised to cents, the heavier consignment never cheaper, and a zone outside `ZONES` raising `RatingError`. Three negative fixtures live in the test module and aren't model code. One strengthens a precondition:

```python
class AsiaOnlyRate(BaseRate):
    """Negative fixture: strengthens the precondition by rejecting zones the contract accepts."""

    def price(self, consignment: Consignment, /) -> Money:
        if consignment.zone != "ASIA":
            raise RatingError(f"only ASIA is served, got {consignment.zone!r}")
        return super().price(consignment)
```

The second, `DollarRate`, is a structural class that returns `Money(Decimal("10.00"), "USD")` and so weakens a postcondition. `test_mypy_cannot_see_a_behavioural_violation` passes copies of both to `quote` and gets exit status 0 with empty output. The contract suite is what fails: `rejected zone EU` for the first, `priced in USD` for the second. A third, `AnyZoneRate`, prices `POLAR` at zero instead of raising, and fails with `accepted zone POLAR that the contract rejects`. The suite runs against `BaseRate` and `FlatRate` as well, and a calculator added later joins it with one more entry in the parametrize list.

## Where Python changes how the principles apply

The forces are the ones the principles name. Three Python features change how much structure it takes to honour them.

Structural typing means a substitutable implementation doesn't need to inherit. `FlatRate` isn't a subclass of anything and satisfies `RateCalculator` by having the right `price`. That removes the requirement to build a hierarchy, and it leaves the contract in place: a class that matches by shape still has to keep the promises in the docstring, which is why the contract suite takes any `RateCalculator` and not any `BaseRate`. The shape-versus-promise distinction is developed in [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}).

The narrowest abstraction is a callable. Tax and audit have one operation each and no state to share, so `type` aliases over `Callable` express them, and a lambda, a closure, a bound method such as `records.append` or a `functools.partial` all fit. Pricing has a contract with several clauses, so it keeps a named `Protocol`.

The extension point is data. A dict of callables replaces what a subclass-per-variant hierarchy would have needed.

## When the principle costs more than it buys

A tax rule that never varies doesn't need a mapping. If the book shipped to one country and the rate were a constant, a function that multiplies by it would be the right size, and the table would be indirection that a reader has to learn and the tests have to cover. The same goes for the split itself: pulling audit out of `price` before a second reason to change exists adds a parameter and a name for a single caller. The test for a split is a request you have actually received that would touch two things at once.

A contract suite pays off when two implementations exist. With one calculator, the contract is a docstring and the calculator's own tests. With two, the suite is the only place where the second is held to the first's promises.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a split.** "Split the rate calculation" leaves open how many Protocols it needs, where the tax rules live and what an override may accept. Paste a prompt that states the form:

> Split `quote` into pricing, tax and audit. Pricing is a `RateCalculator` Protocol, tax a `TaxRule` looked up by destination country in a read-only mapping, audit an `AuditSink` callable. Add no Protocol or base class without a second implementation. An override may accept more and promise more, never less. Write one parametrised contract test that every `RateCalculator` must pass.

If an override narrows `price`, ask for the contract case it fails.
</blockquote>

## Build, run, observe

From the repository root, run the one-time sync, then work from the example directory:

```bash
uv sync --locked --all-packages
cd examples/05-srp-ocp-lsp
uv run pytest -v --no-header
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
collecting ... collected 19 items

tests/test_lsp.py::test_calculator_honours_the_rate_contract[BaseRate] PASSED [  5%]
tests/test_lsp.py::test_calculator_honours_the_rate_contract[FlatRate] PASSED [ 10%]
tests/test_lsp.py::test_contract_catches_a_strengthened_precondition PASSED [ 15%]
tests/test_lsp.py::test_contract_catches_a_weakened_postcondition PASSED [ 21%]
tests/test_lsp.py::test_contract_catches_an_accepted_unknown_zone PASSED [ 26%]
tests/test_lsp.py::test_mypy_rejects_an_incompatible_override[narrowed-argument] PASSED [ 31%]
tests/test_lsp.py::test_mypy_rejects_an_incompatible_override[widened-return] PASSED [ 36%]
tests/test_lsp.py::test_mypy_rejects_an_incompatible_override[misspelled-override] PASSED [ 42%]
tests/test_lsp.py::test_mypy_accepts_an_override_that_widens_the_argument PASSED [ 47%]
tests/test_lsp.py::test_mypy_checks_a_structural_calculator_where_it_is_used PASSED [ 52%]
tests/test_lsp.py::test_mypy_cannot_see_a_behavioural_violation PASSED   [ 57%]
tests/test_ocp.py::test_a_new_tax_rule_is_added_without_editing_quote PASSED [ 63%]
tests/test_ocp.py::test_default_tax_table_is_read_only PASSED            [ 68%]
tests/test_ocp.py::test_missing_tax_rule_is_a_rating_error PASSED        [ 73%]
tests/test_srp.py::test_each_change_moves_only_the_fields_it_feeds[tariff] PASSED [ 78%]
tests/test_srp.py::test_each_change_moves_only_the_fields_it_feeds[tax-rule] PASSED [ 84%]
tests/test_srp.py::test_each_change_moves_only_the_fields_it_feeds[audit-sink] PASSED [ 89%]
tests/test_srp.py::test_audit_receives_exactly_the_quote_returned PASSED [ 94%]
tests/test_srp.py::test_pricing_and_tax_run_alone PASSED                 [100%]

============================== 19 passed in 2.73s ==============================
```

```text
Success: no issues found in 10 source files
```

Two experiments, each made in a scratch copy of the example and reverted afterwards.

First, make `FlatRate.price` return `Money(Decimal("10.00"), "USD")` in place of the zone lookup. `mypy --strict src tests` still prints `Success: no issues found in 10 source files`, because the signature is unchanged. `uv run pytest` reports `1 failed, 18 passed`. The failing test is `tests/test_lsp.py::test_calculator_honours_the_rate_contract[FlatRate]`, with `AssertionError: priced in USD, contract requires EUR`. The type checker passed a calculator that breaks the contract, and the suite caught it in one parametrised case while `BaseRate` stayed green.

Second, widen `FlatRate.price` to take `Consignment | None` and raise `RatingError` on `None`. mypy and pytest both stay green: `Success: no issues found in 10 source files` and `19 passed`. A weaker precondition is allowed, and nothing in the contract suite objects, because it never passes `None`.

## What you can do now

- Separate pricing, tax and audit: `RateCalculator`, `TaxRule` and `AuditSink` sit behind one `quote`, and `test_each_change_moves_only_the_fields_it_feeds` shows which change touches which part.
- Add a destination tax rule as data: `{**TAX_RULES, "HK": exempt}` goes to `quote`, and `test_a_new_tax_rule_is_added_without_editing_quote` shows `quote` unchanged.
- State Liskov as a contract: mypy enforces the `[override]` half, and `test_mypy_cannot_see_a_behavioural_violation` shows the half it can't.
- Write one contract suite: the same helper runs against every `RateCalculator`, and experiment one shows it catching a `FlatRate` that prices in dollars.
- Judge the cost: a one-country table and a one-calculator suite are indirection without a second case to pay for it.

## For deeper coverage

Martin's *Agile Software Development: Principles, Patterns, and Practices* is the source for the single responsibility formulation and for the restatement of open-closed on abstraction. Meyer's *Object-Oriented Software Construction*, second edition, is the book where open-closed and Design by Contract are developed; the contract vocabulary of preconditions and postconditions in this chapter comes from that tradition. *Python Object-Oriented Programming* by Steven F. Lott and Dusty Phillips (fifth edition) treats inheritance and composition in Python, and the book list is on the [bibliography page]({{ '/bibliography/' | relative_url }}).

The behavioural definition of substitution is in Liskov and Wing, "A Behavioral Notion of Subtyping", *ACM Transactions on Programming Languages and Systems* 16(6), 1994, and the original statement is in Liskov's OOPSLA '87 keynote, "Data Abstraction and Hierarchy". The Python references are [PEP 544](https://peps.python.org/pep-0544/) on Protocols, [PEP 698](https://peps.python.org/pep-0698/) on `typing.override`, the typing specification's chapter on protocols, and the mypy documentation on [incompatible overrides](https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides). The next chapter, [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}), picks up how the collaborators reach the coordinator.
