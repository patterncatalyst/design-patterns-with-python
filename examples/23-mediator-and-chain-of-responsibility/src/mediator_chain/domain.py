"""Shipping values for the clearance example: a customs declaration and the tracking record."""

from dataclasses import dataclass
from enum import Enum
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class DocumentKind(Enum):
    """The documents a customs declaration can carry."""

    COMMERCIAL_INVOICE = "commercial invoice"
    DANGEROUS_GOODS_DECLARATION = "dangerous goods declaration"


@dataclass(frozen=True, slots=True)
class Commodity:
    """A commodity classified by harmonised-system code. `restricted` goods need inspection."""

    hs_code: str
    description: str
    restricted: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomsDeclaration:
    """What customs is told about a consignment. `duty_paid` means duty paid in full."""

    consignment_id: ConsignmentId
    port: str
    commodity: Commodity
    documents: frozenset[DocumentKind]
    duty_paid: bool


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


class TrackingHistory:
    """Records handling events in the order they arrive."""

    def __init__(self) -> None:
        self._events: list[HandlingEvent] = []

    def record(self, event: HandlingEvent, /) -> None:
        self._events.append(event)

    @property
    def events(self) -> tuple[HandlingEvent, ...]:
        return tuple(self._events)
