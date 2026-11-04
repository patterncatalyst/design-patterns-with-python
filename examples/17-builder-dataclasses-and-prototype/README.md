# Builder, dataclasses, and Prototype

A booking request with twelve fields, four of them required, built three ways and copied from
templates. The chapter's thesis is that Builder and Prototype dissolve: a keyword-only frozen
dataclass names every argument and validates once, and `replace` copies with changes. Port codes,
documents and weights are illustrative.

## What it witnesses

Builder.

- `BookingRequest` is a frozen, slotted, keyword-only dataclass. Its `__post_init__` raises
  `BookingError` for equal ports, an insured booking without a declared value, and dangerous goods
  without the note in `documents`.
- Two comparison fixtures sit in `tests/conftest.py`: a twelve-argument positional constructor and a
  fluent builder. They run the same four-case booking table as the dataclass, with the same checks,
  so the comparison is measured. They are not part of the model code.
- The positional constructor accepts a swapped origin and destination, and mypy reports only swaps
  across types. The dataclass call is checked for `Literal` values, missing fields and misspelt
  keywords. The builder with a step left out is accepted by mypy and fails when `build` runs.

Prototype.

- `TEMPLATES` is a read-only `frozendict` of requests, and `from_template` copies one with
  `dataclasses.replace`. An unknown name is a `BookingError`.
- `replace` and `copy.replace` rerun the cross-field checks, and mypy checks `copy.replace` keywords
  and types like `dataclasses.replace`.
- `copy.copy` and `replace` share a list field, `copy.deepcopy` separates it, and a tuple field
  removes the question. mypy is silent about the sharing.

## Layout

- `src/builder_prototype/domain.py`: `ConsignmentId`, `Weight`, `Money`, `BookingError`.
- `src/builder_prototype/booking.py`: `CarrierCode`, `ServiceLevel`, `BookingRequest`.
- `src/builder_prototype/templates.py`: `TEMPLATES`, `from_template`.

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

`tests/test_builder.py`

- `test_a_positional_constructor_accepts_a_swapped_origin_and_destination`: nothing is raised.
- `test_both_constructors_pass_the_booking_table`: keyword, positional and builder forms on four cases.
- `test_the_request_has_twelve_fields_and_four_are_required`: required fields, defaults and `kw_only`.
- `test_a_builder_with_a_step_left_out_fails_only_at_build`: a plain `ValueError` naming the step.
- `test_a_booking_request_and_a_weight_are_frozen`: assignment is refused on both.
- `test_a_booking_request_has_no_instance_dict`: the request is slotted.
- `test_a_requested_weight_must_be_positive_and_finite`: zero, negative and NaN.

`tests/test_prototype.py`

- `test_a_template_and_replace_give_a_new_request`: a new id and weight, the template unchanged.
- `test_replace_reruns_the_cross_field_checks`: `replace` and `copy.replace`.
- `test_a_deep_copy_separates_the_documents_list`: the template keeps its list.
- `test_a_shallow_copy_shares_the_documents_list`: `copy.copy` and `replace`.
- `test_a_tuple_field_makes_the_template_safe_to_share`: a longer tuple leaves the template alone.
- `test_copy_replace_works_on_dataclasses_and_refuses_a_plain_class`: a `TypeError` for the class.
- `test_an_unknown_template_is_a_booking_error`: the original `KeyError` is suppressed.
- `test_the_template_registry_is_read_only`: item assignment raises `TypeError`.

`tests/test_static.py`

- `test_mypy_cannot_see_two_same_typed_arguments_swapped`: ports, carrier and service, and flags.
- `test_mypy_reports_swapped_arguments_of_different_types`: `[arg-type]` on a reduced model.
- `test_mypy_checks_literal_fields_and_keyword_names`: `[arg-type]` and two `[call-arg]` results.
- `test_mypy_accepts_a_builder_with_a_step_left_out`: clean on a reduced model.
- `test_mypy_checks_copy_replace_like_dataclasses_replace`: keyword name, type and plain class.
- `test_mypy_cannot_see_a_shallow_copy_sharing_a_list`: clean.

Classes named with a leading underscore in the test modules are test fixtures and aren't part of
the model code. The snippets for the positional constructor and the builder in `test_static.py` are
reduced models of the fixtures in `conftest.py`.
