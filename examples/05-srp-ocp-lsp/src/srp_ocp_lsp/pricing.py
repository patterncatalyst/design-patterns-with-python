"""Pricing: the RateCalculator contract and two implementations of it."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from types import MappingProxyType
from typing import Protocol

from srp_ocp_lsp.domain import Consignment, Money, RatingError, Tariff

ZONES = ("EU", "ASIA", "AMERICAS")

_CENT = Decimal("0.01")


class RateCalculator(Protocol):
    """Prices one consignment.

    Contract, which no type signature states:

    - accepts every consignment whose zone is in ``ZONES``;
    - returns ``Money`` in the tariff currency (EUR), non-negative, quantised to cents;
    - a heavier consignment in the same zone is never cheaper;
    - a zone outside ``ZONES`` raises ``RatingError``.
    """

    def price(self, consignment: Consignment, /) -> Money: ...


TARIFF = Tariff(
    MappingProxyType(
        {
            "EU": Money(Decimal("1.20"), "EUR"),
            "ASIA": Money(Decimal("3.40"), "EUR"),
            "AMERICAS": Money(Decimal("2.75"), "EUR"),
        }
    )
)

FLAT_BY_ZONE: Mapping[str, Money] = MappingProxyType(
    {
        "EU": Money(Decimal("25.00"), "EUR"),
        "ASIA": Money(Decimal("60.00"), "EUR"),
        "AMERICAS": Money(Decimal("45.00"), "EUR"),
    }
)


@dataclass(frozen=True, slots=True)
class BaseRate:
    """Weight times the per-kilogram rate of the zone, rounded half up to cents."""

    tariff: Tariff

    def price(self, consignment: Consignment, /) -> Money:
        rate = self.tariff.rate_for(consignment.zone)
        amount = rate.amount * Decimal(str(consignment.weight.kilograms))
        return Money(amount.quantize(_CENT, rounding=ROUND_HALF_UP), rate.currency)


@dataclass(frozen=True, slots=True)
class FlatRate:
    """One fixed price per zone, whatever the weight."""

    by_zone: Mapping[str, Money] = FLAT_BY_ZONE

    def price(self, consignment: Consignment, /) -> Money:
        try:
            return self.by_zone[consignment.zone]
        except KeyError:
            raise RatingError(f"no flat rate for zone {consignment.zone!r}") from None
