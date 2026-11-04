---
title: "Command, undo, and command queues"
order: 15
layout: tutorial
sectionid: docs
part: "selecting-varying-behavior"
description: "Command survives where undo needs data a deferred call never kept: frozen amendment values, an inverse computed when the amendment runs, undo and redo stacks and a queue that applies all or nothing."
---

## Learning objectives

By the end of this chapter you can:

- Say which part of Command dissolves into `functools.partial` and which part survives, and name what a partial lacks.
- Write amendments as frozen values and a single `match` that applies one and returns the amendment that reverses it.
- Keep undo and redo as two `deque` stacks, the undo stack bounded, and say why the inverse is read when the amendment runs.
- Explain how two commands sharing a mutable mapping undo to the wrong text, and close the gap with a `frozendict` field.
- Apply a queue of amendments all or nothing, with a failing amendment leaving the booking as it was.

## Why this matters

A booking request changes after it's made. The shipper revises the weight, redirects the consignment to another port, rewrites the handling instructions. The back office wants to queue those amendments and apply them in one go, and to step back through them when a clerk makes a mistake. Three things go wrong in the obvious versions.

Two instruction amendments are built from one dictionary that the caller keeps editing. The first says "keep dry", the caller changes the dictionary to "fragile", the second is built from it, and after one undo the instructions read "fragile" where "keep dry" was expected. mypy accepts the code.

An amendment records the old weight when it's queued. Two are queued while the weight is 120, one to 130 and one to 140. After both run, undoing the second restores 120 where 130 was expected, because the old value was read before the first one ran.

A batch of amendments fails halfway, and the booking is left with the first two applied and the third refused.

{% include excalidraw.html name="15-command-undo-and-command-queues" caption="Figure 15.1: Amendments as values on two stacks. Queued amendments are applied first in, first out, all or nothing; each application returns a new frozen request and the inverse it computed, which undo and redo move between the two stacks." %}

Read the figure from the top down. An accent box, `submit(amendment)`, feeds `pending`, a deque that is first in, first out. `apply_pending` follows, folding on a local request so that the batch is all or nothing, and it calls `apply(request, amendment)`, one match in one function. That box forks into two: `BookingRequest`, the new frozen value, and the inverse amendment, read at the moment of change. The inverse arrow runs down to `undo_stack`, a `deque(maxlen)` that forgets its oldest entry. Between `undo_stack` and `redo_stack` two arrows carry an inverse each way, labelled undo and redo. A dashed box above `redo_stack`, "new amendment clears redo", points into it.

## What dissolves and what survives

The *Design Patterns* catalogue by Gamma, Helm, Johnson and Vlissides (1994) gives Command to a request that has to outlive the moment it was made: held, passed to something else, replayed and, with enough data, reversed. The force is that a change needs an identity of its own.

The packaging of that force dissolves. A deferred call is a `functools.partial`, and [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) shows a deque of partials that change nothing until called. What the partial can't do is the rest of the force. It has no inverse, and it has no value equality, so a queue of partials can't be undone or deduplicated. [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) covers `functools.partial` itself.

`test_amendments_compare_by_value_and_partials_do_not` shows the split in one test. Two `Reweigh(kg(130))` are equal with equal hashes, and `Redirect("MYPKG")` prints as `Redirect(destination='MYPKG')`. Two partials built from the same function and the same argument compare unequal, and a partial has no `undo` attribute.

So the bucket is survives, with the deferred call dissolving. Undo, a queue and an inverse that stays correct need design. A Python shape for them is a closed set of frozen values, one function that applies a value, an undo stack with a bound, a redo stack and a queue. The classes of the original pattern, a `Command` base with `execute` and `undo`, don't appear.

## Commands as values

Each amendment is a frozen, slotted dataclass that carries only the new value. The union and `apply` are the whole model:

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True)
class Reweigh:
    """Change the declared weight."""

    weight: Weight


@dataclass(frozen=True, slots=True)
class Redirect:
    """Change the destination to another UN/LOCODE port."""

    destination: str


@dataclass(frozen=True, slots=True)
class SetInstructions:
    """Replace the handling instructions as a whole."""

    instructions: frozendict[str, str]


type Amendment = Reweigh | Redirect | SetInstructions


