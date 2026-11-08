---
layout: example
order: 28
title: "singledispatch: the Visitor the language gives you"
description: A customs tariff lookup and a container surcharge method built on functools.singledispatch, with a raising and a defaulting fallback on one table, registration by annotation, another team's module that extends the set, and what mypy does and does not check.
github_path: examples/28-singledispatch
card_eyebrow: "Idiomatic Python · singledispatch"
card_blurb: "One generic function replaces the visitor class. A raising fallback names the unregistered kind, and a registration made in another module exists only once that module is imported."
card_title: "Fallbacks, registration and what mypy cannot see"
---

One shipping domain witnesses the open form of Visitor. A customs declaration needs a tariff code
per commodity kind, and the dangerous goods team adds kinds the customs team does not own. Each
test asserts the behaviour named in its title. No test registers on the real dispatcher: a
registration is process-wide and cannot be undone, so tests use a fresh dispatcher each, and the
cross-module claim runs in a fresh interpreter.

## One function, one implementation per kind

`tariff_code` has an `object` fallback that raises `TariffCodeError`, and an annotated
implementation for `Coffee`, `InstantCoffee` and `TShirt`. The most specific registration wins, an
unregistered subclass takes its base class's code, and `dispatch` and the read-only `registry` show
the choice. A union annotation registers each member.

## The fallback is a decision

A defaulting fallback over the same implementations gives the same codes on one table of seven
commodities, and answers `"unclassified"` for a battery without an error. The raising fallback
names the kind.

## What fails at registration, and what mypy checks

A forward reference raises `TypeError` at the decorator, and mypy accepts it. mypy checks calls and
registrations against the fallback's signature, refuses a kind outside a union fallback, and accepts
a `register(cls, fn)` whose class differs from the function's parameter.

## Another module extends the set

`dangerous_goods` registers `LithiumIonBattery`. In a fresh interpreter a battery raises before that
module is imported and gets its code after.

## singledispatchmethod

`SurchargeSchedule.surcharge` dispatches on one argument, the container kind, which is the argument
after `self`.
mypy does not check its arguments.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/28-singledispatch
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
