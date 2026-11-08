---
title: "Iterator: generators and the iterator protocol"
order: 24
layout: tutorial
sectionid: docs
part: "coordinating-traversing"
description: "A generator replaces the cursor class, but one pass or many, how much to read and who closes the source are decisions the language leaves to you."
---

## Learning objectives

By the end of this chapter you can:

- Say what Iterator dissolves into, and name the three decisions a generator leaves to you.
- Choose between an iterable and a self-iterator, and write `__iter__` as a generator so each loop gets a fresh iterator.
- Read only the part of a source you need with `batched`, `islice`, `pairwise` and `chain.from_iterable`.
- Delegate with `yield from`, type the value it returns with `Generator`, and say what `list()` drops.
- Close a reader that a consumer abandons, with `close()` or `contextlib.closing`, and say what `break` alone leaves open.

## Why this matters

A tracking history is read page by page by a display and a report. Both want the events one at a time and neither should care how the history stores them. That's the force behind Iterator, and Python resolves it inside the language: a generator function writes the cursor for you. What it leaves open are questions about the consumer's use of the source, and three of them go wrong in the obvious version.

A display wants the first page of a feed, so the code builds a list and slices it. Against a source of 1,000,000 events, the first page of three reads all 1,000,000.

A report walks a generator once to count and once to summarise. The second pass finds nothing and raises no error.

A reader of the tracking log opens its file, and a caller stops after the first event with `break`. The file is still open.

Each is a decision about one pass or many, how much to read, and who closes the source. The cursor class dissolves, and those three decisions remain.

{% include excalidraw.html name="24-iterator-generators-and-the-iterator-protocol" caption="Figure 24.1: A tracking history gives each loop a fresh iterator, so two walks both see every event. Pages are read one batch at a time, and closing a reader closes its file." %}

Read the figure from the top down. An accent box, `TrackingHistory` ("each loop gets a fresh iterator"), leads to two `__iter__` boxes, "walk one" and "walk two". Both lead to `pages` ("batched: reads one page at a time"), which leads to `page` ("islice: stops at the page it returns"). A muted, dashed box beside them reads "self-iterating cursor" and "empty on the second pass". On the right, `read_events` ("opens inside with") leads to `close()` ("file closed, reader finished"), and a muted, dashed box below reads "break alone" and "still open while named".

## The protocol, and what a generator writes for you

*Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994) wants the code that uses a collection to stay ignorant of how the collection is built, and it gets there by moving the walk into a cursor object of its own. Python builds the cursor into the language. A `for` loop asks the iterable for an iterator, and the built-in `next()` pulls from it until it raises `StopIteration`. Of `next()` the built-in functions page says "If *default* is given, it is returned if the iterator is exhausted, otherwise StopIteration is raised." Brandon Rhodes's "The Iterator Pattern" on python-patterns.guide separates the iterable, a container that hands out iterators, from the iterator that holds a position. It also points out that a file is its own iterator, so a second loop over a file resumes where the first stopped.

You rarely write the cursor. This is the whole of the history's iteration:

```python
    def __iter__(self) -> Iterator[HandlingEvent]:
        yield from self._events
```

A function with `yield` is a generator function, and calling it returns a generator iterator. The glossary says "Each yield temporarily suspends processing, remembering the execution state (including local variables and pending try-statements)." The suspended frame holds the position a cursor class would keep in a field. Schemenauer, Peters and Hetland introduced generators in PEP 255, "Simple Generators". The bucket is dissolves, as the sorting in [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) puts it.

The protocol has two sides, and the tests pin both. `test_a_traversal_visits_every_event_in_order` and `test_an_empty_history_yields_nothing` run on `TrackingHistory` and on a cursor written to the protocol by hand, and both visit the three events in order and yield nothing when empty. `test_iter_of_an_iterator_is_the_iterator_itself` shows that `iter(walk)` is `walk`, while two calls of `iter(history)` give two objects. A class with `__next__` and no `__iter__` isn't iterable: `test_a_class_with_only_next_is_not_iterable` gets a `TypeError` matching "is not iterable", and `test_mypy_refuses_a_class_with_only_next_in_a_for_loop` shows mypy refusing it with `attr-defined` and "(not iterable)". That test runs a reduced model, a class defined in the test's own snippet.