def apply(request: BookingRequest, amendment: Amendment) -> tuple[BookingRequest, Amendment]:
    """Return the amended request and the amendment that reverses it.

    The inverse is read from the request being amended, at the moment of the change.
    """
    match amendment:
        case Reweigh(weight):
            amended = replace(request, consignment=replace(request.consignment, weight=weight))
            return amended, Reweigh(request.consignment.weight)
        case Redirect(destination):
            if not _PORT_CODE.fullmatch(destination):
                raise AmendmentError(f"not a port code: {destination!r}")
            amended = replace(
                request, consignment=replace(request.consignment, destination=destination)
            )
            return amended, Redirect(request.consignment.destination)
        case SetInstructions(instructions):
            return replace(request, instructions=instructions), SetInstructions(
                request.instructions
            )
        case _:
            assert_never(amendment)
```
<!-- fmt:on -->

`apply` returns two things, the amended request and the amendment that reverses it. The inverse of `Reweigh(kg(130))` on a 120 kg request is `Reweigh(kg(120))`, read from the request that was amended. `test_apply_returns_the_amendment_that_reverses_it` runs this for each kind: applying the inverse restores the original request, and the inverse's inverse is the amendment you started with. `dataclasses.replace`, documented in the [`dataclasses` module](https://docs.python.org/3/library/dataclasses.html), builds the new request, so the old one is untouched. `test_a_redirect_needs_a_port_code` shows `Redirect` refusing `"sgsin"` and `"SGSIN "` with an `AmendmentError` that quotes the code it was given.

The last arm is `case _: assert_never(amendment)`. A fourth kind added to the union without an arm is a type error, and the technique is the one taught in [State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}). `test_mypy_reports_an_amendment_kind_missing_from_apply` runs a reduced copy of this module with an `Insure` kind added. `test_the_amendment_snippet_mirrors_the_source` holds the copy to the real classes and arms, and the run through the test's own helper prints:

```text
<string>:51: error: Argument 1 to "assert_never" has incompatible type "Insure"; expected "Never"  [arg-type]
```

An obvious alternative is one `Amendment` class with an `apply` callable and an `undo` callable as fields. A command holding callables captures its undo data when it's built, which is the stale-inverse failure measured in the next section, and two commands built around partials don't compare equal, so the equality that the first test shows is gone.

## Undo, redo and the inverse captured at run time

`Booking` is an entity, so it's a plain slotted dataclass with identity equality. It holds the current request and the two stacks:

<!-- fmt:off -->
```python
@dataclass(slots=True, eq=False)
class Booking:
    """An entity: its request changes over time, and its history says how to go back."""

    request: BookingRequest
    history_limit: int = 20
    undo_stack: deque[Amendment] = field(init=False)
    redo_stack: deque[Amendment] = field(init=False)
    pending: deque[Amendment] = field(init=False)

    def __post_init__(self) -> None:
        self.undo_stack = deque(maxlen=self.history_limit)
        self.redo_stack = deque()
        self.pending = deque()

    def amend(self, amendment: Amendment) -> None:
        self.request, inverse = apply(self.request, amendment)
        self.undo_stack.append(inverse)
        self.redo_stack.clear()

    def undo(self) -> None:
        if not self.undo_stack:
            raise AmendmentError("nothing to undo")
        self.request, redo = apply(self.request, self.undo_stack.pop())
        self.redo_stack.append(redo)

    def redo(self) -> None:
        if not self.redo_stack:
            raise AmendmentError("nothing to redo")
        self.request, undo = apply(self.request, self.redo_stack.pop())
        self.undo_stack.append(undo)
