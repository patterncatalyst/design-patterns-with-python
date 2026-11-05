"""Fixtures. The comparison form lives here as a fixture parameter so that it runs the same
traversal table as the idiomatic code: a GoF cursor whose `__iter__` returns itself."""

from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Self, TextIO

import pytest
from iterator_protocol.domain import ConsignmentId, HandlingEvent, HandlingKind, TrackingHistory
from iterator_protocol.reading import open_utf8

CN = ConsignmentId("CN-1")
type HistoryBuilder = Callable[[Iterable[HandlingEvent]], Iterable[HandlingEvent]]

EVENTS = (
    HandlingEvent(CN, HandlingKind.BOOKED, "NLRTM"),
    HandlingEvent(CN, HandlingKind.LOADED, "SGSIN"),
    HandlingEvent(CN, HandlingKind.DEPARTED, "DEHAM"),
)


class _OneShotHistory:
    """The GoF cursor written to the protocol: an index, and `__iter__` returns itself."""

    def __init__(self, events: Iterable[HandlingEvent]) -> None:
        self._events = tuple(events)
        self._index = 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> HandlingEvent:
        if self._index >= len(self._events):
            raise StopIteration
        event = self._events[self._index]
        self._index += 1
        return event


def _filled(events: Iterable[HandlingEvent]) -> TrackingHistory:
    history = TrackingHistory()
    for event in events:
        history.record(event)
    return history


@pytest.fixture
def history() -> TrackingHistory:
    """A history of a booking, a loading and a departure at three ports."""
    return _filled(EVENTS)


@pytest.fixture
def one_shot() -> Iterable[HandlingEvent]:
    """The same three events behind a self-iterating cursor."""
    return _OneShotHistory(EVENTS)


@pytest.fixture(params=["iterable", "self-iterator"])
def history_form(
    request: pytest.FixtureRequest,
) -> Callable[[Iterable[HandlingEvent]], Iterable[HandlingEvent]]:
    """Builds the same events as a `TrackingHistory` or as a self-iterating cursor."""
    builders: dict[str, HistoryBuilder] = {
        "iterable": _filled,
        "self-iterator": _OneShotHistory,
    }
    return builders[request.param]


class _Counted:
    """A source of one shared event that records how many it has produced."""

    def __init__(self, size: int) -> None:
        self._size = size
        self.pulled = 0

    def stream(self) -> Iterator[HandlingEvent]:
        for _ in range(self._size):
            self.pulled += 1
            yield EVENTS[0]


@pytest.fixture
def counting() -> Callable[[int], _Counted]:
    return _Counted


@pytest.fixture
def write_log(tmp_path: Path) -> Callable[[list[str]], Path]:
    """Write a tracking log under `tmp_path` with the given lines."""

    def write(lines: list[str]) -> Path:
        path = tmp_path / "tracking.log"
        path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
        return path

    return write


@pytest.fixture
def tracking_log(write_log: Callable[[list[str]], Path]) -> Path:
    return write_log(["CN-1;BOOKED;NLRTM", "CN-1;LOADED;SGSIN", "CN-1;DEPARTED;DEHAM"])


class _RecordingOpener:
    """Opens with `open_utf8` and keeps every handle so a test can read `.closed`."""

    def __init__(self) -> None:
        self.handles: list[TextIO] = []

    def __call__(self, path: Path, /) -> TextIO:
        handle = open_utf8(path)
        self.handles.append(handle)
        return handle


@pytest.fixture
def recording_opener() -> Iterator[_RecordingOpener]:
    opener = _RecordingOpener()
    yield opener
    for handle in opener.handles:
        handle.close()
