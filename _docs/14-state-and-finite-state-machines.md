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

A consignment is booked, loaded, in transit, cleared and delivered, in that order. Leave the order implicit and nothing stops a step backwards, a new state slips past every branch, and a seeded simulation stops repeating. Python shortens the State pattern's structure but doesn't write down which transitions are legal.

{% include excalidraw.html name="14-state-and-finite-state-machines" described="true" caption="Figure 14.1: One consignment lifecycle, two ways to write it. A read-only table maps a status and an event to the next status; a match over frozen states does the same with per-state data, and any other pair is refused. An injected generator drives delays." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-14-state-and-finite-state-machines" markdown="1">
`TRANSITIONS`, a read-only table, and `apply_event`, a match ending in `assert_never`, both lead into the lifecycle `Booked`, `Loaded`, `InTransit`, `Cleared` and `Delivered`, the terminal state. A dashed box beside `InTransit` reads "each day: delay with probability p (injected Random)". Dashed arrows run from every status, `Delivered` included, to the accent box, "any pair outside the lifecycle: TransitionError". Both forms refuse every status and event pair that isn't one of the four steps.
</div>
</details>

The figure shows the two forms of one lifecycle, both refusing any pair outside it.

## Pattern: State

### The problem

A tracking service applies handling events to consignments. Three failures come from leaving the lifecycle implicit:

- A tracking record keeps a `status` field. Nothing stops a caller setting it from delivered back to booked, and nothing says so when it happens.
- A customs hold is added as a sixth state. The code that handles each state has a final "anything else" branch, so held consignments are treated as something they aren't, with no error anywhere.
- A transit-delay simulation is seeded to make it repeatable, and its result changes anyway, because another part of the program drew from the generator it shares.

The force is that the legal transitions are a business rule that has to be written in one place and checked.

### The solution

A **State** machine makes an object's behaviour depend on where it is in a history of transitions, and refuses any transition the lifecycle doesn't allow.

**Bucket: survives.** Enums, `match` and frozen dataclasses make the one place short, and none of them says which transitions are legal: the transition table is the design.

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) uses a class per state, with the owning object forwarding each operation to the state object it holds. In Python, two questions decide the shape: where are the legal transitions written, and what notices a state that a piece of code forgot?

| Form | Use it when |
| --- | --- |
| Read-only transition table | states carry no data, and the lifecycle should be reviewable as data |
| Frozen states and a `match` | states carry their own data, or behaviour differs per state, and one team owns the set |
| State objects behind a Protocol | the set of states is open, each owns several operations, and whoever adds states can't edit a central `match` |

The tracking events are one `HandlingEvent` with a `HandlingKind` field, `BOOKED`, `LOADED`, `DEPARTED`, `CLEARED` or `DELIVERED`, not a class per event, because the class names belong to the states.

### How Python models it

When states carry no data, the lifecycle is a mapping from a status and an event kind to the next status:

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

