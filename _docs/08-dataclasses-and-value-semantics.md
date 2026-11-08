---
title: "Dataclasses and value semantics"
order: 8
layout: tutorial
sectionid: docs
part: "python-substrate"
description: "One frozen, slotted dataclass declaration writes the structure of the Value Object pattern, and three decisions stay with the author: the invariant, immutable field types, and value or entity."
---

## Learning objectives

By the end of this chapter you can:

- Say what `@dataclass(frozen=True, slots=True)` generates and which guarantees it leaves to you.
- Explain why a frozen dataclass hashes, why a mutable one doesn't, and why a `list` field breaks the promise.
- Amend a shared value with `replace` and say why the other holder keeps the old one.
- Choose between a value and an entity, and write each with the right `eq` setting.
- Say where `order=True`, `kw_only=True` and `field(compare=False)` fit, and what mypy checks and misses in each.

## Why this matters

Three failures share a cause. A consignment is shared by two booking requests, and a clerk reweighs it for one of them. The other request now shows the new weight, because both hold the same object. A stowage slot is a bay, a row and a tier, and a mutable `SlotId` can't key the reservation table at all: building the dict raises `TypeError`. Two stowage plans need a reservation table each: if they shared one default table, a slot reserved in one would show as taken in the other.

Each is the same question answered wrongly: is this thing a value, defined by its content, or an entity, defined by its identity? A value should compare by content, be safe to share and work as a dictionary key. An entity should not. The old way to get a value was a class written out by hand. In Python 3.15 one decorator writes most of it, and the parts it doesn't write are the parts that need judgement.

{% include excalidraw.html name="08-dataclasses-and-value-semantics" caption="Figure 8.1: One declaration, the Value Object's structure. A frozen, slotted, ordered dataclass writes the constructor, repr, equality, hash, ordering and the assignment guard for SlotId; the invariant, immutable field types and the value-or-entity choice stay with you." %}

Read the figure from the top. The accent box is the declaration the author writes. The arrows fan out to six generated members, and a second set of arrows brings them together in the box labelled with the Value Object force. The box underneath has no arrows into it. It lists what the decorator can't write: the invariant in `__post_init__`, immutable field types, and the decision that a type is a value at all.

## Value Object: the force and the structure

Martin Fowler's *Patterns of Enterprise Application Architecture* (2002) catalogues Value Object as "a small simple object, like money or a date range, whose equality isn't based on identity." Eric Evans's *Domain-Driven Design* (2003) draws the same line from the modelling side: an entity is tracked by who it is, and a value object is described by what it is. Both treat it as a design decision about the domain, and it isn't a Gang of Four catalogue entry.

The force is four needs at once. Two values with the same content should be equal. A value should be shareable without defensive copies. It should work as a dictionary key or set member. An invariant, such as a positive weight, should hold for as long as the value exists.

The structure that pattern calls for, written by hand, is private fields with read accessors, a constructor that checks the invariant, an `__eq__` and `__hash__` pair that must be kept in step, and methods that return a modified copy. The pair that has to stay in step is the one that drifts.

This pattern dissolves. A feature resolves the force without the pattern's structure: one `@dataclass(frozen=True, slots=True)` declaration produces the constructor, `repr`, equality, hash and an assignment guard, and `dataclasses.replace` is the copy-with-change method. Dataclasses arrived with [PEP 557](https://peps.python.org/pep-0557/), new in Python 3.7; the [`dataclasses` documentation](https://docs.python.org/3.15/library/dataclasses.html) covers the current behaviour, including `slots`, `kw_only` and `weakref_slot`, added later, and is the source for the generated behaviour below. What remains is the part no decorator can supply.

## One declaration: frozen and slotted

A weight is the simplest value here, one field, equal by content and positive by construction:

```python
@dataclass(frozen=True, slots=True, order=True)
class Weight:
    """A positive mass in kilograms, ordered by its one field."""

    kilograms: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.kilograms) and self.kilograms > 0):
            raise ValueError(f"kilograms must be positive and finite, got {self.kilograms}")
```

`inf > 0` is true, so the finiteness test is what rejects it. The decorator writes `__init__`, `__repr__`, `__eq__`, `__hash__` and the ordering methods, and with `frozen=True` it writes a `__setattr__` and `__delattr__` that raise `FrozenInstanceError`. `test_a_frozen_value_refuses_assignment` assigns to `kilograms` and matches the message `cannot assign to field 'kilograms'`. The same assignment is a static error. `test_mypy_checks_the_generated_methods[frozen-assignment]` runs this through `mypy --strict`:

