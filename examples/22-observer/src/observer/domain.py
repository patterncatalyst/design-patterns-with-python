"""Tracking values for the observer example: a handling event raised as cargo moves."""

from dataclasses import dataclass
from enum import Enum
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class HandlingKind(Enum):
    """What happened to the cargo."""

    BOOKED = "booked"
    LOADED = "loaded"
    DEPARTED = "departed"
    CLEARED = "cleared"
    DELIVERED = "delivered"


@dataclass(frozen=True, slots=True)
class HandlingEvent:
    """One handling event: a single class, with the kind as an enum."""

    consignment_id: ConsignmentId
    kind: HandlingKind
    port: str
