from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

import pytest
from state_machines.domain import ConsignmentStatus, HandlingKind, TransitionError
from state_machines.table import next_status

type Legal = Sequence[tuple[Sequence[HandlingKind], ConsignmentStatus]]
type Illegal = Sequence[tuple[Sequence[HandlingKind], str]]


class _LifecycleState(Protocol):
    """Comparison fixture: the GoF form, one object per state, each deciding the next state."""

    @property
    def status(self) -> ConsignmentStatus: ...

    def on_event(self, kind: HandlingKind) -> _LifecycleState: ...


def _refuse(state: _LifecycleState, kind: HandlingKind) -> TransitionError:
    return TransitionError(f"{kind.name} not allowed when {state.status.name}")


@dataclass(frozen=True, slots=True)
class _BookedObject:
    @property
    def status(self) -> ConsignmentStatus:
        return ConsignmentStatus.BOOKED

    def on_event(self, kind: HandlingKind) -> _LifecycleState:
        if kind is HandlingKind.LOADED:
            return _LoadedObject()
        raise _refuse(self, kind)


@dataclass(frozen=True, slots=True)
class _LoadedObject:
    @property
    def status(self) -> ConsignmentStatus:
        return ConsignmentStatus.LOADED

    def on_event(self, kind: HandlingKind) -> _LifecycleState:
        if kind is HandlingKind.DEPARTED:
            return _InTransitObject()
        raise _refuse(self, kind)


@dataclass(frozen=True, slots=True)
class _InTransitObject:
    @property
    def status(self) -> ConsignmentStatus:
        return ConsignmentStatus.IN_TRANSIT

    def on_event(self, kind: HandlingKind) -> _LifecycleState:
        if kind is HandlingKind.CLEARED:
            return _ClearedObject()
        raise _refuse(self, kind)


@dataclass(frozen=True, slots=True)
class _ClearedObject:
    @property
    def status(self) -> ConsignmentStatus:
        return ConsignmentStatus.CLEARED

    def on_event(self, kind: HandlingKind) -> _LifecycleState:
        if kind is HandlingKind.DELIVERED:
            return _DeliveredObject()
        raise _refuse(self, kind)


@dataclass(frozen=True, slots=True)
class _DeliveredObject:
    @property
    def status(self) -> ConsignmentStatus:
        return ConsignmentStatus.DELIVERED

    def on_event(self, kind: HandlingKind) -> _LifecycleState:
        raise _refuse(self, kind)


def _fold_objects(kinds: Sequence[HandlingKind]) -> ConsignmentStatus:
    state: _LifecycleState = _BookedObject()
    for kind in kinds:
        state = state.on_event(kind)
    return state.status


def test_state_objects_pass_the_same_lifecycle_table(
    legal_histories: Legal, illegal_histories: Illegal
) -> None:
    for kinds, expected in legal_histories:
        assert _fold_objects(kinds) is expected
    for kinds, message in illegal_histories:
        with pytest.raises(TransitionError) as caught:
            _fold_objects(kinds)
        assert str(caught.value) == message


def test_state_objects_agree_with_the_transition_table() -> None:
    objects: dict[ConsignmentStatus, Callable[[], _LifecycleState]] = {
        ConsignmentStatus.BOOKED: _BookedObject,
        ConsignmentStatus.LOADED: _LoadedObject,
        ConsignmentStatus.IN_TRANSIT: _InTransitObject,
        ConsignmentStatus.CLEARED: _ClearedObject,
        ConsignmentStatus.DELIVERED: _DeliveredObject,
    }
    for status, make in objects.items():
        for kind in HandlingKind:
            try:
                expected = next_status(status, kind)
            except TransitionError:
                with pytest.raises(TransitionError):
                    make().on_event(kind)
            else:
                assert make().on_event(kind).status is expected
