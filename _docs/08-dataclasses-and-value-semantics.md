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

Three failures share a cause:

- Two booking requests share one consignment. A clerk reweighs it for one, and the other shows the new weight too.
- A stowage slot is a bay, a row and a tier. A mutable `SlotId` can't key the reservation table: building the dict raises `TypeError`.
- Two stowage plans share one default reservation table, so a slot reserved in one shows as taken in the other.

Each one answers the same question wrongly: is this thing a value, defined by its content, or an entity, defined by its identity? A value compares by content, is safe to share and works as a dictionary key. An entity doesn't. One decorator writes most of a value, and the parts it leaves out need judgement.

{% include excalidraw.html name="08-dataclasses-and-value-semantics" described="true" caption="Figure 8.1: One declaration, the Value Object's structure. A frozen, slotted, ordered dataclass writes the constructor, repr, equality, hash, ordering and the assignment guard for SlotId; the invariant, immutable field types and the value-or-entity choice stay with you." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-08-dataclasses-and-value-semantics" markdown="1">
The accent box at the top is the declaration the author writes. Arrows fan out to six generated members, and a second set of arrows brings them together in the box labelled with the Value Object force. The box underneath has no arrows into it. It lists what the decorator can't write: the invariant in `__post_init__`, immutable field types, and the decision that a type is a value at all.
</div>
</details>

The figure separates what the decorator writes from what stays with you.

## Value Object: the force and the structure

Martin Fowler's *Patterns of Enterprise Application Architecture* (2002) catalogues Value Object as "a small simple object, like money or a date range, whose equality isn't based on identity." Eric Evans's *Domain-Driven Design* (2003) draws the same line from the modelling side: an entity is tracked by who it is, and a value object is described by what it is. It's a domain decision, not a Gang of Four entry.

The force is four needs at once. Two values with the same content should be equal. A value should be shareable without defensive copies. It should work as a dictionary key or set member. An invariant, such as a positive weight, should hold for as long as the value exists.

Written by hand, the structure is private fields with read accessors, a constructor that checks the invariant, an `__eq__` and `__hash__` pair kept in step, and methods that return a modified copy. The pair that has to stay in step is the one that drifts.

This pattern dissolves. One `@dataclass(frozen=True, slots=True)` declaration produces the constructor, `repr`, equality, hash and an assignment guard, and `dataclasses.replace` is the copy-with-change method. Dataclasses arrived with [PEP 557](https://peps.python.org/pep-0557/), new in Python 3.7; the [`dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html) covers the current behaviour, including `slots`, `kw_only` and `weakref_slot`, added later.

## One declaration: frozen and slotted

A weight is the simplest value: one field, equal by content and positive by construction:

```python
@dataclass(frozen=True, slots=True, order=True)
class Weight:
    """A positive mass in kilograms, ordered by its one field."""

    kilograms: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.kilograms) and self.kilograms > 0):
            raise ValueError(f"kilograms must be positive and finite, got {self.kilograms}")
```

`inf > 0` is true, so the finiteness test is what rejects it. The decorator writes `__init__`, `__repr__`, `__eq__`, `__hash__` and the ordering methods, and with `frozen=True` a `__setattr__` and `__delattr__` that raise `FrozenInstanceError` (`cannot assign to field 'kilograms'`). mypy catches the same assignment statically:

```python
def reweigh(w: Weight) -> None:
    w.kilograms = 2.0
```

`--strict` reports `<string>:6: error: Property "kilograms" defined in "Weight" is read-only  [misc]`.

Frozen guards attribute assignment; it doesn't seal the object. `object.__setattr__(w, "kilograms", -5.0)` succeeds, past the invariant. The generated `__init__` itself writes fields that way, as the documentation on frozen instances notes. Don't use the back door to normalise inside `__post_init__`: normalise before construction, as the section on invariants does.

`slots=True` replaces the per-instance `__dict__` with fixed slots and drops the weak-reference slot too. `weakref.ref(w)` raises `TypeError` (`cannot create weak reference to 'Weight' object`) until `weakref_slot=True` puts it back. mypy accepts `weakref.ref(Weight(1.0))` without a word, so a cache of weak references to values fails at run time, not at type-check time.

## Hashing follows from frozen

With `eq=True`, the default, a dataclass generates `__eq__`, and `frozen` decides `__hash__`:

| Declaration | `__hash__` | As a dict key |
| --- | --- | --- |
| `frozen=True` | generated from the fields | equal values find the same entry |
| `eq=True`, not frozen | set to `None` | raises `TypeError: unhashable type` |
| `frozen=True` with a `list` field | generated, but hashing the list fails | raises `TypeError: unhashable type: 'list'` |

The decorator sets `__hash__` to `None` on a mutable class rather than offer a hash that changes under the key. mypy doesn't flag a `dict` keyed by the mutable class: `--strict` exits 0. The failure shows up when the code runs, so keep a test that puts two equal values in a set.

Frozen is also shallow. Appending to a `list[str]` field through a frozen instance changes the value. The class is frozen and still isn't a value. The repair is a field type that is itself immutable: `tuple[str, ...]` in place of `list[str]`, `frozenset` in place of `set`. Frozen can't check this for you.

## Values and entities

Back to the shared consignment. With a plain mutable consignment, reweighing it through one booking changes what the other booking sees. Sharing made the change visible, so the cure is a value that can't change.

`Consignment` is frozen, slotted and `kw_only`. An amendment isn't an edit. It's a new value:

```python
    amended = replace(request_a.consignment, weight=Weight(250.0))
    request_a = replace(request_a, consignment=amended)
```

The first booking now sees 250 kilograms, and the second booking and the original still see 100. Two bookings can hold one consignment because neither can change it. `replace` calls the constructor, so `__post_init__` runs again: `replace(Weight(1.0), kilograms=-1.0)` raises `ValueError`, and so does a slot amended to `bay=0`. An amendment can't produce an invalid value.

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

`eq=False` keeps the identity `__eq__` and hash from `object`, and the dataclass still writes `__init__` and `__repr__`. Two plans for `"SAILING-1"` are unequal, a set of both has two members, and reserving a taken slot raises `ValueError`. `default_factory=dict` gives each plan its own table. A literal `{}` default would be one dict shared by every instance, so the decorator refuses it at class creation with `ValueError` (`use default_factory`). mypy is silent on that too, so the refusal at class creation is the only guard.

Sometimes a value has fields that aren't part of its identity. A booking retried with a different driver remark is the same booking:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    """A retried request with a different remark is the same booking."""

    consignment: Consignment
    insured: bool = False
    remarks: str = field(default="", compare=False)
```

`field(compare=False)` keeps `remarks` out of equality and the hash. Two requests that differ only in remarks are equal, hash equal and occupy one dictionary entry, and each still prints its own remark, because `repr` is unaffected. When a type has many optional fields and the question is how to assemble it, that's a construction problem, covered in [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}).

## Ordering: order=True and when to write it yourself

`order=True` generates `__lt__`, `__le__`, `__gt__` and `__ge__`, comparing the fields as tuples in declaration order. For `SlotId` that order is the meaning: bay, then row, then tier. `sorted` and `max` work on slots and weights, and `StowagePlan.occupied` relies on it.

The danger is a type whose fields don't compare meaningfully in sequence. A `Money` with an amount and a currency would, under `order=True`, put three euros below five dollars without complaint. The real `Money` has no ordering: `<` raises `TypeError`, and mypy reports `<string>:4: error: Unsupported left operand type for < ("Money")  [operator]`. Put ordering on a value only when the comparison means something for every pair of values the type can hold.

A hand-written `__lt__` and `order=True` don't mix. Class creation fails with `TypeError: Cannot overwrite attribute __lt__ in class _HandWritten Consider using functools.total_ordering`, and mypy flags the method with `[misc]`. If the comparison isn't field order, drop `order=True` and write the method with `functools.total_ordering`, as covered in [The data model: dunder methods as the substrate]({{ '/docs/07-the-data-model/' | relative_url }}).

## Invariants: validate in __post_init__, normalise before

The decorator can't know that a weight must be positive or a currency three capital letters. The author states those checks in `__post_init__`, and `replace` reruns them. `Money` shows the division of labour:

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

`__post_init__` reads and raises. It doesn't repair. Rounding is a decision about the input, so it belongs where the input is accepted. `Money.of("12.505", "EUR")` rounds half up to `12.51` before construction, while `Money(Decimal("12.505"), "EUR")` raises `ValueError` (`amount must be whole cents`). Nothing needs `object.__setattr__`, so the frozen guarantee stays intact.

Two more checks help callers:

- **`kw_only=True`** on `Consignment` forces keyword construction, so a transposed weight and destination can't slip through as positional arguments. The runtime raises `TypeError`, and mypy reports `<string>:5: error: Too many positional arguments for "Consignment"  [call-arg]`.
- **`replace` keywords** are checked by mypy against the class: `replace(Weight(1.0), kilos=2.0)` gets `<string>:6: error: Unexpected keyword argument "kilos" for "replace" of "Weight"  [call-arg]`.

What mypy checks and misses, in one place:

| Mistake | mypy `--strict` | Runtime |
| --- | --- | --- |
| Assigning to a frozen field | error `[misc]` | `FrozenInstanceError` |
| Positional args to a `kw_only` class | error `[call-arg]` | `TypeError` |
| Unknown field in `replace` | error `[call-arg]` | `TypeError` |
| `<` on unordered `Money` | error `[operator]` | `TypeError` |
| Mutable dataclass as a dict key | silent | `TypeError` |
| Mutable default `{}` | silent | `ValueError` at class creation |
| Weak reference to a slotted value | silent | `TypeError` |

## When not to use it

- **Lifecycle and identity.** A type with a lifecycle and an identity isn't a value. `StowagePlan` changes as slots are reserved, and two plans with equal reservations are still two plans, so it uses `eq=False`. Freezing it would force each reservation to build a new plan, which describes the wrong thing.
- **One aggregate changing in place.** A running tally with thousands of updates is a mutable object with a method, not a stream of replacements.
- **Equality that isn't field by field.** A carton that may be stowed on any face is equal to its rotation, and no field comparison says so. Write `__eq__` and a matching `__hash__` by hand; see [The data model: dunder methods as the substrate]({{ '/docs/07-the-data-model/' | relative_url }}).

> **🤖 Explore with your agent**
>
> "Write each value as `@dataclass(frozen=True, slots=True)` with immutable field types (`tuple`, `frozenset`, `Decimal`). `__post_init__` only validates and raises; normalise in a classmethod such as `Money.of` before construction. Amend with `dataclasses.replace`. Use `order=True` only where field order is the meaning, and `eq=False` for an entity such as `StowagePlan`. Add a test that puts two equal values in a set."
>
> If `__post_init__` assigns through `object.__setattr__`, ask for the normalising constructor.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/08-dataclasses-and-value-semantics
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 32 cases pass, including mypy runs over snippets that pin what it catches and misses, and mypy reports `Success: no issues found in 9 source files`. Two experiments, each in a scratch copy:

- **Remove `frozen=True` from `SlotId`.** Two tests fail with `TypeError: unhashable type: 'SlotId'`: one inside `StowagePlan.reserve`, one at `hash()` in the equality check. mypy stays green, because nothing in the type system connects `frozen` to the dictionary the plan keeps.
- **Add `order=True` to `Money`.** Two tests fail: `<` across currencies no longer raises, and the mypy snippet that expected an `[operator]` error now passes. mypy on the member adds `Unused "type: ignore" comment  [unused-ignore]`, because the ignore on the comparison has nothing left to suppress.

## What you can do now

- Say what the decorator generates: `__init__`, `__repr__`, `__eq__`, `__hash__` and the assignment guard, and that `object.__setattr__` still gets past it.
- Explain hashing: a mutable dataclass can't key a dict, and a frozen one with a `list` field can't be hashed.
- Amend a shared value with `replace`, which builds a new consignment and leaves the other booking with the old one.
- Choose value or entity: `SlotId` and `Consignment` compare by content, and `StowagePlan` with `eq=False` compares by identity.
- Place the switches: `order=True` on `SlotId` but not `Money`, `kw_only=True` on `Consignment` and `field(compare=False)` on `remarks`, and know which mistakes mypy reports.

## For deeper coverage

Martin Fowler's *Patterns of Enterprise Application Architecture* (2002) includes Value Object in its catalogue, and the [catalogue entry](https://martinfowler.com/eaaCatalog/valueObject.html) is short. Eric Evans's *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003) develops value objects and entities as modelling tools, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}).

On the Python side, Luciano Ramalho's *Fluent Python*, second edition, has a chapter on data class builders, and Brett Slatkin's *Effective Python*, third edition, has practical rules on dataclasses. Both are in the bibliography.

The language references are [PEP 557](https://peps.python.org/pep-0557/) for the design and the [`dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html) for frozen instances, `__post_init__`, `replace`, mutable default values, `slots` and `weakref_slot`, and `kw_only`.