```
<!-- fmt:on -->

The stacks hold inverses. `amend` applies an amendment and pushes what `apply` returned. `undo` pops an inverse, applies it, and pushes what that application returned onto the redo stack, which is the amendment that redoes the change. `redo` runs the same move the other way. `test_undo_and_redo_walk_the_history` amends twice, undoes twice and redoes twice, checking the request and the stack sizes at each step, and `test_two_amendments_undone_restore_the_original_request` checks that the request returns to the starting value. `test_undo_or_redo_with_nothing_recorded_is_an_amendment_error` covers both operations on an empty stack: an `AmendmentError`, with the request unchanged.

A new amendment clears the redo stack, which is the dashed box in the figure. Once the history has branched, the old redo entries describe a future that no longer follows from the present, and `test_a_new_amendment_clears_redo` undoes a weight change, makes a redirect and finds redo empty and refused.

The rule that keeps this correct is to read the inverse when the command runs. The test `test_an_inverse_captured_when_queued_restores_a_stale_weight` builds the opposite shape as a fixture, `_PrecomputedReweigh(before, after)`, where `before` is recorded at construction. Both commands are built while the weight is 120. After both run, the weight is 140, and undoing the second sets it to 120 where 130 was expected. The same test then amends through `Booking`, where `apply` reads the weight at the moment of change, and one undo gives 130. A command that knows its inverse in advance is right only while nothing else runs in between, and a queue is a place where other things run.

The history is bounded. `Booking` builds `undo_stack` with `maxlen=history_limit`, and the [`collections` documentation](https://docs.python.org/3/library/collections.html) says what that does: "Once a bounded length deque is full, when new items are added, a corresponding number of items are discarded from the opposite end." Inverses are appended on the right, so the oldest goes from the left, without a message. `test_a_bounded_history_forgets_the_oldest_amendment` sets a limit of two, makes three amendments and undoes twice. The third undo is an `AmendmentError`, and the weight is the one after the first amendment. The limit is a choice to state. Twenty is the default here, and an audit trail that needs the whole history wants a log, not this stack.

## Commands that share mutable data

The failure needs no unusual code. The test fixtures `_LooseSetInstructions` and `_loose_apply` are the same command as `SetInstructions` with one change in the field type:

```python
@dataclass(frozen=True, slots=True)
class _LooseSetInstructions:
    instructions: dict[str, str]


def _loose_apply(
    request: _LooseRequest, command: _LooseSetInstructions
) -> tuple[_LooseRequest, _LooseSetInstructions]:
    return (
        replace(request, instructions=command.instructions),
        _LooseSetInstructions(request.instructions),
    )
```

`test_commands_sharing_a_mutable_mapping_undo_to_the_wrong_state` builds a first command from a `notes` dictionary holding "keep dry", then edits `notes` to "fragile", builds a second command from the same dictionary and applies the inverse of the second. The instructions are `{"handling": "fragile"}` where "keep dry" was expected. Both commands, and the request that stored the first one's mapping, point at one dict. The frozen decorator stopped nobody, and `test_mypy_accepts_commands_that_share_a_dict` shows that mypy accepts the shape with exit status 0 and no output. Frozen is shallow, which [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) teaches. Here the consequence is concrete: an inverse is only as good as the data it holds, and a mutable field makes that data a moving target.

The fix is the field type. `SetInstructions.instructions` and `BookingRequest.instructions` are `frozendict[str, str]`. Python 3.15 adds the type as a builtin, and [PEP 814](https://peps.python.org/pep-0814/), by Victor Stinner and Donghee Na, says what it is for: "A new public immutable type `frozendict` is added to the `builtins` module." The [What's New page for 3.15](https://docs.python.org/3/whatsnew/3.15.html) adds: "It does not allow modification after creation." Three tests measure what that buys:

- `test_mypy_rejects_a_dict_where_frozen_instructions_belong` passes a `dict` to `SetInstructions`. The test's own run prints `<string>:5: error: Argument 1 to "SetInstructions" has incompatible type "dict[str, str]"; expected "frozendict[str, str]"  [arg-type]`, so the caller's dictionary is refused at the call.
- `test_mypy_rejects_assigning_into_frozen_instructions` assigns into `request.instructions["handling"]` and gets `<string>:5: error: Unsupported target for indexed assignment ("frozendict[str, str]")  [index]`.
- `test_instructions_cannot_be_changed_after_queueing` does the assignment at run time, behind a `# type: ignore[index]`, and gets a `TypeError` matching "does not support item assignment", with the original text intact.

The caller who wants to supply a mapping writes `frozendict({"handling": "keep dry"})`, a mapping that nobody else holds. mypy catches the caller who forgets, and an item assignment into a `frozendict` raises at run time. A frozen dataclass may also default a `frozendict` field without `default_factory`: `BookingRequest` does, and `test_a_frozen_mapping_default_needs_no_factory` shows two requests sharing one default object, with a `dict` default refused as a `ValueError` that says to use `default_factory`.

