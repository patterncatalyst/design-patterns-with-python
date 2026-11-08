---
layout: example
order: 38
title: "asyncio and the patterns"
description: A carrier feed as an async generator, a session that survives cancellation, quotes run in a task group, an async Observer and a command queue that shuts down.
github_path: examples/38-asyncio-and-the-patterns
card_eyebrow: "Concurrency · asyncio and the patterns"
card_blurb: "An await between reading and writing lets five tasks take one slot. A feed closes through aclosing, quotes run in a task group, an async signal runs every subscriber, and a command queue shuts down without a sentinel."
card_title: "Feeds, quotes, signals and queues"
---

One shipping domain witnesses the argument. A carrier's tracking feed, two carriers' rate quotes, a
signal for handling events, a queue of booking commands and a sailing's slot reservation all run on
one event loop. The carriers are in-memory stand-ins.

## An await changes the edges

A coroutine called without `await` is a coroutine and not a quote. mypy reports one that is returned
or dropped, and the runtime warns about one that is never awaited. Five tasks parked at an `await`
between reading a slot and storing it all take the same slot, and an `asyncio.Lock` gives each its
own.

## Iterator and context manager

`handling_events` is an async generator. Breaking out of `async for` leaves the feed open, and
`first_departure` closes it with `contextlib.aclosing`. `carrier_session` closes the feed when its
body raises and when its task is cancelled.

## Strategy and Adapter

`RateSource` is a Protocol with an `async def quote`, and mypy refuses a blocking source. `AircoSource`
adapts a blocking SDK with `asyncio.to_thread`. `cheapest` asks every source in a `TaskGroup`:
a failing source cancels the other quote, a zero timeout cancels a quote that never answers, and
`first_quote` stops the group at the first answer with `TaskGroup.cancel()`.

## Observer and Command

`AsyncSignal.publish` runs every subscriber and then raises one `ExceptionGroup` of the failures. A
publisher built on a `TaskGroup` cancels the other subscribers instead. `run_commands` drains a queue
of coroutine commands, records a failure and carries on, and `Queue.shutdown()` stops it without a
sentinel.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/38-asyncio-and-the-patterns
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies and how to run the tests on the free-threaded
build.