```python
def reweigh(w: Weight) -> None:
    w.kilograms = 2.0
```

and gets `<string>:6: error: Property "kilograms" defined in "Weight" is read-only  [misc]`, which means the mistake is caught before a test runs.

Frozen guards attribute assignment; it doesn't seal the object. `test_frozen_is_a_setattr_guard_not_a_seal` calls `object.__setattr__(w, "kilograms", -5.0)` and the write succeeds, past the invariant. That's why the example doesn't normalise inside `__post_init__` through that back door: a type that mutates itself in its constructor is no longer immutable. The documentation on frozen instances notes that the generated `__init__` itself writes fields through `object.__setattr__`, and the back door is a reason to normalise before construction, which a later section does.

`slots=True` replaces the per-instance `__dict__` with fixed slots. A slotted class also loses the weak-reference slot. `test_slots_remove_dict_and_weakref_until_asked` shows `weakref.ref(w)` raising `TypeError` with the message `cannot create weak reference to 'Weight' object`, and shows that `weakref_slot=True` puts the slot back. mypy says nothing about it: `test_mypy_cannot_see_value_semantics_mistakes[slots-weakref]` runs `weakref.ref(Weight(1.0))` through `--strict` and gets exit status 0 and empty output. A cache that holds weak references to values fails at run time, not at type-check time.

## Hashing follows from frozen

A dataclass with `eq=True` generates `__eq__`. What it does about `__hash__` depends on `frozen`. With `frozen=True` it generates a hash from the fields, so equal values hash equal and `{slot: reservation}` finds its entry. With `eq=True` and no `frozen`, the class is mutable, so the decorator sets `__hash__` to `None` rather than offer a hash that changes under the key.

The fixture `_MutableSlotId` in `tests/test_aliasing.py` is a `SlotId` without `frozen`. `test_a_mutable_dataclass_is_not_a_dict_key` checks that its hash is `None` and that building `{slot: "held"}` raises `TypeError`. On Python 3.15 the message names the class twice, first by its module-qualified name, for example `cannot use 'test_aliasing._MutableSlotId' as a dict key (unhashable type: '_MutableSlotId')`, so the test matches only the stable `unhashable type: '_MutableSlotId'` part. mypy doesn't flag it: `test_mypy_cannot_see_value_semantics_mistakes[mutable-dict-key]` annotates `dict[MutableSlotId, str]` and builds one, and `--strict` exits 0 with no output. The failure shows up when the code runs, which is a reason to keep a test that puts two equal values in a set.

Frozen is also shallow. `_FrozenWithList` has one field, `codes: list[str]`. `test_frozen_is_shallow` appends to that list through a frozen instance, and the value changes. Hashing it raises `TypeError` with `unhashable type: 'list'`. The class is frozen and still isn't a value, because a field is mutable. The repair is a field type that is itself immutable: `tuple[str, ...]` in place of `list[str]`, `frozenset` in place of `set`. Frozen can't check this for you.

## Values and entities

Back to the shared consignment. `test_a_mutable_consignment_aliased_between_bookings_changes_both` builds two bookings around one plain mutable consignment, reweighs it through the first and finds the new weight through the second. Sharing is what made the change visible, so the cure is to make the value unable to change.

`Consignment` in the example is frozen, slotted and `kw_only`. An amendment isn't an edit. It's a new value:

```python
    amended = replace(request_a.consignment, weight=Weight(250.0))
    request_a = replace(request_a, consignment=amended)
```

`test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old` asserts that `amended` is not the original, that the first booking sees 250 kilograms, and that the second booking and the original still see 100. Two bookings can hold one consignment because neither can change it. `replace` calls the constructor, so `__post_init__` runs again: `test_replace_runs_post_init` shows `replace(Weight(1.0), kilograms=-1.0)` raising `ValueError`, and the same for a slot with `bay=0`. An amendment can't produce an invalid value.

Not everything should be a value. A stowage plan has a lifecycle, since slots are reserved over time, and two plans for one sailing are two plans:

```python
@dataclass(eq=False, slots=True)
class StowagePlan:
    """Slot reservations for one sailing. Equality and hash stay identity based."""

    sailing: str
    reservations: dict[SlotId, ConsignmentId] = field(default_factory=dict)

    def reserve(self, slot: SlotId, consignment_id: ConsignmentId) -> None:
        if slot in self.reservations:
            raise ValueError(f"slot {slot} already holds {self.reservations[slot]}")
        self.reservations[slot] = consignment_id

    def occupied(self) -> list[SlotId]:
        return sorted(self.reservations)
```

