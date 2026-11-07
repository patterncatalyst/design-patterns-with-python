"""Fixtures: a lock that records who reaches it, and two threads released together.

The recording lock is a seam, not a comparison form. It lets a test hold one thread inside the
lock until the other has arrived at its door.
"""

from collections.abc import Callable
from threading import Barrier, Event, Lock, Thread
from typing import TYPE_CHECKING

import pytest
from gil_and_performance.domain import ConsignmentId

if TYPE_CHECKING:
    from gil_and_performance.domain import SlotId
    from gil_and_performance.stowage import StowagePlan

GUARD_SECONDS = 10


class _RecordingLock:
    """Counts the callers that reach it and sets an event when the second one arrives."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._count = Lock()
        self._callers = 0
        self._second = Event()

    def __enter__(self) -> None:
        with self._count:
            self._callers += 1
            if self._callers == 2:
                self._second.set()
        self._lock.acquire()

    def __exit__(self, *exc: object) -> None:
        self._lock.release()

    @property
    def second_caller(self) -> bool:
        return self._second.is_set()

    def wait_for_second_caller(self) -> None:
        if not self._second.wait(GUARD_SECONDS):
            raise TimeoutError("the second caller never reached the lock")


@pytest.fixture
def recording_lock() -> _RecordingLock:
    return _RecordingLock()


def _reserve_from_two_threads(plan: StowagePlan) -> list[SlotId]:
    ids = (ConsignmentId("CN-1"), ConsignmentId("CN-2"))
    slots: list[SlotId | None] = [None, None]

    def book(index: int) -> None:
        slots[index] = plan.reserve(ids[index])

    threads = [Thread(target=book, args=(index,)) for index in (0, 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(GUARD_SECONDS)
        assert not thread.is_alive(), "a booking thread did not finish within the guard"
    return sorted(slot for slot in slots if slot is not None)


@pytest.fixture
def two_threads() -> Callable[[StowagePlan], list[SlotId]]:
    return _reserve_from_two_threads


@pytest.fixture
def barrier_gap() -> Callable[[], object]:
    """A gap that parks each thread until both have reached it."""
    return Barrier(2, timeout=GUARD_SECONDS).wait
