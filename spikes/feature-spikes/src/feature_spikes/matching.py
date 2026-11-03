"""PDP-014: structural pattern matching over tracking events."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, assert_never


@dataclass(frozen=True)
class Booked:
    reference: str


@dataclass(frozen=True)
class PickedUp:
    driver: str


@dataclass(frozen=True)
class InTransit:
    location: str


@dataclass(frozen=True)
class Delivered:
    signed_by: str


@dataclass(frozen=True)
class DeliveryFailed:
    reason: str


type TrackingEvent = Booked | PickedUp | InTransit | Delivered | DeliveryFailed


def describe(event: TrackingEvent) -> str:
    """Class patterns use the positional ``__match_args__`` dataclasses generate."""
    match event:
        case Booked(reference):
            return f"booked as {reference}"
        case PickedUp(driver):
            return f"picked up by {driver}"
        case InTransit("customs") | InTransit("border"):
            return "held at a border crossing"
        case InTransit(location) if location.startswith("depot"):
            return f"sorting at {location}"
        case InTransit(location):
            return f"in transit at {location}"
        case Delivered(signed_by):
            return f"delivered, signed by {signed_by}"
        case DeliveryFailed(reason):
            return f"delivery failed: {reason}"
        case _:
            assert_never(event)


def is_terminal(event: TrackingEvent) -> bool:
    match event:
        case Delivered() | DeliveryFailed():
            return True
        case Booked() | PickedUp() | InTransit():
            return False
        case _:
            assert_never(event)


def from_webhook(payload: Mapping[str, Any]) -> TrackingEvent:
    """Mapping patterns match on keys and ignore extra keys."""
    match payload:
        case {"type": "booked", "reference": str(reference)}:
            return Booked(reference)
        case {"type": "picked_up", "driver": str(driver)}:
            return PickedUp(driver)
        case {"type": "in_transit", "location": {"name": str(name)}}:
            return InTransit(name)
        case {"type": "delivered", "signed_by": str(signed_by)}:
            return Delivered(signed_by)
        case {"type": "failed", "reason": str(reason)}:
            return DeliveryFailed(reason)
        case {"type": str(kind)}:
            raise ValueError(f"unsupported webhook event {kind!r}")
        case _:
            raise ValueError("payload has no event type")


def summarize(history: Sequence[TrackingEvent]) -> str:
    """Sequence patterns match lists and tuples, never ``str`` or ``bytes``."""
    match history:
        case []:
            return "no events"
        case [Booked()]:
            return "booked, nothing moved yet"
        case [Booked(), *middle, Delivered(signed_by)]:
            return f"delivered after {len(middle)} events, signed by {signed_by}"
        case [*_, DeliveryFailed(reason)]:
            return f"failed: {reason}"
        case [first, *_, last]:
            return f"{type(first).__name__} ... {type(last).__name__}"
        case [only]:
            return f"single event {type(only).__name__}"
        case _:
            raise AssertionError("unreachable: empty and non-empty cases are covered")
