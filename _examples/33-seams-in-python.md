---
layout: example
order: 33
title: "Seams in Python"
description: An inherited rating engine and the patches that reach it, with where each patch lands, the guards that turn a miss into an error, the patches that cannot reach, and what mypy checks.
github_path: examples/33-seams-in-python
card_eyebrow: "Changing inherited code · Seams"
card_blurb: "A rating engine written before anyone tested it. Patch it where its names are looked up, see which patches miss, and see what mypy checks at each one."
card_title: "Patching where the name is looked up"
---

One shipping domain witnesses the argument. A rating engine asks two carriers for a price and adds
a margin. Both carrier SDKs are stand-ins that do no I/O and raise a timeout, so a test that
reaches them fails.

## The inherited engine

The legacy module imports the FASTLINE function by name and AIRCO as a module, and
`RateEngine.quote` calls both. Python looks those two names up when the call runs, so a test can
rebind them without editing the engine. The margin is captured as a default argument when the
class is defined, so a patch can't reach it.

## Where a patch lands

A patch on the module that defines the FASTLINE function leaves the engine calling the real
carrier, because the engine holds its own name. AIRCO is patched on its own module.
`monkeypatch` and `unittest.mock.patch` follow the same rule, and a misspelt name is refused
unless the call says otherwise. `autospec=True` refuses a call with the wrong signature that a
plain patch accepts.

## Patches that miss

A patched margin is not read by a default captured when the class was defined. A reload
overwrites a patch and leaves old bindings and instances behind, and runs in a fresh interpreter.
An object with a `price` method stands in for the AIRCO module, and one without it fails only when
called.

## What mypy checks

A monkeypatched replacement and a target string pass unchecked. A direct assignment to the module
name is reported. A patch is typed as a `MagicMock` union, and a fake passed to a Protocol
parameter is checked.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/33-seams-in-python
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
