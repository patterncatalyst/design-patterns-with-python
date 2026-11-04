# The data model

One small shipping model, twenty-two test functions. Each test witnesses a claim about how
Python's special methods let a type join the language's own protocols: equality and hashing,
arithmetic, ordering, containers and text.

## What it witnesses

Equality and hashing: equal values must hash equal.

- Operators and builtins look a special method up on the type, so an instance attribute named
  `__len__` is ignored.
- Defining `__eq__` alone sets `__hash__` to `None`, and the class stops being a set element.
- `Dimensions` treats a carton stowed on another face as the same carton: equality and hash both
  use the sorted extents, and equality returns `NotImplemented` for any other type.
- A frozen dataclass with a custom `__eq__` and no `__hash__` keeps a hash over its fields, so
  equal cartons land in two set elements. mypy says nothing.

Arithmetic and reflected operands: `NotImplemented` hands the operation to the other side.

- `Money + Money` works within one currency and raises `ValueError` across currencies.
- `Decimal("2") * price` and `2 * price` reach `Money.__rmul__`; foreign operands raise
  `TypeError`; `sum()` needs a `Money` start value.
- mypy checks operand types because the parameters are annotated with the class.

Ordering: `functools.total_ordering` derives the other comparisons from `__lt__`.

- `<=`, `>` and `>=` come from one method, and `Money` refuses to order across currencies.
- With `__lt__` alone, `>` works by reflection and `<=` raises `TypeError`.
- Quotes sort by `total`, not by themselves.

Containers and text:

- `TrackingHistory` defines `__len__` and `__iter__`; truthiness and `in` follow from them. An
  iterable without `__len__` is truthy when empty, and an iterable is not subscriptable.
- `repr`, `str` and `format` serve different readers, and a class with `__str__` alone rejects a
  format spec.

## Layout

- `src/data_model/cargo.py`: `Weight`, `Dimensions`.
- `src/data_model/money.py`: `ConsignmentId`, `Money`, `RateQuote`.
- `src/data_model/tracking.py`: `HandlingKind`, `HandlingEvent`, `TrackingHistory`.

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

`tests/test_equality.py`

- `test_special_methods_are_looked_up_on_the_type`: `len()` on an instance with a `__len__`
  attribute raises `TypeError` matching `has no len`.
- `test_equal_weights_are_one_set_element`: equal `Weight` values form one set element, and a
  class without `__eq__` gives two.
- `test_defining_eq_alone_makes_a_class_unhashable`: `__hash__` is `None` and a set raises
  `TypeError` matching `unhashable type`.
- `test_a_turned_carton_is_one_set_element`: a turned carton is equal, hashes equal and keeps its
  declared order in `repr`; a tuple is unequal and `__eq__` returns `NotImplemented`.
- `test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash`: equal cartons form a set of two.
- `test_dimensions_reject_a_non_positive_extent`: a zero extent raises `ValueError`.
- `test_weight_rejects_a_value_that_is_not_finite_and_positive`: zero, negative, infinite and NaN
  weights raise `ValueError`.

`tests/test_arithmetic.py`

- `test_money_adds_within_one_currency_only`: the sum is exact, a currency mismatch raises
  `ValueError`, and `price + 1` and `1 + price` raise `TypeError`.
- `test_a_factor_times_money_uses_the_reflected_method`: `Decimal` and `int` factors on the left
  work, a float factor raises `TypeError`, and the product is quantised to cents.
- `test_money_multiplication_rounds_half_up`: a half cent rounds up.
- `test_sum_needs_a_money_start`: `sum(..., start=...)` is exact and bare `sum()` raises
  `TypeError`.

`tests/test_ordering.py`

- `test_total_ordering_derives_the_other_comparisons`: `<=`, `>` and `>=` exist on `Money`; with
  `__lt__` alone `>` works and `<=` raises `TypeError`.
- `test_money_refuses_to_order_across_currencies`: `<` and `<=` raise `ValueError`, and comparing
  with an `int` raises `TypeError`.
- `test_quotes_sort_by_total_but_not_by_themselves`: sorting by `total` orders the quotes and
  sorting the quotes raises `TypeError`.

`tests/test_containers.py`

- `test_history_is_sized_and_reiterable`: length, repeated iteration and membership.
- `test_empty_history_is_falsy_through_len`: an empty history is falsy with no `__bool__`, and an
  iterable without `__len__` is truthy.
- `test_history_is_not_subscriptable`: indexing raises `TypeError`.

`tests/test_text.py`

- `test_repr_str_and_format_serve_different_readers`: the three forms differ, and a class with
  `__str__` alone raises `TypeError` for a format spec.

`tests/test_static.py`

- `test_mypy_rejects_an_eq_that_narrows_its_argument`: `[override]` with the substitution note.
- `test_mypy_rejects_operands_the_methods_do_not_accept`: four `[operator]` errors.
- `test_mypy_accepts_the_protocols_the_types_define`: the supported operations are clean, and
  sorting an unordered `Money` by key gives `[arg-type]` and `[return-value]`.
- `test_mypy_cannot_see_a_broken_hash_contract`: the equal-but-unequal-hash carton passes
  `mypy --strict` with no output.

The `_`-prefixed classes in the test modules are negative fixtures and are not part of the model
code.
