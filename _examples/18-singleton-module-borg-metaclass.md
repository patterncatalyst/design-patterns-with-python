---
layout: example
order: 18
title: "Singleton: module, Borg, and metaclass"
description: A tariff table built at import time, loaded on first use with a lazy import, passed in as a parameter, or loaded once under threads with a double-checked lock, beside Borg, metaclass and new-based fixtures on one table.
github_path: examples/18-singleton-module-borg-metaclass
card_eyebrow: "Creating objects · Singleton"
card_title: "A module, a lazy import and a load that runs once"
card_blurb: "The tariff table is a module attribute, loaded on first use with a lazy import, and a lock with a double check keeps a run-time load to one. Borg, a metaclass and a new-based form run the same table as comparisons."
---

One shipping domain witnesses what Singleton becomes in Python. Each test asserts the behaviour
named in its title.

## The module and the lazy import

`tariff_table.TARIFF` is built when the module is first imported, and every importer gets that
object. A `lazy from` import defers the load to the first quote. `quote` takes the table it is
given, so a test builds its own. mypy still checks attributes through the lazy import.

## Once, under threads

A `functools.cache` loader runs twice when two threads arrive together. `LoadOnce` keeps the result
behind a lock with a double check, and a test forces the interleaving with a lock that waits on a
`Barrier`. A loader that returns `None` still runs once because the marker is a sentinel.

## Comparison fixtures

Borg, a metaclass singleton and a `__new__` singleton run the same table of callers as the module, `LoadOnce` and the cache. Five of the six forms load once and the `__new__` form loads twice.
Borg instances are distinct and unequal, the metaclass ignores a second call's arguments, and the
`__new__` form reruns `__init__` and rewrites the shared table.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/18-singleton-module-borg-metaclass
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
