---
title: "State and finite state machines"
order: 14
layout: tutorial
sectionid: docs
part: "selecting-varying-behavior"
description: "State survives because no feature says which transitions are legal; a read-only table, frozen states with a match ending in assert_never, and a seeded transit model make the lifecycle short and checkable."
---

## Learning objectives

By the end of this chapter you can:

- Say why State survives in Python, and which parts of the catalogue's structure the language shortens.
- Write a lifecycle as a read-only table, and say what mypy checks in it and what it leaves to a test.
- Write a lifecycle as frozen states with a `match` that ends in `assert_never`, and say which shapes of `match` let a forgotten state through.
- Choose between the table, the `match` and per-state objects by asking what each state carries and who extends the set.
- Inject a random generator so that a probabilistic machine is reproducible.

## Why this matters

A consignment is booked, loaded, in transit, cleared and delivered, in that order. Three failures come from leaving that order implicit.

A tracking record keeps a `status` field. Nothing stops a caller setting it from delivered back to booked, and nothing says so when it happens. A customs hold is added as a sixth state, and the page that renders each state has a final "anything else" branch, so held consignments render as something they aren't, with no error anywhere. A transit-delay simulation is seeded to make it repeatable, and its result changes anyway, because another part of the program drew from the generator it shares.

Each is a lifecycle problem that the type system and the test suite can be made to see, once the lifecycle is written down as something they can read.

{% include excalidraw.html name="14-state-and-finite-state-machines" caption="Figure 14.1: One consignment lifecycle, two ways to write it. A read-only table maps a status and an event to the next status; a match over frozen states does the same with per-state data, and an injected generator drives transit delays." %}

Read the figure from the top. Two boxes sit above the lifecycle: `TRANSITIONS`, a read-only table keyed by status and event, on the left, and `apply_event`, a match on state ending in `assert_never`, on the right. Dashed arrows run from both into `Booked`, because both forms start there. Below them a column runs `Booked`, `Loaded`, `InTransit`, `Cleared` and `Delivered`, with the arrows labelled `LOADED`, `DEPARTED`, `CLEARED` and `DELIVERED`. `Delivered` is marked terminal. A dashed box beside `InTransit` reads "each day: delay with probability p (injected Random)" and points into it. At the bottom, a dashed arrow labelled "any other event" runs from `Delivered` to the accent box, "illegal event: TransitionError". An illegal event raises from any state, not only from `Delivered`.

## The force that remains

*Design Patterns*, by Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides, catalogues State for an object whose behaviour depends on where it is in a history of transitions. The catalogue's answer is a class per state, with the owning object forwarding each operation to whichever state object it currently holds.

The sorting question from [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) is whether a language feature resolves the force without the pattern's structure. For State it doesn't. The force is that the legal transitions are a business rule that has to be written in one place and checked. Enums, `match` and frozen dataclasses make that place short, and none of them says which transitions are legal. The pattern survives, and the transition table is the design.

Two questions decide the shape. Where are the legal transitions written? And what notices a state that a piece of code forgot?

The tracking events here are a single `HandlingEvent` with a `HandlingKind` field, `BOOKED`, `LOADED`, `DEPARTED`, `CLEARED` or `DELIVERED`, and not a class per event, because the class names in this chapter belong to the states.

## The transition table

When states carry no data of their own, the lifecycle is a mapping from a status and an event kind to the next status:

```python
TRANSITIONS: Mapping[tuple[ConsignmentStatus, HandlingKind], ConsignmentStatus] = frozendict(
    {
        (ConsignmentStatus.BOOKED, HandlingKind.LOADED): ConsignmentStatus.LOADED,
        (ConsignmentStatus.LOADED, HandlingKind.DEPARTED): ConsignmentStatus.IN_TRANSIT,
        (ConsignmentStatus.IN_TRANSIT, HandlingKind.CLEARED): ConsignmentStatus.CLEARED,
        (ConsignmentStatus.CLEARED, HandlingKind.DELIVERED): ConsignmentStatus.DELIVERED,
    }
)


def next_status(status: ConsignmentStatus, kind: HandlingKind) -> ConsignmentStatus:
    """Return the status an event leads to, or refuse it with a domain error."""
    try:
        return TRANSITIONS[status, kind]
    except KeyError:
        raise TransitionError(f"{kind.name} not allowed when {status.name}") from None
```

