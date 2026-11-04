---
layout: example
order: 11
title: "Proving it works: pytest, pytest-mock, and mypy"
description: A rating engine tested with fixtures, a hand-written fake and three kinds of mock, an injected clock and a restored environment, with mypy checking the tests themselves.
github_path: examples/11-testing-with-pytest-pytest-mock-and-mypy
card_eyebrow: "Python substrate · Testing baseline"
card_title: "A test is evidence for one named claim"
card_blurb: "A rating engine that books only the cheapest carrier, tested with a checked fake, Mock, Mock(spec=) and create_autospec, an injected clock, a restored environment and mypy over the tests."
---

One rating engine witnesses what each test tool proves. Each test asserts the behaviour named in
its title.

## Fixtures and parametrize

`conftest.py` supplies a consignment, a fixed instant, a factory for fake gateways and a `yield`
fixture whose teardown runs on failure. Parametrized cases carry ids that name the claim.

## What each double checks

A plain `Mock` passes an assertion on a misspelled method. `Mock(spec=...)` rejects the unknown
name but accepts a call with the wrong signature. `create_autospec(..., instance=True)` rejects
both. mypy accepts every mock where a `CarrierGateway` is expected and checks a hand-written fake.

## Time and process state

The engine takes a clock and a validity, asks carriers in code order and breaks a tie by carrier
code. The environment is changed only inside `monkeypatch.context()` and is restored on exit.

## mypy as a test

`assert_type` fails the mypy run and does nothing at runtime. The mypy API helper asserts the exit
status and the exact set of error codes.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/11-testing-with-pytest-pytest-mock-and-mypy
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
