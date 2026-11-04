"""The tariff table, built once when the module is first imported."""

from decimal import Decimal

from singleton.domain import TariffTable
from singleton.loads import record_load

STANDARD_RATES: frozendict[str, Decimal] = frozendict(
    {"EUROPE": Decimal("1.20"), "ASIA": Decimal("2.40")}
)


def load_tariff(rates: frozendict[str, Decimal]) -> TariffTable:
    """Build a table from rates, noting the load."""
    record_load("tariff")
    return TariffTable(rates)


TARIFF = load_tariff(STANDARD_RATES)