## One pass or many

The first decision is whether the object you pass around can be walked twice. The hand-written cursor in the fixtures is the comparison, a class with an index whose `__iter__` returns itself:

```python
class _OneShotHistory:
    """The GoF cursor written to the protocol: an index, and `__iter__` returns itself."""

    def __init__(self, events: Iterable[HandlingEvent]) -> None:
        self._events = tuple(events)
        self._index = 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> HandlingEvent:
        if self._index >= len(self._events):
            raise StopIteration
        event = self._events[self._index]
        self._index += 1
        return event
```

It passes the traversal table above. It differs on a second loop. The glossary says of an iterable that when it's passed to `iter()`, "This iterator is good for one pass over the set of values." An iterator is that one pass. In the glossary's words, "Attempting this with an iterator will just return the same exhausted iterator object used in the previous iteration pass, making it appear like an empty container."

The tests record both behaviours:

| Walk | `TrackingHistory` | Self-iterating cursor |
| --- | --- | --- |
| Second pass | 3 events again (`test_a_tracking_history_can_be_walked_twice`) | `[]` (`test_a_self_iterating_history_is_empty_on_the_second_pass`) |
| A loop inside a loop over 3 events | 9 pairs (`test_nested_walks_of_a_tracking_history_are_independent`) | 2 pairs (`test_a_self_iterating_history_cuts_a_nested_walk_short`) |

The nested case comes out at 2 because the inner loop drains the one cursor after the outer loop has taken its first event. Rhodes's page makes the same point with two nested loops over one list. A generator behaves like the cursor, not like the history: `test_an_exhausted_generator_looks_empty` walks `(event for event in history)` into a list of 3, then gets `[]`, and `sum` over it is 0, with no error. The history is the idiomatic form because `__iter__` is a generator, so each call makes a new one. [The data model: dunder methods as the substrate]({{ '/docs/07-the-data-model/' | relative_url }}) covers `__iter__` on a container.

mypy sees neither failure. `test_mypy_cannot_see_a_second_pass_over_an_iterator` type-checks `sum(xs), sum(xs)` over an `Iterator[int]` and finds nothing, and `test_mypy_accepts_a_self_iterating_history_as_an_iterable` shows a self-iterating class accepted where an `Iterable` is asked for. Both are reduced models, snippets in the test with no part in the example's source. Asking for a `Collection` is the annotation that says "walk me more than once": `test_mypy_refuses_a_generator_where_a_collection_is_needed`, a reduced model too, passes a generator to a `Collection[str]` parameter and gets `arg-type`. When a function walks its argument twice, annotate it `Collection` or materialise once.

## Read only what you need

The second decision is how much of the source a consumer reads. The display wants one page, and the standard library supplies the pieces. `pages` is the two-line function that [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) shows, re-declared in this example so the tests can measure it.

```python
def pages(history: Iterable[HandlingEvent], size: int) -> Iterator[tuple[HandlingEvent, ...]]:
    """Yield the history in tuples of `size`, reading one page at a time."""
    yield from batched(history, size, strict=False)


def page(history: Iterable[HandlingEvent], number: int, size: int) -> tuple[HandlingEvent, ...]:
    """Return page `number`, counted from 1, or an empty tuple past the end."""
    if number < 1:
        raise ValueError("page numbers start at 1")
    return next(islice(pages(history, size), number - 1, None), ())
```

The `itertools` page says of `batched` "The input is consumed lazily, just enough to fill a batch." The tests count what the source produced. A counting source of 1,000,000 events gives its first page of 3 after producing 3 (`test_the_first_page_reads_only_one_page`), and the eager `list(source)[:3]` produces 1,000,000 (`test_an_eager_list_reads_every_event_to_get_the_first_page`). The page says "The last batch may be shorter than n", and `test_pages_keep_a_short_last_page` gets sizes 3, 3 and 1 from 7 events. `test_a_page_size_below_one_is_refused` finds a `ValueError` matching "n must be at least one". The same page says "If strict is true, will raise a ValueError if the final batch is shorter than n." The source passes `strict=False` and no test passes `True`. A run on Python 3.15.2 of `batched(range(7), 3, strict=True)` raised `ValueError: batched(): incomplete batch`. The page marks `batched` as added in 3.12 and `strict` in 3.13.

