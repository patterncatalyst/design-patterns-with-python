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

In the recorded runs of `bench/lost_update_probe.py`, 300 trials of four threads each adding 1 to a shared attribute 5,000 times lost an update in none on the default build and in all 300 on the free-threaded build. A race that doesn't fire on one build still exists, so the interleaving is forced with a seam and gives the same answer on both builds. How much faster threads, processes or interpreters rate a batch depends on the build and the work, and that belongs in a benchmark script, not an assertion.

{% include excalidraw.html name="37-the-gil-and-performance" described="true" caption="Figure 37.1: Two threads reserving a slot on one sailing. Parked between reading and writing, they take the same slot on either build; a lock that covers the read and the write gives each its own." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-37-the-gil-and-performance" markdown="1">
From the top. `StowagePlan.reserve` ("pick slot, gap, store") has two arrows down. The left one reaches "no lock: nullcontext" ("two threads meet in the gap (Barrier)"), and a dashed arrow from there reaches a dashed box, "the two threads take the same SlotId" ("on either build; one reservation is left"). The right arrow reaches an accent box, "Lock over the read and the write" ("_RecordingLock: the second caller waits"), and a solid arrow goes on to "each thread gets its own SlotId" ("two reservations are stored"). Beneath the lanes, connected to neither, a bar reads "a lock that covers the read and the write keeps the pair together" ("the GIL does not join them").
</div>
</details>

The figure contrasts the two lanes: no lock, and a lock that covers both the read and the write.

## Two builds, one question

CPython now ships two builds. The [glossary](https://docs.python.org/3/glossary.html) defines the lock as "The mechanism used by the CPython interpreter to assure that only one thread executes Python bytecode at a time." The [What's New page for the 3.14 release](https://docs.python.org/3/whatsnew/3.14.html) lists "PEP 779: Free-threaded Python is officially supported" and says "The free-threaded build of Python is now supported and no longer experimental." PEP 703, "Making the Global Interpreter Lock Optional in CPython", specifies the build. Which build is running decides what a thread pool can do, and a program can ask:

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

Two functions are needed because the build and the running state can differ. The [free-threading how-to](https://docs.python.org/3/howto/free-threading-python.html) says "Free-threaded builds of CPython support optionally running with the GIL enabled at runtime using the environment variable PYTHON_GIL or the command-line option -X gil." It calls `Py_GIL_DISABLED` "the recommended mechanism for decisions related to the build configuration". The [sys documentation](https://docs.python.org/3/library/sys.html) says of `sys._is_gil_enabled`: "Return True if the GIL is enabled and False if it is disabled." With neither override set, the GIL is on exactly when the build isn't free-threaded, and `sys.version` carries "free-threading build" on that build alone.

`sysconfig.get_config_var` is typed `Any`, so returning a comparison on it from a `-> bool` function is a mypy `no-any-return` error under `--strict`. `bool(...)` fixes that.

On the default build, threads interleave because the lock changes hands. The sys documentation describes `sys.getswitchinterval()` as returning "the interpreter’s “thread switch interval” in seconds", and `sys.setswitchinterval` as setting "the ideal duration of the “timeslices” allocated to concurrently running Python threads", adding that "which thread becomes scheduled at the end of the interval is the operating system’s decision." The glossary adds "Also, the GIL is always released when doing I/O." In the recorded probe runs on 3.15.2, `sys.getswitchinterval()` reads 0.005. A thread loses the interpreter when its timeslice ends or when it waits on I/O, and you don't choose where in your code that happens.

## The GIL is not your lock

The smallest case is a counter on an object:

<!-- fmt:off -->
```python
    def bump(self) -> None:
        self.count += 1
```
<!-- fmt:on -->

`dis` shows `LOAD_ATTR`, `BINARY_OP` and `STORE_ATTR`, in that order: the read, the add and the write are separate instructions, with a gap between the read and the write. The reservation has the same shape, with a larger gap:

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

`gap` defaults to a function that does nothing; it's a test seam where a `Barrier` wait parks a thread between the read and the write. `lock` defaults to a `threading.Lock`, so the class is a Monitor Object in the vocabulary of *Pattern-Oriented Software Architecture, Volume 2*, and `with` is its Scoped Locking, which releases the lock however the block exits. Replace the lock with `nullcontext()` and park both threads at the gap:

<!-- fmt:off -->
```python
    plan = StowagePlan("SAILING-1", lock=nullcontext(), gap=barrier_gap)

    slots = two_threads(plan)

    assert slots == [SlotId(1, 1, 1), SlotId(1, 1, 1)]
    assert len(plan.reservations) == 1
```
<!-- fmt:on -->

Both threads take tier 1, and because reservations are keyed by slot, one entry survives. The GIL doesn't change the outcome on either build, because it never promised that the steps run together.

The fix is a lock that covers the read as well as the write. A `Barrier` can't park two threads inside a lock, since the second can't get in, so a recording lock in `conftest.py` counts the callers at its door and sets an event when the second arrives; the gap waits for that event. The first thread holds the lock inside the gap until the second is waiting outside. The result is tiers 1 and 2 and two reservations. A lock around only the write leaves the read unprotected and fails the same way as no lock.

For built-in structures the how-to says "It’s recommended to use the threading.Lock or other synchronization primitives instead of relying on the internal locks of built-in types, when possible." [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) forces a race of this kind for `functools.cache`, and [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) forces a read that fails between the check and the use.

## Rating a batch: threads, processes, interpreters

`quote` is a CPU-bound, pure-Python `Decimal` loop over the weight in 100 g steps. A batch can go to a thread, process or interpreter pool, and the caller picks without the rating code changing:

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

All three pools return the serial loop's answers in batch order. What differs is what the workers can see. `append_reserved` appends to the list it's given; submitted with an empty list, it leaves `CN-1` in the caller's list after a thread pool, and nothing after a process or interpreter pool, where the worker appended to a copy.

| Pool | Shares the caller's objects | Sends work by | A lambda |
| --- | --- | --- | --- |
| `ThreadPoolExecutor` | yes | reference | accepted |
| `ProcessPoolExecutor` | no, copies | pickling | `Can't pickle` |
| `InterpreterPoolExecutor` | no, copies | cross-interpreter data | `NotShareableError` |

The [concurrent.futures documentation](https://docs.python.org/3/library/concurrent.futures.html) says of a process pool that "only picklable objects can be executed and returned", and of the interpreter pool, "The worker interpreters are isolated from each other, which means each has its own runtime state and that they can’t share any mutable objects or other data." The worker functions live in the package so a worker can import them by name. What's New in the 3.14 release says "On Unix platforms other than macOS, ‘forkserver’ is now the default start method for ProcessPoolExecutor (replacing ‘fork’)."

The threading documentation says "However, the GIL limits the performance gains of threading when it comes to CPU-bound tasks, as only one thread can execute Python bytecode at a time." The interpreter pool's documentation says "Each interpreter has its own Global Interpreter Lock, which means code run with this executor has true multi-core parallelism." On the free-threaded build the glossary's entry on free threading applies to a thread pool: "A threading model where multiple threads can run Python bytecode simultaneously within the same interpreter." A thread pool is a third parallel option there, and what it does for a given loop is a measurement.

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

A second coroutine waits for `started` and logs "tracking polled". It could run once `started` is set, and doesn't until rating returns: the log reads `["rating started", "rating finished", "tracking polled"]`. An `await asyncio.sleep(0)` before `quote` moves "tracking polled" to second place. The [asyncio development guide](https://docs.python.org/3/library/asyncio-dev.html) states the rule: "Blocking (CPU-bound) code should not be called directly." It goes on: "For example, if a function performs a CPU-intensive calculation for 1 second, all concurrent asyncio Tasks and IO operations would be delayed by 1 second." The patterns that run on the loop are in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## What the benchmark measured

`bench/gil_bench.py` times the rating batch serially and through each pool, warm and cold, and four waits of 0.2 seconds serially, in threads and in asyncio. A warm pool has started its workers already; a cold row includes start-up and shut-down. A second CPU-bound section is an integer-cents loop that mirrors `quote` with `int` in place of `Decimal`. No test asserts any figure. One example run on Python 3.15.2's default build, with 4 workers and the best of 3 timings:

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

And one on the free-threading build of the same version, with the same worker count:

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

The ratio is serial time over pool time, so 3.6x means 3.6 times as fast. A second run of each build agreed within about 0.4 on every ratio, and your figures will differ. In these runs:

- **Default build, thread pool:** 1.0 times serial on both CPU-bound loops, as the threading documentation predicts.
- **Free-threaded build, thread pool:** 3.9 times serial on the integer loop and 0.5 times on the `Decimal` loop, nearly twice as long as serial (1.648 against 0.878 seconds). The how-to says "While not all software will benefit from this automatically, programs designed with threading in mind will run faster on multi-core hardware." Two loops on one build moved in opposite directions, so measure your loop.
- **Process and interpreter pools:** about 3.4 to 3.7 times serial, warm, on both builds. The cold interpreter pool on the short integer loop ran at 1.3 times on the default build and 0.8 times on the free-threaded one, where start-up and shut-down weigh against 0.132 or 0.159 seconds of work.
- **Waits:** 4.0 times serial in threads and in asyncio on both builds.

The serial rows are about 1.2 times longer on the free-threaded build. The how-to says "On the pyperformance benchmark suite, the average overhead ranges from about 1% on macOS aarch64 to 8% on x86-64 Linux systems." That's an average over a suite, and these are single runs of small loops.

## When threads are the wrong tool

| Work | Default build | Free-threaded build |
| --- | --- | --- |
| Waits (I/O) | threads or asyncio | threads or asyncio |
| CPU-bound pure Python | process or interpreter pool | process or interpreter pool; measure a thread pool, with every shared write behind a lock |

> **🤖 Explore with your agent**
>
> "Rate the batch through `rate_batch` with a `PoolFactory` from `POOLS`, with no shared mutable state. Where state must be shared, as in `StowagePlan.reserve`, hold one lock across the read and the write, and add a test that parks two threads in the gap with a `threading.Barrier`. Report timings from `bench/gil_bench.py` on both builds, not from a test."
>
> If a test asserts a duration, ask which build and machine it was written for.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/37-the-gil-and-performance
uv run pytest -q
uv run mypy --strict src tests
uv run python bench/gil_bench.py --cpu-class "16-thread x86-64 CPU"
```

All 15 cases pass, mypy is clean, and the last command prints the benchmark report. `bench/lost_update_probe.py` takes `--cpu-class` too, and its recorded outputs are `bench/lost_update_probe.out.txt` and `bench/lost_update_probe.ft.out.txt`. To run on the free-threaded build, install it and build a second environment from the same lockfile, from the repository root:

```bash
uv python install 3.15.2t
UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages
.venv-ft/bin/python -m pytest examples/37-the-gil-and-performance
.venv-ft/bin/python examples/37-the-gil-and-performance/bench/lost_update_probe.py --cpu-class "16-thread x86-64 CPU"
```

The same 15 cases pass there. Run each experiment in a scratch copy of the repository with its own `.venv`, and check that `gil_and_performance.__file__` points into the copy:

- **Read outside the lock.** In `src/gil_and_performance/stowage.py`, move the line that picks the slot above `with self._lock:`. One case fails: both threads read tier 1 before either wrote, and the lock serialised only the writes. mypy exits 0; only the forced interleaving sees it.
- **Map a lambda.** Restore the file and, in `rate_batch`, map `lambda consignment: quote(consignment)` in place of `quote`. The process pool fails with `PicklingError: Can't pickle local object` and the interpreter pool with `NotShareableError`; the thread pool passes. mypy exits 0, since a lambda is a valid callable for `map`.

## What you can do now

- Say what the GIL guarantees and tell the build: `gil_disabled_build` and `gil_enabled` answer on both builds.
- Force a lost update and fix it: `StowagePlan.reserve` takes the same slot twice without a lock, and gives each thread its own with a lock over the read and the write.
- Choose a pool: `rate_batch` takes a factory from `POOLS`; a thread pool shares the caller's objects, and the other two copy them.
- Explain the stalled loop: a coroutine that never awaits holds the loop until it returns.
- Read a benchmark: `bench/gil_bench.py` and its two recorded outputs give ratios for one build and one machine, and no test asserts one.

## For deeper coverage

The Python documentation covers each piece: the [glossary](https://docs.python.org/3/glossary.html) entries for the global interpreter lock and free threading, the [threading](https://docs.python.org/3/library/threading.html) page's "GIL and performance considerations", the [sys](https://docs.python.org/3/library/sys.html) page, the [free-threading how-to](https://docs.python.org/3/howto/free-threading-python.html), the [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) page, [What's New in the 3.14 release](https://docs.python.org/3/whatsnew/3.14.html) and the [asyncio development guide](https://docs.python.org/3/library/asyncio-dev.html). [PEP 703](https://peps.python.org/pep-0703/), "Making the Global Interpreter Lock Optional in CPython", and [PEP 779](https://peps.python.org/pep-0779/) set out the build and its supported status. Douglas Schmidt, Michael Stal, Hans Rohnert and Frank Buschmann's *Pattern-Oriented Software Architecture, Volume 2* catalogues Monitor Object and Scoped Locking. Luciano Ramalho's *Fluent Python*, second edition, carries the asyncio material. The loop's side is in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}). The books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
