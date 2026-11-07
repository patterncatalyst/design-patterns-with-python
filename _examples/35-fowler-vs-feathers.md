---
layout: example
order: 35
title: "Fowler vs Feathers, contrasted and combined"
description: A rating engine refactored under golden quotes recorded from the inherited code, beside tests written from the requirement that pass a refactor that changes 18 of 120 totals.
github_path: examples/35-fowler-vs-feathers
card_eyebrow: "Changing inherited code · Fowler and Feathers"
card_blurb: "Five rows written from the requirement pass a tidy-up that changes totals. Quotes recorded from the legacy engine list the rows it changed."
card_title: "Intent rows and golden quotes"
---

One shipping domain witnesses the argument. A rating engine asks two carriers for a price, takes
the cheaper and adds a margin. Both carrier SDKs are stand-ins that do no I/O, and the tests pass
plain functions in their place.

## Tests written from the requirement

Five rows say what the engine should do: the cheaper carrier wins each way, a tie goes to AIRCO,
the margin is applied to a round price and grams are truncated. They pass the inherited engine, the refactored engine
and two refactors that change a total. A carrier timeout fails the quote.

## Golden quotes

A generated grid of 120 consignments, two zones and 0.5 kg to 30 kg, is quoted by the inherited
engine and recorded in a JSON file. A test ties the file to the engine, and the refactored engine
must match it. A failure is an ordered list of the rows that moved, because pytest prints the
differing keys of a dict comparison in set order under pytest 9.2.0.

## Two refactors that change totals

Rounding each carrier price when it becomes `Money` moves 18 of the 120 totals. Replacing the
half-up quantise with `round(amount, 2)` moves two, because the default decimal context rounds
half to even. The golden quotes list both sets exactly.

## Regenerating the file

`uv run pytest --update-golden` rewrites the file from the inherited engine and skips the test.
Without the option nothing is written.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/35-fowler-vs-feathers
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
