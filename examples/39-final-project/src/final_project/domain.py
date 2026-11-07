"""Value types shared by every area: money, weight, consignments, requests and handling events."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)

FASTLINE = "FASTLINE"


@dataclass(frozen=True, slots=True)
class Money:
    """An amount in one currency. Adding two currencies is an error, not a conversion."""

    amount: Decimal
    currency: str = "EUR"

    def __add__(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True, slots=True)
class Weight:
    kilograms: Decimal

    def __post_init__(self) -> None:
        if self.kilograms <= 0:
            raise ValueError(f"weight must be positive, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Commodity:
    hs_code: str
    description: str
    value: Money


@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str
    destination: str
    weight: Weight
    commodities: tuple[Commodity, ...]


@dataclass(frozen=True, slots=True)
class BookingRequest:
    consignment: Consignment
    carrier: str = FASTLINE


@dataclass(frozen=True, slots=True)
class Sailing:
    code: str
    origin: str
    destination: str


class HandlingKind(Enum):
    BOOKED = auto()
    LOADED = auto()
    DEPARTED = auto()
    CLEARED = auto()
    DELIVERED = auto()


@dataclass(frozen=True, slots=True)
class HandlingEvent:
    consignment_id: ConsignmentId
    kind: HandlingKind
    location: str
