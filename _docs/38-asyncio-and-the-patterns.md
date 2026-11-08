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

Tracking events arrive from a carrier's live feed, and quotes come from two carriers at once. Both wait on something outside the process, which is the case asyncio is for. The patterns that handle them keep their intent: a feed is still iterated, a session still closes what it opened, a signal still tells its subscribers. Their edges move:

- another task can run only where the running one awaits or returns;
- a coroutine has to be awaited to produce anything;
- cancellation arrives as an exception that cleanup has to survive.

The second edge is the easiest to hit. `FastlineSource().quote(consignment)` is a coroutine, not a `RateQuote`, until something awaits it. A quote that's assigned and never awaited doesn't fail where it was written: the runtime warns when the coroutine is collected, and mypy reports the cases it can see.

{% include excalidraw.html name="38-asyncio-and-the-patterns" described="true" caption="Figure 38.1: A carrier session closes its feed when its body ends, subscribers run under gather, quotes run in a task group and commands drain from a queue. An await is a point where another task can run, and cancellation still closes the feed." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-38-asyncio-and-the-patterns" markdown="1">
From the top left. An accent box, `carrier_session` ("open the feed; close it when the body ends"), stands above `handling_events` ("an async generator over the feed"), with no arrow between them. Below, `AsyncSignal.publish` ("gather runs the subscribers; failures raise as a group") has a dashed arrow to a dashed box, `_TaskGroupSignal` ("one failing subscriber cancels the rest"). In a column on the right, `cheapest` ("TaskGroup over RateSource", "AircoSource runs the SDK in a thread") and `run_commands` ("a Queue until shutdown") stand without arrows. A bar across the bottom reads "an await is where another task can run" and "cancellation still closes the feed".
</div>
</details>

The figure places the four async shapes side by side, each with the rule that's new under asyncio.

## What an await changes

Calling a coroutine function builds a coroutine and runs none of it. mypy knows the type, and reports a quote returned where a `RateQuote` is declared:

```text
<string>:6: error: Incompatible return value type (got "Coroutine[Any, Any, RateQuote]", expected "RateQuote")  [return-value]
<string>:6: note: Maybe you forgot to use "await"?
```

| Code | mypy `--strict` | Runtime |
| --- | --- | --- |
| `return source.quote(consignment)` from a `-> RateQuote` | `[return-value]` | |
| `source.quote(consignment)` as a statement | `[unused-coroutine]` | `RuntimeWarning: coroutine ... was never awaited` |
| `_ = source.quote(consignment)` | accepted | the warning is the only check |
| `await source.quote(consignment)` | clean | a `RateQuote` |

The [Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html) page shows the warning's wording as `RuntimeWarning: coroutine 'test' was never awaited`. It's raised while the coroutine is finalised, after the code that dropped it has moved on: a scratch test on Python 3.15.2 that called `source.quote(...)` and discarded the result failed under `filterwarnings = ["error"]` with `PytestUnraisableExceptionWarning: Exception ignored while finalizing coroutine`. A dropped task is a related slip: the [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) page says "The event loop only keeps weak references to tasks.", and ruff's [RUF006](https://docs.astral.sh/ruff/rules/asyncio-dangling-task/) "Checks for asyncio.create_task and asyncio.ensure_future calls that do not store a reference to the returned result."

The first edge is the switch point. The Developing with asyncio page says: "While a Task is running in the event loop, no other Tasks can run in the same thread." It continues: "When a Task executes an await expression, the running Task gets suspended, and the event loop executes the next Task." A read-modify-write that spans an `await` can therefore interleave with another task's. `StowagePlan.reserve` picks a slot from the size of its reservations, awaits a `confirm` callback, then stores. With no lock and an `asyncio.Barrier` as `confirm`, five tasks all read before any stores: five calls return `SlotId(1, 1, 1)` and one reservation remains. An `asyncio.Lock` around the three steps gives tiers 1 to 5. Without the `await confirm()` there's no suspension point, and each task finishes `reserve` before the next starts. For threads, see [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}).

Each pattern below has a bucket and one new rule:

| Pattern | Bucket under asyncio | The rule that is new |
| --- | --- | --- |
| Iterator | Dissolves into an async generator | Leaving `async for` early doesn't close it; `aclosing` does |
| Context manager | Survives as `asynccontextmanager` | Cancellation still runs the cleanup |
| Strategy | Dissolves into an async method | The type now says awaitable |
| Adapter | Survives | A blocking SDK needs a thread |
| Observer | Survives | `gather` with `return_exceptions`, not a task group |
| Command | Survives | Queue shutdown replaces the sentinel |

## Iterator: the carrier's live feed

