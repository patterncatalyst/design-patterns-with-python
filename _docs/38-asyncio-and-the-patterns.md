---
title: "asyncio and the patterns"
order: 38
layout: tutorial
sectionid: docs
part: "concurrency"
description: "How six patterns change when an await is a switch point: a feed closed through aclosing, a session that survives cancellation, quotes in a task group, an async Observer and a command queue that shuts down."
---

## Learning objectives

By the end of this chapter you can:

- Say what an `await` changes, and what mypy and the runtime each report when one is missing.
- Write a carrier feed as an async generator and close it with `aclosing`.
- Write a carrier session that closes the feed when its body raises or its task is cancelled.
- Quote carriers through an async Protocol, adapt a blocking SDK, and stop the group on a failure, a first answer or a timeout.
- Publish to async subscribers, queue coroutine commands and shut the queue down.
- Protect a read-modify-write that spans an `await`.

## Why this matters

Tracking events arrive from a carrier's live feed, and quotes come from two carriers at once. Both are waiting on something outside the process, which is the case asyncio is for. The patterns that handle them keep their intent under asyncio: a feed is still iterated, a session still closes what it opened, a signal still tells its subscribers. What moves is their edges. Another task on the loop can run only where the running one awaits or returns, a coroutine has to be awaited to produce anything, and cancellation arrives as an exception that cleanup has to survive.

The first edge is the easiest to hit. `FastlineSource().quote(consignment)` is a coroutine and not a `RateQuote` until something awaits it (`test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote`). A quote that is assigned and never awaited doesn't fail where it was written. The runtime warns when the coroutine is collected (`test_a_quote_that_is_never_awaited_warns_when_it_is_collected`), and mypy reports the cases it can see (`test_mypy_reports_a_quote_returned_without_await`).

{% include excalidraw.html name="38-asyncio-and-the-patterns" caption="Figure 38.1: A carrier session closes its feed when its body ends, subscribers run under gather, quotes run in a task group and commands drain from a queue. An await is a point where another task can run, and cancellation still closes the feed." %}

Read the figure from the top left. An accent box, `carrier_session` ("open the feed; close it when the body ends"), stands above `handling_events` ("an async generator over the feed"), with no arrow between them. Below, `AsyncSignal.publish` ("gather runs the subscribers; failures raise as a group") has a dashed arrow to a dashed box, `_TaskGroupSignal` ("one failing subscriber cancels the rest"). In a column on the right, `cheapest` ("TaskGroup over RateSource", "AircoSource runs the SDK in a thread") and `run_commands` ("a Queue until shutdown") stand without arrows. A bar across the bottom reads "an await is where another task can run" and "cancellation still closes the feed".

## What an await changes

Calling a coroutine function builds a coroutine and runs none of it. mypy knows the type, and reports a quote returned where a `RateQuote` is declared. This is the output of the snippet that `test_mypy_reports_a_quote_returned_without_await` type-checks, run through the test's own helper:

```text
<string>:6: error: Incompatible return value type (got "Coroutine[Any, Any, RateQuote]", expected "RateQuote")  [return-value]
<string>:6: note: Maybe you forgot to use "await"?
```

A call whose result is dropped gets `[unused-coroutine]` (`test_mypy_reports_a_quote_call_whose_result_is_never_used`). Adding the `await` empties both lists. `_ = source.quote(consignment)` is accepted under `--strict`, so for that form the runtime warning is the check that remains (`test_mypy_accepts_a_coroutine_bound_to_underscore` asserts both halves). The [Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html) page shows the warning's wording as `RuntimeWarning: coroutine 'test' was never awaited`, and the test matches it for `FastlineSource.quote`.

