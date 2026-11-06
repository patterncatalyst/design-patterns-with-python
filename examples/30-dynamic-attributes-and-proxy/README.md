# Dynamic attributes: `__getattr__` and Proxy as a feature

A virtual proxy creates an expensive object on demand. In Python an object can do that for itself:
`__getattr__` runs only when ordinary lookup fails, so a tracking history can declare its fields,
load them from a slow carrier feed on the first read, and keep them as plain attributes. That is
interception without a surrogate. What remains to design is which names it may load, that it never
reads a missing attribute while loading, and that it behaves like any other object under `dir()`,
`copy`, special-method lookup and mypy.

## What it witnesses

A history that loads itself.

- `TrackingHistory` declares `events`, `status` and `last_port` as class annotations. Nothing loads
  until one of them is read. One load fills all three, and they then sit in the instance dictionary,
  so later reads never reach `__getattr__`.
- `__setattr__` refuses assignment to the loaded fields, and the load writes around it through
  `vars(self).update`. `__iter__` is explicit, and iterating loads.
- `history_form` is `getattr` or `cached_property`. The conftest `_CachedTrackingHistory` passes the
  same table of four consignments and three shared behaviour tests.

When each hook runs, and the recursion trap.

- `__getattr__` runs once, for the first missing name. A counting `__getattribute__` runs on every
  read, including the set `consignment_id`.
- A `__getattr__` that reads a missing attribute recurses on a bare instance, so `copy.copy`,
  `copy.deepcopy` and `pickle` recurse too. Refusing names outside a fixed set, reading through
  `object.__getattribute__` and reading through `vars(self)` each stop it.
- `TrackingHistory` copies before and after loading, and copying an unloaded history loads nothing.
- A `__getattr__` that answers every name from a mapping returns `None` for a misspelt field.

Consistent with the rest of Python.

- `dir()` lists the lazy fields without loading, and with `__dir__` a misspelt field gets the
  interpreter's "Did you mean" hint.
- `iter()` and `len()` look on the type and reach neither `__getattr__` nor `__getattribute__`.
- `hasattr` on a lazy name loads the history.

A module-level `__getattr__`.

- `tracking.LazyTrackingHistory` warns with `DeprecationWarning`, attributed to the caller, and
  returns `TrackingHistory`. Any other missing module attribute raises `AttributeError`, and a
  module `__dir__` lists the old name.

mypy 2.4.1.

- It keeps the declared field types and types an unknown attribute as `__getattr__`'s return type,
  `object`, so only its use is reported.
- It accepts assigning a loaded field and a new name, which the run time refuses or allows
  differently, because `__setattr__` takes any name.
- On a reduced `cached_property` model it reports a typo with `maybe "status"?`.
- It accepts any name imported through a module `__getattr__`.

## Layout

- `src/dynamic_attributes/tracking.py`: `ConsignmentId`, `HandlingKind`, `ConsignmentStatus`,
  `HandlingEvent`, `TrackingHistory`, and the module `__getattr__` and `__dir__` for
  `LazyTrackingHistory`.

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

`tests/test_history.py`

- `test_every_history_form_reads_the_loaded_fields`: `history_form` and four consignments, including
  one with no events.
- `test_every_history_form_loads_once_for_every_field`: two reads of each field, one load.
- `test_every_history_form_refuses_assignment_to_a_loaded_field`: `AttributeError`.
- `test_every_history_form_raises_attribute_error_for_a_misspelt_field`: the message names
  `stauts`.
- `test_nothing_is_loaded_until_a_field_is_read`: only `_load` and `consignment_id` in the
  instance dictionary.
- `test_a_loaded_history_reads_its_fields_from_the_instance_dict`: the three fields in `vars`.
- `test_iterating_a_history_loads_it`: the event kinds, one load.

`tests/test_lookup.py`

- `test_getattr_runs_only_when_normal_lookup_fails`: a counting subclass logs `status` once over
  three reads.
- `test_getattribute_runs_on_every_access`: a counting subclass logs `consignment_id` once and
  `status` three times.
- `test_a_getattr_that_reads_a_missing_attribute_recurses`: a bare instance, `RecursionError`.
- `test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute`: `copy`, `deepcopy` and
  `pickle`.
- `test_copy_keeps_a_history_before_and_after_loading`: copies of `TrackingHistory`, unloaded and
  loaded.
- `test_each_fix_keeps_getattr_out_of_recursion`: the allow-list, `object.__getattribute__` and
  `vars`.
- `test_a_getattr_that_returns_none_hides_a_typo`: a mapping lookup that answers every name.
- `test_implicit_special_method_lookup_bypasses_getattr`: `iter()` and `len()` against a
  forwarding object, with an empty hook log.
- `test_dir_lists_the_lazy_fields_before_loading`: no load.
- `test_a_misspelt_field_suggests_the_declared_name_through_dir`: the hint, and none without
  `__dir__`.
- `test_hasattr_loads_the_history`: one load.

`tests/test_module.py`

- `test_a_deprecated_name_warns_and_returns_the_tracking_history`: the warning text, the value and
  the file it is attributed to.
- `test_an_unknown_module_attribute_raises_attribute_error`: the message names the module.
- `test_module_dir_lists_the_deprecated_name`: `dir()` of the module.

`tests/test_static.py`

- `test_mypy_types_an_unknown_attribute_by_the_getattr_return_type`: `[attr-defined]` on the use,
  and the type `object` (one error).
- `test_mypy_keeps_the_declared_field_types`: `[assignment]` against `ConsignmentStatus | None`.
- `test_mypy_accepts_an_assignment_that_setattr_refuses`: exit 0, and the run time refuses the
  loaded field and accepts the new name.
- `test_mypy_reports_a_typo_on_the_cached_property_form`: `maybe "status"?` (a reduced model).
- `test_mypy_accepts_any_name_imported_through_a_module_getattr`: exit 0 and the type, then
  `ImportError` at run time.

Classes and functions named with a leading underscore in the tests are fixtures and aren't part
of the model code.
