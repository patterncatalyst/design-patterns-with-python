"""Quotes that take their table as a parameter, and one that reads the module's table."""

from decimal import Decimal

from singleton.domain import TariffTable
lazy from singleton import tariff_table


def quote(zone: str, kilograms: Decimal, *, table: TariffTable) -> Decimal:
    """Price a consignment from the table it is given."""
    return table.rate_for(zone) * kilograms


def quote_standard(zone: str, kilograms: Decimal) -> Decimal:
    """Price a consignment from the standard tariff, loaded on first use."""
    return quote(zone, kilograms, table=tariff_table.TARIFF)
