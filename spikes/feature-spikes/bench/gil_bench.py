"""GIL benchmark: CPU-bound vs I/O-bound work across serial, threads, processes and asyncio.

Run from the member directory: ``uv run python bench/gil_bench.py``. Standard library only.
Prints the interpreter version and GIL state; nothing that identifies the machine.
"""

import asyncio
import platform
import sys
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

WORKERS = 4
CPU_ITERATIONS = 3_000_000
IO_WAIT_SECONDS = 0.2
REPEATS = 3


def rate_loop(iterations: int) -> float:
    """Pure-Python rate computation: a tight loop that never releases the GIL on its own."""
    total = 0.0
    for i in range(iterations):
        total += (i % 97) * 0.0125 + (i % 13) * 0.5
    return total


def blocking_lookup(seconds: float) -> None:
    time.sleep(seconds)


async def async_lookup(seconds: float) -> None:
    await asyncio.sleep(seconds)


def best_of(run: Callable[[], object]) -> float:
    best = float("inf")
    for _ in range(REPEATS):
        start = time.perf_counter()
        run()
        best = min(best, time.perf_counter() - start)
    return best


def cpu_serial() -> None:
    for _ in range(WORKERS):
        rate_loop(CPU_ITERATIONS)


def cpu_threads() -> None:
    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(rate_loop, [CPU_ITERATIONS] * WORKERS))


def io_serial() -> None:
    for _ in range(WORKERS):
        blocking_lookup(IO_WAIT_SECONDS)


def io_threads() -> None:
    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(blocking_lookup, [IO_WAIT_SECONDS] * WORKERS))


def io_asyncio() -> None:
    async def main() -> None:
        async with asyncio.TaskGroup() as group:
            for _ in range(WORKERS):
                group.create_task(async_lookup(IO_WAIT_SECONDS))

    asyncio.run(main())


def main() -> None:
    print("GIL benchmark, 2026-11-03")
    print(f"python {platform.python_version()}  gil_enabled={sys._is_gil_enabled()}")
    print(f"{WORKERS} workers, best of {REPEATS}, pool start-up excluded for processes")
    print()

    with ProcessPoolExecutor(WORKERS) as pool:
        list(pool.map(rate_loop, [1] * WORKERS))  # warm the workers before timing

        def cpu_processes() -> None:
            list(pool.map(rate_loop, [CPU_ITERATIONS] * WORKERS))

        cpu = {
            "serial": best_of(cpu_serial),
            "4 threads": best_of(cpu_threads),
            "4 processes": best_of(cpu_processes),
        }
    io = {
        "serial": best_of(io_serial),
        "4 threads": best_of(io_threads),
        "asyncio (4 tasks)": best_of(io_asyncio),
    }

    for title, results in (
        (f"CPU-bound: {WORKERS} x rate_loop({CPU_ITERATIONS:,})", cpu),
        (f"I/O-bound: {WORKERS} x {IO_WAIT_SECONDS}s wait", io),
    ):
        baseline = results["serial"]
        print(title)
        print(f"  {'strategy':<20}{'seconds':>10}{'vs serial':>12}")
        for name, seconds in results.items():
            print(f"  {name:<20}{seconds:>10.3f}{baseline / seconds:>11.2f}x")
        print()


if __name__ == "__main__":
    main()
