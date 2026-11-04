# SRP, OCP and LSP

One rate quote, thirteen test functions. Each test witnesses a claim about the single-responsibility,
open-closed and Liskov substitution principles in modern Python. The tax rates are illustrative
values for the example and are not statutory rates.

## What it witnesses

Single responsibility: pricing, tax and audit change for different reasons.

- `quote` coordinates three collaborators: a `RateCalculator` for pricing, a mapping of
  `TaxRule` callables for destination tax, and an `AuditSink` callable.
- Replacing the tariff moves the net price and the tax that follows from it, replacing a tax
  rule moves only the tax, and replacing the sink moves neither.
- Pricing and tax run on their own, with no sink and no rules built.

Open-closed: a new tax rule is data.

- A rule for a new destination country is a callable added to a mapping passed to `quote`.
- The default table `TAX_RULES` is read-only, and a missing rule is a `RatingError` and never a
  silent zero tax.

Liskov substitution: the contract the type does not state.

- One contract helper checks every `RateCalculator`: all zones accepted, EUR, non-negative,
  quantised to cents, heavier never cheaper, an unknown zone rejected.
- `mypy --strict` rejects an override that narrows the argument to a subtype, widens a return type or
  misspells a method marked `@override`, and accepts one that widens an argument.
- On a `Protocol`, mypy checks conformance where the object is used.
- A subclass that rejects zones the base accepts, or a structural class that prices in USD,
  passes mypy and fails the contract.

## Layout

- `src/srp_ocp_lsp/domain.py`: value types (`Consignment`, `Money`, `Weight`, `RateQuote`,
  `Tariff`) and `RatingError`.
- `src/srp_ocp_lsp/pricing.py`: the `RateCalculator` protocol and its contract, `BaseRate`,
  `FlatRate`, `TARIFF`, `FLAT_BY_ZONE`, `ZONES`.
- `src/srp_ocp_lsp/tax.py`: `TaxRule`, `percent`, `TAX_RULES`.
- `src/srp_ocp_lsp/audit.py`: `AuditSink`.
- `src/srp_ocp_lsp/rating.py`: `quote`.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

## What the tests verify

`tests/test_srp.py`

- `test_each_change_moves_only_the_fields_it_feeds`: replacing the tariff changes `net` and the `tax`
  computed from it, replacing a tax rule changes only `tax`, and replacing the sink changes no
  field and redirects the audit record.
- `test_audit_receives_exactly_the_quote_returned`: the sink holds one record, the same object
  `quote` returned.
- `test_pricing_and_tax_run_alone`: `BaseRate` and `percent` give exact amounts with no sink or
  rule table.

`tests/test_ocp.py`

- `test_a_new_tax_rule_is_added_without_editing_quote`: an exempt rule added to a copy of the
  table taxes a Hong Kong consignment at zero, and the default table is untouched.
- `test_default_tax_table_is_read_only`: assigning to `TAX_RULES` raises `TypeError`.
- `test_missing_tax_rule_is_a_rating_error`: a destination without a rule raises `RatingError`
  naming the country, and nothing is audited.

`tests/test_lsp.py`

- `test_calculator_honours_the_rate_contract`: `BaseRate` and `FlatRate` both pass the contract.
- `test_contract_catches_a_strengthened_precondition`: a subclass that serves only one zone fails
  with `rejected zone EU`.
- `test_contract_catches_a_weakened_postcondition`: a structural class that prices in USD fails
  with `priced in USD`.
- `test_mypy_rejects_an_incompatible_override`: a narrowed argument gives `[override]` with the
  substitution note, a widened return gives `[override]`, and a misspelled `@override` gives
  `[misc]`.
- `test_mypy_accepts_an_override_that_widens_the_argument`: accepting `Consignment | None` is
  clean.
- `test_mypy_checks_a_structural_calculator_where_it_is_used`: a class whose `price` returns
  `Decimal` fails with `[arg-type]` at the call to `quote`.
- `test_mypy_cannot_see_a_behavioural_violation`: the two contract violators pass `mypy --strict`
  with no output.

The two violators are negative fixtures in the test module and are not part of the model code.
