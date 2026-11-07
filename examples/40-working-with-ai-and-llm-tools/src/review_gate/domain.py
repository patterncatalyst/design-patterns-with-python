"""Value types for the pricing code under review."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class RatingError(LookupError):
    """No pricing rule is known by that name."""


@dataclass(frozen=True, slots=True)
class Weight:
    kilograms: Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "EUR"


@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str
    weight: Weight
