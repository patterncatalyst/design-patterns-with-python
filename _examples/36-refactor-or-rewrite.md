---
layout: example
order: 36
title: "Refactor or rewrite"
description: A legacy rating engine and a bisect-based rewrite held to the same quotes by a parity table, joined by a router that moves one zone at a time and runs the rewrite in shadow for the rest.
github_path: examples/36-refactor-or-rewrite
card_eyebrow: "Changing inherited code · Refactor or rewrite"
card_blurb: "A first draft of the rewrite moves 5, 20 and 50 kg into the next band. A parity table lists every row where the two engines differ, and a router serves one zone at a time."
card_title: "Parity table and strangler-style router"
---

One shipping domain witnesses the argument. A legacy rating engine prices a consignment by weight
band in an `if`/`elif` chain. A rewrite holds the bands as data and finds one with `bisect_left`.

## The parity table

Seventeen rows put weights either side of each band limit, on it, and above the last band, for two
zones, plus one unknown zone. The rewrite differs from the legacy engine on one row, the unknown
zone, which is recorded in `ACCEPTED_DIFFERENCES`. A first draft that uses `bisect_right` differs
on seven rows: each limit weight in each zone, and the unknown zone.

## A strangler-style router

`Router` serves migrated zones from the rewrite and every other zone from the legacy engine. In
shadow mode it also runs the rewrite on the other zones, reports a difference or a refusal as a
`Mismatch`, and serves only the legacy quote. With every zone migrated the legacy engine is never
called. The router routes calls and converts no interface, so it is not the Adapter pattern.

## What mypy checks

A rewrite that takes a zone and a weight is rejected where it is passed to `Router`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/36-refactor-or-rewrite
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
