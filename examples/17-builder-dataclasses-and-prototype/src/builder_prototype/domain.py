"""Shipping values for the booking example: a consignment id, a weight, money and one error."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class BookingError(ValueError):
    """A booking request that breaks one of its cross-field rules."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A finite, positive mass in kilograms."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not self.kilograms.is_finite() or self.kilograms <= 0:
            raise ValueError(f"kilograms must be finite and positive, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code."""

    amount: Decimal
    currency: str
