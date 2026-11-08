---
layout: example
order: 19
title: "Adapter, Facade, and Bridge"
description: Two carrier SDKs of different shapes behind one gateway Protocol, a desk function as the facade, and booking kinds that vary independently of the carriers, with tests for what mypy checks and what units hide.
github_path: examples/19-adapter-facade-bridge
card_eyebrow: "Structure · Adapter, Facade, Bridge"
card_title: "One adapter, one facade call, two booking kinds"
card_blurb: "A client whose shape already matches needs no adapter, and Fastline's SDK gets one that converts pounds and errors in a single place. A class adapter, a class per kind and carrier, and a branching caller run the same tables as comparisons."
---

One shipping domain witnesses what the three structural patterns become in Python. Each test
asserts the behaviour named in its title.

## Adapter

`AircoClient` already has the shape of the `CarrierGateway` Protocol and sits in the registry
unwrapped. `FastlineClient` takes a payload of strings in pounds and a cover amount in cents, so
`FastlineGateway` translates call shape, units and errors in one class. A parameter typed
`Weight` makes mypy catch a units mix-up that a `float` hides. A class adapter passes the same
table and leaks the SDK's own methods.

## Facade

`ship` is one module function with a narrow public surface. It picks the gateway from a read-only
registry, chooses the booking kind and turns an unknown code into a domain error. Its signature
names no SDK type. A caller that branches on the carrier code sends kilograms to a pounds API.

## Bridge

`StandardBooking` and `InsuredBooking` each hold a gateway and build their operation from its two
primitives. Every kind works with every carrier, with two classes where a class per kind and
carrier needs four. The cost sits on the implementor: a gateway that lacks a primitive is a mypy
error.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/19-adapter-facade-bridge
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
