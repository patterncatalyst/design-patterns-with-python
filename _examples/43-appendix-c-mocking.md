---
layout: example
order: 43
title: "Mocking reference"
description: A mocking reference whose API rows are tests of unittest.mock and pytest-mock against one carrier gateway, with the book's order of preference stated first.
github_path: examples/43-appendix-c-mocking
card_eyebrow: "Appendices · Mocking reference"
card_blurb: "Each API row of the reference is a test on the pinned pytest-mock. Autospecs, call records, patches, spies and stubs run against one carrier gateway, and two static tests show what mypy sees."
card_title: "A fake first, an autospec next, a patch last"
---

One small booking module carries the examples. `CarrierGateway` is a protocol with `quote` and
`book`, `FastlineGateway` implements it deterministically, `confirm` is async, and `book_cheapest`
books the cheapest carrier and passes the reference to a callback.

## Order of preference

A fake passed as a parameter comes first. `create_autospec` comes next, when the calls are the
claim. A patch is the last resort, for a name with no parameter to pass. The mocks appear in the
tests only, because the mock API is the subject; the source holds none.

## Doubles, calls and patches

`spec_set`, `seal` and the assertion typo each have a test for what they refuse. `wraps` has one
for the calls it passes through to the real gateway, and `MagicMock` and `AsyncMock` have tests for
what they add. Call records are read back with `mock_calls`, `call_args_list`, `ANY` and
`assert_has_calls`. Patching through `mocker` covers `patch.object` with `autospec`,
`patch.dict`, `stop` and the context-manager warning, and the spies and stubs have tests of their
own, including what `resetall` leaves alone.

## What mypy sees

A mock is assignable to every type, so the checker has nothing to check at the call site. Two
static tests show the types mypy gives `mocker` objects and the one check that remains, on a
hand-written callback.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/43-appendix-c-mocking
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
