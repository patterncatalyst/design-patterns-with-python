---
title: "Composite and Flyweight"
order: 21
layout: tutorial
sectionid: docs
part: "composing-adapting-structure"
description: "A consignment and a consolidation of consignments answer the same question through a closed union, and a flyweight pool shares one frozen commodity among them while deciding who builds it and how long it lives."
---

## Learning objectives

By the end of this chapter you can:

- Model a tree as a closed union with one shared attribute, and say which part of Composite dissolves.
- Compute a total that recurses through nested groups, and use `match` with `assert_never` where the two kinds differ.
- Name the invariants a tree keeps (no empty group, no consignment twice) and build the tree so they hold.
- Build a flyweight pool, choose how long its values live, and say why a frozen value makes sharing safe.
- Read recorded memory figures for slots, sharing and interning, and say why `sys.getsizeof` misleads.
- Intern port codes with `sys.intern`, knowing equality works without it.

## Why this matters

A consolidation puts several consignments under one booking, and a consolidation can sit inside another. A caller asks it for a weight and doesn't want to know how deep the nesting goes. Meanwhile the same few commodities can repeat across many consignments, and each repetition costs an object. Both patterns survive in Python: Composite because the shape of the tree is still a design decision, Flyweight because identity and lifetime are. What Python removes is machinery, the Component base class and the factory class.

Three things go wrong in the obvious versions.

A total sums the consignments directly under a consolidation and skips the nested one. The fixture's groups hold 23.75 kg, and the flat sum reports 17.25.

A consignment sits in two groups of one consolidation and is counted twice. Nothing in the weight arithmetic notices.

One commodity object is shared by all the consignments that carry it, and one consignment's line edits it. The other consignments see the change, because they hold the same object.

{% include excalidraw.html name="21-composite-and-flyweight" caption="Figure 21.1: One weight question, one shared commodity. A consolidation answers weight as a consignment does, summing its parts through nested groups; consignments reach a single frozen commodity per code from a pool that lets go of commodities nobody holds." %}

The figure has a top `ConsolidatedShipment` ("weight: sums its parts, nested or not") with two children: a `Consignment` and a second, nested `ConsolidatedShipment` ("a nested group, same question") that holds two more. All three `Consignment` leaves point to one `Commodity` ("one object per code, frozen"), and `CommodityPool` ("weak values: dropped when nobody holds them") points up to it. At the side, a note reads "Shipment = Consignment | ConsolidatedShipment", and a separate `port_code` box reads "sys.intern: one object per code". Port codes are the other shared value, and they have no arrow into the tree because a consignment holds them as plain strings.

## One question for a consignment and a consolidation

Composite is for the caller who holds something and asks one question without caring whether it's a single item or a bundle of them. The *Design Patterns* catalogue by Gamma, Helm, Johnson and Vlissides (1994) gives it to part-whole structures. Brandon Rhodes, in [The Composite Pattern](https://python-patterns.guide/gang-of-four/composite/), treats the pattern as symmetry between containers and contents and writes that "The art of using the Composite Pattern is determining where to break the symmetry." In Python he lets any mechanism supply that symmetry, whether a base class, a type checker or duck typing. That's the part that dissolves here. [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) lists the assumptions behind the base class. The decisions that remain are what both kinds answer, where the total is computed and which invariants hold, so the bucket is survives.

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True)
class ConsolidatedShipment:
    """A group: consignments, or smaller consolidations, carried together.

    Built bottom-up, so its parts exist before it does and cannot be rewired afterwards.
    """

    id: str
    parts: tuple[Shipment, ...]

    def __post_init__(self) -> None:
        if not self.parts:
            raise ConsolidationError(f"consolidation {self.id} needs at least one part")
        seen: set[ConsignmentId] = set()
        for part in self.parts:
            for consignment_id in _consignment_ids(part):
                if consignment_id in seen:
                    raise ConsolidationError(
                        f"consignment {consignment_id} appears twice in consolidation {self.id}"
                    )
                seen.add(consignment_id)

    @property
    def weight(self) -> Weight:
        """The total, recursing through nested consolidations."""
        return reduce(operator.add, (part.weight for part in self.parts))


