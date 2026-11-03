---
layout: example
order: 0
title: "Prerequisites smoke test: a frozen Consignment"
description: A small shipping model that exercises uv, Python 3.14, ruff, mypy in strict mode and pytest end to end.
github_path: examples/00-prerequisites
card_eyebrow: "Orientation · Toolchain"
card_title: "A frozen Consignment that proves the toolchain"
card_blurb: "A frozen, slotted Consignment built from validated ConsignmentId and Weight value types and amended with dataclasses.replace. It passes ruff, mypy --strict and pytest, so a green run means the environment is ready for every other demo."
---

A small shipping model exercises the whole toolchain: uv, Python 3.14, ruff,
mypy in strict mode and pytest. If the commands below pass, the environment is
ready for the other demos.

## The model

`src/consignments/consignment.py` defines three immutable value types:

- `ConsignmentId`: a reference of the form `CN-` followed by eight digits.
- `Weight`: a mass in kilograms, finite and greater than zero.
- `Consignment`: an id, an origin and destination port code (five uppercase
  letters, as in a UN/LOCODE) and a weight. `reweigh` returns an amended copy
  built with `dataclasses.replace`.

All three are frozen, slotted dataclasses. Each validates in `__post_init__` and
raises `ValueError` on bad input, so an invalid instance cannot exist.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the demo directory:

```bash
cd examples/00-prerequisites
uv run pytest
uv run mypy --strict src tests
```

From the repository root, the lint and format checks:

```bash
uv run ruff check examples/00-prerequisites
uv run ruff format --check examples/00-prerequisites
```

## What the tests verify

- Equal values compare equal, and equal consignments hash alike, so they work as
  dict keys and set members.
- `reweigh` returns a new consignment with the new weight and leaves the original
  unchanged.
- Assigning to a field raises `dataclasses.FrozenInstanceError`.
- Malformed ids, non-positive or non-finite weights, and port codes that are not
  five uppercase letters raise `ValueError`.
