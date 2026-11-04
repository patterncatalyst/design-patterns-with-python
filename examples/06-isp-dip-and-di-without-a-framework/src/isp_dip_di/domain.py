"""Shipping value types shared by the policy modules and the carrier adapters."""

import math
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum, auto
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


@dataclass(frozen=True, slots=True)
class Weight:
    """A mass in kilograms: finite and strictly positive."""

    kilograms: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.kilograms) or self.kilograms <= 0:
            raise ValueError(f"weight must be finite and positive, got {self.kilograms!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment of a given weight between two UN/LOCODE locations."""

    id: ConsignmentId
    weight: Weight
    origin: str
    destination: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    """What a carrier needs to accept a consignment."""

    consignment: Consignment
    insured: bool = False


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

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)