type Shipment = Consignment | ConsolidatedShipment
```
<!-- fmt:on -->

The uniform question is `.weight`. A `Consignment` stores it and a `ConsolidatedShipment` computes it from its parts, so the total is calculated on demand at the group and nowhere else. `test_a_consignment_and_a_consolidation_answer_weight_the_same_way` passes both kinds through one function with no `isinstance`, and `test_the_total_weight_includes_nested_consolidations` gets 23.75 kg from the nested fixture. `test_a_flat_sum_misses_nested_consolidations` keeps the first failure from the start of the chapter on record: the flat sum is 17.25 kg against the total of 23.75 kg.

The union is closed, and mypy reads it. `test_mypy_reads_weight_on_either_kind_of_shipment` type-checks `shipment.weight` on a `Shipment` with exit status 0 and no output. `test_mypy_refuses_parts_on_a_shipment_that_may_be_a_consignment` shows the other side: `.parts` exists on only one kind, so mypy reports `[union-attr]`.

## Where the kinds differ: match over a closed union

Rhodes names the limit on symmetry: "The question of return type will serve as a very important guardrail when you are designing in Python". Flattening is a case where the kinds differ in what they do but return one type, a tuple of consignments, so no caller needs `isinstance`:

<!-- fmt:off -->
```python
def consignments(shipment: Shipment) -> tuple[Consignment, ...]:
    """Every consignment beneath a shipment, depth first, in order."""
    match shipment:
        case Consignment():
            return (shipment,)
        case ConsolidatedShipment():
            return tuple(c for part in shipment.parts for c in consignments(part))
        case _ as unreachable:
            assert_never(unreachable)
```
<!-- fmt:on -->

`test_consignments_lists_every_leaf_in_order` expects CN-1, CN-3, CN-4, CN-2 from the fixture, and `test_a_consolidation_with_dangerous_goods_anywhere_is_flagged` runs `carries_dangerous_goods`, which is built on `consignments`, for a hit at the top level, a hit in a nested group and no hit.

The last arm is the safety. A kind with no arm leaves `unreachable` typed as something other than `Never`, and `assert_never` takes an argument of type `Never`. `test_mypy_reports_a_missing_match_arm` removes the `ConsolidatedShipment` arm in a snippet and gets `[arg-type]` with `expected "Never"`. `test_mypy_refuses_a_part_that_is_not_a_shipment` puts a `Weight` in `parts` and gets `[arg-type]` too. This form suits a domain that names its kinds. For kinds that other code adds, [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers interfaces without a base class.

## Invariants: built bottom-up, frozen, counted once

The tree's invariants are the part of Composite that no language feature supplies. This one has three. A consolidation needs at least one part (`test_a_consolidation_must_have_parts`). A consignment appears once, at the same level or nested below another group (`test_a_consignment_may_appear_only_once_in_a_consolidation`, both placements). Weights are positive and finite (`test_weight_refuses_zero_negative_and_non_finite_values`, for zero, negative, NaN and infinity).

The other protection is construction order. Parts are passed as a tuple of objects that already exist, and the dataclass is frozen, so `test_a_frozen_consolidation_cannot_be_rewired` finds `FrozenInstanceError` on assignment and a tuple in `parts`. mypy refuses `add`, `append` and assignment on a group (`test_mypy_refuses_adding_to_a_frozen_consolidation`, three cases). Two trees built separately from the same data compare equal and hash equal (`test_consolidations_compare_by_value`); [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers frozen and hash. Recursion has a limit: `test_a_pathologically_deep_consolidation_hits_the_recursion_limit` assembles a 5,000-level tree and gets `RecursionError` on `.weight`. The domain nests a few levels.

For contrast, here is the mutable form the original catalogue describes, kept as a test fixture that passes the same weight table as the frozen form (`test_the_total_weight_includes_nested_consolidations`, parametrised over `frozen-union` and `component-classes`).

<!-- fmt:off -->
```python
# Comparison: the GoF form, a base class that declares the child operations for every component.
# A leaf inherits `add` and refuses it only when the program runs.
class _Component(ABC):
    @abstractmethod
    def weight(self) -> Decimal: ...

    def add(self, component: _Component, /) -> None:
        raise TypeError(f"{type(self).__name__} cannot hold components")


