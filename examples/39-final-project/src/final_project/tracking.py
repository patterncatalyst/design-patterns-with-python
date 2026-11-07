"""Tracking: a signal that delivers events to subscribers, and a history that records them."""

from collections.abc import Callable

from final_project.domain import HandlingEvent

type Subscriber[E] = Callable[[E], None]


class Signal[E]:
    """Single-threaded, strong references, delivery in subscription order."""

    def __init__(self) -> None:
        self._subscribers: list[Subscriber[E]] = []

    def subscribe(self, subscriber: Subscriber[E], /) -> None:
        self._subscribers.append(subscriber)

    def publish(self, event: E, /) -> None:
        for subscriber in tuple(self._subscribers):
            subscriber(event)


class TrackingHistory:
    def __init__(self) -> None:
        self._events: list[HandlingEvent] = []

    @property
    def events(self) -> tuple[HandlingEvent, ...]:
        return tuple(self._events)

    def record(self, event: HandlingEvent, /) -> None:
        self._events.append(event)
