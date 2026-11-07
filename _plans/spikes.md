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

**r13 note, 2026-11-06 (singledispatch registration and descriptors on 3.15.2, mypy 2.4.1).** Extends the r12 note. A name that isn't defined yet fails at the `@register` decorator with `TypeError: Invalid annotation for '<param>'. ForwardRef('<Name>', owner=<function <fn> at 0x...>) is an unresolved forward reference.` (the `owner=` part, with its address, is new since PDP-012); a class imported only under `TYPE_CHECKING` fails the same way when the module is imported, while mypy exits 0. mypy doesn't link the class to the function in `register(Cls, fn)` or `@register(Cls)`, and types a bound `singledispatchmethod` as `def (*Any, **Any) -> R`, checking only the return. `cached_property` fails on first access on a slotted dataclass (`No '__dict__' attribute ... to cache`), caches on a frozen non-slotted one, and can't be deleted there (`FrozenInstanceError`). Evidence: `_plans/r13-plan.md`, Planning evidence D, I and J; witnessed by `examples/27-descriptors-and-properties` and `examples/28-singledispatch`. Left out of the chapters by decision 10, and still observed on 3.15.2: one descriptor instance assigned to two names takes the second name (evidence A; a `cached_property` raises `TypeError` at class creation, evidence D); registration through an ABC and ambiguous multiple inheritance (evidence H); and `@register` on an unannotated first parameter takes the first annotation it finds (evidence I).

**r14 note, 2026-11-06 (class registries and dynamic attributes on 3.15.2, mypy 2.4.1).** Corrects spike 013: `inspect.isabstract` works inside `__init_subclass__` (CPython's `inspect.py` has a branch for that case), while `__abstractmethods__` isn't set yet there, so abstractness validation isn't a metaclass-only case. A metaclass registry needs no ignores when the metaclass declares `code: str` and the registry is typed by the metaclass, but calling a registry value is then typed `Any`; mypy checks neither the type nor the name of a metaclass keyword, reports a conflict as `[metaclass]`, rejects `Self` in a metaclass `__new__`, and ignores a metaclass `__call__` return type. A closed `__init_subclass__(cls, *, code=None)` lets mypy report a misspelt class keyword with "did you mean"; forwarding `**kwargs` loses that, and the runtime message then names the class (`'<Class>.__init_subclass__() takes no keyword arguments'`). A `__getattr__` that reads a missing attribute recurses under `copy.copy`, `copy.deepcopy` and `pickle` (`RecursionError`) when its loader raises `AttributeError` for unknown names; with a loader that answers every name, `deepcopy` fails earlier with `TypeError`. Out of scope and still observed: a refused class lingers in `__subclasses__()` until collected (evidence F); the `__annotate_func__` namespace key and metaclass `__getitem__` read by mypy as a type application (evidence H, I). Evidence: `_plans/r14-plan.md`, Planning evidence D, F, G, H, I and K; witnessed by `examples/29-metaclasses-init-subclass-and-registries` and `examples/30-dynamic-attributes-and-proxy`.

**r15 note, 2026-11-06 (dispatch tables, EAFP and over-abstraction on 3.15.2, mypy 2.4.1, ruff 0.17.4).** mypy checks a dispatch table's value signatures (`[dict-item]`), lookup key type (`[index]`), assignment into a `Mapping` or `frozendict` (`[index]`) and a call on `.get`'s result without a check (`[misc]`), but not a missing key; a `match` with `assert_never` (`[arg-type]`) and an enum if-chain with no `else` (`[return]`) are checked for totality, so a dict table's totality needs a test. A wrong key type in a `frozendict(...)` literal is reported as `[assignment]`, where a dict literal gives `[dict-item]`. ruff's SIM116 fires on an if-chain over string literals that ends in `else: return`, not over enum members and not when the chain ends in `else: raise`. The natural check-then-read race still never reproduces (0 in 20 runs of 200,000), so the tests force it through a storage seam parked on a `threading.Barrier`. A nine-class rating engine passes `mypy --strict` and ruff; for one quote it makes 11 Python-level calls against the function's 1, and adding a charge kind breaks it at run time (`AttributeError`) and under mypy (`[attr-defined]`, then `[abstract]`); mypy also accepts an abstract class passed as `Callable[[], Base]` while rejecting it as `type[...]` (`[type-abstract]`). Evidence: `_plans/r15-plan.md`, Planning evidence B, D, F, H and K; witnessed by `examples/31-shortcut-patterns-dict-dispatch-and-eafp` and `examples/32-anti-patterns-and-pattern-misuse`.

**r16 note, 2026-11-06 (patching, seams and characterisation on 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0).** With a `from`-import, patching the defining module leaves the using module calling the original; patching where the name is looked up works, and `unittest.mock.patch` follows the same rule. `monkeypatch.setattr` refuses a misspelt name in both target forms unless `raising=False`; only `autospec` checks a replacement's signature (`spec_set` accepts a wrong arity). mypy checks nothing inside `monkeypatch.setattr`, but checks a direct module assignment (`[assignment]`, plus `[attr-defined]` under `--strict` because a `from`-imported name isn't re-exported); `patch(...)` reveals `MagicMock | AsyncMock`, or the replacement's type with `new=`. A constant captured as a default argument ignores a patch. `importlib.reload` overwrites a live patch, and teardown restores the pre-reload object, so reload is witnessed only in a fresh interpreter. A misspelt override is `[misc]` only with `@override`; without it mypy is silent and the real carrier is called. One characterisation table passes across legacy, parameterised, wrapped, function and subclass forms, and its mutants (truncation and half-up rounding) each fail exactly one row. Out of scope for r16 (decision 9): `contextvars` as a seam (spiked; the outline doesn't ask for it); `patch.dict`, `patch.multiple`, `mock.seal`, `AsyncMock`, and injection through `sys.modules` or import hooks; golden files, approval libraries, Fowler's contrast and any rounding-rule experiment (Fowler vs Feathers); the strangler adapter and parity tests (Refactor or rewrite); coverage and mutation-testing tools; free-threading. Evidence: `_plans/r16-plan.md`, Planning evidence B-J; witnessed by `examples/33-seams-in-python` and `examples/34-dependency-breaking-techniques`.

