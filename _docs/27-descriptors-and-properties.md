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

A managed attribute is a name that runs code when it is read or written. Python's attribute lookup calls `__get__` and `__set__` for you, and `property` and `cached_property` are descriptors already written, so the language owns the mechanism. What survives as design is the choice among them: one validator per rule, shared by every field that needs it, and a clear view of where a descriptor can and can't sit. In the buckets of [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}), that design survives, and `cached_property` is where the Proxy name needs disambiguating.

The example validates weights and extents that arrive from carrier feeds. They must be finite and positive wherever they're held, and three things go wrong in the obvious versions.

A setter is copied to a third field and loses its finiteness check on the way. The copy accepts `Decimal("Infinity")`.

A dataclass is made slotted. The validator disappears and the field accepts `-1`, and mypy has no complaint.

A payload is cached because it's expensive to add up. After cargo is added following the first read, it still reports the old total.

Each one has a test below.

{% include excalidraw.html name="27-descriptors-and-properties" caption="Figure 27.1: One Positive descriptor validates six fields in three classes. A lookup tries data descriptors, then the instance dictionary, then non-data descriptors, so a cached property is read from the dictionary after its first computation." %}

Read the figure from the top down. `Positive` ("__set_name__: learns the field name", "__get__: reads the stored value", "__set__: validates, stores in vars()") has an arrow to each of three classes: `Consignment` with `kilograms`, `Dimensions` with `length_cm, width_cm, height_cm`, and `Container` with `tare_kg, max_payload_kg`. Below, under "attribute lookup on an instance", three boxes run downward: "data descriptor" (`Positive, property`), "instance __dict__" and "non-data descriptor" (`cached_property`). An arrow runs from `chargeable_kg` ("cached_property: computed on first read, then read from __dict__") into the last box. A dashed, muted box reads "slots=True" and "a slot replaces the descriptor".

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

