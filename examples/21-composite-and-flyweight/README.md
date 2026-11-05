# Composite and Flyweight

A consolidation of consignments that answers the same question as a single consignment, and one
shared, frozen commodity per code that many consignments point to. The chapter's thesis is that both
patterns survive: Python removes the Component base class and the factory class, and the decisions
remain. For Composite they are what both kinds answer, where the total is computed and which
invariants a tree keeps. For Flyweight they are who builds a shared value, how long it lives and why
immutability makes sharing safe. HS codes, port codes and weights are illustrative.

## What it witnesses

Composite.

- `Consignment` is a leaf and `ConsolidatedShipment(id, parts)` is a group, with
  `type Shipment = Consignment | ConsolidatedShipment`. Both answer `.weight`, and mypy types it on the
  union without narrowing. The group's `weight` recurses, so a nested consolidation counts: 23.75 kg
  against 17.25 kg for a sum of the direct consignments.
- Where the kinds differ, `consignments` and `carries_dangerous_goods` use `match` over the closed
  union with `assert_never`. A missing arm is an `[arg-type]` error.
- A group is built bottom-up from a tuple of parts, so it can't be rewired afterwards. It refuses
  empty `parts` and a consignment that appears twice anywhere beneath it, and it compares and hashes by value. mypy refuses `add`, `append` and assignment on it.
- The GoF form is a fixture in `tests/conftest.py`: `_Component` declares `add` for every component,
  `_ComponentLeaf` inherits the `add` that raises, and `_ComponentGroup` holds a mutable list. It
  passes the same weight table as the frozen form. mypy accepts `leaf.add(...)`, the call fails only
  when the program runs, and a group can contain itself and then raises `RecursionError`.
- A very deep tree raises `RecursionError` on `.weight`. The deep tree in the test is assembled
  without running validation, because validation recurses as well. The threshold is a CPython
  detail and isn't asserted.

Flyweight.

- `CommodityPool` builds each `Commodity` once per code from the read-only `CATALOGUE` and holds it in a
  `weakref.WeakValueDictionary`. An unknown code is an `UnknownCommodityError`. A commodity nobody else
  holds is dropped, and the next request builds an equal one. The `functools.cache` form is a fixture: it
  passes the same table and keeps every commodity it has made.
- `Commodity` is a frozen slotted dataclass with `weakref_slot=True`: a pool of values without a
  weak-reference slot raises `TypeError`. Equal commodities need not be the same object, which is why
  sharing is safe. A shared mutable value changes every holder.
- `port_code` validates a five-character code and returns `sys.intern(text)`. Split strings are equal
  but distinct objects, interned codes are one object, and equality works without interning.
- Every lifetime test drops its names and calls `gc.collect()` before asserting.

Memory figures aren't asserted. `bench/commodity_memory.py` prints them for the running
interpreter, and the chapter quotes a recorded run with its Python version and date.

The reduced-model snippet in `test_static.py` (the component form with `add` on a leaf) restates the
shape and doesn't import the fixture.

## Layout

- `src/composite_flyweight/domain.py`: `ConsignmentId`, `Weight`, `Commodity`, `PortCall`,
  `Consignment`, `ConsolidatedShipment`, `Shipment`, `ConsolidationError`.
- `src/composite_flyweight/consolidation.py`: `consignments`, `carries_dangerous_goods`.
- `src/composite_flyweight/flyweights.py`: `CATALOGUE`, `CommodityPool`, `UnknownCommodityError`,
  `PortCodeError`, `port_code`, `route`.
- `bench/commodity_memory.py`: the `sys.getsizeof` and `tracemalloc` comparison. Pytest doesn't collect it.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests bench
uv run python -I bench/commodity_memory.py
```

## What the tests verify

`tests/test_composite.py`

- `test_the_total_weight_includes_nested_consolidations`: 23.75 kg in the frozen and the component forms.
- `test_a_flat_sum_misses_nested_consolidations`: 17.25 kg against 23.75 kg.
- `test_a_consignment_and_a_consolidation_answer_weight_the_same_way`: one function, no `isinstance`.
- `test_consignments_lists_every_leaf_in_order`: CN-1, CN-3, CN-4, CN-2.
- `test_a_consolidation_with_dangerous_goods_anywhere_is_flagged`: top level, nested and none.
- `test_a_consolidation_must_have_parts`: `ConsolidationError`.
- `test_a_consignment_may_appear_only_once_in_a_consolidation`: same level and nested.
- `test_a_frozen_consolidation_cannot_be_rewired`: `FrozenInstanceError`, and `parts` is a tuple.
- `test_a_component_leaf_refuses_add_only_when_the_program_runs`: `TypeError` from the comparison form.
- `test_a_mutable_component_group_can_contain_itself`: the comparison form raises `RecursionError`.
- `test_consolidations_compare_by_value`: two separately built trees are equal and hash equal.
- `test_a_pathologically_deep_consolidation_hits_the_recursion_limit`: `RecursionError`.
- `test_weight_refuses_zero_negative_and_non_finite_values`: zero, negative, NaN and infinity.

`tests/test_flyweight.py`

- `test_the_pool_returns_one_commodity_per_code`: both pool forms.
- `test_an_unknown_commodity_code_is_refused`: both pool forms.
- `test_the_weak_pool_drops_a_commodity_nobody_holds`: gone after `del` and `gc.collect()`.
- `test_a_cache_keeps_every_commodity_it_has_made`: still alive after `gc.collect()`.
- `test_a_pool_needs_commodities_that_accept_weak_references`: `TypeError` for a plain slotted value.
- `test_equal_commodities_need_not_be_the_same_object`: equal, same hash, distinct.
- `test_a_shared_mutable_commodity_changes_every_consignment`: and the frozen one refuses.
- `test_commodities_have_no_instance_dict`: slotted, with a `__weakref__` slot.
- `test_split_port_codes_are_equal_but_distinct_objects`: CPython 3.15.2 behaviour.
- `test_interned_port_codes_are_one_object`: `route` interns.
- `test_a_malformed_port_code_is_refused`: lowercase and too short.
- `test_the_commodity_catalogue_is_read_only`: item assignment raises `TypeError`.

`tests/test_static.py`

- `test_mypy_reads_weight_on_either_kind_of_shipment`: clean.
- `test_mypy_refuses_parts_on_a_shipment_that_may_be_a_consignment`: `[union-attr]`.
- `test_mypy_reports_a_missing_match_arm`: `[arg-type]`, `expected "Never"`.
- `test_mypy_refuses_a_part_that_is_not_a_shipment`: `[arg-type]`.
- `test_mypy_refuses_adding_to_a_frozen_consolidation`: `[attr-defined]` for `add` and `append`, `[misc]` for assignment.
- `test_mypy_accepts_add_on_a_component_leaf`: clean (a reduced model).

Classes and functions named with a leading underscore in `tests/conftest.py` are test fixtures and
aren't part of the model code.
