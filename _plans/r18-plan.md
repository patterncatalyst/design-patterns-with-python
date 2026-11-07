---
title: "r18 plan: chapters 37-38 (The GIL and performance; asyncio and the patterns)"
order: 18
output: false
render_with_liquid: false
---

# r18: chapters 37-38, The GIL and performance; asyncio and the patterns

Opus-planned 2026-11-06. Branch `release/r18`, cut from main at f60cca0 (the r17 merge). This file is the source of truth for r18 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No pin changes this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4, uv 0.13.7 and uv_build 0.13.7 match PyPI and python.org (checked 2026-11-06 from PyPI JSON: pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, ruff 0.17.4 of 2026-11-05, mypy 2.4.1 of 2026-10-28, uv and uv-build 0.13.7 of 2026-11-03; python.org lists 3.15.0 to 3.15.2 as releases, and `ftp/python/3.16.0/` holds only `Python-3.16.0a1`, a pre-release; `uv python list` offers `cpython-3.16.0a1` and `cpython-3.15.2+freethreaded`). U0 re-checks before any edit. `uv.lock` changes only because two members are added. If decision 2 is accepted, `.github/workflows/ci.yml` gains one job (U1b).

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch37: slug `37-the-gil-and-performance`, title "The GIL and performance", part 12 (`concurrency`), `kind = "hands-on"`, `has_example = true`, `status = "stub"`. The stub carries a `## How it works` heading that the draft drops.
- ch38: slug `38-asyncio-and-the-patterns`, title "asyncio and the patterns", part 12, `kind = "hands-on"`, `has_example = true`, `status = "stub"`. Same stub heading, also dropped.

`validate.py` SPINE for `hands-on`: Learning objectives, Why this matters, Build, run, observe, What you can do now, For deeper coverage. No sidebar count is enforced (the count check runs only for `kind == "pattern"`). One figure is required, the word ceiling (2,500) is an error and the floor (1,900) a warning. `check_stale_versions` flags `Python 3.N` and `3.N.M` below the pin unless `since `, `before `, `until ` or `new in ` sits within 16 characters before it, so "Python 3.13" and "3.14" need that wording or a phrasing such as "the 3.13 release" (evidence M). The hands-on models are "Proving it works: pytest, pytest-mock, and mypy" and "Seams in Python: monkeypatch, injection, and duck typing".

Work items: PDP-137a-c (ch37 example, figure, prose) and PDP-138a-c (ch38), `todo` in `_plans/iteration-plan.md`.

## User decisions (owner to confirm)

0. **Step ids.** The steps are U0 to U7. At planning time `grep -nE '^\| U[0-9]' _plans/*.md` and `grep -n 'run: U' _plans/*.md` both print nothing. Following r16 and r17, only suffixed ids are cited as `run:` tokens: `U1a`, `U1b`, `U5a` and `U5b`. Plain U0, U2, U3, U4, U6 and U7 appear only in this plan's table. One `run:` token cites a recorded file instead: `run: _plans/evidence/r18-gil-benchmark.md` (written at U2; `validate.py` resolves a path token by file existence).

   **Recommend: yes.**

1. **Kinds.** Both chapters stay `hands-on` with `has_example = true`, each with one AI sidebar in the 2026-11-05 form, held in a chapter-specific "when it's the wrong tool" section, as in "Proving it works".
   - ch37 is a disambiguation chapter in effect (domain row 37's bucket): "the GIL" is an interpreter lock, not a lock on your invariants. It says so in its thesis, not through the `pattern` spine.
   - ch38 shows several patterns under asyncio. It gives each pattern's bucket in one table (evidence K) instead of taking the `pattern` spine, which wants one pattern and a `## When not to use it`.

   **Recommend: yes.** Alternative: ch38 as `kind = "pattern"`. That adds `## When not to use it` and the sidebar count check, but the chapter has no single pattern to set against its forces.

2. **Free-threaded Python. Option B, a bounded change to the r01 decision.** The r01 build plan (2026-11-03, binding) says "Skip free-threaded Python (PEP 703). Do discuss GIL performance impact and its relation to async code", and the reconciliation plan says "Free-threaded Python is out of scope". Domain row 37 says "no free-threading". Since then the evidence has changed: free-threading has been a supported build since the 3.14 release (PEP 779), and uv installs it into its own store with one command (evidence B). Options:
   - **A. Keep the skip.** No free-threaded interpreter anywhere. ch37 names the build in one sentence, citing the docs, and makes no claim about it. Consistent with r01, but the chapter's title then teaches a 2026 reader half the story, and its claims ("threads don't speed up CPU-bound Python") read as universal when they hold only for the default build.
   - **B. Bounded (recommended).**
     - ch37 names both builds, shows which one is running (`sysconfig.get_config_var("Py_GIL_DISABLED")`, `sys._is_gil_enabled()`), and scopes every timing sentence to a build.
     - Its tests are build-agnostic: every assertion holds on both builds (evidence C, D, E). The free-threaded build's behaviour enters prose only through docs quotations and the labelled example runs of the benchmark (decision 3).
     - CI gains one job, `free-threaded`, that runs only `examples/37-*` and `examples/38-*` on `cpython-3.15.2+freethreaded`; `ci-ok` needs it (U1b).
     - The r01 line, the reconciliation plan's header sentence and domain row 37 get dated notes at U0. Nothing else in the book changes.
   - **C. Full.** As B, and the whole suite runs on 3.15t in CI. Evidence B shows all 1,220 tests pass there today (148 s against 137 s), but every later member would then carry a second interpreter's behaviour, which no plan has asked for.

   **Recommend: B.** It overrides a binding owner line, so it needs explicit sign-off. If the owner keeps A, drop test 2's free-threaded half, the `free-threaded` CI job, the free-threaded benchmark run and the sentences that cite them; nothing else changes.

3. **Benchmark policy.** Speed is never asserted.
   - `examples/37-the-gil-and-performance/bench/gil_bench.py` (standard library only, `print()` report, the one sanctioned idiom-scan survivor, as spike 015's bench was) times CPU-bound rating serially and through thread, process and interpreter pools (warm and cold), and I/O-bound waits serially, in threads and in asyncio.
   - Its output records only the Python version, the build ("free-threading build" or not), `sys._is_gil_enabled()`, the worker count, the date and a CPU class written by hand ("16-thread x86-64 laptop CPU"), never a model. Scrubbed with `host_ids.py filter` before commit.
   - Recorded twice per build at U1a, into `bench/gil_bench.out.txt` (default build) and `bench/gil_bench.ft.out.txt` (free-threaded, decision 2), and copied with a dated header into `_plans/evidence/r18-gil-benchmark.md` at U2.
   - Prose quotes the recorded table once, labelled "one example run", with the interpreter, the build and the worker count; gives ratios to one decimal place ("about 3.7 times"); and says the reader's numbers will differ. Every speed sentence names the build it was measured on.
   - No benchmark number appears in a test, a card, a README or a caption.

   **Recommend: yes.**

4. **ch37's witnesses are structural.** What the tests can assert deterministically on both builds (evidence C to F):
   - which build is running, and that the build flag and the runtime GIL state agree;
   - that `+=` on an attribute is separate load, add and store instructions (`dis`);
   - a forced lost update: two threads parked in the reservation's gap by a `threading.Barrier` both take the same `SlotId`, on both builds;
   - a lock that covers the read gives two slots; a lock that doesn't cover the read loses one (experiment a), forced by a lock that records a second caller at its door;
   - every pool rates a batch exactly as the serial loop does; threads share an argument object, processes and interpreters receive a copy;
   - a process pool refuses a lambda (`PicklingError`);
   - a CPU-bound coroutine holds the event loop until it returns (ordering only).

   What can't be made deterministic, and so appears only as a quoted docs sentence or a labelled example run (decision 3), with the caveat in the sentence:
   - threads don't speed up CPU-bound pure Python on the default build, and do on the free-threaded build;
   - processes and interpreter pools speed up CPU-bound work, and what their start-up costs;
   - the free-threaded build's single-thread overhead (docs: "about 1% on macOS aarch64 to 8% on x86-64 Linux"; the example run on this rate loop is larger, evidence G; prose quotes the docs and reports the run as a run, not as a contradiction);
   - how often the natural race happens: 0 of 300 runs on the default build and 300 of 300 on the free-threaded build (evidence D). Prose may say "in one run of 300 trials" with both counts. No test asserts a count from an unforced race;
   - I/O-bound speed-ups for threads and asyncio.

   **Recommend: yes.**

5. **Pool scope: thread, process and interpreter pools, through one factory alias.** `type PoolFactory = Callable[[int], Executor]`; `POOLS` is a read-only `frozendict` of `thread`, `process`, `interpreter`. mypy rejects `type[Executor]` called with `max_workers` (`[call-arg]`, evidence E), which is why the alias is a callable. `concurrent.interpreters` (the low-level module) is named in one clause and not used. `multiprocessing` directly, shared memory, `Manager` objects and `forkserver` restrictions are cut; the default start method (`forkserver` on Linux since the 3.14 release) is one quoted sentence, not a test.

   **Not claimed** (evidence E): `InterpreterPoolExecutor` accepted a lambda on 3.15.2 although its docs say the worker "serializes the callable and arguments using pickle"; a closure was refused with `NotShareableError`. Kept as a spike note. Not filed without the owner.

   **Recommend: yes.**

6. **ch38's patterns** (evidence H to K). Six, each with one witness set and at most one excerpt:
   - **Iterator**: the carrier's live feed as an async generator; `break` out of `async for` leaves it open; `contextlib.aclosing` closes it (legacy row 20; the Iterator chapter's pointer).
   - **Context manager**: an `asynccontextmanager` carrier session that closes the feed when the body raises and when the task is cancelled (legacy row 21; the context-manager chapter's pointer).
   - **Strategy and Adapter**: a `RateSource` Protocol with an `async def quote`; a blocking carrier SDK adapted with `asyncio.to_thread`; the cheapest quote across both. mypy refuses a blocking source where the Protocol wants a coroutine.
   - **Structured concurrency** (not a GoF pattern, the mechanism the others now use): `TaskGroup` cancels siblings on the first failure, `TaskGroup.cancel()` (new in 3.15) stops the group at the first answer, and `asyncio.timeout(0)` cancels a quote that never answers.
   - **Observer**: `AsyncSignal[E]` publishes with `gather(..., return_exceptions=True)` and raises one `ExceptionGroup` after every subscriber has run, matching the Observer chapter's synchronous rule. A `TaskGroup` publisher is the chapter's one comparison form (`publish_form` `gather|taskgroup`): it cancels the other subscribers on the first failure.
   - **Command**: coroutine commands on an `asyncio.Queue`, a worker that records failures and carries on, and `Queue.shutdown()` in place of a `None` sentinel; `shutdown(immediate=True)` drops what's pending (legacy row 22; the Command chapter's pointer to "queues shared across concurrent tasks").

   Plus the two hazards domain row 38 names: a forgotten `await` (a coroutine where a quote was expected; mypy reports it; the never-awaited `RuntimeWarning` fails a test under `filterwarnings = ["error"]`), and an `await` between read and write that double-books a slot, fixed by `asyncio.Lock`.

   Cut: the async ledger append (domain row 38 lists it; Billing gets nothing here), `asyncio.Barrier` beyond its one use as a test seam, eager task factories, `asyncio` introspection (`capture_call_graph`), streams, subprocesses, `run_in_executor` beyond one clause, `uvloop`.

   **Recommend: yes.** Alternative: drop Strategy and Adapter to save about 300 words. They carry the GIL link (the `to_thread` note, evidence L), which is the r01 line's "relation to async code".

7. **Library scope: standard library only.** No pytest-asyncio, anyio, trio or uvloop. Async tests are plain sync tests that call `asyncio.run` on a local coroutine, as spike 015's are. No change to the root dev group or the ruff selection: RUF006 (dangling task) is already selected; the `ASYNC` rule family is named in one clause with its docs link and not enabled, because enabling it is a root config change for every member.

   **Recommend: yes.**

8. **Determinism for threads and tasks.** CLAUDE.md's rule, applied:
   - every interleaving is forced by a seam (`threading.Barrier`, a recording lock, `threading.Event`, `asyncio.Event`, `asyncio.Barrier`), with a guard timeout of 10 seconds that a healthy run never reaches;
   - no `time.sleep`, `perf_counter`, clock or `random` in tests; `asyncio.sleep(0)` only where the text says the order it gives is a CPython detail;
   - the never-awaited warning relies on CPython freeing the coroutine when its last reference goes; the test says so in its docstring;
   - tests 1 and 2 read the build, so they depend on `PYTHON_GIL` and `-X gil` being unset; their docstrings say so and CI sets neither;
   - worker functions for process and interpreter pools live in `src`, because under `--import-mode=importlib` a test module can't be imported by name in a worker (evidence E).

   **Recommend: yes.**

9. **No mocks, `mocker` or `monkeypatch`.** Seams are parameters (`lock=`, `gap=`, injected sources and subscribers). The r16 exception isn't extended.

   **Recommend: yes.**

10. **Citations** (evidence L). Python docs pages, quoted exactly from fetched 3.15.2 pages: the glossary (global interpreter lock), `threading` ("GIL and performance considerations"), `sys._is_gil_enabled`, the free-threading how-to, `concurrent.futures` (`InterpreterPoolExecutor`, `ProcessPoolExecutor`), What's New in 3.14 (PEP 779, forkserver) and 3.15 (`TaskGroup.cancel`), asyncio's tasks, queues and "Developing with asyncio" pages. PEP 703 and PEP 779 by title. POSA2 (already in `bibliography.html`, whose note promises "the original Monitor Object and Active Object catalogue entries, read against the GIL and asyncio chapters"): Monitor Object and Scoped Locking in ch37, Active Object in ch38, by name only, verified on the publisher's table of contents. *Fluent Python* (2nd ed., already listed) by topic only; no chapter title could be verified (the O'Reilly search returns no table of contents). ruff's RUF006 page for one clause.

    **Recommend: yes.**