The table is a `frozendict`, new in 3.15 ([PEP 814](https://peps.python.org/pep-0814/)), typed as a `Mapping` so callers see the read side. `test_the_transition_table_is_read_only` shows that assigning an entry raises `TypeError` and that the table isn't a `dict`. An absent pair is a domain error that names both halves: `test_an_illegal_event_is_a_transition_error` expects `DEPARTED not allowed when BOOKED` from both forms, and `test_a_transition_error_hides_the_key_error` checks that the `KeyError` is suppressed. For dispatch tables as a general technique, see [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}).

Because the table is data, tests can walk it as a graph. `test_every_status_is_reachable_from_booked` does a breadth-first search over its keys, and `test_delivered_is_terminal` feeds every event kind to a delivered consignment and expects a refusal for each. A mutable `status` field offers nothing to walk. `test_a_status_field_accepts_an_illegal_transition` sets one from delivered to booked and nothing raises.

mypy checks what the entries are made of. Swapping the halves of a key is an error, and so is a value of the wrong type. The test runs each snippet through its own mypy helper and the output is quoted as the run printed it:

```text
<string>:10: error: Dict entry 1 has incompatible type "tuple[HandlingKind, ConsignmentStatus]": "ConsignmentStatus"; expected "tuple[ConsignmentStatus, HandlingKind]": "ConsignmentStatus"  [dict-item]
<string>:10: error: Dict entry 1 has incompatible type "tuple[ConsignmentStatus, HandlingKind]": "HandlingKind"; expected "tuple[ConsignmentStatus, HandlingKind]": "ConsignmentStatus"  [dict-item]
```

What mypy can't check is legality. A table with a well-typed entry from delivered back to booked passes with exit status 0 and no output in `test_mypy_checks_table_entry_types_but_not_legality[illegal-pair]`. A repeated key keeps the last value at run time (`test_a_repeated_table_key_keeps_the_last_value`), and mypy is silent about it. ruff isn't: in a scratch file with `(S.CLEARED, K.DELIVERED)` written twice with different values, `ruff check` reported ``F601 Dictionary key literal `(S.CLEARED, K.DELIVERED)` repeated``, mypy reported `Success: no issues found in 1 source file`, and the table held one entry, the second. The graph tests and the linter cover what the type checker leaves open.

## States that carry data: match and assert_never

Some states carry data. A consignment in transit has days sailed and days lost to delay, and a delivered one has neither. The states become frozen dataclasses, so each holds only its own fields. Two of them, and the union:

```python
@dataclass(frozen=True, slots=True)
class InTransit:
    departed_from: str
    days_sailed: int = 0
    delay_days: int = 0


@dataclass(frozen=True, slots=True)
class Delivered:
    port: str


type ConsignmentState = Booked | Loaded | InTransit | Cleared | Delivered
```

`test_each_state_carries_only_its_own_data` shows that `InTransit` has `delay_days`, that a `Delivered` has no such attribute, and that assigning one raises `FrozenInstanceError`. Frozen and slotted dataclasses are the subject of [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}). Here they make each state a value that a transition replaces and doesn't edit.

The transitions are a `match` on the state, with one guarded arm per legal move:

```python
def apply_event(state: ConsignmentState, event: HandlingEvent) -> ConsignmentState:
    """Return the state an event leads to, or refuse it with a domain error."""
    match state:
        case Booked() if event.kind is HandlingKind.LOADED:
            return Loaded(event.location)
        case Loaded() if event.kind is HandlingKind.DEPARTED:
            return InTransit(departed_from=event.location)
        case InTransit() if event.kind is HandlingKind.CLEARED:
            return Cleared(event.location)
        case Cleared() if event.kind is HandlingKind.DELIVERED:
            return Delivered(event.location)
        case Booked() | Loaded() | InTransit() | Cleared() | Delivered():
            raise TransitionError(f"{event.kind.name} not allowed when {status_of(state).name}")
        case _:
            assert_never(state)
```

The second-to-last arm is the illegal arm, and it names every state. The last arm, `case _`, can only be reached by a state the arms above didn't name, and `assert_never` is where the type checker says so. The typing documentation puts the rule this way: "For a call to assert_never to pass type checking, the inferred type of the argument passed in must be the bottom type, Never, and nothing else." The same page adds: "At runtime, this throws an exception when called." The [typing guide on unreachable code and exhaustiveness checking](https://typing.python.org/en/latest/guides/unreachable.html) has more.

Add a `Held` state to the union and mypy reports the call that can now be reached. The snippet is a copy of the source's states and `match` with one more state, and `test_the_static_snippets_mirror_the_source` parses `states.py` and fails if the two drift apart:

```text
<string>:57: error: Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"  [arg-type]
```

An enum works the same way. A status `match` that doesn't name a new `HELD` member reports `Literal[ConsignmentStatus.HELD]` in the same position:

```text
<string>:24: error: Argument 1 to "assert_never" has incompatible type "Literal[ConsignmentStatus.HELD]"; expected "Never"  [arg-type]
```

Two shapes of `match` lose that report. The first is the wildcard illegal arm, the "anything else" branch from the opening. Replace the explicit arm with `case _: raise TransitionError(...)` and the same snippet with `Held` added type-checks with exit status 0 and no output (`test_mypy_cannot_see_a_state_swallowed_by_a_wildcard`). The wildcard handles `Held` without anyone having decided how, and no checker is positioned to object. The second is a match on a tuple of state and kind. mypy 2.4.1 doesn't prove a complete one exhaustive:

```text
<string>:29: error: Argument 1 to "assert_never" has incompatible type "tuple[Booked, K]"; expected "Never"  [arg-type]
```

That snippet is a reduced model, two states and two kinds, covering every pair, and the error is reported on it anyway (`test_mypy_cannot_prove_a_tuple_match_exhaustive`). Match on the state first, then guard on the kind, as `apply_event` does. The finding belongs to this mypy version, and the test pins it, so a release that learns to prove the tuple form will fail it visibly.

`assert_never` is a function, so it isn't an `assert` statement and stripping asserts doesn't remove it. `test_assert_never_raises_even_when_asserts_are_stripped` runs a child interpreter with `-O`, where an `assert False` in the same script does nothing, and the call still exits non-zero with `Expected code to be unreachable, but got: 'x'` on stderr. A run of the same call under Python 3.15.2 printed `AssertionError: Expected code to be unreachable, but got: 'x'`.

The chapter titled [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}) notes that a `match` over an event union is where a missing case becomes visible, and [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) uses the same `match` and `assert_never` to apply amendments. The method behind the snippets, mypy's API run on a source string with the exit status and the error codes asserted, is the one in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

