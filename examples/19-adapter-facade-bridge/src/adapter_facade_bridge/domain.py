"""Shipping values for the adapter example: weight with exact unit conversion, money, a booking."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, NewType, Self

ConsignmentId = NewType("ConsignmentId", str)

# The international pound of 1959, exactly.
POUND_IN_KILOGRAMS: Final = Decimal("0.45359237")


class BookingError(ValueError):
    """A booking that the desk refuses to place."""


class CarrierError(RuntimeError):
    """A carrier refused or failed a request."""


class UnknownCarrierError(LookupError):
    """A carrier code that the registry does not know."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass held in kilograms. Pounds convert in one place."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not self.kilograms.is_finite() or self.kilograms <= 0:
            raise ValueError(f"weight must be positive and finite, got {self.kilograms}")

    @classmethod
    def from_pounds(cls, pounds: Decimal) -> Self:
        return cls(pounds * POUND_IN_KILOGRAMS)

    @property
    def pounds(self) -> Decimal:
        return self.kilograms / POUND_IN_KILOGRAMS


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code."""

    amount: Decimal
    currency: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """What a caller wants carried."""

    id: ConsignmentId
    weight: Weight
    origin: str
    destination: str


@dataclass(frozen=True, slots=True)
class Booking:
    """A carrier's reference for a consignment, with the declared value when it is insured."""

    carrier: str
    reference: str
    insured_for: Money | None = None
