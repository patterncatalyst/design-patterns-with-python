import functools
from collections.abc import Iterator
from decimal import Decimal

import pytest
from singleton.domain import TariffTable
from singleton.tariff_table import STANDARD_RATES

_OVERRIDES: dict[str, Decimal] = {}


class _NaiveTariffTable:
    """The class every call site constructs for itself, so each one loads."""

    def __init__(self, log: list[str]) -> None:
        log.append("naive")
        self.table = TariffTable(STANDARD_RATES)


@functools.cache
def _cached_tariff() -> TariffTable:
    return TariffTable(frozendict({**STANDARD_RATES, **_OVERRIDES}))


@pytest.fixture(autouse=True)
def _clean_cache() -> Iterator[None]:
    _OVERRIDES.clear()
    _cached_tariff.cache_clear()
    yield
    _OVERRIDES.clear()
    _cached_tariff.cache_clear()


def test_a_naive_class_loads_the_table_once_per_caller() -> None:
    log: list[str] = []
    first = _NaiveTariffTable(log)
    second = _NaiveTariffTable(log)
    assert log == ["naive", "naive"]
    assert first is not second
    assert first.table is not second.table


def test_a_cached_loader_carries_one_tests_table_into_the_next() -> None:
    # Phase one stands for a first test that overrides a rate and loads.
    _OVERRIDES["ASIA"] = Decimal("9")
    assert _cached_tariff().rate_for("ASIA") == Decimal("9")
    # Phase two stands for the next test: the override is gone, the table is not.
    _OVERRIDES.clear()
    assert _cached_tariff().rate_for("ASIA") == Decimal("9")


def test_cache_clear_resets_the_cached_loader() -> None:
    _OVERRIDES["ASIA"] = Decimal("9")
    assert _cached_tariff().rate_for("ASIA") == Decimal("9")
    _OVERRIDES.clear()
    _cached_tariff.cache_clear()
    assert _cached_tariff().rate_for("ASIA") == Decimal("2.40")
