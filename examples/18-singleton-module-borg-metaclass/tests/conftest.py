"""Shared tables and the comparison fixtures for the other ways to write a singleton.

`_TariffBorg`, `_SingletonMeta` with `_MetaTariffTable`, and `_NewTariffTable` are test fixtures
that stand for code a team inherits or an assistant writes. They are not part of the model code in
`src/`. Each holds state at class level, so each fixture clears it before and after a test.
"""

import functools
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar, Self

import pytest
from singleton import tariff_table
from singleton.domain import TariffTable
from singleton.loads import LOAD_LOG
from singleton.once import LoadOnce
from singleton.tariff_table import STANDARD_RATES

_SOURCES: Mapping[str, frozendict[str, Decimal]] = frozendict(
    {
        "standard.csv": STANDARD_RATES,
        "express.csv": frozendict({"EUROPE": Decimal("2.00"), "ASIA": Decimal("4.00")}),
    }
)


class _TariffBorg:
    """Many objects, one shared `__dict__`."""

    _shared_state: ClassVar[dict[str, object]] = {}
    loads: ClassVar[list[str]] = []

    def __init__(self) -> None:
        self.__dict__ = self._shared_state
        if "rates" not in self.__dict__:
            self.loads.append("borg")
            self.rates = STANDARD_RATES

    @classmethod
    def reset(cls) -> None:
        cls._shared_state.clear()
        cls.loads.clear()


class _SingletonMeta(type):
    """A metaclass that builds each class once and returns that object on every later call."""

    _instances: ClassVar[dict[type, object]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in _SingletonMeta._instances:
            _SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return _SingletonMeta._instances[cls]


class _MetaTariffTable(metaclass=_SingletonMeta):
    loads: ClassVar[list[str]] = []

    def __init__(self, source: str) -> None:
        self.loads.append(source)
        self.source = source
        self.rates = _SOURCES[source]

    @classmethod
    def reset(cls) -> None:
        _SingletonMeta._instances.clear()
        cls.loads.clear()


class _NewTariffTable:
    """The `__new__` form: one instance, and `__init__` runs on every call."""

    _instance: ClassVar[Self | None] = None
    loads: ClassVar[list[str]] = []

    def __new__(cls, source: str) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, source: str) -> None:
        self.loads.append(source)
        self.source = source
        self.rates = _SOURCES[source]

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
        cls.loads.clear()


_CACHE_LOADS: list[str] = []


@functools.cache
def _cached_rates() -> frozendict[str, Decimal]:
    _CACHE_LOADS.append("cache")
    return STANDARD_RATES


@dataclass(frozen=True, slots=True)
class RatesForm:
    """What one caller can do with a form: read the rates, and count the loads so far."""

    read: Callable[[], Mapping[str, Decimal]]
    loads: Callable[[], int]


@pytest.fixture
def small_table() -> TariffTable:
    return TariffTable(frozendict({"EUROPE": Decimal("1.20")}))


@pytest.fixture
def borg() -> Iterator[type[_TariffBorg]]:
    _TariffBorg.reset()
    yield _TariffBorg
    _TariffBorg.reset()


@pytest.fixture
def meta_table() -> Iterator[type[_MetaTariffTable]]:
    _MetaTariffTable.reset()
    yield _MetaTariffTable
    _MetaTariffTable.reset()


@pytest.fixture
def new_table() -> Iterator[type[_NewTariffTable]]:
    _NewTariffTable.reset()
    yield _NewTariffTable
    _NewTariffTable.reset()


@pytest.fixture
def cached_rates() -> Iterator[Callable[[], frozendict[str, Decimal]]]:
    _cached_rates.cache_clear()
    _CACHE_LOADS.clear()
    yield _cached_rates
    _cached_rates.cache_clear()
    _CACHE_LOADS.clear()


@pytest.fixture(params=["module", "load-once", "borg", "metaclass", "cache"])
def rates_form(
    request: pytest.FixtureRequest,
    borg: type[_TariffBorg],
    meta_table: type[_MetaTariffTable],
    cached_rates: Callable[[], frozendict[str, Decimal]],
) -> RatesForm:
    """One way to give every caller the same rates, with fresh state for each test."""
    name: str = request.param
    if name == "module":
        return RatesForm(
            read=lambda: tariff_table.TARIFF.rates,
            loads=lambda: LOAD_LOG.count("tariff"),
        )
    if name == "load-once":
        log: list[str] = []

        def load() -> TariffTable:
            log.append("tariff")
            return TariffTable(STANDARD_RATES)

        once = LoadOnce(load)
        return RatesForm(read=lambda: once().rates, loads=lambda: len(log))
    if name == "borg":
        return RatesForm(read=lambda: borg().rates, loads=lambda: len(borg.loads))
    if name == "metaclass":
        return RatesForm(
            read=lambda: meta_table("standard.csv").rates,
            loads=lambda: len(meta_table.loads),
        )
    return RatesForm(read=cached_rates, loads=lambda: len(_CACHE_LOADS))
