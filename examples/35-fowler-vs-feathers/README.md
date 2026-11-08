# Fowler vs Feathers, contrasted and combined

The same rating engine under two kinds of test. `RateEngine.quote` asks two carriers for a price,
takes the cheaper and adds a margin. The two carrier SDKs are stand-ins that do no I/O and raise
`CarrierTimeoutError`, and tests pass plain functions in their place. Zones, weights and prices are
illustrative.

## What it witnesses

`legacy.py` is the engine as inherited: its constructor already takes `fastline_quote`,
`airco_price` and `margin` as keyword parameters, and its only tests are five rows written from the
requirement. `refactored.py` is the same engine after three catalogue refactorings.

- Extract Function: `_cheapest` and `_with_margin` hold the choice and the margin.
- Replace Primitive with Object: carrier prices are `Money` at full precision, and only the total
  is rounded, once, half up. `CENT` names the quantum.

Two more refactors live in `tests/conftest.py` as altered engines. They change totals that the golden quotes record.

- `_CentFirstRateEngine` rounds each carrier price to the cent when it becomes `Money`.
- `_RoundBuiltinRateEngine` replaces the half-up quantise with `round(amount, 2)`.

The five intent rows in `INTENT_ROWS` pass the legacy engine, the refactored engine and both
altered engines. The golden file `tests/golden/rate_quotes.json` records what the legacy engine
quotes for 120 consignments (two zones, 0.5 kg to 30 kg in 0.5 kg steps). The refactored engine
matches it. The cent-first engine disagrees on 18 rows, and the `round` engine on `EU-30` and
`ASIA-30`. A failure is a list of `"<row>: golden <quote>, now <quote>"` lines in grid order,
because pytest 9.2.0 prints the differing keys of a dict comparison in set order, which changes
between runs.

Five rows are also written inline in `INLINE_GOLDEN`, so a reviewer can read them without opening
the file.

## Regenerating the golden file

```bash
uv run pytest --update-golden
```

The option is registered in `tests/conftest.py`. With it, the provenance test rewrites the file
from the legacy engine (sorted keys, two-space indent, trailing newline) and skips. Without it,
nothing is written. The diff is the review: regenerate only for a deliberate change to the legacy
quotes, and never in the same change as a refactor.

## Layout

- `src/fowler_feathers/domain.py`: `ConsignmentId`, `Consignment`, `Money`, `RateQuote`,
  `CarrierTimeoutError`.
- `src/fowler_feathers/fastline.py`, `airco.py`: the stand-in SDKs.
- `src/fowler_feathers/legacy.py`: `MARGIN`, `FastlineQuote`, `AircoPrice`, `RateEngine`.
- `src/fowler_feathers/refactored.py`: `CENT` and the refactored `RateEngine`.
- `tests/conftest.py`: `--update-golden`, the two rate cards, the altered engines, the
  `engine_forms` and `rate_cards` fixtures.
- `tests/golden/rate_quotes.json`: the recorded quotes.

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

`tests/test_intent.py`

- `test_the_intent_rows_pass_every_engine_and_both_rounding_refactors`: four forms, five rows (the fifth pins that grams are truncated).
- `test_every_engine_lets_a_carrier_timeout_fail_the_quote`: the legacy and refactored engines.

`tests/test_golden.py`

- `test_the_golden_file_records_the_legacy_engine`: the file equals the legacy engine's quotes;
  with `--update-golden` it writes the file and skips.
- `test_the_refactored_engine_matches_the_golden_quotes`
- `test_inline_golden_values_pin_the_rows_a_reviewer_reads`: the legacy and refactored engines.
- `test_the_golden_quotes_catch_a_refactor_that_changes_rounding`: the exact 18 rows, then
  `EU-30` and `ASIA-30`.
- `test_round_with_two_digits_rounds_half_to_even_in_the_default_context`
- `test_the_golden_writer_sorts_and_indents`

The tests use no mocks and no patching, and nothing in `src` reads or writes JSON.