**r17 note, 2026-11-06 (golden values, rounding refactors and parity on 3.15.2, pytest 9.2.0, mypy 2.4.1).** pytest 9.2.0 builds a dict comparison's differing keys as a set, so the "Differing items" order for string keys changes between runs; golden comparisons therefore assert an ordered list of mismatches, whose failure output ("Left contains N more items, first extra item: ...") is stable. Over a 120-row grid, rounding each carrier price to the cent as it becomes `Money` changes 18 totals by one cent (first `EU-11`, 14.84 to 14.85) while intent rows written from the requirement still pass; `round(Decimal, 2)` follows the context's half-even rounding and changes the only two half-cent rows (`EU-30` 32.505, `ASIA-30` 53.845). A grid of multiples of 0.5 kg cannot see gram truncation, so a fractional-weight intent row was added. A rewrite with `bisect_left` matches inclusive legacy bands everywhere except the deliberate unknown-zone refusal; a `bisect_right` draft also diverges at each band limit, and without a row above the last limit, moving it is caught only by the first-draft test. mypy reports `[arg-type]` for a rewrite of the wrong shape passed to the router. Out of scope (decision 12): approval-library dependencies (decision 4); property-based testing (hypothesis) for parity; Branch by Abstraction, feature-flag libraries, percentage rollouts, which would need randomness; Event Interception and the other displacement patterns beyond the four quoted; coverage and mutation-testing tools; the `float` against `Decimal` divergence (evidence F), kept as a spike note; free-threading and asyncio. Evidence: `_plans/r17-plan.md`, Planning evidence B-F; witnessed by `examples/35-fowler-vs-feathers` and `examples/36-refactor-or-rewrite`.


