# Iterator: generators and the iterator protocol

A tracking history walked, paged and read from a log. The chapter's thesis is that Iterator
dissolves: a generator function, or `__iter__` written as one, replaces the cursor class. Three
decisions remain that the language doesn't make for you: whether the thing passed around can be
walked once or many times, how much of the source a caller reads, and who closes the source when the
consumer stops early. The example is synchronous. Port codes and consignment ids are illustrative,
and `HandlingEvent` is one class with a `HandlingKind` enum.

## What it witnesses

One pass or many.

- `TrackingHistory.__iter__` is a generator, so every loop gets a fresh iterator. The history walks
  twice and nests.
- `history_form` is `iterable` or `self-iterator`. The self-iterating cursor (`_OneShotHistory`, an
  index with `__iter__` returning itself) passes the same traversal table, then is empty on the
  second pass and cuts a nested walk short. Each failure has its own test.
- An exhausted generator looks empty, `iter(it) is it` for an iterator, and a class with only
  `__next__` isn't iterable.

How much to read.

- `pages(history, size)` is `itertools.batched`. The first page of a counting source of 1,000,000
  events pulls 3, and an eager list pulls all of them. `page` uses `islice` and pulls only up to its
  page. `out_of_order` uses `pairwise`, and `events_of` uses `chain.from_iterable`.

Delegation and cleanup.

- `read_events(path, *, opener=open_utf8) -> Generator[HandlingEvent, None, int]` opens inside a
  `with` block and returns the line count through `yield from events_from(lines)`. `list()` drops
  that count. A `StopIteration` leaking from `next()` inside a generator becomes `RuntimeError`.
- The test opener records each handle so tests read `.closed`. A reader never started opens no file,
  `close()` closes it, `break` leaves a named reader open, `contextlib.closing` closes it at the end
  of the block, and an abandoned reader closes when collected (the test collects explicitly, because
  the language doesn't promise when).

Static checks.

- mypy refuses `close()` and `closing()` on an `Iterator` and accepts them on the reader, types the
  value of `yield from`, and refuses a class with only `__next__` in a `for` loop. It can't see a
  second pass over an iterator and accepts the self-iterating cursor as an `Iterable`. Those and the
  `Collection` check are reduced models.

## Layout

- `src/iterator_protocol/domain.py`: `ConsignmentId`, `HandlingKind`, `HandlingEvent`, `TrackingHistory`.
- `src/iterator_protocol/paging.py`: `pages`, `page`, `out_of_order`, `events_of`.
- `src/iterator_protocol/reading.py`: `Opener`, `open_utf8`, `TrackingLogError`, `events_from`,
  `read_events`.

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

## What the tests verify

`tests/test_protocol.py`

- `test_a_traversal_visits_every_event_in_order`, `test_an_empty_history_yields_nothing`: both history forms.
- `test_a_tracking_history_can_be_walked_twice`, `test_nested_walks_of_a_tracking_history_are_independent`: nine pairs from three events.
- `test_a_self_iterating_history_is_empty_on_the_second_pass`, `test_a_self_iterating_history_cuts_a_nested_walk_short`: two pairs, not nine.
- `test_an_exhausted_generator_looks_empty`: `list` then `[]`, and `sum` 0.
- `test_iter_of_an_iterator_is_the_iterator_itself`: and a history gives a new iterator each time.
- `test_a_class_with_only_next_is_not_iterable`: `TypeError`.
- `test_stop_iteration_inside_a_generator_becomes_runtime_error`: with the `StopIteration` as cause.

`tests/test_laziness.py`

- `test_the_first_page_reads_only_one_page`: 3 events pulled.
- `test_an_eager_list_reads_every_event_to_get_the_first_page`: 1,000,000 pulled.
- `test_pages_keep_a_short_last_page`, `test_a_page_size_below_one_is_refused`.
- `test_page_reads_only_up_to_the_page_it_returns`, `test_page_numbers_start_at_one`, `test_a_page_past_the_end_is_empty`.
- `test_out_of_order_finds_an_event_that_steps_back_in_the_lifecycle`, `test_out_of_order_is_empty_for_fewer_than_two_events`.
- `test_events_of_starts_each_history_only_when_the_last_is_done`: the second source has produced nothing.

`tests/test_reading.py`

- `test_read_events_parses_each_line`, `test_a_malformed_line_is_refused_with_its_number`.
- `test_yield_from_hands_the_line_count_to_the_caller`, `test_list_drops_a_generators_return_value`.
- `test_a_reader_never_started_opens_no_file`, `test_closing_a_reader_closes_its_file`.
- `test_breaking_out_of_a_loop_leaves_a_named_reader_open`, `test_contextlib_closing_closes_the_reader_at_the_end_of_the_block`.
- `test_an_abandoned_reader_closes_its_file_when_collected`: deletes the name and collects explicitly.

`tests/test_static.py`

- `test_mypy_refuses_close_on_an_iterator`: `[attr-defined]`.
- `test_mypy_refuses_contextlib_closing_on_an_iterator`: `[type-var]`.
- `test_mypy_accepts_contextlib_closing_on_a_reader`: clean.
- `test_mypy_cannot_see_a_second_pass_over_an_iterator`: clean (a reduced model).
- `test_mypy_refuses_a_generator_where_a_collection_is_needed`: `[arg-type]` (a reduced model).
- `test_mypy_types_the_value_of_yield_from`: `[assignment]`.
- `test_mypy_refuses_a_class_with_only_next_in_a_for_loop`: `[attr-defined]` (a reduced model).
- `test_mypy_accepts_a_self_iterating_history_as_an_iterable`: clean (a reduced model).

Classes and functions named with a leading underscore in `tests/conftest.py` are test fixtures and
aren't part of the model code.
