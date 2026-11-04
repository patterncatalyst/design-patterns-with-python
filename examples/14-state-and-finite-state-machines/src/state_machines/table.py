"""The lifecycle as data: one read-only table of legal transitions."""

from collections.abc import Mapping

from state_machines.domain import ConsignmentStatus, HandlingKind, TransitionError

TRANSITIONS: Mapping[tuple[ConsignmentStatus, HandlingKind], ConsignmentStatus] = frozendict(
    {
        (ConsignmentStatus.BOOKED, HandlingKind.LOADED): ConsignmentStatus.LOADED,
        (ConsignmentStatus.LOADED, HandlingKind.DEPARTED): ConsignmentStatus.IN_TRANSIT,
        (ConsignmentStatus.IN_TRANSIT, HandlingKind.CLEARED): ConsignmentStatus.CLEARED,
        (ConsignmentStatus.CLEARED, HandlingKind.DELIVERED): ConsignmentStatus.DELIVERED,
    }
)


def next_status(status: ConsignmentStatus, kind: HandlingKind) -> ConsignmentStatus:
    """Return the status an event leads to, or refuse it with a domain error."""
    try:
        return TRANSITIONS[status, kind]
    except KeyError:
        raise TransitionError(f"{kind.name} not allowed when {status.name}") from None
