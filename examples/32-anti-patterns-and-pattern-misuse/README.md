# Anti-patterns and pattern misuse

An anti-pattern here is a pattern's structure kept after its forces have gone. The rating function
`quote(consignment, tariff)` is the lesson. It is priced against a class-per-role engine on one
shared table of quotes, and the structure is measured with `ast` and `sys.setprofile`, because
neither mypy nor ruff reports proportion. Zones, fees and rates are illustrative.

## What it witnesses

The rating function and its overbuilt twin.

- `quote` looks up the flat fee for a zone, adds the fuel fee and adds tax rounded to the cent. An
  unknown zone raises `RatingError` with the `KeyError` suppressed.
- `rating_form` is `function` or `engine`. The conftest `_RateEngine` is built from
  `_PricingStrategyFactory`, `_PricingStrategy`, `_FlatFeeStrategy`, `_Charge`, `_FlatFeeCharge`,
  `_FuelSurcharge`, `_ChargeVisitor` and `_NetTotalVisitor`, with a `get_tariff` getter. Both forms
  quote `EU` 35.70 and `ASIA` 78.05 and refuse `POLAR` the same way.

What the structure costs.

- `ast` counts classes, functions and the lines of `ast.unparse` output without docstrings: 0, 1 and
  8 for `quote`, against 9, 17 and 57 for the nine engine classes in conftest.
- The fuel surcharge is one definition of the function (`quote`) and five of the engine, found by
  reading each definition's own name and statements.
- One quote enters one Python function in the function form and eleven in the engine, counted with
  `sys.setprofile` and filtered by file, so generated dataclass `__init__` methods and the test's own
  frames are left out.
- A new charge kind whose `accept` calls an undeclared visit method fails at run time with
  `AttributeError`. Declaring the method abstract on the visitor base makes the concrete visitor
  uninstantiable. mypy reports both (reduced model).
- mypy `--strict` and ruff pass the function and the engine alike. `bash scripts/verify.sh` runs both
  over the conftest engine.

Getters and setters, and a service locator.

- `_AccessorConsignment` compares by identity, and `set_zone` changes the quote of a consignment that
  was already quoted. The frozen `Consignment` compares by value and refuses assignment.
- `_LocatedRateEngine` constructs with nothing registered and fails with `KeyError` at its first
  quote. It quotes once `_ServiceLocator` holds a tariff. mypy needs an `isinstance` check to use
  what the locator returns, doesn't see a missing registration, and reports a missing `tariff`
  argument to `quote` as `[call-arg]`.

The mypy snippets that restate a shape (the locator and the visitor) are reduced models. They don't
import the engine.

## Layout

- `src/pattern_misuse/rating.py`: `ConsignmentId`, `Money`, `Consignment`, `Tariff`, `RateQuote`,
  `RatingError`, `STANDARD_TARIFF`, `quote`.
- `tests/conftest.py`: the engine, the new-charge-kind extensions, `_AccessorConsignment`,
  `_ServiceLocator`, `_LocatedRateEngine` and the fixtures. They are the over-built subjects and
  never part of `src`.

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

`tests/test_forms.py`

- `test_every_rating_form_quotes_the_same_table`: `rating_form` and the `EU` and `ASIA` rows.
- `test_every_rating_form_refuses_an_unknown_zone`: both forms, context suppressed.

`tests/test_measure.py`

- `test_the_engine_needs_more_classes_functions_and_lines_than_the_function`: exact `ast` counts.
- `test_the_fuel_surcharge_lives_in_one_definition_of_the_function`: `["quote"]` against five engine
  definitions.
- `test_one_engine_quote_makes_more_python_calls_than_the_function`: the ordered call names.
- `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`: `AttributeError`.
- `test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract`: `TypeError`.

`tests/test_misuse.py`

- `test_an_accessor_consignment_has_no_value_equality`: identity against value.
- `test_a_setter_lets_a_quoted_consignment_change_its_quote`: `35.70` then `78.05`.
- `test_a_frozen_consignment_refuses_assignment`: `FrozenInstanceError`.
- `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`: `KeyError`.
- `test_a_located_engine_quotes_once_its_tariff_is_registered`: equals `quote`.

`tests/test_static.py`

- `test_mypy_needs_a_type_check_to_use_a_located_service`: `[attr-defined]` and `[no-any-return]`
  (reduced model).
- `test_mypy_does_not_see_a_missing_registration`: exit 0, and `KeyError` at run time (reduced
  model).
- `test_mypy_reports_a_missing_tariff_argument`: `[call-arg]`.
- `test_mypy_reports_a_visitor_missing_a_new_visit_method`: `[abstract]` and `[attr-defined]`
  (reduced model).

Classes and functions named with a leading underscore in the tests are fixtures and aren't part of
the model code.
