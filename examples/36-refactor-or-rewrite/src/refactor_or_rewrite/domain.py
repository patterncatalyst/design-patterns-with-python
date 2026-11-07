"""The shipping values both rating engines work with."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)

MARGIN = Decimal("1.10")


class RatingError(Exception):
    """A consignment cannot be priced."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass in kilograms."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not (self.kilograms.is_finite() and self.kilograms > 0):
            raise ValueError(f"kilograms must be positive and finite, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str
    weight: Weight


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "EUR"


@dataclass(frozen=True, slots=True)
class RateQuote:
    consignment_id: ConsignmentId
    total: Money
