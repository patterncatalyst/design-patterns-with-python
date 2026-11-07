"""The shipping values the slot reservation and the rating batch work with."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


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
    total: Money


@dataclass(frozen=True, slots=True, order=True)
class SlotId:
    """A position on a sailing's stowage plan."""

    bay: int
    row: int
    tier: int
