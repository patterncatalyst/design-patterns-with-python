---
title: "Evidence: yield-fixture teardown runs when the test fails"
output: false
render_with_liquid: false
---

# `yield` fixture teardown on a failing test

Recorded 2026-11-04 (r05) for claim 64, on Python 3.15.2 and pytest 9.2.0. The pytest fixtures
how-to says teardown runs once the test is finished; it doesn't state the failure case, so this
run is the evidence for it.

Scratch copy of the repo; one change in
`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py`: the assertion in
`test_quote_validity_comes_from_the_injected_clock` expects `timedelta(minutes=46)` instead of 45, so
the test fails. The test uses the `quote_log` yield fixture from `tests/conftest.py`, whose code
after `yield` writes `quote_log teardown: <name>` to stdout.

Command, from the example directory:

```
uv run pytest -s -q -p no:cacheprovider --tb=no -k test_quote_validity_comes_from_the_injected_clock
```

Output (filtered with `scripts/host_ids.py filter`):

```
Fquote_log teardown: quotes.log

=========================== short test summary info ============================
FAILED tests/test_engine.py::test_quote_validity_comes_from_the_injected_clock
1 failed, 33 deselected in 0.03s
```

The `F` is followed by the teardown line: the code after `yield` ran although the test failed.