11. **Domain names** come from `_plans/shipping-domain-model.md`: the Routing area (`Sailing`, `StowagePlan`, `SlotId`; "the reservation is the shared state in the concurrency chapters"), Tracking (`HandlingEvent`, `HandlingKind`, `TrackingHistory`), Rating (`RateQuote`, `Money`, `Consignment`) and Carrier (`FASTLINE`, `AIRCO`, `CarrierTimeoutError`). No new domain area and no new carrier code. Rows 37 and 38 are updated at U0 (this commit drafts them).

    **Recommend: yes.**

12. **Spike 015 stays.** `spikes/feature-spikes` keeps `concurrency.py`, `async_patterns.py` and the 3.14.10 bench (no earlier iteration retired a spike). The U2 spikes note says which findings the new members now witness on 3.15.2.

    **Recommend: yes.**

13. **No cross-language wording, no project-outcome statistics.** No sentence claims how much faster "applications" get, how many projects use asyncio, or any adoption figure. The docs' overhead figure (decision 4) is a measurement of CPython, quoted as the docs give it.

    **Recommend: yes.**

Also proposed for the owner (no decision needed unless declined):
- **No new books.**
- **A dated r18 note** in `_plans/spikes.md` at U2: evidence B to J and the decision 5 and 6 cuts.
- **The free-threaded interpreter** stays installed in uv's store (`uv python install 3.15t` also linked `~/.local/bin/python3.15t`, as the existing `python3.15` link was made). Remove with `uv python uninstall 3.15t` if unwanted.

## Planning evidence

Probes ran in a scratch copy at `<scratchpad>/plan18` (built from `git ls-files` plus untracked files, `.venv` removed, `uv sync --locked --all-packages`) and in `<scratchpad>/probes18`, outside the repo. Both were deleted afterwards; the repo was unchanged.
- Runtime (default): `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- Runtime (free-threaded): `uv python install 3.15t` printed `Installed Python 3.15.2` and `+ cpython-3.15.2+freethreaded-linux-x86_64-gnu (python3.15t)`; `python -VV` gives `Python 3.15.2 free-threading build (main, Oct 26 2026, 14:06:54) [Clang 23.1.3 ]`.
- mypy 2.4.1 `--strict --warn-unreachable --cache-dir /dev/null`; ruff 0.17.4 `--isolated --line-length 100 --select E,F,W,I,UP,B,SIM,RUF,PT,N --target-version py315`; pytest 9.2.0 with `filterwarnings = ["error"]` and the repo's `addopts`.
- Host: a 16-thread x86-64 laptop CPU. Timings below are single example runs.

The models are reduced models: names differ from the members' dotted names, and every output is a prediction until the build quotes it as observed.

**A. Pins.** See the header. No bump.

**B. The free-threaded build under uv.**
- `uv python install 3.15t` works; `uv python find 3.15t` resolves it.
- `UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15t --locked --all-packages` builds a second environment from the same `uv.lock`, which stays byte-identical (`cmp` clean). mypy installs as a `cp315t` mypyc wheel.
- The whole suite on 3.15t: `1220 passed in 148.14s`; on the default build `1220 passed in 137.35s`. No warning re-enabled the GIL: `sys._is_gil_enabled()` stays `False` after importing mypy.
- CI: `astral-sh/setup-uv` then `uv python install 3.15t` uses the same python-build-standalone download for `x86_64-linux-gnu`. Not run on GitHub at planning time; U1b's PR run is the check (risk).

**C. Which build is running.**
```
default        abiflags ''  Py_GIL_DISABLED 0  _is_gil_enabled True   switchinterval 0.005
free-threaded  abiflags 't' Py_GIL_DISABLED 1  _is_gil_enabled False  switchinterval 0.005
```
- `python3.15t -X gil=1` gives `_is_gil_enabled() == True`. `PYTHON_GIL=0` on the default build exits 0 and leaves it `True`.
- mypy reveals `bool` for `sys._is_gil_enabled()` and `Any` for `sysconfig.get_config_var(...)`. Returning `sysconfig.get_config_var("Py_GIL_DISABLED") == 1` from a `-> bool` function gives `Returning Any from function declared to return "bool"  [no-any-return]`; `bool(...)` is accepted.
- Both builds have `InterpreterPoolExecutor`, `concurrent.interpreters`, `asyncio.Queue.shutdown`, `asyncio.QueueShutDown`, `TaskGroup` and `asyncio.timeout`.

**D. `+=` and the slot reservation.**
- `dis` of `self.reserved += 1` on 3.15.2 (both builds): `['RESUME', 'LOAD_FAST_BORROW', 'COPY', 'LOAD_ATTR', 'LOAD_SMALL_INT', 'BINARY_OP', 'SWAP', 'STORE_ATTR', 'LOAD_COMMON_CONSTANT', 'RETURN_VALUE']`. The test asserts the ordered subsequence `LOAD_ATTR`, `BINARY_OP`, `STORE_ATTR` only.
- Natural race, 4 threads x 5,000 increments, 300 runs:
  - default build: `runs with a lost update 0` (also 0 at a 1 microsecond switch interval);
  - free-threaded build: `runs with a lost update 300`, `max lost 13566` of 20,000.
  Not asserted (decision 4).
- Slot model: `StowagePlan(sailing, *, lock=None, gap=_no_gap)`, `reserve(consignment_id) -> SlotId` takes `SlotId(1, 1, len(reservations) + 1)`, calls `gap()`, stores. 100 runs on each build:
  - `lock=nullcontext()`, `gap=Barrier(2).wait`: both threads get `SlotId(bay=1, row=1, tier=1)`, one reservation, every run;
  - a recording lock (`__enter__` counts callers and sets an `Event` at the second, then takes a real `Lock`) with a gap that waits for the second caller: tiers 1 and 2, two reservations, every run;
  - the same, with the read moved before `with self._lock:`: both get tier 1, one reservation, every run. That's experiment (a).

**E. Pools.**
- Default start method on Linux: `forkserver`.
- An 8-consignment batch rated by `ThreadPoolExecutor`, `ProcessPoolExecutor` and `InterpreterPoolExecutor` (4 workers) equals the serial list on both builds.
- `append_reserved(reserved: list[str], cid) -> int` submitted to each pool with a fresh list: the call returns `1` everywhere; the caller's list is `['CN-1']` after the thread pool and `[]` after the process and interpreter pools.
- `ProcessPoolExecutor().submit(lambda: 1).result()` raises `_pickle.PicklingError: Can't pickle <function <lambda> at 0x...>: it's not found as __main__.<lambda>`. The test matches `Can't pickle` only (the address varies).
- `InterpreterPoolExecutor` returned `1` for the same lambda; a closure raised `NotShareableError ... does not support cross-interpreter data` (decision 5: not claimed).
- `pickle.dumps(threading.Lock())` raises `TypeError: cannot pickle '_thread.lock' object` (prose may mention; no test planned).
- A probe member in the scratch workspace (worker functions in `src`, tests importing them) passed 10 tests three times in 0.20 s on the default build, from the member directory and from the root, and in 0.31 s on 3.15t.
- mypy: a pool parameter typed `type[Executor]` and called with `max_workers=4` gives `Unexpected keyword argument "max_workers" for "Executor"  [call-arg]`; `type PoolFactory = Callable[[int], Executor]` with the three classes as values passes.

**F. A CPU-bound coroutine holds the loop.** Two tasks created in order, `busy` (log, `sum(range(100_000))`, log) and `other` (log): the log is `["busy start", "busy end", "other"]` on both builds. It holds because nothing in `busy` awaits, whichever task the loop starts first after `busy`, so the claim doesn't rest on the FIFO detail.

**G. Benchmark (example runs, best of 3, 4 workers, 4 x a 3,000,000-step float loop).** Two runs per build agreed to within 0.2x:
```
3.15.2 gil True
serial 0.640
ThreadPoolExecutor         warm 0.688 (0.93x)  cold 0.712 (0.90x)
ProcessPoolExecutor        warm 0.171 (3.75x)  cold 0.176 (3.63x)
InterpreterPoolExecutor    warm 0.176 (3.65x)  cold 0.202 (3.17x)
io serial 0.801  asyncio 0.201
io threads 0.202
3.15.2 gil False
serial 0.798
ThreadPoolExecutor         warm 0.241 (3.31x)  cold 0.224 (3.56x)
ProcessPoolExecutor        warm 0.220 (3.63x)  cold 0.231 (3.45x)
InterpreterPoolExecutor    warm 0.223 (3.58x)  cold 0.301 (2.65x)
io serial 0.801  asyncio 0.201
io threads 0.203
```
The free-threaded serial run is about 25% slower on this loop, more than the docs' 1% to 8% pyperformance range. The member's bench uses the rating function instead of the bare loop, so U1a re-measures and these numbers are not quoted.

**H. asyncio behaviour (both builds; 12 probe tests, 3 runs each).**
- `quote(1)` without `await` is a `coroutine` object.
- A coroutine created and never awaited fails the test under `filterwarnings = ["error"]`: `pytest.PytestUnraisableExceptionWarning: Exception ignored while finalizing coroutine <coroutine object quote at 0x...>: None`. Inside `pytest.warns(RuntimeWarning) as record`, the messages are exactly `["coroutine 'quote' was never awaited"]` (qualname of a method: executor check).
- `Queue.shutdown()`: `put_nowait` raises `QueueShutDown`; `get` drains `a`, `b`, then raises. `shutdown(immediate=True)`: `qsize() == 0`, `get` raises, `join()` returns. A worker blocked in `get` wakes with `QueueShutDown`.
- `TaskGroup`: a sibling blocked on an `Event` logs `slow cancelled` when another task raises `LookupError("AIRCO")`, and `except* LookupError` sees `ExceptionGroup ['AIRCO']`. `eg.message` is `unhandled errors in a TaskGroup`; `str(eg)` adds `(1 sub-exception)`.
- `TaskGroup.cancel()` (3.15): with AIRCO waiting forever and FASTLINE answering, the result is `('FASTLINE 14.84', ['AIRCO cancelled'])`; mypy 2.4.1 accepts `tg.cancel()`.
- `asyncio.timeout(0)` around a never-set `Event`: the inner `finally` runs, then `TimeoutError`.
- `asyncio.to_thread(blocking)` where `blocking` waits on a `threading.Event` that a loop task sets: log `["loop ran", "booked"]`.
- Five tasks that read, `await asyncio.sleep(0)`, write: the count is 1. The member uses `asyncio.Barrier(5)` as the gap instead, so the result doesn't rest on FIFO order.
- `break` out of `async for` leaves the generator's `finally` unrun at that point; `aclosing` runs it.
- `publish` by `gather(..., return_exceptions=True)` then `ExceptionGroup`: `["history LOADED", "1 subscriber(s) failed: ['history full']"]`. By `TaskGroup`: the history subscriber never logs. The member gates the subscribers on an `Event` so the order doesn't rest on `sleep(0)`.
- A command worker over `Queue.shutdown()`: `["booked CN-1", "failed: no slot", "redirected CN-1", "worker stopped"]`.