`eq=False` leaves the identity `__eq__` and identity hash from `object`, and the dataclass still writes `__init__` and `__repr__`. `test_stowage_plan_is_an_entity` creates two plans for `"SAILING-1"` and asserts they are unequal, that a set of both has two members, that a second reservation of a taken slot raises `ValueError`, and that the second plan's reservations stay empty. The last assertion exists because of `default_factory=dict`. A literal `{}` as a default would be one dict shared by all instances, so `test_mutable_default_is_refused_at_class_creation` shows the decorator raising `ValueError` with `use default_factory`. mypy is silent on that too (`mutable-default` in the same static test), so the refusal at class creation is the guard that exists.

Sometimes a value has fields that aren't part of its identity. A booking retried with a different driver remark is the same booking:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    """A retried request with a different remark is the same booking."""

    consignment: Consignment
    insured: bool = False
    remarks: str = field(default="", compare=False)
```

`field(compare=False)` keeps `remarks` out of equality and the generated hash. `test_compare_false_keeps_remarks_out_of_equality` builds two requests that differ only in remarks, finds them equal with equal hashes, and shows a dictionary keyed by both holding one entry. Each request still prints its own remark, because `repr` is unaffected. When a type has many optional fields and the question is how to assemble it, that's a construction problem, and the chapter titled [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}) takes it up.

## Ordering: order=True and when to write it yourself

`order=True` generates `__lt__`, `__le__`, `__gt__` and `__ge__`, comparing the fields as tuples in declaration order. For `SlotId` that order is the meaning: bay, then row, then tier. `test_order_true_sorts_by_field_order` sorts four slots into that order, and the same test takes a `max` over three weights. `StowagePlan.occupied` returns `sorted(self.reservations)` for the same reason.

The danger is a type whose fields don't compare meaningfully in sequence. A `Money` with an amount and a currency would, under `order=True`, put three euros below five dollars without complaint. `_OrderedMoney` in `tests/test_generated.py` is that type, and `test_order_true_would_compare_money_across_currencies` asserts the comparison holds. The real `Money` has no ordering, and the same test asserts that `<` on two of them raises `TypeError`. The static side agrees. `test_mypy_checks_the_generated_methods[money-has-no-order]` gets `<string>:4: error: Unsupported left operand type for < ("Money")  [operator]`. Ordering belongs on a value when the comparison means something for each pair of values the type can hold.

A hand-written `__lt__` and `order=True` don't mix. `test_order_true_refuses_a_hand_written_lt` defines both, and class creation fails with `TypeError: Cannot overwrite attribute __lt__ in class _HandWritten Consider using functools.total_ordering`. mypy also flags the method, with `[misc]`, so the test carries a `# type: ignore[misc]` that `--strict` would report if mypy stopped complaining. If the comparison isn't field order, drop `order=True` and write the method with `functools.total_ordering`, as the chapter titled [The data model: dunder methods as the substrate]({{ '/docs/07-the-data-model/' | relative_url }}) does.

## Invariants: validate in __post_init__, normalise before

The decorator can't know that a weight must be positive or a currency three capital letters. The author states those checks in `__post_init__`, and `replace` reruns them. The example's `Money` shows the division of labour:

```python
@dataclass(frozen=True, slots=True)
class Money:
    """An amount in whole cents and an ISO 4217 code. Unordered: ordering needs one currency."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not _CURRENCY.fullmatch(self.currency):
            raise ValueError(f"currency must be three capital letters, got {self.currency!r}")
        if self.amount != self.amount.quantize(_CENT):
            raise ValueError(f"amount must be whole cents, got {self.amount}")

    @classmethod
    def of(cls, amount: str, currency: str) -> Self:
        """Quantise to cents before construction, so validation only has to read."""
        return cls(Decimal(amount).quantize(_CENT, rounding=ROUND_HALF_UP), currency)
```

`__post_init__` reads and raises. It doesn't repair. A value arriving with three decimal places is rejected, not rounded, because rounding is a decision about the input that belongs where the input is accepted. `Money.of("12.505", "EUR")` rounds half up to `12.51` before construction, and `Money(Decimal("12.505"), "EUR")` raises `ValueError` with `amount must be whole cents`. `test_money_validates_and_of_normalises` checks both, along with the lower-case currency rejection. This split keeps the frozen guarantee intact, since nothing needs `object.__setattr__`.

