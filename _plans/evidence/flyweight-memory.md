---
title: "Evidence: memory of shared and slotted commodities"
output: false
render_with_liquid: false
---

# What a commodity held by many consignments costs

Recorded 2026-11-05 (r10) for the chapter on Composite and Flyweight, on Python 3.15.2 and mypy 2.4.1.
Run from `examples/21-composite-and-flyweight` with `uv run python -I bench/commodity_memory.py`, three
times, with identical output each time. The script is `bench/commodity_memory.py`; its output went
through `python3 scripts/host_ids.py filter`.

The figures are approximate bytes for this interpreter version and allocator. They are not asserted by
any test. `sys.getsizeof` counts only the object itself, so a slotted instance reads larger than a
dict-backed one; `tracemalloc` counts what is allocated for the list and everything it holds, and is
the comparison to read. The per-item figures include the 8-byte list pointer.

```text
Python 3.15.2, 100,000 items held in a list

sys.getsizeof of one instance (the object itself, not what it refers to)
  dict-backed instance            48
  dict-backed __dict__           296
  slotted instance                56
  slotted with weakref slot       72

tracemalloc, bytes allocated for the list and what it holds (list pointer included)
  dict-backed copies            10404232  (~104 bytes per item)
  slotted copies                 6401272  (~64 bytes per item)
  slotted with weakref slot      8001272  (~80 bytes per item)
  one shared slotted instance     800320  (~8 bytes per item)

tracemalloc, port codes drawn from four values
  plain split                  5402520
  interned                      801104
  distinct objects, plain        100000
  distinct objects, interned          4
```
