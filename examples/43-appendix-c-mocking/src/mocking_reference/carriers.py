"""A carrier gateway, the contract the doubles in the tests copy, and one real implementation."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import NewType, Protocol

ConsignmentId = NewType("ConsignmentId", str)

CENT = Decimal("0.01")

# Illustrative rate and limit.
FASTLINE_RATE = Decimal("0.45")
FASTLINE_MAX_KILOGRAMS = Decimal("500")


@dataclass(frozen=True, slots=True)
class CarrierQuote:
    carrier: str
    total: Decimal


class CarrierTimeoutError(Exception):
    """The carrier did not answer."""


class CarrierGateway(Protocol):
    """What the booking code needs from a carrier."""

    def quote(self, consignment_id: ConsignmentId, weight_kg: Decimal, /) -> CarrierQuote: ...

    def book(self, consignment_id: ConsignmentId, /) -> str: ...


class FastlineGateway:
    """A deterministic carrier: a fixed rate per kilogram, and a timeout above the limit."""

    def quote(self, consignment_id: ConsignmentId, weight_kg: Decimal, /) -> CarrierQuote:
        if weight_kg > FASTLINE_MAX_KILOGRAMS:
            raise CarrierTimeoutError(f"FASTLINE did not answer for {consignment_id}")
        total = (weight_kg * FASTLINE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
        return CarrierQuote("FASTLINE", total)

    def book(self, consignment_id: ConsignmentId, /) -> str:
        return f"FASTLINE:{consignment_id}"


async def confirm(reference: str, /) -> str:
    """Confirm a booking reference."""
    return f"CONFIRMED:{reference}"