**r18 note, 2026-11-06 (the GIL, pools and asyncio on 3.15.2, default and free-threaded builds, mypy 2.4.1, pytest 9.2.0).** Spike 015 stays (decision 12): `concurrency.py`, `async_patterns.py` and its 3.14.10 bench are unchanged, and the new members `gil-and-performance` and `asyncio-patterns` re-witness its findings on 3.15.2. The planning probes (evidence B to J) and the two built members found:
- **Both builds (B, C).** uv installs `cpython-3.15.2+freethreaded`; the whole suite passed there at planning (1,220 tests, 148 s against 137 s). `sysconfig.get_config_var("Py_GIL_DISABLED")` is 1 only on the free-threaded build, and `sys._is_gil_enabled()` is `False` there, `True` on the default build. mypy types the config var as `Any`, so `-> bool` needs `bool(...)` (`[no-any-return]` otherwise). The two members pass on both builds: ch37 15 tests, ch38 28, 43 together on 3.15t.
- **Lost update (D).** `self.reserved += 1` compiles to separate `LOAD_ATTR`, `BINARY_OP` and `STORE_ATTR` on both builds. A natural race of 4 threads x 5,000 increments lost updates in 0 of 300 runs on the default build and 300 of 300 on the free-threaded build. A `Barrier` in the gap forces the double-booking on both builds; this is the member's witness (spike 015's "rare but real" `+=` finding, now forced).
- **Pools (E, decision 5).** Thread, process and interpreter pools rate a batch as the serial loop does; threads share an argument and the other two receive a copy. A process pool refuses a lambda (`Can't pickle`). `type[Executor]` called with `max_workers` is a `[call-arg]` error, so the factory alias is `Callable[[int], Executor]`. At planning the interpreter pool accepted a lambda and refused a closure with `NotShareableError`. **Differs in the built member:** a lambda defined inside `rate_batch` is refused by the interpreter pool with `NotShareableError` too, so experiment (b) fails `[process]` and `[interpreter]`, not `[process]` alone. Not claimed beyond what two runs agree on; the docs' "serializes ... using pickle" wording against the planning-time acceptance is not filed.
- **Benchmark.** The member's bench times `Decimal` rating and an integer-cents loop. In the example runs of `_plans/evidence/r18-gil-benchmark.md`, thread pools ran at 1.0x on the default build for both loops; on the free-threaded build the `Decimal` loop ran at 0.5x and the integer loop at 3.9x. **This differs from planning**, where a bare float loop ran at 3.3x in threads on the free-threaded build. A scratch probe in U1a saw the same split (four threads over a `Decimal` loop at 0.5x with or without a copied price, local context or integer step; floats 3.7x, integers 3.5x). No cause is established and none is claimed. Process and interpreter pools ran at about 3.4 to 3.7x warm on both builds, and waits in threads or asyncio at 4.0x.
- **asyncio (F, H, I).** A CPU-bound coroutine holds the loop on both builds. A coroutine called without `await` is a coroutine object; never awaited, it warns `coroutine 'FastlineSource.quote' was never awaited`, which fails under `filterwarnings = ["error"]`. `Queue.shutdown()` replaces the `None` sentinel and `shutdown(immediate=True)` drops what is pending. `TaskGroup.cancel()` (3.15) stops the group at the first answer. mypy reports a quote returned without `await` as `[return-value]`, an unused coroutine as `[unused-coroutine]`, and a blocking source in a list of `RateSource` as `[list-item]` (planning guessed `[arg-type]`; test 24 asserts `list-item`). ruff `--select ASYNC` passes the probes and RUF006 reports a dangling `create_task`.
- **Pitfalls found while writing the tests (U1b).** `except* LookupError` also catches a bare `LookupError`, so a test that wants to prove `return_exceptions=True` must catch `ExceptionGroup`. A `TimeoutError` raised by the runner's guard is indistinguishable from the timeout under test unless the test catches it inside the coroutine. asyncio closes a dropped async generator at loop shutdown, so a test that reads `feed.closed` after `asyncio.run` returns cannot show that `aclosing` was missing; it reads the flag inside the coroutine. `except Exception` in place of `except asyncio.QueueShutDown` changes nothing, because `QueueShutDown` is an `Exception`; no test claims the narrower handler.

