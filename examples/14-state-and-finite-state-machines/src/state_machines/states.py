"""The lifecycle as frozen states, each holding only its own data, and a match over them."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import assert_never

from state_machines.domain import (
    ConsignmentId,
    ConsignmentStatus,
    HandlingEvent,
    HandlingKind,
    TransitionError,
)


@dataclass(frozen=True, slots=True)
class Booked:
    origin: str


@dataclass(frozen=True, slots=True)
class Loaded:
    port: str


@dataclass(frozen=True, slots=True)
class InTransit:
    departed_from: str
    days_sailed: int = 0
    delay_days: int = 0


@dataclass(frozen=True, slots=True)
class Cleared:
    port: str


@dataclass(frozen=True, slots=True)
class Delivered:
    port: str


type ConsignmentState = Booked | Loaded | InTransit | Cleared | Delivered


def status_of(state: ConsignmentState) -> ConsignmentStatus:
    """Name the status a state stands for."""
    match state:
        case Booked():
            return ConsignmentStatus.BOOKED
        case Loaded():
            return ConsignmentStatus.LOADED
        case InTransit():
            return ConsignmentStatus.IN_TRANSIT
        case Cleared():
            return ConsignmentStatus.CLEARED
        case Delivered():
            return ConsignmentStatus.DELIVERED
        case _:
            assert_never(state)


def apply_event(state: ConsignmentState, event: HandlingEvent) -> ConsignmentState:
    """Return the state an event leads to, or refuse it with a domain error."""
    match state:
        case Booked() if event.kind is HandlingKind.LOADED:
            return Loaded(event.location)
        case Loaded() if event.kind is HandlingKind.DEPARTED:
            return InTransit(departed_from=event.location)
        case InTransit() if event.kind is HandlingKind.CLEARED:
            return Cleared(event.location)
        case Cleared() if event.kind is HandlingKind.DELIVERED:
            return Delivered(event.location)
        case Booked() | Loaded() | InTransit() | Cleared() | Delivered():
            raise TransitionError(f"{event.kind.name} not allowed when {status_of(state).name}")
        case _:
            assert_never(state)


def track(
    consignment_id: ConsignmentId, events: Iterable[HandlingEvent], *, start: ConsignmentState
) -> ConsignmentState:
    """Fold a consignment's handling history into its current state."""
    state = start
    for event in events:
        if event.consignment_id != consignment_id:
            raise TransitionError(
                f"event for {event.consignment_id} in the history of {consignment_id}"
            )
        state = apply_event(state, event)
    return state
