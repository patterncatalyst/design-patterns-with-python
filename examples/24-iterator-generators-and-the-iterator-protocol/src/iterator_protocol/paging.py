"""Reading a history without reading all of it."""

from collections.abc import Iterable, Iterator
from itertools import batched, chain, islice, pairwise

from iterator_protocol.domain import HandlingEvent, HandlingKind


def pages(history: Iterable[HandlingEvent], size: int) -> Iterator[tuple[HandlingEvent, ...]]:
    """Yield the history in tuples of `size`, reading one page at a time."""
    yield from batched(history, size, strict=False)


def page(history: Iterable[HandlingEvent], number: int, size: int) -> tuple[HandlingEvent, ...]:
    """Return page `number`, counted from 1, or an empty tuple past the end."""
    if number < 1:
        raise ValueError("page numbers start at 1")
    return next(islice(pages(history, size), number - 1, None), ())


def out_of_order(
    events: Iterable[HandlingEvent],
) -> Iterator[tuple[HandlingEvent, HandlingEvent]]:
    """Yield each consecutive pair whose second event steps back in the lifecycle."""
    lifecycle = list(HandlingKind)
    for earlier, later in pairwise(events):
        if lifecycle.index(later.kind) < lifecycle.index(earlier.kind):
            yield earlier, later


def events_of(histories: Iterable[Iterable[HandlingEvent]]) -> Iterator[HandlingEvent]:
    """Yield every event of every history, starting each history when the last is done."""
    yield from chain.from_iterable(histories)
