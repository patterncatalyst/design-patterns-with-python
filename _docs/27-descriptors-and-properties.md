---
title: "Descriptors and properties"
order: 27
layout: tutorial
sectionid: docs
part: "idiomatic-python"
description: "One validator, written once, guarding every field that needs it, and when a plain property or a cached one is the better tool."
---

## Learning objectives

By the end of this chapter you can:

- Choose between `property`, a descriptor and `cached_property` for an attribute.
- Write a validating descriptor that learns its field name with `__set_name__`.
- Predict whether a descriptor or an entry in the instance dictionary wins a lookup.
- Put a descriptor on a dataclass and type it for mypy.
- Cache a computed value without a proxy, and say when it goes stale.

## Why this matters

A managed attribute is a name that runs code when it's read or written. Python's attribute lookup calls `__get__` and `__set__` for you, and `property` and `cached_property` are descriptors already written, so the language owns the mechanism. What survives as design is the choice among them. In the buckets of [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}), that design survives, and `cached_property` is where the Proxy name needs disambiguating.

Weights and extents arrive from carrier feeds and must be finite and positive wherever they're held. The obvious versions fail three ways:

- A setter is copied to a third field and loses its finiteness check. The copy accepts `Decimal("Infinity")`.
- A dataclass is made slotted. The validator disappears, the field accepts `-1`, and mypy has no complaint.
- A payload is cached because it's expensive to add up. After more cargo is loaded, it still reports the old total.

