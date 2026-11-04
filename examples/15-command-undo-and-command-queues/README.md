# Command, undo, and command queues

Booking amendments written as frozen values, with undo and redo, a bounded history and a queue
that applies all or nothing. The chapter's thesis is that Command survives and the plain deferred
call dissolves: a deferred call is a `functools.partial`, but undo and a queue need data the call
never kept (the value an amendment replaced, an order, and values nobody can change afterwards).

## What it witnesses

Commands as values.

- `Reweigh`, `Redirect` and `SetInstructions` are frozen slotted dataclasses under
  `type Amendment = Reweigh | Redirect | SetInstructions`. They compare, hash and print by value.
  Two partials built from the same function and argument don't compare equal, and a partial has no inverse.
- `apply(request, amendment)` returns the amended request and the amendment that reverses it,
  computed from the request it actually amended. Applying the inverse restores the original.
- A `Redirect` to something that is not five uppercase letters is an `AmendmentError`.
- Adding an amendment kind that `apply` does not handle is an `[arg-type]` error at
  `assert_never`.

Undo and redo.

- `Booking` keeps an undo stack and a redo stack of inverses in `collections.deque`s. Undo then
  redo walk the history, a new amendment clears redo, and an empty stack is an `AmendmentError`.
- An inverse recorded when a command is built, not when it runs, restores a stale weight once two
  commands are queued. The bounded `deque(maxlen=...)` forgets the oldest amendment silently.
- Every `BookingRequest` is frozen, so a request kept from before the amendments is a safe
  snapshot.

Commands that share mutable data.

- Two commands built from one `dict` the caller keeps editing undo to the wrong state, and mypy
  accepts them.
- `SetInstructions.instructions` is a `frozendict[str, str]`. A `dict` argument is an `[arg-type]`
  error, item assignment is an `[index]` error and a runtime `TypeError`, and a frozen dataclass
  may default a `frozendict` without `default_factory`.

The queue.

- `submit` appends to a `deque` and `apply_pending` drains it first in, first out. The batch is
  folded on a local request, so a failing amendment leaves the request, the history and the queue
  as they were.

## Layout

- `src/command_undo/domain.py`: `ConsignmentId`, `Weight`, `Consignment`, `BookingRequest`,
  `AmendmentError`.
- `src/command_undo/amendments.py`: `Reweigh`, `Redirect`, `SetInstructions`, `Amendment`, `apply`.
- `src/command_undo/booking.py`: `Booking`.

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

`tests/test_commands.py`

- `test_amendments_compare_by_value_and_partials_do_not`: equal amendments are equal with equal hashes and a value repr; equal partials are not equal and have no `undo`.
- `test_apply_returns_the_amendment_that_reverses_it`: for each kind, applying the inverse restores the request and the inverse's inverse is the amendment.
- `test_a_redirect_needs_a_port_code`: lower case and a trailing space are refused with the code named.
- `test_a_booked_weight_must_be_positive_and_finite`: zero, negative, NaN and infinity are `ValueError`.

`tests/test_undo.py`

- `test_undo_and_redo_walk_the_history`: two amendments, two undos, two redos, with stack sizes.
- `test_a_new_amendment_clears_redo`: redo is empty and refused afterwards.
- `test_undo_or_redo_with_nothing_recorded_is_an_amendment_error`: both operations, request unchanged.
- `test_two_amendments_undone_restore_the_original_request`: equal to the starting request.
- `test_an_inverse_captured_when_queued_restores_a_stale_weight`: 120 where 130 is expected, against the inverse computed at run time.
- `test_a_bounded_history_forgets_the_oldest_amendment`: a limit of two, three amendments, the third undo refused.
- `test_a_frozen_request_is_a_safe_snapshot`: a request kept before the amendments still equals the original.

`tests/test_shared_data.py`

- `test_commands_sharing_a_mutable_mapping_undo_to_the_wrong_state`: `fragile` where `keep dry` is expected.
- `test_instructions_cannot_be_changed_after_queueing`: item assignment raises `TypeError`.
- `test_a_frozen_mapping_default_needs_no_factory`: the default is shared, and a `dict` default is refused.

`tests/test_queue.py`

- `test_queued_amendments_apply_in_order`: nothing runs until the batch does, and the inverses undo in reverse.
- `test_a_failing_batch_leaves_the_booking_unchanged`: request, undo stack, redo stack and queue are as before.
- `test_a_batch_clears_redo_and_records_one_inverse_per_amendment`: a successful batch commits its inverses.

`tests/test_static.py`

- `test_mypy_rejects_a_dict_where_frozen_instructions_belong`: `[arg-type]`.
- `test_mypy_rejects_assigning_into_frozen_instructions`: `[index]`.
- `test_mypy_reports_an_amendment_kind_missing_from_apply`: `[arg-type]` naming `Insure`.
- `test_mypy_accepts_commands_that_share_a_dict`: clean.
- `test_the_amendment_snippet_mirrors_the_source`: the snippet's classes, union and arms are the ones in `amendments.py`.
- `test_apply_ends_in_assert_never`: the source and the snippet end in `assert_never`.

Classes named with a leading underscore in the test modules are test fixtures and aren't part of
the model code.
