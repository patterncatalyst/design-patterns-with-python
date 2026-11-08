---
layout: example
order: 17
title: "Builder, dataclasses, and Prototype"
description: A twelve-field booking request as a keyword-only dataclass beside a positional constructor and a fluent builder on one booking table, and templates copied with replace, with tests for what mypy checks and what a copy shares.
github_path: examples/17-builder-dataclasses-and-prototype
card_eyebrow: "Creating objects · Builder and Prototype"
card_title: "A keyword-only request, and templates copied with replace"
card_blurb: "A frozen dataclass names every argument and validates once, a positional constructor and a fluent builder run the same table as comparisons, and replace and copy.replace copy a template and rerun its checks."
---

One shipping domain witnesses what Builder and Prototype become in Python. Each test asserts the
behaviour named in its title.

## Builder

`BookingRequest` has twelve fields, four of them required, and every argument is named. Its
post-init checks run once. A positional constructor and a fluent builder pass the same four-case
table in tests. mypy reports a swap across types in the positional form, misses a swap of two
`str`, and accepts a builder with a step left out, which fails when `build` runs.

## Prototype

A read-only table of template requests, copied with `replace`. `replace` and `copy.replace` rerun
the cross-field checks, and mypy checks both. `copy.copy` and `replace` share a list field,
`copy.deepcopy` separates it, and a tuple field removes the question.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/17-builder-dataclasses-and-prototype
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
