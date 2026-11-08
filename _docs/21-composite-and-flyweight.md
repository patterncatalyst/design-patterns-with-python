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

A consolidation puts several consignments under one booking, and a consolidation can sit inside another. Meanwhile the same few commodities can repeat across many consignments, and each repetition costs an object. Both patterns survive in Python: Composite because the shape of the tree is still a design decision, Flyweight because identity and lifetime are. What Python removes is machinery, the Component base class and the factory class. The obvious versions fail three ways:

- A total sums the consignments directly under a consolidation and skips the nested one: 17.25 kg reported for groups that hold 23.75 kg.
- A consignment sits in two groups of one consolidation and is counted twice. Nothing in the weight arithmetic notices.
- One commodity object is shared by every consignment that carries it, and one consignment's line edits it. The others see the change.

{% include excalidraw.html name="21-composite-and-flyweight" described="true" caption="Figure 21.1: One weight question, one shared commodity. A consolidation answers weight as a consignment does, summing its parts through nested groups; consignments reach a single frozen commodity per code from a pool that lets go of commodities nobody holds." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-21-composite-and-flyweight" markdown="1">
A top `ConsolidatedShipment` ("weight: sums its parts, nested or not") has two children: a `Consignment` and a second, nested `ConsolidatedShipment` ("a nested group, same question") that holds two more. All three `Consignment` leaves point to one `Commodity` ("one object per code, frozen"), and `CommodityPool` ("weak values: dropped when nobody holds them") points up to it. At the side, a note reads "Shipment = Consignment | ConsolidatedShipment", and a separate `port_code` box reads "sys.intern: one object per code". Port codes are the other shared value, and they have no arrow into the tree because a consignment holds them as plain strings.
</div>
</details>

The figure shows the tree answering one weight question, and its leaves sharing one commodity from the pool.

## Pattern: Composite

### The problem

A caller asks a consignment or a consolidation, nested to any depth, for its weight. It shouldn't need to know which it holds, and the tree must not count a consignment twice.

### The solution

A **Composite** lets a group of items answer the same questions as a single item, so callers treat part and whole alike.

**Bucket: survives.** Composite is for the caller who holds something and asks one question without caring whether it's a single item or a bundle of them. The base class dissolves, and what both kinds answer, where the total is computed and which invariants hold remain decisions.

The *Design Patterns* catalogue by Gamma, Helm, Johnson and Vlissides (1994) gives it to part-whole structures. Brandon Rhodes, in [The Composite Pattern](https://python-patterns.guide/gang-of-four/composite/), treats it as symmetry between containers and contents: "The art of using the Composite Pattern is determining where to break the symmetry." In Python any mechanism can supply that symmetry, whether a base class, a type checker or duck typing. [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) lists the assumptions behind the base class.

### How Python models it

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

The uniform question is `.weight`. A `Consignment` stores it and a `ConsolidatedShipment` computes it from its parts, so the total is calculated at the group and nowhere else: 23.75 kg for the nested groups, with no `isinstance`. The union is closed and mypy reads it: `shipment.weight` on a `Shipment` type-checks, and `.parts`, which exists on one kind, is `[union-attr]`.

### Where the kinds differ: match over a closed union

Rhodes names the limit on symmetry: "The question of return type will serve as a very important guardrail when you are designing in Python". Flattening differs by kind but returns one type:

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

The leaves come out depth first, CN-1, CN-3, CN-4, CN-2, and `carries_dangerous_goods` builds on them to find dangerous goods at any level. The last arm is the safety: `assert_never` takes `Never`, so a missing arm is `[arg-type]` with `expected "Never"`, and so is a `Weight` placed in `parts`. This form suits a domain that names its kinds. For kinds that other code adds, [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers interfaces without a base class.

### Invariants: built bottom-up, frozen, counted once

No language feature supplies a tree's invariants. This one has three:

- A consolidation needs at least one part.
- A consignment appears once, whether at the same level or nested below another group.
- Weights are positive and finite: zero, negative, NaN and infinity are refused.

Construction order is the other protection. Parts are a tuple of objects that already exist, and the dataclass is frozen, so assignment raises `FrozenInstanceError` and mypy refuses `add`, `append` and assignment on a group. Two trees built separately from the same data compare and hash equal; [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers frozen and hash. A 5,000-level tree raises `RecursionError` on `.weight`; the domain nests a few levels.

### The Component base class

The mutable catalogue form, kept as a comparison, is an abstract `_Component` that declares `weight` and an `add` that leaves inherit and refuse with `TypeError`. It passes the same weight table. Putting `add` on the base class gives every component the same surface, at the price of a leaf that offers an operation it can't honour. mypy accepts `add` on a leaf, which then raises `TypeError` "cannot hold components" at run time. A group can `add` itself, and `weight` recurses until `RecursionError`. The frozen form gives up `add` and gains a type error at the call.

## Pattern: Flyweight

### The problem

The same few commodities can repeat across many consignments, and each repetition costs an object. Sharing one object per commodity saves memory, but then someone must build it, decide how long it lives, and stop one consignment's edit reaching the others.

### The solution

A **Flyweight** splits the state that's the same everywhere from the state that varies by use, and shares one object for the first.

**Bucket: survives.** Python removes the factory class, and who builds the shared value and how long it lives remain decisions.

The shared part is intrinsic (a commodity's HS code, description and dangerous-goods flag) and the per-use part extrinsic (each consignment's weight and ports). The HS codes are illustrative. Rhodes's [The Flyweight Pattern](https://python-patterns.guide/gang-of-four/flyweight/) points at what Python already does: `sys.intern` is a factory function, a dictionary behind one is the usual store, and a `WeakValueDictionary` suits callers who may ask for so many distinct values that memory runs out. He advises against a factory in `__new__`, because a call that looks like construction then returns a shared object.

### How Python models it

`CommodityPool` keeps the catalogue and the weak dictionary together, and `get` is the factory function:

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

The same code gives the same object (`is`), different codes different objects, and an unknown code raises `UnknownCommodityError`. A `functools.cache` form behaves the same on that table. The two differ in lifetime:

| Store | Documented behaviour | After `gc.collect()` with no holder |
| --- | --- | --- |
| `WeakValueDictionary` | "Entries in the dictionary will be discarded when no strong reference to the value exists any more." | dropped; the next request builds an equal, new object |
| `functools.cache` | "it never needs to evict old values" | kept alive by the cache alone |

The collection is explicit because the [data model](https://docs.python.org/3/reference/datamodel.html) says: "Do not depend on immediate finalization of objects when they become unreachable". For three codes either works. For a catalogue of thousands, requested by callers who come and go, the weak pool bounds memory by what's in use. Callers can't rely on identity across a drop. Under threads a cache can build the same value twice, as [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) shows; `CommodityPool` is single-threaded.

A weak pool needs values that accept weak references. The [`weakref` documentation](https://docs.python.org/3/library/weakref.html): "When `__slots__` are defined for a given type, weak reference support is disabled unless a '`__weakref__`' string is also present". `Commodity` sets `weakref_slot=True`, which [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) explains; a plain slotted dataclass gets `TypeError`, "cannot create weak reference".

A frozen value makes sharing safe. Two equal commodities built separately are distinct objects with equal hashes, so `==` gives the right answer without the pool, which is Rhodes's point about strings. A mutable commodity edited through one consignment changes for the other; the frozen one refuses the edit.

### Memory: slots trim, sharing removes

`bench/commodity_memory.py`, run with `uv run python -I bench/commodity_memory.py` and recorded on Python 3.15.2 on 5 November 2026, holds 100,000 items in a list. The figures are approximate, depend on the interpreter and allocator, and include the 8-byte list pointer per item.

| What is held | Bytes allocated | Per item |
| --- | --- | --- |
| Dict-backed copies | 10,404,232 | ~104 |
| Slotted copies | 6,401,272 | ~64 |
| Slotted with weakref slot | 8,001,272 | ~80 |
| One shared slotted instance | 800,320 | ~8 |
| Port codes, plain split | 5,402,520 | ~54 |
| Port codes, interned | 801,104 | ~8 |

Slots trim each instance by a constant ("The space saved over using `__dict__` can be significant."), the weakref slot adds about 16 bytes back, and sharing removes the instances. `Commodity` has no `__dict__` and has `__weakref__` among its slots.

`sys.getsizeof` points the wrong way. Its [documentation](https://docs.python.org/3/library/sys.html): "Only the memory consumption directly attributed to the object is accounted for, not the memory consumption of objects it refers to." It reports 48 bytes for a dict-backed instance and 56 for a slotted one, the reverse of the table. `tracemalloc` counts everything allocated, which is the comparison to read.

### Interning port codes

Port codes are the strings in a route line such as `NLRTM;SGSIN`. It's observed on CPython 3.15.2 that two codes from `str.split` are equal and distinct objects. `port_code` validates and interns:

<!-- fmt:off -->
```python
def port_code(text: str) -> str:
    """Validate a port code and return the interned string."""
    if not _PORT_CODE.fullmatch(text):
        raise PortCodeError(f"malformed port code {text!r}")
    return sys.intern(text)
```
<!-- fmt:on -->

Parsing `"NLRTM;SGSIN;NLRTM"` through `route` gives one object for the first and last ports, and a lowercase or short code raises. The `sys.intern` entry says what it buys: "Interning strings is useful to gain a little performance on dictionary lookup". The benchmark held 4 distinct objects instead of 100,000. Equality works without interning; nothing depends on it.

## When not to use it

- **Composite.** A flat list of consignments with no nesting needs a tuple and `sum`, not a union. Leaves and groups that share no question are two types, with no union to join them.
- **Flyweight.** A handful of commodities doesn't need a pool. Mutable values aren't shared. Comparing codes with `is` ties correctness to interning; use `==`.

> **🤖 Explore with your agent**
>
> "Model a consolidation as a frozen dataclass holding a tuple of parts, with `type Shipment = Consignment | ConsolidatedShipment` and `.weight` on both kinds. Reject an empty group and a consignment that appears twice. Use `match` with `assert_never` where the kinds differ. Share commodities from a pool built on `weakref.WeakValueDictionary`, with frozen slotted dataclasses and `weakref_slot=True`, and intern port codes with `sys.intern`. No Component base class and no `__new__` caching."
>
> If the reply gives a leaf an `add` method or caches in `__new__`, ask for the union and the pool function.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/21-composite-and-flyweight
uv run pytest -v --no-header
uv run mypy --strict src tests bench
```

All 44 cases pass and mypy is clean. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers how the mypy checks are built. Two experiments, each in a fresh scratch copy:

- **Drop the duplicate check.** Delete the `if consignment_id in seen:` block in `ConsolidatedShipment.__post_init__`. Both placements of a repeated consignment build without complaint (`DID NOT RAISE ConsolidationError`). mypy is clean: a tuple with a repeat is still a tuple.
- **Remove the weak-reference slot.** Delete `weakref_slot=True` from `Commodity`. The pool can't hold a commodity, so 8 cases fail and 10 error wherever a consignment is built through it. mypy is clean, so the error appears only at run time.

## What you can do now

- Model a tree as `type Shipment = Consignment | ConsolidatedShipment`, with `.weight` on both kinds and no Component base class.
- Total through nested groups with `weight`, and flatten with `consignments`, ending its `match` in `assert_never`.
- Keep a tree's invariants in `ConsolidatedShipment.__post_init__`: no empty group, no repeated consignment.
- Build `CommodityPool` over `WeakValueDictionary`, choosing it over `functools.cache` for lifetime, with `weakref_slot=True` on a frozen `Commodity`.
- Read memory with `tracemalloc`, not `sys.getsizeof`, and intern port codes with `port_code` while comparing with `==`.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Composite and Flyweight. Brandon Rhodes covers both in [The Composite Pattern](https://python-patterns.guide/gang-of-four/composite/) and [The Flyweight Pattern](https://python-patterns.guide/gang-of-four/flyweight/). The references are the [`weakref`](https://docs.python.org/3/library/weakref.html), [`sys`](https://docs.python.org/3/library/sys.html) and [`functools`](https://docs.python.org/3/library/functools.html) module documentation and the [data model](https://docs.python.org/3/reference/datamodel.html) on `__slots__`. Luciano Ramalho's *Fluent Python*, second edition, covers the data model and dataclasses behind both. Weak references return in [Observer]({{ '/docs/22-observer/' | relative_url }}). The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
