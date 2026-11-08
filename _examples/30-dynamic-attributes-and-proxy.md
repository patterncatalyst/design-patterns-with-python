---
layout: example
order: 30
title: "Dynamic attributes: __getattr__ and Proxy as a feature"
description: A tracking history that declares its fields, loads them once from a slow feed on the first read through __getattr__, and behaves like any other object under dir(), copy, iteration and mypy, with a cached_property form on the same table and a module-level __getattr__ that deprecates an old name.
github_path: examples/30-dynamic-attributes-and-proxy
card_eyebrow: "Idiomatic Python · Dynamic attributes"
card_blurb: "A tracking history loads its fields on the first read and keeps them as plain attributes. A __getattr__ that reads a missing attribute recurses under copy, and an allow-list stops it."
card_title: "Lazy loading without a surrogate"
---

One shipping domain witnesses the virtual proxy's intent without a surrogate. A consignment's
handling events come from a carrier feed that is slow to read, and most callers want only the
consignment id. Each test asserts the behaviour named in its title, and the loader records every
call, so a load is counted and never timed.

## A history that loads itself

`TrackingHistory` declares `events`, `status` and `last_port` as annotations and stores nothing
for them. The first read reaches `__getattr__`, which loads once, writes all three fields into the
instance dictionary around `__setattr__`, and returns the one asked for. Later reads find the
fields by ordinary lookup. A `cached_property` form passes the same table of consignments.

## When each hook runs

`__getattr__` runs only for a name that ordinary lookup cannot find, and `__getattribute__` runs on
every read. A `__getattr__` that reads an attribute the instance does not have recurses on a bare
instance, so `copy`, `deepcopy` and `pickle` recurse too. The history refuses names outside a fixed
set before it reads anything, and two other fixes hold.

## Consistent with the rest of Python

`__setattr__` refuses loaded fields, `__dir__` lists the lazy fields so `dir()` and the "Did you
mean" hint work, and `__iter__` is explicit because `iter()` and `len()` don't reach `__getattr__`.
`hasattr` loads. mypy types an unknown attribute by `__getattr__`'s return type, keeps the declared
field types, and accepts assignments that `__setattr__` refuses.

## A module-level `__getattr__`

`tracking.LazyTrackingHistory` warns with `DeprecationWarning` and returns `TrackingHistory`.
Other missing names raise `AttributeError`, and the module `__dir__` lists the old name.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/30-dynamic-attributes-and-proxy
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
