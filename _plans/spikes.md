---
title: "r01 feature spikes: findings"
order: 6
output: false
---

# r01 feature spikes

Evidence for chapters that depend on language features. Code lives in
`spikes/feature-spikes` (package `feature_spikes`); spikes are retired in the iteration
whose example covers the claim. Recorded 2026-11-03, Python 3.14.10, mypy 2.4.1,
pytest 9.2.0. Workspace layout decisions (S4a) are in `spikes/S4a-findings.md`.

| PDP | Spike | Verdict |
| --- | --- | --- |
| 010 | Decorator pattern vs `@decorator` | **go** (framing adjusted) |
| 011 | Protocol, ParamSpec, PEP 695 generics | **go** |
| 012 | singledispatch on 3.14 | pending |
| 013 | `__init_subclass__` vs metaclass registry | pending |
| 014 | `match` + `assert_never` | pending |
| 015 | GIL and asyncio determinism | **go** (perf claims benchmark-only) |

## PDP-010 Decorator pattern vs `@decorator`: go

Files: `decorator_vs_syntax.py`, `test_decorator_vs_syntax.py` (3 consecutive green runs).

Proven:
- GoF stack (`FuelSurcharge`, `VolumeDiscount`, `Vat`, `HandlingFee` frozen dataclasses,
  no base class) still satisfies the `RateCalculator` Protocol (mypy).
- Stacks are data: `compose(base, layers)` with `type Layer = Callable[[RateCalculator], RateCalculator]`.
- Layers added and removed per consignment at runtime; the inner object is wrapped, never mutated.
- `@retry(attempts=, on=)` re-invokes on listed exceptions, gives up after N, ignores
  unlisted ones; `@audited(sink)` records to an injected sink; `__name__`, `__doc__`,
  `__wrapped__` preserved through two stacked decorators.
- `@` replaces the function object at definition time (`f is not f.__wrapped__`;
  `retry(...)(plain)` is the same rebinding without `@`); GoF wrappers leave classes untouched.
- Independence: the composition uses no `@`; an `@`-wrapped function has no `quote`.
- PEP 695 `def retry[**P, R](...)` accepted by mypy 2.4.1; signatures preserved
  (`reveal_type` gives `def (carrier: str, n: int =) -> decimal.Decimal`; bad calls are `[arg-type]` errors).

Adjustments for the chapter:
- **Pure percentage layers commute** (discount then VAT == VAT then discount). The
  "order matters" demo must use an additive fee, a cap, or rounding.
- `@audited` must be a factory, `@audited(sink)`; a bare form needs global state.
- `__wrapped__` is not on `Callable`; reading it needs `# type: ignore[attr-defined]` (one sentence).
- Exception names: ruff N818 wants an `Error` suffix; name it `CarrierTimeoutError` in reader code.
- Overlap case (a decorator function returning a wrapper object) gets one paragraph, not a section.
- Open with the two one-liners: `Vat(FuelSurcharge(BaseRate(...)))` vs
  `quote_carrier = retry(...)(quote_carrier)`. Teach `functools.wraps` + `ParamSpec` as the syntax-specific part.

## PDP-011 Protocol, ParamSpec, PEP 695: go

Files: `typing_generics.py`, `test_typing_generics.py`.

Proven:
- Structural conformance without a base class; PEP 695 `Quoter[T: Consignment]` infers
  contravariance (no `contravariant=True`); a narrower `HazmatQuoter` is rejected as `Quoter[Consignment]`.
- `typing.override` sets `__override__`; mypy rejects a misspelled override
  (`Method "qoute" is marked as an override, but no base method was found with this name [misc]`).
- `cheapest[T](options, key)` infers T correctly.
- Callback Protocol `RateStrategy.__call__(self, c, /)` accepts def, lambda and bound
  method; **use positional-only `/`** or parameter names must match.
- `@runtime_checkable` checks name presence only: wrong signature and even a
  non-callable attribute pass `isinstance`.