`page` starts from `pages`, so it reads up to its page and no further. `test_page_reads_only_up_to_the_page_it_returns` takes page 2 of size 3 from the million-event source, and the source has produced 6. The `itertools` page describes `islice` as "Make an iterator that returns selected elements from the iterable." Page numbers start at 1, and `test_page_numbers_start_at_one` refuses 0 and -1 with `ValueError`. A page past the end is `()`, as `test_a_page_past_the_end_is_empty` shows. The `()` is the default given to `next()`, so an exhausted `islice` gives `()` instead of `StopIteration`.

Two more functions in the module pull lazily the same way. `out_of_order` uses `pairwise`, which the page describes as "Return successive overlapping pairs taken from the input iterable.", to find consecutive events where the second kind comes earlier in the `HandlingKind` order. `test_out_of_order_finds_an_event_that_steps_back_in_the_lifecycle` feeds loaded, booked and departed and gets the one pair, loaded then booked. With none or one event there's no pair, and `test_out_of_order_is_empty_for_fewer_than_two_events` checks both. `events_of` uses `chain.from_iterable`, which "Gets chained inputs from a single iterable argument that is evaluated lazily." In `test_events_of_starts_each_history_only_when_the_last_is_done`, after three events from the first of two counting sources, the second has produced 0.

## Delegating with yield from

A reader of the log has two jobs: parse lines into events and report how many lines it read. `events_from` parses and returns the count, and `read_events` owns the file and hands the parsing to it:

```python
def read_events(path: Path, *, opener: Opener = open_utf8) -> Generator[HandlingEvent, None, int]:
    """Open the log when the first event is asked for, and close it when the reader ends."""
    with opener(path) as lines:
        return (yield from events_from(lines))
```

