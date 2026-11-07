---
title: "The GIL and performance"
order: 37
layout: tutorial
sectionid: docs
part: "concurrency"
description: "What the global interpreter lock guarantees and what it leaves to your own lock, how to tell the default build from the free-threaded one, which pool suits CPU-bound rating, and why a benchmark stays out of the tests."
---

## Learning objectives

By the end of this chapter you can:

- Say what the GIL guarantees and what it doesn't, and tell which CPython build is running.
- Force a lost update between two threads and fix it with a lock that covers the read.
- Choose between thread, process and interpreter pools for CPU-bound rating, knowing what each shares and copies.
- Explain why a CPU-bound coroutine stalls the event loop.
- Read a benchmark as a measurement of one build on one machine, and keep it out of the tests.

## Why this matters

Two bookings reach the same sailing from two threads, and each reserves a slot. The global interpreter lock sounds like the answer, because only one thread runs bytecode at a time. It protects the interpreter's own structures, and a reservation that reads a count and then writes a slot is several steps of your code.

In one example run, 300 trials of four threads each adding 1 to a shared attribute 5,000 times lost an update in none on the default build and in all 300 on the free-threaded build. A race that doesn't fire on one build still exists, so the example forces the interleaving with a seam, and its tests give the same answer on both builds. How much faster threads, processes or interpreters rate a batch depends on the build and the work, and that lives in a benchmark script, not an assertion.

{% include excalidraw.html name="37-the-gil-and-performance" caption="Figure 37.1: Two threads reserving a slot on one sailing. Parked between reading and writing, they take the same slot on either build; a lock that covers the read and the write gives each its own." %}

Read the figure from the top. `StowagePlan.reserve` ("pick slot, gap, store") has two arrows down. The left one reaches "no lock: nullcontext" ("two threads meet in the gap (Barrier)"), and a dashed arrow from there reaches a dashed box, "the two threads take the same SlotId" ("on either build; one reservation is left"). The right arrow reaches an accent box, "Lock over the read and the write" ("_RecordingLock: the second caller waits"), and a solid arrow goes on to "each thread gets its own SlotId" ("two reservations are stored"). Both lanes end at a bar: "a lock that covers the read and the write keeps the pair together" ("the GIL does not join them").

## Two builds, one question

