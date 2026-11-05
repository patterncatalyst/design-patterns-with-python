"""Shipping values shared by the three patterns: ids, statuses, documents, money, weight."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)

_CENT = Decimal("0.01")


class ConsignmentStatus(Enum):
    BOOKED = "booked"
    LOADED = "loaded"
    IN_TRANSIT = "in transit"
    CLEARED = "cleared"
    DELIVERED = "delivered"


class DocumentKind(Enum):
    COMMERCIAL_INVOICE = "commercial invoice"
    DANGEROUS_GOODS_DECLARATION = "dangerous goods declaration"


class AmendmentError(Exception):
    """A booking amendment that is refused."""


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code. Amounts never mix currencies."""

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __lt__(self, other: Money) -> bool:
        if other.currency != self.currency:
            raise ValueError(f"cannot compare {other.currency} with {self.currency}")
        return self.amount < other.amount

    def times(self, factor: Decimal) -> Money:
        """Scale the amount and round to cents."""
        return Money((self.amount * factor).quantize(_CENT, rounding=ROUND_HALF_UP), self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass in kilograms."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not self.kilograms.is_finite() or self.kilograms <= 0:
            raise ValueError(f"weight must be positive and finite, got {self.kilograms}")


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A consignment to price: its id, weight and UN/LOCODE destination."""

    id: ConsignmentId
    weight: Weight
    destination: str