One more property comes free. Every `BookingRequest` is a frozen value, so a request kept from before a series of amendments still equals the original after them. `test_a_frozen_request_is_a_safe_snapshot` checks that. Snapshots as an undo strategy, with rollback of a whole object, belong to [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}). A snapshot is the alternative when no inverse exists.

## A queue that applies all or nothing

Queued amendments change nothing until they're applied. `submit` appends to a deque, and `apply_pending` drains it first in, first out:

<!-- fmt:off -->
```python
    def submit(self, amendment: Amendment) -> None:
        self.pending.append(amendment)

    def apply_pending(self) -> None:
        """Apply the queue first in, first out, all or nothing."""
        queue = deque(self.pending)
        request = self.request
        inverses: list[Amendment] = []
        while queue:
            request, inverse = apply(request, queue.popleft())
            inverses.append(inverse)
        self.request = request
        self.undo_stack.extend(inverses)
        self.pending.clear()
        self.redo_stack.clear()
```
<!-- fmt:on -->

The loop works on a local deque built from the queue and a local request, and nothing on `self` changes until the loop has finished. `test_queued_amendments_apply_in_order` submits four amendments, checks that the weight is still 120, applies the batch and finds the last weight, destination and instructions in place. Undoing then walks back through them in reverse, with one inverse per amendment. `test_a_batch_clears_redo_and_records_one_inverse_per_amendment` checks the committed history, `[Reweigh(kg(120)), Redirect("SGSIN")]`.

The failing case is the reason for the local variable. `test_a_failing_batch_leaves_the_booking_unchanged` submits a reweigh and then `Redirect("nowhere")`. The second raises `AmendmentError`, and the test finds the request, the undo stack, the redo stack and the pending queue all equal to their values before the call, with both amendments still waiting. The first amendment's effect was computed and thrown away.

