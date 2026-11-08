---
layout: example
order: 32
title: "Anti-patterns and pattern misuse"
description: A rating function measured against a class-per-role engine on one table of quotes, with the cost of a new charge kind, an accessor consignment and a service locator.
github_path: examples/32-anti-patterns-and-pattern-misuse
card_eyebrow: "Patterns in the wild · Anti-patterns"
card_blurb: "One rating function and a factory, strategy and visitor quote the same table. mypy and ruff pass both, so the structure is counted with ast and call counts."
card_title: "Measuring structure against the function"
---

One shipping domain witnesses the argument. A consignment is quoted from a flat fee for its zone, a
fuel fee and tax rounded to the cent. The plain function is the lesson, and every other form is a
test fixture that runs the same table of quotes.

## The function and its twin

`quote(consignment, tariff)` takes a frozen `Tariff` and raises `RatingError` for an unknown zone.
The comparison is a nine-class engine in conftest: a factory of strategies of visitors for one flat
fee. Both quote `EU` 35.70 and `ASIA` 78.05.

## What the structure costs

`ast` counts classes, functions and lines, and finds the fuel surcharge in one definition of the
function and five of the engine. `sys.setprofile` counts the Python functions a quote enters: one for the function and
eleven for the engine. mypy `--strict` and ruff pass both, so none of this is reported by a tool. A
new charge kind fails at run time in the visitor, and declaring its method makes every concrete
visitor abstract.

## Getters, setters and a locator

An accessor consignment has no value equality, and its setter changes the quote of a consignment
that was already quoted. A service locator moves a missing tariff from a mypy error to the first
quote.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/32-anti-patterns-and-pattern-misuse
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
