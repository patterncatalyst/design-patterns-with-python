"""Tracking policy. It owns the one method it needs and imports only the domain types."""

from typing import Protocol

from isp_dip_di.domain import ConsignmentId, HandlingEvent, TrackingHistory


class TrackingGateway(Protocol):
    """What tracking needs from a carrier: the events recorded for a consignment."""

    def track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]: ...


def tracking_history(consignment_id: ConsignmentId, *, gateway: TrackingGateway) -> TrackingHistory:
    """Collect the handling events a gateway holds for one consignment."""
    return TrackingHistory(gateway.track(consignment_id))