**r19 note, 2026-11-07 (the final project and the review gates on 3.15.2, mypy 2.4.1, ruff 0.17.4, pytest 9.2.0).** No spike changes. The planning probes (evidence B to J) ran on reduced models in a scratch copy and the two built members `final-project` and `working-with-ai-and-llm-tools` re-witness them. They found:
- **Both builds (D).** The reduced models passed on the free-threaded `3.15.2t` (18 passed), so neither member joins the `free-threaded` CI job (decision 7). No build-dependent behaviour is claimed.
- **Final project (B, C).** One request (`CN-1`, 12.5 kg, coffee `0901.21`) gives freight `5.63` (12.5 x 0.45 = 5.625, half up), duty `30.00`, invoice `35.63`, slot `SlotId(1, 1, 1)`, carrier `{1001: 12500}` (grams) and one `BOOKED` event; `35.00` does not settle it. A held declaration (`9999.99`) leaves no reservation, no carrier booking and no event, and the next request takes the same slot. The undo log of the `ExitStack` is `["cancel", "release"]`, the reverse of registration. `ExitStack.callback` and `pop_all` are taught nowhere earlier in the book.
- **Stage left out (C, E).** The acceptance helper returns an ordered list, and a probe's first `!= []` assertion passed on anything, so the member asserts exact lists: `['freight 0.00', 'invoice 30.00']` (rating), `['carrier {}']` (carrier), `['duty 0.00', 'invoice 5.63']` (clearance), `['tracking']` (tracking).
- **Final-project mutations (D, built in V1a).** The `cancel` callback removed fails tests 4 and 5; `pop_all()` removed fails test 1 and the four cases of test 2; the publish moved inside the `with` fails test 8 only; `try/except` in place of `ExitStack` fails test 5 only. Planning's reduced model had `pop_all()` fail the end-to-end test alone; the built member's acceptance test is parametrised over four stage-left-out cases, so it fails five items.
- **Drafts under the gates (F to I).** `untyped_factory` fails mypy (`no-untyped-def`, `no-untyped-call`), ruff (`UP037`, `UP045`), the shape review and the oracle; `typed_hierarchy` passes mypy and ruff and fails only the shape review; `rounded_callable` passes mypy, ruff and the shape review and fails only the oracle, with `["CN-5 per_kg: 0.23 != 0.22", "CN-7 per_kg: 1.13 != 1.12", "CN-8 per_kg: 5.63 != 5.62"]` (the half-cent products 0.225, 1.125 and 5.625, half up against half even). ruff 0.17.4 reports no rule for a one-method base or a static-only class (`ruff rule PLR0903` is an invalid value there). `ast.walk` yields nodes "in no specified order", so `review` sorts its findings. The built `untyped_factory` has one `no-untyped-call`, not the two planning saw.
- **Experiment (a) differs from planning.** Rounding `pricing.py` with `round(amount, 2)` fails `test_the_idiomatic_module_passes_every_gate` only, not tests 1 and 2: test 1 runs the drafts and never `pricing.py`. Experiment (b), `static_only_class` removed from `SHAPE_RULES`, fails the typed-hierarchy shape test, `8[static-only-class]` and also two `propose` tests that use the typed draft as a rejected reply; test 1 still passes because `single_method_base` still flags that draft's base.
- **Final project, test 12.** The first version passed a `build_desk` that hard-coded a flat `10.00` rule, because it used one constant rule. The test now builds the desk twice, once with the flat rule and once with a two-euros-a-kilogram rule, and asserts both (quote, invoice) pairs (`10.00` and `40.00`; `25.0` and `55.0`). The hard-coded rule now fails tests 1, 3 and 12. Final project tests added in the build for the deletion runs: an overpayment, a non-positive weight and an unknown zone (19 functions, 23 cases against the planned 16 and 20); ch40 added three the same way (18 functions, 26 cases against 15 and 21).
- **Assistant seam (J).** `RecordedAssistant` with `propose` and the static and shape gates gives reviews accepted `[False, True]` and prompts `[prompt, prompt + "\n\nFix these findings:\n" + one "line N: rule, advice" line per finding]`; an unrecorded prompt raises `LookupError` (`no recorded reply for prompt '...'`). A prompt whose recorded replies are used up is refused the same way.
- **importlib conftest lesson (J).** Under `--import-mode=importlib` a test module cannot import helpers from `conftest` by name, nor from another test module (the probe's first collection failed). The built members reach shared values through fixtures (`coffee_request`, `held_request`, `world`, `recording_parts`, `publish_form` in ch39; `static_gate`, `drafts`, `draft`, `load_module` in ch40) and keep shared tables in the one test module that uses them.
- **Mutations of the tests V1b left without one (V2, fresh scratch copy built from `git ls-files`, no `.venv`, `uv sync --locked --all-packages`, `review_gate.__file__` inside the copy, deleted afterwards).** The copy passed 26 before any change. A module-level `BROKEN: int = "not an int"` appended to the `typed_hierarchy` draft fails `test_mypy_and_ruff_pass_the_typed_hierarchy` and `test_each_draft_fails_exactly_the_gates_in_the_table[typed_hierarchy]` (2 failed). `single_method_base` made to fire on every class fails `test_shape_rules_stay_quiet_on_a_callable_class_and_a_frozen_dataclass` and nine other tests (10 failed; `test_each_draft_fails_exactly_the_gates_in_the_table` still passes, because no draft in the table has a class the change newly flags). Removing the first line of the `rounded_callable` draft fails `test_every_draft_says_it_was_written_for_the_book[rounded_callable]` only (1 failed).
- **Sources (K).** Fetched 2026-11-06 and listed in the plan. The five `source:` witnesses stay open until chapter prose links them and V5a and V5b re-fetch each sentence.
- **Sidebar census.** `_plans/evidence/r19-sidebar-census.md` records the greps: 34 of 47 documents have exactly one sidebar, each with one nested prompt and one review line.