class _ComponentLeaf(_Component):
    def __init__(self, kilograms: Decimal) -> None:
        self._kilograms = kilograms

    def weight(self) -> Decimal:
        return self._kilograms
```
<!-- fmt:on -->

Putting `add` on the base class gives all components the same surface, at the price of a leaf that offers an operation it can't honour. The cost shows up late. `test_mypy_accepts_add_on_a_component_leaf` type-checks a reduced model of this shape (it restates the classes and doesn't import the fixture) and gets exit status 0. `test_a_component_leaf_refuses_add_only_when_the_program_runs` then gets `TypeError` matching "cannot hold components". And `test_a_mutable_component_group_can_contain_itself` adds a group to itself; the `add` succeeds, and `weight` recurses until `RecursionError`. The frozen form gives up `add` and gains a type error at the call.

## Flyweight: one commodity, many consignments

Flyweight is for many references to equal values. A consolidation can carry many consignments, and several of them can name one commodity. The catalogue's remedy, credited to Gamma, Helm, Johnson and Vlissides, is to split what's the same everywhere (a commodity: HS code, description, dangerous-goods flag) from what varies by use (each consignment's weight and ports), and to share one object for the first. The catalogue's terms, as Rhodes quotes them, are intrinsic for the first kind of state and extrinsic for the second. The HS codes here are illustrative.

Rhodes's [The Flyweight Pattern](https://python-patterns.guide/gang-of-four/flyweight/) points at what Python already does: `sys.intern` is a factory function, and a dictionary behind one is the usual store. He suggests a `WeakValueDictionary` when callers may ask for so many distinct values that memory runs out, and he advises against putting the factory in `__new__`, because a call that looks like construction then returns a shared object. Python removes the need for a factory class: a lookup over a mapping does the job. `CommodityPool` wraps one so the catalogue and the weak dictionary travel together, and its `get` is the factory function Rhodes describes:

<!-- fmt:off -->
```python
class CommodityPool:
    """Builds each commodity once and hands the same object to every caller.

    The pool holds its commodities weakly: a commodity nobody else holds is dropped, and a later
    request builds an equal one. It is not safe to share between threads.
    """

    def __init__(self, catalogue: Mapping[str, tuple[str, bool]] = CATALOGUE) -> None:
        self._catalogue = catalogue
        self._pool: weakref.WeakValueDictionary[str, Commodity] = weakref.WeakValueDictionary()

    def get(self, hs_code: str, /) -> Commodity:
        try:
            return self._pool[hs_code]
        except KeyError:
            pass
        try:
            description, dangerous_goods = self._catalogue[hs_code]
        except KeyError:
            raise UnknownCommodityError(f"unknown commodity {hs_code!r}") from None
        commodity = Commodity(hs_code, description, dangerous_goods)
        self._pool[hs_code] = commodity
        return commodity

    def __len__(self) -> int:
        return len(self._pool)
