# Dataclasses and value semantics

Value types for a shipping booking, built from frozen and slotted dataclasses. Each test witnesses
a claim about what `@dataclass` generates, what its switches change, and what stays with the
author. The chapter's thesis is that Value Object dissolves into one declaration.

## What it witnesses

A frozen, slotted dataclass supplies the pattern's structure.

- `Weight`, `Money` and `SlotId` compare by content, hash equal when equal and work as dict keys.
- Assignment raises `FrozenInstanceError`. Frozen is a `__setattr__` guard and is shallow: a
  `list` field still mutates and makes the value unhashable.
- `slots=True` drops `__dict__` and weak references, and `weakref_slot=True` restores the latter.

Values and entities.

- A mutable consignment shared between two bookings changes both. With a frozen `Consignment`,
  `replace` returns a new value, reruns `__post_init__` and leaves the other booking alone.
- A mutable `eq` dataclass has no hash and cannot be a dict key.
- `StowagePlan` is an entity: `eq=False` keeps identity equality, `default_factory` gives each
  plan its own reservations, and a mutable default is refused when the class is created.

Ordering and construction.

- `order=True` sorts `SlotId` by bay, row and tier. On an amount with a currency it would compare
  across currencies without complaint, so `Money` defines no order.
- `order=True` refuses a hand-written `__lt__`.
- `field(compare=False)` keeps `remarks` out of equality, hash and dict keys, and `kw_only=True`
  rejects positional construction.
- `__post_init__` only reads. `Money.of` quantises to cents before construction.

Static checks.

- `mypy --strict` flags frozen assignment, positional arguments to a `kw_only` class, an unknown
  `replace` keyword and `<` on `Money`.
- It reports nothing for a mutable dict key, a mutable default or a weak reference to a slotted
  instance.

## Layout

- `src/value_semantics/values.py`: `ConsignmentId`, `Weight`, `Money`, `SlotId`.
- `src/value_semantics/booking.py`: `Consignment`, `BookingRequest`.
- `src/value_semantics/stowage.py`: `StowagePlan`.

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

`tests/test_values.py`

- `test_equal_values_are_interchangeable`: equal `Weight`, `Money` and `SlotId` values are
  equal, hash equal and find the same dict entry.
- `test_weight_must_be_positive_and_finite`: zero, negative, infinite and NaN weights raise
  `ValueError`.
- `test_a_frozen_value_refuses_assignment`: assigning to a field raises `FrozenInstanceError`
  naming the field.
- `test_frozen_is_a_setattr_guard_not_a_seal`: `object.__setattr__` writes an invalid weight.
- `test_frozen_is_shallow`: a frozen class with a `list` field mutates and cannot be hashed.
- `test_slots_remove_dict_and_weakref_until_asked`: no `__dict__`, no weak reference, until
  `weakref_slot=True`.

`tests/test_aliasing.py`

- `test_a_mutable_consignment_aliased_between_bookings_changes_both`: reweighing through one
  booking shows through the other.
- `test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old`: `replace` gives a new
  consignment and the original and the other booking are unchanged.
- `test_replace_runs_post_init`: `replace` with an invalid weight or bay raises `ValueError`.
- `test_a_mutable_dataclass_is_not_a_dict_key`: the hash is `None` and a dict literal keyed by it raises
  `TypeError`.

`tests/test_generated.py`

- `test_order_true_sorts_by_field_order`: slots sort by bay, row, tier.
- `test_order_true_would_compare_money_across_currencies`: an ordered money type compares EUR
  with USD, and `Money` raises `TypeError`.
- `test_order_true_refuses_a_hand_written_lt`: the class cannot be created.
- `test_compare_false_keeps_remarks_out_of_equality`: two requests that differ only in remarks
  are one dict key.
- `test_kw_only_rejects_positional_arguments`: positional `Consignment` and `BookingRequest`
  raise `TypeError`.
- `test_money_validates_and_of_normalises`: `Money.of` rounds half up, and the constructor
  rejects a third decimal place and a lower-case code.
- `test_slot_id_validates_each_coordinate`: bay, row and tier each raise `ValueError`.
- `test_money_addition_needs_one_currency`: same-currency addition works, mixed currencies
  raise `ValueError` and a foreign operand raises `TypeError`.
- `test_stowage_plan_is_an_entity`: two plans for one sailing are unequal, a taken slot raises
  `ValueError`, reservations are not shared and `occupied()` is sorted.
- `test_mutable_default_is_refused_at_class_creation`: `{}` as a default raises `ValueError`.

`tests/test_static.py`

- `test_mypy_checks_the_generated_methods`: frozen assignment gives `[misc]`, positional
  `Consignment` and an unknown `replace` keyword give `[call-arg]`, and `<` on `Money` gives
  `[operator]`.
- `test_mypy_cannot_see_value_semantics_mistakes`: a mutable dict key, a mutable default and a
  weak reference to a slotted instance pass `mypy --strict` with no output.
- `test_mypy_accepts_the_correct_use_of_the_same_values`: the control snippet is clean.

Classes named with a leading underscore in the test modules are negative fixtures and are not
part of the model code.