- Non-runtime Protocol in `isinstance`: static `[misc]` error, runtime `TypeError`.

Key surprise for the Protocol and testing chapters:
- **mypy gives no protection when a mock stands in for a Protocol parameter.** `Mock()`,
  `Mock(spec=...)`, `MagicMock(spec=...)` and `create_autospec(..., instance=True)` are all
  accepted because typeshed types them as `Any`, not because the spec is checked.
  `create_autospec` does enforce the call signature at runtime (`TypeError: missing a
  required argument`); a bare `Mock` accepts anything. Recommend autospec and say plainly
  that mocks bypass the static check.

## PDP-015 GIL and asyncio determinism: go

Files: `concurrency.py`, `async_patterns.py`, `test_concurrency.py` (9), `test_async_patterns.py` (17),
`bench/gil_bench.py` + `bench/gil_bench.out.txt`. 3 consecutive green runs; no sleep, wall clock or
perf_counter in tests. Barrier/Event waits carry a 10 s guard timeout that a healthy run never reaches.

Rule for both concurrency chapters: **every race is forced by a seam** (a hook, `threading.Barrier`,
`threading.Event`, `asyncio.Event`, `asyncio.sleep(0)`), never by timing. Assert exact outcomes of the
forced interleaving, or only an upper bound for unforced races.

Threads and the GIL:
- Natural lost update on `self.count += 1` did **not** reproduce in 600 runs (4 threads x 5000, default and
  1 us switch interval). Prose-only claim: "the GIL does not make `+=` atomic"; it is rare on 3.14 but real.
- Assertable: `dis` shows LOAD_ATTR / BINARY_OP / STORE_ATTR; a `between=` hook plus `Barrier(2)` loses an
  update every time (result 1, not 2); a Lock gives exactly 8000 of 8000.
- Event handshake makes two carrier pollers interleave `a1 b1 a2 b2 a3 b3` deterministically.
- Check-then-set cache: barrier-forced loader runs twice. **Surprise: `functools.cache` is not
  call-once under threads** (same barrier loader runs twice). Double-checked Lock runs it once. For a
  module-level singleton: build at import time, or Lock with double check.

asyncio:
- `sleep(0)` interleaves tasks in creation order (CPython FIFO ready queue: implementation detail, say so).
- `gather` keeps argument order whatever the completion order (forced via Events, 3 orders).
- `TaskGroup` cancels siblings on first failure; caught with `except*`.
- `asyncio.timeout(0)` cancels a never-finishing wait with no wall-clock dependence. Never assert that
  something finishes *inside* a timeout.
- asyncio race is easy to show: an `await` between read and write loses updates (5 workers give 1);
  no await gives 5; `asyncio.Lock` gives 5.
- Async generator as Iterator: lazy; `aclose()` runs cleanup. **Surprise: `break` out of `async for`
  does not run the generator's `finally`**; use `contextlib.aclosing`. Annotate as `AsyncGenerator[...]`,
  not `AsyncIterator`, or mypy rejects `aclosing`/`aclose`.
- `asynccontextmanager` session closes the feed on error and on cancellation.
- Coroutine Commands via `asyncio.Queue` + None sentinel run in order, undo in reverse; a failing
  command is recorded and the worker carries on.

Benchmark (illustrative, recorded output only, never asserted; prints only Python version and GIL state):

```
GIL benchmark, 2026-11-03
python 3.14.10  gil_enabled=True
4 workers, best of 3, pool start-up excluded for processes

CPU-bound: 4 x rate_loop(3,000,000)
  strategy               seconds   vs serial
  serial                   0.646       1.00x
  4 threads                0.756       0.86x
  4 processes              0.169       3.82x

I/O-bound: 4 x 0.2s wait
  strategy               seconds   vs serial
  serial                   0.801       1.00x
  4 threads                0.201       3.98x
  asyncio (4 tasks)        0.201       3.99x
```

Chapter prose must also cover pool start-up, pickling and memory costs of processes.
