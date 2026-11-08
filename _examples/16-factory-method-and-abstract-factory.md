---
layout: example
order: 16
title: "Factory Method and Abstract Factory"
description: Carrier gateways built from a registry of constructors and carrier families held together as frozen kits, with tests for what mypy checks in a constructor slot and what a kit's reference type ties.
github_path: examples/16-factory-method-and-abstract-factory
card_eyebrow: "Creating objects · Factories"
card_title: "A registry of constructors and a kit per carrier"
card_blurb: "Self classmethods in a Callable slot as the factory method, a GoF creator hierarchy kept as a comparison, and a generic frozen kit whose reference type ties the gateway to the label printer."
---

One shipping domain witnesses what the two factory patterns become in Python. Each test asserts
the behaviour named in its title.

## Factory Method

A read-only registry maps a carrier code to `FastlineGateway.from_settings` or
`AircoGateway.from_settings`. Each classmethod returns `Self`, so a subclass builds itself, and the
registry slot is a `Callable`, which mypy checks against every constructor. A `type[...]` slot
accepts a class that can't be called without arguments. A GoF creator hierarchy passes the same
table in a test, with three classes where the registry declares none.

## Abstract Factory

A carrier added to two of three if-chains is quoted at another carrier's rate, and mypy says
nothing. `CarrierKit` holds one family's constructors as a frozen value. Its reference type ties
the gateway to the label printer, so a mixed kit is a type error. It doesn't tie the rate source,
and a printer that takes any `str` fits every family.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/16-factory-method-and-abstract-factory
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
