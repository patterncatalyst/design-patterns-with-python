---
layout: example
order: 24
title: "Iterator: generators and the iterator protocol"
description: A tracking history that hands each loop a fresh iterator, lazy paging with itertools, and a log reader that opens inside with and closes on close(), with a self-iterating cursor as the comparison.
github_path: examples/24-iterator-generators-and-the-iterator-protocol
card_eyebrow: "Traversal · Iterator"
card_blurb: "A generator replaces the cursor class. The history walks many times, pages read one batch at a time, and a reader closes its file when it is closed or collected, not when a loop over a named reader breaks."
card_title: "One pass or many, how much to read, who closes"
---

One shipping domain witnesses the pattern: a tracking history of handling events. Each test asserts
the behaviour named in its title.

## The protocol

`TrackingHistory.__iter__` is a generator, so every loop gets a fresh iterator and the history can
be walked twice or nested. A cursor written to the protocol, with `__iter__` returning itself, passes
the same traversal table and is then empty on the second pass and cuts a nested walk short. An
exhausted generator looks empty, and mypy can't see a second pass over an iterator.

## Reading only what you need

`pages` uses `itertools.batched`: the first page of a million-event source pulls three events, where
an eager list pulls them all. `page` uses `islice`, `out_of_order` uses `pairwise` and `events_of`
uses `chain.from_iterable`.

## Delegation and cleanup

`read_events` opens a tracking log inside a `with` block and returns the line count through `yield
from`. `close()` closes the file, `break` leaves a named reader open, and `contextlib.closing` closes
it at the end of the block. mypy refuses `close()` and `closing()` on an `Iterator`, so the reader is
annotated `Generator`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/24-iterator-generators-and-the-iterator-protocol
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
