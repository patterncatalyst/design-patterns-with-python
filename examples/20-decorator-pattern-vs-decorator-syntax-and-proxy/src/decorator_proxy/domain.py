"""Shipping values for the decorator example: weight, money that rounds to cents, a consignment."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)

_CENT = Decimal("0.01")


class RatingError(ValueError):
    """A price that cannot be computed."""


class CarrierTimeoutError(Exception):
    """A carrier did not answer in time."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass in kilograms."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not self.kilograms.is_finite() or self.kilograms <= 0:
            raise ValueError(f"weight must be positive and finite, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code."""

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise RatingError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)

    def scaled(self, factor: Decimal) -> Money:
        """Multiply by a factor and round half-up to cents."""
        return Money((self.amount * factor).quantize(_CENT, rounding=ROUND_HALF_UP), self.currency)


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """What a caller wants carried."""

    id: ConsignmentId
    weight: Weight
    destination: str
    dangerous_goods: bool = False


@dataclass(frozen=True, slots=True)
class CarrierQuote:
    """A carrier's answer to a request for a price."""

    carrier: str
    price: Money
