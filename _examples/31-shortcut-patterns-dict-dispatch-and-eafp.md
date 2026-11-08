---
layout: example
order: 31
title: "Shortcut patterns: dict dispatch, function tables, and EAFP"
description: A read-only table of document issuers over an enum, checked for signatures by mypy and for totality by a test, and a duty-rate cache read in one lookup, with a look-first form on the same table and a race forced through a storage seam.
github_path: examples/31-shortcut-patterns-dict-dispatch-and-eafp
card_eyebrow: "Patterns in the wild · Dispatch tables and EAFP"
card_blurb: "A table of callables replaces an if-chain, and mypy checks every entry but not that every kind has one. A cache read in one lookup survives an eviction that breaks check-then-read."
card_title: "Tables, totality and asking forgiveness"
---

One shipping domain witnesses both shortcuts. A consignment needs a bill of lading, a manifest and a
customs declaration issued by kind, and duty rates come from a cache that other threads evict from.
Each test asserts the behaviour named in its title, and the loader records every call, so a load is
counted and never timed.

## A table of callables

`ISSUERS` is a `frozendict` of issuers keyed by `DocumentKind`. `issue` puts only the lookup inside
`try` and calls the issuer after it, so an issuer's own `KeyError` isn't reported as an unsupported
kind. mypy checks each entry's signature and the key type of a lookup, refuses assignment, and
rejects calling the `None` that `.get` may return. It accepts a table that misses a kind and an
if-chain whose `else` raises, so a test walks the enum.

## Choosing the form

`match` with `assert_never` and a chain with no `else` are reported by mypy when an arm is missing
(reduced models). `singledispatch` dispatches on type, so every member of `DocumentKind` reaches one
implementation. A table suits a set that arrives as data: another table passed by the caller, or a
kind parsed from text. ruff reports a chain over string literals and not over enum members.

## Asking forgiveness

`declaration_from` reads required fields with `try`/`except KeyError` and names the missing one, and
reads the optional `origin` with `.get`. A `getattr` default and `hasattr` hide an `AttributeError`
raised inside a property, and `contextlib.suppress` ends its block at the first exception.

## The look-first race

`DutyRateCache` reads a rate once and reloads on a miss. A look-first form passes the same table of
hit, miss and evicted reads. A storage seam parks the first read on a `threading.Barrier` until
another thread has evicted: the look-first form raises `KeyError`, and the EAFP form reloads. Two
EAFP readers that both miss both load. Cost is benchmark-only: `bench/lookup_cost.py` prints it, and
no test asserts it.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/31-shortcut-patterns-dict-dispatch-and-eafp
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