## One lifecycle, two forms

The table and the `match` say the same thing in different places, and that is deliberate. A fixture parametrised over `table` and `match` folds a history of event kinds through each form, so `test_the_lifecycle_runs_booked_to_delivered`, `test_an_illegal_event_is_a_transition_error` and `test_delivered_is_terminal` each run twice from one set of cases. `test_the_two_forms_agree_on_every_status_and_event` then takes every status paired with every event kind and asserts that the forms both refuse with the same message or both reach the same status. A change to one form that the other doesn't follow fails that test.

Pick the table when the states carry no data and the lifecycle should be reviewable as data: a reviewer reads four lines, and a test walks them. Pick the `match` when states carry their own data, as `InTransit` does, or when behaviour differs per state. The `match` form is the one `track` folds over a history, and it refuses an event for another consignment with `test_an_event_for_another_consignment_is_refused`.

## Where state objects still fit

The catalogue's form is a class per state with a method per event. The example keeps one as a test fixture, so that the comparison is measured against the same cases:

<!-- fmt:off -->
```python
class _LifecycleState(Protocol):
    """Comparison fixture: the GoF form, one object per state, each deciding the next state."""

    @property
    def status(self) -> ConsignmentStatus: ...

    def on_event(self, kind: HandlingKind) -> _LifecycleState: ...
```
<!-- fmt:on -->

Five frozen classes implement it, each returning the next state object or raising. `test_state_objects_pass_the_same_lifecycle_table` runs the legal and illegal histories from the shared behaviour table and gets the same statuses and the same messages. The form works. What it costs shows up in two mypy witnesses, which use a reduced Protocol, `LifecycleState`, with one method per event, `on_loaded` and `on_departed` (see [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) for how the matching works).

