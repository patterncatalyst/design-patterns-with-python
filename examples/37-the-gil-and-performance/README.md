# The GIL and performance

A slot reservation shared by two threads, and a batch of consignments rated through thread,
process and interpreter pools. Weights, zones and prices are illustrative.

## What it witnesses

`build.py` reports which CPython build is running (`gil_disabled_build`) and whether its GIL is
on (`gil_enabled`). The tests hold on both the default and the free-threaded build.

`stowage.py` holds `StowagePlan`. `reserve` picks the next `SlotId`, calls a `gap` hook and stores
the reservation, all under a lock. The hook is a test seam: a `threading.Barrier` parks two threads
between the read and the write. Without a lock, both take the same slot and one reservation
survives. With a lock held across the read and the write, each thread takes its own slot. The
`reservations` view is read-only.

`pools.py` holds `POOLS`, a read-only mapping of `thread`, `process` and `interpreter` pool
factories, and `rate_batch`, which rates a batch through any of them. `append_reserved` is the
sharing witness: a thread pool appends to the caller's list, and a process or interpreter pool
appends to a copy. A process pool refuses a lambda. The worker functions live in the package
because a process or interpreter worker imports them by name.

`rating.py` holds `quote`, a pure-Python `Decimal` loop over the weight in 100 g steps.

A coroutine that never awaits holds the event loop until it returns.

## The benchmark

`bench/gil_bench.py` times the rating batch serially and through each pool, warm and cold, then
repeats the batch with an integer-cents loop that mirrors `quote` with `int` in place of `Decimal`,
and times four waits serially, in threads and in asyncio. It is a measurement, not a test, and no
test asserts any of its figures. The recorded outputs are `bench/gil_bench.out.txt` (default build)
and `bench/gil_bench.ft.out.txt` (free-threaded build). They name the interpreter, the build and a
class of machine, never a model. Your figures will differ.

`bench/lost_update_probe.py` runs 300 trials of four threads, each adding 1 to a shared attribute
5,000 times with no lock, and counts the trials that lost an update. The recorded outputs are
`bench/lost_update_probe.out.txt` (default build) and `bench/lost_update_probe.ft.out.txt`
(free-threaded build). No test asserts a count, and the counts depend on the build and the
scheduler.

## Layout

- `src/gil_and_performance/domain.py`: `ConsignmentId`, `Consignment`, `Money`, `RateQuote`,
  `SlotId`.
- `src/gil_and_performance/build.py`: `gil_disabled_build`, `gil_enabled`.
- `src/gil_and_performance/stowage.py`: `StowagePlan`.
- `src/gil_and_performance/rating.py`: `quote`.
- `src/gil_and_performance/pools.py`: `PoolFactory`, `POOLS`, `rate_batch`, `append_reserved`.
- `tests/conftest.py`: a lock that records its callers, a barrier gap, and a helper that reserves
  from two threads.
- `bench/gil_bench.py`: the benchmark and its recorded outputs.
- `bench/lost_update_probe.py`: the lost-update probe and its recorded outputs.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
uv run python bench/gil_bench.py --cpu-class "16-thread x86-64 CPU"
uv run python bench/lost_update_probe.py --cpu-class "16-thread x86-64 CPU"
```

To run the tests on the free-threaded build, from the repository root:

```bash
uv python install 3.15.2t
UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages
.venv-ft/bin/python -m pytest examples/37-the-gil-and-performance
.venv-ft/bin/python examples/37-the-gil-and-performance/bench/lost_update_probe.py --cpu-class "16-thread x86-64 CPU"
```

## What the tests verify

`tests/test_build.py` (these two read the build, so `PYTHON_GIL` and `-X gil` must be unset)

- `test_the_build_flag_and_the_runtime_gil_state_agree`
- `test_sys_version_names_the_free_threading_build_only_on_that_build`

`tests/test_stowage.py`

- `test_two_threads_parked_between_read_and_write_take_the_same_slot`: both take
  `SlotId(1, 1, 1)` and one reservation remains.
- `test_an_attribute_increment_is_a_separate_load_add_and_store`: read from the bytecode.
- `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot`: tiers 1 and 2, two
  reservations.
- `test_the_reservations_view_refuses_assignment`

`tests/test_pools.py`

- `test_every_pool_rates_the_batch_as_the_serial_loop_does`: thread, process and interpreter.
- `test_threads_share_the_argument_and_processes_and_interpreters_copy_it`: the same three.
- `test_a_process_pool_cannot_send_a_lambda`

`tests/test_loop.py`

- `test_a_coroutine_that_never_awaits_holds_the_loop_until_it_returns`

`tests/test_static.py`

- `test_mypy_types_the_build_flag_as_any`: returning the sysconfig flag unwrapped is a
  `no-any-return` error, and `build.py` is clean.

The tests use no mocks and no patching. The two stowage races are forced by a barrier and a
recording lock, the loop test by an `asyncio.Event`, and the waits sit under a ten-second guard that
a healthy run never reaches.
