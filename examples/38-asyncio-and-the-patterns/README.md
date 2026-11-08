# asyncio and the patterns

A carrier's live tracking feed, quotes from two carriers at once, an async Observer, a command
queue and a slot reservation, all on one event loop. Weights, zones and prices are illustrative,
and the carriers are in-memory stand-ins with no I/O.

## What it witnesses

`feed.py` holds `handling_events`, an async generator over a `CarrierFeed`. Breaking out of
`async for` leaves the feed open. `first_departure` reads through `contextlib.aclosing`, so it
closes the feed when it stops early. `carrier_session` is an `asynccontextmanager` that closes the
feed when its body raises and when its task is cancelled.

`quoting.py` holds the `RateSource` Protocol, whose `quote` is an `async def`. `FastlineSource` is
asynchronous. `AircoSource` adapts the blocking `AircoClient` by running each call with
`asyncio.to_thread`, so the loop keeps running while the SDK waits. `cheapest` asks every source in
a `TaskGroup` under `asyncio.timeout` and returns the lowest total. A failing source cancels the
other quote. `first_quote` calls `TaskGroup.cancel()` on the first answer.

`signal.py` holds `AsyncSignal`. `publish` runs every subscriber with `asyncio.gather(...,
return_exceptions=True)` and then raises one `BaseExceptionGroup` of the failures, which is an
`ExceptionGroup` when each failure is an `Exception`. The tests compare it with a publisher built
on a `TaskGroup`, which cancels the other subscribers when one fails.

`commands.py` holds `run_commands`, a worker over an `asyncio.Queue` of coroutine commands. It logs
a failure and carries on. It stops when the queue is shut down: `shutdown()` lets it drain the
queue first, and `shutdown(immediate=True)` drops the pending commands.

`stowage.py` holds an async `StowagePlan`. An `await` between picking a slot and storing it lets
tasks book the same slot, and an `asyncio.Lock` around the three steps gives each its own.

Four tests run mypy over small snippets: a quote returned without `await`, a quote call whose
result is dropped, and a blocking source where a `RateSource` is expected are all reported, and a
coroutine bound to `_` is not.

## Layout

- `src/asyncio_patterns/domain.py`: `ConsignmentId`, `HandlingKind`, `HandlingEvent`,
  `Consignment`, `Money`, `RateQuote`, `CarrierTimeoutError`, `SlotId`.
- `src/asyncio_patterns/feed.py`: `CarrierFeed`, `InMemoryFeed`, `handling_events`,
  `first_departure`, `carrier_session`.
- `src/asyncio_patterns/quoting.py`: `RateSource`, `FastlineSource`, `AircoClient`, `AircoSource`,
  `cheapest`, `first_quote`.
- `src/asyncio_patterns/signal.py`: `AsyncSignal`, `Subscriber`, `Unsubscribe`.
- `src/asyncio_patterns/commands.py`: `BookingCommand`, `run_commands`.
- `src/asyncio_patterns/stowage.py`: `StowagePlan`.
- `tests/conftest.py`: a guarded runner, feeds, carrier and subscriber doubles, and the
  `TaskGroup` publisher used for comparison.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

To run the tests on the free-threaded build, from the repository root:

```bash
uv python install 3.15.2t
UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages
.venv-ft/bin/python -m pytest examples/38-asyncio-and-the-patterns
```

## What the tests verify

`tests/test_await.py`

- `test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote`
- `test_a_quote_that_is_never_awaited_warns_when_it_is_collected`

`tests/test_feed.py`

- `test_the_feed_yields_events_in_order_and_closes_at_the_end`
- `test_breaking_out_of_async_for_leaves_the_feed_open`
- `test_first_departure_closes_the_feed_when_it_stops_early`
- `test_the_session_closes_the_feed_when_its_body_raises`
- `test_the_session_closes_the_feed_when_its_task_is_cancelled`

`tests/test_quoting.py`

- `test_the_cheapest_quote_wins_across_an_async_and_an_adapted_source`
- `test_the_adapter_runs_the_blocking_sdk_in_a_thread_while_the_loop_runs`
- `test_a_failing_carrier_cancels_the_other_quote`
- `test_the_first_answer_cancels_the_rest_of_the_group`
- `test_a_zero_timeout_cancels_a_quote_that_never_answers`

`tests/test_signal.py`

- `test_every_subscriber_hears_each_event_in_subscription_order`: on both publishers. Within one
  publish the order is the order the loop starts the tasks, which is first in, first out in
  CPython and not a documented guarantee.
- `test_a_failing_subscriber_does_not_stop_the_others`
- `test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails`
- `test_an_unsubscribed_subscriber_hears_nothing`: on both publishers.

`tests/test_commands.py`

- `test_queued_commands_run_in_order_and_a_failure_is_recorded`
- `test_shutdown_lets_the_worker_drain_the_queue_then_stop`
- `test_an_immediate_shutdown_drops_the_pending_commands`
- `test_a_shut_down_queue_refuses_a_new_command`

`tests/test_stowage.py`

- `test_an_await_between_read_and_write_double_books_a_slot`: five tasks parked by an
  `asyncio.Barrier` all take `SlotId(1, 1, 1)`, and one reservation remains.
- `test_an_asyncio_lock_gives_each_task_its_own_slot`

`tests/test_static.py`

- `test_mypy_reports_a_quote_returned_without_await`
- `test_mypy_reports_a_quote_call_whose_result_is_never_used`
- `test_mypy_refuses_a_blocking_source_where_a_rate_source_is_expected`
- `test_mypy_accepts_a_coroutine_bound_to_underscore`: mypy exits 0, and the runtime warns.

The tests use no mocks and no patching, and no test sleeps to wait for another task. Interleavings
are forced by events, queues and barriers, one test yields once with `asyncio.sleep(0)` as its
docstring explains, and the order within one publish rests on CPython starting tasks first in,
first out. A ten-second guard sits over the waits, and a healthy run never reaches it.
