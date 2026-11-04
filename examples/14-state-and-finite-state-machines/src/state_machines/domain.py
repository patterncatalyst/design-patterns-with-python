"""Shipping values for the lifecycle example: handling events, statuses and the domain error."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class TransitionError(Exception):
    """An event is not allowed in the consignment's current state."""


class HandlingKind(Enum):
    """The kinds of handling event a consignment can receive."""

    BOOKED = auto()
    LOADED = auto()
    DEPARTED = auto()
    CLEARED = auto()
    DELIVERED = auto()


class ConsignmentStatus(Enum):
    """Where a consignment is in its lifecycle."""

    BOOKED = auto()
    LOADED = auto()
    IN_TRANSIT = auto()
    CLEARED = auto()
    DELIVERED = auto()


@dataclass(frozen=True, slots=True)
class HandlingEvent:
    """One thing that happened to a consignment at a UN/LOCODE location."""

    consignment_id: ConsignmentId
    kind: HandlingKind
    location: str
