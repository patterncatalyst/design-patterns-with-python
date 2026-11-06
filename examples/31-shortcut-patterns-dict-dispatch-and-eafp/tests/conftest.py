"""Fixtures. The look-first cache is the comparison form: it runs the same table of cases as
``DutyRateCache``. ``_HandoverRates`` is the seam that forces a race without a clock."""

import threading
from collections.abc import Callable, MutableMapping
from decimal import Decimal
from typing import Protocol

import pytest
from shortcut_patterns.duties import DutyRateCache

type Load = Callable[[str], Decimal]


class DutyRateView(Protocol):
    """What the shared table reads from a cache: one read and one eviction."""

    def rate_for(self, hs_code: str, /) -> Decimal: ...

    def evict(self, hs_code: str, /) -> None: ...


type CacheForm = Callable[[Load, MutableMapping[str, Decimal]], DutyRateView]


class _LookFirstDutyRateCache(DutyRateCache):
    """The comparison: check that the code is present, then read it."""

    def rate_for(self, hs_code: str) -> Decimal:
        if hs_code in self._rates:
            return self._rates[hs_code]
        rate = self._load(hs_code)
        self._rates[hs_code] = rate
        return rate


class _HandoverRates(dict[str, Decimal]):
    """A dict that parks the first read until the test says go.

    ``__contains__`` answers and then parks, so a look-first reader has its answer when another
    thread evicts. ``__getitem__`` parks and then reads, so an EAFP reader has not read yet. The
    barrier is waited on twice: once when the reader has parked, once to let it go.
    """

    def __init__(self, rates: dict[str, Decimal]) -> None:
        super().__init__(rates)
        self.barrier = threading.Barrier(2, timeout=10)
        self._parked = False

    def _park(self) -> None:
        if self._parked:
            return
        self._parked = True
        self.barrier.wait()
        self.barrier.wait()

    def __contains__(self, key: object) -> bool:
        found = super().__contains__(key)
        self._park()
        return found

    def __getitem__(self, key: str) -> Decimal:
        self._park()
        return super().__getitem__(key)


class RecordingLoad:
    """A loader that appends each code it is asked for and answers 8.0."""

    def __init__(self) -> None:
        self.codes: list[str] = []

    def __call__(self, hs_code: str) -> Decimal:
        self.codes.append(hs_code)
        return Decimal("8.0")


@pytest.fixture
def recording_load() -> RecordingLoad:
    return RecordingLoad()


@pytest.fixture
def eafp_form() -> CacheForm:
    return lambda load, rates: DutyRateCache(load, rates=rates)


@pytest.fixture
def look_first_form() -> CacheForm:
    return lambda load, rates: _LookFirstDutyRateCache(load, rates=rates)


@pytest.fixture(params=["eafp", "lbyl"])
def cache_form(
    request: pytest.FixtureRequest, eafp_form: CacheForm, look_first_form: CacheForm
) -> CacheForm:
    """``DutyRateCache`` (EAFP) or ``_LookFirstDutyRateCache`` (look first)."""
    if request.param == "eafp":
        return eafp_form
    return look_first_form


@pytest.fixture
def handover_rates() -> _HandoverRates:
    """A cache storage holding a stale rate for 0901.21, whose first read parks."""
    return _HandoverRates({"0901.21": Decimal("6.5")})
