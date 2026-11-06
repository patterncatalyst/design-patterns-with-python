# Descriptors and properties

Python's attribute lookup calls `__get__` and `__set__` for you, and `property` and `cached_property`
are descriptors already written. The design that survives is one validator per rule shared by every
field that needs it, the choice between `property`, a descriptor and `cached_property`, and where a
descriptor can sit on a dataclass: a frozen class takes one, `slots=True` removes it. The example
validates weights and extents in the Consignment area. Weights and the volumetric factor are
illustrative.

## What it witnesses

One attribute, then many.

- `Container.payload_kg` is a read-only computed `property`, recomputed after each `load`, and
  assigning to it raises `AttributeError`. `load` refuses a consignment that takes the payload past
  `max_payload_kg`, and accepts one that reaches it exactly.
- `Positive` is one descriptor class on six `Decimal` fields in three classes: `Consignment.kilograms`,
  `Dimensions.length_cm`, `width_cm` and `height_cm`, and `Container.tare_kg` and `max_payload_kg`.
  `__set_name__` gives each field its own name and its own storage, written through `vars()`. Each
  refuses a bad value with its own name in the message on construction, and `tare_kg` refuses one
  on assignment.
- `field_form` is `descriptor` or `property`: `Dimensions` and a plain class with one validating
  property pair per field. Both give the same answer on one table of extents. A copy-pasted setter
  that drops `is_finite()` accepts infinity, and `Dimensions` refuses it.

Lookup and dataclasses.

- A data descriptor beats an entry in the instance dictionary, and an entry in the instance
  dictionary beats a `cached_property`. Class access to a `Positive` field raises
  `AttributeError`.
- On a dataclass, class access decides the default: a descriptor that raises leaves the field with
  none, and one that returns itself becomes the default. A frozen class refuses a descriptor that
  writes with `setattr`, and refuses assignment. `dataclasses.replace` validates, and equal values
  compare and hash equal.
- mypy types a field by `__set__`'s value and reads `= Positive()` as a default. On a
  `slots=True` dataclass mypy exits 0 while the slot replaces the descriptor and accepts `-1`.

`cached_property`.

- `Consignment.chargeable_kg` is the larger of the actual and the volumetric weight at 167 kg per
  cubic metre. It is absent from `vars()` before the first read, present after it, recomputed by
  `replace`, and refused by `del` on a frozen class.
- A slotted class has no `__dict__` to cache in. Over mutable state a cached value goes stale, which
  is why `payload_kg` is a `property`. Since 3.12 the getter can run twice when two threads race,
  forced here with a `threading.Barrier`.

## Layout

- `src/descriptors_properties/fields.py`: `Positive`.
- `src/descriptors_properties/cargo.py`: `ConsignmentId`, `VOLUMETRIC_KG_PER_M3`, `ContainerError`,
  `Dimensions`, `Consignment`, `Container`.

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

`tests/test_fields.py`

- `test_every_field_form_validates_the_same_extents`: `field_form` and five rows of extents.
- `test_a_positive_field_refuses_a_bad_value_on_every_class`: four fields across the three classes.
- `test_assignment_to_a_container_field_is_validated`: the old value stays.
- `test_set_name_gives_each_field_its_own_storage`: the keys of `vars()`.
- `test_one_descriptor_class_validates_every_field`: six class entries, one class.
- `test_a_copy_pasted_property_validator_drifts`: a test-local copy without `is_finite()`.
- `test_a_property_without_a_setter_refuses_assignment`: `has no setter`.
- `test_payload_is_recomputed_after_each_load`: 100, then 350.
- `test_load_refuses_a_consignment_over_the_max_payload`: at the limit and over it.

`tests/test_lookup.py`

- `test_a_data_descriptor_takes_precedence_over_the_instance_dict`: a planted `kilograms`.
- `test_an_instance_dict_entry_takes_precedence_over_cached_property`: a planted `chargeable_kg`.
- `test_class_access_to_a_positive_field_raises_attribute_error`: on `Container`.

`tests/test_dataclasses.py`

- `test_a_descriptor_field_has_no_default_when_class_access_raises`: `MISSING` and a `TypeError`.
- `test_a_descriptor_that_returns_itself_on_class_access_becomes_the_default`: a test-local subclass.
- `test_a_frozen_dataclass_refuses_a_descriptor_that_writes_with_setattr`: `_length_cm`.
- `test_a_frozen_dataclass_refuses_assignment_to_a_descriptor_field`: `FrozenInstanceError`.
- `test_replace_validates_the_new_value`: a negative width.
- `test_equal_dimensions_compare_and_hash_equal`: and a different height does not.

`tests/test_cached.py`

- `test_chargeable_weight_is_computed_on_first_access_and_stored`: `vars()` before and after.
- `test_chargeable_weight_is_the_larger_of_actual_and_volumetric_weight`: `bulky` and `heavy`.
- `test_cached_property_needs_an_instance_dict`: a test-local slotted class.
- `test_a_frozen_dataclass_cannot_clear_a_cached_property`: `cannot delete field`.
- `test_replace_recomputes_the_chargeable_weight`: 300 after 160.32.
- `test_a_cached_property_over_mutable_state_goes_stale`: a test-local container subclass.
- `test_a_cached_property_getter_can_run_twice_under_threads`: two threads and a `Barrier`.

`tests/test_static.py`

- `test_mypy_types_a_positive_field_by_its_set_value`: `[arg-type]`, `[assignment]` and `[misc]`.
- `test_mypy_reads_a_descriptor_field_as_a_default`: exit 0, and the run-time `TypeError`.
- `test_mypy_accepts_cached_property_on_a_slotted_dataclass`: exit 0 and the run-time `TypeError`
  (a reduced model).
- `test_mypy_accepts_a_descriptor_field_on_a_slotted_dataclass`: exit 0, and `-1` accepted (a reduced
  model).

Classes and functions named with a leading underscore in the tests are fixtures and aren't part
of the model code.