```
<!-- fmt:on -->

`test_the_pool_returns_one_commodity_per_code` checks `is` for the same code and `is not` for different ones, and `test_an_unknown_commodity_code_is_refused` gets `UnknownCommodityError`; both run on the pool and on a `functools.cache` form. The two forms differ in lifetime, which is the decision this pattern leaves you. The [`weakref` documentation](https://docs.python.org/3.15/library/weakref.html) says of `WeakValueDictionary`: "Entries in the dictionary will be discarded when no strong reference to the value exists any more." The [`functools` documentation](https://docs.python.org/3.15/library/functools.html) calls `functools.cache` a "Simple lightweight unbounded function cache" and adds that "it never needs to evict old values". Here's the weak pool letting go:

<!-- fmt:off -->
```python
def test_the_weak_pool_drops_a_commodity_nobody_holds(pool: CommodityPool) -> None:
    first = pool.get(LITHIUM)
    first_ref = weakref.ref(first)
    assert len(pool) == 1

    del first
    # CPython usually frees an object at its last reference, but the language promises no
    # immediate finalisation, so collect explicitly before asserting.
    gc.collect()

    assert first_ref() is None
    assert len(pool) == 0
    second = pool.get(LITHIUM)
    assert second == Commodity(LITHIUM, "lithium-ion batteries", True)
    assert len(pool) == 1
```
<!-- fmt:on -->

The comment follows the [data model](https://docs.python.org/3.15/reference/datamodel.html), which says: "Do not depend on immediate finalization of objects when they become unreachable". `test_a_cache_keeps_every_commodity_it_has_made` runs the same `gc.collect()` and finds the commodity still alive, held by the cache alone. For three commodity codes that's fine. For a catalogue of thousands, requested by callers who come and go, the weak pool bounds memory by what's in use, and the cache grows. The pool's second request builds a new object equal to the first, so callers can't rely on identity across a drop. Under threads a cache can build the same value twice, and [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) shows that race; `CommodityPool` is documented as single-threaded.

A weak pool needs values that can be weakly referenced. The `weakref` page states the rule for slotted classes: "When `__slots__` are defined for a given type, weak reference support is disabled unless a '`__weakref__`' string is also present in the sequence of strings in the `__slots__` declaration." `Commodity` sets `weakref_slot=True`, which [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) explains. `test_a_pool_needs_commodities_that_accept_weak_references` shows a plain slotted dataclass refused with `TypeError`, "cannot create weak reference".

What makes sharing safe is that the value is frozen. `test_equal_commodities_need_not_be_the_same_object` builds two equal commodities that are distinct objects with equal hashes, so equality gives the right answer without the pool and callers compare with `==`, which is also Rhodes's point about strings. `test_a_shared_mutable_commodity_changes_every_consignment` is the third failure from the start: a mutable commodity edited through one consignment changes for the other, and the frozen one refuses the edit.

## Memory: slots trim, sharing removes, interning for strings

The figures below come from `bench/commodity_memory.py`, run with `uv run python -I bench/commodity_memory.py` and recorded on Python 3.15.2 on 5 November 2026. They're approximate and depend on the interpreter version and allocator, so no test asserts them. A fresh run for this chapter printed the same numbers. Each row holds 100,000 items in a list, and the per-item figure includes the 8-byte list pointer.

| What is held | Bytes allocated | Per item |
| --- | --- | --- |
| Dict-backed copies | 10,404,232 | ~104 |
| Slotted copies | 6,401,272 | ~64 |
| Slotted with weakref slot | 8,001,272 | ~80 |
| One shared slotted instance | 800,320 | ~8 |
| Port codes, plain split | 5,402,520 | ~54 |
| Port codes, interned | 801,104 | ~8 |

Slots trim each instance by a constant (the data model says: "The space saved over using `__dict__` can be significant."), the weakref slot adds about 16 bytes back, and sharing removes the instances, leaving the pointer. `test_commodities_have_no_instance_dict` shows the structure: no `__dict__`, and `__weakref__` among the slots.

`sys.getsizeof` points the wrong way here. Its [documentation](https://docs.python.org/3.15/library/sys.html) says: "Only the memory consumption directly attributed to the object is accounted for, not the memory consumption of objects it refers to." The same run reports 48 bytes for a dict-backed instance and 56 for a slotted one, so the slotted one reads larger while the table shows it costs less per item. `tracemalloc` counts what was allocated for the list and everything it holds, which is the comparison to read.

Port codes are the strings in a route line such as `NLRTM;SGSIN`. `test_split_port_codes_are_equal_but_distinct_objects` observes on CPython 3.15.2 that two codes from `str.split` are equal and `is not` the same object. `port_code` validates and returns an interned string:

<!-- fmt:off -->
```python
def port_code(text: str) -> str:
    """Validate a port code and return the interned string."""
    if not _PORT_CODE.fullmatch(text):
        raise PortCodeError(f"malformed port code {text!r}")
    return sys.intern(text)
