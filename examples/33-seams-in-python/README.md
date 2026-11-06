# Seams in Python

A rating engine inherited without tests, and the places where a test can change what it does
without editing it. `RateEngine.quote` asks two carrier SDKs for a price and adds a margin. The
SDKs are stand-ins that do no I/O and raise `CarrierTimeoutError` where a connection would time
out, so a test that reaches one fails. Zones, weights and prices are illustrative.

## What it witnesses

The legacy engine, kept as found in `legacy.py`.

- `request_quote` is imported by name, `airco` is imported as a module and called as
  `airco.price`, both calls sit inside `quote`, and the margin is a default argument.
- A patch on the name in `seams.legacy` replaces FASTLINE. A patch on `seams.fastline` leaves the
  engine calling the real carrier. AIRCO is patched on its own module. `unittest.mock.patch`
  follows the same rule.
- `monkeypatch` refuses a misspelt name unless `raising=False`, which creates a name nothing
  reads. `patch` refuses a name the module lacks unless `create=True`. Only `autospec=True`
  refuses a call with the wrong signature. `monkeypatch.context()` undoes its changes.
- A patched `MARGIN` misses the default captured when the class was defined. A reload, run in a
  fresh interpreter, overwrites a patch, leaves a `from`-import on the old object and leaves an
  old instance on the old class.
- An object with a `price` method stands in for the `airco` module. One without it fails only
  when `quote` is called.

What mypy checks (version 2.4.1, `--strict`).

- A monkeypatched replacement of the wrong shape and a misspelt target string pass. A direct
  assignment to the module name is reported as `[assignment]`, together with `[attr-defined]`,
  because `seams.legacy` does not re-export the imported name.
- `patch` is typed as a `MagicMock` union, or as its replacement when `new=` is given. A
  decorator-injected mock needs an annotation. A fake of the wrong shape passed to a Protocol
  parameter is `[arg-type]` (reduced model).

## Layout

- `src/seams/domain.py`: `ConsignmentId`, `Consignment`, `Money`, `RateQuote`,
  `CarrierTimeoutError`.
- `src/seams/fastline.py`, `src/seams/airco.py`: the stand-in SDKs.
- `src/seams/legacy.py`: `MARGIN`, `RateEngine`.
- `tests/conftest.py`: the consignment and two fake carriers.

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

`tests/test_patching.py`

- `test_the_legacy_engine_calls_the_real_carrier`: `CarrierTimeoutError` for FASTLINE.
- `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`: string and object forms.
- `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`
- `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`
- `test_unittest_mock_patch_follows_the_same_lookup_rule`: `using-module` and `defining-module`.
- `test_monkeypatch_refuses_a_misspelt_name`
- `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`
- `test_patch_refuses_a_name_the_module_does_not_have`: and `create=True`.
- `test_autospec_refuses_a_call_with_the_wrong_signature`: `autospec` and `plain`.
- `test_monkeypatch_undoes_its_changes_when_the_context_ends`

`tests/test_seams.py`

- `test_patching_a_module_constant_misses_a_default_captured_at_definition`
- `test_reload_discards_a_patch_and_keeps_old_bindings`: four facts from a fresh interpreter.
- `test_an_object_with_the_right_method_can_stand_in_for_a_module`

`tests/test_static.py`

- `test_mypy_does_not_check_a_monkeypatched_replacement`
- `test_mypy_checks_a_direct_assignment_to_a_module_name`
- `test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement`
- `test_mypy_requires_an_annotation_on_a_decorator_injected_mock`
- `test_mypy_checks_a_fake_passed_to_a_protocol_parameter`: reduced model.
- `test_mypy_accepts_a_misspelt_monkeypatch_target_string`

Mocks and `monkeypatch` appear in these tests because the patch is what is under test. They never
appear in `src`. A mock is assignable to every type, so mypy checks none of the replacements.