The warning is raised while the coroutine is being finalised, which is after the code that dropped it has moved on. A scratch test on Python 3.15.2 that called `source.quote(...)` and discarded the result failed under the repository's `filterwarnings = ["error"]` with `PytestUnraisableExceptionWarning: Exception ignored while finalizing coroutine`. A dropped task is a related slip: the [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) page says "The event loop only keeps weak references to tasks.", and ruff's [RUF006](https://docs.astral.sh/ruff/rules/asyncio-dangling-task/) "Checks for asyncio.create_task and asyncio.ensure_future calls that do not store a reference to the returned result."

The second edge is the switch point. The Developing with asyncio page says: "While a Task is running in the event loop, no other Tasks can run in the same thread." It continues: "When a Task executes an await expression, the running Task gets suspended, and the event loop executes the next Task." A read-modify-write that spans an `await` can therefore interleave with another task's. `StowagePlan.reserve` picks a slot from the size of its reservations, awaits a `confirm` callback, then stores. With no lock and an `asyncio.Barrier` as `confirm`, five tasks all read before any stores, so five calls return `SlotId(1, 1, 1)` and one reservation remains (`test_an_await_between_read_and_write_double_books_a_slot`). The default `asyncio.Lock` around the three steps gives tiers 1 to 5 (`test_an_asyncio_lock_gives_each_task_its_own_slot`). Removing `await confirm()` makes the double booking test fail: without a suspension point, each task finishes `reserve` before the next starts. For threads, see [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}).

Each pattern below has a bucket and one new rule.

| Pattern | Bucket under asyncio | The rule that is new | Test |
| --- | --- | --- | --- |
| Iterator | Dissolves into an async generator | Leaving `async for` early doesn't close it; `aclosing` does | `test_breaking_out_of_async_for_leaves_the_feed_open`, `test_first_departure_closes_the_feed_when_it_stops_early` |
| Context manager | Survives as `asynccontextmanager` | Cancellation still runs the cleanup | `test_the_session_closes_the_feed_when_its_task_is_cancelled` |
| Strategy | Dissolves into an async method | The type now says awaitable | `test_mypy_refuses_a_blocking_source_where_a_rate_source_is_expected` |
| Adapter | Survives | A blocking SDK needs a thread | `test_the_adapter_runs_the_blocking_sdk_in_a_thread_while_the_loop_runs` |
| Observer | Survives | `gather` with `return_exceptions`, not a task group | `test_a_failing_subscriber_does_not_stop_the_others` |
| Command | Survives | Queue shutdown replaces the sentinel | `test_shutdown_lets_the_worker_drain_the_queue_then_stop` |

## Iterator: the carrier's live feed

A carrier pushes handling events for a consignment as they happen, and the reader wants to consume them with `async for` and stop when it has what it needs. An async generator gives the same dissolution as a sync one: no iterator class, just a function with `yield`. The feed is a resource, so the generator closes it in a `finally`. [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}) covers the synchronous generator.

<!-- fmt:off -->
```python
async def handling_events(feed: CarrierFeed) -> AsyncGenerator[HandlingEvent]:
    try:
        while (event := await feed.next_event()) is not None:
            yield event
    finally:
        await feed.close()

async def first_departure(feed: CarrierFeed) -> HandlingEvent | None:
    """Return the first departure, closing the feed even though the loop stops early."""
    async with aclosing(handling_events(feed)) as events:
        async for event in events:
            if event.kind is HandlingKind.DEPARTED:
                return event
    return None
```
<!-- fmt:on -->

Reading to the end closes the feed (`test_the_feed_yields_events_in_order_and_closes_at_the_end`). Breaking out of the loop doesn't: the feed is still open when the `async for` ends, and the test closes it by calling `aclose()` (`test_breaking_out_of_async_for_leaves_the_feed_open`). The [contextlib](https://docs.python.org/3/library/contextlib.html) page says "aclosing() supports deterministic cleanup of async generators when they happen to exit early by break or an exception", which is why `first_departure` wraps the generator, and the feed is closed when it returns (`test_first_departure_closes_the_feed_when_it_stops_early`). The annotation is `AsyncGenerator`. With `AsyncIterator`, a run of `mypy --strict` over the example reports `[type-var]` at the `aclosing` call and `[attr-defined]`, `"AsyncIterator[HandlingEvent]" has no attribute "aclose"`, in the test that closes the generator by hand.

## Context manager: a session that survives cancellation

A carrier session opens a feed for the length of one job and has to close it however the job ends. That's a context manager's work, and `asynccontextmanager` writes one as a generator. The contextlib page describes it as a way to define the factory "without needing to create a class or separate __aenter__() and __aexit__() methods".

