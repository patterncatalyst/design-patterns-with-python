"""A load that runs once under threads, for a load that needs run-time input."""

import threading
from collections.abc import Callable
from contextlib import AbstractContextManager

NOT_LOADED = sentinel("NOT_LOADED")


class LoadOnce[T]:
    """Call `load` the first time, keep the result, and read it without the lock afterwards.

    The lock is injected so a test can place both threads between the first check and the lock.
    """

    def __init__(
        self,
        load: Callable[[], T],
        *,
        lock: AbstractContextManager[object, None] | None = None,
    ) -> None:
        self._load = load
        self._lock = lock if lock is not None else threading.Lock()
        self._value: T | NOT_LOADED = NOT_LOADED

    def __call__(self) -> T:
        if self._value is NOT_LOADED:
            with self._lock:
                if self._value is NOT_LOADED:
                    self._value = self._load()
        return self._value
