from collections.abc import Iterator

import pytest
from data_model.money import ConsignmentId
from data_model.tracking import HandlingEvent, HandlingKind, TrackingHistory


class _IterOnlyHistory:
    """Negative fixture: iterable, with no __len__ and no __bool__."""

    def __init__(self, events: tuple[HandlingEvent, ...]) -> None:
        self.events = events

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)


def test_history_is_sized_and_reiterable(history: TrackingHistory) -> None:
    assert len(history) == 3
    assert list(history) == list(history)
    assert history.events[1] in history
    absent = HandlingEvent(ConsignmentId("CN-00000001"), HandlingKind.DELIVERED, "SGSIN")
    assert absent not in history
    assert [e.kind for e in history] == [
        HandlingKind.BOOKED,
        HandlingKind.LOADED,
        HandlingKind.DEPARTED,
    ]


def test_empty_history_is_falsy_through_len() -> None:
    assert not TrackingHistory(())
    assert "__bool__" not in vars(TrackingHistory)
    assert _IterOnlyHistory(())


def test_history_is_not_subscriptable(history: TrackingHistory) -> None:
    with pytest.raises(TypeError, match="'TrackingHistory' object is not subscriptable"):
        history[0]  # type: ignore[index]
