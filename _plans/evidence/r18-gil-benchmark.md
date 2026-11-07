# r18 GIL benchmark: recorded example runs

Date: 2026-11-06 (Python 3.15.2, both builds).

**These are example runs on one machine, not tests.** No test asserts any figure here. The chapter
quotes them as "one example run", names the build and the worker count, and says the reader's
numbers will differ. Nothing in this file shows a cause for any ratio.

## Commands

Reader-safe; run from the repository root after `uv sync --locked --all-packages`.

Default build:

```bash
cd examples/37-the-gil-and-performance
uv run python bench/gil_bench.py --cpu-class "16-thread x86-64 CPU"
```

Free-threaded build, in its own environment built from the same lockfile:

```bash
uv python install 3.15t
UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15t --locked --all-packages
.venv-ft/bin/python examples/37-the-gil-and-performance/bench/gil_bench.py --cpu-class "16-thread x86-64 CPU"
```

The outputs below were scrubbed of host identifiers before they were recorded. The commands above
carry none.

## Recorded output, default build (`bench/gil_bench.out.txt`)

```
Python 3.15.2, default build, GIL enabled: True
workers: 4, batch: 4 consignments, best of 3
date: 2026-11-06, machine: 16-thread x86-64 CPU

Decimal rating (rating.quote)
serial                     0.727 s
thread pool               warm  0.703 s (1.0x)   cold  0.740 s (1.0x)
process pool              warm  0.203 s (3.6x)   cold  0.209 s (3.5x)
interpreter pool          warm  0.211 s (3.4x)   cold  0.248 s (2.9x)

integer-cents loop
serial                     0.132 s
thread pool               warm  0.130 s (1.0x)   cold  0.132 s (1.0x)
process pool              warm  0.039 s (3.4x)   cold  0.048 s (2.8x)
interpreter pool          warm  0.038 s (3.5x)   cold  0.102 s (1.3x)

waits, serial              0.800 s
waits, threads             0.201 s (4.0x)
waits, asyncio             0.201 s (4.0x)
```

## Recorded output, free-threaded build (`bench/gil_bench.ft.out.txt`)

```
Python 3.15.2, free-threading build, GIL enabled: False
workers: 4, batch: 4 consignments, best of 3
date: 2026-11-06, machine: 16-thread x86-64 CPU

Decimal rating (rating.quote)
serial                     0.878 s
thread pool               warm  1.648 s (0.5x)   cold  1.656 s (0.5x)
process pool              warm  0.255 s (3.4x)   cold  0.267 s (3.3x)
interpreter pool          warm  0.238 s (3.7x)   cold  0.354 s (2.5x)

integer-cents loop
serial                     0.159 s
thread pool               warm  0.040 s (3.9x)   cold  0.044 s (3.6x)
process pool              warm  0.045 s (3.5x)   cold  0.056 s (2.9x)
interpreter pool          warm  0.043 s (3.7x)   cold  0.196 s (0.8x)

waits, serial              0.800 s
waits, threads             0.202 s (4.0x)
waits, asyncio             0.201 s (4.0x)
```

## The other run of each build (ratios only)

Each build was run twice. The files above hold one run each; the other run's warm/cold ratios were:

| Section | Pool | Default build, other run | Free-threaded build, other run |
| --- | --- | --- | --- |
| Decimal rating | thread | 1.0 / 1.0 | 0.5 / 0.5 |
| Decimal rating | process | 3.3 / 3.5 | 3.6 / 3.5 |
| Decimal rating | interpreter | 3.5 / 3.0 | 3.6 / 2.4 |
| integer-cents loop | thread | 1.0 / 0.9 | 3.9 / 3.8 |
| integer-cents loop | process | 3.3 / 2.9 | 3.6 / 3.3 |
| integer-cents loop | interpreter | 3.9 / 1.3 | 3.7 / 0.8 |

The two runs of each build agree within about 0.4x on every ratio.

## What the runs show

In these example runs:

- Decimal rating: the thread pool ran at 1.0x serial on the default build and 0.5x on the
  free-threaded build. The process and interpreter pools ran at about 3.4 to 3.7x warm on both builds.
- Integer-cents loop: the thread pool ran at 1.0x on the default build and 3.9x on the free-threaded
  build. The process and interpreter pools ran at about 3.4 to 3.7x warm on both builds.
- Waits: threads and asyncio ran at 4.0x serial on both builds.

No cause is established for the Decimal thread result on the free-threaded build.
