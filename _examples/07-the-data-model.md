---
layout: example
order: 7
title: "The data model: special methods as calls on the type"
description: One small shipping model whose tests show equality and hashing, reflected operators, total ordering, containers and text as calls the interpreter makes on the type.
github_path: examples/07-the-data-model
card_eyebrow: "Python substrate · The data model"
card_title: "Special methods the interpreter calls on the type"
card_blurb: "Cartons that hash equal when turned, money that multiplies from either side and refuses to mix currencies, and a history that is sized and iterable, checked at runtime and under mypy."
---

One small shipping model witnesses how a type joins Python's protocols by defining the method.
Each test asserts the behaviour named in its title.

## Equality and hashing

An operator or builtin calls the special method on the type, so an instance attribute named
`__len__` is ignored. Defining `__eq__` alone sets `__hash__` to `None`. `Dimensions` treats a
carton stowed on another face as the same carton, and a frozen dataclass with a custom `__eq__`
and no `__hash__` keeps a field hash that splits equal cartons across two set elements, with no
complaint from mypy.

## Arithmetic and ordering

Returning `NotImplemented` hands the operation to the other operand, so `2 * price` reaches
`Money.__rmul__`. Foreign operands raise `TypeError`, and `sum()` needs a `Money` start value.
`functools.total_ordering` derives `<=`, `>` and `>=` from `__lt__`, and quotes sort by `total`
and not by themselves.

## Containers and text

`TrackingHistory` defines `__len__` and `__iter__`, and truthiness and `in` follow. An iterable
without `__len__` is truthy when empty. `repr`, `str` and `format` serve different readers.

## Under mypy

`mypy --strict` requires `__eq__` to accept `object`, rejects operands the methods don't
accept and sorting a type with no ordering, and can't see a broken hash contract.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/07-the-data-model
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