```python
@asynccontextmanager
async def carrier_session(feed: CarrierFeed) -> AsyncIterator[CarrierFeed]:
    """Hand the feed to the body and close it when the body ends, raises or is cancelled."""
    try:
        yield feed
    finally:
        await feed.close()
```

[Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) covers what release means and the order across several resources. What asyncio adds is cancellation. The asyncio tasks page says "When a task is cancelled, asyncio.CancelledError will be raised in the task at the next opportunity. It is recommended that coroutines use try/finally blocks to robustly perform clean-up logic." The `finally` does that. The feed closes when the body raises a `LookupError` (`test_the_session_closes_the_feed_when_its_body_raises`). It also closes when `asyncio.timeout(0)` cancels a body that waits on a feed that never answers, and the `TimeoutError` arrives outside the session (`test_the_session_closes_the_feed_when_its_task_is_cancelled`). A zero timeout needs no wait on a clock.

## Strategy and Adapter: quoting carriers together

Rating asks more than one carrier and takes the cheapest answer. Strategy dissolves into a method here as it does for sync code, and asyncio changes the method's type. `RateSource.quote` is an `async def`, so a source that blocks is a different type. mypy refuses one where a `RateSource` is expected, and the message names the difference, `Coroutine[Any, Any, RateQuote]` expected and `RateQuote` got (`test_mypy_refuses_a_blocking_source_where_a_rate_source_is_expected`). This is the output of the snippet that test checks:

```text
<string>:11: error: List item 0 has incompatible type "BlockingSource"; expected "RateSource"  [list-item]
<string>:11: note: Following member(s) of "BlockingSource" have conflicts:
<string>:11: note:     Expected:
<string>:11: note:         def quote(self, Consignment, /) -> Coroutine[Any, Any, RateQuote]
<string>:11: note:     Got:
<string>:11: note:         def quote(self, Consignment, /) -> RateQuote
```

The Adapter survives, because AIRCO's SDK blocks and has to be fitted to that async interface. The fit is a thread, so the loop stays free:

<!-- fmt:off -->
```python
class RateSource(Protocol):
    async def quote(self, consignment: Consignment, /) -> RateQuote: ...

class AircoSource:
    def __init__(self, client: AircoClient) -> None:
        self._client = client

    async def quote(self, consignment: Consignment, /) -> RateQuote:
        cents = await asyncio.to_thread(
            self._client.price,
            destination=consignment.zone,
            grams=int(consignment.weight_kg * 1000),
        )
        return RateQuote(consignment.id, AIRCO, _euros(cents))
```
<!-- fmt:on -->

In the test the SDK waits on a `threading.Event` that a coroutine on the loop sets, so the call returns only because the loop keeps running while the SDK waits (`test_the_adapter_runs_the_blocking_sdk_in_a_thread_while_the_loop_runs`). The asyncio tasks page gives the limit: "Due to the GIL, asyncio.to_thread() can typically only be used to make IO-bound functions non-blocking."

`cheapest` asks the sources in a `TaskGroup` under `asyncio.timeout(within)` and takes the lowest total (`test_the_cheapest_quote_wins_across_an_async_and_an_adapted_source`). Structured concurrency isn't a GoF pattern; it's the mechanism these patterns now share. The tasks page says: "The first time any of the tasks belonging to the group fails with an exception other than asyncio.CancelledError, the remaining tasks in the group are cancelled." In the test, FASTLINE fails and AIRCO is cancelled, and the failure leaves as an exception group caught with `except*` (`test_a_failing_carrier_cancels_the_other_quote`). `first_quote` wants the first answer instead, and calls `group.cancel()` when one arrives (`test_the_first_answer_cancels_the_rest_of_the_group`). [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) lists it: "Added TaskGroup.cancel to allow early termination of a task group". The tasks page describes `cancel()` as "a non-exceptional, early exit of the task group’s lifetime". A zero timeout cancels a quote that never answers (`test_a_zero_timeout_cancels_a_quote_that_never_answers`).

## Observer: every subscriber hears the event

An Observer tells its subscribers about an event and decides what happens when one fails. [Observer]({{ '/docs/22-observer/' | relative_url }}) settled that for sync code: run every subscriber, then raise the failures together. `AsyncSignal` keeps the rule, and the mechanism is `gather` with `return_exceptions=True`:

