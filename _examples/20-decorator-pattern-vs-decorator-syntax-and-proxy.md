---
layout: example
order: 20
title: "Decorator the pattern vs @decorator the syntax, and Proxy"
description: A stack of rate layers chosen per consignment, the retry and audited factories that rebind a function name at definition time, and a caching gateway proxy, with tests for order, value equality and what mypy sees through each form.
github_path: examples/20-decorator-pattern-vs-decorator-syntax-and-proxy
card_eyebrow: "Structure · Decorator and Proxy"
card_blurb: "Layers stack while the program runs and compare by value; the @ form rebinds a name once. An explicit caching proxy is checked by mypy, and a forwarding proxy runs the same table as a comparison."
card_title: "Two things called Decorator, and a proxy"
---

One shipping domain separates three wrapper-shaped things. Each test asserts the behaviour named
in its title.

## The Decorator pattern

`Discount`, `Surcharge` and `Tax` are frozen dataclasses with the interface of the calculator
they wrap. `compose` puts the last layer outermost and `layers_for` chooses the layers for a
consignment while the program runs. An additive fee makes the order change the price, and two
percentages that agree before rounding split by a cent after it. A stack compares and hashes by
value.

## The `@decorator` syntax

`retry` and `audited` are factories that rebind a function name once, when the `def` runs. Stacking
order is fixed there: an audit above a retry reports once per call, and below it once per attempt.
A rebound function doesn't compare by value and has no `price`.

## Proxy

`CarrierGatewayProxy` has the gateway's interface and controls access: it asks for each
consignment's quote once and forwards every booking. mypy checks every member of the Protocol on
it. A `__getattr__` form passes the same table, and mypy accepts typos through it.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/20-decorator-pattern-vs-decorator-syntax-and-proxy
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
