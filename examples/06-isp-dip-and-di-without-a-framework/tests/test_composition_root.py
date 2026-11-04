from functools import partial

import pytest
from isp_dip_di.app import GATEWAYS, build_app
from isp_dip_di.booking import BookingService
from isp_dip_di.domain import (
    BookingRequest,
    ConsignmentId,
    HandlingEvent,
    HandlingKind,
)
from isp_dip_di.tracking import tracking_history


class FakeCarrier:
    """A fake with all three methods, so it can stand in for a whole carrier."""

    def __init__(self) -> None:
        self.booked: list[BookingRequest] = []

    def book(self, request: BookingRequest, /) -> str:
        self.booked.append(request)
        return "FAKE:1"

    def track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]:
        return ()

    def cancel(self, reference: str, /) -> None:
        return None


def test_build_app_shares_one_gateway_between_booking_and_tracking(records: list[str]) -> None:
    app = build_app("FASTLINE", audit=records.append)

    assert isinstance(app.track, partial)
    assert app.booking.gateway is app.track.keywords["gateway"]


def test_partial_injects_a_collaborator_into_a_function(
    request_for: BookingRequest, records: list[str]
) -> None:
    app = build_app("AIRCO", audit=records.append)

    assert isinstance(app.track, partial)
    assert app.track.func is tracking_history

    app.booking.book(request_for)

    assert list(app.track(request_for.consignment.id)) == [
        HandlingEvent(request_for.consignment.id, HandlingKind.BOOKED, "NLRTM")
    ]


def test_swapping_the_carrier_changes_no_consumer(
    request_for: BookingRequest, records: list[str]
) -> None:
    apps = {code: build_app(code, audit=records.append) for code in ("FASTLINE", "AIRCO")}

    references = {code: app.booking.book(request_for) for code, app in apps.items()}

    assert references == {
        "FASTLINE": f"FASTLINE:{request_for.consignment.id}",
        "AIRCO": f"AIRCO:{request_for.consignment.id}",
    }
    for app in apps.values():
        assert type(app.booking) is BookingService
        assert isinstance(app.track, partial)
        assert app.track.func is tracking_history


def test_composition_root_accepts_a_substitute_without_patching(
    request_for: BookingRequest, records: list[str]
) -> None:
    before = dict(GATEWAYS)

    app = build_app("FASTLINE", audit=records.append, gateways={"FASTLINE": FakeCarrier})
    reference = app.booking.book(request_for)

    assert isinstance(app.booking.gateway, FakeCarrier)
    assert reference == "FAKE:1"
    assert app.booking.gateway.booked == [request_for]
    assert dict(GATEWAYS) == before


def test_unknown_carrier_fails_at_the_composition_root(records: list[str]) -> None:
    with pytest.raises(ValueError, match="NOSUCH"):
        build_app("NOSUCH", audit=records.append)
