---
layout: example
order: 23
title: "Mediator and Chain of Responsibility"
description: A customs clearance chain written as a tuple of typed stages with a final stage that always decides, and a mediator that releases a consignment exactly once, after the duty and inspection it still owes have reported, with a linked chain, a match and colleagues that call each other as comparisons.
github_path: examples/23-mediator-and-chain-of-responsibility
card_eyebrow: "Coordination · Mediator and Chain of Responsibility"
card_blurb: "Stages return a decision or None to pass it on, the first decision wins, and the final stage is typed so it cannot pass. A mediator holds the release rule and its state, and a choreography shows what it replaces."
card_title: "Who decides, in what order, and when to release"
---

One shipping domain witnesses both patterns: customs clearance. A declaration passes along an
ordered chain of stages until one holds it, and a separate mediator releases it after the reports it is owed have arrived. Each
test asserts the behaviour named in its title.

## The chain

`clear(declaration, stages, /, *, final=release)` returns the first decision a stage makes. A stage
returns `None` to pass the declaration on, and stages after a decision aren't called. The final
stage is typed to always decide, so a stage that can pass is refused as the final stage by mypy.
Appending to the chain lands before the final stage. A stage placed after `release` inside the
chain isn't visible to the type checker, and it clears a restricted commodity at run time. A linked
chain and a single `match` run the same hold table as comparisons.

## The mediator

`ClearanceMediator` receives a closed union of messages through `match` and releases once, after
the duty and inspection it still owes have reported, in either order. A failed inspection holds the consignment.
Colleagues that call each other pass the inspection-first case and lose a settlement that arrives
before the inspection.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/23-mediator-and-chain-of-responsibility
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
