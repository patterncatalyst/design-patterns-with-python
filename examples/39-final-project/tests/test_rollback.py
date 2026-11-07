"""A refusal part-way through a booking undoes the completed steps, in reverse."""

from typing import TYPE_CHECKING

import pytest
from final_project.carriers import FastlineGateway
from final_project.clearance import ClearanceHeldError
from final_project.desk import BookingDesk
from final_project.domain import (
    BookingRequest,
    Consignment,
    ConsignmentId,
    HandlingEvent,
    Sailing,
)
from final_project.rating import per_kg
from final_project.stowage import SlotId, StowageFullError, StowagePlan
from final_project.tracking import Signal

if TYPE_CHECKING:
    from conftest import RecordingParts, World


def _desk(parts: RecordingParts) -> BookingDesk:
    return BookingDesk(
        rule=per_kg, plan=parts.plan, gateway=parts.gateway, events=Signal[HandlingEvent]()
    )


def test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking(
    world: World, recording_parts: RecordingParts, held_request: BookingRequest
) -> None:
    client, plan, _history = world

    with pytest.raises(ClearanceHeldError, match=r"unknown HS code 9999\.99"):
        _desk(recording_parts).ship(held_request)

    assert (list(plan.reservations.items()), list(client.open.items())) == ([], [])


def test_the_undo_runs_in_reverse_order_of_the_steps(
    recording_parts: RecordingParts, held_request: BookingRequest
) -> None:
    """The slot is reserved, then the carrier booked: the carrier is cancelled first."""
    with pytest.raises(ClearanceHeldError):
        _desk(recording_parts).ship(held_request)

    assert recording_parts.log == ["cancel", "release"]


def test_a_full_sailing_books_nothing_with_the_carrier(
    world: World, coffee_request: BookingRequest
) -> None:
    """A booking made before the refusal would have used receipt 1001."""
    client, _plan, _history = world
    full = StowagePlan(Sailing("SAIL-2", "NLRTM", "SGSIN"), tiers=1)
    full.reserve(ConsignmentId("CN-0"))
    desk = BookingDesk(
        rule=per_kg,
        plan=full,
        gateway=FastlineGateway(client),
        events=Signal[HandlingEvent](),
    )

    with pytest.raises(StowageFullError, match="SAIL-2"):
        desk.ship(coffee_request)

    consignment: Consignment = coffee_request.consignment
    assert (list(client.open.items()), FastlineGateway(client).book(consignment)) == (
        [],
        "FL-1001",
    )


def test_the_next_request_takes_the_slot_a_rollback_freed(
    world: World,
    recording_parts: RecordingParts,
    held_request: BookingRequest,
    coffee_request: BookingRequest,
) -> None:
    client, plan, _history = world
    with pytest.raises(ClearanceHeldError):
        _desk(recording_parts).ship(held_request)

    shipment = BookingDesk(
        rule=per_kg,
        plan=plan,
        gateway=FastlineGateway(client),
        events=Signal[HandlingEvent](),
    ).ship(coffee_request)

    assert shipment.slot == SlotId(1, 1, 1)
