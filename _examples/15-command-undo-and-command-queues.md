---
layout: example
order: 15
title: "Command, undo, and command queues"
description: Booking amendments as frozen values whose apply returns the inverse, with undo and redo stacks, a bounded history and an all-or-nothing queue, and tests for what a shared mutable mapping breaks.
github_path: examples/15-command-undo-and-command-queues
card_eyebrow: "Selecting behaviour · Command"
card_title: "Amendments as values with undo"
card_blurb: "Reweigh, redirect and set instructions as frozen values under a closed union, an apply that returns the inverse computed at run time, and a queue that applies a batch all or nothing."
---

One booking witnesses what Command becomes in Python. Each test asserts the behaviour named in its
title.

## Commands as values

`Reweigh`, `Redirect` and `SetInstructions` are frozen dataclasses under one `type` alias. They
compare and print by value, which a `functools.partial` doesn't. `apply` matches on the amendment,
ends in `assert_never`, and returns the amended request together with the amendment that reverses
it.

## Undo and redo

`Booking` keeps undo and redo stacks of inverses in `deque`s. The inverse is read from the request
at the moment the command runs, because one recorded when the command is built restores a stale
value once commands are queued. A bounded stack forgets the oldest amendment silently.

## Commands that share data

Two commands built from one `dict` undo to the wrong state, and mypy accepts them. A `frozendict`
field turns the shared `dict` into a type error and item assignment into a runtime error.

## A queue that applies all or nothing

`apply_pending` folds the queued amendments first in, first out on a local request and commits only
when the whole batch succeeded.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/15-command-undo-and-command-queues
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