A carrier pushes handling events as they happen, and the reader consumes them with `async for` and stops when it has what it needs. An async generator dissolves the iterator class as a sync one does. The feed is a resource, so the generator closes it in a `finally`. [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}) covers the synchronous generator.

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

Reading to the end closes the feed. Breaking out of the loop doesn't: the feed is still open when the `async for` ends, until something calls `aclose()`. The [contextlib](https://docs.python.org/3/library/contextlib.html) page says "aclosing() supports deterministic cleanup of async generators when they happen to exit early by break or an exception", which is why `first_departure` wraps the generator. The annotation is `AsyncGenerator`. With `AsyncIterator`, `mypy --strict` reports `[type-var]` at the `aclosing` call and `"AsyncIterator[HandlingEvent]" has no attribute "aclose"`, `[attr-defined]`, where the generator is closed by hand.

## Context manager: a session that survives cancellation

A carrier session opens a feed for one job and closes it however the job ends. `asynccontextmanager` writes that as a generator; the contextlib page describes it as a way to define the factory "without needing to create a class or separate __aenter__() and __aexit__() methods".

```python
@asynccontextmanager
async def carrier_session(feed: CarrierFeed) -> AsyncIterator[CarrierFeed]:
    """Hand the feed to the body and close it when the body ends, raises or is cancelled."""
    try:
        yield feed
    finally:
        await feed.close()
```

[Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) covers what release means and the order across several resources. asyncio adds cancellation. The asyncio tasks page says "When a task is cancelled, asyncio.CancelledError will be raised in the task at the next opportunity. It is recommended that coroutines use try/finally blocks to robustly perform clean-up logic." The feed closes when the body raises a `LookupError`. It also closes when `asyncio.timeout(0)` cancels a body that waits on a feed that never answers, and the `TimeoutError` arrives outside the session. A zero timeout needs no wait on a clock.

## Strategy and Adapter: quoting carriers together

Rating asks more than one carrier and takes the cheapest answer. Strategy dissolves into a method as it does for sync code, and asyncio changes the method's type. `RateSource.quote` is an `async def`, so a source that blocks is a different type, and mypy refuses it:

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

An SDK that waits on a `threading.Event` set by a coroutine on the loop still returns, because the loop keeps running while the SDK waits. The asyncio tasks page gives the limit: "Due to the GIL, asyncio.to_thread() can typically only be used to make IO-bound functions non-blocking."

`cheapest` asks the sources in a `TaskGroup` under `asyncio.timeout(within)` and takes the lowest total. Structured concurrency isn't a GoF pattern; it's the mechanism these patterns now share. The tasks page says: "The first time any of the tasks belonging to the group fails with an exception other than asyncio.CancelledError, the remaining tasks in the group are cancelled."

| Stop | Mechanism | Result |
| --- | --- | --- |
| A carrier fails | the group cancels the rest | FASTLINE fails, AIRCO is cancelled; an exception group, caught with `except*` |
| The first answer arrives | `first_quote` calls `group.cancel()` | the rest are cancelled, no exception |
| No answer in time | `asyncio.timeout(within)` | the quote is cancelled; `timeout(0)` does it without a clock |

[What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) lists "Added TaskGroup.cancel to allow early termination of a task group", and the tasks page describes `cancel()` as "a non-exceptional, early exit of the task group’s lifetime".

## Observer: every subscriber hears the event

An Observer tells its subscribers about an event and decides what happens when one fails. [Observer]({{ '/docs/22-observer/' | relative_url }}) settled that for sync code: run every subscriber, then raise the failures together. `AsyncSignal` keeps the rule with `gather` and `return_exceptions=True`:

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

The [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) page says: "If return_exceptions is True, exceptions are treated the same as successful results, and aggregated in the result list." Subscribers hear events in subscription order. Within one publish that's the order the loop starts the tasks, first in, first out in CPython and not a documented guarantee. A failing subscriber doesn't stop a slow one beside it, which still records its event, and the failure arrives as one `ExceptionGroup`. Unsubscribing stops delivery.

A publisher built on a `TaskGroup` looks tidier and breaks the rule:

<!-- fmt:off -->
```python
    @override
    async def publish(self, event: E, /) -> None:
        async with asyncio.TaskGroup() as group:
            for subscriber in self._subscribers:
                group.create_task(_deliver(subscriber, event))
```
<!-- fmt:on -->

On the same table of events, it cancels the slow subscriber when the failing one raises, so the slow one records nothing. A task group is right for quotes, where one failure makes the rest worthless, and wrong for notifications, where subscribers are independent.

## Command: a queue that shuts down

