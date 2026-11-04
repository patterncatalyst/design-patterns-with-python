"""In-memory carrier adapters. They import only the domain and name no Protocol."""

from isp_dip_di.domain import BookingRequest, ConsignmentId, HandlingEvent, HandlingKind


class FastlineGateway:
    """The FASTLINE carrier, held in memory."""

    def __init__(self) -> None:
        self._events: dict[ConsignmentId, tuple[HandlingEvent, ...]] = {}

    def book(self, request: BookingRequest, /) -> str:
        consignment = request.consignment
        self._events[consignment.id] = (
            HandlingEvent(consignment.id, HandlingKind.BOOKED, consignment.origin),
        )
        return f"FASTLINE:{consignment.id}"

    def track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]:
        return self._events.get(consignment_id, ())

    def cancel(self, reference: str, /) -> None:
        self._events.pop(ConsignmentId(reference.removeprefix("FASTLINE:")), None)


class AircoGateway:
    """The AIRCO carrier, held in memory."""

    def __init__(self) -> None:
        self._events: dict[ConsignmentId, tuple[HandlingEvent, ...]] = {}

    def book(self, request: BookingRequest, /) -> str:
        consignment = request.consignment
        self._events[consignment.id] = (
            HandlingEvent(consignment.id, HandlingKind.BOOKED, consignment.origin),
        )
        return f"AIRCO:{consignment.id}"

    def track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]:
        return self._events.get(consignment_id, ())

    def cancel(self, reference: str, /) -> None:
        self._events.pop(ConsignmentId(reference.removeprefix("AIRCO:")), None)
