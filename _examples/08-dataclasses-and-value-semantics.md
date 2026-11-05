---
layout: example
order: 8
title: "Dataclasses and value semantics: value types in one declaration"
description: Frozen, slotted dataclasses for a shipping booking, with tests for hashing, aliasing, ordering, entities and what mypy can and can't see.
github_path: examples/08-dataclasses-and-value-semantics
card_eyebrow: "Python substrate · Dataclasses, Value Object"
card_title: "Value types from one dataclass declaration"
card_blurb: "Weight, Money and SlotId as frozen slotted dataclasses, an amendment that is a new value, a stowage plan that stays an entity, and the checks mypy makes and misses."
---

One booking model witnesses what `@dataclass` writes and what stays with the author. Each test
asserts the behaviour named in its title.

## Values

`Weight`, `Money` and `SlotId` are frozen and slotted. They compare by content, hash equal when
equal and serve as dict keys. Assignment raises, and `slots=True` removes `__dict__` and weak
references. Frozen is a `__setattr__` guard and is shallow, so a `list` field still mutates and
makes the value unhashable.

## Values and entities

An amended consignment is a new value from `replace`, which reruns `__post_init__`, and the
other booking keeps the old one. `StowagePlan` is an entity: identity equality, its own
reservations per plan, and a mutable default refused when the class is created.

## Ordering and construction

- `order=True` sorts `SlotId` by bay, row and tier. On `Money` it would compare across
  currencies, so `Money` defines no order.
- `field(compare=False)` keeps a remark out of equality, and `kw_only=True` rejects positional
  arguments.
- `__post_init__` only reads, and `Money.of` quantises to cents first.

## What mypy sees

`mypy --strict` flags frozen assignment, positional arguments to a `kw_only` class, an unknown
`replace` keyword and `<` on `Money`. A mutable dict key, a mutable default and a weak reference
to a slotted instance pass without output.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/08-dataclasses-and-value-semantics
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
