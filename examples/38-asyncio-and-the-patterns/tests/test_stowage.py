"""An await between reading a slot and storing it lets another task read the same slot."""

import asyncio
from contextlib import nullcontext
from typing import TYPE_CHECKING

from asyncio_patterns.domain import ConsignmentId, SlotId
from asyncio_patterns.stowage import StowagePlan

if TYPE_CHECKING:
    from conftest import Runner

TASKS = 5
IDS = [ConsignmentId(f"CN-{number}") for number in range(1, TASKS + 1)]


def test_an_await_between_read_and_write_double_books_a_slot(run: Runner) -> None:
    plan = StowagePlan("MV-ORION", lock=nullcontext())
    barrier = asyncio.Barrier(TASKS)  # every task has read the slot before any stores it

    async def main() -> list[SlotId]:
        return list(
            await asyncio.gather(*(plan.reserve(consignment, barrier.wait) for consignment in IDS))
        )

    slots = run(main())

    assert (slots, len(plan.reservations)) == ([SlotId(1, 1, 1)] * TASKS, 1)


def test_an_asyncio_lock_gives_each_task_its_own_slot(run: Runner) -> None:
    """The sleep(0) yields to the loop inside the lock. Without the lock the tasks would all read
    before any stored, which rests on the loop starting tasks first in, first out: a CPython
    detail, and the reason the double booking above uses a barrier."""
    plan = StowagePlan("MV-ORION")

    async def main() -> list[SlotId]:
        return sorted(
            await asyncio.gather(*(plan.reserve(consignment, _yield) for consignment in IDS))
        )

    slots = run(main())

    assert (slots, len(plan.reservations)) == (
        [SlotId(1, 1, tier) for tier in range(1, TASKS + 1)],
        TASKS,
    )


async def _yield() -> None:
    await asyncio.sleep(0)