PEP 380, "Syntax for Delegating to a Subgenerator" by Gregory Ewing, says "the subgenerator is allowed to return with a value, and the value is made available to the delegating generator." In `test_yield_from_hands_the_line_count_to_the_caller` a test-local delegating generator receives 3 from `events_from`. `Generator[HandlingEvent, None, int]` follows the [`typing`](https://docs.python.org/3.15/library/typing.html) docs' `Generator[YieldType, SendType, ReturnType]`: what it yields, what `send()` accepts and what it returns. `test_mypy_types_the_value_of_yield_from` assigns `yield from events_from([])` to a `str` and gets `assignment`, with the message `expression has type "int", variable has type "str"`.

`list()` discards the return value. `test_list_drops_a_generators_return_value` reads the count from the `StopIteration` that ends a manual walk, and the same reader through `list()` gives only the events. A malformed line stops the reader with its number: `test_a_malformed_line_is_refused_with_its_number` gets `TrackingLogError` matching "line 2" for a line with too few fields and for an unknown kind.

A generator that calls `next()` on an empty iterator hits the other generator rule. PEP 479, by Chris Angelico and Guido van Rossum, says "This PEP proposes a change to generators: when StopIteration is raised inside a generator, it is replaced with RuntimeError." In `test_stop_iteration_inside_a_generator_becomes_runtime_error` a test-local generator calls `next(iter(nothing))` on an empty list. The caller gets a `RuntimeError` matching "generator raised StopIteration", and its `__cause__` is the `StopIteration`. Without that rule, the generator would end quietly and look like a short feed.

## Who closes the source

The third decision belongs to whoever stops early. `read_events` holds a file, and a consumer may take one event and leave. The `with` block closes the file when the reader's frame unwinds, and the question is when that happens.

A reader never started hasn't opened anything: `test_a_reader_never_started_opens_no_file` shows an empty list of opened handles and the state `GEN_CREATED`. After the first `next()` the file is open. The built-in types page says of `close()`: "Raises a GeneratorExit exception at the point where the generator function is currently suspended (equivalent to calling `throw(GeneratorExit)`)." The exception passes through the `with`, and the file closes. `test_closing_a_reader_closes_its_file` checks the handle closed and the state `GEN_CLOSED`.

`break` doesn't call `close()`. In `test_breaking_out_of_a_loop_leaves_a_named_reader_open` the loop breaks after one event, the handle is still open and the reader is `GEN_SUSPENDED`, because the name `reader` still holds it. `contextlib.closing` gives the call a place. The documentation says "Return a context manager that closes thing upon completion of the block."

```python
    with closing(read_events(tracking_log, opener=recording_opener)) as reader:
        for _ in reader:
            break
        (handle,) = recording_opener.handles
        assert not _closed(handle)

    assert _closed(handle)
```

The reader is open inside the block and closed after it. A reader nobody names is a different case. The yield-expressions reference says "If the generator is not resumed before it is finalized (by reaching a zero reference count or by being garbage collected), the generator-iterator’s close() method will be called, allowing any pending finally clauses to execute." In `test_an_abandoned_reader_closes_its_file_when_collected` the test deletes the name and calls `gc.collect()` before asserting, because the language doesn't promise when finalisation runs. A caller that must close at a known point calls `close()` or uses `closing`.

mypy knows which iterators can be closed. `test_mypy_refuses_close_on_an_iterator` calls `close()` on `events_from([])` annotated `Iterator[HandlingEvent]` and gets `attr-defined` with `has no attribute "close"`. `test_mypy_refuses_contextlib_closing_on_an_iterator` passes it to `closing` and gets `type-var`. `test_mypy_accepts_contextlib_closing_on_a_reader` is clean for `read_events`. That's why `read_events` is annotated `Generator`. Asynchronous generators aren't part of this chapter; see [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## When not to use it

Pass the tuple when the data is already in a list that callers index or measure. Materialise once, or pass an iterable, when a result is needed twice. When a source must close at a known point, let a context manager own it and let the generator only read. A single value is a return value.

<blockquote class="ai-sidebar" markdown="1">
**Specifying an iterator.** "Make the history iterable" doesn't say whether it's walked once or many times, how much a page reads or who closes the log. State those in the prompt:

> Make `TrackingHistory.__iter__` a generator so every loop gets a fresh iterator. Write `pages(history, size)` with `itertools.batched` so the first page reads only `size` events, and `page(history, number, size)` with `islice`. Write the log reader as a generator that opens its file inside `with`, annotate it `Generator[HandlingEvent, None, int]`, and close it with `contextlib.closing` where a caller may stop early.

If the reply returns `self` from `__iter__` or builds a `list` first, ask for the test that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/24-iterator-generators-and-the-iterator-protocol
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 42 items

tests/test_laziness.py::test_the_first_page_reads_only_one_page PASSED   [  2%]
tests/test_laziness.py::test_an_eager_list_reads_every_event_to_get_the_first_page PASSED [  4%]
tests/test_laziness.py::test_pages_keep_a_short_last_page PASSED         [  7%]
tests/test_laziness.py::test_a_page_size_below_one_is_refused PASSED     [  9%]
tests/test_laziness.py::test_page_reads_only_up_to_the_page_it_returns PASSED [ 11%]
tests/test_laziness.py::test_page_numbers_start_at_one[zero] PASSED      [ 14%]
tests/test_laziness.py::test_page_numbers_start_at_one[negative] PASSED  [ 16%]
tests/test_laziness.py::test_a_page_past_the_end_is_empty PASSED         [ 19%]
tests/test_laziness.py::test_out_of_order_finds_an_event_that_steps_back_in_the_lifecycle PASSED [ 21%]
tests/test_laziness.py::test_out_of_order_is_empty_for_fewer_than_two_events[none] PASSED [ 23%]
tests/test_laziness.py::test_out_of_order_is_empty_for_fewer_than_two_events[one] PASSED [ 26%]
tests/test_laziness.py::test_events_of_starts_each_history_only_when_the_last_is_done PASSED [ 28%]
tests/test_protocol.py::test_a_traversal_visits_every_event_in_order[iterable] PASSED [ 30%]
tests/test_protocol.py::test_a_traversal_visits_every_event_in_order[self-iterator] PASSED [ 33%]
tests/test_protocol.py::test_an_empty_history_yields_nothing[iterable] PASSED [ 35%]
tests/test_protocol.py::test_an_empty_history_yields_nothing[self-iterator] PASSED [ 38%]
tests/test_protocol.py::test_a_tracking_history_can_be_walked_twice PASSED [ 40%]
tests/test_protocol.py::test_a_self_iterating_history_is_empty_on_the_second_pass PASSED [ 42%]
tests/test_protocol.py::test_nested_walks_of_a_tracking_history_are_independent PASSED [ 45%]
tests/test_protocol.py::test_a_self_iterating_history_cuts_a_nested_walk_short PASSED [ 47%]
tests/test_protocol.py::test_an_exhausted_generator_looks_empty PASSED   [ 50%]
tests/test_protocol.py::test_iter_of_an_iterator_is_the_iterator_itself PASSED [ 52%]
tests/test_protocol.py::test_a_class_with_only_next_is_not_iterable PASSED [ 54%]
tests/test_protocol.py::test_stop_iteration_inside_a_generator_becomes_runtime_error PASSED [ 57%]
tests/test_reading.py::test_read_events_parses_each_line PASSED          [ 59%]
tests/test_reading.py::test_yield_from_hands_the_line_count_to_the_caller PASSED [ 61%]
tests/test_reading.py::test_list_drops_a_generators_return_value PASSED  [ 64%]
tests/test_reading.py::test_a_malformed_line_is_refused_with_its_number[too-few-fields] PASSED [ 66%]
tests/test_reading.py::test_a_malformed_line_is_refused_with_its_number[unknown-kind] PASSED [ 69%]
tests/test_reading.py::test_a_reader_never_started_opens_no_file PASSED  [ 71%]
tests/test_reading.py::test_closing_a_reader_closes_its_file PASSED      [ 73%]
tests/test_reading.py::test_breaking_out_of_a_loop_leaves_a_named_reader_open PASSED [ 76%]
tests/test_reading.py::test_contextlib_closing_closes_the_reader_at_the_end_of_the_block PASSED [ 78%]
tests/test_reading.py::test_an_abandoned_reader_closes_its_file_when_collected PASSED [ 80%]
tests/test_static.py::test_mypy_refuses_close_on_an_iterator PASSED      [ 83%]
tests/test_static.py::test_mypy_refuses_contextlib_closing_on_an_iterator PASSED [ 85%]
tests/test_static.py::test_mypy_accepts_contextlib_closing_on_a_reader PASSED [ 88%]
tests/test_static.py::test_mypy_cannot_see_a_second_pass_over_an_iterator PASSED [ 90%]
tests/test_static.py::test_mypy_refuses_a_generator_where_a_collection_is_needed PASSED [ 92%]
tests/test_static.py::test_mypy_types_the_value_of_yield_from PASSED     [ 95%]
tests/test_static.py::test_mypy_refuses_a_class_with_only_next_in_a_for_loop PASSED [ 97%]
tests/test_static.py::test_mypy_accepts_a_self_iterating_history_as_an_iterable PASSED [100%]

============================== 42 passed in 3.54s ==============================
Success: no issues found in 9 source files
```

The suite has 37 test functions and 42 cases: 10 functions in `test_protocol.py` (12 cases), 10 in `test_laziness.py` (12), 9 in `test_reading.py` (10) and 8 in `test_static.py` (8). For how the tests and the mypy witnesses are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: store one iterator.** In a scratch copy, add `self._walk = iter(self._events)` to `TrackingHistory.__init__` and replace the `yield from` line in `__iter__` with `return self._walk`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))' | sed -E 's/0x[0-9a-f]+/0x.../g'` and then `uv run mypy --strict src tests` prints:

```text
E       AssertionError: assert [HandlingEven...port='DEHAM')] == []
tests/test_protocol.py:23: AssertionError
E       AssertionError: assert 2 == 9
tests/test_protocol.py:37: AssertionError
E       assert <list_iterator object at 0x...> is not <list_iterator object at 0x...>
tests/test_protocol.py:60: AssertionError
FAILED tests/test_protocol.py::test_a_tracking_history_can_be_walked_twice - ...
FAILED tests/test_protocol.py::test_nested_walks_of_a_tracking_history_are_independent
FAILED tests/test_protocol.py::test_iter_of_an_iterator_is_the_iterator_itself
3 failed, 39 passed in 3.41s
Success: no issues found in 9 source files
```

The history is now a self-iterating cursor. The second pass is empty, the nested walk gives 2 pairs instead of 9, and `iter(history)` returns the same object twice, which fails `test_iter_of_an_iterator_is_the_iterator_itself`. The traversal tests pass, because they walk once. mypy stays green: a method that returns an `Iterator` is type-correct.

**Experiment two: open without `with`.** In a fresh scratch copy, replace `with opener(path) as lines:` and its `return` in `read_events` with `lines = opener(path)` and `return (yield from events_from(lines))`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` prints:

```text
FAILED tests/test_reading.py::test_read_events_parses_each_line - pytest.Pyte...
FAILED tests/test_reading.py::test_list_drops_a_generators_return_value - Exc...
FAILED tests/test_reading.py::test_a_malformed_line_is_refused_with_its_number[too-few-fields]
FAILED tests/test_reading.py::test_a_malformed_line_is_refused_with_its_number[unknown-kind]
FAILED tests/test_reading.py::test_closing_a_reader_closes_its_file - Asserti...
FAILED tests/test_reading.py::test_breaking_out_of_a_loop_leaves_a_named_reader_open
FAILED tests/test_reading.py::test_contextlib_closing_closes_the_reader_at_the_end_of_the_block
FAILED tests/test_reading.py::test_an_abandoned_reader_closes_its_file_when_collected
8 failed, 34 passed in 3.47s
Success: no issues found in 9 source files
```

Four tests fail on `closed`: `close()`, `closing` and collection no longer close the file, and the `break` test fails at the `close()` that ends it. The other four fail through pytest's unraisable-exception handling. The root `filterwarnings = ["error"]` turns the `ResourceWarning` for an unclosed file into `PytestUnraisableExceptionWarning`, which reaches the tests that read a reader to the end and the two malformed-line cases. mypy stays green again, since a reader without `with` is type-correct.

## What you can do now

- Say what Iterator dissolves into: `TrackingHistory.__iter__` is a generator, and the three decisions are what remains.
- Choose one pass or many: the history walks twice and nests, and `_OneShotHistory` is empty on the second pass, as the tests and experiment one show.
- Read only what you need: `pages` and `page` read 3 and 6 events of a million, and `pairwise` and `chain.from_iterable` do the same in `out_of_order` and `events_of`.
- Delegate and type it: `read_events` and `events_from` return the line count through `yield from`, `Generator[HandlingEvent, None, int]` types it, and `list()` drops it.
- Close the source: `close()` and `contextlib.closing` close the reader, `break` alone leaves a named reader open, and experiment two shows what the `with` supplies.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Iterator. Rhodes's [The Iterator Pattern](https://python-patterns.guide/gang-of-four/iterator/) covers the iterable, the iterator and objects that are their own iterator. The [glossary](https://docs.python.org/3.15/glossary.html) defines iterable, iterator and generator iterator. The [built-in functions](https://docs.python.org/3.15/builtins/functions.html) page covers `iter` and `next`, the [built-in types](https://docs.python.org/3.15/builtins/stdtypes.html) page covers the generator methods, and the [expressions reference](https://docs.python.org/3.15/reference/expressions.html) covers yield expressions. The [`itertools`](https://docs.python.org/3.15/library/itertools.html) and [`contextlib`](https://docs.python.org/3.15/library/contextlib.html) pages cover `batched`, `islice`, `pairwise`, `chain.from_iterable` and `closing`. [PEP 255](https://peps.python.org/pep-0255/) introduced generators, [PEP 380](https://peps.python.org/pep-0380/) added `yield from`, and [PEP 479](https://peps.python.org/pep-0479/) changed `StopIteration` inside a generator. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