Harry Percival and Bob Gregory, in *Architecture Patterns with Python*, have a chapter titled "Commands and Command Handler" on commands that are queued and handled in one place. The idea that a command is a message with one handler comes from that chapter, where the dispatcher expects one handler per command; the code and examples here are new. For queues shared across concurrent tasks, see [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## When not to use it

Call the function when a change is never undone or queued. A `reweigh(request, weight)` function does the job with no history to keep.

If a database transaction already gives you undo, a second stack of inverses repeats it. If the history exists to audit changes rather than reverse them, record what happened as events and publish them; [Observer]({{ '/docs/22-observer/' | relative_url }}) covers that. If an amendment's inverse depends on state you don't hold, such as a rate fetched from another system, no value can carry it, and a snapshot of the whole object is the tool to reach for.

<blockquote class="ai-sidebar" markdown="1">
**Reviewing assistant-written commands.** An assistant asked for "the Command pattern" may write a `Command` base class with `execute` and `undo`, record the old value when the command is created, store a caller's `dict` or `list` in a command, or apply a batch by changing the booking step by step. Check: is each command a frozen value that compares equal; is the inverse computed from the state the command actually changed; are the command's fields immutable types such as `frozendict` or `tuple`; does a failing batch leave the booking unchanged; is the history's bound a stated choice.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/15-command-undo-and-command-queues
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
collecting ... collected 29 items

tests/test_commands.py::test_amendments_compare_by_value_and_partials_do_not PASSED [  3%]
tests/test_commands.py::test_apply_returns_the_amendment_that_reverses_it[reweigh] PASSED [  6%]
tests/test_commands.py::test_apply_returns_the_amendment_that_reverses_it[redirect] PASSED [ 10%]
tests/test_commands.py::test_apply_returns_the_amendment_that_reverses_it[instructions] PASSED [ 13%]
tests/test_commands.py::test_a_redirect_needs_a_port_code PASSED         [ 17%]
tests/test_commands.py::test_a_booked_weight_must_be_positive_and_finite[kilograms0] PASSED [ 20%]
tests/test_commands.py::test_a_booked_weight_must_be_positive_and_finite[kilograms1] PASSED [ 24%]
tests/test_commands.py::test_a_booked_weight_must_be_positive_and_finite[kilograms2] PASSED [ 27%]
tests/test_commands.py::test_a_booked_weight_must_be_positive_and_finite[kilograms3] PASSED [ 31%]
tests/test_queue.py::test_queued_amendments_apply_in_order PASSED        [ 34%]
tests/test_queue.py::test_a_failing_batch_leaves_the_booking_unchanged PASSED [ 37%]
tests/test_queue.py::test_a_batch_clears_redo_and_records_one_inverse_per_amendment PASSED [ 41%]
tests/test_shared_data.py::test_commands_sharing_a_mutable_mapping_undo_to_the_wrong_state PASSED [ 44%]
tests/test_shared_data.py::test_instructions_cannot_be_changed_after_queueing PASSED [ 48%]
tests/test_shared_data.py::test_a_frozen_mapping_default_needs_no_factory PASSED [ 51%]
tests/test_static.py::test_mypy_rejects_a_dict_where_frozen_instructions_belong PASSED [ 55%]
tests/test_static.py::test_mypy_rejects_assigning_into_frozen_instructions PASSED [ 58%]
tests/test_static.py::test_mypy_reports_an_amendment_kind_missing_from_apply PASSED [ 62%]
tests/test_static.py::test_mypy_accepts_commands_that_share_a_dict PASSED [ 65%]
tests/test_static.py::test_the_amendment_snippet_mirrors_the_source PASSED [ 68%]
tests/test_static.py::test_apply_ends_in_assert_never PASSED             [ 72%]
tests/test_undo.py::test_undo_and_redo_walk_the_history PASSED           [ 75%]
tests/test_undo.py::test_a_new_amendment_clears_redo PASSED              [ 79%]
tests/test_undo.py::test_undo_or_redo_with_nothing_recorded_is_an_amendment_error[undo] PASSED [ 82%]
tests/test_undo.py::test_undo_or_redo_with_nothing_recorded_is_an_amendment_error[redo] PASSED [ 86%]
tests/test_undo.py::test_two_amendments_undone_restore_the_original_request PASSED [ 89%]
tests/test_undo.py::test_an_inverse_captured_when_queued_restores_a_stale_weight PASSED [ 93%]
tests/test_undo.py::test_a_bounded_history_forgets_the_oldest_amendment PASSED [ 96%]
tests/test_undo.py::test_a_frozen_request_is_a_safe_snapshot PASSED      [100%]

============================== 29 passed in 1.75s ==============================
Success: no issues found in 10 source files
```

The suite has 23 test functions and 29 cases. The tests that cover this chapter's claims are in `test_commands.py`, `test_undo.py`, `test_shared_data.py`, `test_queue.py` and `test_static.py`. For how the tests and the mypy witnesses are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: stop clearing redo.** In a scratch copy, delete the `self.redo_stack.clear()` line in `Booking.amend`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then the member's mypy run gives:

```text
E       AssertionError: assert 1 == 0
tests/test_undo.py:50: AssertionError
FAILED tests/test_undo.py::test_a_new_amendment_clears_redo - AssertionError:...
1 failed, 28 passed in 1.76s
Success: no issues found in 10 source files
```

The redo stack still holds the inverse of the undone weight change after a redirect, so `test_a_new_amendment_clears_redo` finds one entry where it expected none. mypy stays green, because a stack that's too full is still a valid deque.

**Experiment two: change the request in the loop.** In a fresh scratch copy, delete the local `request` in `Booking.apply_pending` and assign to `self.request` inside the loop instead of after it. The same filtered run, then mypy, gives:

```text
E       AssertionError: assert BookingReques...=frozendict()) == BookingReques...=frozendict())
tests/test_queue.py:44: AssertionError
FAILED tests/test_queue.py::test_a_failing_batch_leaves_the_booking_unchanged
1 failed, 28 passed in 1.75s
Success: no issues found in 10 source files
```

The batch's first amendment is applied to the booking before the second one raises, so the request is half amended and no longer equals the one the test captured. mypy reports success again. Nothing in a type says that a batch is atomic.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Command. Harry Percival and Bob Gregory's *Architecture Patterns with Python* has the chapter "Commands and Command Handler", published free at [cosmicpython.com](https://www.cosmicpython.com/book/preface.html). The [`collections` documentation](https://docs.python.org/3/library/collections.html) covers `deque` and `maxlen`, [PEP 814](https://peps.python.org/pep-0814/) and the [3.15 What's New](https://docs.python.org/3/whatsnew/3.15.html) cover `frozendict`, and the [`dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html) covers `frozen` and `replace`. [PEP 634](https://peps.python.org/pep-0634/) specifies the `match` statement. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
