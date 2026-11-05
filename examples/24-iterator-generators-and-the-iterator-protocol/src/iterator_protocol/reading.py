"""Reading a tracking log: one `CN-1;LOADED;NLRTM` line per handling event."""

from collections.abc import Callable, Generator, Iterable
from pathlib import Path
from typing import TextIO

from iterator_protocol.domain import ConsignmentId, HandlingEvent, HandlingKind

type Opener = Callable[[Path], TextIO]


class TrackingLogError(ValueError):
    """A line of the tracking log could not be read."""


def open_utf8(path: Path, /) -> TextIO:
    return path.open(encoding="utf-8")


def events_from(lines: Iterable[str]) -> Generator[HandlingEvent, None, int]:
    """Parse lines into events and return how many lines were read."""
    count = 0
    for number, line in enumerate(lines, start=1):
        fields = line.rstrip("\n").split(";")
        if len(fields) != 3:
            raise TrackingLogError(f"line {number}: expected 3 fields, found {len(fields)}")
        consignment, kind, port = fields
        try:
            handling = HandlingKind[kind]
        except KeyError:
            raise TrackingLogError(f"line {number}: unknown kind {kind!r}") from None
        yield HandlingEvent(ConsignmentId(consignment), handling, port)
        count = number
    return count


def read_events(path: Path, *, opener: Opener = open_utf8) -> Generator[HandlingEvent, None, int]:
    """Open the log when the first event is asked for, and close it when the reader ends."""
    with opener(path) as lines:
        return (yield from events_from(lines))
