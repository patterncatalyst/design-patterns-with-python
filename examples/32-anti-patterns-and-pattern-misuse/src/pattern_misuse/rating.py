"""Rating a consignment with one function over a frozen tariff."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class RatingError(LookupError):
    """A zone the tariff has no flat fee for."""


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str


@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str


@dataclass(frozen=True, slots=True)
class Tariff:
    """Flat fees by zone, one fuel fee and one tax rate. Illustrative figures."""

    flat_fee_by_zone: frozendict[str, Decimal]
    fuel_fee: Decimal
    tax_rate: Decimal
    currency: str = "EUR"


@dataclass(frozen=True, slots=True)
class RateQuote:
    consignment_id: ConsignmentId
    total: Money


STANDARD_TARIFF = Tariff(
    flat_fee_by_zone=frozendict({"EU": Decimal("25.00"), "ASIA": Decimal("60.00")}),
    fuel_fee=Decimal("4.50"),
    tax_rate=Decimal("0.21"),
)


def quote(consignment: Consignment, tariff: Tariff) -> RateQuote:
    """Price a consignment: its zone's flat fee, the fuel fee, then tax rounded to the cent."""
    try:
        flat_fee = tariff.flat_fee_by_zone[consignment.zone]
    except KeyError:
        raise RatingError(f"no flat fee for zone {consignment.zone!r}") from None
    net = flat_fee + tariff.fuel_fee
    tax = (net * tariff.tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, Money(net + tax, tariff.currency))
