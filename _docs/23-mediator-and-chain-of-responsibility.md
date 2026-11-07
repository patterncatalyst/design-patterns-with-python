---
title: "Mediator and Chain of Responsibility"
order: 23
layout: tutorial
sectionid: docs
part: "coordinating-traversing"
description: "A chain of responsibility is a tuple of callables, but which stage runs first and who decides when nobody does are still decisions, and a mediator keeps the rule for releasing a declaration, once its duty and inspection reports have arrived, in one place."
---

## Learning objectives

By the end of this chapter you can:

- Say what Python removes from Chain of Responsibility and Mediator, the handler class with its successor link and the Mediator and Colleague classes, and which decisions survive.
- Write a clearance chain as a tuple of typed callables, where `None` passes the declaration on and a separately typed final stage can't.
- Say what mypy checks about a chain, the shape of each stage, and what it can't see, their order.
- Write one mediator that releases a declaration exactly once, after every report it still owes has arrived (duty if unpaid, inspection if restricted), in either order.
- Choose between a chain, a `match`, a mediator and a signal.

## Why this matters

Customs clearance is a row of checks, and each one can stop a consignment: the documents are incomplete, the duty is unpaid, the commodity needs inspection. The code that submits a declaration shouldn't know which check stops it, and a new check shouldn't mean an edit at every call site. That's the force behind Chain of Responsibility. A consignment held for duty or inspection then waits on two parties who don't know each other, billing and the inspection party, and something has to decide when the reports it is owed have arrived. That's the force behind Mediator. One story joins them: the chain decides whether a declaration is held, and the mediator decides when a held one is released. Three things go wrong in the obvious versions.

A restricted batch of batteries is cleared. Someone appended the inspection stage after the release stage, so release decided first. mypy accepts the code.

A clean declaration comes back from a chain of linked handler objects as `None`. Nobody said what the last handler does when it passes.

Billing and the inspection party are wired to tell each other what happened. A settlement that arrives before the inspection is dropped, and the batteries never clear.

Each is a decision, and both patterns survive because Python's syntax doesn't make those decisions for you.

{% include excalidraw.html name="23-mediator-and-chain-of-responsibility" caption="Figure 23.1: A declaration passes along an ordered tuple of clearance stages; the first stage that decides ends the walk, and a clean one is released by the final stage. A separate mediator releases a declaration after the reports it is owed arrive." %}

Read the figure from the top down. `CustomsDeclaration` goes to `clear`, "walks the stages in order". Below it sit `check_documents`, `assess_duty` and `inspect_goods`, each with a "None: pass it on" arrow down, and then `release`, "final stage: decides". Each stage also has an arrow to `Held`, "the stage stops the walk", and the figure draws nothing out of `Held`. On the right, apart from the chain, `Settlement` and `Inspection` feed `ClearanceMediator`, "releases once nothing is outstanding", which sends `CLEARED` to `TrackingHistory.record`. A muted dashed box, "linked chain", reads "falls off the end with None".

## A chain is a tuple of stages

Chain of Responsibility is for a request that several parties might deal with, where the sender can't say which. In *Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994), the receivers are objects that each hold a reference to the next, and a request travels along them until one takes it. The class that carries the successor link is the part Python removes. A stage is a function from a declaration to a decision, or to `None` for "not mine", and the chain is a tuple of them. The bucket is survives, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it.

```python
type Decision = Released | Held
type ClearanceStage = Callable[[CustomsDeclaration], Decision | None]
type FinalStage = Callable[[CustomsDeclaration], Decision]
```

