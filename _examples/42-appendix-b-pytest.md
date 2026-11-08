---
layout: example
order: 42
title: "pytest reference"
description: A pytest reference whose rows name their witnesses, most of them tests, and most of those run through an inner pytest session with pytester, which asserts the outcome counts, the node ids or the exit status.
github_path: examples/42-appendix-b-pytest
card_eyebrow: "Appendices · pytest reference"
card_blurb: "Each row of the reference names its witness, and most are tests on the pinned pytest. Strictness options, import modes and command-line options run in an inner session, and the test asserts the outcome counts or the exit status."
card_title: "pytest run inside pytest"
---

One small rating module carries the examples. `quote` prices a `Consignment` by weight and zone,
`rate_batch` raises one exception group holding every failure, `legacy_quote` is deprecated, and
`write_quotes` writes lines to the stream it is given, or to the current `sys.stdout` when it is
given none.

## Inner sessions

Tests of configuration, import modes, command-line options, fixture order and case ids write a
project into a temporary directory, run pytest on it with the `pytester` fixture and assert the
outcome counts, the node ids or the exit status. Each test module that uses `pytester` loads it
with `pytest_plugins`. The same line in a `conftest.py` below the root fails collection, and a
test asserts that.

## Fixtures, parametrisation and assertions

Yield order, fixture scope, factory, `autouse`, `usefixtures`, indirect parameters and
`getfixturevalue` each have a test, as do `pytest.param` ids and marks, stacked parametrisation,
`tmp_path`, `capsys`, `caplog`, `pytest.raises` with `match` and `check`, `RaisesGroup` and
`pytest.warns`. One static test shows mypy checking the use of a typed fixture.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/42-appendix-b-pytest
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
