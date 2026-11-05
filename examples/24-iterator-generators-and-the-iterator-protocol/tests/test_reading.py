import gc
import inspect
from collections.abc import Callable, Generator, Iterator
from contextlib import closing
from pathlib import Path
from typing import Protocol, TextIO

import pytest
from iterator_protocol.domain import ConsignmentId, HandlingEvent, HandlingKind
from iterator_protocol.reading import TrackingLogError, events_from, read_events


class Recorder(Protocol):
    handles: list[TextIO]

    def __call__(self, path: Path, /) -> TextIO: ...


type LogWriter = Callable[[list[str]], Path]


def _closed(handle: TextIO) -> bool:
    # A function call keeps mypy from narrowing `handle.closed` across the close() calls.
    return handle.closed


def _drain(reader: Generator[HandlingEvent, None, int]) -> tuple[list[HandlingEvent], int]:
    """Run a reader to the end and keep the value it returns, which list() would drop."""
    events: list[HandlingEvent] = []
    while True:
        try:
            events.append(next(reader))
        except StopIteration as stop:
            return events, stop.value


def test_read_events_parses_each_line(tracking_log: Path) -> None:
    events = list(read_events(tracking_log))

    assert events == [
        HandlingEvent(ConsignmentId("CN-1"), HandlingKind.BOOKED, "NLRTM"),
        HandlingEvent(ConsignmentId("CN-1"), HandlingKind.LOADED, "SGSIN"),
        HandlingEvent(ConsignmentId("CN-1"), HandlingKind.DEPARTED, "DEHAM"),
    ]


def test_yield_from_hands_the_line_count_to_the_caller(tracking_log: Path) -> None:
    received: list[int] = []

    def delegating(lines: list[str]) -> Iterator[HandlingEvent]:
        received.append((yield from events_from(lines)))

    assert len(list(delegating(tracking_log.read_text(encoding="utf-8").splitlines()))) == 3
    assert received == [3]


def test_list_drops_a_generators_return_value(tracking_log: Path) -> None:
    events, count = _drain(read_events(tracking_log))

    assert len(events) == 3
    assert count == 3
    assert list(read_events(tracking_log)) == events


@pytest.mark.parametrize(
    "bad",
    ["CN-1;LOADED", "CN-1;TELEPORTED;NLRTM"],
    ids=["too-few-fields", "unknown-kind"],
)
def test_a_malformed_line_is_refused_with_its_number(write_log: LogWriter, bad: str) -> None:
    log = write_log(["CN-1;BOOKED;NLRTM", bad])

    with pytest.raises(TrackingLogError, match="line 2"):
        list(read_events(log))


def test_a_reader_never_started_opens_no_file(
    tracking_log: Path, recording_opener: Recorder
) -> None:
    reader = read_events(tracking_log, opener=recording_opener)

    assert recording_opener.handles == []
    assert inspect.getgeneratorstate(reader) == inspect.GEN_CREATED


def test_closing_a_reader_closes_its_file(tracking_log: Path, recording_opener: Recorder) -> None:
    reader = read_events(tracking_log, opener=recording_opener)
    next(reader)
    (handle,) = recording_opener.handles
    assert not _closed(handle)

    reader.close()

    assert _closed(handle)
    assert inspect.getgeneratorstate(reader) == inspect.GEN_CLOSED


def test_breaking_out_of_a_loop_leaves_a_named_reader_open(
    tracking_log: Path, recording_opener: Recorder
) -> None:
    reader = read_events(tracking_log, opener=recording_opener)
    for _ in reader:
        break
    (handle,) = recording_opener.handles

    # The name `reader` still holds the generator, so nothing has finalised it.
    assert not _closed(handle)
    assert inspect.getgeneratorstate(reader) == inspect.GEN_SUSPENDED

    reader.close()
    assert _closed(handle)


def test_contextlib_closing_closes_the_reader_at_the_end_of_the_block(
    tracking_log: Path, recording_opener: Recorder
) -> None:
    with closing(read_events(tracking_log, opener=recording_opener)) as reader:
        for _ in reader:
            break
        (handle,) = recording_opener.handles
        assert not _closed(handle)

    assert _closed(handle)


def test_an_abandoned_reader_closes_its_file_when_collected(
    tracking_log: Path, recording_opener: Recorder
) -> None:
    reader = read_events(tracking_log, opener=recording_opener)
    next(reader)
    (handle,) = recording_opener.handles

    del reader
    # CPython usually finalises at the last reference, and the language promises nothing,
    # so collect explicitly before asserting.
    gc.collect()

    assert _closed(handle)