<!-- fmt:off -->
```python
    async def publish(self, event: E, /) -> None:
        results = await asyncio.gather(
            *(subscriber(event) for subscriber in self._subscribers), return_exceptions=True
        )
        failures = [result for result in results if isinstance(result, BaseException)]
        if failures:
            raise BaseExceptionGroup(f"{len(failures)} subscriber(s) failed", failures)
```
<!-- fmt:on -->

The [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) page says: "If return_exceptions is True, exceptions are treated the same as successful results, and aggregated in the result list." Subscribers hear events in subscription order on a table shared by both forms (`test_every_subscriber_hears_each_event_in_subscription_order`). Within one publish that order is the order the loop starts the tasks, which is first in, first out in CPython and not a documented guarantee. A failing subscriber doesn't stop the one beside it: the test lets the failure happen and then opens the gate of the slow subscriber, which still records its event, and the failure arrives as one `ExceptionGroup` (`test_a_failing_subscriber_does_not_stop_the_others`). Unsubscribing stops delivery (`test_an_unsubscribed_subscriber_hears_nothing`).

The comparison form is a publisher built on a `TaskGroup`, which looks tidier and breaks the rule:

<!-- fmt:off -->
```python
    @override
    async def publish(self, event: E, /) -> None:
        async with asyncio.TaskGroup() as group:
            for subscriber in self._subscribers:
                group.create_task(_deliver(subscriber, event))
```
<!-- fmt:on -->

It runs on the same table (the `publish_form` fixture has a `taskgroup` case). It cancels the slow subscriber when the failing one raises, so the slow one records nothing (`test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails`). A task group is right for quotes, where one failure makes the rest worthless, and wrong for notifications, where subscribers are independent.

## Command: a queue that shuts down

A Command packages a request so it can be queued and run later. Under asyncio the command is a coroutine function, and the queue is an `asyncio.Queue` that one worker drains. The worker and its queue have the shape that *Pattern-Oriented Software Architecture, Volume 2* names Active Object. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) covers commands and undo; what asyncio changes is how the worker stops.

<!-- fmt:off -->
```python
    while True:
        try:
            command = await queue.get()
        except asyncio.QueueShutDown:
            log.append("worker stopped")
            return
        try:
            log.append(await command())
        except Exception as error:
            log.append(f"failed: {error}")
        finally:
            queue.task_done()
```
<!-- fmt:on -->

