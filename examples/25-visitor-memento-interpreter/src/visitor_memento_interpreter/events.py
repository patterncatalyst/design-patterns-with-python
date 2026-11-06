"""Tracking events as a closed union, and one function per operation over it."""

from dataclasses import dataclass
from typing import assert_never

from visitor_memento_interpreter.domain import ConsignmentId, ConsignmentStatus


@dataclass(frozen=True, slots=True)
class Booked:
    consignment_id: ConsignmentId
    port: str


@dataclass(frozen=True, slots=True)
class Loaded:
    consignment_id: ConsignmentId
    port: str


@dataclass(frozen=True, slots=True)
class Departed:
    consignment_id: ConsignmentId
    port: str


@dataclass(frozen=True, slots=True)
class Cleared:
    consignment_id: ConsignmentId
    port: str


@dataclass(frozen=True, slots=True)
class Delivered:
    consignment_id: ConsignmentId
    port: str


type HandlingEvent = Booked | Loaded | Departed | Cleared | Delivered


def describe(event: HandlingEvent, /) -> str:
    """One line for a tracking feed. A kind left out is a type error."""
    match event:
        case Booked(consignment_id, port):
            return f"{consignment_id} booked at {port}"
        case Loaded(consignment_id, port):
            return f"{consignment_id} loaded at {port}"
        case Departed(consignment_id, port):
            return f"{consignment_id} departed {port}"
        case Cleared(consignment_id, port):
            return f"{consignment_id} cleared customs at {port}"
        case Delivered(consignment_id, port):
            return f"{consignment_id} delivered at {port}"
        case _:
            assert_never(event)


def status_after(event: HandlingEvent, /) -> ConsignmentStatus:
    """The status a consignment holds once the event has happened."""
    match event:
        case Booked():
            return ConsignmentStatus.BOOKED
        case Loaded():
            return ConsignmentStatus.LOADED
        case Departed():
            return ConsignmentStatus.IN_TRANSIT
        case Cleared():
            return ConsignmentStatus.CLEARED
        case Delivered():
            return ConsignmentStatus.DELIVERED
        case _:
            assert_never(event)
