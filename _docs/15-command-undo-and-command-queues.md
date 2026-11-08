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

A booking request changes after it's made: the shipper revises the weight, redirects the consignment, rewrites the handling instructions. The back office queues those amendments, applies them in one go and steps back through them when a clerk makes a mistake. A deferred call can be queued but not undone, so Command keeps its design work.

{% include excalidraw.html name="15-command-undo-and-command-queues" described="true" caption="Figure 15.1: Amendments as values on two stacks. Queued amendments are applied first in, first out, all or nothing; each application returns a new frozen request and the inverse it computed, which undo and redo move between the two stacks." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-15-command-undo-and-command-queues" markdown="1">
An accent box, `submit(amendment)`, feeds `pending`, a deque that is first in, first out. `apply_pending` follows, folding on a local request so that the batch is all or nothing, and it calls `apply(request, amendment)`, one match in one function. That box forks into two: `BookingRequest`, the new frozen value, and the inverse amendment, read at the moment of change. The inverse arrow runs down to `undo_stack`, a `deque(maxlen)` that forgets its oldest entry. Between `undo_stack` and `redo_stack` two arrows carry an inverse each way, labelled undo and redo. A dashed box above `redo_stack`, "new amendment clears redo", points into it.
</div>
</details>

The figure follows an amendment from the queue through `apply` to the undo and redo stacks.

## Pattern: Command

### The problem

Three things go wrong in the obvious versions:

- **Shared data.** Two instruction amendments are built from one dictionary the caller keeps editing. The first says "keep dry", the caller changes the dictionary to "fragile", the second is built from it, and after one undo the instructions read "fragile" where "keep dry" was expected. mypy accepts the code.
- **A stale inverse.** An amendment records the old weight when it's queued. Two are queued while the weight is 120, one to 130 and one to 140. After both run, undoing the second restores 120 where 130 was expected.
- **A half-applied batch.** A batch fails on its third amendment, and the booking keeps the first two.

The force is that a change needs an identity of its own. It's held, passed on, replayed and, with enough data, reversed.

### The solution

A **Command** turns a request into a value that can be queued, applied later and reversed.

**Bucket: survives.** The deferred call dissolves into `functools.partial`, and undo, a queue and an inverse that stays correct still need design.

*Design Patterns* (Gamma, Helm, Johnson and Vlissides, 1994) builds it as a `Command` base with `execute` and `undo`. A deferred call alone is a `functools.partial`, and [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) shows a deque of partials that change nothing until called. A partial lacks the rest of the force:

| | Amendment value | `partial` |
| --- | --- | --- |
| Equal to another built the same way | yes: two `Reweigh(kg(130))` are equal, with equal hashes | no |
| Repr | `Redirect(destination='MYPKG')` | carries a function address |
| Inverse | returned by `apply` | none, and no `undo` attribute |

So a queue of partials can't be undone or deduplicated. [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) covers `partial` itself. The Python shape is a closed set of frozen values, one function that applies a value, a bounded undo stack, a redo stack and a queue.

### How Python models it

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

`apply` returns the amended request and the amendment that reverses it. The inverse of `Reweigh(kg(130))` on a 120 kg request is `Reweigh(kg(120))`, read from the request that was amended. Applying the inverse restores the original request, and the inverse's inverse is the amendment you started with. `dataclasses.replace`, documented in the [`dataclasses` module](https://docs.python.org/3/library/dataclasses.html), builds the new request and leaves the old one untouched. `Redirect` refuses `"sgsin"` and `"SGSIN "` with an `AmendmentError` that quotes the code.

The last arm is `case _: assert_never(amendment)`, the technique from [State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}). Add an `Insure` kind to the union without an arm, and mypy reports:

```text
<string>:51: error: Argument 1 to "assert_never" has incompatible type "Insure"; expected "Never"  [arg-type]
```

The obvious alternative is one `Amendment` class with `apply` and `undo` callables as fields. It captures its undo data when it's built, which is the stale-inverse failure, and two commands built around partials don't compare equal.

### Undo, redo and the inverse captured at run time

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

The stacks hold inverses. Two amendments undone restore the original request, and redone reach the amended one again. Undo or redo on an empty stack raises `AmendmentError` and leaves the request unchanged.

A new amendment clears the redo stack. Once the history has branched, the old redo entries describe a future that no longer follows from the present: undo a weight change, make a redirect, and redo is empty and refused.

The rule that keeps this correct is to read the inverse when the command runs. A command that records `before` at construction, built twice while the weight is 120, leaves 120 after one undo where 130 was expected. Through `Booking`, where `apply` reads the weight at the moment of change, one undo gives 130. A command that knows its inverse in advance is right only while nothing else runs in between, and a queue is a place where other things run.

