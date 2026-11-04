---
layout: example
order: 13
title: "Template Method and the function alternative"
description: Customs declarations issued by a function that takes hooks and by a final template method on a class family, with tests for the fixed steps, the required hooks and what mypy and the runtime enforce.
github_path: examples/13-template-method-and-the-function-alternative
card_eyebrow: "Selecting behaviour · Template Method"
card_title: "Fixed steps, hooks and a final template"
card_blurb: "A customs skeleton that no hook can reorder, required and defaulted hooks, and an abstract declarer for destinations that share a schedule, both forms giving the same declaration."
---

One customs model witnesses what Template Method becomes in Python. Each test asserts the
behaviour named in its title.

## The function form

`declare_customs` fixes the order of the steps and the invariant checks: no commodities, one
currency, the commercial invoice first. `CustomsHooks` supplies the rest. `classify` and `duty`
have no default, so a missing one fails at construction and under mypy. `extra_documents` has a
default.

## Defaults in a Protocol

A default body in a Protocol reaches an explicit subclass and not a class that only matches
structurally. mypy requires every member for a structural match.

## The class form

`CustomsDeclarer` shares a classification and a schedule across destinations and leaves
`extra_documents` abstract. Its `declare` is `@final` and hands its own bound methods to
`declare_customs`, so the skeleton exists once and both forms give the same declaration.

## Keeping the skeleton fixed

An override that skips a base step issues a declaration with no lines, and mypy accepts it.
`typing.final` makes overriding the template a mypy error, while the runtime only sets
`__final__`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/13-template-method-and-the-function-alternative
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