Adding an operation, say `amendable`, to the Protocol is reported at each return site that now hands back a state without it:

```text
<string>:17: error: Incompatible return value type (got "Loaded", expected "LifecycleState")  [return-value]
<string>:17: note: "Loaded" is missing following "LifecycleState" protocol member:
<string>:17: note:     amendable
```

That's a good report, though it lands where a state is returned and not where the class is written. Adding a state gets no report at all if nothing returns it. A `Held` class that defines only `on_loaded`, and that no other state hands back, is accepted with exit status 0 and empty output (`test_mypy_accepts_a_state_object_nothing_returns`). In the `match` form the opposite holds: a new state is reported at once, at `assert_never`.

So the line is about who extends the set. Where the set of states is open, each state owns several operations, and the people adding states can't edit a central `match`, objects behind a Protocol are the right form. A closed lifecycle owned by one team is a union and a `match`, with a checker that reports a forgotten state.

## A probabilistic machine: transit delays

A voyage isn't deterministic. Each day at sea a consignment is delayed with some probability, and the model draws the day's outcome from a generator it's given:

```python
def sail_one_day(state: InTransit, *, rng: random.Random, delay_probability: float) -> InTransit:
    """Sail one day, or lose it to a delay with the given probability."""
    if rng.random() < delay_probability:
        return replace(state, delay_days=state.delay_days + 1)
    return replace(state, days_sailed=state.days_sailed + 1)
```

The generator is a parameter. The `random` documentation explains why that matters: "The functions supplied by this module are actually bound methods of a hidden instance of the random.Random class. You can instantiate your own instances of Random to get generators that don’t share state." A call to `random.random()` inside the model would draw from that hidden instance, and any other code drawing from it would share state with the model.

With an injected generator the model is reproducible. The same page says: "By reusing a seed value, the same sequence should be reproducible from run to run as long as multiple threads are not running." `test_a_seeded_transit_is_reproducible` runs a 21-day voyage at a delay probability of 0.2 from `Random(7)` twice and gets 11 delay days both times, and gets 3 from `Random(2026)`. The voyage lengths and probabilities are illustrative. A generator that two voyages share is a different matter: `test_a_shared_generator_gives_a_different_second_run` runs two voyages from one `Random(7)` and gets 11 delay days, then 5. `test_transit_delay_bounds` covers probabilities 0 and 1: a voyage is never delayed in the first case and, in the second, stops at the day cap, sixty simulated days, having sailed none. `test_the_day_cap_bounds_the_number_of_draws` counts draws and sees exactly the cap, and `test_a_draw_equal_to_the_probability_is_not_a_delay` pins the strict comparison. `test_the_model_leaves_the_module_generator_alone` reads `random.getstate()` before and after a simulation and finds them equal.

Over 10,000 seeds the same 21-day voyage averaged 5.2758 delay days against 5.25 from the negative-binomial mean, in a run recorded under `_plans/evidence/transit-delay-model.md`. That's a recorded run, and no test asserts it. The same documentation carries a warning that matters if someone reuses the pattern for tokens: "The pseudo-random generators of this module should not be used for security purposes." The model is a simulation, and [`random`](https://docs.python.org/3/library/random.html) is the right module for it.

## When not to use it

A two-state flag is a `bool`. A lifecycle that nothing ever checks, because nothing branches on it, is an enum field. A workflow whose steps are configured by users at run time is data in a store, and a type per step would be a mistake. Ordered processing stages that can stop an item belong with [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}).

<blockquote class="ai-sidebar" markdown="1">
**Reviewing assistant-written state machines.** An assistant asked for "the State pattern" may propose a state class per status with a method per event, a mutable `status` field that any caller can set, or a `match` whose last arm raises for "anything else". Check: is every legal transition written in one place; is an illegal one refused with a domain error; does the `match` name every state before an `assert_never` arm; does a test walk the table for unreachable and terminal states; is any random generator passed in and not drawn from the module.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/14-state-and-finite-state-machines
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
collecting ... collected 40 items

