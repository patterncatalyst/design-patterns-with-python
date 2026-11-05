from collections.abc import Callable, Iterator
from typing import Protocol

import pytest
from iterator_protocol.domain import ConsignmentId, HandlingEvent, HandlingKind, TrackingHistory
from iterator_protocol.paging import events_of, out_of_order, page, pages

CN = ConsignmentId("CN-1")


class Counted(Protocol):
    pulled: int

    def stream(self) -> Iterator[HandlingEvent]: ...


type CountingFactory = Callable[[int], Counted]


def test_the_first_page_reads_only_one_page(counting: CountingFactory) -> None:
    source = counting(1_000_000)

    first = next(pages(source.stream(), 3))

    assert len(first) == 3
    assert source.pulled == 3


def test_an_eager_list_reads_every_event_to_get_the_first_page(counting: CountingFactory) -> None:
    source = counting(1_000_000)

    first = list(source.stream())[:3]

    assert len(first) == 3
    assert source.pulled == 1_000_000


def test_pages_keep_a_short_last_page(counting: CountingFactory) -> None:
    assert [len(p) for p in pages(counting(7).stream(), 3)] == [3, 3, 1]


def test_a_page_size_below_one_is_refused(history: TrackingHistory) -> None:
    with pytest.raises(ValueError, match="n must be at least one"):
        next(pages(history, 0))


def test_page_reads_only_up_to_the_page_it_returns(counting: CountingFactory) -> None:
    source = counting(1_000_000)

    second = page(source.stream(), 2, 3)

    assert len(second) == 3
    assert source.pulled == 6


@pytest.mark.parametrize("number", [0, -1], ids=["zero", "negative"])
def test_page_numbers_start_at_one(history: TrackingHistory, number: int) -> None:
    with pytest.raises(ValueError, match="page numbers start at 1"):
        page(history, number, 3)


def test_a_page_past_the_end_is_empty(history: TrackingHistory) -> None:
    assert page(history, 5, 3) == ()


def test_out_of_order_finds_an_event_that_steps_back_in_the_lifecycle() -> None:
    loaded = HandlingEvent(CN, HandlingKind.LOADED, "NLRTM")
    booked = HandlingEvent(CN, HandlingKind.BOOKED, "NLRTM")
    departed = HandlingEvent(CN, HandlingKind.DEPARTED, "NLRTM")

    assert list(out_of_order([loaded, booked, departed])) == [(loaded, booked)]


@pytest.mark.parametrize("count", [0, 1], ids=["none", "one"])
def test_out_of_order_is_empty_for_fewer_than_two_events(
    history: TrackingHistory, count: int
) -> None:
    events = list(history)[:count]

    assert list(out_of_order(events)) == []


def test_events_of_starts_each_history_only_when_the_last_is_done(
    counting: CountingFactory,
) -> None:
    first, second = counting(3), counting(3)
    walk = events_of([first.stream(), second.stream()])

    taken = [next(walk) for _ in range(3)]

    assert len(taken) == 3
    assert first.pulled == 3
    assert second.pulled == 0
