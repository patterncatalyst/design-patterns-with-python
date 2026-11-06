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
| 012 | singledispatch on 3.14 | **go** (caveats) |
| 013 | `__init_subclass__` vs metaclass registry | **go** (lead with `__init_subclass__`) |
| 014 | `match` + `assert_never` | **go** |
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
perf_counter in tests. Barrier/Event waits carry a 10 s guard timeout that a healthy run never reaches
(`alternating_pollers` raises `TimeoutError` if one expires).
`bench/gil_bench.py` uses `print()` deliberately: it is a CLI benchmark whose output is a report on stdout,
and it is the one kept survivor of the idiomatic-review ban tier.

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

## PDP-012 singledispatch on 3.14: go, with caveats

Files: `dispatch.py`, `test_dispatch.py`. mypy-behaviour tests call `mypy.api.run` on snippets in `tmp_path`.

Proven: register by annotation picks the most specific class, unregistered subclasses fall back to the
base registration; `A | B` annotation registers both; `singledispatchmethod` works with no extra setup;
open extension from another module works (registrations are global, process-wide state);
no double dispatch: dispatch on the first argument then `match` on the second (`load_plan(cargo, vehicle)`).

Caveats:
- **Forward reference fails at registration** even on 3.14 with deferred annotations:
  `TypeError: Invalid annotation for 'x'. ForwardRef('Later') is an unresolved forward reference.`
  Define classes first, or use `f.register(Later, fn)`. No `from __future__ import annotations` needed.
- **mypy does not model dispatch.** With fallback `(cargo: Cargo)`, registering `int` is legal at runtime
  but mypy says `Dispatch type "int" must be subtype of fallback function first argument "Cargo" [misc]`;
  registered functions must return the fallback's return type (`[arg-type]`). Use an `object`
  fallback for open-ended dispatch.
- singledispatch gives **no exhaustiveness check**. Closed hierarchy: union alias + `match` + `assert_never`;
  open extension: singledispatch.

## PDP-013 `__init_subclass__` vs metaclass registry: go, lead with `__init_subclass__`

Files: `registry.py`, `test_registry.py`.

Proven for both designs: concrete classes register by `code=`, intermediates without `code=` don't,
duplicates raise `DuplicateCarrierError` and keep the original, unknown class keywords raise `TypeError`.

Typing:
- `__init_subclass__` needs no `type: ignore`; mypy **checks class keywords** against its signature
  (`code=1` is an error). With a metaclass mypy never checks the keywords; it needs two targeted ignores
  (`[attr-defined]`, `[assignment]`); `-> Self` in a metaclass `__new__` is rejected
  (`Self type cannot be used in a metaclass [misc]`).
- `ClassVar[dict[str, type[Carrier]]]` works; mypy lets `registry["NWD"]()` type-check even for an abstract class.
- **`__init_subclass__` cannot see abstractness** (it runs before `ABCMeta` computes
  `__abstractmethods__`); a metaclass can reject an abstract class that declares `code=` at creation time.

Keep the metaclass for: validating abstractness at creation, `__prepare__`/namespace rewriting,
class-level dunders (`__call__`, `__getitem__`, `__instancecheck__`).

## PDP-014 `match` + `assert_never`: go

Files: `matching.py`, `test_matching.py`.

Proven: frozen dataclasses give positional `__match_args__`; or-patterns of literal subpatterns and
guards; mapping patterns ignore extra keys and `str(x)` checks value types (webhook payloads);
sequence patterns with star captures, and `str` never matches a sequence pattern.
**Exhaustiveness proven with mypy:** removing the `Delivered` case gives exactly
`error: Argument 1 to "assert_never" has incompatible type "Delivered"; expected "Never"`; adding a new
event to `type TrackingEvent = ...` fails every `match` that lacks it. Runtime fallback raises
`AssertionError: Expected code to be unreachable`.

State/FSM chapter: frozen dataclass states, `type State = A | B | C`, transitions by `match` ending in
`case _: assert_never(...)`, so adding a state fails mypy until every transition handles it.

2026-11-04 (r05): Python 3.15.2. The spike tests were re-run green on 3.15.2. The recorded GIL benchmark output and the S4a findings remain 3.14.10 evidence, and the GIL chapter re-measures.

**r09 note, 2026-11-04 (Decorator layering).** "Pure percentage layers commute" holds in exact arithmetic only. With per-layer rounding to cents, two percentage layers in opposite orders differ by one cent on 6,940 of 20,000 per-kilogram prices from 0.01 to 200.00 (6,726 of 20,000 in a seeded draw over price and weight); see `_plans/evidence/percentage-layer-rounding.md`. The order-matters demo still uses an additive fee.

**r12 note, 2026-11-05 (singledispatch under mypy 2.4.1).** The PDP-012 finding "mypy does not model dispatch" is out of date. mypy 2.4.1 types a `singledispatch` function as `functools._SingleDispatchCallable[R, def (...)]` from its fallback's signature, checks call arguments against that signature (`[arg-type]`), refuses a registered implementation whose return type differs (`[arg-type]` on `register`) and a dispatch type that isn't a subtype of the fallback's first argument (`[misc]`). It still says nothing about a type that is never registered, so there is still no exhaustiveness check. Evidence: `_plans/r12-plan.md`, Planning evidence A. For the singledispatch chapter (r13); no r12 prose uses it.