**I. What mypy catches with async code** (probe module, `--strict`):
- `return source.quote(1)` from `-> RateQuote`: `Incompatible return value type (got "Coroutine[Any, Any, RateQuote]", expected "RateQuote")  [return-value]` with the note `Maybe you forgot to use "await"?`.
- `source.quote(1)` as a statement: `Value of type "Coroutine[Any, Any, RateQuote]" must be used  [unused-coroutine]`, note `Are you missing an await?`.
- `q = source.quote(1); return q.total`: `[attr-defined]` plus `[no-any-return]`.
- A class with `def quote(self, kg: int, /) -> RateQuote` passed where `RateSource` (an `async def quote`) is expected: `[list-item]` in a list literal (`[arg-type]` as an argument: executor check), with the note `Expected: def quote(self, int, /) -> Coroutine[Any, Any, RateQuote]`. A `def quote(...) -> Awaitable[RateQuote]` is refused the same way.
- A sync function in a `dict[str, Callable[[int], Awaitable[RateQuote]]]`: `[dict-item]`.
- Silent under `--strict`: `_ = source.quote(1)` (the runtime warning is the only witness); `if source.quote(1):` (`[truthy-bool]` only when enabled); `asyncio.create_task(...)` with its result discarded (`[unused-awaitable]` only when enabled; ruff's RUF006, already selected, reports `Store a reference to the return value of asyncio.create_task`).

**J. ruff.** `--select ASYNC` passes the probe tests; RUF006 fires as above. No other new rule fires on idiomatic code.

**K. Buckets under asyncio** (for ch38's table, each row backed by a test):
- Iterator: dissolves (an async generator); the close rule is new (`aclosing`).
- Context manager: survives (`asynccontextmanager`); cancellation still runs the exit.
- Strategy: dissolves (an async callable or a Protocol method); the type now says "awaitable".
- Adapter: survives; adapting a blocking SDK means a thread (`to_thread`).
- Observer: survives; delivery to every subscriber needs `gather` with `return_exceptions`, not a `TaskGroup`.
- Command: survives; the queue's shutdown replaces the sentinel. The worker and its queue are POSA2's Active Object (name only).

**L. Sources, fetched 2026-11-06** (all `docs.python.org/3/...` pages carry the banner "Python 3.15.2 documentation"). Quotable, exactly as on the page:
- Glossary, global interpreter lock (https://docs.python.org/3/glossary.html): "The mechanism used by the CPython interpreter to assure that only one thread executes Python bytecode at a time." and "Also, the GIL is always released when doing I/O." The "free threading" entry: "In free-threaded Python, multiple Python threads can run Python code simultaneously on different cores."
- threading (https://docs.python.org/3/library/threading.html), "GIL and performance considerations": "However, the GIL limits the performance gains of threading when it comes to CPU-bound tasks, as only one thread can execute Python bytecode at a time."
- sys (https://docs.python.org/3/library/sys.html), `_is_gil_enabled`: "Return True if the GIL is enabled and False if it is disabled." and "CPython implementation detail: It is not guaranteed to exist in all implementations of Python."
- Free-threading how-to (https://docs.python.org/3/howto/free-threading-python.html): "If the variable is set to 1, then the build supports free threading. This is the recommended mechanism for decisions related to the build configuration."; "It’s recommended to use the threading.Lock or other synchronization primitives instead of relying on the internal locks of built-in types, when possible." (curly apostrophe on the page); the overhead sentence "On the pyperformance benchmark suite, the average overhead ranges from about 1% on macOS aarch64 to 8% on x86-64 Linux systems."
- concurrent.futures (https://docs.python.org/3/library/concurrent.futures.html): `InterpreterPoolExecutor` "Each interpreter has its own Global Interpreter Lock, which means code run with this executor has true multi-core parallelism."; "each module imported in an interpreter is a completely separate object from the same module in a different interpreter"; `ProcessPoolExecutor` "only picklable objects can be executed and returned."
- What's New in 3.14 (https://docs.python.org/3/whatsnew/3.14.html): heading "PEP 779: Free-threaded Python is officially supported"; "free-threading is a supported Python build option now and into the future"; "On Unix platforms other than macOS, ‘forkserver’ is now the default start method".
- What's New in 3.15 (https://docs.python.org/3/whatsnew/3.15.html): "Added TaskGroup.cancel to allow early termination of a task group".
- Coroutines and tasks (https://docs.python.org/3/library/asyncio-task.html): `TaskGroup` "The first time any of the tasks belonging to the group fails with an exception other than asyncio.CancelledError, the remaining tasks in the group are cancelled."; `cancel()` "This is a non-exceptional, early exit of the task group’s lifetime"; `create_task` "The event loop only keeps weak references to tasks."; `to_thread` note "Due to the GIL, asyncio.to_thread() can typically only be used to make IO-bound functions non-blocking." (the sentence ties the two chapters; ch38 quotes it).
- Queues (https://docs.python.org/3/library/asyncio-queue.html): "Put a Queue instance into a shutdown mode."; "Once the queue is empty, future calls to get() will raise QueueShutDown."; "Use caution when using join() with immediate set to true."
- Developing with asyncio (https://docs.python.org/3/library/asyncio-dev.html): "Blocking (CPU-bound) code should not be called directly."; the never-awaited section's sample output `RuntimeWarning: coroutine 'test' was never awaited`.
- PEP 703 "Making the Global Interpreter Lock Optional in CPython" and PEP 779 "Criteria for supported status for free-threaded Python" (peps.python.org), by title.
- POSA2 (Wiley product page, table of contents): "2.5 Synchronization Patterns": Scoped Locking, Strategized Locking, Thread-Safe Interface, Double Checked Locking Optimization; "2.6 Concurrency Patterns": Active Object, Monitor Object, Leader/Followers, Half Sync/Half-Async, Thread-Specific Storage; "2.3 Event Handling Patterns": Reactor, Proactor. Names only.
- ruff RUF006 (https://docs.astral.sh/ruff/rules/asyncio-dangling-task/): "Checks for asyncio.create_task and asyncio.ensure_future calls that do not store a reference to the returned result."
- Not verified: *Fluent Python* chapter titles (decision 10).
- Not yet fetched, for U5b: `contextlib.aclosing` and `asynccontextmanager` sentences.

**M. Repo facts.**
- **Reconciliation.** Rows run 1 to 211, so r18 adds 212 to 231. Legacy rows 17 to 19 (ch37) and 20 to 23 (ch38) are carried and noted "r18" (U0); expected outcomes in the reconciliation section. `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** `_data/diagrams.yml` has 37 entries; r18 makes 39.
- **Test names.** 841 `def test_` lines across `examples` and `spikes` (three known duplicates). All 36 names in the Example spec were checked against that list; none clashes.
- **Members.** No member uses project `gil-and-performance` or `asyncio-patterns`, or package `gil_and_performance` or `asyncio_patterns`.
- **Promises these chapters must honour** (exact sentences in earlier chapters):
  - "Singleton: module, Borg, and metaclass": "Why threads interleave at all is the subject of The GIL and performance." ch37 explains the switch interval and the GIL handoff, and points back by title for `functools.cache` (the ch18/ch37 non-overlap rule: ch37 doesn't re-teach it).
  - "Shortcut patterns: dict dispatch, function tables, and EAFP": "See also The GIL and performance." after its forced eviction race. ch37 says why the natural race is rare on the default build (evidence D), by title pointer only.
  - "Context managers": "The `async with` counterpart of all this is in the chapter titled asyncio and the patterns." ch38's session.
  - "Command, undo, and command queues": "For queues shared across concurrent tasks, see asyncio and the patterns." ch38's command queue.
  - "Iterator: generators and the iterator protocol": "Asynchronous generators aren't part of this chapter". ch38's feed and `aclosing` (non-overlap rule ch24/ch38).
  - "The three-way split": the Iterator row's "async form in asyncio and the patterns". ch38's bucket table.
  - "Observer": "`Signal` is single-threaded ... Publishing from several threads is outside this chapter." ch38 publishes from tasks on one thread and says so; neither chapter publishes from threads.
  - `bibliography.html`: POSA2's Monitor Object and Active Object "read against the GIL and asyncio chapters" (decision 10).
  - Part blurb: "Two chapters on the GIL and performance, and on how asyncio reshapes the patterns."
- **Status board hygiene.** r17 is merged (f60cca0) but `iteration-plan.md` marks r17 "(active)" and PDP-135a to 136c `active`, and r17's T6 and T7 read `todo`. The orchestrator closes them at U0.
- **Stale-version check.** "Python 3.13" or "3.14.x" in prose must follow `since `, `before `, `until ` or `new in ` within 16 characters; "the 3.14 release" passes because it matches neither pattern.

## What is new in each chapter

**ch37 (the GIL is an interpreter lock, not yours).**
- Two builds, and how a program tells which one it's on.
- `+=` is separate steps; a forced interleaving double-books a slot on both builds; a lock fixes it only if it covers the read.
- CPU-bound rating through thread, process and interpreter pools: the same answers everywhere, different sharing, different costs.
- Why asyncio doesn't help CPU-bound work: a coroutine that never awaits holds the loop.
- What the benchmark measured, on which build, and why no test asserts it.

**ch38 (the patterns, where an await changes them).**
- A coroutine is a value until it's awaited; what mypy and the runtime each catch.
- The async forms of Iterator, Context manager, Strategy, Adapter, Observer and Command, each with the rule that's new.
- `TaskGroup`, `TaskGroup.cancel()`, `asyncio.timeout` and `Queue.shutdown` as the 3.15 mechanisms.
- An `await` is a visible switch point: no `await`, no interleaving; an `await` in a read-modify-write needs `asyncio.Lock`.

## Approach

- **Thesis wording.**
  - ch37: the GIL makes one thread at a time run bytecode in a default build; it never made a read-modify-write atomic, and the free-threaded build removes even that. Correctness comes from your lock or from not sharing; speed comes from the right executor for the build and the work, measured, never assumed.
  - ch38: asyncio keeps most patterns and changes their edges. Each await is a point where another task may run, every coroutine must be awaited, and cancellation is an exception that cleanup must survive. The 3.15 standard library gives each pattern the mechanism it needs: `aclosing`, `asynccontextmanager`, `TaskGroup`, `timeout`, `Queue.shutdown`.
- **One uv member per chapter**, standalone and named after its package, with no `[tool.*]` table:
  - `examples/37-the-gil-and-performance` (project `gil-and-performance`, package `gil_and_performance`);
  - `examples/38-asyncio-and-the-patterns` (project `asyncio-patterns`, package `asyncio_patterns`).
- **mypy witnesses.** Copy `_run` and `_codes` from `examples/36-refactor-or-rewrite/tests/test_static.py`. Each static test asserts the exit status, the exact sorted code list and one stable substring, never line numbers, and names its credited thing and a mutation that fails it.
- **Negative witness rule.** Every pinned behaviour in `src` has a test that fails when it's changed (deletion tables).
- **Comparison and seam code** lives in conftest and reaches tests through fixtures: ch37's `_RecordingLock`; ch38's `_TaskGroupSignal` (the one comparison form) and its gated subscribers. Shared tables live in the test module that uses them; conftest types are imported under `TYPE_CHECKING` only.
- **Determinism** (decision 8). Lists and tuples only in failing assertions, never a set or dict repr. No assertion names an address or a module path.
- **Counts** come from the code; the pytest summary line wins.
- **Repair rule (r12).** After every repair the validator re-reads the paragraph and the close bullets that depend on it.
- **Excerpt rule.** At most six excerpts per chapter. ch38 shows one comparison excerpt (`_TaskGroupSignal.publish`); ch37 shows none from conftest except the recording lock's `__enter__` if the word budget allows (it is a seam, not a comparison form).

Rejected in either `src`: `monkeypatch`, `mock`, `patch`, `Any`, `cast`, `Optional`, `random`, `global`, `sys.modules`, `time.sleep`, `asyncio.sleep`, `perf_counter`, `print(`. `print(` is allowed only in `examples/37-*/bench/gil_bench.py`.

## Per-chapter spec

### ch37: The GIL and performance (hands-on)

Thesis: as above. Sections (about 2,350 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~110), five bullets, one per close bullet:
   - say what the GIL guarantees and what it doesn't, and tell which build is running;
   - force a lost update between two threads and fix it with a lock that covers the read;
   - choose between thread, process and interpreter pools for CPU-bound rating, knowing what each shares and copies;
   - explain why a CPU-bound coroutine stalls the event loop;
   - read a benchmark as a measurement of one build on one machine, and keep it out of the tests.
2. `## Why this matters` (~180). Intent first: two bookings reserve a slot on the same sailing from two threads. Under the default build the natural race didn't show in 300 trials (example run), which is why it ships. A forced interleaving double-books the slot every time (test 3), and on the free-threaded build the natural race showed in every trial (example run).
3. Figure plus one paragraph (~50).
4. `## Two builds, one question` (~350).
   - Quote the glossary sentence. Quote "PEP 779: Free-threaded Python is officially supported" by heading and "free-threading is a supported Python build option now and into the future".
   - Excerpt `build.py` (`gil_disabled_build`, `gil_enabled`). Quote the how-to's "recommended mechanism" sentence and the `sys` docs' implementation-detail sentence. Tests 1 and 2.
   - One clause: `sysconfig.get_config_var` is typed `Any`, so the function wraps it in `bool` (test 10).
   - The default build switches threads every `sys.getswitchinterval()` seconds (0.005, from the `sys` docs; executor fetches the sentence), which is why threads interleave at all (the Singleton chapter's promise).
5. `## The GIL is not your lock` (~450).
   - `dis` shows `+=` as load, add, store (test 4).
   - Excerpt `StowagePlan.reserve`. Forced with a `Barrier` in the gap and no lock, two threads take the same `SlotId` on either build (test 3).
   - With the lock, a recording lock makes the second thread arrive while the first holds it, and each gets its own slot (test 5). Moving the read outside the lock loses a booking again (experiment a). This is POSA2's Monitor Object, and `with` is its Scoped Locking (names only).
   - Example run: the natural race, 0 of 300 trials on the default build and 300 of 300 on the free-threaded build. Quote the how-to's "use the threading.Lock" sentence. One pointer to "Singleton: module, Borg, and metaclass" for `functools.cache` under threads, and one to "Shortcut patterns: dict dispatch, function tables, and EAFP" for a race on a read; neither re-taught.
6. `## Rating a batch: threads, processes, interpreters` (~450).
   - Excerpt `rate_batch` and `POOLS`. Every pool gives the serial answers (test 6).
   - Threads share the argument; processes and interpreters receive a copy (test 7). Quote `ProcessPoolExecutor`'s "only picklable objects" and the interpreter page's "completely separate object" sentence. A lambda can't reach a process (test 8). One clause on `forkserver`, quoted from What's New in 3.14.
   - Quote the threading docs' CPU-bound sentence and `InterpreterPoolExecutor`'s "own Global Interpreter Lock" sentence, then the free-threading glossary sentence: on the free-threaded build, a thread pool is the third parallel option.
7. `## Why asyncio doesn't help here` (~200). A coroutine that never awaits holds the loop (test 9); quote "Blocking (CPU-bound) code should not be called directly." One pointer to "asyncio and the patterns" by title, describing nothing.
8. `## What the benchmark measured` (~300). The recorded table (decision 3), one example run per build. Warm and cold pools, the I/O rows. Say which differences are larger than run-to-run variation in the recorded runs and stop there. Quote the docs' overhead sentence beside the serial rows. No test asserts any of it.
9. `## When threads are the wrong tool` (~200). Pick by the work and the build: I/O waits suit threads or asyncio on either build; CPU-bound pure Python wants processes or interpreters on the default build, and may use threads on the free-threaded one once every shared write is locked. Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Parallel code that assumes the GIL.** "Speed up rating with threads" can produce code whose shared writes rely on one thread running at a time, which the free-threaded build doesn't give. Paste a prompt that makes the sharing explicit:

   > Rate the batch through `rate_batch` with a `PoolFactory` from `POOLS`, passing consignments in and returning quotes, with no shared mutable state. Where state must be shared, as in `StowagePlan.reserve`, hold one lock across the read and the write, and add a test that parks two threads in the gap with a `threading.Barrier`. Report timings from `bench/gil_bench.py` on both builds, not from a test.

   If a test asserts a duration, ask which build and machine it was written for.</blockquote>

   At most 120 words; every backticked name exists in `src`, the tests, the bench or the standard library.
10. `## Build, run, observe` (~200 plus output). From the repository root once `uv sync --locked --all-packages`, then `cd examples/37-the-gil-and-performance`, `uv run pytest -v`, `uv run mypy --strict src tests`, `uv run python bench/gil_bench.py` (the reader's numbers will differ). The free-threaded run, as an optional block: `uv python install 3.15t`, `UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15t --locked --all-packages` from the root, then `.venv-ft/bin/python -m pytest examples/37-the-gil-and-performance` (decision 2; omit under option A). Experiments run in fresh scratch copies (delete `.venv`, `uv sync --locked --all-packages`, confirm `gil_and_performance.__file__` points into the copy). The stated filter is r17's: `uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'`, then `uv run mypy --strict src tests`. No repo script and no `host_ids.py` in any reader command.
    - (a) In `src/gil_and_performance/stowage.py`, move the line that picks the slot above `with self._lock:`.
      - Expected: test 5 fails with both threads on `SlotId(bay=1, row=1, tier=1)`; test 3 passes; mypy exits 0 (executor check: exact `E` lines).
    - (b) Restore, then in `rate_batch` map `lambda consignment: quote(consignment)` instead of `quote`.
      - Expected: test 6[process] fails with `Can't pickle`; mypy exits 0. Executor check: whether 6[interpreter] passes (evidence E). Quote only what two runs agree on.
11. `## What you can do now` (~130): five bullets in objective order. They name `gil_disabled_build` and `gil_enabled` with tests 1 and 2; `StowagePlan.reserve` with tests 3 and 5; `rate_batch`, `POOLS` and test 7; test 9; `bench/gil_bench.py` and its recorded output. Every backticked token appears earlier.
12. `## For deeper coverage` (~120): the glossary, threading, sys, free-threading how-to and concurrent.futures pages; What's New in 3.14; PEP 703 and PEP 779; POSA2 (Monitor Object, Scoped Locking); *Fluent Python* by topic; one title pointer to "asyncio and the patterns"; the bibliography link.

Figure `37-the-gil-and-performance` (vertical, two lanes, one bar):
- **Top:** "StowagePlan.reserve: pick slot, gap, store".
- **Left lane** (muted): "two threads meet in the gap (Barrier)", then a dashed box "both take the same SlotId, on either build".
- **Right lane** (accent): "_RecordingLock: second caller waits at the door", then "each thread gets its own SlotId".
- **Bottom bar:** "the GIL runs one thread's bytecode at a time; only your lock covers the read and the write".
- No digits in the SVG.

Caption draft (about 38 words with the prefix): "Figure 37.1: Two threads reserving a slot on one sailing. Parked between reading and writing, both take the same slot on either build; a lock that covers the read and the write gives each its own." U3 counts and adjusts.

### ch38: asyncio and the patterns (hands-on)

Thesis: as above. Sections (about 2,400 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~120), six bullets:
   - say what an `await` changes, and what mypy and the runtime each catch when one is missing;
   - write a carrier feed as an async generator and close it with `aclosing`;
   - write a carrier session that closes the feed when its body raises or its task is cancelled;
   - quote carriers through an async Protocol, adapt a blocking SDK, and stop the group on a failure, a first answer or a timeout;
   - publish to async subscribers and queue coroutine commands, and shut the queue down;
   - protect a read-modify-write that spans an `await`.
2. `## Why this matters` (~180). Intent first: tracking events arrive from a carrier's live feed and quotes from two carriers at once. A quote assigned without `await` is a coroutine, not a quote (test 1); mypy reports it (test 22) and the never-awaited warning fails the test run (test 2).
3. Figure plus one paragraph (~50).
4. `## What an await changes` (~300). Coroutine as a value (tests 1, 2); mypy's three codes (tests 22, 23) and what it misses (test 25), with RUF006 in one clause. An `await` is the only place another task can run: an `await` between read and write double-books a slot (test 20); `asyncio.Lock` fixes it (test 21). Contrast in one sentence with threads: without an `await` there is no interleaving; one pointer to "The GIL and performance" by title.
5. The bucket table (~120): pattern, bucket, the async rule, the test (evidence K).
6. `## Iterator: the carrier's live feed` (~300). Excerpt `handling_events`. Order and close at the end (test 3); `break` leaves it open (test 4); `first_departure` closes it with `aclosing` (test 5). Annotated `AsyncGenerator`, which mypy needs for `aclose` (spike 015, one clause).
7. `## Context manager: a session that survives cancellation` (~250). Excerpt `carrier_session`. Closes on an exception (test 6) and on cancellation by `asyncio.timeout(0)` (test 7). Cancellation is an exception; cleanup in `finally` or `__aexit__` runs.
8. `## Strategy and Adapter: quoting carriers together` (~400). Excerpt `RateSource` and `AircoSource`. mypy refuses a blocking source (test 24). The adapter runs the SDK in a thread so the loop keeps running (test 9); quote the `to_thread` GIL note. `cheapest` (test 8) runs sources in a `TaskGroup`: a failing carrier cancels the other quote (test 10; quote the TaskGroup sentence). `first_quote` stops the group at the first answer with `TaskGroup.cancel()` (test 11; quote What's New in 3.15). `within=0` cancels a quote that never answers (test 12).
9. `## Observer: every subscriber hears the event` (~300). Excerpt `AsyncSignal.publish` and the comparison excerpt `_TaskGroupSignal.publish`. Order on the shared table (test 13), a failure doesn't stop the others under `gather` (test 14) and does under a `TaskGroup` (test 15); unsubscribe (test 16). The Observer chapter's rule stays: run everyone, then raise one group. One pointer to "Observer" by title.
10. `## Command: a queue that shuts down` (~300). Excerpt `run_commands`. In order with a failure recorded (test 17); `shutdown()` drains and stops the worker (test 18), `shutdown(immediate=True)` drops the rest (test 19; quote the `join()` caution); a closed queue refuses a command (test 26). The worker and queue are an Active Object (POSA2, name only). One pointer to "Command, undo, and command queues" by title.
11. `## When asyncio is the wrong tool` (~150). CPU-bound work (pointer to "The GIL and performance"), a codebase with no async I/O to wait on, a single sequential call. Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Async code that forgets an await or a cancellation.** "Make the carrier calls async" can leave a coroutine unawaited, a blocking SDK on the loop, or a feed that stays open when its task is cancelled. Paste a prompt that names each edge:

    > Make `RateSource.quote` an `async def` and adapt the blocking AIRCO SDK with `asyncio.to_thread`. Run the sources in an `asyncio.TaskGroup` under `asyncio.timeout(within)`. Open the feed with `carrier_session` and read it through `contextlib.aclosing`. Stop the command worker with `Queue.shutdown()`, not a sentinel. Run mypy `--strict` and pytest with `filterwarnings = ["error"]`.

    If a test awaits `asyncio.sleep` with a non-zero delay, ask which event it is waiting for.</blockquote>
12. `## Build, run, observe` (~200 plus output). Same rules and filter as ch37 (confirm `asyncio_patterns.__file__`).
    - (a) In `src/asyncio_patterns/feed.py`, replace `async with aclosing(handling_events(session)) as events:` in `first_departure` with `events = handling_events(session)`.
      - Expected: test 5 fails (the feed is still open); mypy exits 0 (executor check on the `E` lines).
    - (b) Restore, then in `AsyncSignal.publish` remove `return_exceptions=True`.
      - Expected: test 14[gather] fails, because `gather` raises the subscriber's `LookupError` and the test expects one `ExceptionGroup`; mypy exits 0 or reports the narrowed results list (executor check).
13. `## What you can do now` (~140): six bullets mapped to the objectives, naming tests 22 and 20; `handling_events` and `first_departure`; `carrier_session` and test 7; `RateSource`, `AircoSource`, `cheapest` and `first_quote`; `AsyncSignal` and `run_commands`; `StowagePlan.reserve` and test 21.
14. `## For deeper coverage` (~120): asyncio's tasks, queues and "Developing with asyncio" pages; `contextlib`; What's New in 3.15; POSA2 (Active Object, Reactor by name); *Fluent Python* by topic; ruff's RUF006; one title pointer to "The GIL and performance"; the bibliography link.

Figure `38-asyncio-and-the-patterns` (vertical):
- **Top:** "carrier_session: open the feed" (accent).
- **Then:** "handling_events (async generator)", then "AsyncSignal.publish: gather, every subscriber runs".
- **Side lane:** "cheapest: TaskGroup over RateSource; AircoSource runs the SDK in a thread".
- **Then:** "run_commands: Queue until shutdown".
- **Bottom bar:** "every await is a switch point; cancellation runs the session's cleanup".
- **Muted dashed box:** "_TaskGroupSignal: one failing subscriber cancels the rest".
- No digits in the SVG.

Caption draft (about 40 words): "Figure 38.1: A carrier session feeds tracking events to async subscribers while quotes run in a task group and commands drain from a queue. Each await is a point where another task may run, and cancellation still closes the session." U3 counts and adjusts.

Citations, both chapters: verify each before writing; quote no sentence unless checked on a fetched page; stop each quotation where the page's sentence stops; keep the docs' curly apostrophes or stop before them; no outcome claim, no comparison between languages.

## Example spec

### `examples/37-the-gil-and-performance` (project `gil-and-performance`, package `gil_and_performance`)

`pyproject.toml` in the r17 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`).

- **`domain.py`**: `ConsignmentId` (`NewType`); frozen slotted `Consignment(id, zone, weight_kg: Decimal)`; `Money(amount, currency="EUR")`; `RateQuote(consignment_id, total: Money)`; frozen slotted, ordered `SlotId(bay, row, tier)`.
- **`build.py`**: `gil_disabled_build() -> bool` (`bool(sysconfig.get_config_var("Py_GIL_DISABLED"))`) and `gil_enabled() -> bool` (`sys._is_gil_enabled()`), with docstrings quoting nothing and naming `PYTHON_GIL`.
- **`stowage.py`**: `StowagePlan(sailing: str, *, lock: AbstractContextManager[object] | None = None, gap: Callable[[], None] = _no_gap)`. `reserve(consignment_id) -> SlotId` holds the lock across picking `SlotId(1, 1, len(reservations) + 1)`, calling `gap()` and storing; `reservations` returns a read-only view (`MappingProxyType`). Default lock `threading.Lock()`. Docstring: the gap is a test seam; the class is a Monitor Object.
- **`rating.py`**: `quote(consignment, /) -> RateQuote`, pure-Python `Decimal` arithmetic over the weight in 100 g steps (deterministic, CPU-bound, illustrative prices), quantised half up.
- **`pools.py`**: `type PoolFactory = Callable[[int], Executor]`; `POOLS = frozendict(thread=ThreadPoolExecutor, process=ProcessPoolExecutor, interpreter=InterpreterPoolExecutor)`; `rate_batch(batch, /, *, pool: PoolFactory, workers: int = 4) -> list[RateQuote]` via `executor.map(quote, batch)`; `append_reserved(reserved: list[ConsignmentId], consignment_id) -> int` (the sharing witness, documented as such).
- `py.typed`, and an `__init__.py` that imports nothing.
- **`bench/gil_bench.py`** (decision 3) and its recorded outputs. Not under mypy (verify.sh covers `src tests`); ruff covers it.

`tests/conftest.py`:
- `_RecordingLock`: counts callers in `__enter__`, sets an `Event` at the second, then takes a real `Lock`; `second_caller` property.
- fixture `recording_lock`; fixture `two_threads(plan) -> list[SlotId]` (start both, join, return sorted slots) with the 10 s guard.

`test_build.py`:
1. `test_the_build_flag_and_the_runtime_gil_state_agree`: `gil_enabled() is not gil_disabled_build()`.
2. `test_sys_version_names_the_free_threading_build_only_on_that_build`: `("free-threading build" in sys.version) is gil_disabled_build()`.

`test_stowage.py`:
3. `test_two_threads_parked_between_read_and_write_take_the_same_slot`: `lock=nullcontext()`, `gap=Barrier(2).wait` gives `[SlotId(1, 1, 1), SlotId(1, 1, 1)]` and one reservation.
4. `test_an_attribute_increment_is_a_separate_load_add_and_store`: a test-only `_Tally.bump` (`self.count += 1`); the opnames contain `LOAD_ATTR`, `BINARY_OP`, `STORE_ATTR` in that order.
5. `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot`: recording lock, gap waits for the second caller; `[SlotId(1, 1, 1), SlotId(1, 1, 2)]`, two reservations, `second_caller` true.

`test_pools.py` (holds `BATCH`, 8 consignments):
6. `test_every_pool_rates_the_batch_as_the_serial_loop_does` x pool (`thread`, `process`, `interpreter`) = 3.
7. `test_threads_share_the_argument_and_processes_and_interpreters_copy_it` x (`thread`, `["CN-1"]`), (`process`, `[]`), (`interpreter`, `[]`) = 3.
8. `test_a_process_pool_cannot_send_a_lambda`: `pytest.raises(pickle.PicklingError, match="Can't pickle")`.

`test_loop.py`:
9. `test_a_coroutine_that_never_awaits_holds_the_loop_until_it_returns`: `["rating started", "rating finished", "tracking polled"]`.

`test_static.py`:
10. `test_mypy_types_the_build_flag_as_any`: a snippet returning `sysconfig.get_config_var("Py_GIL_DISABLED") == 1` from `-> bool` gives `["no-any-return"]`; the `src` form gives `[]`. Credits `bool(...)` in `build.py`. Mutation: dropping `bool(` in `src` makes `mypy --strict src` report `no-any-return` (U1a quotes it).

Planned: 10 test functions, 14 cases (`test_build.py` 2/2, `test_stowage.py` 3/3, `test_pools.py` 3/7, `test_loop.py` 1/1, `test_static.py` 1/1). The pytest summary line wins. U1a runs the member on both builds (decision 2) with the same count.

Also `README.md` and the card `_examples/37-the-gil-and-performance.md`: `order: 37`, eyebrow "Concurrency · The GIL and performance", a concept title with no count. Cards and READMEs carry only claims the tests back; no benchmark number.

Deletion table (U1a; each in a fresh scratch copy):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| read inside the lock | moved above `with` (experiment a) | 5 | both threads take tier 1 |
| `gap()` between read and write | removed | 3 | the barrier is never met; threads take two slots (executor check: barrier guard) |
| `bool(` in `gil_disabled_build` | `== 1` without `bool` | 10's mutation run | `no-any-return` |
| `POOLS["process"]` | `ThreadPoolExecutor` | 7[process] | the caller's list holds `CN-1` |
| `executor.map(quote, ...)` | a lambda (experiment b) | 6[process] | `Can't pickle` |
| read-only `reservations` | returns the dict | executor adds a test if nothing fails (criterion 6) | |

### `examples/38-asyncio-and-the-patterns` (project `asyncio-patterns`, package `asyncio_patterns`)

- **`domain.py`**: `ConsignmentId`; `HandlingKind` enum (`BOOKED`, `LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED`); frozen slotted `HandlingEvent(consignment_id, kind, location)` with UN/LOCODE locations (`NLRTM`, `SGSIN`); `Consignment(id, zone, weight_kg: Decimal)`; `Money`; `RateQuote(consignment_id, carrier, total)`; `CarrierTimeoutError`; `SlotId`.
- **`feed.py`**: `CarrierFeed` Protocol (`async def next_event(self) -> HandlingEvent | None`, `async def close(self) -> None`); `InMemoryFeed` (stand-in SDK, no I/O, records `closed`; can be told to wait forever on an `Event`); `handling_events(feed) -> AsyncGenerator[HandlingEvent]` (closes the feed in `finally`); `first_departure(feed) -> HandlingEvent | None` with `aclosing`; `carrier_session(feed)` as an `asynccontextmanager` yielding the feed and closing it in `finally`.
- **`quoting.py`**: `RateSource` Protocol (`async def quote(self, consignment, /) -> RateQuote`); `FastlineSource` (async stand-in); `AircoClient` (blocking stand-in SDK, `price(*, destination, grams) -> int` cents, may wait on an injected `threading.Event`); `AircoSource` adapter over `asyncio.to_thread`; `cheapest(consignment, /, sources, *, within: float | None = None) -> RateQuote` (TaskGroup inside `asyncio.timeout(within)`, min by `(total, carrier)`); `first_quote(consignment, /, sources) -> RateQuote` (`TaskGroup.cancel()` on the first answer).
- **`signal.py`**: `type Subscriber[E] = Callable[[E], Awaitable[None]]`, `type Unsubscribe = Callable[[], None]`; `AsyncSignal[E]` with `subscribe` and `async publish` (snapshot, `gather(..., return_exceptions=True)`, then one `ExceptionGroup` of the `Exception`s in subscription order; a `BaseException` such as `CancelledError` propagates).
- **`commands.py`**: `type BookingCommand = Callable[[], Awaitable[str]]`; `run_commands(queue: asyncio.Queue[BookingCommand], log: list[str]) -> None` (until `QueueShutDown`; records `failed: <message>` for an `Exception` and carries on; `task_done` in `finally`).
- **`stowage.py`**: async `StowagePlan(sailing, *, lock: asyncio.Lock | None = None)` with `async reserve(consignment_id, confirm: Callable[[], Awaitable[None]]) -> SlotId` that picks the slot, awaits `confirm()`, stores; with a lock, the three steps run under it. The lock is a keyword, `lock: asyncio.Lock | None`, defaulting to a fresh `asyncio.Lock`; `None` means no lock and exists only for the double-booking test, which the docstring says.
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- fixture `publish_form` (`gather|taskgroup`) returning a signal factory; `_TaskGroupSignal[E]` publishes in a `TaskGroup` (the comparison form);
- `_GatedSubscriber` (records into a list after an `asyncio.Event`), `_FailingSubscriber`;
- fixture `feed_of(*events)`.

`test_await.py`:
1. `test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote` (closes it).
2. `test_a_quote_that_is_never_awaited_warns_when_it_is_collected`: `pytest.warns(RuntimeWarning)`; messages equal `["coroutine 'FastlineSource.quote' was never awaited"]` (executor check on the qualname).

`test_feed.py`:
3. `test_the_feed_yields_events_in_order_and_closes_at_the_end`.
4. `test_breaking_out_of_async_for_leaves_the_feed_open`.
5. `test_first_departure_closes_the_feed_when_it_stops_early`.
6. `test_the_session_closes_the_feed_when_its_body_raises`.
7. `test_the_session_closes_the_feed_when_its_task_is_cancelled` (`asyncio.timeout(0)`, `TimeoutError`, `closed`).

`test_quoting.py`:
8. `test_the_cheapest_quote_wins_across_an_async_and_an_adapted_source`.
9. `test_the_adapter_runs_the_blocking_sdk_in_a_thread_while_the_loop_runs` (`["loop ran", "AIRCO ..."]`).
10. `test_a_failing_carrier_cancels_the_other_quote` (`except* CarrierTimeoutError`; the other source records `cancelled`).
11. `test_the_first_answer_cancels_the_rest_of_the_group` (`TaskGroup.cancel`).
12. `test_a_zero_timeout_cancels_a_quote_that_never_answers`.

`test_signal.py` (holds `EVENTS`):
13. `test_every_subscriber_hears_each_event_in_subscription_order` x `publish_form` (2).
14. `test_a_failing_subscriber_does_not_stop_the_others` (gather form): one `ExceptionGroup`, the gated subscriber still recorded.
15. `test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails` (taskgroup form): the gated subscriber recorded nothing.
16. `test_an_unsubscribed_subscriber_hears_nothing` x `publish_form` (2).

`test_commands.py`:
17. `test_queued_commands_run_in_order_and_a_failure_is_recorded`.
18. `test_shutdown_lets_the_worker_drain_the_queue_then_stop`.
19. `test_an_immediate_shutdown_drops_the_pending_commands`.
26. `test_a_shut_down_queue_refuses_a_new_command` (`QueueShutDown`). Numbered 26 so that tests 20 to 25 keep the numbers the prose spec cites.

`test_stowage.py`:
20. `test_an_await_between_read_and_write_double_books_a_slot`: five tasks, no lock, `confirm` is `asyncio.Barrier(5).wait`; five `SlotId(1, 1, 1)`, one reservation.
21. `test_an_asyncio_lock_gives_each_task_its_own_slot`: tiers 1 to 5.

`test_static.py`:
22. `test_mypy_reports_a_quote_returned_without_await`: `["return-value"]`, substring `Maybe you forgot to use "await"?`. Mutation: adding `await` empties the list.
23. `test_mypy_reports_a_quote_call_whose_result_is_never_used`: `["unused-coroutine"]`.
24. `test_mypy_refuses_a_blocking_source_where_a_rate_source_is_expected`: passing a `def quote` class to `cheapest`: `["arg-type"]` (executor check against `list-item`), substring `Coroutine[Any, Any, RateQuote]`. Credits `async def` on `RateSource`. Mutation: declaring `RateSource.quote` as `def quote(...) -> RateQuote | Awaitable[RateQuote]` empties it.
25. `test_mypy_accepts_a_coroutine_bound_to_underscore`: `[]`, and the runtime half warns `never awaited` (both halves, r13 rule).

Planned: 26 test functions, 28 cases (`test_await.py` 2/2, `test_feed.py` 5/5, `test_quoting.py` 5/5, `test_signal.py` 4/6, `test_commands.py` 4/4, `test_stowage.py` 2/2, `test_static.py` 4/4). The pytest summary line wins.

Also `README.md` and the card `_examples/38-asyncio-and-the-patterns.md`: `order: 38`, eyebrow "Concurrency · asyncio and the patterns".

Deletion table (U1b):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| `aclosing` in `first_departure` | removed (experiment a) | 5 | feed still open |
| `finally` close in `carrier_session` | close after `yield` only | 7 | cancellation skips the close |
| `asyncio.to_thread` in `AircoSource` | direct call | 9 | the SDK waits on an Event only the loop can set: guard `TimeoutError` (executor check: duration) |
| `TaskGroup` in `cheapest` | sequential awaits | 10 | the other source is never cancelled, or isn't reached |
| `tg.cancel()` in `first_quote` | removed | 11 | the group waits for AIRCO: guard needed (executor designs a deterministic failure) |
| `return_exceptions=True` | removed (experiment b) | 14 | bare `LookupError` |
| snapshot in `publish` | iterate the live list | executor adds a test if nothing fails | |
| `task_done` in `finally` | after success only | 18 | `join()` never returns: guard (executor check) |
| `QueueShutDown` handling | catches `Exception` | 18 | worker never stops (executor check) |
| the lock in async `reserve` | removed | 21 | tiers repeat |

Rows marked "executor check" are resolved at U1b or moved to Corrections; a row whose failure is a guard timeout states the guard and the measured duration in the handback.

## Steps and status

Step ids are `U*` (decision 0). Only `U1a`, `U1b`, `U5a` and `U5b` are cited as `run:` tokens.

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| U0 | Bookkeeping with dated notes, re-checking the pins and recording the decisions. In `iteration-plan.md`: PDP-137a-c and 138a-c `active`, r18 active, r17 closed, PDP-135a to 136c closed. In r17's plan: T6 and T7 closed. In the reconciliation plan: rows 212-231 `open`; rows 17-23 noted "r18"; a dated note on the "Free-threaded Python is out of scope" sentence (decision 2). In `r01-build-plan.md`: a dated note on the free-threading line if decision 2 is B. Domain rows 37-38 as drafted in this commit. The ch37-38 stub `description` lines are written | - | done |
| U1a | ch37 member, bench and its two recorded outputs per build, card and README; one `uv lock`; three green runs and one reverse-order run on the default build, one green run on 3.15t (`.venv-ft`, decision 2); the deletion table and the static mutation run, each in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`), deleted after use | U0 | done |
| U1b | ch38 member, card and README; one `uv lock` after U1a; three green runs plus one reverse-order run, one on 3.15t; the deletion table; the static mutation runs. Adds the `free-threaded` job to `ci.yml` and to `ci-ok`'s `needs` (decision 2) | U1a | done |
| U2 | Witness results into rows 212-229. `_plans/evidence/r18-gil-benchmark.md` (scrubbed bench outputs, dated, labelled example runs). The dated r18 note in `_plans/spikes.md` (evidence B-J, decisions 5, 6 and 12). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | U1b | done |
| U3 | Two figures, specs `diagrams/specs/37-*.py` and `38-*.py`, and `_data/diagrams.yml` (single owner; 39 entries). Figures 00-36 unchanged. Every name drawn exists in `src`, conftest, the tests or the standard library | U2 | done |
| U4 | ch37-38 `status = "drafted"` (`kind` stays `hands-on`) | U3 | done |
| U5a | ch37 prose agent: re-fetch every source and quote exactly (including the `sys.getswitchinterval` sentence); run both experiments twice in fresh scratch copies with the stated filter; quote the recorded bench, never a fresh unrecorded run; scrub before quoting; hand back the sources checked and a per-paragraph claims table that marks each sentence as test, source or example run | U3, U4 | todo |
| U5b | ch38 prose agent, in parallel with U5a, with the same duties, plus fetching the `contextlib` sentences | U3, U4 | todo |
| U6 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also: close-to-objective mapping, the excerpt check, every speed sentence names its build and is labelled an example run (criterion 20), pointer promises (criterion 11), the cross-language and outcome greps | U5a, U5b | todo |
| U7 | PR, `ci-ok` green (including `free-threaded` under decision 2), ask the owner before merge; squash-merge; tag `r18.x` on main; notes-only release | U6 | todo |

Reconciliation rows (step U0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 212 | 37 | The build flag and the runtime GIL state agree, and `sys.version` names the free-threading build only on that build | `test_the_build_flag_and_the_runtime_gil_state_agree`, `test_sys_version_names_the_free_threading_build_only_on_that_build`, `source: https://docs.python.org/3/howto/free-threading-python.html`, `source: https://docs.python.org/3/library/sys.html` |
| 213 | 37 | An attribute increment is a separate load, add and store, and two threads parked between read and write take the same slot on either build | `test_an_attribute_increment_is_a_separate_load_add_and_store`, `test_two_threads_parked_between_read_and_write_take_the_same_slot`, `run: U1a` |
| 214 | 37 | A lock held across the read and the write gives each thread its own slot | `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot` |
| 215 | 37 | Thread, process and interpreter pools rate a batch as the serial loop does; threads share the argument, processes and interpreters receive a copy | `test_every_pool_rates_the_batch_as_the_serial_loop_does`, `test_threads_share_the_argument_and_processes_and_interpreters_copy_it`, `source: https://docs.python.org/3/library/concurrent.futures.html` |
| 216 | 37 | A process pool can't send a lambda | `test_a_process_pool_cannot_send_a_lambda`, `source: https://docs.python.org/3/library/concurrent.futures.html` |
| 217 | 37 | A coroutine that never awaits holds the event loop until it returns | `test_a_coroutine_that_never_awaits_holds_the_loop_until_it_returns`, `source: https://docs.python.org/3/library/asyncio-dev.html` |
| 218 | 37 | mypy types the build flag as `Any`, so the check wraps it in `bool` | `test_mypy_types_the_build_flag_as_any` |
| 219 | 37 | In the recorded example runs, threads don't speed up the CPU-bound batch on the default build and do on the free-threaded build; process and interpreter pools do on both | `run: _plans/evidence/r18-gil-benchmark.md`, `source: https://docs.python.org/3/library/threading.html` |
| 220 | 37 | What the GIL is, and that the free-threaded build is supported | `source: https://docs.python.org/3/glossary.html`, `source: https://docs.python.org/3/whatsnew/3.14.html` |
| 221 | 38 | A coroutine called without `await` is a coroutine, and one never awaited warns, which fails the run under `filterwarnings = ["error"]` | `test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote`, `test_a_quote_that_is_never_awaited_warns_when_it_is_collected`, `source: https://docs.python.org/3/library/asyncio-dev.html` |
| 222 | 38 | The feed yields in order and closes at the end; `break` leaves it open; `aclosing` closes it | `test_the_feed_yields_events_in_order_and_closes_at_the_end`, `test_breaking_out_of_async_for_leaves_the_feed_open`, `test_first_departure_closes_the_feed_when_it_stops_early` |
| 223 | 38 | The carrier session closes the feed when its body raises and when its task is cancelled | `test_the_session_closes_the_feed_when_its_body_raises`, `test_the_session_closes_the_feed_when_its_task_is_cancelled`, `source: https://docs.python.org/3/library/asyncio-task.html` |
| 224 | 38 | The cheapest quote wins across an async source and a blocking SDK adapted with `to_thread`, and the loop runs while the SDK blocks | `test_the_cheapest_quote_wins_across_an_async_and_an_adapted_source`, `test_the_adapter_runs_the_blocking_sdk_in_a_thread_while_the_loop_runs` |
| 225 | 38 | A failing carrier cancels the other quote, the first answer cancels the rest with `TaskGroup.cancel()`, and a zero timeout cancels a quote that never answers | `test_a_failing_carrier_cancels_the_other_quote`, `test_the_first_answer_cancels_the_rest_of_the_group`, `test_a_zero_timeout_cancels_a_quote_that_never_answers`, `source: https://docs.python.org/3/whatsnew/3.15.html` |
| 226 | 38 | An async signal delivers in subscription order and keeps delivering past a failing subscriber; a task-group publisher cancels the others; unsubscribing stops delivery | `test_every_subscriber_hears_each_event_in_subscription_order`, `test_a_failing_subscriber_does_not_stop_the_others`, `test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails`, `test_an_unsubscribed_subscriber_hears_nothing` |
| 227 | 38 | Queued commands run in order with failures recorded; shutdown drains then stops the worker, an immediate shutdown drops the rest, and a shut-down queue refuses a command | `test_queued_commands_run_in_order_and_a_failure_is_recorded`, `test_shutdown_lets_the_worker_drain_the_queue_then_stop`, `test_an_immediate_shutdown_drops_the_pending_commands`, `test_a_shut_down_queue_refuses_a_new_command`, `source: https://docs.python.org/3/library/asyncio-queue.html` |
| 228 | 38 | An `await` between read and write double-books a slot, and `asyncio.Lock` gives each task its own | `test_an_await_between_read_and_write_double_books_a_slot`, `test_an_asyncio_lock_gives_each_task_its_own_slot` |
| 229 | 38 | mypy reports a quote returned without `await`, an unused coroutine and a blocking source, and accepts a coroutine bound to `_` | `test_mypy_reports_a_quote_returned_without_await`, `test_mypy_reports_a_quote_call_whose_result_is_never_used`, `test_mypy_refuses_a_blocking_source_where_a_rate_source_is_expected`, `test_mypy_accepts_a_coroutine_bound_to_underscore` |
| 230 | 37-38 | mypy `--strict`, ruff and the idiom scan pass both members, and both members pass on the free-threaded build | `run: U1a`, `run: U1b` |
| 231 | 37-38 | The "Build, run, observe" experiments behave as quoted, and mypy exits 0 on each | `run: U5a`, `run: U5b` |

Legacy rows carried (U0 notes them "r18"; U2 sets the status):
- Row 17 (threads and CPU-bound against I/O-bound work): expected **adjusted (r18)**: scoped to the default build, witnessed by row 219's recorded runs; the free-threaded build differs.
- Row 18 (processes speed up CPU-bound work at a pickling and start-up cost): expected **adjusted (r18)**: the copy is witnessed by row 215, refusal by 216, the speed by row 219's runs (warm and cold), not three batch sizes.
- Row 19 (asyncio helps I/O and not CPU; a blocking call stalls the loop): expected **verified (r18)** by row 217 plus row 219's I/O rows.
- Row 20 (async generator as Iterator): **verified (r18)** by row 222.
- Row 21 (`async with` and cancellation): **verified (r18)** by row 223.
- Row 22 (a coroutine as Command; a forgotten `await` is detectable): **verified (r18)** by rows 221, 227 and 229.
- Row 23 (deterministic async tests need no sleep): **verified (r18)** by criterion 2's grep and three runs.

## Corrections after the build
- Step U3: figures 37 and 38 (39 entries). Scope words and the untested GIL clause were dropped from the ch37 bar. In figure 38 the orchestrator removed the arrow from `handling_events` to `AsyncSignal.publish` and reworded the caption's "feeds tracking events to async subscribers": no code or test connects the feed to the signal. `cheapest` and `run_commands` stand alone, with no arrows.

The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.

- **Step U1a:** the ch37 member is built (2026-11-06). Differences from the plan:
  - Counts: 11 test functions and 15 cases, against the planned 10 and 14. The extra function is `test_the_reservations_view_refuses_assignment` (`test_stowage.py`, now 4 functions), added because the read-only `reservations` deletion row failed nothing (criterion 6). Per file: `test_build.py` 2/2, `test_stowage.py` 4/4, `test_pools.py` 3/7, `test_loop.py` 1/1, `test_static.py` 1/1. The full suite is 1235 passed (1220 plus 15); the member is 15 passed on the default build and on 3.15t.
  - `StowagePlan.gap` is typed `Callable[[], object]`, not `Callable[[], None]`, because `Barrier.wait` returns an `int` and mypy refuses it as a `None`-returning callable. `reservations` maps `SlotId` to `ConsignmentId` (keyed by slot), which is what makes the parked pair leave one reservation. `quote` reads the zone from `_PRICE_PER_STEP` (`EU` and `ASIA`); an unknown zone raises `KeyError` and is not claimed.
  - Test 10 type-checks the unwrapped snippet with `-c` and `src/gil_and_performance/build.py` by path (not a snippet that imports it), so the `bool(` mutation fails the test. Its mutation run: `src` form reports `build.py:14: error: Returning Any from function declared to return "bool"  [no-any-return]`; the test fails with `At index 1 diff: ['no-any-return'] != []`.
  - Messages and values: the no-lambda test matches `Can't pickle` as planned. A lambda defined inside `rate_batch` is refused by the interpreter pool with `concurrent.interpreters.NotShareableError` (`... does not support cross-interpreter data`), unlike evidence E's lambda, which it accepted; so experiment (b) fails `[process]` and `[interpreter]` (2 failed, 13 passed), not `[process]` alone, and mypy exits 0. Quote only what two runs agree on. The pytest summary on a deletion run reads `1 failed, 14 passed` for every other row.
  - Deletion table, each in a fresh scratch copy: read above the lock fails test 5 (`At index 1 diff: SlotId(bay=1, row=1, tier=1) != SlotId(bay=1, row=1, tier=2)`); `gap()` removed fails test 3 promptly with no guard wait (`tier=2 != tier=1`); `bool(` dropped fails test 10; `POOLS["process"]` as a thread pool fails 7[process]; `POOLS["interpreter"]` as a thread pool fails 7[interpreter]; a lambda in `executor.map` fails 6[process] and 6[interpreter]; `reservations` returning the dict fails the added test; `gil_disabled_build` returning `True` fails tests 1 and 2; `+=` replaced by an assignment fails test 4; a reversed `rate_batch` fails 6 in all three; `append_reserved` working on a copy fails 7[thread]; an `await asyncio.sleep(0)` in the rating coroutine fails test 9; a picklable callable in test 8 fails it. `gil_disabled_build` returning `False` passes on the default build and fails only on 3.15t.
  - **The thesis for threads on the free-threaded build did not hold for this rate loop.** The plan expected a thread pool to speed up the CPU-bound batch on 3.15t (evidence G measured a bare float loop at 3.3 times). With the member's `Decimal` loop, the recorded 3.15t run has the thread pool at 0.6 times serial (warm and cold), while the process pool is at 3.4 times and the interpreter pool at 3.6 and 2.5 times. A scratch probe on 3.15t isolates the cause to `Decimal` arithmetic: four threads over a `Decimal` loop ran at 0.5 times serial with or without a copied price, a local context or an integer step, while the same loop in floats ran at 3.7 times and in integers at 3.5 times. Row 219 and the ch37 sentences "threads do on the free-threaded build" need rewording or the rating loop needs integer arithmetic; that is for U2 and the owner. The default build matches the plan (thread pool 0.9 times; process 3.9 and 3.8; interpreter 3.5 and 3.1).
  - Recorded bench (4 workers, 4 consignments of 60,000 kg, best of 3): default build, serial 0.757 s; ft build, serial 0.879 s (about 16% slower than the default run; the two earlier default runs had serial 0.699 and 0.690, so serial varies by about 0.07 s). Each build was run twice before recording and agreed within 0.2 times on every ratio except the thread pool on 3.15t (0.5 and 0.6) and the interpreter cold ratio. The files hold one run each (the third default run and the second ft run). Waits: threads and asyncio 4.0 times serial on both builds (3.9 once).
  - The bench takes `--cpu-class` on the command line; the recorded runs passed "16-thread x86-64 laptop CPU". The 3.15t sync prints a `<frozen site>` prefix warning when `.venv-ft/bin/python` is called by a relative path from a member directory; the recorded run used an absolute path and discarded stderr.
  - `.venv-ft/` is added to `.gitignore`. `uv.lock` gained only the `gil-and-performance` member.

- **Step U1b:** the ch38 member is built (2026-11-06). Differences from the plan:
  - Counts: 26 test functions and 28 cases, as planned (`test_await.py` 2/2, `test_feed.py` 5/5, `test_quoting.py` 5/5, `test_signal.py` 4/6, `test_commands.py` 4/4, `test_stowage.py` 2/2, `test_static.py` 4/4). The member is 28 passed on the default build and on 3.15t; the full suite is 1263 passed (1235 plus 28); on 3.15t the two members together are 43 passed. `uv.lock` gained only the `asyncio-patterns` member.
  - `StowagePlan.lock` is `AbstractAsyncContextManager[object] | None`, as in ch37: `None` gives a fresh `asyncio.Lock` and `contextlib.nullcontext()` runs without one. The plan's "None means no lock" would have contradicted its "defaulting to a fresh Lock". The class also has a `reservations` view (`MappingProxyType`), as in ch37, which test 20 reads to show one reservation; it has no test of its own for read-only-ness, so nothing claims it.
  - No snapshot in `AsyncSignal.publish`: the subscriber coroutines are built before any runs, so a snapshot protects nothing and the deletion row has no mutation. `publish` raises `BaseExceptionGroup` for every `BaseException` result, which is an `ExceptionGroup` when all are `Exception`s; the `BaseException` case is untested and unclaimed. `unsubscribe` called twice raises `ValueError`, unclaimed.
  - `cheapest` takes the lowest `total.amount` with `min` and has no carrier tie-break (the plan's `(total, carrier)` key); ties are not claimed.
  - Test 24's code is `list-item`, not `arg-type` (a list literal passed to `cheapest`); the substring `Coroutine[Any, Any, RateQuote]` is as planned. Test 2's message is `coroutine 'FastlineSource.quote' was never awaited`, as planned.
  - Tests 7 and 12 catch `TimeoutError` inside the coroutine, because the runner's 10 s guard raises `TimeoutError` too and `pytest.raises(TimeoutError)` outside passed when the timeout under test was removed. Tests 14 and 15 catch `ExceptionGroup` and not `except*`, because `except* LookupError` also catches a bare `LookupError`, so removing `return_exceptions=True` passed. Test 5 reads `feed.closed` inside the coroutine, because asyncio closes a dropped async generator at shutdown, which made the `aclosing` mutation pass.
  - Test 14 releases the gated subscriber only after the failing one has set `failed`, and test 15 never opens the gate, because a gate opened as the sibling fails is woken before the task group cancels it. Test 13's order within one publish rests on the loop starting tasks first in, first out (CPython); its docstring says so. Test 21's fail-without-lock needs the same order, and its docstring says so; the passing assertion does not.
  - Experiment (a) cannot be a one-line replacement: `events = handling_events(feed)` needs the loop body dedented one level. The mutation that was run did that. It fails test 5 only (`(HandlingKind.DEPARTED, False) != (HandlingKind.DEPARTED, True)`), and mypy exits 0. Experiment (b) (removing `return_exceptions=True`) fails test 14[gather] only with `LookupError: history full` escaping, and mypy reports `signal.py: error: Value of type variable "_BaseExceptionT_co" of "BaseExceptionGroup" cannot be "None"  [type-var]` (exit 1, not 0).
  - Deletion table, each in a fresh scratch copy (guard rows fail by the 10 s guard; the run then takes about 15 s against 5 s): `aclosing` removed fails 5; `try/finally` in `carrier_session` removed fails 6 and 7; `to_thread` replaced by a direct call fails 9 by the guard (`CarrierTimeoutError: AIRCO did not answer for EU`, the SDK's own 10 s patience); sequential awaits in `cheapest` fail 10 by the guard; `group.cancel()` removed fails 11 by the guard; `asyncio.timeout(within)` removed fails 12 by the guard; `return_exceptions` removed fails 14; `task_done` after success only fails 17 and 18 by the guard; the `QueueShutDown` handler removed fails 17, 18, 19 and 26 promptly (no `worker stopped`); the failure branch of `run_commands` removed fails 17 and 18; `except Exception` in place of `except asyncio.QueueShutDown` fails nothing, because `QueueShutDown` is an `Exception`, so that row is not a witness and nothing claims the narrower handler; the lock removed fails 21; `await confirm()` removed fails 20; the feed's `finally` removed fails 3, 4 and 5; closing before the first `yield` fails 4; `min` replaced by `max` fails 8; `unsubscribe` as a no-op fails 16 on both publishers; iteration reversed fails 13[gather]; the comparison publisher built on `gather` fails 15 by the guard; `FastlineSource.quote` made synchronous fails 1, 2, 8 and 25 (and mypy on the tests).
  - Static mutations (executor ran both): `RateSource.quote` made a plain `def ... -> RateQuote` fails 22 (`[] != ['return-value']`), 23 (`[] != ['unused-coroutine']`) and 24 (`[] != ['list-item']`); `def quote(...) -> RateQuote | Awaitable[RateQuote]` fails 22 (`['misc', 'no-any-return']` on the fixed form), 23 and 24 (`[[], []]`).
  - CI: the `free-threaded` job installs `3.15.2t` (the pinned patch, so it follows `.python-version`) with `uv python install`, builds `.venv-ft` from the same lockfile and runs `pytest` on the two members. It has not run on GitHub (risk).
  - The 10 s guard lives in one `Runner` fixture class in `conftest.py`; test modules import it under `TYPE_CHECKING` for the annotation.

- **Step U2:** witness results are in (2026-11-06). Differences from the plan:
  - `_plans/evidence/r18-gil-benchmark.md` holds both builds' scrubbed outputs, the other run's ratios, the spread (within about 0.4x), the commands and the label "example runs on one machine, not tests". The dated r18 note is in `_plans/spikes.md`.
  - **Row 219 is rewritten to what the example runs show**, with no cause and no generality: the Decimal rating batch ran at 1.0 times serial in a thread pool on the default build and 0.5 times on the free-threaded build, the integer-cents loop at 1.0 times and 3.9 times; process and interpreter pools ran at about 3.4 to 3.7 times warm on both builds; waits in threads or asyncio ran at 4.0 times on both builds. The plan's "threads do on the free-threaded build" is gone from the row, and ch37 prose must not repeat it for the rating loop. No cause is established for the Decimal result.
  - **The bench has a second CPU-bound section**, an integer-cents loop beside the Decimal `rating.quote` loop (commit a89c92b), so the bench reports two CPU-bound sections and the I/O waits. The integer section is what shows threads at 3.9 times on 3.15t; it is not the rating function.
  - Statuses: rows 213, 214, 218, 222, 224, 226, 228, 229 and 230 are `verified (r18)` (tests or done runs only). Rows with a `source:` token (212, 215-217, 219-221, 223, 225, 227) stay `open` until prose links the source (U5a, U5b); row 231 stays `open`. Legacy rows 17 and 18 are `adjusted (r18)`; rows 19 to 23 are `verified (r18)`.
  - `validate.py` errors after U2 are only the unlinked `source:` tokens and `run: U5a`, `run: U5b`.

Lessons carried from r11-r17, which this plan applies up front:
- **Counts.** Per-file counts are summed from the spec, and the pytest summary line wins (r13 to r17; r16's and r17's builds both added tests the deletion runs needed).
- **Members.** Named after the package, with no `[tool.*]` table (r13).
- **Shared tables** in the test module; conftest types under `TYPE_CHECKING`; classes through fixtures (r13, r14).
- **Determinism.** Lists or tuples only, never a set or dict in a failing assertion (r13 to r15, r17's dict diff). Nothing asserted on an address, a module path or an unforced interleaving.
- **Experiment filters.** `E` plus 3, 7, 9 and 11 spaces as separate alternatives, `(tests|src)/.*Error$` and `skipped` (r13 to r17).
- **Reader commands.** No repo script, and never `host_ids.py` (r15).
- **Pointers.** None that describes a stub's content, none circular (r14, r16). ch37 and ch38 point to each other by title only. ch38 must not describe "Final project" or "Working with AI and LLM tools".
- **Claim scrutiny.** Cards, READMEs, conftest and `src` docstrings get the same review as chapters (r14, r16, r17 T5): no "by a cent"-style size claim a test doesn't assert.
- **Unverified names.** No unverified chapter title (r16, r17): *Fluent Python*'s are bracketed out.
- **Draft pages.** No page carrying a do-not-link notice is cited (r17 T6 round 1).
- **Voice.** "earns its place" is banned (r15).
- **Close.** Every artifact named in "What you can do now" appears earlier in the chapter (r16).
- **Paths.** Repo-relative only in plans (r09).

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs and once in reverse file order, with the same pass count, and once on 3.15t with the same count (decision 2).
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|random|print\(|asyncio\.sleep\((?!0\))"` (with `-P`) over both members' `tests` prints nothing; `asyncio.sleep(0)` appears only where a docstring names the FIFO detail.
   - `grep -rnE "monkeypatch|mocker|unittest\.mock|\bpatch\b|\bAny\b|cast\(|print\(|Optional|random|\bglobal\b|sys\.modules|time\.sleep|asyncio\.sleep|perf_counter"` over both members' `src` prints nothing.
   - `grep -rnE "monkeypatch|mocker|unittest\.mock"` over both members' `tests` prints nothing.
   - `print(` appears in `examples/37-*/bench/gil_bench.py` only.
3. Every test name cited in rows 212-229 is defined exactly once across `examples/*/tests`.
4. Static tests assert their exit status, an exact sorted code list and no line number. Every `# type: ignore[...]` and `# noqa` names a code, and there are no unused ignores.
5. Every static test fails on its named mutation (U1a, U1b quote the line). Exit-0 tests also assert the hazard at run time (test 25's warning).
6. Deletion tables: every row, changed in a fresh scratch copy, makes the named test fail for the stated reason; the handback quotes the failing line. Executor-check rows are resolved or moved to Corrections. A row that fails only by a guard timeout is replaced by a seam that fails promptly, or recorded with its duration.
7. Every "double-books", "holds", "cancels", "closes", "refuses", "shares", "copies" or "reports" sentence names a test with a deletion row, experiment or mutation that makes it fail. Scope words name the test that covers the whole scope, or are cut.
8. ch37-38 are drafted, with one figure each, captions of 20-45 words including `Figure N.1:`, and at most 2,500 prose words each by `validate.py` (a warning below 1,900 is reported, not padded).
9. Spine and sidebar:
   - Both pass the `hands-on` spine; `grep -c "^## How it works"` is 0 in both.
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `## What you can do now` is the second-to-last H2 with as many bullets as the objectives; every backticked token in it appears earlier.
   - Each sidebar opens with a bold lead and holds a nested `>` prompt; has at most two non-quoted paragraphs; matches no `\bCheck(:| that| three| four| whether)`; is at most 120 words; names only identifiers in the chapter, its `src`, tests, bench or the standard library; and claims nothing about what assistants or models produce.
10. Thesis:
    - ch37 says the GIL is an interpreter lock, never made a read-modify-write atomic, and is absent in the free-threaded build; shows the forced double-booking and the lock that covers the read; and scopes every speed sentence to a build.
    - ch38 gives each pattern's bucket and new rule with its test, and states that an `await` is the only switch point.
11. Pointers and promises:
    - ch37 explains why threads interleave (the Singleton chapter's promise), and points to "Singleton: module, Borg, and metaclass", "Shortcut patterns: dict dispatch, function tables, and EAFP" and "asyncio and the patterns" by title, describing nothing of the last.
    - ch38 points to "The GIL and performance", "Iterator: generators and the iterator protocol", "Context managers: deterministic cleanup" (exact title checked at U5b), "Command, undo, and command queues" and "Observer" by title, and honours each one's promise (evidence M).
    - Neither re-teaches `functools.cache` under threads, builds a dict dispatch table, or describes "Final project" or "Working with AI and LLM tools".
12. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, cards, specs and SVGs, with `--stats` reviewed. "earns its place" appears nowhere.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|optimiz|synchroniz|parallelizat|utiliz)"` over prose (quotations, code and API names such as `serializes` inside a quotation excluded) prints nothing.
13. No em or en dash in any file touched in r18, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. Quotations stop before any dash on the docs page.
14. `grep -nE "Java|JavaScript|C#|C\+\+|\.NET|\bGo\b|Rust|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]"` over `_docs/37-*.md`, `_docs/38-*.md`, the new READMEs and the cards prints nothing.
15. Idiom scan: 0 ban-tier in both members' `src` and `tests`; the bench's `print()` is the recorded survivor.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs scrubbed before quoting. The bench outputs name a CPU class, never a model, and give the kernel at most as `major.minor` (prefer none).
17. Every excerpt matches its source byte for byte. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Each experiment runs in a fresh scratch copy, changes one thing and is deleted afterwards. Its filter is stated in the chapter; its output is quoted as the filter's complete output followed by mypy's; and it is run twice with identical output apart from duration.
19. Attribution:
    - Every docs quotation is exact and stops where the page's sentence stops; PEP 703 and PEP 779 are cited by title; POSA2's patterns by name only; *Fluent Python* by topic only. Every book cited is already in `bibliography.html`.
20. Claims:
    - Every factual sentence maps to a named test, a `run: U1a`/`U1b`/`U5a`/`U5b` token, the recorded benchmark file, or a fetched source URL linked in the chapter, in the prose agent's claims table.
    - Every sentence with a speed, a ratio or a race frequency names the build and says it is an example run; `grep -nE "[0-9.]+ ?(x|times)\b|faster|slower|speed-?up"` over both chapters lists only such sentences (U6 reads each).
    - `validate.py`, `--self-test` and `--claims` exit 0 with rows 212-231 resolved.
    - No outcome statistic: `grep -niE "percent of (teams|projects|apps)|most (teams|projects)|in production"` over both chapters prints nothing.
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 39 entries, and figures 00-36 are unchanged.
22. Reconciliation rows 212-231 are `verified` or `adjusted` with evidence; legacy rows 17-23 carry their r18 status.
23. Deterministic: no test depends on wall time, file paths, hash order, test order or an unforced interleaving; the two build tests' dependence on `PYTHON_GIL` is stated in their docstrings. `filterwarnings = ["error"]` stays in the root config.
24. CI `ci-ok` is green on the PR, including the `free-threaded` job under decision 2. Merge happens only after the owner's explicit approval.
25. Test counts in prose and handbacks come from a fresh pytest summary line.
26. Repo-relative paths only: `grep -rnE "/home/|/Users/"` over the files touched in r18 prints nothing.

## Risks

- **Predicted messages and counts.** Expect differences in:
  - the never-awaited warning's qualname for a method, and whether a second warning (an unraisable) appears beside it;
  - mypy's code for a blocking source passed as an argument (`[arg-type]`) against a list literal (`[list-item]`);
  - `ExceptionGroup` messages (`eg.message` against `str(eg)`);
  - experiment (b) in ch37: whether the interpreter pool accepts the lambda (evidence E).

  Tests match codes and stable substrings only.
- **Guard timeouts.** Several deletion rows fail only by a guard expiring (a blocking call on the loop, a group that never ends). A healthy run never waits, but a deletion run waits the full guard. U1b designs prompt failures where it can and records durations where it can't.
- **The free-threaded CI job** hasn't run on GitHub. If `uv python install 3.15t` or the second sync fails there, U1b records the error, and the owner chooses between fixing it in r18 and falling back to option A for CI only (local runs stay as evidence).
- **Build-dependent tests.** Tests 1 and 2 read the build and would fail under `PYTHON_GIL=1` on the free-threaded build. Stated in docstrings; CI sets nothing.
- **Process pools under pytest.** Worker functions must be importable by name in a forkserver child, so they live in `src`; a test-defined worker would fail with a pickling or import error. U1a's reverse-order run and the root run guard against import-mode surprises.
- **Benchmark numbers drift** between runs and machines. They're recorded once per build, quoted once, and labelled. A reviewer may want a test for them; criterion 20 forbids it.
- **Stale-version check.** "Python 3.13" and "3.14.x" in prose fail `validate.py` unless phrased as history (evidence M).
- **Word budgets.** ch38 carries six patterns. It shrinks first: the bucket table to five rows, then the Strategy half of its Strategy and Adapter section, then the RUF006 clause; its tests stay. ch37 shrinks first: the `forkserver` clause, then the warm/cold discussion.
- **Overlap.** ch37 must not re-teach `functools.cache` (ch18) or the EAFP race (ch31). ch38 must not re-teach sync generators (ch24), undo (ch15) or weak references in `Signal` (ch22).
- **`uv.lock` and `ci.yml` races.** U1a and U1b are sequenced; U1b owns `ci.yml`.
- **Not upstream defects for prose:** the `InterpreterPoolExecutor` lambda behaviour against its docs (evidence E) is not claimed and not filed; nothing goes upstream without the owner, through `lgtm-issue-reporting`.