{% include excalidraw.html name="27-descriptors-and-properties" described="true" caption="Figure 27.1: One Positive descriptor validates six fields in three classes. A lookup tries data descriptors, then the instance dictionary, then non-data descriptors, so a cached property is read from the dictionary after its first computation." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-27-descriptors-and-properties" markdown="1">
From the top down, `Positive` ("__set_name__: learns the field name", "__get__: reads the stored value", "__set__: validates, stores in vars()") has an arrow to each of three classes: `Consignment` with `kilograms`, `Dimensions` with `length_cm, width_cm, height_cm`, and `Container` with `tare_kg, max_payload_kg`. Below, under "attribute lookup on an instance", three boxes run downward: "data descriptor" (`Positive, property`), "instance __dict__" and "non-data descriptor" (`cached_property`). An arrow runs from `chargeable_kg` ("cached_property: computed on first read, then read from __dict__") into the last box. A dashed, muted box reads "slots=True" and "a slot replaces the descriptor".
</div>
</details>

The figure shows one descriptor shared by three classes above the order in which a lookup consults descriptors and the instance dictionary.

## One attribute: property

A `property` is the right tool for one attribute: a value computed from other state, or a setter that guards one field. `Container.payload_kg` is the first kind.

<!-- fmt:off -->
```python
    @property
    def payload_kg(self) -> Decimal:
        return sum((c.kilograms for c in self.consignments), Decimal(0))

    def load(self, consignment: Consignment) -> None:
        if self.payload_kg + consignment.kilograms > self.max_payload_kg:
            raise ContainerError(
                f"{consignment.id} would exceed {self.max_payload_kg} kg in {self.number}"
            )
        self.consignments.append(consignment)
```
<!-- fmt:on -->

The [builtins documentation](https://docs.python.org/3/builtins/functions.html) says "This makes it possible to create read-only properties easily using @property as a decorator". Assigning to `payload_kg` raises `AttributeError`, and on 3.15.2 the message is "property 'payload_kg' of 'Container' object has no setter". Nothing is stored, so the total is recomputed on each read: 100 after one load and 350 after a second. `load` accepts a consignment that brings the payload to exactly 28,000 kg and refuses one that takes it to 28,050, leaving the cargo unchanged.

A setter that guards one field is a pair of `property` definitions. Here's the `height_cm` of a plain class with one validating pair per extent:

<!-- fmt:off -->
```python
    @property
    def height_cm(self) -> Decimal:
        return self._height_cm

    @height_cm.setter
    def height_cm(self, value: Decimal) -> None:
        if not value.is_finite() or value <= 0:
            raise ValueError(f"height_cm must be positive and finite, got {value}")
        self._height_cm = value
```
<!-- fmt:on -->

The pair is correct, and it validates the same extents as the descriptor version: one valid row, and zero, negative, `NaN` and infinity refused. The trouble is the third copy. A copy of the setter that lacks `is_finite()` accepts `Decimal("Infinity")` as a height, where `Dimensions` refuses it. Each pair is its own code, so nothing keeps the rules in step. That's the force for a shared rule.

## A rule for many fields: a descriptor

A descriptor puts the rule in one place and lets any number of fields use it. The [Descriptor Guide](https://docs.python.org/3/howto/descriptor.html) builds its worked example around the same idea: "A validator is a descriptor for managed attribute access." `Positive` is that validator.

<!-- fmt:off -->
```python
    public_name: str
    private_name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type) -> Never: ...

    @overload
    def __get__(self, instance: object, owner: type) -> Decimal: ...

    def __get__(self, instance: object | None, owner: type) -> Decimal:
        if instance is None:
            raise AttributeError(self.public_name)
        value: Decimal = vars(instance)[self.private_name]
        return value

    def __set__(self, instance: object, value: Decimal) -> None:
        if not value.is_finite() or value <= 0:
            raise ValueError(f"{self.public_name} must be positive and finite, got {value}")
        vars(instance)[self.private_name] = value
```
<!-- fmt:on -->

A descriptor sits in the class body, and Martin Teichmann's [PEP 487](https://peps.python.org/pep-0487/) states what that leaves it unable to do: "Descriptors are defined in the body of a class, but they do not know anything about that class, they do not even know the name they are accessed with." The PEP's remedy is `__set_name__`, which the [data model](https://docs.python.org/3/reference/datamodel.html) describes as "Automatically called at the time the owning class owner is created." The guide adds the limit: "notifications only take place at the time of class creation." It continues: "If descriptors are added to the class afterwards, __set_name__() will need to be called manually."

With the name in hand, each field gets its own message and its own storage:

- A valid `Dimensions` holds `_length_cm`, `_width_cm` and `_height_cm` in its instance dictionary.
- Six fields in three classes (`Consignment.kilograms`, the three extents, and `Container.tare_kg` and `max_payload_kg`) are six instances of one class.
- Each refuses -1 on construction with its own name in the message, for example "kilograms must be positive and finite, got -1".
- Assigning zero to `tare_kg` on a built container raises and leaves the old value in place.

The `instance is None` branch is class access. The data model says `__get__` is called with the instance "or None when the attribute is accessed through the owner". `Positive` raises there, so `Container.tare_kg` is an `AttributeError` that names the field. The two overloads tell mypy that class access never returns and that instance access gives a `Decimal`.

Storage goes through `vars(instance)`, where the guide's examples call `setattr`, because a frozen dataclass refuses `setattr`.

## Who wins a lookup

A descriptor and an entry in the instance dictionary can share a name, and the lookup has to pick one. Plant `vars(shipment)["kilograms"] = Decimal(999)` on a 100 kg consignment, and `shipment.kilograms` still reads 100.

The guide gives the rule: "If an instance’s dictionary has an entry with the same name as a data descriptor, the data descriptor takes precedence." A descriptor with `__set__` is a data descriptor, and so is `property`: the data model says "The @property decorator is implemented as a data descriptor." For one without `__set__`, the guide reverses the result: "the dictionary entry takes precedence". `cached_property` is that kind, so an entry planted under `chargeable_kg` is what the next read returns.

| Descriptor | Has `__set__` | Against an instance dictionary entry |
| --- | --- | --- |
| `Positive`, `property` | yes (data) | the descriptor wins |
| `cached_property` | no (non-data) | the dictionary entry wins |

The guide's lookup chain puts them in order: "Instance lookup scans through a chain of namespaces giving data descriptors the highest priority, followed by instance variables, then non-data descriptors, then class variables, and lastly __getattr__() if it is provided." The last link is the subject of [Dynamic attributes: __getattr__ and Proxy as a feature]({{ '/docs/30-dynamic-attributes-and-proxy/' | relative_url }}).

For an ordinary class attribute the order is the one Brandon Rhodes states on his page [The Factory Method Pattern](https://python-patterns.guide/gang-of-four/factory-method/): "the instance attribute wins". A data descriptor is the exception.

## Descriptors in a dataclass

A dataclass generates `__init__` from its annotated fields, and a field whose default is a descriptor gets special treatment. `Dimensions` is frozen, with three `Positive` fields.

```python
@dataclass(frozen=True)
class Dimensions:
    """Package extents in centimetres.

    Not slotted: a slot would replace each ``Positive`` field and accept any value.
    """

    length_cm: Positive = Positive()
    width_cm: Positive = Positive()
    height_cm: Positive = Positive()

    @property
    def volume_m3(self) -> Decimal:
        return self.length_cm * self.width_cm * self.height_cm / 1_000_000
```

The [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) says how a default is found: "To determine whether a field contains a default value, @dataclass will call the descriptor’s __get__() method using its class access form". It continues: "If the descriptor returns a value in this case, it will be used as the field’s default. On the other hand, if the descriptor raises AttributeError in this situation, no default value will be provided for the field." That's why `Positive` raises. `fields(Dimensions)` reports no default for any of the three, and `Dimensions()` fails with "missing 3 required positional arguments". The conventional `return self` makes the descriptor the default, so a bare constructor hands the descriptor to `__set__`, which fails on "has no attribute 'is_finite'".

Frozen is why `Positive` writes through `vars()`:

| Operation on a frozen `Dimensions` | Result |
| --- | --- |
| a descriptor that stores with `setattr` | `FrozenInstanceError`, "cannot assign to field '_length_cm'" |
| assignment after construction | `FrozenInstanceError`, "cannot assign to field 'length_cm'" |
| `dataclasses.replace(..., width_cm=Decimal(-2))` | validated through `__init__`: "width_cm must be positive and finite, got -2" |
| two with equal extents | compare and hash equal |

mypy reads the descriptor through `__set__`. Building `Dimensions(120, ...)` with an `int`, assigning `5` to `tare_kg` and assigning to a frozen field give:

```text
<string>:6: error: Argument 1 to "Dimensions" has incompatible type "int"; expected "Decimal"  [arg-type]
<string>:8: error: Incompatible types in assignment (expression has type "int", variable has type "Decimal")  [assignment]
<string>:9: error: Property "length_cm" defined in "Dimensions" is read-only  [misc]
<string>:10: note: Revealed type is "decimal.Decimal"
```

mypy also reads `= Positive()` as a default, although `__get__` raises on class access. `Dimensions()` type-checks and then raises the `TypeError` above when it runs: the checker accepts a call the runtime refuses.

`slots=True` removes the descriptor. The data model says "__slots__ are implemented at the class level by creating descriptors for each variable name", so a slot descriptor takes the field's place in the class. A slotted dataclass with a `Positive` field accepts `Decimal(-1)`, the class entry is a `member_descriptor`, and mypy accepts it. What else `slots=True` costs is in [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}).

## cached_property: lazy initialisation without a proxy

The lazy-initialisation use of Proxy is a stand-in object that builds the real one on first use. `functools.cached_property` has the same effect with no stand-in: a value is computed on first read and then kept on the instance itself. The Proxy pattern and the `@` syntax are sorted in [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}).

<!-- fmt:off -->
```python
    @cached_property
    def chargeable_kg(self) -> Decimal:
        """The larger of the actual weight and the volumetric weight."""
        return max(self.kilograms, self.dimensions.volume_m3 * VOLUMETRIC_KG_PER_M3)
```
<!-- fmt:on -->

The [functools documentation](https://docs.python.org/3/library/functools.html) describes a property "whose value is computed once and then cached as a normal attribute for the life of the instance", and adds that the decorator "only runs on lookups and only when an attribute of the same name doesn’t exist." Before the first read, `chargeable_kg` isn't in `vars(shipment)`, and after it the computed value is. The value is the larger of actual and volumetric weight at 167 kg per cubic metre, an illustrative factor: 160.32 for a 100 kg consignment of 120 by 80 by 100 cm, and 250 for one that weighs 250 kg. `replace` makes a new instance with no cached value, so a consignment replaced at 300 kg reads 300.

The cache lives in the instance dictionary, and it has four costs:

- **It needs the dictionary.** The page says the decorator "requires that the __dict__ attribute on each instance be a mutable mapping". On a class whose slots leave out `__dict__`, the read raises `TypeError` with "No '__dict__' attribute". mypy accepts the same decorator on a slotted dataclass.
- **A frozen class can't clear it.** The page says "The cached value can be cleared by deleting the attribute." A frozen dataclass refuses the `del` with "cannot delete field 'chargeable_kg'". On `Consignment` that's fine, because the inputs can't change.
- **Over mutable state it goes stale.** A container that caches `payload_kg` reads 100 after more cargo is loaded, where the live container reads 350. `payload_kg` is a `property` for this reason.
- **Two threads can both run the getter.** What's New in 3.12 records the lock's removal: "a cached property getter function could now run more than once for a single instance, if two threads race". With a `Barrier` holding two readers inside the getter, both run it and both get the same value; a later read doesn't run it again. Nothing here shares a consignment between threads.

The functools page offers an alternative: "If a mutable mapping is not available or if space-efficient key sharing is desired, an effect similar to @cached_property can also be achieved by stacking @property on top of @lru_cache." What a cache on a method keeps alive is covered in [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}).

## When not to use it

- **One field in one class.** Skip the descriptor: a `property` pair is shorter and validates the same values.
- **Validated once.** A frozen value type that's validated once at construction needs neither, because `__post_init__` runs the check ([Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers it).
- **Changing state.** A value derived from state that changes belongs to a `property`, not `cached_property`.
- **Slots.** A dataclass with `slots=True` takes no `Positive` field and no `cached_property`.

> **🤖 Explore with your agent**
>
> "Validate every positive `Decimal` field with one `Positive` descriptor that learns its name in `__set_name__`, raises `AttributeError` on class access and stores through `vars(instance)`, on dataclasses without `slots=True`. Use `@property` for a value computed from state that changes, and `functools.cached_property` only on a frozen class. Don't copy a validating setter from one property to another."
>
> If the reply adds `slots=True` or a setter per field, ask for the test that fails.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/27-descriptors-and-properties
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 43 cases pass and mypy is clean. For how the mypy checks run from pytest, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}). Two experiments:

- **Store with `setattr`.** In a scratch copy, change the last line of `Positive.__set__` to `setattr(instance, self.private_name, value)`. Seven tests fail and fifteen error in setup, all with `FrozenInstanceError: cannot assign to field '_length_cm'`, because every frozen `Dimensions` now refuses construction. mypy stays green.
- **Slot `Dimensions`.** In a scratch copy, change its decorator to `@dataclass(frozen=True, slots=True)`. Nine tests fail: seven with `DID NOT RAISE ValueError`, because the slot replaced the descriptor, one on `vars()`, which needs a `__dict__`, and one that finds `member_descriptor` where it expects `Positive`. mypy stays green.

## What you can do now

- Choose the form for an attribute: `payload_kg` as a read-only `property`, a `property` pair for one guarded field, and a descriptor for a rule many fields share.
- Write a validating descriptor: `Positive`, with `__set_name__` giving each of six fields in three classes its own name and storage.
- Predict a lookup: a data descriptor beats the instance dictionary, and the dictionary beats `cached_property`.
- Put a descriptor on a dataclass: `Dimensions`, frozen and unslotted, typed by `__set__` for mypy.
- Cache without a proxy with `chargeable_kg`, and keep `payload_kg` a `property` because its state changes.

## For deeper coverage

The [Descriptor Guide](https://docs.python.org/3/howto/descriptor.html) is the primary source, and the data model's sections on implementing descriptors and `__slots__` complete it. Guido van Rossum's [PEP 252](https://peps.python.org/pep-0252/) introduced descriptors, and Martin Teichmann's [PEP 487](https://peps.python.org/pep-0487/) added `__set_name__`. The [functools](https://docs.python.org/3/library/functools.html), [dataclasses](https://docs.python.org/3/library/dataclasses.html) and [builtins](https://docs.python.org/3/builtins/functions.html) pages cover `cached_property`, descriptor-typed fields and `property`, and [What's New in 3.12](https://docs.python.org/3/whatsnew/3.12.html) records the lock removal. Brandon Rhodes's [The Factory Method Pattern](https://python-patterns.guide/gang-of-four/factory-method/) covers the instance-over-class rule. Luciano Ramalho's *Fluent Python*, second edition, treats descriptors in its metaprogramming material. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
