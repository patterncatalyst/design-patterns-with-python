"""Time CPU-bound rating and I/O-bound waits on the running interpreter.

This is a measurement of one build on one machine, not a test. Run it with
``uv run python bench/gil_bench.py --cpu-class "<a class, never a model>"`` and scrub the
output before recording it. The report names the Python version, the build, whether the GIL is
on, the worker count and the date, and nothing that identifies the host.
"""

import argparse
import asyncio
import sys
import time
from collections.abc import Callable
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import date
from decimal import Decimal

from gil_and_performance.build import gil_disabled_build, gil_enabled
from gil_and_performance.domain import Consignment, ConsignmentId
from gil_and_performance.pools import POOLS
from gil_and_performance.rating import quote

WORKERS = 4
REPEATS = 3
BATCH = tuple(
    Consignment(ConsignmentId(f"CN-{n}"), "EU" if n % 2 else "ASIA", Decimal(60000))
    for n in range(WORKERS)
)
WAITS = 4
WAIT_SECONDS = 0.2


def best_of(run: Callable[[], object]) -> float:
    times: list[float] = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        run()
        times.append(time.perf_counter() - start)
    return min(times)


def serial() -> object:
    return [quote(consignment) for consignment in BATCH]


def warm(factory: Callable[[int], Executor]) -> float:
    """Time the batch on a pool that has already started its workers."""
    with factory(WORKERS) as executor:
        list(executor.map(quote, BATCH))
        return best_of(lambda: list(executor.map(quote, BATCH)))


def cold(factory: Callable[[int], Executor]) -> float:
    """Time the batch including the pool's start-up and shut-down."""

    def run() -> object:
        with factory(WORKERS) as executor:
            return list(executor.map(quote, BATCH))

    return best_of(run)


def io_serial() -> None:
    for _ in range(WAITS):
        time.sleep(WAIT_SECONDS)


def io_threads() -> None:
    with ThreadPoolExecutor(WAITS) as executor:
        list(executor.map(time.sleep, [WAIT_SECONDS] * WAITS))


def io_asyncio() -> None:
    async def main() -> None:
        await asyncio.gather(*(asyncio.sleep(WAIT_SECONDS) for _ in range(WAITS)))

    asyncio.run(main())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu-class", default="unspecified", help="a class, never a model")
    args = parser.parse_args()

    build = "free-threading build" if gil_disabled_build() else "default build"
    version = sys.version.split()[0]
    print(f"Python {version}, {build}, GIL enabled: {gil_enabled()}")
    print(f"workers: {WORKERS}, batch: {len(BATCH)} consignments, best of {REPEATS}")
    print(f"date: {date.today().isoformat()}, machine: {args.cpu_class}")
    print()
    base = best_of(serial)
    print(f"{'serial':<26}{base:6.3f} s")
    for name, factory in POOLS.items():
        warm_s, cold_s = warm(factory), cold(factory)
        print(
            f"{name + ' pool':<26}warm {warm_s:6.3f} s ({base / warm_s:.1f}x)"
            f"   cold {cold_s:6.3f} s ({base / cold_s:.1f}x)"
        )
    print()
    io_base = best_of(io_serial)
    print(f"{'waits, serial':<26}{io_base:6.3f} s")
    for label, run in (("waits, threads", io_threads), ("waits, asyncio", io_asyncio)):
        taken = best_of(run)
        print(f"{label:<26}{taken:6.3f} s ({io_base / taken:.1f}x)")


if __name__ == "__main__":
    main()
