---
layout: example
order: 10
title: "Context managers: deterministic cleanup"
description: A manifest writer that commits a partial file only on success, in class, generator and ExitStack forms, with tests for what with guarantees and what the author still decides.
github_path: examples/10-context-managers
card_eyebrow: "Python substrate · Context managers, Resource Acquisition"
card_title: "Release on every path, committed on success"
card_blurb: "A manifest writer with __enter__ and __exit__, the generator form and why it needs try, an ExitStack that unwinds in reverse, and what mypy reads from __exit__'s return type."
---

One manifest writer witnesses what `with` guarantees. Each test asserts the behaviour named in
its title.

## Release on every path

`ManifestWriter` writes to a `.partial` file, closes the handle on every exit and replaces the
final file only when the block succeeds. The generator form `manifest_file` has the same contract
through `try`, `except` and `else`, and without `try` the cleanup is skipped on an exception
while mypy stays silent.

## Several resources

`write_manifests` enters one writer per manifest on an `ExitStack`. When a later open fails, the
writers already entered exit in reverse order and discard their partial files.

## What __exit__ returns

A truthy return swallows the exception, and `contextlib.suppress` swallows one named exception
only. mypy reads the return type: `-> None` makes the code after a raising `with` unreachable,
`-> bool` doesn't.

## Python 3.15

A context manager used as a decorator on a generator function stays entered across iteration.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/10-context-managers
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
