"""Fixtures. The comparison form lives here as a fixture parameter so that a ``cached_property``
history runs the same table of cases as ``TrackingHistory``. The loader records every call, so a
test can count loads without a clock."""

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from functools import cached_property
from typing import Protocol

import pytest
from dynamic_attributes.tracking import (
    ConsignmentId,
    ConsignmentStatus,
    HandlingEvent,
    HandlingKind,
    TrackingHistory,
)

type Load = Callable[[ConsignmentId], Iterable[HandlingEvent]]

_STATUS_OF = {
    HandlingKind.BOOKED: ConsignmentStatus.BOOKED,
    HandlingKind.LOADED: ConsignmentStatus.LOADED,
    HandlingKind.DEPARTED: ConsignmentStatus.IN_TRANSIT,
    HandlingKind.CLEARED: ConsignmentStatus.CLEARED,
    HandlingKind.DELIVERED: ConsignmentStatus.DELIVERED,
}


def _events(consignment_id: ConsignmentId, *stops: tuple[HandlingKind, str]) -> list[HandlingEvent]:
    return [HandlingEvent(consignment_id, kind, port) for kind, port in stops]


_FEED = {
    "CN-1": [
        (HandlingKind.BOOKED, "NLRTM"),
        (HandlingKind.LOADED, "NLRTM"),
        (HandlingKind.DEPARTED, "SGSIN"),
    ],
    "CN-2": [(HandlingKind.BOOKED, "NLRTM")],
    "CN-3": [
        (HandlingKind.BOOKED, "NLRTM"),
        (HandlingKind.LOADED, "NLRTM"),
        (HandlingKind.DEPARTED, "NLRTM"),
        (HandlingKind.CLEARED, "SGSIN"),
        (HandlingKind.DELIVERED, "SGSIN"),
    ],
    "CN-4": [],
}


@dataclass(slots=True)
class RecordingLoad:
    """A loader over the feed that appends each consignment id it is asked for."""

    calls: list[ConsignmentId] = field(default_factory=list)

    def __call__(self, consignment_id: ConsignmentId) -> list[HandlingEvent]:
        self.calls.append(consignment_id)
        return _events(consignment_id, *_FEED[consignment_id])


class _CachedTrackingHistory:
    """The comparison: one ``cached_property`` for the load and a read-only property per field."""

    def __init__(self, consignment_id: ConsignmentId, load: Load) -> None:
        self.consignment_id = consignment_id
        self._load = load

    @cached_property
    def _events(self) -> tuple[HandlingEvent, ...]:
        return tuple(self._load(self.consignment_id))

    @property
    def events(self) -> tuple[HandlingEvent, ...]:
        return self._events

    @property
    def status(self) -> ConsignmentStatus | None:
        return _STATUS_OF[self._events[-1].kind] if self._events else None

    @property
    def last_port(self) -> str | None:
        return self._events[-1].port if self._events else None

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self._events)


class HistoryView(Protocol):
    """What the shared table reads from a history: four read-only names and iteration."""

    @property
    def consignment_id(self) -> ConsignmentId: ...

    @property
    def events(self) -> tuple[HandlingEvent, ...]: ...

    @property
    def status(self) -> ConsignmentStatus | None: ...

    @property
    def last_port(self) -> str | None: ...

    def __iter__(self) -> Iterator[HandlingEvent]: ...


type HistoryForm = Callable[[ConsignmentId, Load], HistoryView]


@pytest.fixture(params=["getattr", "cached_property"])
def history_form(request: pytest.FixtureRequest) -> HistoryForm:
    """``TrackingHistory`` (``__getattr__``) or ``_CachedTrackingHistory`` (``cached_property``)."""
    if request.param == "getattr":
        return TrackingHistory
    return _CachedTrackingHistory


@pytest.fixture
def recording_load() -> RecordingLoad:
    return RecordingLoad()