The history is bounded. The [`collections` documentation](https://docs.python.org/3/library/collections.html) says: "Once a bounded length deque is full, when new items are added, a corresponding number of items are discarded from the opposite end." Inverses are appended on the right, so the oldest goes from the left, without a message. With a limit of two, three amendments allow two undos, and the third raises `AmendmentError`. Twenty is the default here. An audit trail that needs the whole history wants a log, not this stack.

### Commands that share mutable data

The failure needs no unusual code. The same command as `SetInstructions`, with one change in the field type:

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

Build one command from a `notes` dictionary holding "keep dry", edit `notes` to "fragile", build a second from the same dictionary and apply the second's inverse. The instructions are `{"handling": "fragile"}`, because both commands and the request point at one dict. The frozen decorator stopped nobody, and mypy accepts the shape. Frozen is shallow; see [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}).

The fix is the field type. `SetInstructions.instructions` and `BookingRequest.instructions` are `frozendict[str, str]`. Python 3.15 adds the type as a builtin, and [PEP 814](https://peps.python.org/pep-0814/), by Victor Stinner and Donghee Na, says what it is for: "A new public immutable type `frozendict` is added to the `builtins` module." The [What's New page for 3.15](https://docs.python.org/3/whatsnew/3.15.html) adds: "It does not allow modification after creation."

| Mistake | mypy | Runtime |
| --- | --- | --- |
| Passing a `dict` to `SetInstructions` | `incompatible type "dict[str, str]"; expected "frozendict[str, str]"  [arg-type]` | accepted |
| Assigning into `request.instructions["handling"]` | `Unsupported target for indexed assignment ("frozendict[str, str]")  [index]` | `TypeError`: "does not support item assignment" |

A caller who wants to supply a mapping writes `frozendict({"handling": "keep dry"})`, which nobody else holds. A frozen dataclass may default a `frozendict` field without `default_factory`, as `BookingRequest` does; two requests share the one default safely, where a `dict` default raises `ValueError` asking for `default_factory`.

Every `BookingRequest` is a frozen value, so a request kept from before a series of amendments still equals the original after them. Snapshots as an undo strategy, rolling back a whole object, belong to [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}). A snapshot is the alternative when no inverse exists.

### A queue that applies all or nothing

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

Four submitted amendments leave the weight at 120 until the batch applies, then all take effect, and undo walks back through them in reverse, one inverse per amendment.

The local `request` is what makes the batch atomic. Submit a reweigh and then `Redirect("nowhere")`: the second raises `AmendmentError`, and the request, both stacks and the pending queue are all as they were, with both amendments still waiting. The first amendment's effect was computed and thrown away.

Harry Percival and Bob Gregory's *Architecture Patterns with Python*, in "Commands and Command Handler", treats commands that are queued and handled in one place, with one handler per command; that idea comes from them, and the code here is new. For queues shared across concurrent tasks, see [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## When not to use it

- **Command.** Call the function when a change is never undone or queued. `reweigh(request, weight)` keeps no history. If a database transaction already gives you undo, a second stack of inverses repeats it. If the history exists to audit changes rather than reverse them, record events and publish them; see [Observer]({{ '/docs/22-observer/' | relative_url }}). If an inverse depends on state you don't hold, such as a rate fetched from another system, no value can carry it, and a snapshot of the whole object is the tool.

> **🤖 Explore with your agent**
>
> "Make each amendment a frozen, slotted dataclass in a closed union, with immutable field types (`frozendict`, `tuple`). Write `apply(request, amendment)` as a `match` ending in `assert_never` that returns the new request and the inverse read from the request it changed. Keep undo and redo in `deque`s, the undo stack with `maxlen`, and clear redo on a new amendment. Apply a queue on a local request, so a failure leaves the booking unchanged."
>
> If the inverse is recorded when the command is queued, ask for the two-amendment undo test.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/15-command-undo-and-command-queues
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 29 cases pass, and mypy reports `Success: no issues found in 10 source files`. Two experiments, each in a scratch copy:

- **Stop clearing redo.** Delete `self.redo_stack.clear()` in `Booking.amend`. One test fails: after a redirect, redo still holds the undone weight change. mypy stays green, because a stack that's too full is still a valid deque.
- **Change the request in the loop.** In `apply_pending`, assign to `self.request` inside the loop instead of a local. One test fails: the first amendment lands before the second raises, and the request is half amended. mypy stays green; no type says a batch is atomic.

## What you can do now

- Say what dissolves and what survives: the deferred call becomes a `partial`, and the amendment value with its inverse survives.
- Write amendments as a closed union of frozen values and one `apply` ending in `assert_never`, reading the inverse from the request it changes.
- Keep undo and redo as two `deque` stacks, the undo stack bounded, with the inverse read when the amendment runs.
- Close the shared-mapping gap with a `frozendict` field.
- Apply a queue all or nothing by folding on a local request, as `apply_pending` does.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Command. Harry Percival and Bob Gregory's *Architecture Patterns with Python* has "Commands and Command Handler", published free at [cosmicpython.com](https://www.cosmicpython.com/book/preface). The [`collections` documentation](https://docs.python.org/3/library/collections.html) covers `deque` and `maxlen`, [PEP 814](https://peps.python.org/pep-0814/) and the [3.15 What's New](https://docs.python.org/3/whatsnew/3.15.html) cover `frozendict`, and the [`dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html) covers `frozen` and `replace`. [PEP 634](https://peps.python.org/pep-0634/) specifies the `match` statement. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
