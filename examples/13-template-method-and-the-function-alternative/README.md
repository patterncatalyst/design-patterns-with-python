# Template Method and the function alternative

Customs declarations that vary by destination, written once as a function that takes hooks and
once as an abstract class for a family of destinations that share state. Each test witnesses a
claim about what the structure of the Template Method pattern becomes in Python, which part of it
dissolves into a function, and which part survives as inheritance. The chapter's thesis is that the
pattern straddles the line: the hook structure dissolves, and the class form survives where a
family of variants shares state and code across steps.

## What it witnesses

The function form.

- `declare_customs` runs fixed steps in a fixed order: refuse a consignment without commodities,
  classify each commodity, total the declared value in one currency, assess duty, then put the
  commercial invoice first and the extra documents after it. No hook can remove or reorder them.
- `classify` and `duty` are required hooks with no default, so leaving one out is a `TypeError` at
  construction and `[call-arg]` under mypy. `extra_documents` defaults to `no_extra_documents`.
  A hook with the wrong signature is `[arg-type]`.
- Lookups and duty rates that are missing raise `CustomsError`, with the `KeyError` suppressed.
  Duty rounds half up to the cent.

Defaults in a Protocol.

- A default body in a Protocol reaches an explicit subclass. A class that matches structurally does
  not inherit it and fails with `AttributeError`, and mypy reports `[assignment]` with a note that
  names the missing member.

The class form.

- `CustomsDeclarer` holds a classification and a schedule, shares the `classify` and `duty` steps,
  declares `extra_documents` abstract and marks `declare` as `@final`. Its `declare` hands its own
  bound methods to `declare_customs`, so the skeleton exists once.
- The class form and the function form give the same declaration. `NetherlandsDeclarer` and
  `GermanyDeclarer` share the schedule and the lines and differ in their documents. A declarer
  without its documents cannot be built.

Keeping the skeleton fixed.

- A template whose invariant lives in an overridable step issues a declaration with no lines when a
  subclass skips the base step, and mypy accepts it.
- `typing.final` on `declare`: the runtime runs an override and only sets `__final__`, while mypy
  reports `[misc]` on the override.

## Layout

- `src/template_method/domain.py`: `ConsignmentId`, `Money`, `Commodity`, `Consignment`,
  `DeclarationLine`, `CustomsDeclaration`, `CustomsError`.
- `src/template_method/hooks.py`: `Classifier`, `DutyRule`, `DocumentRule`, `CustomsHooks`,
  `no_extra_documents`, `lookup_tariff_code`, `schedule_duty`, `declare_customs`, `SINGAPORE`,
  `NETHERLANDS`, `EU_CLASSIFICATION`, `EU_SCHEDULE`. Tariff codes and duty rates are illustrative.
- `src/template_method/declarer.py`: `CustomsDeclarer`, `NetherlandsDeclarer`, `GermanyDeclarer`.

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

`tests/test_hooks.py`

- `test_declare_customs_runs_its_steps_in_order`: recording hooks see classify per commodity, then duty, then extra documents.
- `test_a_hook_left_out_takes_its_default`: `SINGAPORE` has no extra documents, so only the invoice is listed.
- `test_a_declaration_needs_at_least_one_commodity`: both forms refuse an empty consignment.
- `test_a_declaration_in_two_currencies_is_refused`: both forms raise `CustomsError` naming both currencies.
- `test_the_commercial_invoice_is_always_first`: the invoice leads the document list in both forms.
- `test_a_required_hook_cannot_be_left_out`: `TypeError` naming `classify`, with a typed ignore for mypy.
- `test_an_unclassified_commodity_is_refused`: `CustomsError`, with the `KeyError` suppressed.
- `test_duty_rounds_half_up_to_cents`: a half-cent case where half-even differs.
- `test_a_tariff_code_without_a_duty_rate_is_refused`: `CustomsError`, with the `KeyError` suppressed.
- `test_a_declaration_lists_a_line_per_commodity_and_totals_them`: lines, country, declared value and duty.
- `test_every_value_in_the_model_is_frozen`: every dataclass in the model refuses attribute assignment.

`tests/test_template.py`

- `test_the_template_and_the_hooks_give_the_same_declaration`: equal declarations from both forms.
- `test_a_declarer_without_its_documents_cannot_be_built`: `TypeError` naming the abstract method.
- `test_final_marks_the_template_without_enforcing_it`: `__final__` is set and an override runs.
- `test_a_subclass_that_skips_the_base_check_declares_nothing`: a declaration with no lines from the open template, and a refusal from the final one.
- `test_two_destinations_share_the_schedule_and_differ_in_documents`: equal duty and lines, different documents.

`tests/test_protocol_defaults.py`

- `test_protocol_defaults_reach_only_explicit_subclasses`: the explicit subclass gets the default, the structural class raises `AttributeError`.

`tests/test_static.py`

- `test_mypy_rejects_overriding_the_final_template`: `[misc]` on an override of `declare`.
- `test_mypy_accepts_an_override_that_skips_the_base_step`: clean.
- `test_mypy_checks_hooks_at_construction`: `[call-arg]` for a missing required hook, `[arg-type]` for a wrong signature.
- `test_mypy_requires_every_protocol_member_for_a_structural_match`: `[assignment]` naming the missing member.

Classes named with a leading underscore in the test modules are test fixtures and aren't part of
the model code.