[PEP 695](https://peps.python.org/pep-0695/), by Eric Traut, "also introduces a new statement for declaring type aliases", and that statement writes these three. `Released` and `Held` are frozen dataclasses, and `Held` carries a reason. The two stage types differ by one `| None`, and that difference is the point of the next section. The `X | None` form is the one [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) narrows before use.

The walk is a loop:

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

Three decisions are visible in it. What "pass it on" means: a stage returns `None`. Which stage runs first: the order of `stages`, which the caller supplies, and `CLEARANCE_STAGES` is the tuple of `check_documents`, `assess_duty` and `inspect_goods` that the tests pass in. Who decides when nobody does: `final`, which defaults to `release`.

The first stage that decides wins. `test_the_first_stage_that_decides_wins` gives a declaration with no documents and unpaid duty, and the reason is the missing invoice, because `check_documents` runs before `assess_duty`. Stages after the winner don't run: `test_stages_after_a_decision_are_not_called` records the names of the stages that were called and gets `["passing", "holding"]`, with a third stage left out. A clean declaration reaches the final stage and is released (`test_a_clean_declaration_is_released`). A restricted commodity, a missing document and unpaid duty are each held, in the tuple form and in the two comparison forms below (`test_a_restricted_commodity_is_held_for_inspection`, `test_a_declaration_missing_a_document_is_held` and `test_an_unpaid_declaration_is_held_for_duty`).

The comparison form is the linked chain that *Design Patterns* draws, written as a test fixture so it runs the same hold table:

```python
class _Handler:
    """The GoF linked chain: each handler holds the next one. Off the end it returns None."""

    def __init__(self, stage: ClearanceStage, next_handler: _Handler | None = None) -> None:
        self._stage = stage
        self._next = next_handler

    def handle(self, declaration: CustomsDeclaration, /) -> Decision | None:
        if (decision := self._stage(declaration)) is not None:
            return decision
        return self._next.handle(declaration) if self._next is not None else None
```

It holds the same three cases. It parts from `clear` on a clean declaration: `test_a_linked_chain_with_no_terminal_returns_none` gets `None`, because no handler is responsible for the end. `clear` has `final`, and a name for "nobody decided" is what the loop adds. A reduced model of this handler, which is not part of the example, goes through `describe`, a function that needs a `Decision`. `test_mypy_refuses_a_linked_chain_result_where_a_decision_is_needed` runs it through the test's own helper and prints:

```text
<string>:18: error: Argument 1 to "describe" has incompatible type "Released | Held | None"; expected "Released | Held"  [arg-type]
```

## The terminal and the order

`final` is typed `Callable[[CustomsDeclaration], Decision]`, so it can't return `None`. A stage that can pass is refused in that position. `test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage` passes one and prints:

```text
<string>:10: error: Argument "final" to "clear" has incompatible type "Callable[[CustomsDeclaration], Released | Held | None]"; expected "Callable[[CustomsDeclaration], Released | Held]"  [arg-type]
```

A stage with the wrong return type is an `[arg-type]` error too (`test_mypy_refuses_a_stage_with_the_wrong_return_type`), and a stage that returns a value on one path and falls off the end on another gets `Missing return statement  [return]` (`test_mypy_reports_a_stage_that_falls_off_the_end`). A new stage appended to the default order is a plain tuple operation, and `test_a_stage_added_to_the_chain_runs_before_the_final_stage` shows a stage that holds everything running ahead of `final`. An empty chain leaves the decision to `final` (`test_an_empty_chain_leaves_the_decision_to_the_final_stage`, once with a releasing final and once with a holding one).

Order is another matter. This test builds the misordered chain:

```python
def test_a_stage_added_after_release_clears_a_restricted_commodity(
    declaration: DeclarationFactory,
) -> None:
    misordered: list[ClearanceStage] = [check_documents, assess_duty, release]
    misordered.append(inspect_goods)

    assert clear(declaration(restricted=True), misordered) == Released()
```

`release` is a function that returns `Released()`, so it satisfies `ClearanceStage` as well as `FinalStage`. Placed inside the chain it decides, the loop stops there, and `inspect_goods` never sees the batteries. `test_mypy_cannot_see_release_placed_inside_the_chain` type-checks `clear(declaration, (release, inspect_goods))` under `--strict`, and mypy exits 0 with empty output. The type system checks the shape of each stage, and a chain's order is a property of the whole tuple. A test that runs a restricted declaration through the production order is what sees a misplaced `release`.

`describe` consumes a decision with `match`. When an arm is missing, mypy says so at the call to `assert_never`. `test_mypy_reports_a_decision_left_unhandled` has a `match` that handles `Released` and prints:

```text
<string>:12: error: Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"  [arg-type]
```

A `Decision` that gains a third member turns each `match` that ends in `assert_never` into the same kind of error.

When the rules are closed and fixed, one `match` with a default is the chain. The `match` statement, as the Python tutorial puts it, "takes an expression and compares its value to successive patterns given as one or more case blocks". The conftest function `_clear_by_match` is that form and passes the same hold table. The difference shows in its signature. It takes the declaration and nothing else, so its order lives in source and a caller can't extend it or test a stage on its own. Choose it when nobody adds rules, and the tuple when someone does.

## Mediator: one place decides when to release

Mediator is for a group of parties whose actions depend on one another. If each party calls the others, each must know who else exists and what order they report in. *Design Patterns* moves that knowledge into an object of its own, and the parties talk to it. In Python the abstract Mediator and Colleague classes dissolve. A colleague needs only the mediator's `receive`, and the mediator is given a callable that does the release. The rule is what survives, written once with its state.

Here the rule is that a declaration is released exactly once, after duty is settled if it was unpaid and inspection has passed if the commodity is restricted, in either order. A `Settlement` is billing reporting that duty is paid in full, and an `Inspection` carries the inspection party's result. Both are messages:

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

`ClearanceMessage` is `Settlement | Inspection`, and `_outstanding` starts as what the declaration still needs: duty if it isn't paid, inspection if the commodity is restricted, so a declaration that owes one of them is released on that one report (`test_a_declaration_that_owes_one_report_is_released_on_that_report`). The rule lives in `_try_release`, next to the state it reads. No colleague knows another exists. A declaration with nothing outstanding is released at construction (`test_a_declaration_with_nothing_outstanding_is_released_at_once`), and the event it records is `CLEARED` at the declaration's port (`test_release_records_a_cleared_handling_event_at_the_port`).

`test_the_mediator_releases_in_either_order` runs inspection first and settlement first. After the first message the history is empty, and after the second it holds one `CLEARED` event. A second settlement after release adds nothing (`test_a_duplicate_settlement_releases_once`). A failed inspection holds the consignment: after a settlement and an `Inspection(CN1, False)` the history is empty (`test_a_failed_inspection_holds_the_consignment`). A message for another consignment is refused, and `test_a_message_for_another_consignment_is_refused` expects a `ClearanceError` that names `CN-2`, then finds the history still empty after the right inspection. The class says in its docstring that it's single-threaded, and the example has no thread test.

The choreography is the other form. In `_Choreography`, in `tests/conftest.py`, inspection tells billing and billing releases, and billing acts on a settlement only after it has been told the inspection passed. Both forms pass `test_release_follows_inspection_then_settlement`, where the inspection comes first. They part when the settlement arrives first: `test_a_choreography_loses_a_settlement_that_arrives_before_inspection` sends the settlement, then the inspection, and the history is empty. The settlement was dropped because billing hadn't been told yet, and nothing asks it again. The mediator keeps the outstanding set, so the order of arrival doesn't matter.

Two static checks apply to the messages. A message the mediator doesn't know is refused. `test_mypy_refuses_a_message_the_mediator_does_not_know` passes a `HandlingEvent` to `receive` and prints:

```text
<string>:7: error: Argument 1 to "receive" of "ClearanceMediator" has incompatible type "HandlingEvent"; expected "Settlement | Inspection"  [arg-type]
```

And the second `Inspection` arm of `receive` is `case Inspection()`, not `case Inspection(passed=False)`, because mypy 2.4.1 doesn't treat `True` and `False` patterns on a field as exhausting the class. `test_mypy_cannot_exhaust_a_match_on_true_and_false_patterns` runs a reduced model, a one-field class matched on both values and then on `assert_never`, and mypy reports `Argument 1 to "assert_never" has incompatible type "Inspection"; expected "Never"`.

## A mediator decides, a signal broadcasts

[Observer]({{ '/docs/22-observer/' | relative_url }}) builds a `Signal` that delivers each event to its subscribers, in order, and leaves what they do to them. A mediator knows the messages its colleagues send and decides who acts next: `receive` turns two reports into one release, and a `Signal` has no rule of that kind. The Observer chapter's "When not to use it" section draws the same line: when parties must reply to each other, so that who acts depends on what the others did, a mediator decides and an observer can't. A mediator carries a cost too. All the coordination rules sit in one class, so a mediator that takes on every rule in a system becomes the place everything changes. Keep the rule for one declaration's release in it, and nothing else.

## When not to use it

With one check, call the function. With a fixed set of rules that nobody extends, write one `match` with a default. With parties that don't depend on each other's replies, use a signal. And if a mediator starts to make a decision that belongs to one colleague, move that rule back to the colleague.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a chain and a mediator.** "A chain of responsibility" doesn't say what "pass it on" means, which stage is final or who decides when none do. State those in the prompt:

> Write the clearance chain as `clear(declaration, stages, /, *, final=release)`, where each stage is a typed callable returning `Decision | None`, `None` passes the declaration on, the first decision wins, and `final` is typed `Callable[[CustomsDeclaration], Decision]` so it can't pass. Write release coordination as one `ClearanceMediator` that receives a closed union of messages through `match` with `assert_never`, releases only after every report it still owes (duty if unpaid, inspection if restricted) has arrived, in either order, and releases once.

If the reply puts the final stage inside the tuple or lets the parties call each other, ask for the test that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/23-mediator-and-chain-of-responsibility
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
collecting ... collected 44 items

tests/test_chain.py::test_a_restricted_commodity_is_held_for_inspection[stages] PASSED [  2%]
tests/test_chain.py::test_a_restricted_commodity_is_held_for_inspection[linked] PASSED [  4%]
tests/test_chain.py::test_a_restricted_commodity_is_held_for_inspection[match] PASSED [  6%]
tests/test_chain.py::test_a_declaration_missing_a_document_is_held[stages-commercial-invoice] PASSED [  9%]
tests/test_chain.py::test_a_declaration_missing_a_document_is_held[stages-dangerous-goods] PASSED [ 11%]
tests/test_chain.py::test_a_declaration_missing_a_document_is_held[linked-commercial-invoice] PASSED [ 13%]
tests/test_chain.py::test_a_declaration_missing_a_document_is_held[linked-dangerous-goods] PASSED [ 15%]
tests/test_chain.py::test_a_declaration_missing_a_document_is_held[match-commercial-invoice] PASSED [ 18%]
tests/test_chain.py::test_a_declaration_missing_a_document_is_held[match-dangerous-goods] PASSED [ 20%]
tests/test_chain.py::test_an_unpaid_declaration_is_held_for_duty[stages] PASSED [ 22%]
tests/test_chain.py::test_an_unpaid_declaration_is_held_for_duty[linked] PASSED [ 25%]
tests/test_chain.py::test_an_unpaid_declaration_is_held_for_duty[match] PASSED [ 27%]
tests/test_chain.py::test_the_first_stage_that_decides_wins[stages] PASSED [ 29%]
tests/test_chain.py::test_the_first_stage_that_decides_wins[linked] PASSED [ 31%]
tests/test_chain.py::test_the_first_stage_that_decides_wins[match] PASSED [ 34%]
tests/test_chain.py::test_a_clean_declaration_is_released PASSED         [ 36%]
tests/test_chain.py::test_a_linked_chain_with_no_terminal_returns_none PASSED [ 38%]
tests/test_chain.py::test_stages_after_a_decision_are_not_called PASSED  [ 40%]
tests/test_chain.py::test_a_stage_added_after_release_clears_a_restricted_commodity PASSED [ 43%]
tests/test_chain.py::test_a_stage_added_to_the_chain_runs_before_the_final_stage PASSED [ 45%]
tests/test_chain.py::test_an_empty_chain_leaves_the_decision_to_the_final_stage[release] PASSED [ 47%]
tests/test_chain.py::test_an_empty_chain_leaves_the_decision_to_the_final_stage[hold] PASSED [ 50%]
tests/test_chain.py::test_describe_names_every_decision[released] PASSED [ 52%]
tests/test_chain.py::test_describe_names_every_decision[held] PASSED     [ 54%]
tests/test_mediator.py::test_release_follows_inspection_then_settlement[mediator] PASSED [ 56%]
tests/test_mediator.py::test_release_follows_inspection_then_settlement[choreography] PASSED [ 59%]
tests/test_mediator.py::test_the_mediator_releases_in_either_order[inspection-first] PASSED [ 61%]
tests/test_mediator.py::test_the_mediator_releases_in_either_order[settlement-first] PASSED [ 63%]
tests/test_mediator.py::test_a_choreography_loses_a_settlement_that_arrives_before_inspection PASSED [ 65%]
tests/test_mediator.py::test_a_duplicate_settlement_releases_once PASSED [ 68%]
tests/test_mediator.py::test_a_failed_inspection_holds_the_consignment PASSED [ 70%]
tests/test_mediator.py::test_a_declaration_with_nothing_outstanding_is_released_at_once PASSED [ 72%]
tests/test_mediator.py::test_a_declaration_that_owes_one_report_is_released_on_that_report[duty-only] PASSED [ 75%]
tests/test_mediator.py::test_a_declaration_that_owes_one_report_is_released_on_that_report[inspection-only] PASSED [ 77%]
tests/test_mediator.py::test_a_message_for_another_consignment_is_refused PASSED [ 79%]
tests/test_mediator.py::test_release_records_a_cleared_handling_event_at_the_port PASSED [ 81%]
tests/test_static.py::test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage PASSED [ 84%]
tests/test_static.py::test_mypy_cannot_see_release_placed_inside_the_chain PASSED [ 86%]
tests/test_static.py::test_mypy_refuses_a_stage_with_the_wrong_return_type PASSED [ 88%]
tests/test_static.py::test_mypy_reports_a_stage_that_falls_off_the_end PASSED [ 90%]
tests/test_static.py::test_mypy_reports_a_decision_left_unhandled PASSED [ 93%]
tests/test_static.py::test_mypy_refuses_a_linked_chain_result_where_a_decision_is_needed PASSED [ 95%]
tests/test_static.py::test_mypy_refuses_a_message_the_mediator_does_not_know PASSED [ 97%]
tests/test_static.py::test_mypy_cannot_exhaust_a_match_on_true_and_false_patterns PASSED [100%]

============================== 44 passed in 3.43s ==============================
Success: no issues found in 8 source files
```

The suite has 28 test functions and 44 cases. `tests/test_chain.py` holds the chain and its comparison forms, `tests/test_mediator.py` the release table with its two coordination forms, and `tests/test_static.py` the mypy witnesses. For how those are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: compute every decision first.** In a scratch copy, replace the loop in `clear` with `decisions = [stage(declaration) for stage in stages]` followed by a loop that returns the first decision that isn't `None`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` prints:

```text
E       AssertionError: assert ['passing', '...ing', 'never'] == ['passing', 'holding']
tests/test_chain.py:107: AssertionError
FAILED tests/test_chain.py::test_stages_after_a_decision_are_not_called - Ass...
1 failed, 43 passed in 3.34s
Success: no issues found in 8 source files
```

The answers are the same, so every table that checks a result passes, and only the test that records which stages ran fails. mypy exits 0, because a list comprehension over the stages is type-correct.

**Experiment two: drop the released check.** In a fresh scratch copy, change the first line of `_try_release` to `if self._outstanding or self._failed:`. The same filter, then mypy, prints:

```text
E       AssertionError: assert 2 == 1
tests/test_mediator.py:91: AssertionError
FAILED tests/test_mediator.py::test_a_duplicate_settlement_releases_once - As...
1 failed, 43 passed in 3.37s
Success: no issues found in 8 source files
```

Only the duplicate settlement fails: after release, a second message calls `_try_release` again and records a second `CLEARED`. The inspection-then-settlement tests send each message once, so they pass. mypy exits 0.

## What you can do now

- Say what survives: the handler class and successor link dissolve into the tuple behind `clear`, and `ClearanceMediator` is a class with a `receive` method and no Colleague base, with the decisions left to you.
- Write the chain: `clear(declaration, stages, /, *, final=release)`, where `None` passes and `final` is a `FinalStage`, witnessed by `test_the_first_stage_that_decides_wins` and `test_stages_after_a_decision_are_not_called`.
- Know what mypy checks: a stage's shape, a final stage that can pass and a missing `match` arm, and not the order, as `test_a_stage_added_after_release_clears_a_restricted_commodity` shows.
- Release once: `ClearanceMediator.receive` and `_try_release`, in either order, witnessed by `test_the_mediator_releases_in_either_order` and experiment two.
- Choose a form: a `match` for closed rules, a signal for independent parties, and the mediator where one rule needs the reports it is owed, as `test_a_choreography_loses_a_settlement_that_arrives_before_inspection` shows.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for both Chain of Responsibility and Mediator. The Python tutorial's [`match` statements](https://docs.python.org/3/tutorial/controlflow.html) cover the pattern syntax `describe` and `receive` use, and [PEP 695](https://peps.python.org/pep-0695/) specifies the `type` statement. The site python-patterns.guide, by Brandon Rhodes, has no page on either pattern in its index. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
