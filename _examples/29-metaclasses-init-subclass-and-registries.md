---
layout: example
order: 29
title: "Metaclasses, __init_subclass__, and registries"
description: A carrier registry filled by a class keyword on __init_subclass__, with refusals at definition, registrations that depend on imports, a metaclass form on the same table of cases, and what mypy checks about each.
github_path: examples/29-metaclasses-init-subclass-and-registries
card_eyebrow: "Idiomatic Python · Class registries"
card_blurb: "A carrier registers by a class keyword, and a bad class is refused before it reaches the registry. The metaclass form passes the same table and conflicts with other metaclasses."
card_title: "Class keywords, refusals and imports"
---

One shipping domain witnesses the registry that dissolves into `__init_subclass__`. A booking
takes a carrier code and needs the gateway class for it, and other teams add carriers. Each test
asserts the behaviour named in its title. No test registers a carrier in the test process: every
class a test defines is refused before insertion, and a carrier that does register is checked in a
fresh interpreter.

## A registry filled at class creation

`CarrierBase.__init_subclass__` takes the code as a class keyword and inserts the class into a
read-only `registry`. `gateway_for` books through it and raises `UnknownCarrierError` for an
unknown code. The signature takes no extra keywords, so mypy checks the keyword's type and reports
a misspelt keyword with a suggestion.

## Refusing a bad carrier class

A duplicate code keeps the first class. A concrete class without a code and an abstract class with
one are refused, an abstract intermediate class is skipped, and an unknown keyword raises
`TypeError`. `inspect.isabstract` sees abstractness inside the hook. Every refusal leaves the
registry unchanged.

## Where registrations come from

`carrier_registry` imports no carrier module, so in a fresh interpreter the registry is empty until
each carrier module is imported. A forgotten dict entry becomes a forgotten import.

## The same registry as a metaclass

`_CarrierMeta` applies the same rules and passes the same table of bookings and refusals. A second
metaclass conflicts with an `ABC` or a `Protocol` base. mypy does not check a metaclass's class
keywords, and the reduced models show four more places where it differs. Only a metaclass gives
the class object `in`, `list` and `len`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/29-metaclasses-init-subclass-and-registries
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
