"""Shipping values for the iterator example: handling events and the tracking history."""

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class HandlingKind(Enum):
    """What happened to the cargo, in lifecycle order."""

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


class TrackingHistory:
    """Records handling events in the order they arrive.

    Each loop over the history gets a fresh iterator, so it can be walked many times.
    """

    def __init__(self) -> None:
        self._events: list[HandlingEvent] = []

    def record(self, event: HandlingEvent, /) -> None:
        self._events.append(event)

    def __iter__(self) -> Iterator[HandlingEvent]:
        yield from self._events