```
<!-- fmt:on -->

`test_interned_port_codes_are_one_object` parses `"NLRTM;SGSIN;NLRTM"` through `route` and finds the first and last ports are one object. `test_a_malformed_port_code_is_refused` covers a lowercase code and a short one. The `sys.intern` entry says what interning buys: "Interning strings is useful to gain a little performance on dictionary lookup". The same run counted 4 distinct objects instead of 100,000. Equality works without interning, and the tests above compare with `==`; interning saves memory and lookup time, and nothing depends on it.

## When not to use it

- A flat list of consignments with no nesting needs a tuple and `sum`, not a union.
- Leaves and groups that share no question are two types, with no union to join them.
- A handful of commodities doesn't need a pool.
- Mutable values aren't shared.
- Comparing codes with `is` ties correctness to interning; use `==`.

<blockquote class="ai-sidebar" markdown="1">
**Specifying trees and flyweights.** "A composite" leaves open whether leaves and groups share a base class, and "a flyweight" leaves open who owns the shared objects and when they go. Paste a prompt that states the form:

> Model a consolidation as a frozen dataclass holding a tuple of parts, with `type Shipment = Consignment | ConsolidatedShipment` and `.weight` on both kinds. Reject an empty group and a consignment that appears twice. Use `match` with `assert_never` where the kinds differ. Share commodities from a pool built on `weakref.WeakValueDictionary`, with frozen slotted dataclasses and `weakref_slot=True`, and intern port codes with `sys.intern`. No Component base class and no `__new__` caching.

If the reply gives a leaf an `add` method or caches in `__new__`, ask for the union and the pool function.
</blockquote>

## Build, run, observe

The run checks that the tree and the pool each do what the chapter claims: the total includes nested groups in both forms, the invariants refuse bad trees, the pool shares and lets go, and mypy sees the difference between the union and the component form. From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/21-composite-and-flyweight
uv run pytest -v
uv run mypy --strict src tests bench
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 44 items

tests/test_composite.py::test_the_total_weight_includes_nested_consolidations[frozen-union] PASSED [  2%]
tests/test_composite.py::test_the_total_weight_includes_nested_consolidations[component-classes] PASSED [  4%]
tests/test_composite.py::test_a_flat_sum_misses_nested_consolidations PASSED [  6%]
tests/test_composite.py::test_a_consignment_and_a_consolidation_answer_weight_the_same_way[consignment] PASSED [  9%]
tests/test_composite.py::test_a_consignment_and_a_consolidation_answer_weight_the_same_way[consolidation] PASSED [ 11%]
tests/test_composite.py::test_consignments_lists_every_leaf_in_order PASSED [ 13%]
tests/test_composite.py::test_a_consolidation_with_dangerous_goods_anywhere_is_flagged[top-level] PASSED [ 15%]
tests/test_composite.py::test_a_consolidation_with_dangerous_goods_anywhere_is_flagged[nested] PASSED [ 18%]
tests/test_composite.py::test_a_consolidation_with_dangerous_goods_anywhere_is_flagged[none] PASSED [ 20%]
tests/test_composite.py::test_a_consolidation_must_have_parts PASSED     [ 22%]
tests/test_composite.py::test_a_consignment_may_appear_only_once_in_a_consolidation[same-level] PASSED [ 25%]
tests/test_composite.py::test_a_consignment_may_appear_only_once_in_a_consolidation[nested] PASSED [ 27%]
tests/test_composite.py::test_a_frozen_consolidation_cannot_be_rewired PASSED [ 29%]
tests/test_composite.py::test_a_component_leaf_refuses_add_only_when_the_program_runs PASSED [ 31%]
tests/test_composite.py::test_a_mutable_component_group_can_contain_itself PASSED [ 34%]
tests/test_composite.py::test_consolidations_compare_by_value PASSED     [ 36%]
tests/test_composite.py::test_a_pathologically_deep_consolidation_hits_the_recursion_limit PASSED [ 38%]
tests/test_composite.py::test_weight_refuses_zero_negative_and_non_finite_values[zero] PASSED [ 40%]
tests/test_composite.py::test_weight_refuses_zero_negative_and_non_finite_values[negative] PASSED [ 43%]
tests/test_composite.py::test_weight_refuses_zero_negative_and_non_finite_values[nan] PASSED [ 45%]
tests/test_composite.py::test_weight_refuses_zero_negative_and_non_finite_values[infinity] PASSED [ 47%]
tests/test_flyweight.py::test_the_pool_returns_one_commodity_per_code[weak-pool] PASSED [ 50%]
tests/test_flyweight.py::test_the_pool_returns_one_commodity_per_code[cache] PASSED [ 52%]
tests/test_flyweight.py::test_an_unknown_commodity_code_is_refused[weak-pool] PASSED [ 54%]
tests/test_flyweight.py::test_an_unknown_commodity_code_is_refused[cache] PASSED [ 56%]
tests/test_flyweight.py::test_the_weak_pool_drops_a_commodity_nobody_holds PASSED [ 59%]
tests/test_flyweight.py::test_a_cache_keeps_every_commodity_it_has_made PASSED [ 61%]
tests/test_flyweight.py::test_a_pool_needs_commodities_that_accept_weak_references PASSED [ 63%]
tests/test_flyweight.py::test_equal_commodities_need_not_be_the_same_object PASSED [ 65%]
tests/test_flyweight.py::test_a_shared_mutable_commodity_changes_every_consignment PASSED [ 68%]
tests/test_flyweight.py::test_commodities_have_no_instance_dict PASSED   [ 70%]
tests/test_flyweight.py::test_split_port_codes_are_equal_but_distinct_objects PASSED [ 72%]
tests/test_flyweight.py::test_interned_port_codes_are_one_object PASSED  [ 75%]
tests/test_flyweight.py::test_a_malformed_port_code_is_refused[lowercase] PASSED [ 77%]
tests/test_flyweight.py::test_a_malformed_port_code_is_refused[too-short] PASSED [ 79%]
tests/test_flyweight.py::test_the_commodity_catalogue_is_read_only PASSED [ 81%]
tests/test_static.py::test_mypy_reads_weight_on_either_kind_of_shipment PASSED [ 84%]
tests/test_static.py::test_mypy_refuses_parts_on_a_shipment_that_may_be_a_consignment PASSED [ 86%]
tests/test_static.py::test_mypy_reports_a_missing_match_arm PASSED       [ 88%]
tests/test_static.py::test_mypy_refuses_a_part_that_is_not_a_shipment PASSED [ 90%]
tests/test_static.py::test_mypy_refuses_adding_to_a_frozen_consolidation[add] PASSED [ 93%]
tests/test_static.py::test_mypy_refuses_adding_to_a_frozen_consolidation[append] PASSED [ 95%]
tests/test_static.py::test_mypy_refuses_adding_to_a_frozen_consolidation[assign] PASSED [ 97%]
tests/test_static.py::test_mypy_accepts_add_on_a_component_leaf PASSED   [100%]

============================== 44 passed in 3.61s ==============================
Success: no issues found in 9 source files
```

