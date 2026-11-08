---
layout: example
order: 27
title: "Descriptors and properties"
description: One validating descriptor shared by six Decimal fields in three shipping classes, compared with a property per field, with the lookup order, dataclass placement, a cached chargeable weight, and what slots=True silently removes.
github_path: examples/27-descriptors-and-properties
card_eyebrow: "Idiomatic Python · Descriptors"
card_blurb: "A copied setter drifts, a descriptor does not. One Positive class validates every weight and extent, a cached_property computes a chargeable weight once, and slots=True removes the validator without a word."
card_title: "Validators, lookup order and cached values"
---

One Consignment domain witnesses the three tools behind managed attributes. Weights and extents
arrive from carrier feeds and must be finite and positive everywhere. Each test asserts the
behaviour named in its title, and no test sleeps: the thread race is forced with a barrier.

## One attribute, then many

`Container.payload_kg` is a computed `property`, and a validating setter on one field is a
`property` pair. A second and third class that need the same rule are the force for `Positive`, a
descriptor that learns each field's name in `__set_name__` and stores through `vars()`. A property
form and the descriptor give the same answer on one table of extents, and a copied setter that
dropped `is_finite()` accepts infinity.

## Lookup and dataclasses

A data descriptor beats the instance dictionary, and the instance dictionary beats a
`cached_property`. On a dataclass, class access decides whether a field has a default, a frozen
class needs a descriptor that writes through `vars()`, and `slots=True` replaces the descriptor with
a slot that accepts a negative length.

## cached_property

`Consignment.chargeable_kg` is the larger of the actual and the volumetric weight, computed on the
first read and stored in `__dict__`. It needs that dictionary, cannot be cleared on a frozen class,
goes stale over mutable state, and since 3.12 its getter can run twice when two threads race.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/27-descriptors-and-properties
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
