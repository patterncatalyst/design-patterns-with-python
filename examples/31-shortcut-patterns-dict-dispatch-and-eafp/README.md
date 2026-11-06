# Shortcut patterns: dict dispatch, function tables, and EAFP

An if-chain that picks behaviour by a value dissolves into a read-only table of callables. What
remains to design is totality, which mypy does not check, where the `try` goes, and how shared state
is read. A document issuer table and a duty-rate cache witness all three. HS codes and rates are
illustrative.

## What it witnesses

A table of callables.

- `ISSUERS` is a `frozendict` typed `Mapping[DocumentKind, DocumentIssuer]`. It gives `BL-CN-1`,
  `MF-CN-1` and `CD-CN-1`, refuses assignment, and is not a `dict`. `issue` takes another table by
  keyword.
- `issue` puts only the lookup inside `try`. A missing kind raises `UnsupportedDocumentError` with
  the `KeyError` suppressed. An issuer's own `KeyError` passes through, and a test-local form with
  the call inside the `try` reports it as an unsupported kind.
- `parse_kind` reads a kind from its text value and raises `UnsupportedDocumentError` for anything
  else.
- mypy checks an entry's signature (`[dict-item]`), a lookup's key type (`[index]`), assignment
  (`[index]`) and the `None` from `.get` (`[misc]`). It accepts a table that misses a kind, so a test
  walks `DocumentKind`. It accepts an if-chain whose `else` raises, and reports a missing arm in a
  `match` with `assert_never` and in a chain with no `else` (reduced models).
- `singledispatch` dispatches on type, so every member of `DocumentKind` reaches one implementation.
- ruff reports `SIM116` for a chain over string literals and nothing for a chain over enum members.

Asking forgiveness.

- `declaration_from` reads the required fields of a `CustomsDeclaration` with `try`/`except KeyError`,
  names the missing one in a `CustomsError`, and reads the optional `origin` with `get`.
- `DutyRateCache` takes its storage as a `MutableMapping`. `rate_for` reads once and reloads on a
  `KeyError`. `evict` uses `pop(hs_code, None)`.
- `cache_form` is `eafp` or `lbyl`. The conftest `_LookFirstDutyRateCache` passes the same table of
  hit, miss and evicted reads.
- `_HandoverRates` parks the first read on a `threading.Barrier` so another thread evicts in between.
  The look-first form raises `KeyError: '0901.21'` and the EAFP form reloads. Two EAFP readers that
  both miss both load. No test sleeps or reads a clock.
- A `getattr` default and `hasattr` hide an `AttributeError` raised inside a property.
  `contextlib.suppress` ends its block at the first exception.

Cost is benchmark-only. `bench/lookup_cost.py` prints nanoseconds per call for the EAFP, look-first
and `get` forms on a present and an absent key, and the chapter quotes a recorded run with its Python
version and date.

The reduced-model snippets in `test_static.py` (the `match`, the chains and the string and enum
literals) restate a shape and do not import the model.

## Layout

- `src/shortcut_patterns/documents.py`: `ConsignmentId`, `DocumentKind`, `UnsupportedDocumentError`,
  `DocumentIssuer`, `issue_bill_of_lading`, `issue_manifest`, `issue_customs_declaration`, `ISSUERS`,
  `issue`, `parse_kind`.
- `src/shortcut_patterns/declarations.py`: `CustomsError`, `CustomsDeclaration`, `declaration_from`.
- `src/shortcut_patterns/duties.py`: `DutyRateCache`, `duty_for`.
- `bench/lookup_cost.py`: the `timeit` comparison. Pytest does not collect it.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests bench
uv run python -I bench/lookup_cost.py
```

## What the tests verify

`tests/test_dispatch.py`

- `test_every_document_kind_has_an_issuer`: the names of kinds missing from `ISSUERS` are `[]`.
- `test_issue_gives_each_kind_its_reference`: three kinds.
- `test_an_unsupported_kind_raises_unsupported_document_error`: the message, and the context is
  suppressed.
- `test_the_issuer_table_is_read_only`: `TypeError`, and it is not a `dict`.
- `test_an_issuers_own_key_error_passes_through_issue`: `KeyError`.
- `test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind`: the comparison form.
- `test_a_table_passed_by_the_caller_replaces_the_default`: and the default is unchanged.
- `test_an_if_chain_whose_else_raises_misses_a_new_kind`: `ValueError` for the new kind.
- `test_singledispatch_sends_every_document_kind_to_one_implementation`: three equal results and a
  registry of `DocumentKind` and `object`.
- `test_parse_kind_reads_a_document_kind_from_its_value`: three kinds.
- `test_parse_kind_refuses_an_unknown_value`: the message, and the context is suppressed.

`tests/test_eafp.py`

- `test_every_cache_form_reads_loads_and_evicts_the_same_way`: `cache_form` and the hit, miss and
  evicted rows, each read twice, with the loader's recorded codes.
- `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`: `KeyError:
  '0901.21'` and no load.
- `test_an_eafp_read_reloads_when_another_thread_evicts_first`: the reloaded rate and one load.
- `test_two_eafp_readers_that_both_miss_both_load`: two loads of the same code.
- `test_evicting_an_absent_code_is_not_an_error`: both forms.
- `test_declaration_from_reads_required_fields_and_an_optional_origin`: with and without `origin`.
- `test_a_missing_required_field_names_the_field`: three fields, context suppressed.
- `test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property`: the default,
  `hasattr` and the direct access.
- `test_suppress_skips_the_rest_of_its_block_after_the_first_exception`: the second `del` never runs.
- `test_duty_for_applies_the_cached_rate_to_the_declared_value`: `7.50`.

`tests/test_static.py`

- `test_mypy_checks_an_issuers_signature_in_the_table`: `[dict-item]`.
- `test_mypy_checks_the_key_type_of_a_table_lookup`: `[index]`.
- `test_mypy_accepts_a_table_that_misses_a_kind`: exit 0, and `UnsupportedDocumentError` at run time.
- `test_mypy_reports_a_missing_arm_in_a_match_and_an_if_chain_without_else`: `[arg-type]` and
  `[return]` (reduced model).
- `test_mypy_accepts_an_if_chain_whose_else_raises`: exit 0, and `ValueError` at run time (reduced
  model).
- `test_mypy_refuses_assignment_into_the_issuer_table`: `[index]`.
- `test_mypy_requires_a_branch_after_dict_get`: `[misc]`.
- `test_ruff_flags_an_if_chain_over_literals_but_not_over_enum_members`: `SIM116` and none.
- `test_ruff_suggests_get_suppress_and_plain_membership`: `SIM105`, `SIM118` and `SIM401`.

Classes and functions named with a leading underscore in the tests are fixtures and are not part of
the model code.