The [builtins documentation](https://docs.python.org/3.15/builtins/functions.html) says "This makes it possible to create read-only properties easily using @property as a decorator". Assigning to `payload_kg` raises `AttributeError`, and on 3.15.2 the message is "property 'payload_kg' of 'Container' object has no setter" (`test_a_property_without_a_setter_refuses_assignment`). Nothing is stored, so the total is recomputed on each read: 100 after one load and 350 after a second (`test_payload_is_recomputed_after_each_load`). `load` accepts a consignment that brings the payload to exactly 28,000 kg and refuses one that takes it to 28,050, leaving the container's cargo unchanged (`test_load_refuses_a_consignment_over_the_max_payload`).

A setter that guards one field is a pair of `property` definitions. The comparison form is a plain class with one validating pair per extent, kept as a fixture in the tests. This is its `height_cm`:

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

The pair is correct, and it passes the same table as the descriptor version. `test_every_field_form_validates_the_same_extents` runs two forms, `Dimensions` and this class, over five rows of extents: one valid, and zero, negative, `NaN` and infinity refused. That's 10 cases, all green. The trouble is the third copy. A test-local copy of the setter that lacks `is_finite()` accepts `Decimal("Infinity")` as a height, and `Dimensions` refuses it (`test_a_copy_pasted_property_validator_drifts`). Each pair is its own code, so nothing keeps the rules in step. That's the force for a shared rule.

## A rule for many fields: a descriptor

A descriptor puts the rule in one place and lets any number of fields use it. The [Python documentation's Descriptor Guide](https://docs.python.org/3.15/howto/descriptor.html) builds its worked example around the same idea: "A validator is a descriptor for managed attribute access." `Positive` is that validator.

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

A descriptor sits in the class body, and Martin Teichmann's [PEP 487](https://peps.python.org/pep-0487/) states what that leaves it unable to do: "Descriptors are defined in the body of a class, but they do not know anything about that class, they do not even know the name they are accessed with." The PEP's remedy is `__set_name__`, which the [data model](https://docs.python.org/3.15/reference/datamodel.html) describes as "Automatically called at the time the owning class owner is created." The guide adds the limit that matters in practice: "notifications only take place at the time of class creation." It continues: "If descriptors are added to the class afterwards, __set_name__() will need to be called manually."

With the name in hand, each field gets its own message and its own storage. A valid `Dimensions` holds `_length_cm`, `_width_cm` and `_height_cm` in its instance dictionary (`test_set_name_gives_each_field_its_own_storage`). Six fields in three classes, `Consignment.kilograms`, the three extents and `Container.tare_kg` and `max_payload_kg`, are six separate instances of one class, read through `vars()` on each class (`test_one_descriptor_class_validates_every_field`). A field from each class refuses -1 on construction with its own name in the message, for example "kilograms must be positive and finite, got -1" (`test_a_positive_field_refuses_a_bad_value_on_every_class`, over `kilograms`, `height_cm`, `tare_kg` and `max_payload_kg`). Assigning zero to `tare_kg` on a built container raises and leaves the old value in place (`test_assignment_to_a_container_field_is_validated`).

The `instance is None` branch is class access. The data model says `__get__` is called with the instance "or None when the attribute is accessed through the owner". `Positive` raises there, and `Container.tare_kg` is an `AttributeError` that names the field (`test_class_access_to_a_positive_field_raises_attribute_error`). The two overloads tell mypy that class access never returns and that instance access gives a `Decimal`.

Storage goes through `vars(instance)`, where the guide's examples call `setattr`, because a frozen dataclass refuses `setattr`.

## Who wins a lookup

A descriptor and an entry in the instance dictionary can share a name, and the lookup has to pick one. This test plants a value under a field's name:

<!-- fmt:off -->
```python
    shipment = consignment(100)

    vars(shipment)["kilograms"] = Decimal(999)

    assert shipment.kilograms == Decimal(100)
```
<!-- fmt:on -->

The descriptor wins (`test_a_data_descriptor_takes_precedence_over_the_instance_dict`). The guide gives the rule: "If an instance’s dictionary has an entry with the same name as a data descriptor, the data descriptor takes precedence." A descriptor with `__set__` is a data descriptor, and so is `property`: the data model says "The @property decorator is implemented as a data descriptor." For one without `__set__`, the guide reverses the result: "the dictionary entry takes precedence". `cached_property` is that kind. The same planted entry under `chargeable_kg` is what the next read returns (`test_an_instance_dict_entry_takes_precedence_over_cached_property`).

The guide's lookup chain puts the two in order: "Instance lookup scans through a chain of namespaces giving data descriptors the highest priority, followed by instance variables, then non-data descriptors, then class variables, and lastly __getattr__() if it is provided." The figure draws the first three links. The last is the subject of [Dynamic attributes: __getattr__ and Proxy as a feature]({{ '/docs/30-dynamic-attributes-and-proxy/' | relative_url }}).

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

The [dataclasses documentation](https://docs.python.org/3.15/library/dataclasses.html) says how a default is found: "To determine whether a field contains a default value, @dataclass will call the descriptor’s __get__() method using its class access form". It continues: "If the descriptor returns a value in this case, it will be used as the field’s default. On the other hand, if the descriptor raises AttributeError in this situation, no default value will be provided for the field." That's why `Positive` raises. `fields(Dimensions)` reports no default for any of the three, and `Dimensions()` fails with "missing 3 required positional arguments" (`test_a_descriptor_field_has_no_default_when_class_access_raises`). The conventional `return self` has a cost. A test-local subclass that returns itself makes the descriptor the default, so `_Box()` builds a box by handing the descriptor to `__set__`, which fails on "has no attribute 'is_finite'" (`test_a_descriptor_that_returns_itself_on_class_access_becomes_the_default`).

Frozen is why `Positive` writes through `vars()`. A test-local subclass that stores with `setattr` makes constructing a frozen box fail with `FrozenInstanceError` and "cannot assign to field '_length_cm'" (`test_a_frozen_dataclass_refuses_a_descriptor_that_writes_with_setattr`). Assignment after construction is refused for the same reason, with "cannot assign to field 'length_cm'" (`test_a_frozen_dataclass_refuses_assignment_to_a_descriptor_field`). `dataclasses.replace` builds a new instance through `__init__`, so it validates: a width of -2 raises "width_cm must be positive and finite, got -2" (`test_replace_validates_the_new_value`). Two `Dimensions` with equal extents compare and hash equal, and one with a different height doesn't (`test_equal_dimensions_compare_and_hash_equal`).

mypy 2.4.1 reads the descriptor through `__set__`. This is the snippet in `test_mypy_types_a_positive_field_by_its_set_value`, run through the test's own `_run`; it builds `Dimensions(120, ...)` with an `int`, assigns `5` to `tare_kg` and assigns to a frozen field:

```text
<string>:6: error: Argument 1 to "Dimensions" has incompatible type "int"; expected "Decimal"  [arg-type]
<string>:8: error: Incompatible types in assignment (expression has type "int", variable has type "Decimal")  [assignment]
<string>:9: error: Property "length_cm" defined in "Dimensions" is read-only  [misc]
<string>:10: note: Revealed type is "decimal.Decimal"
```

The same checker reads `= Positive()` as a default, although `__get__` raises on class access. `Dimensions()` type-checks with exit status 0 and then raises the `TypeError` above when it runs (`test_mypy_reads_a_descriptor_field_as_a_default`). The checker accepts a call the runtime refuses.

`slots=True` removes the descriptor. The data model says "__slots__ are implemented at the class level by creating descriptors for each variable name", so a slot descriptor takes the field's place in the class. In a reduced model, a slotted dataclass with a `Positive` field is built with `Decimal(-1)` and accepts it; the class entry is a `member_descriptor`, and mypy exits 0 (`test_mypy_accepts_a_descriptor_field_on_a_slotted_dataclass`). What else `slots=True` costs is in [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}).

## cached_property: lazy initialisation without a proxy

The lazy-initialisation use of Proxy is a stand-in object that builds the real one on first use. `functools.cached_property` has the same effect with no stand-in: a value is computed on first read and then kept on the instance itself. So `cached_property` is where the Proxy name needs disambiguating. The Proxy pattern and the `@` syntax are sorted in [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}), and the buckets in [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}).

<!-- fmt:off -->
```python
    @cached_property
    def chargeable_kg(self) -> Decimal:
        """The larger of the actual weight and the volumetric weight."""
        return max(self.kilograms, self.dimensions.volume_m3 * VOLUMETRIC_KG_PER_M3)
```
<!-- fmt:on -->

The [functools documentation](https://docs.python.org/3.15/library/functools.html) describes a property "whose value is computed once and then cached as a normal attribute for the life of the instance", and adds that the decorator "only runs on lookups and only when an attribute of the same name doesn’t exist." Before the first read, `chargeable_kg` isn't in `vars(shipment)`. After it, the computed value is (`test_chargeable_weight_is_computed_on_first_access_and_stored`). The value is the larger of actual and volumetric weight at 167 kg per cubic metre, an illustrative factor: 160.32 for a 100 kg consignment of 120 by 80 by 100 cm, and 250 for one that weighs 250 kg (`test_chargeable_weight_is_the_larger_of_actual_and_volumetric_weight`). `replace` makes a new instance whose dictionary holds no cached value, so the value is computed again: 300 for a consignment replaced at 300 kg, after 160.32 for the original (`test_replace_recomputes_the_chargeable_weight`).

The cache lives in the instance dictionary, and it has four costs.

- It needs the dictionary. The page says the decorator "requires that the __dict__ attribute on each instance be a mutable mapping". A class whose slots leave out `__dict__` has none, and the read raises `TypeError` with "No '__dict__' attribute" (`test_cached_property_needs_an_instance_dict`, on a test-local slotted class). mypy accepts the same decorator on a slotted dataclass in a reduced model, and the runtime then raises (`test_mypy_accepts_cached_property_on_a_slotted_dataclass`).
- A frozen class can't clear it. The page says "The cached value can be cleared by deleting the attribute." A frozen dataclass refuses the `del` with "cannot delete field 'chargeable_kg'" (`test_a_frozen_dataclass_cannot_clear_a_cached_property`). On `Consignment` that is fine, because the inputs can't change.
- Over mutable state it goes stale. A test-local `Container` subclass that caches `payload_kg` reads 100 after cargo is added following its first read, where the live container reads 350 (`test_a_cached_property_over_mutable_state_goes_stale`). `payload_kg` is a `property` for this reason.
- Two threads can both run the getter. What's New in 3.12 records the lock's removal: "a cached property getter function could now run more than once for a single instance, if two threads race". A `Barrier` makes two readers meet inside the getter: both run it, both get 2, the getter has run twice, and a third read after both threads have finished doesn't run it again (`test_a_cached_property_getter_can_run_twice_under_threads`). Nothing in this member shares a consignment between threads.

The functools page offers an alternative: "If a mutable mapping is not available or if space-efficient key sharing is desired, an effect similar to @cached_property can also be achieved by stacking @property on top of @lru_cache." What a cache on a method keeps alive is the subject of [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}).

## When not to use it

Skip the descriptor when one field in one class needs a rule: a `property` pair is shorter, and it passes the same table. A frozen value type that's validated once at construction needs neither, because `__post_init__` runs the check ([Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers it). A value derived from state that changes belongs to a `property`, not `cached_property`. A dataclass with `slots=True` takes no `Positive` field and no `cached_property`.

<blockquote class="ai-sidebar" markdown="1">
**Specifying managed attributes.** "Validate the weights" leaves open where the rule lives, whether the classes are slotted and which values are cached. State the forms in the prompt:

> Validate every positive `Decimal` field with one `Positive` descriptor that learns its name in `__set_name__`, raises `AttributeError` on class access and stores through `vars(instance)`, on dataclasses without `slots=True`. Use `@property` for a value computed from state that changes, and `functools.cached_property` only on a frozen class. Don't copy a validating setter from one property to another.

If the reply adds `slots=True` or a setter per field, ask for the test that fails.
</blockquote>

## Build, run, observe

The run shows the descriptor and the property twin on one table, and each rule failing when its code changes. From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/27-descriptors-and-properties
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
collecting ... collected 43 items

tests/test_cached.py::test_chargeable_weight_is_computed_on_first_access_and_stored PASSED [  2%]
tests/test_cached.py::test_chargeable_weight_is_the_larger_of_actual_and_volumetric_weight[bulky] PASSED [  4%]
tests/test_cached.py::test_chargeable_weight_is_the_larger_of_actual_and_volumetric_weight[heavy] PASSED [  6%]
tests/test_cached.py::test_cached_property_needs_an_instance_dict PASSED [  9%]
tests/test_cached.py::test_a_frozen_dataclass_cannot_clear_a_cached_property PASSED [ 11%]
tests/test_cached.py::test_replace_recomputes_the_chargeable_weight PASSED [ 13%]
tests/test_cached.py::test_a_cached_property_over_mutable_state_goes_stale PASSED [ 16%]
tests/test_cached.py::test_a_cached_property_getter_can_run_twice_under_threads PASSED [ 18%]
tests/test_dataclasses.py::test_a_descriptor_field_has_no_default_when_class_access_raises PASSED [ 20%]
tests/test_dataclasses.py::test_a_descriptor_that_returns_itself_on_class_access_becomes_the_default PASSED [ 23%]
tests/test_dataclasses.py::test_a_frozen_dataclass_refuses_a_descriptor_that_writes_with_setattr PASSED [ 25%]
tests/test_dataclasses.py::test_a_frozen_dataclass_refuses_assignment_to_a_descriptor_field PASSED [ 27%]
tests/test_dataclasses.py::test_replace_validates_the_new_value PASSED   [ 30%]
tests/test_dataclasses.py::test_equal_dimensions_compare_and_hash_equal PASSED [ 32%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-valid] PASSED [ 34%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-length-zero] PASSED [ 37%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-width-negative] PASSED [ 39%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-height-nan] PASSED [ 41%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-height-infinity] PASSED [ 44%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[property-valid] PASSED [ 46%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[property-length-zero] PASSED [ 48%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[property-width-negative] PASSED [ 51%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[property-height-nan] PASSED [ 53%]
tests/test_fields.py::test_every_field_form_validates_the_same_extents[property-height-infinity] PASSED [ 55%]
tests/test_fields.py::test_a_positive_field_refuses_a_bad_value_on_every_class[consignment-kilograms] PASSED [ 58%]
tests/test_fields.py::test_a_positive_field_refuses_a_bad_value_on_every_class[dimensions-height_cm] PASSED [ 60%]
tests/test_fields.py::test_a_positive_field_refuses_a_bad_value_on_every_class[container-tare_kg] PASSED [ 62%]
tests/test_fields.py::test_a_positive_field_refuses_a_bad_value_on_every_class[container-max_payload_kg] PASSED [ 65%]
tests/test_fields.py::test_assignment_to_a_container_field_is_validated PASSED [ 67%]
tests/test_fields.py::test_set_name_gives_each_field_its_own_storage PASSED [ 69%]
tests/test_fields.py::test_one_descriptor_class_validates_every_field PASSED [ 72%]
tests/test_fields.py::test_a_copy_pasted_property_validator_drifts PASSED [ 74%]
tests/test_fields.py::test_a_property_without_a_setter_refuses_assignment PASSED [ 76%]
tests/test_fields.py::test_payload_is_recomputed_after_each_load PASSED  [ 79%]
tests/test_fields.py::test_load_refuses_a_consignment_over_the_max_payload[at-the-limit] PASSED [ 81%]
tests/test_fields.py::test_load_refuses_a_consignment_over_the_max_payload[over] PASSED [ 83%]
tests/test_lookup.py::test_a_data_descriptor_takes_precedence_over_the_instance_dict PASSED [ 86%]
tests/test_lookup.py::test_an_instance_dict_entry_takes_precedence_over_cached_property PASSED [ 88%]
tests/test_lookup.py::test_class_access_to_a_positive_field_raises_attribute_error PASSED [ 90%]
tests/test_static.py::test_mypy_types_a_positive_field_by_its_set_value PASSED [ 93%]
tests/test_static.py::test_mypy_reads_a_descriptor_field_as_a_default PASSED [ 95%]
tests/test_static.py::test_mypy_accepts_cached_property_on_a_slotted_dataclass PASSED [ 97%]
tests/test_static.py::test_mypy_accepts_a_descriptor_field_on_a_slotted_dataclass PASSED [100%]

============================== 43 passed in 1.77s ==============================
Success: no issues found in 9 source files
```

The suite has 29 test functions and 43 cases. For how the mypy tests are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

- `tests/test_fields.py` holds the `field_form` table, the four-class refusal test and the property tests.
- `tests/test_lookup.py` and `tests/test_dataclasses.py` hold the precedence tests and the dataclass rules.
- `tests/test_cached.py` holds `cached_property`, including the stale and thread tests.
- `tests/test_static.py` holds the mypy tests: two on `src` types and two reduced models of a slotted class.

**Experiment one: store with `setattr`.** In a fresh scratch copy, change the last line of `Positive.__set__` to `setattr(instance, self.private_name, value)`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|[0-9]+ (passed|failed))|^E +[^ ]' | sed -E 's/^E +/E /; s/^(FAILED [^ ]+) - .*/\1/' | sort | uniq -c` and then `uv run mypy --strict src tests` prints:

```text
      1 7 failed, 21 passed, 15 errors in 1.80s
     22 E dataclasses.FrozenInstanceError: cannot assign to field '_length_cm'
      1 FAILED tests/test_fields.py::test_a_copy_pasted_property_validator_drifts
      1 FAILED tests/test_fields.py::test_a_positive_field_refuses_a_bad_value_on_every_class[consignment-kilograms]
      1 FAILED tests/test_fields.py::test_a_positive_field_refuses_a_bad_value_on_every_class[dimensions-height_cm]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-height-infinity]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-height-nan]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-valid]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-width-negative]
Success: no issues found in 9 source files
```

Seven tests fail and fifteen more error in fixture setup, because the fixtures build frozen `Dimensions`. Each reports the same message, which names `_length_cm` because that extent is assigned first. Tests that build no `Dimensions` still pass, and mypy exits 0.

**Experiment two: slot `Dimensions`.** In a fresh scratch copy, change the decorator on `Dimensions` to `@dataclass(frozen=True, slots=True)`. The same filter, then mypy, prints:

```text
      1 9 failed, 34 passed in 1.92s
      1 E AssertionError: assert ['Positive', ...', 'Positive'] == ['Positive', ...', 'Positive']
      1 E At index 1 diff: 'member_descriptor' != 'Positive'
      7 E Failed: DID NOT RAISE ValueError
      1 E TypeError: vars() argument must have __dict__ attribute
      1 E Use -v to get more diff
      1 FAILED tests/test_dataclasses.py::test_replace_validates_the_new_value
      1 FAILED tests/test_fields.py::test_a_copy_pasted_property_validator_drifts
      1 FAILED tests/test_fields.py::test_a_positive_field_refuses_a_bad_value_on_every_class[dimensions-height_cm]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-height-infinity]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-height-nan]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-length-zero]
      1 FAILED tests/test_fields.py::test_every_field_form_validates_the_same_extents[descriptor-width-negative]
      1 FAILED tests/test_fields.py::test_one_descriptor_class_validates_every_field
      1 FAILED tests/test_fields.py::test_set_name_gives_each_field_its_own_storage
Success: no issues found in 9 source files
```

Nine tests fail. Seven report `DID NOT RAISE ValueError`, because the slot replaced the descriptor and nothing checks the value. `test_set_name_gives_each_field_its_own_storage` fails on `vars()`, which needs a `__dict__` the slotted class lacks. `test_one_descriptor_class_validates_every_field` finds `member_descriptor` at index 1 of its list, the `length_cm` entry, where it expects `Positive`. No `Consignment` test fails, and mypy exits 0.

## What you can do now

- Choose the form for an attribute: `payload_kg` as a read-only `property`, where `test_a_property_without_a_setter_refuses_assignment` shows the refusal and the descriptor shares a table with the property twin.
- Write a validating descriptor: `Positive`, with `__set_name__` giving each field its own name, as `test_one_descriptor_class_validates_every_field` shows across three classes.
- Predict a lookup: a data descriptor beats the instance dictionary and the dictionary beats `cached_property`, as `test_an_instance_dict_entry_takes_precedence_over_cached_property` shows.
- Put a descriptor on a dataclass: `Dimensions`, frozen and unslotted, with `test_mypy_accepts_a_descriptor_field_on_a_slotted_dataclass` showing what `slots=True` does to it, `test_mypy_types_a_positive_field_by_its_set_value` showing the types, and experiment two showing the tests that notice.
- Cache without a proxy: `chargeable_kg`, with `test_a_cached_property_over_mutable_state_goes_stale` showing why `payload_kg` isn't cached.

## For deeper coverage

The [Descriptor Guide](https://docs.python.org/3.15/howto/descriptor.html) is the primary source, and the data model's sections on implementing descriptors and `__slots__` complete it. Guido van Rossum's [PEP 252](https://peps.python.org/pep-0252/) introduced descriptors, and Martin Teichmann's [PEP 487](https://peps.python.org/pep-0487/) added `__set_name__`. The [functools](https://docs.python.org/3.15/library/functools.html), [dataclasses](https://docs.python.org/3.15/library/dataclasses.html) and [builtins](https://docs.python.org/3.15/builtins/functions.html) pages cover `cached_property`, descriptor-typed fields and `property`, and [What's New in 3.12](https://docs.python.org/3.15/whatsnew/3.12.html) records the lock removal. Brandon Rhodes's [The Factory Method Pattern](https://python-patterns.guide/gang-of-four/factory-method/) covers the instance-over-class rule. Luciano Ramalho's *Fluent Python*, second edition, treats descriptors in its metaprogramming material. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