Two switches help callers use these values correctly. `kw_only=True` on `Consignment` forces keyword construction, so a transposed weight and destination can't slip through as positional arguments: `test_kw_only_rejects_positional_arguments` shows `TypeError` with `positional argument`, and the mypy witness reports `<string>:5: error: Too many positional arguments for "Consignment"  [call-arg]`. And mypy checks the keyword names of `replace` against the class: `replace(Weight(1.0), kilos=2.0)` gets `<string>:6: error: Unexpected keyword argument "kilos" for "replace" of "Weight"  [call-arg]`.

## When not to use it

A type with a lifecycle and an identity isn't a value. `StowagePlan` changes as slots are reserved, and two plans with equal reservations are still two plans, so it uses `eq=False`. Freezing it would force each reservation to build a new plan, which describes the wrong thing.

Data that has to change in place as one aggregate is another poor fit. A running tally with thousands of updates is a mutable object with a method, not a stream of replacements.

A value whose equality isn't field by field needs a hand-written `__eq__` and a matching `__hash__`. A carton that may be stowed on any face is equal to its rotation, and no field comparison says so. The chapter titled [The data model: dunder methods as the substrate]({{ '/docs/07-the-data-model/' | relative_url }}) covers that contract.

<blockquote class="ai-sidebar" markdown="1">
**Specifying value types.** "Write the value types" leaves open whether they mutate, what their field types are and where normalising happens. Paste a prompt that states the form:

> Write each value as `@dataclass(frozen=True, slots=True)` with immutable field types (`tuple`, `frozenset`, `Decimal`). `__post_init__` only validates and raises; normalise in a classmethod such as `Money.of` before construction. Amend with `dataclasses.replace`. Use `order=True` only where field order is the meaning, and `eq=False` for an entity such as `StowagePlan`. Add a test that puts two equal values in a set.

If `__post_init__` assigns through `object.__setattr__`, ask for the normalising constructor.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then from the example directory:

```bash
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 32 items

tests/test_aliasing.py::test_a_mutable_consignment_aliased_between_bookings_changes_both PASSED [  3%]
tests/test_aliasing.py::test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old PASSED [  6%]
tests/test_aliasing.py::test_replace_runs_post_init PASSED               [  9%]
tests/test_aliasing.py::test_a_mutable_dataclass_is_not_a_dict_key PASSED [ 12%]
tests/test_generated.py::test_order_true_sorts_by_field_order PASSED     [ 15%]
tests/test_generated.py::test_order_true_would_compare_money_across_currencies PASSED [ 18%]
tests/test_generated.py::test_order_true_refuses_a_hand_written_lt PASSED [ 21%]
tests/test_generated.py::test_compare_false_keeps_remarks_out_of_equality PASSED [ 25%]
tests/test_generated.py::test_kw_only_rejects_positional_arguments PASSED [ 28%]
tests/test_generated.py::test_money_validates_and_of_normalises PASSED   [ 31%]
tests/test_generated.py::test_slot_id_validates_each_coordinate PASSED   [ 34%]
tests/test_generated.py::test_money_addition_needs_one_currency PASSED   [ 37%]
tests/test_generated.py::test_stowage_plan_is_an_entity PASSED           [ 40%]
tests/test_generated.py::test_mutable_default_is_refused_at_class_creation PASSED [ 43%]
tests/test_static.py::test_mypy_checks_the_generated_methods[frozen-assignment] PASSED [ 46%]
tests/test_static.py::test_mypy_checks_the_generated_methods[kw-only-positional] PASSED [ 50%]
tests/test_static.py::test_mypy_checks_the_generated_methods[replace-unknown-field] PASSED [ 53%]
tests/test_static.py::test_mypy_checks_the_generated_methods[money-has-no-order] PASSED [ 56%]
tests/test_static.py::test_mypy_cannot_see_value_semantics_mistakes[mutable-dict-key] PASSED [ 59%]
tests/test_static.py::test_mypy_cannot_see_value_semantics_mistakes[mutable-default] PASSED [ 62%]
tests/test_static.py::test_mypy_cannot_see_value_semantics_mistakes[slots-weakref] PASSED [ 65%]
tests/test_static.py::test_mypy_accepts_the_correct_use_of_the_same_values PASSED [ 68%]
tests/test_values.py::test_equal_values_are_interchangeable PASSED       [ 71%]
tests/test_values.py::test_weight_must_be_positive_and_finite[0.0] PASSED [ 75%]
tests/test_values.py::test_weight_must_be_positive_and_finite[-1.0] PASSED [ 78%]
tests/test_values.py::test_weight_must_be_positive_and_finite[inf] PASSED [ 81%]
tests/test_values.py::test_weight_must_be_positive_and_finite[-inf] PASSED [ 84%]
tests/test_values.py::test_weight_must_be_positive_and_finite[nan] PASSED [ 87%]
tests/test_values.py::test_a_frozen_value_refuses_assignment PASSED      [ 90%]
tests/test_values.py::test_frozen_is_a_setattr_guard_not_a_seal PASSED   [ 93%]
tests/test_values.py::test_frozen_is_shallow PASSED                      [ 96%]
tests/test_values.py::test_slots_remove_dict_and_weakref_until_asked PASSED [100%]

============================== 32 passed in 3.80s ==============================
```