CPython now ships two builds. The glossary defines the lock as "The mechanism used by the CPython interpreter to assure that only one thread executes Python bytecode at a time." The [What's New page for the 3.14 release](https://docs.python.org/3/whatsnew/3.14.html) lists "PEP 779: Free-threaded Python is officially supported" and says "The free-threaded build of Python is now supported and no longer experimental." The build itself is specified in PEP 703, "Making the Global Interpreter Lock Optional in CPython". Which build is running decides what a thread pool can do, and a program can ask:

<!-- fmt:off -->
```python
def gil_disabled_build() -> bool:
    """True when this interpreter is a free-threaded build."""
    # The stub for get_config_var promises no type; bool() gives mypy a bool to return.
    return bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def gil_enabled() -> bool:
    """True when the interpreter is running with the GIL on, whichever build it is."""
    return sys._is_gil_enabled()
```
<!-- fmt:on -->

Two functions are needed because the build and the running state can differ. The [free-threading how-to](https://docs.python.org/3/howto/free-threading-python.html) says "Free-threaded builds of CPython support optionally running with the GIL enabled at runtime using the environment variable PYTHON_GIL or the command-line option -X gil." On the how-to's account, the `Py_GIL_DISABLED` variable "is the recommended mechanism for decisions related to the build configuration", which is what `gil_disabled_build` reads. The [sys documentation](https://docs.python.org/3/library/sys.html) says of `sys._is_gil_enabled`: "Return True if the GIL is enabled and False if it is disabled." With neither override set, the two answers are opposites: `test_the_build_flag_and_the_runtime_gil_state_agree` asserts that the GIL is on exactly when the build isn't free-threaded. `test_sys_version_names_the_free_threading_build_only_on_that_build` checks that `sys.version` carries "free-threading build" on that build alone, the banner the how-to names. Both assume `PYTHON_GIL` and `-X gil` are unset.

`sysconfig.get_config_var` is typed `Any`, so returning a comparison on it from a `-> bool` function is a mypy `no-any-return` error, and `bool(...)` is what the module does about it. `test_mypy_types_the_build_flag_as_any` runs the unwrapped form and `build.py` through `--strict` mypy and finds the code in only the first.

On the default build, threads interleave because the lock changes hands. The sys documentation describes `sys.getswitchinterval()` as returning "the interpreter’s “thread switch interval” in seconds", and `sys.setswitchinterval` as setting "the ideal duration of the “timeslices” allocated to concurrently running Python threads". It adds that "which thread becomes scheduled at the end of the interval is the operating system’s decision." The glossary adds "Also, the GIL is always released when doing I/O." A run on 3.15.2 reads 0.005 from `sys.getswitchinterval()`. A thread loses the interpreter when its timeslice ends or when it waits on I/O, and where in your code that happens isn't yours to choose.

## The GIL is not your lock

The smallest case is a counter on an object. This test-only method exists so that its bytecode can be read:

<!-- fmt:off -->
```python
    def bump(self) -> None:
        self.count += 1
```
<!-- fmt:on -->

`test_an_attribute_increment_is_a_separate_load_add_and_store` disassembles it with `dis` and finds `LOAD_ATTR`, `BINARY_OP` and `STORE_ATTR`, in that order. The statement is three instructions with a gap between the read and the write. The reservation has the same shape, with a larger gap:

<!-- fmt:off -->
```python
    def reserve(self, consignment_id: ConsignmentId) -> SlotId:
        with self._lock:
            slot = SlotId(1, 1, len(self._reservations) + 1)
            self._gap()
            self._reservations[slot] = consignment_id
        return slot
```
<!-- fmt:on -->

The next free tier is read, the gap runs, and the slot is stored. `gap` defaults to a function that does nothing and is a test seam: a test passes a `Barrier` wait there to park a thread between the read and the write. `lock` defaults to a `threading.Lock`, so the class is a Monitor Object in the vocabulary of *Pattern-Oriented Software Architecture, Volume 2*, and `with` is its Scoped Locking, which releases the lock however the block exits. Replace the lock with `nullcontext()` and park both threads at the gap:

<!-- fmt:off -->
```python
    plan = StowagePlan("SAILING-1", lock=nullcontext(), gap=barrier_gap)

    slots = two_threads(plan)

    assert slots == [SlotId(1, 1, 1), SlotId(1, 1, 1)]
    assert len(plan.reservations) == 1
```
<!-- fmt:on -->

Both threads take tier 1, and because reservations are keyed by slot, one entry survives (`test_two_threads_parked_between_read_and_write_take_the_same_slot`). The GIL doesn't change the outcome on either build, because it never promised that the steps run together.

The fix is a lock that covers the read as well as the write. A `Barrier` can't park two threads inside a lock, since the second thread can't get in, so the test uses a recording lock from `conftest.py`. It counts the callers that reach its door and sets an event when the second one arrives, and the gap waits for that event. The first thread therefore holds the lock inside the gap until the second is waiting outside it. The result is tiers 1 and 2, two reservations, and a recorded second caller (`test_a_lock_across_read_and_write_gives_each_thread_its_own_slot`). A lock around only the write leaves the read where the left lane has it, and the first experiment below shows that failure.

For built-in structures the how-to says "It’s recommended to use the threading.Lock or other synchronization primitives instead of relying on the internal locks of built-in types, when possible." [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) forces a race of this kind for `functools.cache`. A read that fails between the check and the use has its own forced test in [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}).

## Rating a batch: threads, processes, interpreters

`quote` is a CPU-bound, pure-Python `Decimal` loop over the weight in 100 g steps. A batch of consignments can go to a thread, process or interpreter pool, and the caller picks without the rating code changing:

<!-- fmt:off -->
```python
# A class cannot stand in here: mypy rejects calling type[Executor] with max_workers.
type PoolFactory = Callable[[int], Executor]

POOLS: frozendict[str, PoolFactory] = frozendict(
    thread=ThreadPoolExecutor,
    process=ProcessPoolExecutor,
    interpreter=InterpreterPoolExecutor,
)


def rate_batch(
    batch: Iterable[Consignment], /, *, pool: PoolFactory, workers: int = 4
) -> list[RateQuote]:
    """Rate every consignment in the pool, in batch order."""
    with pool(workers) as executor:
        return list(executor.map(quote, batch))
```
<!-- fmt:on -->

All three pools return the answers of the serial loop, in batch order, for a batch of eight consignments (`test_every_pool_rates_the_batch_as_the_serial_loop_does`, three cases). What differs is what the workers can see. `append_reserved` appends to the list it is given and returns the new length, and the test submits it to a pool of one worker with an empty list. After a thread pool, the caller's list holds `CN-1`. After a process pool or an interpreter pool it is empty, because the worker appended to a copy (`test_threads_share_the_argument_and_processes_and_interpreters_copy_it`, three cases). The [concurrent.futures documentation](https://docs.python.org/3/library/concurrent.futures.html) says of a process pool that "only picklable objects can be executed and returned." Of the interpreter pool it says "The worker interpreters are isolated from each other, which means each has its own runtime state and that they can’t share any mutable objects or other data."

A lambda can't be pickled, so a process pool refuses one with `Can't pickle` (`test_a_process_pool_cannot_send_a_lambda`). The worker functions, `quote` and `append_reserved`, live in the package so that a worker can import them by name. The default start method for a process pool on Linux is `forkserver`: What's New in the 3.14 release says "On Unix platforms other than macOS, ‘forkserver’ is now the default start method for ProcessPoolExecutor (replacing ‘fork’)."

The threading documentation says "However, the GIL limits the performance gains of threading when it comes to CPU-bound tasks, as only one thread can execute Python bytecode at a time." The interpreter pool says "Each interpreter has its own Global Interpreter Lock, which means code run with this executor has true multi-core parallelism." On the free-threaded build the glossary's entry on free threading applies to a thread pool: "A threading model where multiple threads can run Python bytecode simultaneously within the same interpreter." A thread pool is a third parallel option there, and what it does for a given loop is a measurement.

## Why asyncio doesn't help here

A coroutine hands the event loop back at an `await`. This one has none:

<!-- fmt:off -->
```python
    async def rating() -> None:
        log.append("rating started")
        started.set()
        quote(consignment)  # CPU-bound and never awaits, so nothing else can run
        log.append("rating finished")
```
<!-- fmt:on -->

A second coroutine waits for `started` and then logs "tracking polled". Once `started` is set, tracking could run, and it doesn't until rating returns: the log reads `["rating started", "rating finished", "tracking polled"]` (`test_a_coroutine_that_never_awaits_holds_the_loop_until_it_returns`). Adding an `await asyncio.sleep(0)` before the `quote` call makes the test fail. The [asyncio development guide](https://docs.python.org/3/library/asyncio-dev.html) states the rule: "Blocking (CPU-bound) code should not be called directly." Its example is that "For example, if a function performs a CPU-intensive calculation for 1 second, all concurrent asyncio Tasks and IO operations would be delayed by 1 second." The patterns that run on the loop are in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## What the benchmark measured

`bench/gil_bench.py` times the rating batch serially and through each pool, warm and cold, and four waits of 0.2 seconds serially, in threads and in asyncio. A warm pool has started its workers already, and a cold row includes the pool's start-up and shut-down. A second CPU-bound section is an integer-cents loop that mirrors `quote` with `int` in place of `Decimal`. No test asserts any figure. Here is one example run on Python 3.15.2's default build, with 4 workers and the best of 3 timings:

```text
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

And one example run on the free-threading build of the same version, with the same worker count:

```text
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

The ratio is serial time over pool time, so 3.6x means 3.6 times as fast. A second run of each build agreed with these within about 0.4 on every ratio, and your figures will differ. In these runs:

- On the default build the thread pool ran at 1.0 times serial on both CPU-bound loops, as the threading documentation predicts.
- On the free-threaded build the integer loop ran at 3.9 times serial in the thread pool, and the `Decimal` loop at 0.5 times, which is twice as long as serial. No cause is claimed for the second result. The how-to says "While not all software will benefit from this automatically, programs designed with threading in mind will run faster on multi-core hardware." Two loops on one build moved in opposite directions, so measure your loop.
- Process and interpreter pools ran at about 3.4 to 3.7 times serial, warm, on both builds. The cold interpreter pool on the short integer loop ran at 1.3 times on the default build and 0.8 times on the free-threaded one, where start-up and shut-down weigh against 0.132 or 0.159 seconds of work.
- Four waits ran at 4.0 times serial in threads and in asyncio on both builds.

The serial rows are about 1.2 times longer on the free-threaded build in these two runs. The how-to says "On the pyperformance benchmark suite, the average overhead ranges from about 1% on macOS aarch64 to 8% on x86-64 Linux systems." That is an average over a suite, and these are single runs of small loops.

## When threads are the wrong tool

Pick by the work and the build. Waits suit threads or asyncio on either build, as the last rows show. CPU-bound pure Python wants a process or interpreter pool on the default build. On the free-threaded build a thread pool is worth measuring for it, with every shared write behind a lock.

<blockquote class="ai-sidebar" markdown="1">

**Parallel code that assumes the GIL.** A request to "speed up rating with threads" names neither the build nor what the threads share, and a shared write that relies on one thread running at a time can lose updates on the free-threaded build. Paste a prompt that makes the sharing explicit:

> Rate the batch through `rate_batch` with a `PoolFactory` from `POOLS`, passing consignments in and returning quotes, with no shared mutable state. Where state must be shared, as in `StowagePlan.reserve`, hold one lock across the read and the write, and add a test that parks two threads in the gap with a `threading.Barrier`. Report timings from `bench/gil_bench.py` on both builds, not from a test.

If a test asserts a duration, ask which build and machine it was written for.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then, from `examples/37-the-gil-and-performance`, `uv run pytest -v` runs 11 test functions as 15 cases, and `uv run mypy --strict src tests` checks the example:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 15 items

tests/test_build.py::test_the_build_flag_and_the_runtime_gil_state_agree PASSED [  6%]
tests/test_build.py::test_sys_version_names_the_free_threading_build_only_on_that_build PASSED [ 13%]
tests/test_loop.py::test_a_coroutine_that_never_awaits_holds_the_loop_until_it_returns PASSED [ 20%]
tests/test_pools.py::test_every_pool_rates_the_batch_as_the_serial_loop_does[thread] PASSED [ 26%]
tests/test_pools.py::test_every_pool_rates_the_batch_as_the_serial_loop_does[process] PASSED [ 33%]
tests/test_pools.py::test_every_pool_rates_the_batch_as_the_serial_loop_does[interpreter] PASSED [ 40%]
tests/test_pools.py::test_threads_share_the_argument_and_processes_and_interpreters_copy_it[thread-caller_list0] PASSED [ 46%]
tests/test_pools.py::test_threads_share_the_argument_and_processes_and_interpreters_copy_it[process-caller_list1] PASSED [ 53%]
tests/test_pools.py::test_threads_share_the_argument_and_processes_and_interpreters_copy_it[interpreter-caller_list2] PASSED [ 60%]
tests/test_pools.py::test_a_process_pool_cannot_send_a_lambda PASSED     [ 66%]
tests/test_static.py::test_mypy_types_the_build_flag_as_any PASSED       [ 73%]
tests/test_stowage.py::test_two_threads_parked_between_read_and_write_take_the_same_slot PASSED [ 80%]
tests/test_stowage.py::test_an_attribute_increment_is_a_separate_load_add_and_store PASSED [ 86%]
tests/test_stowage.py::test_a_lock_across_read_and_write_gives_each_thread_its_own_slot PASSED [ 93%]
tests/test_stowage.py::test_the_reservations_view_refuses_assignment PASSED [100%]

============================== 15 passed in 1.02s ==============================
Success: no issues found in 12 source files
```

`uv run python bench/gil_bench.py` prints the benchmark report. To run the tests on the free-threaded build, install it and build a second environment from the same lockfile, from the repository root:

```bash
uv python install 3.15t
UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15t --locked --all-packages
.venv-ft/bin/python -m pytest examples/37-the-gil-and-performance
```

The same 15 cases pass there. Each experiment below runs in a scratch copy of the repository: delete the copy's `.venv`, run `uv sync --locked --all-packages` from its root and check that `gil_and_performance.__file__` points into the copy.

The first moves the read out of the lock. In `src/gil_and_performance/stowage.py`, move the line that picks the slot above `with self._lock:`. Then, from the example directory:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'
uv run mypy --strict src tests
```

```text
E       assert [SlotId(bay=1...ow=1, tier=1)] == [SlotId(bay=1...ow=1, tier=2)]
E         At index 1 diff: SlotId(bay=1, row=1, tier=1) != SlotId(bay=1, row=1, tier=2)
E         Use -v to get more diff
tests/test_stowage.py:53: AssertionError
FAILED tests/test_stowage.py::test_a_lock_across_read_and_write_gives_each_thread_its_own_slot
1 failed, 14 passed in 1.06s
Success: no issues found in 12 source files
```

One test fails: both threads read tier 1 before either wrote, and the lock then serialised only the writes. The parked-pair test still passes, since it never relied on the lock. mypy exits 0 because the change is type-correct, and only the forced interleaving sees it.

The second restores that file and, in `rate_batch` in `src/gil_and_performance/pools.py`, maps `lambda consignment: quote(consignment)` in place of `quote`. The filter is narrower, and a `sed` masks the object addresses:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|E +(_pickle|concurrent)\.|[0-9]+ (passed|failed))' | sed -E 's/0x[0-9a-f]+/0x…/g'
uv run mypy --strict src tests
```

```text
E       _pickle.PicklingError: Can't pickle local object <function rate_batch.<locals>.<lambda> at 0x…>
E       concurrent.interpreters.NotShareableError: (Queue(1), <function rate_batch.<locals>.<lambda> at 0x…>, (Consignment(id='CN-1', zone='EU', weight_kg=Decimal('7.3')),), {}) does not support cross-interpreter data
FAILED tests/test_pools.py::test_every_pool_rates_the_batch_as_the_serial_loop_does[process]
FAILED tests/test_pools.py::test_every_pool_rates_the_batch_as_the_serial_loop_does[interpreter]
2 failed, 13 passed in 1.01s
Success: no issues found in 12 source files
```

Two cases fail, the process pool with a pickling error and the interpreter pool, which refuses this lambda with `NotShareableError`. The thread case passes, because a thread pool sends nothing across a boundary. mypy exits 0, since a lambda is a valid callable for `map`. Both experiments printed the same output on a second run, apart from the duration.

## What you can do now

- Say what the GIL guarantees and tell the build: `gil_disabled_build` and `gil_enabled` answer the second, and `test_the_build_flag_and_the_runtime_gil_state_agree` and `test_sys_version_names_the_free_threading_build_only_on_that_build` check them on both builds.
- Force a lost update and fix it: `StowagePlan.reserve` takes the same slot twice in `test_two_threads_parked_between_read_and_write_take_the_same_slot` and gives each thread its own in `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot`, and the first experiment shows the read outside the lock failing.
- Choose a pool: `rate_batch` takes a factory from `POOLS`, and `test_threads_share_the_argument_and_processes_and_interpreters_copy_it` shows what a thread pool shares and the other two copy.
- Explain the stalled loop: `test_a_coroutine_that_never_awaits_holds_the_loop_until_it_returns` shows tracking waiting until rating returns.
- Read a benchmark: `bench/gil_bench.py` and its two recorded outputs give ratios for one build and one machine, and no test asserts one.

## For deeper coverage

The Python documentation covers each piece: the [glossary](https://docs.python.org/3/glossary.html) entries for the global interpreter lock and free threading, the [threading](https://docs.python.org/3/library/threading.html) page's "GIL and performance considerations", the [sys](https://docs.python.org/3/library/sys.html) page, the [free-threading how-to](https://docs.python.org/3/howto/free-threading-python.html), the [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) page, [What's New in the 3.14 release](https://docs.python.org/3/whatsnew/3.14.html) and the [asyncio development guide](https://docs.python.org/3/library/asyncio-dev.html). [PEP 703](https://peps.python.org/pep-0703/), "Making the Global Interpreter Lock Optional in CPython", and [PEP 779](https://peps.python.org/pep-0779/) set out the build and its supported status. Douglas Schmidt, Michael Stal, Hans Rohnert and Frank Buschmann's *Pattern-Oriented Software Architecture, Volume 2* catalogues Monitor Object and Scoped Locking. Luciano Ramalho's *Fluent Python*, second edition, carries the asyncio material. The loop's side is in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}). The books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
