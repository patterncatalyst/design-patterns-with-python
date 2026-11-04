"""Shipping values for the rating example: a consignment, money, a quote and the rating error."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class RatingError(Exception):
    """A consignment could not be priced."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass in kilograms."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not (self.kilograms.is_finite() and self.kilograms > 0):
            raise ValueError(f"kilograms must be positive and finite, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code."""

    amount: Decimal
    currency: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment to a UN/LOCODE destination, priced by the zone it travels to."""

    id: ConsignmentId
    weight: Weight
    zone: str
    destination: str


@dataclass(frozen=True, slots=True)
class RateQuote:
    """A price and the name of the rule that produced it."""

    consignment_id: ConsignmentId
    rule: str
    price: Money
