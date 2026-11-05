---
layout: example
order: 22
title: "Observer"
description: A generic signal with a written-down delivery contract, bound methods held through WeakMethod, and a plain list of callables as a comparison, with tests for order, failure isolation, subscriber lifetime, re-entrancy and what mypy sees.
github_path: examples/22-observer
card_eyebrow: "Coordination · Observer"
card_blurb: "A typed signal delivers to a snapshot in subscription order, gathers failures into one ExceptionGroup and queues nested events. Bound methods are held weakly, and a plain list runs the same table as a comparison."
card_title: "Who is told, in what order, and for how long"
---

One shipping domain witnesses the pattern: handling events raised as cargo moves, and a tracking
history that subscribes to them. Each test asserts the behaviour named in its title.

## The delivery contract

`Signal[E]` runs subscribers in subscription order and ignores a duplicate. One failing subscriber
does not stop the rest: every failure arrives after delivery as one `ExceptionGroup`. Delivery goes
to a snapshot, so subscribing or unsubscribing during delivery skips no one, and an event published
during delivery waits its turn.

## Subscriber lifetime

A bound method is held through `weakref.WeakMethod`, so an abandoned `TrackingHistory` is not kept
alive. A lambda is held strongly. A plain list of callables keeps every subscriber, stops at the
first failure and iterates live, and it runs the same tables as a comparison.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/22-observer
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