The suite has 31 test functions and 44 cases. The groups are:

- `test_composite.py` (13 functions): the weight table in both tree forms, the flat sum, flattening, and the invariants, plus the component-form fixtures.
- `test_flyweight.py` (12 functions): the pool in both forms, lifetime after `gc.collect()`, equality, no instance dict, and port-code interning.
- `test_static.py` (6 functions): the mypy witnesses through the test's own helper. For how those are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: drop the duplicate check.** In a scratch copy, delete the `if consignment_id in seen:` block in `ConsolidatedShipment.__post_init__`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` printed, identically in three runs apart from the duration:

```text
E       Failed: DID NOT RAISE ConsolidationError
E       Failed: DID NOT RAISE ConsolidationError
FAILED tests/test_composite.py::test_a_consignment_may_appear_only_once_in_a_consolidation[same-level]
FAILED tests/test_composite.py::test_a_consignment_may_appear_only_once_in_a_consolidation[nested]
2 failed, 42 passed in 3.60s
Success: no issues found in 8 source files
```

Both placements of the repeated consignment now build a consolidation without complaint, and mypy stays green because a tuple with a repeat is still a tuple.

**Experiment two: remove the weak-reference slot.** In a fresh scratch copy, delete `weakref_slot=True` from `Commodity`. The filter this time is `uv run pytest -q 2>&1 | grep -E '^(FAILED|[0-9]+ (passed|failed))'`, followed by the same mypy command. It printed, identically in three runs apart from the duration:

