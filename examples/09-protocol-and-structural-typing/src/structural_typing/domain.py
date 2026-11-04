"""Shipping values for the example: a consignment, its hazmat variant and money."""

import math
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)

_UN_NUMBER = re.compile(r"UN\d{4}")


class BookingError(Exception):
    """A booking could not be placed."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass in kilograms."""

    kilograms: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.kilograms) and self.kilograms > 0):
            raise ValueError(f"kilograms must be positive, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code. Addition needs one currency."""

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment to a UN/LOCODE destination."""

    id: ConsignmentId
    weight: Weight
    destination: str


@dataclass(frozen=True, slots=True, kw_only=True)
class HazmatConsignment(Consignment):
    """A consignment carrying dangerous goods, identified by a UN number."""

    un_number: str

    def __post_init__(self) -> None:
        if not _UN_NUMBER.fullmatch(self.un_number):
            raise ValueError(f"un_number must look like UN1203, got {self.un_number!r}")
