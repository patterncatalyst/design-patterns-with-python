# Strategy: the callable

Rate quotes priced by a flat rule, a per-kilogram rule and a zone rule, written as callables in a
read-only registry. Each test witnesses a claim about what the structure of the Strategy pattern
becomes in Python, what a quote can record about the rule that priced it, and what mypy checks in
a strategy slot. The chapter's thesis is that Strategy's force survives while its structure
dissolves into a callable type, a mapping and a call.

## What it witnesses

Selection by name.

- `RATE_RULES` is a `Mapping[str, PricingRule]` over a 3.15 `frozendict`: it isn't a `dict` and
  item assignment raises.
- `quote` records the key it was given. An unknown key is a `RatingError`, not a bare `KeyError`.

Configured rules.

- A function, a `partial` and a frozen dataclass with `__call__` all fill the `PricingRule` slot.
- A `partial` and a rule object have no `__name__`, so a quote that introspects the name fails on
  the first configured rule. A `partial` has no value equality. A rule object compares, hashes and
  prints by value.
- Both configured rules round half up to the cent, in cases where half-even rounding differs.
- A rule that counts its own calls prices the same consignment differently the second time.

The class-per-strategy comparison.

- A test fixture holds an abstract `_PricingStrategy` with three subclasses and a registry. It
  runs the same behaviour table as the registry of callables, and an `ast` count reports four
  strategy classes against one.

What mypy checks.

- Each registry entry is checked against `PricingRule`: the return type, an extra required
  parameter, a lambda's body and a class registered where an instance belongs.
- A `partial` with a misspelt keyword is rejected. A `partial` that binds nothing is accepted and
  fails when it's called.

## Layout

- `src/strategy_callable/domain.py`: `ConsignmentId`, `Weight`, `Money`, `Consignment`,
  `RateQuote`, `RatingError`.
- `src/strategy_callable/rules.py`: `PricingRule`, `flat_rate`, `per_kg`, `Tariff`, `ZoneRate`,
  `TARIFF`, `RATE_RULES`, `quote`. Tariff rates are illustrative.

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

`tests/test_behaviour_table.py`

- `test_each_registered_rule_prices_the_behaviour_table`: the flat, per-kg and zone rules each price one row of the shared table.
- `test_a_class_per_strategy_passes_the_same_table`: the fixture classes price the same rows.
- `test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one`: an `ast` count of classes defining `__call__` or `price`.

`tests/test_rules.py`

- `test_rules_round_half_up_to_cents`: per-kg and zone cases that sit on a half cent, where half-even differs.
- `test_zone_rate_refuses_a_zone_without_a_tariff`: an unknown zone is a `RatingError`.
- `test_a_rated_weight_must_be_positive_and_finite`: zero, negative, NaN and infinite weights raise `ValueError`.

`tests/test_selection.py`

- `test_a_quote_records_the_rule_that_priced_it`: the quote carries the key, the consignment id and the price.
- `test_an_unknown_rule_name_is_a_rating_error`: `RatingError` naming the rule, with the `KeyError` suppressed.
- `test_the_rule_registry_is_read_only`: item assignment raises and the registry isn't a `dict`.

`tests/test_configured.py`

- `test_partials_and_rule_objects_have_no_name`: `AttributeError` for the `partial` and the rule object, a name for the function.
- `test_a_partial_has_no_value_equality`: two equal partials compare unequal, while `func` and `keywords` match.
- `test_a_rule_object_compares_and_hashes_by_value`: equal, same hash, stable repr.
- `test_a_rule_with_hidden_state_is_not_reproducible`: the second call prices differently.
- `test_an_unbound_partial_fails_only_when_called`: `TypeError` naming `rate`.

`tests/test_static.py`

- `test_mypy_checks_each_registry_entry`: clean for a valid registry, `[dict-item]` for four bad entries.
- `test_mypy_checks_partial_keywords_but_not_a_missing_binding`: clean for a partial binding nothing, `[call-arg]` for a misspelt keyword.

Classes named with a leading underscore in the test modules are test fixtures and aren't part of
the model code.
