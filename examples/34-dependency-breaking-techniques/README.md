# Dependency-breaking techniques

A rating engine inherited without tests, changed one technique at a time, with one
characterisation table run against every step. `RateEngine.quote` asks two carrier SDKs for a
price and adds a margin. The SDKs are stand-ins that do no I/O and raise `CarrierTimeoutError`
where a connection would time out, so a test that reaches one fails. Zones, weights and prices
are illustrative.

## What it witnesses

The legacy engine in `legacy.py` is kept as found, and each step is a complete module that
applies one technique to the module before it.

- `parameterised.py` (Parameterize Constructor): `RateEngine` takes `fastline_quote`,
  `airco_price` and `margin` as keyword parameters. The defaults are the real SDK calls, so
  existing callers do not change, and a test that forgets a fake reaches the real SDK.
  `AircoPrice` is a callback Protocol because the SDK takes keyword-only arguments.
- `wrapped.py` (wrap the API): `airco_quote` converts kilograms to truncated grams and cents to
  euros, so both carriers fit `CarrierQuoter` and the engine holds them as a mapping.
- `rating.py` (the class becomes a function): `quote(consignment, /, *, quoters, margin=MARGIN)`
  takes its carriers as a required mapping. `STANDARD_QUOTERS` is a read-only `frozendict` and
  `quote_standard = partial(quote, quoters=STANDARD_QUOTERS)` is the binding at the root.

The diff between neighbouring modules is the technique:

- `legacy.py` to `parameterised.py`: the two SDK calls move behind constructor parameters.
- `parameterised.py` to `wrapped.py`: the AIRCO call moves behind `airco_quote`, and the two
  fields become one mapping.
- `wrapped.py` to `rating.py`: the class and its fields become a function and an argument.

The table `CHARACTERISATION_ROWS` pins five behaviours: the cheaper carrier wins, a tie goes to
AIRCO, the margin is rounded half up, grams are truncated, and a carrier timeout fails the whole
quote. The `step` fixture in `tests/conftest.py` runs it against five forms of the engine: the
legacy engine (the one place a patch appears), constructor keywords, the wrapped carriers, the
function, and subclass and override, which is the comparison form. Two altered engines show the
table can fail: grams rounded fail only the grams row, and a half-even margin fails only the
rounding row.

What mypy checks (version 2.4.1, `--strict`).

- A fake of the wrong shape passed to the `airco_price` parameter is `[arg-type]`.
- A missing `quoters` is `[call-arg]`.
- A misspelt override is reported as `[misc]` only when the method carries `@override`
  (reduced model).

## Layout

- `src/dependency_breaking/domain.py`: `ConsignmentId`, `Consignment`, `Money`, `RateQuote`,
  `CarrierTimeoutError`.
- `src/dependency_breaking/fastline.py`, `airco.py`: the stand-in SDKs.
- `src/dependency_breaking/legacy.py`, `parameterised.py`, `wrapped.py`, `rating.py`: the
  engine and its three steps.
- `tests/conftest.py`: the `step` fixture, the subclass form and the two altered engines.

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

`tests/test_characterisation.py`

- `test_every_step_matches_the_characterisation_table`: five forms, five rows.
- `test_every_step_lets_a_carrier_timeout_fail_the_quote`: five forms.
- `test_the_table_catches_a_step_that_changes_behaviour`: the failing row ids of each altered
  engine.

`tests/test_steps.py`

- `test_the_legacy_engine_needs_a_patch_to_reach_a_fake`
- `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`
- `test_airco_quote_converts_kilograms_and_cents`
- `test_the_function_form_needs_its_quoters`
- `test_standard_quoters_name_both_carriers`
- `test_quote_standard_binds_the_standard_quoters`
- `test_a_misspelt_override_falls_through_to_the_real_carrier`

`tests/test_static.py`

- `test_mypy_checks_a_fake_passed_as_a_constructor_argument`
- `test_mypy_reports_a_missing_quoters_argument`
- `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator`: reduced model.

A patch appears only in the legacy branch of the `step` fixture, because the legacy engine takes
no parameters. It never appears in `src`.
