---
title: "Mediator and Chain of Responsibility"
order: 23
layout: tutorial
sectionid: docs
part: "coordinating-traversing"
description: "A chain of responsibility is a tuple of callables, but the order of its stages and the final stage are still choices you make. A mediator keeps the rule for releasing a declaration, once its duty and inspection reports have arrived, in one place."
---

## Learning objectives

By the end of this chapter you can:

- Say what Python removes from Chain of Responsibility and Mediator (the handler class with its successor link, the Mediator and Colleague classes) and which choices Python leaves to you.
- Write a clearance chain as a tuple of typed callables, where `None` passes the declaration on and a separately typed final stage can't.
- Say what mypy checks about a chain (the shape of each stage) and what it can't see (their order).
- Write one mediator that releases a declaration exactly once, after every report it still owes has arrived (duty if unpaid, inspection if restricted), in either order.
- Choose between a chain, a `match`, a mediator and a signal.

## Why this matters

A customs declaration passes a row of checks. A held one then waits on reports from parties who don't know each other. The chain decides whether a declaration is held, and the mediator decides when a held one is released. Python's syntax makes neither choice for you, so both patterns survive, in the sense of [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}).

{% include excalidraw.html name="23-mediator-and-chain-of-responsibility" caption="Figure 23.1: A declaration passes along an ordered tuple of clearance stages; the first stage that decides ends the walk, and a clean one is released by the final stage. A separate mediator releases a declaration after the reports it is owed arrive." described="true" %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-23-mediator-and-chain-of-responsibility" markdown="1">
The chain runs from the top down. `CustomsDeclaration` goes to `clear`, "walks the stages in order". Below it sit `check_documents`, `assess_duty` and `inspect_goods`, each with a "None: pass it on" arrow down, and then `release`, "final stage: decides". Each stage also has an arrow to `Held`, "the stage stops the walk", and the figure draws nothing out of `Held`. On the right, apart from the chain, `Settlement` and `Inspection` feed `ClearanceMediator`, "releases once nothing is outstanding", which sends `CLEARED` to `TrackingHistory.record`. A muted dashed box, "linked chain", reads "falls off the end with None".
</div>
</details>

The figure draws the chain on the left and the mediator on the right.

## Pattern: Chain of Responsibility

### The problem

Each customs check can stop a consignment: the documents are incomplete, the duty is unpaid, the commodity needs inspection. The code that submits a declaration shouldn't know which check stops it, and a new check shouldn't mean an edit at every call site. Two obvious versions go wrong:

- **A misordered chain.** Someone appends the inspection stage after release, so release decides first, a restricted batch of batteries is cleared, and mypy accepts the code.
- **A linked chain with no terminal.** A clean declaration comes back as `None`, because nobody said what the last handler does when it passes.

### The solution

A **Chain of Responsibility** passes a request along a row of receivers until one takes it. The sender can't say which one will.

**Bucket: survives.** Python removes the class that carries the successor link, and leaves you to choose the order and the final stage.

### How Python models it

A stage is a function from a declaration to a `Decision`, or to `None` for "not mine". The chain is a tuple of them. [PEP 695](https://peps.python.org/pep-0695/) "also introduces a new statement for declaring type aliases", and the three aliases use it:

```python
type Decision = Released | Held
type ClearanceStage = Callable[[CustomsDeclaration], Decision | None]
type FinalStage = Callable[[CustomsDeclaration], Decision]
```

`Released` and `Held` are frozen dataclasses, and `Held` carries a reason. The two stage types differ by one `| None`. The walk is a loop:

```python
def clear(
    declaration: CustomsDeclaration,
    stages: Iterable[ClearanceStage],
    /,
    *,
    final: FinalStage = release,
) -> Decision:
    """Return the first decision a stage makes, else the final stage's. Later stages don't run."""
    for stage in stages:
        if (decision := stage(declaration)) is not None:
            return decision
    return final(declaration)
```

| Choice | Where it lives |
| --- | --- |
| Pass it on | a stage returns `None` |
| Which stage runs first | the order of `stages`, which the caller supplies; `CLEARANCE_STAGES` is `check_documents`, `assess_duty`, `inspect_goods` |
| Who decides when nobody does | `final`, which defaults to `release` |

The first stage that decides wins, and later stages don't run. A declaration with no documents and unpaid duty is held for the missing invoice, because `check_documents` runs before `assess_duty`. A clean declaration reaches `final` and is released; a restricted commodity, a missing document and unpaid duty are each held.

### The terminal and the order

`final` is typed `Callable[[CustomsDeclaration], Decision]`, so it can't return `None`. Passing a `ClearanceStage` as `final` gives:

```text
<string>:10: error: Argument "final" to "clear" has incompatible type "Callable[[CustomsDeclaration], Released | Held | None]"; expected "Callable[[CustomsDeclaration], Released | Held]"  [arg-type]
```

A stage with the wrong return type is `[arg-type]` too, and one that falls off the end on some path is `Missing return statement  [return]`. With an empty chain, `final` decides.

Order is another matter. `release` returns `Released()`, so it satisfies `ClearanceStage` as well as `FinalStage`. Put it inside the chain, as in `[check_documents, assess_duty, release]` with `inspect_goods` appended, and it decides before `inspect_goods` sees the batteries: a restricted declaration is released. mypy accepts `clear(declaration, (release, inspect_goods))` under `--strict`. It checks the shape of each stage, and a chain's order is a property of the whole tuple. Only running a restricted declaration through the production order catches a misplaced `release`.

`describe` consumes a `Decision` with `match` ending in `assert_never`, so a missing arm, or a third member added to `Decision`, is `[arg-type]` with `expected "Never"` at every such `match`.

### Linked chain vs. tuple

*Design Patterns* draws the receivers as objects that each hold a reference to the next. In the comparison `_Handler`, each handler runs its stage and, on `None`, calls the next handler, or returns `None` off the end.

| Declaration | `clear` over a tuple | Linked chain |
| --- | --- | --- |
| Restricted, missing a document, or unpaid | held | held |
| Clean | released by `final` | `None`, because no handler is responsible for the end |

mypy refuses the linked chain's `Released | Held | None` where `describe` needs a `Decision`. `final` is what the loop adds: a name for "nobody decided".

### Chain vs. match

When the rules are closed and fixed, one `match` with a default is the chain. The comparison `_clear_by_match` holds the same declarations.

| | Tuple of stages | `_clear_by_match` |
| --- | --- | --- |
| Takes | the declaration, the stages and `final` | the declaration and nothing else |
| Its order lives in | the tuple the caller passes | the `match` statement's source |
| A caller can extend it or test a stage on its own | yes | no |
| Choose it when | someone adds rules | nobody adds rules |

## Pattern: Mediator

### The problem

A consignment held for duty or inspection waits on two parties who don't know each other: billing and the inspection party. Something has to decide when the reports it is owed have arrived. If the parties call each other instead, a settlement that arrives before the inspection is dropped, and the batteries never clear.

### The solution

A **Mediator** is an object that coordinates a group of parties whose actions depend on one another. The parties talk to it, not to each other, so none has to know who else exists or in what order they report.

**Bucket: survives.** The abstract Mediator and Colleague classes dissolve, but the release rule stays, written once with its state.

### How Python models it

A colleague needs only `receive`, and the mediator is given a callable that does the release. A `Settlement` reports duty paid in full; an `Inspection` carries the result:

<!-- fmt:off -->
```python
    def receive(self, message: ClearanceMessage, /) -> None:
        own = self._declaration.consignment_id
        if message.consignment_id != own:
            raise ClearanceError(
                f"message for {message.consignment_id!r} sent to the mediator for {own!r}"
            )
        match message:
            case Settlement():
                self._outstanding.discard("duty")
            case Inspection(passed=True):
                self._outstanding.discard("inspection")
            case Inspection():
                self._outstanding.discard("inspection")
                self._failed = True
            case _:
                assert_never(message)
        self._try_release()

    def _try_release(self) -> None:
        if self._outstanding or self._failed or self._released:
            return
        self._released = True
        declaration = self._declaration
        self._release(
            HandlingEvent(declaration.consignment_id, HandlingKind.CLEARED, declaration.port)
        )
```
<!-- fmt:on -->

`ClearanceMessage` is `Settlement | Inspection`. The rule lives in `_try_release`, next to the state it reads. `_outstanding` starts as what the declaration still owes: duty if it isn't paid, inspection if the commodity is restricted.

| Messages | History |
| --- | --- |
| nothing owed | `CLEARED` at the declaration's port, at construction |
| one report owed, then that report | one `CLEARED` |
| inspection then settlement, or settlement then inspection | empty after the first, one `CLEARED` after the second |
| a second settlement after release | still one `CLEARED` |
| a settlement and `Inspection(CN1, False)` | empty: held |
| a message for `CN-2` | `ClearanceError` naming `CN-2`; the message doesn't count |

`ClearanceMediator` is single-threaded and says so in its docstring. mypy refuses a message it doesn't know, such as a `HandlingEvent`, with `expected "Settlement | Inspection"`. The second `Inspection` arm is `case Inspection()`, not `case Inspection(passed=False)`, because mypy 2.4.1 doesn't treat `True` and `False` patterns on a field as exhausting the class.

### Mediator vs. choreography

In a choreography the parties call each other. In the `_Choreography` comparison, inspection tells billing, and billing releases on a settlement only once told the inspection passed.

| Arrival order | `ClearanceMediator` | `_Choreography` |
| --- | --- | --- |
| Inspection, then settlement | released | released |
| Settlement, then inspection | released | history empty |

Billing dropped the settlement because it hadn't been told yet, and nothing asks it again. The mediator keeps the outstanding set, so arrival order doesn't matter.

### Mediator vs. signal

[Observer]({{ '/docs/22-observer/' | relative_url }}) builds a `Signal` that delivers each event to its subscribers and leaves what they do to them.

| | Mediator | `Signal` |
| --- | --- | --- |
| Decides who acts next | yes: `receive` turns two reports into one release | no rule of that kind |
| Fits | parties who must reply to each other | parties that don't depend on each other's replies |

The cost is that coordination rules sit in one class, and a mediator that takes on every rule in a system becomes the place everything changes. Keep one declaration's release rule in it, and nothing else.

## When not to use it

- **Chain of Responsibility.** With one check, call the function. With a fixed set of rules that nobody extends, write one `match` with a default.
- **Mediator.** With parties that don't depend on each other's replies, use a signal. If a mediator starts to make a choice that belongs to one colleague, move that rule back to the colleague.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a chain and a mediator.** "A chain of responsibility" doesn't say what "pass it on" means, which stage is final or who decides when none do. State those in the prompt:

> Write the clearance chain as `clear(declaration, stages, /, *, final=release)`, where each stage is a typed callable returning `Decision | None`, `None` passes the declaration on, the first decision wins, and `final` is typed `Callable[[CustomsDeclaration], Decision]` so it can't pass. Write release coordination as one `ClearanceMediator` that receives a closed union of messages through `match` with `assert_never`, releases only after every report it still owes (duty if unpaid, inspection if restricted) has arrived, in either order, and releases once.

If the reply puts the final stage inside the tuple or lets the parties call each other, ask for the check that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/23-mediator-and-chain-of-responsibility
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 44 cases pass and mypy is clean. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers how the mypy checks are built. Two experiments, each in a fresh scratch copy:

- **Compute every decision first.** Replace the loop in `clear` with `decisions = [stage(declaration) for stage in stages]`, then return the first that isn't `None`. Every result is the same, so only the check that records which stages ran fails: it sees a third stage called. mypy is clean.
- **Drop the released check.** Change the first line of `_try_release` to `if self._outstanding or self._failed:`. Only the duplicate settlement fails: a second message after release records a second `CLEARED`. mypy is clean.

## What you can do now

- Replace the handler class and successor link with the tuple behind `clear`, and the Mediator and Colleague classes with `ClearanceMediator.receive`.
- Write `clear(declaration, stages, /, *, final=release)`, where `None` passes and `final` is a `FinalStage`.
- Rely on mypy for a stage's shape, a final stage that can pass and a missing `match` arm, and on a run through the production order for the order.
- Release once, in either order, with the outstanding set and the released check in `_try_release`.
- Choose a `match` for closed rules, a signal for independent parties, and the mediator where one rule needs the reports it is owed.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides, 1994) is the source for both Chain of Responsibility and Mediator. The Python tutorial's [`match` statements](https://docs.python.org/3/tutorial/controlflow.html) cover the pattern syntax `describe` and `receive` use. [PEP 695](https://peps.python.org/pep-0695/), by Eric Traut, specifies the `type` statement. The site python-patterns.guide, by Brandon Rhodes, has no page on either pattern in its index. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
