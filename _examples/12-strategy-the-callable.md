---
layout: example
order: 12
title: "Strategy: the callable"
description: Rate quotes priced by a flat rule, a per-kilogram partial and a zone rule object, chosen by name from a read-only registry, with tests for what a quote can record and what mypy checks in the slot.
github_path: examples/12-strategy-the-callable
card_eyebrow: "Selecting behaviour · Strategy"
card_title: "Strategies as callables in a registry"
card_blurb: "A read-only registry of pricing callables, a partial and a frozen rule object, a quote that records the rule key, and a class-per-strategy fixture that passes the same table."
---

One rating model witnesses what Strategy becomes when a rule is a callable. Each test asserts the
behaviour named in its title.

## Selecting a rule by name

`RATE_RULES` is a `Mapping` over a 3.15 `frozendict`, so item assignment raises. `quote` looks a
rule up by name, records the name and raises `RatingError` for an unknown one.

## Configured rules

A function, a `partial` and a frozen dataclass with `__call__` all fill the `PricingRule` slot.
They differ in what an audit can recover: a `partial` and a rule object have no `__name__`, a
`partial` has no value equality, and a rule object compares, hashes and prints by value. A rule
that counts its calls isn't reproducible.

## The class-per-strategy comparison

A test fixture with an abstract strategy and three subclasses runs the same behaviour table as
the registry. An `ast` count reports four strategy classes against one.

## What mypy checks

Each registry entry is checked against the slot type, including a lambda's body and a class
registered where an instance belongs. A `partial` that binds nothing is accepted and fails when
called.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/12-strategy-the-callable
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
