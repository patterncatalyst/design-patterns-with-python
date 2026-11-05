"""A subscriber that remembers what it was told."""

from observer.domain import HandlingEvent


class TrackingHistory:
    """An entity that records the handling events of a consignment, in the order they arrive.

    It is a plain class, not a slotted one, so a signal can hold its bound methods weakly.
    """

    def __init__(self) -> None:
        self._events: list[HandlingEvent] = []

    def record(self, event: HandlingEvent, /) -> None:
        self._events.append(event)

    @property
    def events(self) -> tuple[HandlingEvent, ...]:
        return tuple(self._events)