The table is a `frozendict`, new in 3.15 ([PEP 814](https://peps.python.org/pep-0814/)), typed as a `Mapping` so callers see the read side; assigning an entry raises `TypeError`. An absent pair is a domain error that names both halves, `DEPARTED not allowed when BOOKED`, with the `KeyError` suppressed. For dispatch tables in general, see [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}).

Because the table is data, a test can walk it as a graph: every status is reachable from booked, and delivered refuses every event kind. A mutable `status` field offers nothing to walk, and setting it from delivered to booked raises nothing.

### What mypy checks in a table

mypy checks what the entries are made of. Swapping the halves of a key is an error, and so is a value of the wrong type:

```text
<string>:10: error: Dict entry 1 has incompatible type "tuple[HandlingKind, ConsignmentStatus]": "ConsignmentStatus"; expected "tuple[ConsignmentStatus, HandlingKind]": "ConsignmentStatus"  [dict-item]
<string>:10: error: Dict entry 1 has incompatible type "tuple[ConsignmentStatus, HandlingKind]": "HandlingKind"; expected "tuple[ConsignmentStatus, HandlingKind]": "ConsignmentStatus"  [dict-item]
```

What mypy can't check is legality. A well-typed entry from delivered back to booked is clean. A repeated key keeps the last value at run time, and mypy is silent about that too. ruff isn't: with `(S.CLEARED, K.DELIVERED)` written twice, `ruff check` reports ``F601 Dictionary key literal `(S.CLEARED, K.DELIVERED)` repeated``. Graph tests and the linter cover what the type checker leaves open.

### States that carry data: match and assert_never

A consignment in transit has days sailed and days lost to delay, and a delivered one has neither. The states become frozen dataclasses, each holding only its own fields. Two of them, and the union:

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

A `Delivered` has no `delay_days`, and assigning to a state raises `FrozenInstanceError`, so a transition replaces a state and never edits it; see [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}). The transitions are a `match` on the state, with one guarded arm per legal move:

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

Only a state the arms above didn't name reaches `case _`, and `assert_never` is where the type checker says so. The typing documentation puts the rule this way: "For a call to assert_never to pass type checking, the inferred type of the argument passed in must be the bottom type, Never, and nothing else." The same page adds: "At runtime, this throws an exception when called." The [typing guide on unreachable code and exhaustiveness checking](https://typing.python.org/en/latest/guides/unreachable.html) has more.

Add a `Held` state to the union and mypy reports the call that can now be reached:

```text
<string>:57: error: Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"  [arg-type]
```

An enum works the same way. A status `match` that doesn't name a new `HELD` member reports `Literal[ConsignmentStatus.HELD]` in the same position:

```text
<string>:24: error: Argument 1 to "assert_never" has incompatible type "Literal[ConsignmentStatus.HELD]"; expected "Never"  [arg-type]
```

Two shapes of `match` lose that report:

- **A wildcard illegal arm.** Replace the explicit arm with `case _: raise TransitionError(...)`, add `Held`, and mypy is clean. The wildcard handles `Held` without anyone having decided how. This is the "anything else" branch from the problem.
- **A match on a tuple of state and kind.** mypy 2.4.1 doesn't prove a complete one exhaustive. On a reduced model, two states and two kinds with every pair covered, it still reports:

```text
<string>:29: error: Argument 1 to "assert_never" has incompatible type "tuple[Booked, K]"; expected "Never"  [arg-type]
```

Match on the state first, then guard on the kind, as `apply_event` does. The tuple finding belongs to this mypy version, and it's pinned, so a release that learns to prove the tuple form will show up as a failure.

`assert_never` is a function, not an `assert` statement, so `-O` doesn't remove it. Under `-O`, where `assert False` does nothing, the call still exits non-zero with `Expected code to be unreachable, but got: 'x'` on stderr. A run of the same call under Python 3.15.2 printed `AssertionError: Expected code to be unreachable, but got: 'x'`.

[Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) uses the same `match` and `assert_never` to apply amendments.

### One lifecycle, two forms

The table and the `match` say the same thing in different places, so each can be held to the other. One set of cases runs through both forms: the full lifecycle, the illegal event and the terminal state. Every status paired with every event kind must then give the same refusal message or the same next status in both. A change to one form that the other doesn't follow fails. The `match` form is the one `track` folds over a history, and it refuses an event for another consignment.

### Where state objects still fit

The catalogue's form is a class per state with a method per event. It's kept as a comparison against the same cases:

<!-- fmt:off -->
```python
class _LifecycleState(Protocol):
    """Comparison fixture: the GoF form, one object per state, each deciding the next state."""

    @property
    def status(self) -> ConsignmentStatus: ...

    def on_event(self, kind: HandlingKind) -> _LifecycleState: ...
```
<!-- fmt:on -->

Five frozen classes implement it, each returning the next state object or raising, and they pass the same legal and illegal histories with the same messages. The cost shows in mypy, using a reduced `LifecycleState` Protocol with `on_loaded` and `on_departed`; [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers the matching rules.

Adding an operation, say `amendable`, to the Protocol is reported at each return site that hands back a state without it:

```text
<string>:17: error: Incompatible return value type (got "Loaded", expected "LifecycleState")  [return-value]
<string>:17: note: "Loaded" is missing following "LifecycleState" protocol member:
<string>:17: note:     amendable
```

The report lands where a state is returned, not where the class is written. Adding a state gets no report at all if nothing returns it: a `Held` class that defines only `on_loaded`, and that no other state hands back, is clean. In the `match` form a new state is reported at once, at `assert_never`. So the choice turns on who extends the set, as the table under the solution shows.

### A probabilistic machine: transit delays

A voyage isn't deterministic. Each day at sea a consignment is delayed with some probability, drawn from a generator the model is given:

```python
def sail_one_day(state: InTransit, *, rng: random.Random, delay_probability: float) -> InTransit:
    """Sail one day, or lose it to a delay with the given probability."""
    if rng.random() < delay_probability:
        return replace(state, delay_days=state.delay_days + 1)
    return replace(state, days_sailed=state.days_sailed + 1)
```

The `random` documentation says: "The functions supplied by this module are actually bound methods of a hidden instance of the random.Random class. You can instantiate your own instances of Random to get generators that don’t share state." A call to `random.random()` inside the model would share that hidden instance with any other code that draws from it.

With an injected generator the model is reproducible. The same page says: "By reusing a seed value, the same sequence should be reproducible from run to run as long as multiple threads are not running." The voyage lengths and probabilities here are illustrative:

| 21-day voyage, delay probability 0.2 | Delay days |
| --- | --- |
| `Random(7)`, run twice | 11, then 11 |
| `Random(2026)` | 3 |
| One `Random(7)` shared by two voyages | 11, then 5 |

At probability 0 a voyage is never delayed. At 1 it stops at the day cap, sixty simulated days, having sailed none, after exactly that many draws. A draw equal to the probability isn't a delay, and the module generator's state is unchanged by a simulation.

Over 10,000 seeds the same voyage averaged 5.2758 delay days against 5.25 from the negative-binomial mean, in a recorded run on Python 3.15.2 that no assertion checks. The documentation also warns: "The pseudo-random generators of this module should not be used for security purposes." The model is a simulation, so the warning doesn't apply.

## When not to use it

- **State.** A two-state flag is a `bool`. A lifecycle that nothing ever checks, because nothing branches on it, is an enum field. A workflow whose steps users configure at run time is data in a store, and a type per step would be a mistake. Ordered processing stages that can stop an item belong with [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}).

> **🤖 Explore with your agent**
>
> "Write the lifecycle as `TRANSITIONS`, a read-only `frozendict` from `(ConsignmentStatus, HandlingKind)` to the next status, and raise `TransitionError`, naming both halves, for an absent pair. Where states carry data, make them frozen dataclasses in a union and write `apply_event` as a `match` on the state with an arm per state and `assert_never` last, no wildcard. Pass a `random.Random` in for delays. Test that every status is reachable and `DELIVERED` is terminal."
>
> If the `match` ends in `case _: raise`, ask what mypy reports when a state is added.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/14-state-and-finite-state-machines
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 40 cases pass, with one behaviour table run through both forms, and mypy reports `Success: no issues found in 10 source files`. Two experiments, each in a scratch copy:

- **Add a state without touching a `match`.** Add a frozen `Held` with a `port` field to the `ConsignmentState` union. mypy reports `assert_never` in both `status_of` and `apply_event`. No behaviour test notices; the one pytest failure is the guard that keeps the mypy snippets in step with the source union.
- **Add an illegal entry to the table.** Add `(ConsignmentStatus.DELIVERED, HandlingKind.BOOKED): ConsignmentStatus.BOOKED` to `TRANSITIONS`. mypy stays green, because the entry is well typed. Four tests fail: delivered is no longer terminal in the table form, the table and the `match` disagree on that pair, the state objects disagree too, and the key is no longer absent.

## What you can do now

- Say why State survives: no feature says which transitions are legal, so `TRANSITIONS` and `apply_event` write them down.
- Write the table, walk it as a graph, and know that mypy accepts an illegal pair.
- Write the `match` ending in `assert_never`, and avoid the wildcard and tuple shapes that lose its report.
- Choose between table, `match` and objects by what states carry and who extends the set.
- Make delays reproducible by passing a `random.Random` in, never sharing it between runs.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for State. The language references are the [`typing` documentation](https://docs.python.org/3/library/typing.html) for `assert_never`, the typing guide on [unreachable code and exhaustiveness checking](https://typing.python.org/en/latest/guides/unreachable.html), [PEP 634](https://peps.python.org/pep-0634/) and [PEP 636](https://peps.python.org/pep-0636/) for structural pattern matching, [PEP 814](https://peps.python.org/pep-0814/) for `frozendict`, and the [`random`](https://docs.python.org/3/library/random.html) documentation on reproducibility.

Luciano Ramalho's *Fluent Python*, second edition, covers `match` in "with, match, and else Blocks". Both books are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
