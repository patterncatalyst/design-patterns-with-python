---
layout: example
order: 5
title: "SRP, OCP and LSP: three reasons to change, one contract"
description: One rate quote whose tests show three reasons to change kept apart, a tax rule added as data, and a contract suite for what no type states.
github_path: examples/05-srp-ocp-lsp
card_eyebrow: "Principles: SOLID · SRP, OCP, LSP"
card_title: "Separate reasons to change, a tax rule as data, and a contract suite"
card_blurb: "A rate quote split into pricing, tax and audit, extended with a new tax rule as data, and checked by a contract suite that catches the substitution failures mypy can't see."
---

One rate quote witnesses three of the SOLID principles. Each test asserts the behaviour named
in its title. The tax rates are illustrative and aren't statutory rates.

## Single responsibility

`quote` coordinates three collaborators that change for different reasons: a
`RateCalculator` for pricing, a mapping of `TaxRule` callables for destination tax, and an
`AuditSink` callable. Replacing one moves only the output it owns, and pricing and tax run
without the others.

## Open-closed

A new tax rule is a callable added to a mapping passed to `quote`, and `quote` isn't edited.
The default `TAX_RULES` table is read-only, and a destination without a rule is a
`RatingError`.

## Liskov substitution

- One contract helper checks every `RateCalculator`: all zones accepted, EUR, non-negative,
  quantised to cents, heavier never cheaper, unknown zone rejected.
- `mypy --strict` rejects an override that narrows the argument to a subtype and one that widens the return, flags a misspelled
  `@override`, accepts a widened argument, and checks a structural calculator where it is used.
- A subclass that rejects zones the base accepts, and a class that prices in USD, pass mypy and
  fail the contract.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/05-srp-ocp-lsp
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
