from collections.abc import Callable, Iterable

import pytest
from iterator_protocol.domain import HandlingEvent, TrackingHistory

type HistoryBuilder = Callable[[Iterable[HandlingEvent]], Iterable[HandlingEvent]]


def test_a_traversal_visits_every_event_in_order(
    history_form: HistoryBuilder, history: TrackingHistory
) -> None:
    expected = list(history)

    assert list(history_form(expected)) == expected
    assert len(expected) == 3


def test_an_empty_history_yields_nothing(history_form: HistoryBuilder) -> None:
    assert list(history_form([])) == []


def test_a_tracking_history_can_be_walked_twice(history: TrackingHistory) -> None:
    assert list(history) == list(history)
    assert len(list(history)) == 3


def test_a_self_iterating_history_is_empty_on_the_second_pass(
    one_shot: Iterable[HandlingEvent],
) -> None:
    assert len(list(one_shot)) == 3
    assert list(one_shot) == []


def test_nested_walks_of_a_tracking_history_are_independent(history: TrackingHistory) -> None:
    pairs = [(outer, inner) for outer in history for inner in history]

    assert len(pairs) == 9


def test_a_self_iterating_history_cuts_a_nested_walk_short(
    one_shot: Iterable[HandlingEvent],
) -> None:
    pairs = [(outer, inner) for outer in one_shot for inner in one_shot]

    assert len(pairs) == 2


def test_an_exhausted_generator_looks_empty(history: TrackingHistory) -> None:
    walk = (event for event in history)

    assert len(list(walk)) == 3
    assert list(walk) == []
    assert sum(1 for _ in walk) == 0


def test_iter_of_an_iterator_is_the_iterator_itself(history: TrackingHistory) -> None:
    walk = iter(history)

    assert iter(walk) is walk
    assert iter(history) is not iter(history)


class _OnlyNext:
    def __next__(self) -> HandlingEvent:
        raise StopIteration


def test_a_class_with_only_next_is_not_iterable() -> None:
    with pytest.raises(TypeError, match="is not iterable"):
        for _ in _OnlyNext():  # type: ignore[attr-defined]
            pass


def test_stop_iteration_inside_a_generator_becomes_runtime_error() -> None:
    def leaky() -> Iterable[int]:
        nothing: list[int] = []
        yield 1
        next(iter(nothing))  # PEP 479: this StopIteration must not end the generator quietly
        yield 2

    with pytest.raises(RuntimeError, match="generator raised StopIteration") as raised:
        list(leaky())

    assert isinstance(raised.value.__cause__, StopIteration)
