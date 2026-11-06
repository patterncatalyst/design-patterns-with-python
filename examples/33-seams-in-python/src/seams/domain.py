"""The shipping values the legacy rating engine works with."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class CarrierTimeoutError(Exception):
    """A carrier did not answer."""


@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str
    weight_kg: Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "EUR"


@dataclass(frozen=True, slots=True)
class RateQuote:
    consignment_id: ConsignmentId
    carrier: str
    total: Money
