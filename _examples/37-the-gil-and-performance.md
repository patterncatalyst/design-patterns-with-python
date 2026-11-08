---
layout: example
order: 37
title: "The GIL and performance"
description: Two threads reserving a slot on one sailing, a batch of consignments rated through thread, process and interpreter pools, and a benchmark kept out of the tests.
github_path: examples/37-the-gil-and-performance
card_eyebrow: "Concurrency · The GIL and performance"
card_blurb: "Two threads parked between reading and writing take the same slot on either CPython build. A lock that covers the read gives each its own, and a benchmark script holds every timing."
card_title: "Slot reservation and rating pools"
---

One shipping domain witnesses the argument. A sailing's `StowagePlan` hands out `SlotId`s, and a
batch of consignments is rated by a CPU-bound `quote` function.

## The GIL is not your lock

A `threading.Barrier` parks two threads between picking a slot and storing it. With no lock both
threads take the same slot and one reservation survives, on the default and the free-threaded
build alike. With a lock held across the read and the write, each thread takes its own slot. A
test reads the bytecode to show that `+=` on an attribute is a separate load, add and store.

## Pools

`rate_batch` rates a batch through a thread, process or interpreter pool and returns the answers
of the serial loop. A thread pool shares the list it is given, and a process or interpreter pool
works on a copy. A process pool refuses a lambda. A coroutine that never awaits holds the event
loop until it returns.

## Two builds

`gil_disabled_build` and `gil_enabled` report which CPython build is running and whether its GIL
is on. The tests hold on both builds.

## The benchmark

`bench/gil_bench.py` times the batch and some waits. `bench/lost_update_probe.py` counts the trials
in which four unlocked threads lose an update. No test asserts a timing or a count, and the recorded
outputs for each build sit beside the scripts.

## What mypy checks

`sysconfig.get_config_var` is typed `Any`, so returning its comparison from a function declared to
return `bool` is a `no-any-return` error. `build.py` wraps the answer in `bool`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/37-the-gil-and-performance
uv run pytest -v
uv run mypy --strict src tests
uv run python bench/gil_bench.py --cpu-class "16-thread x86-64 CPU"
uv run python bench/lost_update_probe.py --cpu-class "16-thread x86-64 CPU"
```

The example README lists what each test verifies and how to run the tests on the free-threaded
build.
