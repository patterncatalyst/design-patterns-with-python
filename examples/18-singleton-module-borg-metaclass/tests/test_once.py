import functools
import threading
from collections.abc import Callable
from types import TracebackType

import pytest
from singleton.domain import TariffTable
from singleton.once import NOT_LOADED, LoadOnce
from singleton.tariff_table import STANDARD_RATES

_GUARD_SECONDS = 10


class _GatedLock:
    """A lock that makes two threads meet at its door before either goes in.

    Both threads have passed the first check by the time they wait here, so the interleaving that
    the inner check exists for is the only one that can happen.
    """

    def __init__(self) -> None:
        self._gate = threading.Barrier(2, timeout=_GUARD_SECONDS)
        self._lock = threading.Lock()
        self.entries = 0

    def __enter__(self) -> None:
        self._gate.wait()
        self._lock.acquire()
        self.entries += 1

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._lock.release()


class _CountingLock:
    """A lock that only counts, for a single thread."""

    def __init__(self) -> None:
        self.entries = 0

    def __enter__(self) -> None:
        self.entries += 1

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None


def _run_on_threads[T](call: Callable[[], T], count: int) -> list[T]:
    """Call from `count` threads, return the results in thread order and re-raise a failure."""
    results: list[T | None] = [None] * count
    failures: list[BaseException] = []

    def work(index: int) -> None:
        try:
            results[index] = call()
        except BaseException as error:
            failures.append(error)

    threads = [threading.Thread(target=work, args=(i,)) for i in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=_GUARD_SECONDS)
    assert not any(thread.is_alive() for thread in threads)
    if failures:
        raise failures[0]
    return [result for result in results if result is not None]


def test_functools_cache_runs_a_loader_twice_when_two_threads_arrive_together() -> None:
    both_inside = threading.Barrier(2, timeout=_GUARD_SECONDS)
    loads: list[str] = []

    @functools.cache
    def cached() -> TariffTable:
        loads.append("tariff")
        both_inside.wait()
        return TariffTable(STANDARD_RATES)

    first, second = _run_on_threads(cached, 2)
    assert len(loads) == 2
    assert first is not second


def test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check() -> None:
    loads: list[str] = []
    lock = _GatedLock()

    def load() -> TariffTable:
        loads.append("tariff")
        return TariffTable(STANDARD_RATES)

    once = LoadOnce(load, lock=lock)
    first, second = _run_on_threads(once, 2)
    assert loads == ["tariff"]
    assert first is second
    assert lock.entries == 2


def test_a_loaded_value_is_read_without_taking_the_lock() -> None:
    lock = _CountingLock()
    once = LoadOnce(lambda: TariffTable(STANDARD_RATES), lock=lock)
    value = once()
    assert lock.entries == 1
    assert once() is value
    assert once() is value
    assert once() is value
    assert lock.entries == 1


def test_load_once_keeps_a_loader_that_returns_none() -> None:
    loads: list[str] = []

    def load() -> None:
        loads.append("none")

    once = LoadOnce(load)
    assert [once(), once(), once()] == [None, None, None]
    assert loads == ["none"]


def test_the_not_loaded_marker_is_a_sentinel_and_not_none() -> None:
    assert repr(NOT_LOADED) == "NOT_LOADED"
    assert NOT_LOADED is not None


def test_a_failed_load_is_tried_again() -> None:
    attempts: list[str] = []

    def load() -> str:
        attempts.append("try")
        if len(attempts) == 1:
            raise RuntimeError("first load fails")
        return "ok"

    once = LoadOnce(load)
    with pytest.raises(RuntimeError, match="first load fails"):
        once()
    assert once() == "ok"
    assert attempts == ["try", "try"]
