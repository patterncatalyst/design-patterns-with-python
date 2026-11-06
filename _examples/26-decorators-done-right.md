---
layout: example
order: 26
title: "Decorators done right"
description: A bill-of-lading renderer wrapped by a timer and a cache with injected clocks, with what functools.wraps copies and gets wrong, ParamSpec and Concatenate for mypy, a keyword-only factory that refuses bare use, stacking order, a class decorator above a slotted dataclass, and decorated methods.
github_path: examples/26-decorators-done-right
card_eyebrow: "Idiomatic Python · Decorators"
card_blurb: "The order of a stack decides what a cache hides from a timer. functools.wraps keeps a renderer's identity for runtime tools, ParamSpec keeps its signature for mypy, and a class decorator belongs above a slotted dataclass."
card_title: "Identity, signatures, factories, stacking and registries"
---

One Documentation domain witnesses the discipline behind the `@` syntax. A portal renders bills of
lading, caches them for a window and times the work. Each test asserts the behaviour named in its
title, and no test sleeps: every clock is injected.

## Identity and signature

`timed_render` uses `functools.wraps`, so the renderer keeps its name, docstring and `__wrapped__`.
A bare wrapper renders the same text and loses all three, yet mypy still sees the signature through
`ParamSpec`. A decorator that supplies an argument shows where `wraps` misleads: `inspect.signature`
reports parameters the wrapper does not take, and `functools.partial` reports the ones that remain.

## Factories and stacking

`cached_for(*, seconds, clock=...)` takes its window by keyword, so using it bare fails when the
module loads. A positional factory used bare returns a function where text was expected, with no
error. With the timer outside the cache every call is timed, and inside it only the miss is.

## Class decorators and methods

`document_kind` registers `BillOfLading` and `Manifest` and is placed above `@dataclass(slots=True)`,
because beneath it the registered class is the one that is thrown away. A function wrapper binds
`self` on a method and a class-based wrapper does not. `functools.cache` on a method keeps the
instance alive.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/26-decorators-done-right
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
