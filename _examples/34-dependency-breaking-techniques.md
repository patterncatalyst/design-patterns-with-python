---
layout: example
order: 34
title: "Dependency-breaking techniques"
description: An inherited rating engine changed one technique at a time, with one characterisation table run against every step, a test that the table can fail, and what mypy checks at each step.
github_path: examples/34-dependency-breaking-techniques
card_eyebrow: "Changing inherited code · Dependency breaking"
card_blurb: "A rating engine written before anyone tested it. Pin what it does, change its structure one step at a time, and run the same table after each step."
card_title: "One table, every step"
---

One shipping domain witnesses the argument. A rating engine asks two carriers for a price and adds
a margin. Both carrier SDKs are stand-ins that do no I/O and raise a timeout, so a test that
reaches them fails.

## Pin what the code does today

A table of five consignments records the carrier, the total and the carrier calls the legacy
engine produces: the cheaper carrier each way, a tie, half-up rounding and truncated grams. A
separate test pins that a timeout fails the whole quote. The same table runs against every step.

## Three steps

The constructor takes the carriers as keyword parameters with the real calls as defaults. The
AIRCO SDK is wrapped into the same shape as FASTLINE. The class becomes a function whose carriers
are a required mapping, bound once at the root with `partial`.

## The table can fail

Two altered engines, one that rounds grams and one that rounds half to even, each fail exactly
the row they change.

## Subclass and override

The one comparison form passes the same table. A misspelt override reaches the real carrier, and
mypy reports it only when the method carries `@override`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/34-dependency-breaking-techniques
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
