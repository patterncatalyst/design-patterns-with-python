"""Handling events and the history of one consignment."""

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum, auto

from data_model.money import ConsignmentId


class HandlingKind(Enum):
    """The stages of a consignment's journey."""

    BOOKED = auto()
    LOADED = auto()
    DEPARTED = auto()
    CLEARED = auto()
    DELIVERED = auto()


@dataclass(frozen=True, slots=True)
class HandlingEvent:
    """One thing that happened to a consignment at a location."""

    consignment_id: ConsignmentId
    kind: HandlingKind
    location: str


@dataclass(frozen=True, slots=True)
class TrackingHistory:
    """The handling events of one consignment, in order."""

    events: tuple[HandlingEvent, ...]

    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)
