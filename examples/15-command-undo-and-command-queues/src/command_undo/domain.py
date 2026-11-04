"""Shipping values for the amendment example: a weight, a consignment and a booking request."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class AmendmentError(Exception):
    """An amendment cannot be applied, or there is nothing to undo or redo."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A mass in kilograms: finite and strictly positive."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not self.kilograms.is_finite() or self.kilograms <= 0:
            raise ValueError(f"weight must be finite and positive, got {self.kilograms!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment of a given weight bound for a UN/LOCODE destination."""

    id: ConsignmentId
    weight: Weight
    destination: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    """What the shipper asked for. Every field is an immutable value."""

    consignment: Consignment
    insured: bool = False
    instructions: frozendict[str, str] = frozendict()