tests/test_lifecycle.py::test_the_lifecycle_runs_booked_to_delivered[table] PASSED [  2%]
tests/test_lifecycle.py::test_the_lifecycle_runs_booked_to_delivered[match] PASSED [  5%]
tests/test_lifecycle.py::test_an_illegal_event_is_a_transition_error[table] PASSED [  7%]
tests/test_lifecycle.py::test_an_illegal_event_is_a_transition_error[match] PASSED [ 10%]
tests/test_lifecycle.py::test_delivered_is_terminal[table] PASSED        [ 12%]
tests/test_lifecycle.py::test_delivered_is_terminal[match] PASSED        [ 15%]
tests/test_lifecycle.py::test_the_two_forms_agree_on_every_status_and_event PASSED [ 17%]
tests/test_lifecycle.py::test_every_status_is_reachable_from_booked PASSED [ 20%]
tests/test_lifecycle.py::test_the_transition_table_is_read_only PASSED   [ 22%]
tests/test_lifecycle.py::test_an_event_for_another_consignment_is_refused PASSED [ 25%]
tests/test_lifecycle.py::test_track_folds_a_history_into_the_final_state PASSED [ 27%]
tests/test_lifecycle.py::test_a_state_keeps_the_location_of_the_event_that_produced_it PASSED [ 30%]
tests/test_lifecycle.py::test_each_state_carries_only_its_own_data PASSED [ 32%]
tests/test_lifecycle.py::test_every_state_and_event_is_frozen PASSED     [ 35%]
tests/test_lifecycle.py::test_a_transition_error_hides_the_key_error PASSED [ 37%]
tests/test_lifecycle.py::test_a_status_field_accepts_an_illegal_transition PASSED [ 40%]
tests/test_state_objects.py::test_state_objects_pass_the_same_lifecycle_table PASSED [ 42%]
tests/test_state_objects.py::test_state_objects_agree_with_the_transition_table PASSED [ 45%]
tests/test_static.py::test_mypy_reports_a_state_missing_from_the_match[dataclass-union] PASSED [ 47%]
tests/test_static.py::test_mypy_reports_a_state_missing_from_the_match[enum] PASSED [ 50%]
tests/test_static.py::test_mypy_cannot_see_a_state_swallowed_by_a_wildcard PASSED [ 52%]
tests/test_static.py::test_mypy_cannot_prove_a_tuple_match_exhaustive PASSED [ 55%]
tests/test_static.py::test_mypy_checks_table_entry_types_but_not_legality[swapped-key] PASSED [ 57%]
tests/test_static.py::test_mypy_checks_table_entry_types_but_not_legality[wrong-value] PASSED [ 60%]
tests/test_static.py::test_mypy_checks_table_entry_types_but_not_legality[illegal-pair] PASSED [ 62%]
tests/test_static.py::test_a_repeated_table_key_keeps_the_last_value PASSED [ 65%]
tests/test_static.py::test_assert_never_raises_even_when_asserts_are_stripped PASSED [ 67%]
tests/test_static.py::test_mypy_reports_an_operation_missing_from_a_state_object PASSED [ 70%]
tests/test_static.py::test_mypy_accepts_a_state_object_nothing_returns PASSED [ 72%]
tests/test_static.py::test_the_static_snippets_mirror_the_source PASSED  [ 75%]
tests/test_transit.py::test_a_seeded_transit_is_reproducible PASSED      [ 77%]
tests/test_transit.py::test_a_shared_generator_gives_a_different_second_run PASSED [ 80%]
tests/test_transit.py::test_transit_delay_bounds[never-delayed] PASSED   [ 82%]
tests/test_transit.py::test_transit_delay_bounds[always-delayed] PASSED  [ 85%]
tests/test_transit.py::test_a_draw_equal_to_the_probability_is_not_a_delay PASSED [ 87%]
tests/test_transit.py::test_a_draw_below_the_probability_is_a_delay PASSED [ 90%]
tests/test_transit.py::test_the_day_cap_bounds_the_number_of_draws PASSED [ 92%]
tests/test_transit.py::test_a_voyage_stops_drawing_once_the_schedule_is_sailed PASSED [ 95%]
tests/test_transit.py::test_sailing_a_day_leaves_the_earlier_state_unchanged PASSED [ 97%]
tests/test_transit.py::test_the_model_leaves_the_module_generator_alone PASSED [100%]

