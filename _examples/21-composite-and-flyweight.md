---
layout: example
order: 21
title: "Composite and Flyweight"
description: A consolidation of consignments that answers weight like one consignment, a pool of shared frozen commodities, and interned port codes, with tests for nested totals, tree invariants, object lifetime and what mypy sees.
github_path: examples/21-composite-and-flyweight
card_eyebrow: "Structure · Composite and Flyweight"
card_blurb: "A closed union of consignment and consolidation, matched where the kinds differ. A weak pool shares one frozen commodity per code, and the GoF component classes and a cache run the same tables as comparisons."
card_title: "One question for a group and a leaf, one object per commodity"
---

One shipping domain witnesses both patterns, joined by one story: a consolidation repeats the same
commodity and port codes. Each test asserts the behaviour named in its title.

## Composite

A `Consignment` and a `ConsolidatedShipment` both answer `weight`, and the group's total includes
nested groups. Where the kinds differ, `match` over the closed `Shipment` union makes a missing arm
a mypy error. A group is built bottom-up and frozen, so it can't be empty or rewired, and it refuses
a consignment that appears twice.

## Flyweight

`CommodityPool` returns one frozen `Commodity` per code and holds it weakly, so a commodity nobody
else holds is dropped. Equal commodities need not be the same object, which is why sharing is safe.
Port codes are interned, and the memory figures come from a benchmark script, not a test.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/21-composite-and-flyweight
uv run pytest -v
uv run mypy --strict src tests bench
uv run python -I bench/commodity_memory.py
```

The example README lists what each test verifies.
