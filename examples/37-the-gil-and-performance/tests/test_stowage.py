"""The slot reservation: forced interleavings, on either build."""

import dis
from collections.abc import Callable
from contextlib import nullcontext
from typing import TYPE_CHECKING

import pytest
from gil_and_performance.domain import ConsignmentId, SlotId
from gil_and_performance.stowage import StowagePlan

if TYPE_CHECKING:
    from conftest import _RecordingLock

    type TwoThreads = Callable[[StowagePlan], list[SlotId]]


class _Tally:
    """An attribute increment, kept only so that its bytecode can be read."""

    def __init__(self) -> None:
        self.count = 0

    def bump(self) -> None:
        self.count += 1


def test_two_threads_parked_between_read_and_write_take_the_same_slot(
    two_threads: TwoThreads, barrier_gap: Callable[[], object]
) -> None:
    plan = StowagePlan("SAILING-1", lock=nullcontext(), gap=barrier_gap)

    slots = two_threads(plan)

    assert slots == [SlotId(1, 1, 1), SlotId(1, 1, 1)]
    assert len(plan.reservations) == 1


def test_an_attribute_increment_is_a_separate_load_add_and_store() -> None:
    names = [instruction.opname for instruction in dis.get_instructions(_Tally.bump)]
    steps = [name for name in names if name in {"LOAD_ATTR", "BINARY_OP", "STORE_ATTR"}]

    assert steps == ["LOAD_ATTR", "BINARY_OP", "STORE_ATTR"]


def test_a_lock_across_read_and_write_gives_each_thread_its_own_slot(
    two_threads: TwoThreads, recording_lock: _RecordingLock
) -> None:
    plan = StowagePlan("SAILING-1", lock=recording_lock, gap=recording_lock.wait_for_second_caller)

    slots = two_threads(plan)

    assert slots == [SlotId(1, 1, 1), SlotId(1, 1, 2)]
    assert dict(plan.reservations).keys() == {SlotId(1, 1, 1), SlotId(1, 1, 2)}
    assert recording_lock.second_caller


def test_the_reservations_view_refuses_assignment() -> None:
    plan = StowagePlan("SAILING-1")
    plan.reserve(ConsignmentId("CN-1"))

    with pytest.raises(TypeError):
        plan.reservations[SlotId(1, 1, 2)] = ConsignmentId("CN-2")  # type: ignore[index]

    assert len(plan.reservations) == 1