============================== 40 passed in 4.32s ==============================
Success: no issues found in 10 source files
```

The suite has 33 test functions and 40 cases. The cases are doubled where one behaviour table runs through the table and the `match`, and the static witnesses carry the mypy snippets.

**Experiment one: add a state without touching a `match`.** In a scratch copy, add a frozen `Held` dataclass with a `port` field and put it in the `ConsignmentState` union. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then the member's mypy run gives:

```text
E       AssertionError: assert 'Booked | Loa...ivered | Held' == 'Booked | Loa...| Held | Held'
tests/test_static.py:390: AssertionError
FAILED tests/test_static.py::test_the_static_snippets_mirror_the_source - Ass...
1 failed, 39 passed in 4.19s
src/state_machines/states.py:65: error: Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"  [arg-type]
src/state_machines/states.py:82: error: Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"  [arg-type]
Found 2 errors in 1 file (checked 10 source files)
```

mypy reports both functions that match on the state, `status_of` and `apply_event`, each at its `assert_never`. pytest passes all but one test, and the one that fails is the guard on the snippets: the static witnesses re-declare the union, and `test_the_static_snippets_mirror_the_source` sees that the source's union no longer matches theirs. No behaviour test notices a new state. The type checker does.

**Experiment two: add an illegal entry to the table.** In a fresh scratch copy, add `(ConsignmentStatus.DELIVERED, HandlingKind.BOOKED): ConsignmentStatus.BOOKED` to `TRANSITIONS`. The same filtered run, then mypy, gives:

```text
tests/test_lifecycle.py:85: AssertionError
E       assert (<ConsignmentStatus.DELIVERED: 5>, <HandlingKind.BOOKED: 1>) not in frozendict({(<ConsignmentStatus.BOOKED: 1>, <HandlingKind.LOADED: 2>): <ConsignmentStatus.LOADED: 2>, (<ConsignmentSta...mentStatus.DELIVERED: 5>, (<ConsignmentStatus.DELIVERED: 5>, <HandlingKind.BOOKED: 1>): <ConsignmentStatus.BOOKED: 1>})
tests/test_lifecycle.py:104: AssertionError
E       state_machines.domain.TransitionError: BOOKED not allowed when DELIVERED
tests/test_state_objects.py:81: TransitionError
FAILED tests/test_lifecycle.py::test_delivered_is_terminal[table] - Failed: D...
FAILED tests/test_lifecycle.py::test_the_two_forms_agree_on_every_status_and_event
FAILED tests/test_lifecycle.py::test_the_transition_table_is_read_only - asse...
FAILED tests/test_state_objects.py::test_state_objects_agree_with_the_transition_table
4 failed, 36 passed in 4.22s
Success: no issues found in 10 source files
```

mypy reports success, because the entry is well typed. Four tests fail. `test_delivered_is_terminal[table]` fails because delivered now accepts a booking event, and the `[match]` case still passes. `test_the_two_forms_agree_on_every_status_and_event` fails because the forms disagree on that pair. `test_state_objects_agree_with_the_transition_table` fails on the same disagreement from the object side. `test_the_transition_table_is_read_only` fails on its `assert key not in TRANSITIONS`, since that key is now present. A table is checked by the tests that read it as a graph and by the forms that must agree with it, and not by mypy.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for State. The language references are the [`typing` documentation](https://docs.python.org/3/library/typing.html) for `assert_never`, the typing guide on [unreachable code and exhaustiveness checking](https://typing.python.org/en/latest/guides/unreachable.html), [PEP 634](https://peps.python.org/pep-0634/) and [PEP 636](https://peps.python.org/pep-0636/) for structural pattern matching, [PEP 814](https://peps.python.org/pep-0814/) for `frozendict`, and the [`random`](https://docs.python.org/3/library/random.html) documentation on reproducibility.

Luciano Ramalho's *Fluent Python*, second edition, has the chapter "with, match, and else Blocks" on `match`. Both books are in the hub's list and on the [bibliography page]({{ '/bibliography/' | relative_url }}).
