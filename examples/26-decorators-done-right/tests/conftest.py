"""Fixtures. The comparison forms live here as fixture parameters so that they run the same
rendering table as the idiomatic code: a wrapper with ``functools.wraps`` and one without, and a
parametrised factory that takes its window positionally."""

from collections.abc import Callable
from functools import wraps
from typing import Protocol

import pytest
from decorators_done_right.domain import BillOfLading, ConsignmentId
from decorators_done_right.rendering import Clock, TimingSink, timed_render


class FakeClock:
    """A clock that moves only when a test says so."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


class Timings:
    """A timing sink that records what it was told, in order."""

    def __init__(self) -> None:
        self.records: list[tuple[str, float]] = []

    def __call__(self, name: str, seconds: float, /) -> None:
        self.records.append((name, seconds))


@pytest.fixture
def timings() -> Timings:
    return Timings()


@pytest.fixture
def bill() -> BillOfLading:
    return BillOfLading("BL-1", ConsignmentId("CN-1"), "NLRTM", "SGSIN")


class WrapperForm(Protocol):
    """A timer decorator, applied to any function without changing its signature for mypy."""

    def __call__[**P, R](self, func: Callable[P, R], /) -> Callable[P, R]: ...


def _bare_timer(sink: TimingSink, clock: Clock) -> WrapperForm:
    """The same timer as ``timed_render`` with ``functools.wraps`` left out."""

    def decorate[**P, R](func: Callable[P, R], /) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = clock()
            try:
                return func(*args, **kwargs)
            finally:
                sink(func.__name__, clock() - started)

        return wrapper

    return decorate


@pytest.fixture(params=["wraps", "bare"])
def wrapper_form(request: pytest.FixtureRequest, timings: Timings, clock: FakeClock) -> WrapperForm:
    """The timer with ``functools.wraps`` (the source's ``timed_render``) or without it."""
    if request.param == "wraps":
        return timed_render(timings, clock=clock)
    return _bare_timer(timings, clock)


@pytest.fixture
def bare_timer(timings: Timings, clock: FakeClock) -> WrapperForm:
    return _bare_timer(timings, clock)


@pytest.fixture
def timer(timings: Timings, clock: FakeClock) -> WrapperForm:
    """The source's ``timed_render``, bound to the recording sink and the fake clock."""
    return timed_render(timings, clock=clock)


type BillRenderer = Callable[[BillOfLading], str]
type PositionalFactory = Callable[[float], Callable[[BillRenderer], BillRenderer]]


def _cached_for_positional[**P, R](
    seconds: float,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """The comparison: the window is a positional argument, so a bare ``@`` use is not refused."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)

        return wrapper

    return decorate


@pytest.fixture
def positional_factory() -> PositionalFactory:
    return _cached_for_positional
