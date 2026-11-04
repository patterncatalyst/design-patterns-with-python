"""The tariff table, built once when the module is first imported."""

from decimal import Decimal
from types import MappingProxyType

from three_way_split.domain import Money, Tariff
from three_way_split.loads import record_load


def _load() -> Tariff:
    record_load("tariff_table")
    return Tariff(
        MappingProxyType(
            {
                "EUROPE": Money(Decimal("1.20"), "EUR"),
                "ASIA": Money(Decimal("2.40"), "EUR"),
            }
        )
    )


TARIFF = _load()