```text
FAILED tests/test_composite.py::test_a_consignment_may_appear_only_once_in_a_consolidation[same-level]
FAILED tests/test_composite.py::test_a_consignment_may_appear_only_once_in_a_consolidation[nested]
FAILED tests/test_composite.py::test_consolidations_compare_by_value - TypeEr...
FAILED tests/test_composite.py::test_a_pathologically_deep_consolidation_hits_the_recursion_limit
FAILED tests/test_flyweight.py::test_the_pool_returns_one_commodity_per_code[weak-pool]
FAILED tests/test_flyweight.py::test_the_weak_pool_drops_a_commodity_nobody_holds
FAILED tests/test_flyweight.py::test_a_cache_keeps_every_commodity_it_has_made
FAILED tests/test_flyweight.py::test_commodities_have_no_instance_dict - Asse...
8 failed, 26 passed, 10 errors in 3.72s
Success: no issues found in 8 source files
```

The pool can't hold a commodity, so the tests that build a consignment through it fail or error (the filter doesn't list the 10 errors). The 8 failures include `test_commodities_have_no_instance_dict`, which sees that `__weakref__` has left the slots. mypy reports success, so the error appears only when a program runs.

## What you can do now

- Model a tree as a closed union: `type Shipment = Consignment | ConsolidatedShipment`, with `.weight` answered by both kinds and no Component base class.
- Compute a total that recurses and a flattening that matches on the kinds, with `weight` on `ConsolidatedShipment` and `consignments` ending in `assert_never`, backed by the nested-weight, flat-sum and missing-arm tests.
- Keep a tree's invariants in its constructor: `ConsolidatedShipment.__post_init__` refuses an empty group and a repeated consignment, and experiment one shows the test that notices.
- Build a pool and decide its lifetime: `CommodityPool` over `WeakValueDictionary` against a `functools.cache` form, run on one table, with `weakref_slot=True` on `Commodity` as experiment two shows.
- Explain why sharing is safe: `Commodity` is frozen, and the mutable-commodity test is the failure it prevents.
- Read the memory table with `tracemalloc` and treat `sys.getsizeof` with suspicion, and intern port codes with `port_code`, knowing `==` doesn't need it.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Composite and Flyweight. Brandon Rhodes covers both in [The Composite Pattern](https://python-patterns.guide/gang-of-four/composite/) and [The Flyweight Pattern](https://python-patterns.guide/gang-of-four/flyweight/). The references are the [`weakref`](https://docs.python.org/3.15/library/weakref.html), [`sys`](https://docs.python.org/3.15/library/sys.html) and [`functools`](https://docs.python.org/3.15/library/functools.html) module documentation and the [data model](https://docs.python.org/3.15/reference/datamodel.html) on `__slots__`. Luciano Ramalho's *Fluent Python*, second edition, covers the data model and dataclasses behind both. Weak references return in Observer, which follows in the book: [Observer]({{ '/docs/22-observer/' | relative_url }}). The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
