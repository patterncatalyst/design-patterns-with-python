from collections import deque
from collections.abc import Callable, Sequence
from dataclasses import FrozenInstanceError, dataclass
from itertools import product

import pytest
from state_machines.domain import (
    ConsignmentId,
    ConsignmentStatus,
    HandlingEvent,
    HandlingKind,
    TransitionError,
)
from state_machines.states import (
    Booked,
    Cleared,
    ConsignmentState,
    Delivered,
    InTransit,
    Loaded,
    apply_event,
    status_of,
    track,
)
from state_machines.table import TRANSITIONS, next_status

type Fold = Callable[[Sequence[HandlingKind]], ConsignmentStatus]
type Legal = Sequence[tuple[Sequence[HandlingKind], ConsignmentStatus]]
type Illegal = Sequence[tuple[Sequence[HandlingKind], str]]

CONSIGNMENT = ConsignmentId("CN-00000014")


@dataclass
class _TrackedConsignment:
    """Negative fixture: a mutable status field that any caller can set."""

    status: ConsignmentStatus


def test_the_lifecycle_runs_booked_to_delivered(forms: Fold, legal_histories: Legal) -> None:
    for kinds, expected in legal_histories:
        assert forms(kinds) is expected


def test_an_illegal_event_is_a_transition_error(forms: Fold, illegal_histories: Illegal) -> None:
    for kinds, message in illegal_histories:
        with pytest.raises(TransitionError) as caught:
            forms(kinds)
        assert str(caught.value) == message


def test_delivered_is_terminal(forms: Fold) -> None:
    delivered = [
        HandlingKind.LOADED,
        HandlingKind.DEPARTED,
        HandlingKind.CLEARED,
        HandlingKind.DELIVERED,
    ]
    assert forms(delivered) is ConsignmentStatus.DELIVERED
    for kind in HandlingKind:
        with pytest.raises(TransitionError, match=f"{kind.name} not allowed when DELIVERED"):
            forms([*delivered, kind])


def _by_table(status: ConsignmentStatus, kind: HandlingKind) -> ConsignmentStatus | str:
    try:
        return next_status(status, kind)
    except TransitionError as error:
        return str(error)


def _by_match(state: ConsignmentState, event: HandlingEvent) -> ConsignmentStatus | str:
    try:
        return status_of(apply_event(state, event))
    except TransitionError as error:
        return str(error)


def test_the_two_forms_agree_on_every_status_and_event(
    sample_states: frozendict[ConsignmentStatus, ConsignmentState],
) -> None:
    for status, kind in product(ConsignmentStatus, HandlingKind):
        event = HandlingEvent(CONSIGNMENT, kind, "NLRTM")
        assert _by_match(sample_states[status], event) == _by_table(status, kind)


def test_every_status_is_reachable_from_booked() -> None:
    reached = {ConsignmentStatus.BOOKED}
    frontier = deque(reached)
    while frontier:
        status = frontier.popleft()
        for (source, _kind), target in TRANSITIONS.items():
            if source is status and target not in reached:
                reached.add(target)
                frontier.append(target)
    assert reached == set(ConsignmentStatus)


def test_the_transition_table_is_read_only() -> None:
    key = (ConsignmentStatus.DELIVERED, HandlingKind.BOOKED)
    with pytest.raises(TypeError, match="does not support item assignment"):
        TRANSITIONS[key] = ConsignmentStatus.BOOKED  # type: ignore[index]
    assert key not in TRANSITIONS
    assert not isinstance(TRANSITIONS, dict)


def test_an_event_for_another_consignment_is_refused() -> None:
    foreign = HandlingEvent(ConsignmentId("CN-00000099"), HandlingKind.LOADED, "NLRTM")
    with pytest.raises(TransitionError, match="CN-00000099 in the history of CN-00000014"):
        track(CONSIGNMENT, [foreign], start=Booked("NLRTM"))


def test_track_folds_a_history_into_the_final_state() -> None:
    events = [
        HandlingEvent(CONSIGNMENT, HandlingKind.LOADED, "NLRTM"),
        HandlingEvent(CONSIGNMENT, HandlingKind.DEPARTED, "NLRTM"),
        HandlingEvent(CONSIGNMENT, HandlingKind.CLEARED, "SGSIN"),
        HandlingEvent(CONSIGNMENT, HandlingKind.DELIVERED, "SGSIN"),
    ]
    assert track(CONSIGNMENT, events, start=Booked("NLRTM")) == Delivered("SGSIN")
    assert track(CONSIGNMENT, events[:3], start=Booked("NLRTM")) == Cleared("SGSIN")


def test_a_state_keeps_the_location_of_the_event_that_produced_it() -> None:
    loaded = apply_event(Booked("NLRTM"), HandlingEvent(CONSIGNMENT, HandlingKind.LOADED, "DEHAM"))
    assert loaded == Loaded("DEHAM")
    departed = apply_event(loaded, HandlingEvent(CONSIGNMENT, HandlingKind.DEPARTED, "DEHAM"))
    assert departed == InTransit(departed_from="DEHAM", days_sailed=0, delay_days=0)


def test_each_state_carries_only_its_own_data() -> None:
    sailing = InTransit("NLRTM")
    assert sailing.delay_days == 0
    assert not hasattr(Delivered("SGSIN"), "delay_days")
    with pytest.raises(FrozenInstanceError):
        sailing.delay_days = 1  # type: ignore[misc]


def test_every_state_and_event_is_frozen() -> None:
    values: list[tuple[object, str]] = [
        (Booked("NLRTM"), "origin"),
        (Loaded("NLRTM"), "port"),
        (InTransit("NLRTM"), "departed_from"),
        (Cleared("SGSIN"), "port"),
        (Delivered("SGSIN"), "port"),
        (HandlingEvent(CONSIGNMENT, HandlingKind.LOADED, "NLRTM"), "location"),
    ]
    for value, field in values:
        with pytest.raises(FrozenInstanceError):
            setattr(value, field, "XXXXX")


def test_a_transition_error_hides_the_key_error() -> None:
    with pytest.raises(TransitionError) as caught:
        next_status(ConsignmentStatus.BOOKED, HandlingKind.DEPARTED)
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__


def test_a_status_field_accepts_an_illegal_transition() -> None:
    tracked = _TrackedConsignment(ConsignmentStatus.DELIVERED)
    tracked.status = ConsignmentStatus.BOOKED
    assert tracked.status is ConsignmentStatus.BOOKED
