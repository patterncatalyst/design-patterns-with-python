# Refactor or rewrite

A legacy rating engine, a rewrite of it, and a router that moves zones across one at a time. All
weights, zones and prices are illustrative.

## What it witnesses

`legacy.py` prices a consignment by weight band in an `if`/`elif` chain. Each band includes its
upper limit (5, 20 and 50 kg), and every zone other than ASIA is priced with the EU prices, so an
unknown zone such as AFRICA gets a quote. Both are kept as found.

`rating.py` is the rewrite. A frozen `Tariff` holds the limits and the prices, and `quote` finds
the band with `bisect_left`, which keeps each limit inclusive. It refuses an unknown zone with
`RatingError`.

`strangler.py` holds `Router`, a frozen dataclass that takes the legacy engine, the rewrite, the
migrated zones and an optional `report` callback. A migrated zone is served by the rewrite. Any
other zone is served by the legacy engine, and when `report` is set the rewrite also runs on it and
a difference, or a `RatingError`, is passed to `report` as a `Mismatch`. The shadow result is never
served. `quote_routed` is the router bound at the module root, migrating ASIA only. It routes calls
and converts no interface, so it is not the Adapter pattern.

`PARITY_ROWS` in `tests/test_parity.py` puts weights on every limit (5, 20 and 50 kg), just above 5
and 50 kg, and above the last band, for EU and ASIA, plus one AFRICA row. `ACCEPTED_DIFFERENCES` lists the row where the
rewrite is meant to differ. The first draft of the rewrite, `_exclusive_limits_quote` in
`tests/conftest.py`, uses `bisect_right`, so a weight equal to a limit no longer
lands in the band that limit closes.

A parity failure is a list of row ids in table order.

## Layout

- `src/refactor_or_rewrite/domain.py`: `ConsignmentId`, `Weight`, `Consignment`, `Money`,
  `RateQuote`, `RatingError`, `MARGIN`.
- `src/refactor_or_rewrite/legacy.py`: `RateEngine`.
- `src/refactor_or_rewrite/rating.py`: `Tariff`, `STANDARD_TARIFF`, `quote`.
- `src/refactor_or_rewrite/strangler.py`: `RateQuoter`, `Mismatch`, `Router`, `MIGRATED_ZONES`,
  `quote_routed`.
- `tests/conftest.py`: the first draft, an engine that must not be called, a consignment builder.

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

`tests/test_parity.py`

- `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted`: the mismatched rows
  equal `ACCEPTED_DIFFERENCES`.
- `test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries`: the exact seven
  ids.
- `test_the_legacy_engine_prices_an_unknown_zone_as_eu`
- `test_the_rewrite_refuses_an_unknown_zone`
- `test_band_limits_include_the_boundary_weight`: the legacy engine and the rewrite.
- `test_the_rewrite_prices_from_the_tariff_it_is_given_and_rounds_half_up`: a one-band tariff
  whose margin lands on a half cent.
- `test_a_weight_must_be_positive_and_finite`: zero, a negative, `NaN` and `Infinity`.

`tests/test_strangler.py`

- `test_the_router_serves_migrated_zones_from_the_rewrite`
- `test_the_router_serves_other_zones_from_the_legacy_engine`
- `test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote`
- `test_shadow_mode_reports_a_refusal_as_a_mismatch`
- `test_shadow_mode_is_silent_when_the_engines_agree`
- `test_with_every_zone_migrated_the_legacy_engine_is_never_called`
- `test_the_standard_router_migrates_asia_only`

`tests/test_static.py`

- `test_mypy_requires_the_rewrite_to_take_a_consignment`: a rewrite that takes a zone and a
  weight is an `arg-type` error at `Router`, and `quote` is accepted.

The tests use no mocks and no patching. Each engine's quote depends only on its arguments: the consignment, and for the rewrite the
tariff, which defaults to `STANDARD_TARIFF`. The router's tests pass plain functions.