Commands run in order, and a failing one is logged while `run_commands` carries on (`test_queued_commands_run_in_order_and_a_failure_is_recorded`). A worker that waits on `get()` needs a way to be told to stop. A `None` sentinel puts a value in the command type that the worker has to test for. `Queue.shutdown()` removes it. The [queue](https://docs.python.org/3/library/asyncio-queue.html) page says it will "Put a Queue instance into a shutdown mode." With the default `immediate=False` the worker drains what is queued and then stops (`test_shutdown_lets_the_worker_drain_the_queue_then_stop`). With `immediate=True` the pending commands are dropped (`test_an_immediate_shutdown_drops_the_pending_commands`), and the page cautions: "Use caution when using join() with immediate set to true." A shut-down queue refuses a new command with `QueueShutDown` (`test_a_shut_down_queue_refuses_a_new_command`).

## When asyncio is the wrong tool

asyncio helps when the program waits on something outside it. The asyncio documentation says, of work that doesn't wait: "Blocking (CPU-bound) code should not be called directly." Rating a large batch is CPU-bound, and [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}) is where that case is argued. A codebase with no I/O to wait on gains nothing from coroutines, and a single sequential call has no second task to overlap with.

<blockquote class="ai-sidebar" markdown="1">

**Async code with no rule for its edges.** A request to "make the carrier calls async" names no rule for the coroutine that has to be awaited, the blocking SDK or the feed that must close on cancellation. Paste a prompt that names each:

> Make `RateSource.quote` an `async def` and adapt the blocking AIRCO SDK with `asyncio.to_thread`. Run the sources in an `asyncio.TaskGroup` under `asyncio.timeout(within)`. Open the feed with `carrier_session` and read it through `contextlib.aclosing`. Stop the command worker with `Queue.shutdown()`, not a sentinel. Run `mypy --strict` and pytest with `filterwarnings = ["error"]`.

If a test awaits `asyncio.sleep` with a non-zero delay, ask which event it is waiting for.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then, from the example directory, `uv run pytest` runs 26 test functions as 28 cases, and `uv run mypy --strict src tests` checks the example. Each experiment below runs in a scratch copy of the repository: delete the copy's `.venv`, run `uv sync --locked --all-packages` from its root and check that `asyncio_patterns.__file__` points into the copy. The first closes the feed by hand in `first_departure`. In `src/asyncio_patterns/feed.py`, replace `async with aclosing(handling_events(feed)) as events:` with `events = handling_events(feed)`, and dedent the `async for` loop below it by one level. Then:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'
uv run mypy --strict src tests
```

```text
E       assert (<HandlingKin...ED: 3>, False) == (<HandlingKin...TED: 3>, True)
E         At index 1 diff: False != True
E         Use -v to get more diff
tests/test_feed.py:56: AssertionError
FAILED tests/test_feed.py::test_first_departure_closes_the_feed_when_it_stops_early
1 failed, 27 passed in 4.63s
Success: no issues found in 15 source files
```

One test fails: the departure is returned and the feed is still open. mypy exits 0, since the change moves a call and not a type. The second experiment restores `feed.py` and, in `AsyncSignal.publish` in `src/asyncio_patterns/signal.py`, removes `, return_exceptions=True`. The same two commands print:

```text
E       LookupError: history full
tests/conftest.py:135: LookupError
FAILED tests/test_signal.py::test_a_failing_subscriber_does_not_stop_the_others
1 failed, 27 passed in 4.57s
src/asyncio_patterns/signal.py:31: error: Value of type variable "_BaseExceptionT_co" of "BaseExceptionGroup" cannot be "None"  [type-var]
Found 1 error in 1 file (checked 15 source files)
```

`gather` now raises the subscriber's own `LookupError`, where the test expects one `ExceptionGroup`, and the other subscriber's result is lost. mypy exits 1 this time: without `return_exceptions=True` it types `results` as `list[None]`, and `BaseExceptionGroup` refuses a failures list of that element type. The type checker sees the change here, and the test names the behaviour it breaks. Both experiments gave identical output on a second fresh copy, apart from the duration.

## What you can do now

- Say what an `await` changes: a coroutine is a value until it is awaited, `test_mypy_reports_a_quote_returned_without_await` shows what mypy reports, `test_a_quote_that_is_never_awaited_warns_when_it_is_collected` shows what the runtime reports, and `test_an_await_between_read_and_write_double_books_a_slot` shows what a switch point costs.
- Close a feed with `aclosing`: `handling_events` closes the feed in a `finally`, and `first_departure` closes it when the loop stops early.
- Survive cancellation: `carrier_session` closes the feed, and `test_the_session_closes_the_feed_when_its_task_is_cancelled` proves it with `asyncio.timeout(0)`.
- Quote together: `RateSource` gives both carriers one async interface and `AircoSource` adapts AIRCO's blocking SDK to it, `cheapest` stops its group on a failure or a timeout, and `first_quote` calls `TaskGroup.cancel()` on the first answer.
- Publish and queue: `AsyncSignal` runs every subscriber before raising one group, and `run_commands` stops on `Queue.shutdown()`.
- Protect a read-modify-write: `StowagePlan.reserve` holds an `asyncio.Lock` across the `await`, and `test_an_asyncio_lock_gives_each_task_its_own_slot` shows five tasks taking five slots.

## For deeper coverage

The Python documentation's [coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html), [queues](https://docs.python.org/3/library/asyncio-queue.html) and [Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html) pages cover the mechanisms, [contextlib](https://docs.python.org/3/library/contextlib.html) covers `aclosing` and `asynccontextmanager`, and [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) records `TaskGroup.cancel`. *Pattern-Oriented Software Architecture, Volume 2* by Douglas Schmidt, Michael Stal, Hans Rohnert and Frank Buschmann has the Active Object pattern. Luciano Ramalho's *Fluent Python* (second edition) covers asynchronous programming in Python. Ruff's [RUF006](https://docs.astral.sh/ruff/rules/asyncio-dangling-task/) reports a task that is created and not stored. For work that burns the processor, see [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}). The books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
