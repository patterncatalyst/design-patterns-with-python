"""Renderers and the decorators around them: a timer and a cache, each with an injected clock."""

import time
from collections.abc import Callable, Hashable
from functools import wraps
from textwrap import shorten

from decorators_done_right.domain import BillOfLading

type Clock = Callable[[], float]
type TimingSink = Callable[[str, float], None]


def render_bill(bill: BillOfLading, /, *, width: int = 72) -> str:
    """Render a bill of lading as one line of text."""
    line = (
        f"Bill of lading {bill.number}: consignment {bill.consignment_id} "
        f"from {bill.port_of_loading} to {bill.port_of_discharge}"
    )
    return shorten(line, width=width, placeholder="...")


def timed_render[**P, R](
    sink: TimingSink, *, clock: Clock = time.perf_counter
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Report the function's name and the elapsed clock time to ``sink`` after every call."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = clock()
            try:
                return func(*args, **kwargs)
            finally:
                sink(func.__name__, clock() - started)

        return wrapper

    return decorate


def cached_for[**P, R](
    *, seconds: float, clock: Clock = time.monotonic
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Serve a result again for ``seconds`` of clock time, one entry per distinct arguments.

    Single-threaded, and every argument must be hashable.
    """
    if seconds <= 0:
        raise ValueError(f"seconds must be positive, got {seconds}")

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        entries: dict[Hashable, tuple[float, R]] = {}

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, frozenset(kwargs.items()))
            now = clock()
            entry = entries.get(key)
            if entry is not None and now - entry[0] < seconds:
                return entry[1]
            result = func(*args, **kwargs)
            entries[key] = (now, result)
            return result

        return wrapper

    return decorate
