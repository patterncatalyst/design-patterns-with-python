import os
import re
from pathlib import Path

import mypy.api
import pytest
from isp_dip_di.app import CarrierGateway
from isp_dip_di.booking import BookingGateway
from isp_dip_di.carriers import AircoGateway, FastlineGateway
from isp_dip_di.domain import BookingRequest, ConsignmentId, HandlingEvent, HandlingKind
from isp_dip_di.tracking import TrackingGateway, tracking_history

_SRC = Path(__file__).resolve().parents[1] / "src"


class FakeTracker:
    """A fake that implements only what tracking consumes."""

    def __init__(self, events: tuple[HandlingEvent, ...]) -> None:
        self.events = events

    def track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]:
        return self.events


def _run(snippet: str, tmp_path: Path) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
            "--config-file",
            str(config),
            "--cache-dir",
            os.devnull,
            "--no-error-summary",
            "-c",
            snippet,
        ]
    )
    return stdout, status


def _codes(stdout: str) -> set[str]:
    return set(re.findall(r"\[([a-z-]+)\]", stdout))


@pytest.mark.parametrize("adapter", [FastlineGateway, AircoGateway], ids=["FASTLINE", "AIRCO"])
def test_adapters_satisfy_every_role_without_naming_one(
    adapter: type[FastlineGateway] | type[AircoGateway], request_for: BookingRequest
) -> None:
    # The three annotated assignments are the static witness: the member's mypy run checks them.
    gateway = adapter()
    booking: BookingGateway = gateway
    tracking: TrackingGateway = gateway
    carrier: CarrierGateway = gateway

    assert not {BookingGateway, TrackingGateway, CarrierGateway} & set(type(gateway).__mro__)
    booking.book(request_for)
    assert carrier.track(request_for.consignment.id) == (
        HandlingEvent(request_for.consignment.id, HandlingKind.BOOKED, "NLRTM"),
    )
    assert tracking.track(request_for.consignment.id) == carrier.track(request_for.consignment.id)


_TRACK_ONLY = """
from isp_dip_di.app import CarrierGateway
from isp_dip_di.domain import ConsignmentId, HandlingEvent
from isp_dip_di.tracking import tracking_history


class TrackOnly:
    def track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]:
        return ()


def needs_a_whole_carrier(gateway: CarrierGateway) -> None: ...


def needs_tracking() -> None:
    tracking_history(ConsignmentId("CN-1"), gateway=TrackOnly())
"""


def test_a_fat_protocol_forces_fakes_to_stub_unused_methods(
    tmp_path: Path, request_for: BookingRequest
) -> None:
    fat = _TRACK_ONLY + "\nneeds_a_whole_carrier(TrackOnly())\n"

    stdout, status = _run(fat, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'is missing following "CarrierGateway" protocol members' in stdout
    assert "book, cancel" in stdout

    stdout, status = _run(_TRACK_ONLY, tmp_path)

    assert status == 0
    assert stdout == ""

    events = (HandlingEvent(request_for.consignment.id, HandlingKind.BOOKED, "NLRTM"),)
    history = tracking_history(request_for.consignment.id, gateway=FakeTracker(events))
    assert history.events == events
