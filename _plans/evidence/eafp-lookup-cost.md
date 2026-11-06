---
title: "Evidence: cost of reading a rate three ways"
output: false
render_with_liquid: false
---

# What an EAFP read, a look-first read and `get` cost

Recorded 2026-11-06 (r15) for the chapter on dict dispatch and EAFP, on Python 3.15.2. Run from
`examples/31-shortcut-patterns-dict-dispatch-and-eafp` with `uv run python -I bench/lookup_cost.py`,
five times. The script is `bench/lookup_cost.py`; its output went through
`python3 scripts/host_ids.py filter`.

The figures are illustrative nanoseconds per call for this interpreter version, taken as the best of
five repeats of one million calls. Each call includes the call to a small function and a lambda, which
is the same for every form. They are not asserted by any test, and the absolute numbers move from run
to run by a few nanoseconds. What held in all five runs is the order: on a present key (`0901.21`)
the EAFP form is the cheapest, and on an absent key (`6109.10`) the EAFP form, which raises and
catches `KeyError`, costs about three times as much as the look-first form or `get`. On a miss the
benchmark returns a default and does not load, so it isolates the lookup.

```text
Python 3.15.2, best of 5 repeats of 1,000,000 calls
0901.21 eafp     42.7 ns/call
0901.21 lbyl     50.4 ns/call
0901.21 get      51.3 ns/call
6109.10 eafp    141.5 ns/call
6109.10 lbyl     45.0 ns/call
6109.10 get      51.0 ns/call
```
