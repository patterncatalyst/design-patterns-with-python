"""Threads and the GIL: what it does not protect, and the deterministic way to show it.

The GIL serialises bytecode, not your invariants. ``self.count += 1`` is a load, an add and a
store; a thread switch between them loses an update. Provoking that by timing is unreliable,
so the classes below take a ``between`` hook that runs exactly in the gap, which lets a test
park two threads there with a :class:`threading.Barrier`.
"""

import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

_BARRIER_GUARD_SECONDS = 10.0  # failure guard only: a healthy run never waits on it


def nothing() -> None:
    """Default ``between`` hook."""


class UnsafeCounter:
    """A shipment counter whose read-modify-write is not atomic."""

    def __init__(self) -> None:
        self.count = 0

    def bump(self) -> None:
        """The textbook form: three bytecodes (load, add, store), no atomicity."""
        self.count += 1

    def bump_split(self, between: Callable[[], None] = nothing) -> None:
        """The same read-modify-write with the gap made explicit."""
        current = self.count
        between()
        self.count = current + 1


class LockedCounter:
    """The fix: one lock around the whole read-modify-write."""

    def __init__(self) -> None:
        self.count = 0
        self._lock = threading.Lock()

    def bump(self) -> None:
        with self._lock:
            self.count += 1


def run_threads(target: Callable[[], None], workers: int) -> None:
    """Start ``workers`` threads on ``target`` and join them all."""
    threads = [threading.Thread(target=target) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def lost_update_with_barrier() -> int:
    """Two threads read, meet at a barrier, then write: one increment is lost, always."""
    counter = UnsafeCounter()
    gap = threading.Barrier(2, timeout=_BARRIER_GUARD_SECONDS)

    def meet() -> None:
        gap.wait()

    run_threads(lambda: counter.bump_split(between=meet), workers=2)
    return counter.count


def hammer(counter: UnsafeCounter | LockedCounter, workers: int, rounds: int) -> int:
    """Increment from many threads released together. The unsafe result is not deterministic."""
    start = threading.Barrier(workers, timeout=_BARRIER_GUARD_SECONDS)

    def work() -> None:
        start.wait()
        for _ in range(rounds):
            counter.bump()

    run_threads(work, workers)
    return counter.count


def alternating_pollers(carrier_a: Sequence[str], carrier_b: Sequence[str]) -> list[str]:
    """Two carrier-poller threads take strict turns, orchestrated with two Events.

    The interleaving is a property of the handshake, not of the scheduler, so the log is the
    same on every run.
    """
    if len(carrier_a) != len(carrier_b):
        msg = "both carriers must have the same number of events"
        raise ValueError(msg)
    turn_a, turn_b = threading.Event(), threading.Event()
    log: list[str] = []

    def poll(events: Sequence[str], mine: threading.Event, theirs: threading.Event) -> None:
        for event in events:
            mine.wait(timeout=_BARRIER_GUARD_SECONDS)
            mine.clear()
            log.append(event)
            theirs.set()

    threads = [
        threading.Thread(target=poll, args=(carrier_a, turn_a, turn_b)),
        threading.Thread(target=poll, args=(carrier_b, turn_b, turn_a)),
    ]
    for thread in threads:
        thread.start()
    turn_a.set()
    for thread in threads:
        thread.join()
    return log


@dataclass
class LoadCounter[T]:
    """Wraps a loader and counts how often it ran."""

    loader: Callable[[], T]
    calls: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __call__(self) -> T:
        with self._lock:
            self.calls += 1
        return self.loader()


class RacyLazyValue[T]:
    """Module-level cache done wrong: check, then set, with a gap in between."""

    def __init__(self, load: Callable[[], T]) -> None:
        self._load = load
        self._value: T | None = None

    def get(self) -> T:
        if self._value is None:
            self._value = self._load()
        assert self._value is not None
        return self._value


class LockedLazyValue[T]:
    """Double-checked locking: the loader runs once however many threads arrive."""

    def __init__(self, load: Callable[[], T]) -> None:
        self._load = load
        self._value: T | None = None
        self._lock = threading.Lock()

    def get(self) -> T:
        if self._value is None:
            with self._lock:
                if self._value is None:
                    self._value = self._load()
        assert self._value is not None
        return self._value


def gather_in_threads[T](call: Callable[[], T], workers: int) -> list[T]:
    """Release ``workers`` threads together on ``call`` and collect their results."""
    start = threading.Barrier(workers, timeout=_BARRIER_GUARD_SECONDS)
    results: list[T] = []
    guard = threading.Lock()

    def work() -> None:
        start.wait()
        value = call()
        with guard:
            results.append(value)

    run_threads(work, workers)
    return results


def rendezvous_loader(parties: int, value: str) -> Callable[[], str]:
    """A loader that returns only once ``parties`` callers are inside it at the same time."""
    inside = threading.Barrier(parties, timeout=_BARRIER_GUARD_SECONDS)

    def load() -> str:
        inside.wait()
        return value

    return load
