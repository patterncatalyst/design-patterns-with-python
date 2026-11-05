---
layout: example
order: 9
title: "Protocol and structural typing: absence and interfaces in the type"
description: Carrier lookup and pricing written with Protocol, an optional return, a sentinel and an ABC, with tests for what mypy checks, what the runtime checks and what neither does.
github_path: examples/09-protocol-and-structural-typing
card_eyebrow: "Python substrate · Protocol, Null Object"
card_title: "Interfaces as shapes, absence as a type"
card_blurb: "A carrier lookup that returns an optional gateway, a Protocol beside an ABC, a callback Protocol, inferred variance, and the checks runtime_checkable does and doesn't make."
---

One carrier model witnesses where each check happens. Each test asserts the behaviour named in
its title.

## Absence in the type

`find_gateway` returns `CarrierGateway | None`, so unguarded access is a mypy error and four
narrowing forms clear it. A do-nothing gateway loses a booking and mypy accepts it, while
`no_discount` stays a correct null object. A 3.15 `sentinel` separates "not given" from `None`,
and the carrier registry is a `frozendict`.

## Generics and callbacks

`Quoter[T: Consignment]` has its variance inferred: a general quoter serves hazmat consignments
and the reverse is rejected. `PricingRule` takes its argument positional-only, so functions with
any parameter name qualify.

## Protocol or ABC

An ABC refuses an incomplete subclass at construction and shares code. The Protocol is compared
where the value is passed, and `AircoGateway` satisfies it while inheriting the ABC. Subclassing
a Protocol explicitly makes the class nominal, and `typing.override` catches a misspelling.

## What runtime_checkable checks

Names only. A wrong signature and a non-callable attribute pass `isinstance`, a data protocol
refuses `issubclass`, and on 3.15 an undecorated sub-protocol warns.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/09-protocol-and-structural-typing
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