```text
Success: no issues found in 9 source files
```

The suite has 23 test functions and 32 cases, because the static module parametrises two of its three functions and the weight test runs five values.

**Experiment one: remove `frozen=True` from `SlotId`.** In a scratch copy, change the decorator on `SlotId` to `@dataclass(slots=True, order=True)` and run `uv run pytest -q`. Two tests fail and 30 pass. Filtering the output to the assertion lines and the summary, with `uv run pytest -q | grep -E '^(E  |FAILED|[0-9]+ (passed|failed))'`, gives:

```text
E       TypeError: cannot use 'value_semantics.values.SlotId' as a dict key (unhashable type: 'SlotId')
E           TypeError: unhashable type: 'SlotId'
FAILED tests/test_generated.py::test_stowage_plan_is_an_entity - TypeError: c...
FAILED tests/test_values.py::test_equal_values_are_interchangeable - TypeErro...
2 failed, 30 passed in 3.61s
```

The first failure is raised inside `StowagePlan.reserve`, and the second is `hash(left)` in the equality test. The dict-key test doesn't fail, because it uses its own fixture and not `SlotId`. mypy reports `Success: no issues found in 9 source files`: nothing in the type system connects `frozen` to the dictionary the plan keeps. Restore the decorator.

**Experiment two: add `order=True` to `Money`.** Change its decorator to `@dataclass(frozen=True, slots=True, order=True)` and run both commands. pytest reports two failures, shown with the same filter:

```text
E       Failed: DID NOT RAISE TypeError
E       assert 0 == 1
FAILED tests/test_generated.py::test_order_true_would_compare_money_across_currencies
FAILED tests/test_static.py::test_mypy_checks_the_generated_methods[money-has-no-order]
2 failed, 30 passed in 3.71s
```

The first test expected `<` on two `Money` values to raise and it now succeeds across currencies. The second expected exit status 1 from mypy and got 0. The member's own mypy run adds one error:

```text
tests/test_generated.py:27: error: Unused "type: ignore" comment  [unused-ignore]
```

The `# type: ignore[operator]` that suppressed the comparison error has nothing left to suppress, so strict mode reports the line. Restore the decorator.

## What you can do now

- Say what the decorator generates: `__init__`, `__repr__`, `__eq__`, `__hash__` and the assignment guard, with `test_frozen_is_a_setattr_guard_not_a_seal` showing what it leaves to you.
- Explain hashing: `_MutableSlotId` can't key a dict, and `_FrozenWithList` can't be hashed, because a `list` field breaks the promise.
- Amend a shared value: `replace` builds the new consignment, and `test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old` shows the other booking keeping the old one.
- Choose value or entity: `SlotId` and `Consignment` compare by content, and `StowagePlan` with `eq=False` compares by identity.
- Place the switches: `order=True` against `_OrderedMoney`, `kw_only=True` on `Consignment` and `field(compare=False)` on `remarks`, each with its static case in the mypy tests.

## For deeper coverage

Martin Fowler's *Patterns of Enterprise Application Architecture* (2002) includes Value Object in its catalogue, and the [catalogue entry](https://martinfowler.com/eaaCatalog/valueObject.html) is short. Eric Evans's *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003) develops value objects and entities as modelling tools, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}).

On the Python side, Luciano Ramalho's *Fluent Python*, second edition, has a chapter on data class builders, and Brett Slatkin's *Effective Python*, third edition, has practical rules on dataclasses. Both are in the bibliography.

The language references are [PEP 557](https://peps.python.org/pep-0557/) for the design and the [`dataclasses` documentation](https://docs.python.org/3.15/library/dataclasses.html) for frozen instances, `__post_init__`, `replace`, mutable default values, `slots` and `weakref_slot`, and `kw_only`.
