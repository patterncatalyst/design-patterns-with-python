"""The shipping values the feed, the quotes, the signal and the stowage plan work with."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


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
    location: str  # a UN/LOCODE such as NLRTM or SGSIN


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


class CarrierTimeoutError(Exception):
    """A carrier did not answer."""


@dataclass(frozen=True, slots=True, order=True)
class SlotId:
    """A position on a sailing's stowage plan."""

    bay: int
    row: int
    tier: int
