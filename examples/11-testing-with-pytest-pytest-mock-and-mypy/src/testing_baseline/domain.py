"""Shipping values for the example: a consignment, its weight and money."""

import math
from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class RatingError(Exception):
    """A rate quote could not be produced."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass in kilograms."""

    kilograms: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.kilograms) and self.kilograms > 0):
            raise ValueError(f"kilograms must be positive and finite, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code. Ordering needs one currency."""

    amount: Decimal
    currency: str

    def __lt__(self, other: Money) -> bool:
        if other.currency != self.currency:
            raise ValueError(f"cannot compare {other.currency} with {self.currency}")
        return self.amount < other.amount


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment to a UN/LOCODE destination."""

    id: ConsignmentId
    weight: Weight
    destination: str
