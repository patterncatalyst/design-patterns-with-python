"""When the tracking event is published: after the commit, or eagerly (the comparison form)."""

from typing import TYPE_CHECKING

import pytest
from final_project.carriers import FastlineGateway
from final_project.clearance import ClearanceHeldError
from final_project.domain import (
    BookingRequest,
    ConsignmentId,
    HandlingEvent,
    HandlingKind,
)
from final_project.rating import per_kg
from final_project.tracking import Signal

if TYPE_CHECKING:
    from conftest import DeskFactory, World


@pytest.mark.parametrize("publish_form", ["after-commit"], indirect=True)
def test_a_held_booking_publishes_no_tracking_event(
    publish_form: DeskFactory, world: World, held_request: BookingRequest
) -> None:
    client, plan, history = world
    events = Signal[HandlingEvent]()
    events.subscribe(history.record)
    desk = publish_form(rule=per_kg, plan=plan, gateway=FastlineGateway(client), events=events)

    with pytest.raises(ClearanceHeldError):
        desk.ship(held_request)

    assert history.events == ()


@pytest.mark.parametrize("publish_form", ["eager"], indirect=True)
def test_an_eager_publisher_reports_a_booking_that_was_rolled_back(
    publish_form: DeskFactory, world: World, held_request: BookingRequest
) -> None:
    client, plan, history = world
    events = Signal[HandlingEvent]()
    events.subscribe(history.record)
    desk = publish_form(rule=per_kg, plan=plan, gateway=FastlineGateway(client), events=events)

    with pytest.raises(ClearanceHeldError):
        desk.ship(held_request)

    booked = HandlingEvent(ConsignmentId("CN-2"), HandlingKind.BOOKED, "NLRTM")
    assert (history.events, list(client.open.items())) == ((booked,), [])
