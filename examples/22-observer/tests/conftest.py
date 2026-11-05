"""Fixtures. The plain list of callables, the comparison form, lives here as a fixture parameter
so that it runs the same delivery table as `Signal`."""

import gc
from collections.abc import Callable, Iterator
from typing import Protocol

import pytest
from observer.domain import ConsignmentId, HandlingEvent, HandlingKind
from observer.signal import Signal, Subscriber, Unsubscribe


@pytest.fixture
def event() -> Callable[[HandlingKind], HandlingEvent]:
    """Build a handling event for consignment CN-1 at Rotterdam."""

    def make(kind: HandlingKind) -> HandlingEvent:
        return HandlingEvent(ConsignmentId("CN-1"), kind, "NLRTM")

    return make


@pytest.fixture
def log() -> list[tuple[str, HandlingKind]]:
    """The shared record of who was told what, in order."""
    return []


@pytest.fixture
def labelled(
    log: list[tuple[str, HandlingKind]],
) -> Callable[[str], Subscriber[HandlingEvent]]:
    """Build a subscriber that appends its label and the event kind to the shared log."""

    def build(label: str) -> Subscriber[HandlingEvent]:
        def subscriber(event: HandlingEvent, /) -> None:
            log.append((label, event.kind))

        return subscriber

    return build


# Comparison: a plain list of callables, iterated live, with no `try` around the calls.
class _ListSignal:
    def __init__(self) -> None:
        self._subscribers: list[Subscriber[HandlingEvent]] = []

    def subscribe(self, subscriber: Subscriber[HandlingEvent], /) -> Unsubscribe:
        self._subscribers.append(subscriber)

        def remove() -> None:
            self._subscribers.remove(subscriber)

        return remove

    def publish(self, event: HandlingEvent, /) -> None:
        for subscriber in self._subscribers:
            subscriber(event)


class SignalForm(Protocol):
    def subscribe(self, subscriber: Subscriber[HandlingEvent], /) -> Unsubscribe: ...

    def publish(self, event: HandlingEvent, /) -> None: ...


@pytest.fixture
def list_signal() -> SignalForm:
    return _ListSignal()


@pytest.fixture
def signal() -> Signal[HandlingEvent]:
    return Signal()


@pytest.fixture(params=["signal", "plain-list"])
def signal_form(request: pytest.FixtureRequest) -> SignalForm:
    """A fresh signal in the parametrised form."""
    if request.param == "signal":
        return Signal[HandlingEvent]()
    return _ListSignal()


@pytest.fixture
def collector_paused() -> Iterator[None]:
    """Stop automatic collection for one test, and restore the previous state afterwards."""
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if was_enabled:
            gc.enable()
