---
layout: example
order: 3
title: "The three-way split: nineteen witnesses"
description: One shipping model whose tests show which classic patterns Python dissolves, which remain design, and which share a name with something else.
github_path: examples/03-three-way-split
card_eyebrow: "Why Python is different · Three-way split"
card_title: "Nineteen tests that sort the patterns"
card_blurb: "A shipping model where each test proves one claim: Strategy as a callable, Iterator as a generator, Visitor as singledispatch, Null Object checked by mypy, Command with undo, and the Decorator pattern kept apart from the @ syntax."
---

One shipping model witnesses the three-way split of the classic patterns. Each test
asserts the mechanism named in its title, not only a value.

## Dissolve

A language feature does the work:

- Strategy is a callable: a function, a lambda or a `functools.partial` fills the
  `PricingRule` slot of `quote`.
- Factory Method is a class stored in a dict.
- Iterator is a generator; `pages` reads a `TrackingHistory` one page at a time.
- Template Method is a function that takes hooks.
- Builder is a keyword-only dataclass, and Prototype is `dataclasses.replace`.
- Visitor is `functools.singledispatch`, with no `accept` method on the events.
- Null Object is an optional, and `mypy --strict` rejects the unguarded call with
  `[union-attr]`.
- Value Object is a frozen dataclass (`Money`), and Registry is `__init_subclass__`.

## Survive

A deferred call is a `functools.partial` in a `collections.deque`. Undo is different: it
needs a command object that remembers what it replaced, and `Amendment` is that object.

## Disambiguate

- The Decorator pattern wraps an instance at runtime (`Surcharge` around `BaseRate`). The
  `@audited(sink)` syntax rebinds a function name at definition time. The tests show the two
  are independent.
- A module is the Singleton: `tariff_table` builds `TARIFF` once, and a separate log
  records the single load.
- `functools.cached_property` gives lazy initialisation without a proxy, and
  `CarrierGatewayProxy` forwards only the attributes it does not define.
- A `Protocol` is structural, while an abstract base class is nominal.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/03-three-way-split
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