A Command packages a request so it can be queued and run later. Under asyncio the command is a coroutine function, and the queue is an `asyncio.Queue` that one worker drains. The worker and its queue have the shape that *Pattern-Oriented Software Architecture, Volume 2* names Active Object. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) covers commands and undo; asyncio changes how the worker stops.

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

Commands run in order, and a failing one is logged while `run_commands` carries on. A `None` sentinel would put a value in the command type that the worker has to test for; `Queue.shutdown()` removes it. The [queue](https://docs.python.org/3/library/asyncio-queue.html) page says it will "Put a Queue instance into a shutdown mode."

| Call | Effect |
| --- | --- |
| `shutdown()` (`immediate=False`) | the worker drains what's queued, then stops |
| `shutdown(immediate=True)` | pending commands are dropped |
| `put` after shutdown | raises `QueueShutDown` |

The page cautions: "Use caution when using join() with immediate set to true."

## When asyncio is the wrong tool

asyncio helps when the program waits on something outside it. Of work that doesn't wait, the asyncio documentation says: "Blocking (CPU-bound) code should not be called directly." Rating a large batch is CPU-bound, and [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}) covers that case. A codebase with no I/O to wait on gains nothing from coroutines, and a single sequential call has no second task to overlap with.

<blockquote class="ai-sidebar" markdown="1">

**Async code with no rule for its edges.** A request to "make the carrier calls async" names no rule for the coroutine that has to be awaited, the blocking SDK or the feed that must close on cancellation. Name each:

> Make `RateSource.quote` an `async def` and adapt the blocking AIRCO SDK with `asyncio.to_thread`. Run the sources in an `asyncio.TaskGroup` under `asyncio.timeout(within)`. Open the feed with `carrier_session` and read it through `contextlib.aclosing`. Stop the command worker with `Queue.shutdown()`, not a sentinel. Run `mypy --strict` and pytest with `filterwarnings = ["error"]`.

If a test awaits `asyncio.sleep` with a non-zero delay, ask which event it is waiting for.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/38-asyncio-and-the-patterns
uv run pytest -q
uv run mypy --strict src tests
```

All 28 cases pass and mypy is clean. Run each experiment in a scratch copy of the repository with its own `.venv`, and check that `asyncio_patterns.__file__` points into the copy:

- **Drop `aclosing`.** In `src/asyncio_patterns/feed.py`, replace `async with aclosing(handling_events(feed)) as events:` with `events = handling_events(feed)` and dedent the loop. One case fails: the departure is returned and the feed is still open. mypy exits 0, since the change moves a call and not a type.
- **Drop `return_exceptions`.** Restore the file and remove `, return_exceptions=True` from `AsyncSignal.publish` in `src/asyncio_patterns/signal.py`. One case fails: `gather` raises the subscriber's own `LookupError: history full` instead of one `ExceptionGroup`, and the other subscriber's result is lost. mypy exits 1 with `[type-var]`, because `results` is now `list[None]` and `BaseExceptionGroup` refuses it.

## What you can do now

- Say what an `await` changes: a coroutine is a value until awaited, mypy reports `[return-value]` and `[unused-coroutine]`, the runtime warns at collection, and a switch point can double-book a slot.
- Close a feed with `aclosing`: `handling_events` closes the feed in a `finally`, and `first_departure` closes it when the loop stops early.
- Survive cancellation: `carrier_session` closes the feed under `asyncio.timeout(0)`.
- Quote together: `RateSource` gives both carriers one async interface, `AircoSource` adapts AIRCO's blocking SDK, `cheapest` stops its group on a failure or a timeout, and `first_quote` calls `TaskGroup.cancel()` on the first answer.
- Publish and queue: `AsyncSignal` runs every subscriber before raising one group, and `run_commands` stops on `Queue.shutdown()`.
- Protect a read-modify-write: `StowagePlan.reserve` holds an `asyncio.Lock` across the `await`, and five tasks take five slots.

## For deeper coverage

The Python documentation's [coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html), [queues](https://docs.python.org/3/library/asyncio-queue.html) and [Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html) pages cover the mechanisms, [contextlib](https://docs.python.org/3/library/contextlib.html) covers `aclosing` and `asynccontextmanager`, and [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) records `TaskGroup.cancel`. *Pattern-Oriented Software Architecture, Volume 2* by Douglas Schmidt, Michael Stal, Hans Rohnert and Frank Buschmann has the Active Object pattern. Luciano Ramalho's *Fluent Python* (second edition) covers asynchronous programming in Python. Ruff's [RUF006](https://docs.astral.sh/ruff/rules/asyncio-dangling-task/) reports a task that is created and not stored. For work that burns the processor, see [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}). The books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
