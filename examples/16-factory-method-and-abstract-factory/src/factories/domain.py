"""Shipping values for the factory example: money, carrier settings, a quote and a shipment."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class UnknownCarrierError(LookupError):
    """A carrier code that no registry knows."""


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code."""

    amount: Decimal
    currency: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CarrierSettings:
    """What a carrier gateway needs to be constructed."""

    account: str
    sandbox: bool = False


@dataclass(frozen=True, slots=True)
class CarrierQuote:
    """A carrier's price for one consignment."""

    carrier: str
    price: Money


@dataclass(frozen=True, slots=True)
class Shipment:
    """A booked consignment: the carrier's reference, the printed label and the quote."""

    reference: str
    label: str
    quote: CarrierQuote
