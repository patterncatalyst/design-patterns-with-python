import asyncio
import contextlib

import pytest
from feature_spikes.async_patterns import (
    CommandWorker,
    FailingCommand,
    FakeCarrierFeed,
    ReassignCarrier,
    Shipment,
    TrackingEvent,
    carrier_session,
    collect_statuses,
    first_failure_cancels_siblings,
    gather_order,
    interleave_with_sleep0,
    locked_across_await,
    lost_update_across_await,
    no_await_no_race,
    tracking_events,
    wait_for_never_set_event,
)


def make_feed() -> FakeCarrierFeed:
    return FakeCarrierFeed(
        [TrackingEvent("S1", status) for status in ("picked_up", "in_transit", "delivered")]
    )


def test_async_generator_yields_events_in_order_and_closes_at_exhaustion() -> None:
    async def scenario() -> tuple[list[str], bool]:
        feed = make_feed()
        statuses = [event.status async for event in tracking_events(feed)]
        return statuses, feed.closed

    assert asyncio.run(scenario()) == (["picked_up", "in_transit", "delivered"], True)


def test_async_generator_is_lazy_and_aclose_runs_cleanup() -> None:
    async def scenario() -> tuple[bool, int, bool, bool]:
        feed = make_feed()
        events = tracking_events(feed)
        first = await anext(events)
        assert first.status == "picked_up"
        before = (feed.opened, feed.pulled, feed.closed)
        await events.aclose()
        return (*before, feed.closed)

    opened, pulled, closed_before, closed_after = asyncio.run(scenario())
    assert (opened, pulled, closed_before, closed_after) == (True, 1, False, True)


def test_break_without_aclosing_leaves_cleanup_pending() -> None:
    async def scenario() -> tuple[bool, bool]:
        feed = make_feed()
        events = tracking_events(feed)
        async for _ in events:
            break
        pending = feed.closed
        await events.aclose()
        return pending, feed.closed

    assert asyncio.run(scenario()) == (False, True)


def test_aclosing_cleans_up_on_early_exit() -> None:
    async def scenario() -> tuple[list[str], bool]:
        feed = make_feed()
        return await collect_statuses(feed, limit=2), feed.closed

    assert asyncio.run(scenario()) == (["picked_up", "in_transit"], True)


def test_session_closes_the_feed_on_error() -> None:
    async def scenario() -> tuple[bool, bool]:
        feed = make_feed()
        with contextlib.suppress(RuntimeError):
            async with carrier_session(feed):
                msg = "boom"
                raise RuntimeError(msg)
        return feed.opened, feed.closed

    assert asyncio.run(scenario()) == (True, True)


def test_session_closes_the_feed_on_cancellation() -> None:
    async def scenario() -> bool:
        feed = make_feed()
        entered = asyncio.Event()

        async def hold() -> None:
            async with carrier_session(feed):
                entered.set()
                await asyncio.Event().wait()

        task = asyncio.create_task(hold())
        await entered.wait()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        return feed.closed

    assert asyncio.run(scenario())


def test_commands_run_in_queue_order_and_undo_in_reverse() -> None:
    async def scenario() -> tuple[str, str, int]:
        shipment = Shipment("S1", "alpha")
        worker = CommandWorker()
        runner = asyncio.create_task(worker.run())
        await worker.queue.put(ReassignCarrier(shipment, "beta"))
        await worker.queue.put(ReassignCarrier(shipment, "gamma"))
        await worker.queue.put(None)
        await runner
        after_run = shipment.carrier
        await worker.undo_all()
        return after_run, shipment.carrier, len(worker.history)

    assert asyncio.run(scenario()) == ("gamma", "alpha", 0)


def test_a_failing_command_is_recorded_and_the_worker_carries_on() -> None:
    async def scenario() -> tuple[str, list[str], int]:
        shipment = Shipment("S1", "alpha")
        worker = CommandWorker()
        runner = asyncio.create_task(worker.run())
        for command in (FailingCommand(), ReassignCarrier(shipment, "beta"), None):
            await worker.queue.put(command)
        await worker.queue.join()
        await runner
        return shipment.carrier, [str(e) for e in worker.errors], len(worker.history)

    assert asyncio.run(scenario()) == ("beta", ["carrier rejected the change"], 1)


def test_sleep_zero_interleaves_tasks_in_creation_order() -> None:
    assert asyncio.run(interleave_with_sleep0(3)) == ["a1", "b1", "a2", "b2", "a3", "b3"]


@pytest.mark.parametrize("finish_order", [["a", "b", "c"], ["c", "b", "a"], ["b", "c", "a"]])
def test_gather_keeps_argument_order_whatever_the_completion_order(
    finish_order: list[str],
) -> None:
    results, completed = asyncio.run(gather_order(finish_order))
    assert results == ["A", "B", "C"]
    assert completed == finish_order


def test_taskgroup_cancels_siblings_on_first_failure() -> None:
    messages, sibling_cancelled = asyncio.run(first_failure_cancels_siblings())
    assert messages == ["carrier feed dropped"]
    assert sibling_cancelled


def test_timeout_cancels_a_wait_that_can_never_finish() -> None:
    assert asyncio.run(wait_for_never_set_event())


def test_await_between_read_and_write_loses_updates() -> None:
    assert asyncio.run(lost_update_across_await(5)) == 1


def test_no_await_in_the_gap_means_no_lost_update() -> None:
    assert asyncio.run(no_await_no_race(5)) == 5


def test_asyncio_lock_restores_correctness_across_an_await() -> None:
    assert asyncio.run(locked_across_await(5)) == 5
