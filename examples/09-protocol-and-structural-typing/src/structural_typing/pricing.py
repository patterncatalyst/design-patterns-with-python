"""Pricing rules as a callback Protocol, and quoters generic in the consignment type."""

from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import Protocol

from structural_typing.domain import Consignment, HazmatConsignment, Money

_CENT = Decimal("0.01")
_PER_KG = Decimal("1.20")
_DEFAULT_SURCHARGE = Money(Decimal("25.00"), "EUR")
_HAZMAT_SURCHARGES: Mapping[str, Money] = frozendict({"UN1203": Money(Decimal("40.00"), "EUR")})


class PricingRule(Protocol):
    """A rule prices a consignment. The consignment is positional-only, so names may differ."""

    def __call__(self, consignment: Consignment, /) -> Money: ...


def flat_rate(consignment: Consignment) -> Money:
    return Money(Decimal("25.00"), "EUR")


def per_kg(shipment: Consignment) -> Money:
    """The parameter is not called consignment on purpose: PricingRule ignores the name."""
    return Money((Decimal(str(shipment.weight.kilograms)) * _PER_KG).quantize(_CENT), "EUR")


def no_discount(consignment: Consignment, /) -> Money:
    """A null object that is the right answer: the discount to subtract is zero."""
    return Money(Decimal("0.00"), "EUR")


def quote(
    consignment: Consignment, rule: PricingRule, discount: PricingRule = no_discount
) -> Money:
    gross = rule(consignment)
    off = discount(consignment)
    return gross + Money(-off.amount, off.currency)


class Quoter[T: Consignment](Protocol):
    """Prices consignments of type T. Variance is inferred from how T is used."""

    def quote(self, consignment: T, /) -> Money: ...


class GeneralQuoter:
    def quote(self, consignment: Consignment, /) -> Money:
        return per_kg(consignment)


class HazmatQuoter:
    def quote(self, consignment: HazmatConsignment, /) -> Money:
        surcharge = _HAZMAT_SURCHARGES.get(consignment.un_number, _DEFAULT_SURCHARGE)
        return per_kg(consignment) + surcharge


def price_all(
    quoter: Quoter[Consignment], consignments: Iterable[Consignment]
) -> tuple[Money, ...]:
    return tuple(quoter.quote(c) for c in consignments)


def price_hazmat(
    quoter: Quoter[HazmatConsignment], consignments: Iterable[HazmatConsignment]
) -> tuple[Money, ...]:
    return tuple(quoter.quote(c) for c in consignments)
