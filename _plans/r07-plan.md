---
title: "r07 plan: chapters 14-15 (Part 5, State and Command)"
order: 7
output: false
render_with_liquid: false
---

# r07: chapters 14-15, State and Command

Opus-planned 2026-11-04. Branch `release/r07` (from main at b393443). This file is the source of truth for r07 scope, criteria and status. Executors never edit it; the orchestrator updates the status board. There's no toolchain work this iteration: Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged, and `uv.lock` changes only because two members are added.

## User decisions (2026-11-04, confirmed by the owner)

Owner answers 2026-11-04: every decision below takes the recommended option (chapter 14 table + match forms with the state-object form as a test fixture; chapter 15 frozen amendment values with the inverse computed at run time; H step ids; plain state names; inverse operations taught, snapshots one paragraph; small seeded transit-delay model; no new books, no hub PR; no Command class count).

1. **Step ids are `H*`, not `G*`.** `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md` (`scripts/validate.py` line 731 globs them all). r06 used `G0`-`G7` and every one is `done`, so an r07 `run: G5` would resolve against r06's row without any r07 proof. r07 uses `H0`, `H1a`, `H1b`, `H2`-`H7`, which appear in no other plan. The section structure is r06's.

   **Recommend: yes.** If you want `G*` kept, `validate.py` has to scope `run:` tokens to the plan that owns the row first. That's a script change and a self-test case, so it would add a step.
2. **Chapter 14 has two forms in `src/` and one comparison fixture in `tests/`.**
   - **The table form.** A read-only `TRANSITIONS: Mapping[tuple[ConsignmentStatus, HandlingKind], ConsignmentStatus]` (a 3.15 `frozendict`) and `next_status(status, kind)`. This is the "transition table is the design" that "The three-way split: dissolve, survive, disambiguate" promised. It suits states that carry no data, and it can be inspected: tests walk it as a graph.
   - **The match form.** Frozen dataclass states under `type ConsignmentState = Booked | Loaded | InTransit | Cleared | Delivered`, and `apply_event(state, event)` by `match`. The arm for illegal transitions names every state explicitly, and the last arm is `case _: assert_never(state)`. This suits states that carry their own data (`InTransit.delay_days`), and mypy reports a state that a `match` forgets.
   - **One behaviour table runs both forms** (`[table|match]`, the r06 `[hooks|template]` precedent). A product test holds the two forms to the same answer for every (status, event kind) pair.
   - **The GoF state-object form is a test-only comparison fixture.** It has a `_LifecycleState` Protocol with one method per event, and state classes that return the next state. It runs the same behaviour table. Two mypy witnesses measure the trade-off:
     - adding an operation fails at every return site in the object form;
     - adding a state fails at `assert_never` in the match form;
     - a state class that nothing returns is never checked.
   - Chapter 14 may show **one** short excerpt of the fixture, inside the six-excerpt limit, under the CLAUDE.md comparison rule. The match form is taught as the answer, and the prose says where the object form survives.

   **Recommend: yes.** Alternatives:
   - (b) The enum table only, with `match` used just for per-status behaviour. That drops the frozen dataclass states that domain row 14 names, and the `type State = A | B | C` exhaustiveness witness.
   - (c) The match form only, with the table described in prose. That leaves "the transition table is the design" without reader-facing code.
3. **Chapter 14 names.** States are frozen dataclasses named for the status: `Booked`, `Loaded`, `InTransit`, `Cleared`, `Delivered`. Events are the single-class form the domain standard allows, `HandlingEvent(consignment_id, kind: HandlingKind, location)`, and the chapter says once which form it picked and why: the class names belong to the states here. `HandlingKind` keeps the members used by the ISP/DIP and data-model members (`BOOKED`, `LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED`). `ConsignmentStatus` is `BOOKED`, `LOADED`, `IN_TRANSIT`, `CLEARED`, `DELIVERED`, which follows domain row 14's "in transit".

   **Recommend: yes.** The alternative is `BookedState` and so on. "Naming patterns for teams and AI assistants" argues against mode-suffix names such as `LoadState`.
4. **Chapter 15's `Amendment` is a closed union of frozen command values, and `apply` returns the inverse.**
   - `type Amendment = Reweigh | Redirect | SetInstructions`.
   - `apply(request, amendment) -> tuple[BookingRequest, Amendment]` matches on the amendment (ending in `assert_never`). It returns the amended request and the amendment that reverses it, computed from the request it actually amended.
   - Commands are data: they compare, hash and print by value, and they're queued in a `collections.deque`.
   - Domain row 15 says "frozen `Amendment` dataclass, `apply`/`undo` callables". It is updated at H0 to "`Amendment` union of frozen dataclasses; `apply` returns the inverse", and the chapter says once why it doesn't hold `apply`/`undo` callables. A command holding callables captures its undo data when it is built, which is the stale-inverse failure below, and it has neither value equality nor a stable repr (chapter 12's evidence).

   **Recommend: yes.** The alternative (b) is a single `Amendment(apply, undo)` with callable fields, which is literally the row's wording. It reproduces the failure the chapter warns about, so it would have to be taught as the comparison rather than the answer.
5. **The ground between chapter 15 and its neighbours.**
   - Chapter 15 teaches undo by **inverse operations computed at apply time**.
   - **Immutable snapshots** get one paragraph and one test (`test_a_frozen_request_is_a_safe_snapshot`), with a pointer to "Visitor, Memento, and Interpreter". Domain row 25 keeps snapshot rollback and "a mutated memento corrupts rollback" there.
   - "Frozen is shallow" is taught in "Dataclasses and value semantics" (`test_frozen_is_shallow`), so chapter 15 gives one sentence and a pointer, and teaches only the consequence for undo.
   - The shallow copy that shares a list belongs to "Builder, dataclasses, and Prototype". No `copy` module appears.

   **Recommend: yes.**
6. **No new books.**
   - GoF (State, Command) and Ramalho's *Fluent Python* 2nd ed. are the books both chapters credit. The chapter title "with, match, and else Blocks" was verified from the book's code repository README (https://github.com/fluentpython/example-code-2e). The book is cited for `match` as further reading only.
   - Chapter 15 also credits Percival and Gregory's *Architecture Patterns with Python*, chapter "Commands and Command Handler" (title verified on https://www.cosmicpython.com/book/preface.html). It's credited for queued commands handled by a handler, as further reading. No text or example is used.
   - All three are already in `bibliography.html` and in hub `books.yml` with `design-patterns-with-python` in `referenced_by`, so there's **no hub PR this iteration**.
   - *Fluent Python*'s Command treatment ("Design Patterns with First-Class Functions") is bracketed: credit it only if a prose agent verifies on the page that the chapter covers Command.

   **Recommend: yes.** If you want Viafore's *Robust Python* (it isn't in the bibliography), add step H0b: verify the edition, add the bibliography row and the hub entry, and open the hub PR at H7.
7. **The probabilistic variant is bounded to one function pair and four tests.**
   - `sail_one_day(state, *, rng, delay_probability)` and `simulate_transit(state, *, rng, delay_probability, scheduled_days, max_days)` act on `InTransit`. The `random.Random` is injected, and the probability is a float.
   - The tests are:
     - exact delays for pinned seeds, which the `random` docs' reproducibility guarantee covers;
     - a shared generator giving a different second run;
     - the bounds at probability 0 and 1;
     - the module-level generator's state left unchanged.
   - The 10,000-seed mean (5.2758 against the negative-binomial expectation 5.25) is recorded evidence only (`_plans/evidence/transit-delay-model.md`, written at H1a), never an assertion.

   **Recommend: yes.** The alternative is a Markov chain over every state, which would double chapter 14's example for a series-parity requirement.
8. **Reconciliation row 1's Command counts.** Row 1 moved "type and line counts" to the Command chapter.

   **Recommend:** don't count types for Command. Command survives, so there's no "same table, fewer classes" claim to make. Chapter 15 witnesses the split instead (the deferred call is a partial with no inverse; undo needs data the call never kept). Row 1 gets the note "Command split witnessed by rows 80-81 (r07); no type count, because the pattern survives". If you say no, add an `ast` count test in the r06 row 65 shape, comparing GoF command classes in a fixture against the three amendment values.

## Planning evidence

All runs were read-only, from the session scratch directory outside the repo (`.../scratchpad/r07plan`):
- Runtime: `~/.local/bin/python3.15 -I` (3.15.2).
- mypy: `uv run --no-project --python 3.15.2 --with mypy==2.4.1 python runmypy.py`, which calls `mypy.api.run(['--strict', '--cache-dir', os.devnull, '--no-error-summary', '-c', SNIPPET])`. `--warn-unreachable` was added where noted, to match the root config.

Each item below becomes a test or a reconciliation row. The plan relies on nothing else, and every experiment output is a prediction until the build quotes it as observed.

mypy 2.4.1, chapter 14:
- **A state added to the union.** A five-state `type ConsignmentState = Booked | Loaded | InTransit | Cleared | Delivered` uses guarded arms (`case Booked() if event.kind is HandlingKind.LOADED:`), then an explicit illegal arm `case Booked() | Loaded() | InTransit() | Cleared() | Delivered(): raise TransitionError(...)`, then `case _: assert_never(state)`. It exits 0, also with `--warn-unreachable`. Adding `Held` to the union only:
  `<string>:50: error: Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"  [arg-type]`
- **A wildcard illegal arm swallows the new state.** With `Held` added, replace the explicit illegal arm and the `assert_never` arm with `case _: raise TransitionError("illegal")`. It exits 0 with empty output, so mypy can't see the forgotten state.
- **A tuple match isn't proved exhaustive (surprise).** `match (s, k):` with `case (Booked(), K.LOADED)`, `case (Booked(), K.DEPARTED) | (Loaded(), _)` and `case _: assert_never((s, k))` covers every pair of a two-state union and a two-member enum, yet mypy reports:
  `<string>:20: error: Argument 1 to "assert_never" has incompatible type "tuple[Booked, K]"; expected "Never"  [arg-type]`
  With a third state `Held` the type is `"tuple[Booked | Held, K]"`. So match on the state first and handle the event inside each arm. The match form does that.
- **An enum member added.** `match status:` with or-patterns of `ConsignmentStatus` members, after adding `HELD`:
  `<string>:12: error: Argument 1 to "assert_never" has incompatible type "Literal[ConsignmentStatus.HELD]"; expected "Never"  [arg-type]`
- **The transition table, `Mapping[tuple[ConsignmentStatus, HandlingKind], ConsignmentStatus] = frozendict({...})`.** Each entry is checked as `[dict-item]`:
  - a swapped key: `Dict entry 5 has incompatible type "tuple[HandlingKind, ConsignmentStatus]": "ConsignmentStatus"; expected "tuple[ConsignmentStatus, HandlingKind]": "ConsignmentStatus"  [dict-item]`;
  - a wrong value type: `Dict entry 7 has incompatible type "tuple[ConsignmentStatus, HandlingKind]": "HandlingKind"; expected "tuple[ConsignmentStatus, HandlingKind]": "ConsignmentStatus"  [dict-item]`.
- **What mypy doesn't check in the table.**
  - A well-typed illegal entry `(S.DELIVERED, K.BOOKED): S.BOOKED` exits 0.
  - Duplicate keys (`(S.CLEARED, K.DELIVERED)` twice) get no mypy message. ruff 0.17.3 reports `F601 Dictionary key literal `(S.CLEARED, K.DELIVERED)` repeated` (F is in the root `select`).
  - `TRANSITIONS.get(...)` reveals `"__main__.ConsignmentStatus | None"`.
- **The state-object form** (Protocol `LifecycleState` with `on_loaded`, `on_departed`, `amendable`; frozen state classes):
  - A class missing a newly added operation, returned from another state's method, gives:
    `<string>:15: error: Incompatible return value type (got "Loaded", expected "LifecycleState")  [return-value]`, then `<string>:15: note: "Loaded" is missing following "LifecycleState" protocol member:` and `<string>:15: note:     amendable`.
  - A complete set exits 0.
  - A new state class `Held` that defines only `on_loaded` and that nothing returns exits 0: it is never checked.

Runtime (3.15.2), chapter 14:
- `assert_never("x")` raises `AssertionError("Expected code to be unreachable, but got: 'x'")`. It still raises under `python -O`, because it's a function call and not an `assert` statement.
- A `frozendict` literal with a repeated key keeps the last value: `frozendict({('x', 1): 2})`.
- The transit model: `InTransit("NLRTM")`, `delay_probability=0.2`, `scheduled_days=21`, `max_days=60`.
  - `Random(1)`, `Random(7)`, `Random(42)` and `Random(2026)` give delays of 7, 11, 9 and 3, the same on every repeat.
  - One shared `Random(7)` used for two runs gives 11, then 5.
  - A fresh `Random(7)` per run gives 11 and 11.
  - **Surprise:** one extra draw on `Random(7)` before the run also gave 11, so an "offset by one draw" test would pass by coincidence. The witness uses the second run on a shared generator.
  - Probability 0 gives `InTransit(departed_from='NLRTM', days_sailed=21, delay_days=0)`. Probability 1 never sails; the plan's version stops at `max_days` (`days_sailed=0, delay_days=60`).
  - `Random(7).random()` is `0.32383276483316237`.
  - Over seeds 0-9999 (`max_days=200`), the mean delay is 5.2758, against 21 x 0.2 / 0.8 = 5.25. Evidence only.
  - `random.random.__self__ is random._inst` is `True`, so the module functions share one hidden `Random`. The prose quotes the docs on this, never `_inst`.

mypy 2.4.1, chapter 15:
- `type Amendment = Reweigh | Redirect | SetInstruction` with `apply(request, amendment) -> tuple[BookingRequest, Amendment]` by `match` ending in `assert_never`. Positional class patterns on slotted frozen dataclasses, `replace`, `frozendict` fields and `deque` fields with `default_factory` all exit 0, also with `--warn-unreachable`. Adding `Insure` to the union only:
  `<string>:51: error: Argument 1 to "assert_never" has incompatible type "Insure"; expected "Never"  [arg-type]`
- Passing a `dict` to a `frozendict[str, str]` field:
  `<string>:6: error: Argument 1 to "SetInstructions" has incompatible type "dict[str, str]"; expected "frozendict[str, str]"  [arg-type]`
  The same `dict` passed to a `dict[str, str]` field in a frozen dataclass is accepted.
- Item assignment into a `frozendict[str, str]` field:
  `error: Unsupported target for indexed assignment ("frozendict[str, str]")  [index]`

Runtime (3.15.2), chapter 15:
- **Undo through inverses computed at apply time.** Four amendments (`Reweigh`, two `SetInstruction`, `Redirect`) undone four times give a request equal to the original. The inverses printed in order are `Reweigh(weight=Weight(kilograms=Decimal('120')))`, `SetInstruction(key='handling', text=None)`, `SetInstruction(key='handling', text='keep dry')`, `Redirect(destination='SGSIN')`. Redo then restores `Decimal('130')`.
- **The documented failure.** Commands share a mutable mapping (a frozen dataclass with a `dict` field; the caller reuses one `notes` dict for two commands and changes it between them). After one undo, the instructions read `{'handling': 'fragile'}` where `keep dry` was expected.
- **The stale inverse.** The chapter 3 shape (`before` recorded when the command is built), queued twice from weight 120 to 130 and then 140, gives 120 after one undo where 130 was expected.
- **`frozendict` facts.**
  - `fd | {"b": "2"}` is a `frozendict`, and `{"b": "2"} | fd` is a `dict`.
  - Item assignment raises `'frozendict' object does not support item assignment`.
  - Equal frozendicts hash equal.
  - A frozen dataclass field defaulting to `frozendict()` is allowed, and the default is shared (`is`). A `dict` default raises `ValueError: mutable default <class 'dict'> for field instructions is not allowed: use default_factory`.
- **`deque` facts.**
  - `deque(maxlen=3)` after appending 0-4 is `deque([2, 3, 4], maxlen=3)`.
  - `popleft()` and `pop()` on an empty deque raise `IndexError('pop from an empty deque')`.
- **Value commands against partials.** `FrozenInstanceError("cannot assign to field 'kg'")` on assignment to a frozen field. Two equal command values compare and hash equal and repr as `W(kg=1)`. Two equal partials compare `False`.

What's New in 3.15 (fetched 2026-11-04, https://docs.python.org/3.15/whatsnew/3.15.html, both halves of the page read):
- `match`: one entry: "Unary plus is now accepted in `match` literal patterns, mirroring the existing support for unary minus." Irrelevant here.
- dataclasses: "Annotations for generated `__init__` methods no longer include internal type names." Irrelevant.
- collections: only `Counter.__xor__`/`__ixor__`. Nothing for `deque`.
- enum, random, `assert_never`/`Never`: no entries.
- **Relevant:** PEP 814 `frozendict` ("It does not allow modification after creation. A `frozendict` is not a subclass of `dict`; it inherits directly from `object`. A `frozendict` is hashable as long as all of its keys and values are hashable."). It's used for both transition tables and for the chapter 15 `instructions` field, where it is the fix for the documented failure.
- PEP 661 `sentinel` was considered and isn't needed: `SetInstructions` replaces the whole mapping, so no "absent" marker is required.

Sources fetched 2026-11-04. The prose agents re-fetch them and quote exactly; the fetch tool paraphrases punctuation, so the page text wins.
- typing docs, `assert_never` (https://docs.python.org/3/library/typing.html#typing.assert_never): "Ask a static type checker to confirm that a line of code is unreachable." and "At runtime, this throws an exception when called." "Added in version 3.11." It links to the typing guide.
- Typing guide "Unreachable Code and Exhaustiveness Checking" (https://typing.python.org/en/latest/guides/unreachable.html): "The `Never` type can be leveraged to perform static exhaustiveness checking". The enum-member sentence is to be confirmed on the page.
- random docs (https://docs.python.org/3/library/random.html):
  - "The functions supplied by this module are actually bound methods of a hidden instance of the random.Random class. You can instantiate your own instances of Random to get generators that don't share state."
  - Notes on Reproducibility: "By reusing a seed value, the same sequence should be reproducible from run to run as long as multiple threads are not running." and the guarantee that "The generator's random() method will continue to produce the same sequence when the compatible seeder is given the same seed."
  - "The pseudo-random generators of this module should not be used for security purposes."
- collections docs, deque (https://docs.python.org/3/library/collections.html#collections.deque): "Once a bounded length deque is full, when new items are added, a corresponding number of items are discarded from the opposite end." and "Deques support thread-safe, memory efficient appends and pops from either side of the deque with approximately the same O(1) performance in either direction."
- PEP 634/636 (structural pattern matching) for the `match` statement, and PEP 814 for `frozendict`. To be fetched by the prose agents. No sentence is planned as a quote.
- *Fluent Python* 2nd ed. chapter titles "with, match, and else Blocks" and "Design Patterns with First-Class Functions": from the code repository README (https://github.com/fluentpython/example-code-2e).
- *Architecture Patterns with Python* chapter "Commands and Command Handler": from the free online edition's contents (https://www.cosmicpython.com/book/preface.html). The Preface says "Finally, we distinguish between _commands_ and _events_." It isn't planned as a quote.
- GoF: not quotable (r06 finding: the O'Reilly MCP confirms the book but can't open its text). **No GoF sentence is quoted.** State and Command are credited by pattern name and the catalogue's standard sections (Intent, Applicability, Consequences, Implementation). Three bracketed items are used only if a prose agent verifies them in the book; otherwise the idea is described without attributing it:
  - [GoF discusses a table-driven alternative to State among its implementation issues];
  - [GoF lists undo/redo and command history among Command's applicabilities];
  - [GoF names the "Memento" collaboration for undo].

Repo facts:
- **Chapter status.** Chapters 14-15 are `kind = "pattern"`, `has_example = true`, `status = "stub"`, part 5 (`selecting-varying-behavior`). The stubs carry `## How it works` and "Draft pending" descriptions. `validate.py` enforces `SPINE["pattern"]` and exactly one `ai-sidebar`.
- **Reconciliation.** Rows run 1-74, so r07 adds 75-84. Row 1 gets the decision 8 note. `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** `_data/diagrams.yml` has 14 entries; r07 makes 16.
- **Test-name collisions.** Claim tokens resolve against `def test_*` across all members. Existing names near this ground: `test_deferred_command_is_a_partial_in_a_deque`, `test_undo_needs_a_command_object` (three-way split member), `test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old` (dataclasses member), `test_a_rule_with_hidden_state_is_not_reproducible` (strategy member). Every name below is new (criterion 3).
- **The mypy-API helper** (r05/r06 shape) doesn't pass `--warn-unreachable`. The planning evidence shows the snippets behave the same with and without it, and the member runs use the root config (`warn_unreachable = true`).
- **Already taught, so not repeated** (each gets a pointer by title and at most one sentence):
  - Partials in a deque and the chapter 3 `Amendment(before, after)` shape: "The three-way split: dissolve, survive, disambiguate".
  - "A command holding state is a deferred call": "What 1994 assumed, and what Python dissolves".
  - Frozen is shallow, `replace` gives a new value and aliasing between bookings: "Dataclasses and value semantics".
  - `partial` has no value equality or `__name__`: "Strategy: the callable".
  - `assert_never` in a `match` over the event union, and a missing case not reported by single dispatch: "Naming patterns for teams and AI assistants" (one sentence there; chapter 14 is the first to teach it).
  - The `assert` statement removed under `-O`: "Protocol, duck typing, and structural typing with mypy".
  - Negative fixtures, the mypy-API helper and deletion tables: "Proving it works: pytest, pytest-mock, and mypy".
- **Later chapters whose ground must not be taken:**
  - "Visitor, Memento, and Interpreter" (snapshot rollback, a mutated memento, `match` vs `singledispatch` as Visitor);
  - "Builder, dataclasses, and Prototype" (`replace` as Prototype, shallow copy);
  - "Observer" (`HandlingEvent`s raised to subscribers);
  - "Shortcut patterns: dict dispatch, function tables, and EAFP" (dispatch tables in general);
  - "asyncio and the patterns" (coroutine Commands, `asyncio.Queue`);
  - "The GIL and performance" (the thread-safety of `deque` is out of scope; the docs sentence isn't quoted).

## What is new in each chapter

**Chapter 14 (survives).** "The three-way split" says only that the transition table is the design. This chapter adds:
- **The table as data.** It's read-only and walked by tests (every status reachable from `BOOKED`, `DELIVERED` terminal). mypy checks the types of its entries but not their legality, and ruff, not mypy, catches a repeated key.
- **The match form.** Frozen dataclass states carry their own data. An explicit illegal arm plus `assert_never` makes a forgotten state a mypy error. A wildcard illegal arm hides the forgotten state, and a tuple match can't be proved exhaustive even when it is.
- **One behaviour table for both forms**, with a product test so the two can't drift.
- **The state-object trade-off, measured.** Adding a state fails in every `match`, adding an operation fails at every return site of the object form, and an unreturned state class is never checked. The class form survives where states own several operations and the set of states is open.
- **The probabilistic variant.** A seeded transit-delay model, reproducible only because its generator is injected.

**Chapter 15 (survives; the plain deferred call dissolves).** "The three-way split" shows partials in a deque and a two-field `Amendment`. This chapter adds:
- **Commands as frozen values** (`Reweigh`, `Redirect`, `SetInstructions`). They compare and print by value, which a partial doesn't.
- **The inverse computed when the command runs.** The chapter 3 shape records `before` when the command is built and restores a stale weight once commands are queued.
- **The documented failure.** Two commands sharing a mutable mapping undo to the wrong state. The 3.15 `frozendict` field makes that a type error and a runtime error.
- **Undo and redo stacks**, a bounded history (`deque(maxlen=...)` forgets the oldest silently), and a FIFO queue whose batch applies all or nothing. Because the request is immutable, all-or-nothing is a local variable.

## Approach

- **Thesis wording.**
  - Chapter 14 names State as surviving: no feature resolves the force (which transitions are legal, written down in one place). `match`, enums, frozen dataclasses and `frozendict` make it short and checkable.
  - Chapter 15 says Command survives and the plain deferred call dissolves into `functools.partial`. What survives is the data that undo needs and the order a queue imposes.
- **Credit.** Both chapters credit GoF where the pattern is introduced. Chapter 14 cites Ramalho's "with, match, and else Blocks" for further reading. Chapter 15 credits Percival and Gregory's "Commands and Command Handler" for command queues handled in one place. Nothing from either book's examples is used: their domains aren't shipping.
- **Domain names** come from `_plans/shipping-domain-model.md`:
  - Chapter 14 (Tracking): `ConsignmentStatus`, `HandlingKind`, `HandlingEvent`, `ConsignmentId`.
  - Chapter 15 (Consignment): `Booking`, `BookingRequest`, `Consignment`, `ConsignmentId`, `Weight`, `Amendment`.
  - New supporting names, recorded in domain rows 14-15 at H0:
    - chapter 14: `Booked`, `Loaded`, `InTransit`, `Cleared`, `Delivered` (states), `ConsignmentState`, `TRANSITIONS`, `next_status`, `apply_event`, `status_of`, `track`, `TransitionError`, `sail_one_day`, `simulate_transit`;
    - chapter 15: `Reweigh`, `Redirect`, `SetInstructions`, `apply`, `AmendmentError`.
  - No new domain area, no carrier codes, port codes as UN/LOCODEs (`NLRTM`, `SGSIN`, `MYPKG`). Delay probabilities and voyage lengths are illustrative, and the prose says so once.
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/14-state-and-finite-state-machines` (project `state-machines`, package `state_machines`);
  - `examples/15-command-undo-and-command-queues` (project `command-undo`, package `command_undo`).
- **mypy witnesses** copy the r06 helper (own `mypy.ini`, `--strict`, `--cache-dir os.devnull`, `--no-error-summary`). Each asserts exit status, an exact `_codes()` set and one or two substrings, never line numbers. Snippets that add a state or an amendment kind are self-contained and mirror the src shape, because a union can't be extended from outside. A test-only consistency check (criterion 23) parses `src` with `ast` and asserts the snippet's class and arm names match it, so a snippet can't drift from the code it stands for.
- **Negative witness rule.** Every check in src has a test that fails when the check is deleted, and the deletion tables (H1a, H1b) name the test and say why it sees the deletion.
- **Global state.**
  - No `mock`, `mocker`, `monkeypatch`, `print(` or wall clock.
  - No module-level mutable tables (every table is a `frozendict`).
  - In chapter 14, `random` appears only as `random.Random` injected by parameter, and `test_the_model_leaves_the_module_generator_alone` uses `random.getstate()` read-only.
  - `filterwarnings = ["error"]` stays active.

Rejected:
- A `match (state, event.kind)` tuple form: mypy can't prove it exhaustive (planning evidence). It's mentioned in one sentence as the reason to match on the state first.
- `enum.StrEnum`, `Flag` and `auto()` tricks: plain `Enum` with `auto()` as the earlier members use.
- A state-machine library or a decorator-based registration of transitions: decorators belong to their own chapters, and no library is wanted.
- A Markov chain over every state (decision 7).
- `functools.Placeholder`.
- `copy.deepcopy` as the undo fix: it hides the shared data rather than removing it, and copying belongs to the Prototype chapter.
- Whole-booking snapshots as the main undo (decision 5).
- `asyncio.Queue` (asyncio chapter).
- Thread-safety claims about `deque`.
- Persisting the command log, and command serialisation formats: out of scope. The stable repr is the only claim.

## Per-chapter spec

### Chapter 14: State and finite state machines (pattern, has_example = true, bucket: survives)

Thesis: State's force is behaviour that depends on a history of transitions, where which transitions are legal is a business rule that has to be written down in one place and checked. No language feature resolves that force, so the pattern survives. What Python 3.15 changes is the shape:
- a read-only table when states carry no data;
- frozen dataclass states and a `match` ending in `assert_never` when they do;
- per-state classes only where states own several operations and the set of states is open.

Sections (about 2,350 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - a mutable `status` field set from delivered back to booked, which nothing refuses (test 9);
   - a customs-hold state added to the lifecycle while the tracking page's branches quietly fall through, with no message;
   - a delay simulation whose seeded result changes when another part of the program draws a random number.
3. Figure plus one paragraph (~60).
4. `## The force that remains` (~280):
   - GoF credited for State, by Intent and Consequences, in the book's own words. Nothing quoted. [Table-driven alternative only if verified.]
   - Bucket: survives.
   - One sentence pointing to "The three-way split: dissolve, survive, disambiguate" for the placement.
   - The two design questions: where are the legal transitions written, and what checks that every state is handled?
   - The tracking events here are one `HandlingEvent` class with a `HandlingKind`, because the class names belong to the states (decision 3). Said once.
5. `## The transition table` (~340). Excerpt `TRANSITIONS` and `next_status`:
   - A read-only `frozendict` (test 6). An absent pair is a `TransitionError` naming the event and the status (test 2[table]).
   - Graph tests over the table: every status reachable from `BOOKED`, and `DELIVERED` terminal (tests 3, 5).
   - What mypy checks: entry types, a swapped key and a wrong value, as `[dict-item]` (test 13). What it can't: a well-typed illegal entry such as delivered to booked, and a repeated key, which ruff's F601 reports and the runtime silently resolves to the last value (test 13[illegal-pair], test 14). Fresh output.
   - One pointer to "Shortcut patterns: dict dispatch, function tables, and EAFP" for dispatch tables in general.
6. `## States that carry data: match and assert_never` (~400). Excerpt the states and `apply_event`:
   - Each state holds only its own data (test 8). `InTransit` has `delay_days`, and `Delivered` has no such field.
   - The explicit illegal arm lists every state. `case _: assert_never(state)` ends the match.
   - Adding a state is a mypy `[arg-type]` naming it (test 10[dataclass-union]). The enum form reports the `Literal[...]` member (test 10[enum]).
   - A wildcard illegal arm hides the new state (test 11). A tuple match isn't proved exhaustive even when complete (test 12), so match the state first.
   - `assert_never` is a function, so `-O` doesn't remove it (test 15). The typing docs are quoted exactly.
   - One sentence pointing to "Naming patterns for teams and AI assistants", where the event union's `assert_never` was first mentioned.
7. `## One lifecycle, two forms` (~220):
   - The behaviour table runs both forms (tests 1-3 `[table|match]`). The product test holds them to the same answer for every status and event kind (test 4).
   - When to pick which: the table when states carry no data and the lifecycle should be reviewable as data; the match when states carry data or behaviour differs per state.
8. `## Where state objects still fit` (~260). At most one short excerpt of the `_LifecycleState` fixture:
   - The GoF form passes the same table (test 16).
   - The measured trade-off: adding an operation fails at every return site of the object form (test 17); adding a state fails in every `match` (test 10); a state class that nothing returns is never checked (test 18).
   - The line: an open set of states, each owning several operations, extended by people who can't edit a central `match`, means objects behind a Protocol. A closed lifecycle owned by one team means a union and `match`.
   - One pointer to "Protocol, duck typing, and structural typing with mypy" for Protocol matching.
9. `## A probabilistic machine: transit delays` (~280). Excerpt `sail_one_day`:
   - Each day at sea, the consignment is delayed with a given probability. The generator is a parameter.
   - The same seed gives the same voyage (test 19). The random docs on reproducibility and on the hidden shared instance are quoted exactly.
   - A shared generator gives a different second run (test 20). The bounds hold (test 21), and the model never touches the module generator (test 22).
   - One sentence on the recorded 10,000-seed mean, pointing at the evidence run, with no assertion. One sentence that `random` is not for security, quoting the docs.
10. `## When not to use it` (~170): a two-state flag (a `bool`); a lifecycle nothing ever checks (an enum field); a workflow whose steps are configured by users at run time (data, not a type); one pointer to "Mediator and Chain of Responsibility" for ordered processing stages. Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written state machines.** An assistant asked for "the State pattern" may write a state class per status with a method per event, a mutable `status` field that any caller can set, or a `match` whose last arm raises for "anything else". Check: is every legal transition written in one place; is an illegal one refused with a domain error; does the `match` name every state before an `assert_never` arm; does a test walk the table for unreachable and terminal states; is any random generator passed in, not drawn from the module.</blockquote>

    Each check maps to tests 1 and 6, 2 and 9, 10-11, 3 and 5, and 19-22. No claim about how often assistants do this.
11. `## Build, run, observe` (~220 plus output). Experiments, each in a scratch copy, one change, reverted:
    - (a) Add a frozen `Held(port: str)` state to `ConsignmentState` without touching any `match`. Expected: the member mypy run reports two `[arg-type]` errors naming `"Held"`, one in `apply_event` and one in `status_of`, and pytest still passes. Quote as observed.
    - (b) Add `(ConsignmentStatus.DELIVERED, HandlingKind.BOOKED): ConsignmentStatus.BOOKED` to `TRANSITIONS`. Expected: mypy reports success; `test_delivered_is_terminal[table]` and `test_the_two_forms_agree_on_every_status_and_event` fail. Quote as observed.
12. `## For deeper coverage` (~130): GoF (State); the typing docs (`assert_never`) and the typing guide "Unreachable Code and Exhaustiveness Checking"; PEP 634 and PEP 636; PEP 814; the `random` docs (reproducibility); Ramalho, *Fluent Python* 2nd ed., "with, match, and else Blocks"; the bibliography link.

Figure `14-state-and-finite-state-machines` (vertical):
- A column of five state boxes, `Booked` -> `Loaded` -> `InTransit` -> `Cleared` -> `Delivered`, with the event kind on each arrow (`LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED`).
- `InTransit` has a side box "each day: delay with probability p (injected Random)".
- `Delivered` has the label "terminal".
- A left side box `TRANSITIONS` "read-only table: status, event to status". A right side box `apply_event` "match on state, assert_never".
- An accent box at the bottom: "illegal event: TransitionError".
- No numbers in the SVG.

Caption draft (40 words with prefix): "Figure 14.1: One consignment lifecycle, two ways to write it. A read-only table maps a status and an event to the next status; a match over frozen states does the same with per-state data, and a seeded generator drives transit delays."

### Chapter 15: Command, undo, and command queues (pattern, has_example = true, bucket: survives; the plain deferred call dissolves)

Thesis: Command packages a request so that it can be queued, logged and undone. The packaging dissolves: a deferred call is a `functools.partial`. Undo and the queue survive, because they need data the call never kept:
- the value each amendment replaced, captured when it runs;
- an order;
- values that no one can change after the fact.

Frozen command values, a `match` that returns the inverse, `frozendict` fields and `deque` stacks are the Python shape.

Sections (about 2,350 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - two instruction amendments built from one mapping the caller kept editing, where undo restores the edited text (test 7);
   - an amendment that records the old weight when it's queued, where undo after a queued pair restores the weight from before both (test 9);
   - a batch that fails halfway and leaves half a booking amended.
3. Figure plus one paragraph (~60).
4. `## What dissolves and what survives` (~300):
   - GoF credited for Command by Intent and Applicability, in the book's own words. [The undo/redo applicability only if verified.]
   - Bucket: survives, with the deferred call dissolving.
   - One sentence pointing to "The three-way split: dissolve, survive, disambiguate" for the deque of partials. New here: a partial has no inverse and no value equality, so a queue of partials can't be undone, inspected or deduplicated, while equal amendments compare equal (test 1).
   - One sentence pointing to "Strategy: the callable" for the partial facts.
5. `## Commands as values` (~360). Excerpt the three amendments, the `Amendment` alias and `apply`:
   - Each command is a frozen slotted dataclass. `apply` returns the amended request and the inverse, computed from the request it amended (test 2).
   - Adding a kind is a mypy error until `apply` handles it (test 18). One sentence pointing to "State and finite state machines" for `assert_never`, with no re-teaching.
   - Why not `apply`/`undo` callables on one `Amendment` (decision 4): they capture their data when built and compare by identity.
6. `## Undo, redo and the inverse captured at run time` (~380). Excerpt `Booking`:
   - An undo stack and a redo stack of inverses. Undo then redo walk the history (test 3). A new amendment clears redo (test 4). An empty stack is an `AmendmentError` (test 5).
   - Two amendments undone restore the original (test 6).
   - The stale inverse: the chapter 3 shape records `before` when built, so a queued pair undoes to 120 instead of 130 (test 9). The rule is to record the inverse when the command runs.
   - The bounded history: `deque(maxlen=...)` forgets the oldest amendment silently (test 12). The collections docs sentence is quoted exactly.
7. `## Commands that share mutable data` (~320):
   - The documented failure: the `_LooseSetInstructions` fixture takes a `dict`, the caller edits it between two amendments, and after one undo the instructions read "fragile" where "keep dry" was expected (test 7). mypy accepts it (test 19).
   - One sentence pointing to "Dataclasses and value semantics" for frozen being shallow.
   - The fix is the field type. `SetInstructions.instructions: frozendict[str, str]` makes the caller's `dict` a mypy `[arg-type]` (test 16) and an item assignment `[index]` (test 17) and a runtime `TypeError` (test 8). PEP 814 is cited, and What's New is quoted on "does not allow modification after creation".
   - A frozen dataclass may default a `frozendict` field without `default_factory` (test 15).
   - Immutable snapshots: because every `BookingRequest` is frozen, a request kept from before the amendments still equals the original (test 14). One sentence pointing to "Visitor, Memento, and Interpreter" for snapshot rollback.
8. `## A queue that applies all or nothing` (~280):
   - `submit` appends to a `deque`, and `apply_pending` drains it first in, first out (test 10).
   - The fold runs on a local variable, so a failing amendment (an invalid port code, test 13) leaves the request, the history and the queue as they were (test 11).
   - One sentence crediting Percival and Gregory ("Commands and Command Handler") for commands queued and handled in one place.
   - One pointer to "asyncio and the patterns" for queues across tasks.
9. `## When not to use it` (~170): a change that is never undone or queued (call the function); undo that a database transaction already gives; a command log kept for audit only (record events, and point to "Observer"); amendments whose inverse needs external state you don't hold (snapshot, and point to "Visitor, Memento, and Interpreter"). Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written commands.** An assistant asked for "the Command pattern" may write a `Command` base class with `execute` and `undo`, record the old value when the command is created, store a caller's `dict` or `list` in a command, or apply a batch by mutating the booking step by step. Check: is each command a frozen value that compares equal; is the inverse computed from the state the command actually changed; are command fields immutable types (`frozendict`, `tuple`); does a failing batch leave the booking unchanged; is the history's bound a stated choice.</blockquote>

   Each check maps to tests 1-2, 9 and 6, 7-8 and 16, 11, and 12.
10. `## Build, run, observe` (~220 plus output). Experiments:
    - (a) Delete `self.redo_stack.clear()` from `Booking.amend`. Expected: `test_a_new_amendment_clears_redo` fails. Quote the observed assertion.
    - (b) In `Booking.apply_pending`, assign `self.request` inside the loop instead of after it. Expected: `test_a_failing_batch_leaves_the_booking_unchanged` fails because the request is half amended. mypy reports success. Quote as observed.
11. `## For deeper coverage` (~130): GoF (Command); Percival and Gregory, *Architecture Patterns with Python*, "Commands and Command Handler"; the collections docs (`deque`); PEP 814 and the What's New entry; the dataclasses docs (frozen, `replace`); PEP 634; [Ramalho's "Design Patterns with First-Class Functions" only if verified for Command]; the bibliography link.

Figure `15-command-undo-and-command-queues` (vertical):
- Top accent box `submit(amendment)`, then `pending` "deque, first in first out".
- Then `apply_pending` "fold on a local request: all or nothing", then `apply(request, amendment)`, which forks into `BookingRequest` "new frozen value" and "inverse amendment".
- The inverse feeds `undo_stack` "deque(maxlen): oldest forgotten". `undo` moves an inverse to `redo_stack`. A side box: "new amendment clears redo".
- No numbers in the SVG.

Caption draft (41 words with prefix): "Figure 15.1: Amendments as values on two stacks. Queued amendments are applied first in, first out, all or nothing; each application returns a new frozen request and the inverse it computed, which undo and redo move between bounded stacks."

Citations, both chapters: verify each before writing; apply the bracketed fallbacks; quote no sentence unless it was checked on a fetched page; no comparison between languages.

## Example spec

### `examples/14-state-and-finite-state-machines` (project `state-machines`, package `state_machines`)

`pyproject.toml` in the r06 shape (`requires-python = ">=3.15"`, no `[tool.*]`).

- `domain.py`:
  - `ConsignmentId = NewType`.
  - `HandlingKind(Enum)`: `BOOKED`, `LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED`, with `auto()`.
  - `HandlingEvent(consignment_id, kind, location: str)`, frozen slotted.
  - `ConsignmentStatus(Enum)`: `BOOKED`, `LOADED`, `IN_TRANSIT`, `CLEARED`, `DELIVERED`.
  - `TransitionError`.
- `table.py`:
  - `TRANSITIONS: Mapping[tuple[ConsignmentStatus, HandlingKind], ConsignmentStatus] = frozendict({...})`: four entries, in dict-literal form so mypy checks each.
  - `next_status(status, kind) -> ConsignmentStatus`: `try`/`except KeyError` raises `TransitionError(f"{kind.name} not allowed when {status.name}") from None`.
- `states.py`:
  - Frozen slotted dataclasses `Booked(origin: str)`, `Loaded(port: str)`, `InTransit(departed_from: str, days_sailed: int = 0, delay_days: int = 0)`, `Cleared(port: str)`, `Delivered(port: str)`.
  - `type ConsignmentState = Booked | Loaded | InTransit | Cleared | Delivered`.
  - `status_of(state) -> ConsignmentStatus` by `match` ending in `assert_never`.
  - `apply_event(state, event) -> ConsignmentState`, shaped as in Planning evidence (guarded legal arms; an explicit illegal arm naming all five states that raises `TransitionError(f"{event.kind.name} not allowed when {status_of(state).name}")`; `case _: assert_never(state)`).
  - `track(consignment_id, events: Iterable[HandlingEvent], *, start: ConsignmentState) -> ConsignmentState` folds `apply_event`, and raises `TransitionError(f"event for {event.consignment_id} in the history of {consignment_id}")` on a foreign event.
- `transit.py`:
  - `sail_one_day(state: InTransit, *, rng: random.Random, delay_probability: float) -> InTransit` (`replace`).
  - `simulate_transit(state, *, rng, delay_probability, scheduled_days, max_days) -> InTransit` stops at `scheduled_days` sailed or after `max_days` simulated days, whichever is first.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- a `forms` fixture parametrized `table` and `match`, each giving a callable `(kinds: Sequence[HandlingKind]) -> ConsignmentStatus` (the table folds `next_status` from `BOOKED`; the match folds `apply_event` from `Booked("NLRTM")` and returns `status_of`);
- `_SAMPLE_STATES: frozendict[ConsignmentStatus, ConsignmentState]`, one state per status.

`test_lifecycle.py` (fixture `_TrackedConsignment`, a mutable dataclass with a `status` field):
1. `test_the_lifecycle_runs_booked_to_delivered[table|match]`
2. `test_an_illegal_event_is_a_transition_error[table|match]`: `DEPARTED` from `BOOKED`, matching `"DEPARTED not allowed when BOOKED"`.
3. `test_delivered_is_terminal[table|match]`: every kind from `DELIVERED` raises.
4. `test_the_two_forms_agree_on_every_status_and_event`: over `ConsignmentStatus` x `HandlingKind`, both forms raise or both give the same status.
5. `test_every_status_is_reachable_from_booked`: a breadth-first walk over `TRANSITIONS`.
6. `test_the_transition_table_is_read_only`: `# type: ignore[index]`; `TypeError` matching `does not support item assignment`; `not isinstance(TRANSITIONS, dict)`.
7. `test_an_event_for_another_consignment_is_refused`
8. `test_each_state_carries_only_its_own_data`: `InTransit` has `delay_days`; `not hasattr(Delivered("SGSIN"), "delay_days")`; assignment raises `FrozenInstanceError`.
9. `test_a_status_field_accepts_an_illegal_transition`: the fixture goes from `DELIVERED` to `BOOKED` with nothing raised.

`test_state_objects.py` (comparison fixture `_LifecycleState(Protocol)` with `on_event(kind) -> _LifecycleState` and `status`, plus five frozen state classes):
16. `test_state_objects_pass_the_same_lifecycle_table[...]`: the same case list as tests 1-3, run through the objects.

`test_transit.py`:
19. `test_a_seeded_transit_is_reproducible`: `Random(7)` twice gives `delay_days == 11` both times; `Random(2026)` gives 3.
20. `test_a_shared_generator_gives_a_different_second_run`: 11, then 5.
21. `test_transit_delay_bounds[never-delayed|always-delayed]`
22. `test_the_model_leaves_the_module_generator_alone`: `random.getstate()` is equal before and after `simulate_transit`.

`test_static.py`:
10. `test_mypy_reports_a_state_missing_from_the_match[dataclass-union|enum]`: `{"arg-type"}`; `Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"`; then `"Literal[ConsignmentStatus.HELD]"`.
11. `test_mypy_cannot_see_a_state_swallowed_by_a_wildcard`: exit 0, empty.
12. `test_mypy_cannot_prove_a_tuple_match_exhaustive`: `{"arg-type"}`, `"tuple[Booked, K]"` (the executor names the enum to match the snippet).
13. `test_mypy_checks_table_entry_types_but_not_legality[swapped-key|wrong-value|illegal-pair]`: `{"dict-item"}` twice, with `expected "tuple[ConsignmentStatus, HandlingKind]"`; then exit 0.
14. `test_a_repeated_table_key_keeps_the_last_value`: runtime; the ruff F601 fact is quoted from the H5 run, not asserted.
15. `test_assert_never_raises_even_when_asserts_are_stripped`: `subprocess.run([sys.executable, "-O", "-c", ...])`, then a non-zero return code and `Expected code to be unreachable` in stderr.
17. `test_mypy_reports_an_operation_missing_from_a_state_object`: `{"return-value"}`, `is missing following "LifecycleState" protocol member`.
18. `test_mypy_accepts_a_state_object_nothing_returns`: exit 0, empty.
23. `test_the_static_snippets_mirror_the_source`: an `ast` check that the snippet state names and the illegal-arm shape match `states.py`.

Also `README.md` and the card `_examples/14-state-and-finite-state-machines.md` (`order: 14`, eyebrow "Selecting behaviour · State"). No `mock`, `monkeypatch`, `print(`, `Optional`, `isinstance` or module-level `random.` calls in `src/`.

Deletion table (H1a). Each row: the check, how it's deleted, the failing test, and why that test sees it.

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `next_status` domain error | plain index | 2[table], 3[table] | expects `TransitionError`; gets `KeyError` |
| explicit illegal arm | arm removed (falls to `assert_never`) | 2[match], 3[match], member mypy | runtime `AssertionError`, not `TransitionError`; mypy reports the reachable `assert_never` |
| a guarded legal arm (`InTransit` + `CLEARED`) | arm removed | 1[match], 4 | `TransitionError` where `CLEARED` was expected; forms disagree |
| `frozendict` table | `dict` | 6 | assignment no longer raises; `isinstance(..., dict)` |
| `track` consignment check | removed | 7 | the foreign event is applied |
| `frozen=True` on `InTransit` | dropped | 8 | assignment succeeds |
| `rng` parameter | module `random.random()` | 22, member mypy | module generator state changes; the unused `rng` parameter remains, so the executor confirms the observed failure |
| delay comparison `<` | `<=` | 21[never-delayed] | `random()` can return 0.0 only rarely, so the executor checks the case actually fails; if not, the row is replaced by a seed whose draws expose it, or marked "not witnessable" with a reason |
| `max_days` bound | loop on `days_sailed` only | 21[always-delayed] | at probability 1 the loop never ends; no test asserts a timeout, so the executor observes the hang in a scratch copy under `timeout 10` and quotes the exit code (124) as the witness |
| `status_of` arm | one arm removed | member mypy, 1[match] | `[arg-type]` naming the state; the runtime `AssertionError` |

The last three rows carry executor checks because the failure mode was predicted, not run. "Not witnessable" needs the orchestrator's agreement and goes in Corrections.

### `examples/15-command-undo-and-command-queues` (project `command-undo`, package `command_undo`)

- `domain.py`:
  - `ConsignmentId`.
  - `Weight(kilograms: Decimal)`, frozen slotted, finite and positive, `ValueError` otherwise.
  - `Consignment(id, weight, destination: str)`, frozen slotted kw_only.
  - `BookingRequest(consignment, insured: bool = False, instructions: frozendict[str, str] = frozendict())`, frozen slotted kw_only.
  - `AmendmentError`.
- `amendments.py`:
  - Frozen slotted `Reweigh(weight: Weight)`, `Redirect(destination: str)`, `SetInstructions(instructions: frozendict[str, str])`.
  - `type Amendment = Reweigh | Redirect | SetInstructions`.
  - `apply(request, amendment) -> tuple[BookingRequest, Amendment]` by `match`, ending in `assert_never`. `Redirect` refuses a destination that isn't five uppercase letters with `AmendmentError(f"not a port code: {destination!r}")`.
- `booking.py`:
  - `Booking`, `@dataclass(slots=True, eq=False)` (an entity): `request`, `history_limit: int = 20`, and `undo_stack`, `redo_stack`, `pending` as `deque` fields built in `__post_init__` (`undo_stack` with `maxlen=history_limit`).
  - `amend(amendment)`, `undo()`, `redo()` (`AmendmentError("nothing to undo")` / `("nothing to redo")`).
  - `submit(amendment)` and `apply_pending()`: a fold on a local request and a local list of inverses, committed only after the whole batch succeeds, and clearing `pending` and `redo_stack` on success.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: `request` (`NLRTM`-origin consignment of 120 kg bound for `SGSIN`, empty instructions), `booking`.

`test_commands.py`:
1. `test_amendments_compare_by_value_and_partials_do_not`: equal `Reweigh`s are `==` with equal hashes; two equal partials are `!=`; `not hasattr(partial(...), "undo")`.
2. `test_apply_returns_the_amendment_that_reverses_it[reweigh|redirect|instructions]`: applying the inverse gives back the original request.
13. `test_a_redirect_needs_a_port_code`

`test_undo.py` (fixture `_PrecomputedReweigh(before, after)`, the chapter 3 shape):
3. `test_undo_and_redo_walk_the_history`
4. `test_a_new_amendment_clears_redo`
5. `test_undo_or_redo_with_nothing_recorded_is_an_amendment_error[undo|redo]`
6. `test_two_amendments_undone_restore_the_original_request`
9. `test_an_inverse_captured_when_queued_restores_a_stale_weight`: 120 where 130 is expected.
12. `test_a_bounded_history_forgets_the_oldest_amendment`: `history_limit=2`, three amendments, two undos, then `AmendmentError`; the request is the one after the first amendment.
14. `test_a_frozen_request_is_a_safe_snapshot`

`test_shared_data.py` (fixtures `_LooseRequest(instructions: dict[str, str])`, `_LooseSetInstructions`, `_loose_apply`):
7. `test_commands_sharing_a_mutable_mapping_undo_to_the_wrong_state`: after one undo the instructions are `{"handling": "fragile"}`.
8. `test_instructions_cannot_be_changed_after_queueing`: `# type: ignore[index]`; `TypeError` matching `does not support item assignment`.
15. `test_a_frozen_mapping_default_needs_no_factory`: `BookingRequest(...).instructions is BookingRequest(...).instructions`; a `dict` default raises `ValueError` matching `use default_factory`.

`test_queue.py`:
10. `test_queued_amendments_apply_in_order`
11. `test_a_failing_batch_leaves_the_booking_unchanged`: the request, `undo_stack` and `pending` are equal to their values before the batch, and the `AmendmentError` names the port code.

`test_static.py`:
16. `test_mypy_rejects_a_dict_where_frozen_instructions_belong`: `{"arg-type"}`, `expected "frozendict[str, str]"`.
17. `test_mypy_rejects_assigning_into_frozen_instructions`: `{"index"}`, `Unsupported target for indexed assignment ("frozendict[str, str]")`.
18. `test_mypy_reports_an_amendment_kind_missing_from_apply`: `{"arg-type"}`, `incompatible type "Insure"; expected "Never"`.
19. `test_mypy_accepts_commands_that_share_a_dict`: exit 0, empty.

Also `README.md` and the card (`order: 15`, eyebrow "Selecting behaviour · Command"). No `mock`, `monkeypatch`, `print(`, `copy`, `deepcopy` or `isinstance` in `src/`.

Deletion table (H1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `Weight` finite/positive | `__post_init__` removed | executor names the test (add `test_a_booked_weight_must_be_positive_and_finite` if none sees it) | constructs zero and NaN weights and expects `ValueError` |
| inverse from the request | inverse built from the amendment | 2[all], 3, 6 | applying the "inverse" changes nothing back |
| `Redirect` port-code check | removed | 13, 11 | no `AmendmentError`; the batch commits |
| `redo_stack.clear()` in `amend` | removed | 4 | redo replays a stale inverse |
| empty-stack `AmendmentError` | plain `pop()` | 5[undo], 5[redo] | `IndexError` from the deque |
| `maxlen=history_limit` | unbounded deque | 12 | the third undo succeeds |
| `frozendict` field type | `dict[str, str]` with `default_factory=dict` | 8, 15, member mypy | assignment succeeds; the default is no longer shared; the unused `[index]` ignore |
| commit after the fold | commit inside the loop | 11 | the request is half amended |
| `pending` FIFO | `pop()` for `popleft()` | 10 | reverse order |
| `assert_never` arm | `case _: raise AmendmentError` | 18 is a snippet, so the executor adds an `ast` check (`test_apply_ends_in_assert_never`) or marks it "seen by review only" with the orchestrator's agreement | |

## Steps and status

Step ids are `H*` because `--claims` resolves `run:` tokens against every plan's steps table (decision 1).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| H0 | This plan file. PDP-114a-c and 115a-c `active` in `iteration-plan.md` (dated note). Reconciliation rows 75-84 `open`, and the row 1 note (decision 8). Domain-model rows 14-15 updated with the example-spec names (row 14: the state classes, single-class `HandlingEvent` with `HandlingKind`, `TRANSITIONS` over a 3.15 `frozendict`, the state-object form as a test fixture, `sail_one_day`/`simulate_transit`; row 15: `type Amendment = Reweigh \| Redirect \| SetInstructions`, `apply` returning the inverse, `AmendmentError`, `frozendict` instructions, `deque` stacks and queue, and the failing test name). ch14/15 stub `description` lines written. Decisions recorded | - | done |
| H1a | ch14 member, card, README; three green runs; the deletion table above, each row run in a scratch copy; `_plans/evidence/transit-delay-model.md` (the 10,000-seed mean, scrubbed) | H0 | done |
| H1b | ch15 member, card, README; one `uv lock` after both members (sequenced); three green runs; deletion table | H1a | done |
| H2 | Witness results into rows 75-84 (claims audit resolves). A failed witness changes the thesis before prose. Any message differing from Planning evidence goes in "Corrections after the build" | H1b | done |
| H3 | Two figures, specs `diagrams/specs/14-*.py` and `15-*.py`, `_data/diagrams.yml` (single owner; `section: "Ch. 14"`/`"Ch. 15"`); figures 00-13 unchanged | H2 | todo |
| H4 | ch14-15 `status = "drafted"` (`kind` stays `pattern`) | H3 | todo |
| H5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly, runs the experiments and the ruff F601 check in scratch copies, quotes fresh output filtered by `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table (claim, then test, run or source URL) | H3, H4 | todo |
| H6 | Opus validation; up to two repair rounds | H5 | todo |
| H7 | PR, `ci-ok` green, ask the user before merge; tag r07.x; notes-only release. No hub PR (decision 6) | H6 | todo |

Reconciliation rows (step H0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 75 | 14 | The legal transitions are one read-only table; an illegal event is a `TransitionError`; every status is reachable from booked and delivered is terminal; a mutable status field accepts an illegal transition | `test_the_lifecycle_runs_booked_to_delivered`, `test_an_illegal_event_is_a_transition_error`, `test_delivered_is_terminal`, `test_every_status_is_reachable_from_booked`, `test_the_transition_table_is_read_only`, `test_a_status_field_accepts_an_illegal_transition` |
| 76 | 14 | mypy checks a table's entry types but not legality; a repeated key keeps the last value | `test_mypy_checks_table_entry_types_but_not_legality`, `test_a_repeated_table_key_keeps_the_last_value`, `run: H5` |
| 77 | 14 | A `match` ending in `assert_never` reports a state missing from a union or an enum; a wildcard illegal arm hides it; a tuple match is not proved exhaustive; `assert_never` survives `-O` | `test_mypy_reports_a_state_missing_from_the_match`, `test_mypy_cannot_see_a_state_swallowed_by_a_wildcard`, `test_mypy_cannot_prove_a_tuple_match_exhaustive`, `test_assert_never_raises_even_when_asserts_are_stripped`, `source: https://docs.python.org/3/library/typing.html` |
| 78 | 14 | The table and match forms agree on every status and event; frozen states carry only their own data; state objects pass the same table, fail mypy at return sites when an operation is added, and go unchecked when nothing returns them | `test_the_two_forms_agree_on_every_status_and_event`, `test_each_state_carries_only_its_own_data`, `test_state_objects_pass_the_same_lifecycle_table`, `test_mypy_reports_an_operation_missing_from_a_state_object`, `test_mypy_accepts_a_state_object_nothing_returns` |
| 79 | 14 | A seeded transit-delay model is reproducible with an injected generator, differs on a shared generator's second run, holds its bounds and leaves the module generator alone | `test_a_seeded_transit_is_reproducible`, `test_a_shared_generator_gives_a_different_second_run`, `test_transit_delay_bounds`, `test_the_model_leaves_the_module_generator_alone`, `source: https://docs.python.org/3/library/random.html`, `run: _plans/evidence/transit-delay-model.md` |
| 80 | 15 | A deferred call is a partial with no inverse and no value equality; amendments are frozen values that compare by value; `apply` returns the inverse and a missing kind fails mypy | `test_amendments_compare_by_value_and_partials_do_not`, `test_apply_returns_the_amendment_that_reverses_it`, `test_mypy_reports_an_amendment_kind_missing_from_apply` |
| 81 | 15 | Undo and redo walk the history; a new amendment clears redo; an inverse captured when queued restores a stale weight; a bounded history forgets the oldest | `test_undo_and_redo_walk_the_history`, `test_a_new_amendment_clears_redo`, `test_undo_or_redo_with_nothing_recorded_is_an_amendment_error`, `test_two_amendments_undone_restore_the_original_request`, `test_an_inverse_captured_when_queued_restores_a_stale_weight`, `test_a_bounded_history_forgets_the_oldest_amendment`, `source: https://docs.python.org/3/library/collections.html` |
| 82 | 15 | Commands sharing a mutable mapping undo to the wrong state and mypy accepts them; a `frozendict` field makes the shared `dict` an `[arg-type]`, item assignment an `[index]` and a runtime `TypeError`; a frozen request is a safe snapshot | `test_commands_sharing_a_mutable_mapping_undo_to_the_wrong_state`, `test_mypy_accepts_commands_that_share_a_dict`, `test_mypy_rejects_a_dict_where_frozen_instructions_belong`, `test_mypy_rejects_assigning_into_frozen_instructions`, `test_instructions_cannot_be_changed_after_queueing`, `test_a_frozen_mapping_default_needs_no_factory`, `test_a_frozen_request_is_a_safe_snapshot`, `source: https://peps.python.org/pep-0814/` |
| 83 | 15 | Queued amendments apply first in, first out, and a failing batch leaves the booking unchanged | `test_queued_amendments_apply_in_order`, `test_a_failing_batch_leaves_the_booking_unchanged`, `test_a_redirect_needs_a_port_code` |
| 84 | 14-15 | The "Build, run, observe" experiments behave as quoted | `run: H5` |

## Corrections after the build

- Step H1a, `rng` deletion row: member mypy is silent (`random` stays imported for the annotation; an unused parameter isn't an error). Only pytest sees it: six `test_transit.py` tests fail.
- Step H1a, `<` to `<=` row: `test_transit_delay_bounds[never-delayed]` still passes. The row's witness is `test_a_draw_equal_to_the_probability_is_not_a_delay`, which sets the probability to `Random(7).random()` so the first draw equals it exactly.
- Step H1a, `max_days` row: the deletion hangs `[always-delayed]` (a 10 s timeout exits 124) as predicted; `test_the_day_cap_bounds_the_number_of_draws` (a counting `random.Random` subclass that raises after 100 draws) fails fast and is the named witness.
- Step H1a: `test_every_value_in_the_model_is_frozen` collided with chapter 13's test name and is `test_every_state_and_event_is_frozen`; the orchestrator re-ran the `HandlingEvent` frozen deletion under the new name (1 failed, 39 passed). Shared case lists live in conftest fixtures, so each table test reports one id per form, not per history.
- Step H1b: the pytest built-in `request` fixture clashes with the spec's conftest name, so the fixture is `booking_request`; `apply_pending` drains a local `deque(self.pending)` with `popleft`, so a failing batch leaves `pending` and the request untouched. No planning errors in chapter 15.
- Row 76 carries `run: H5`, which resolves when H5 is done (not an H1a gate failure).

(empty)

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member: `uv run pytest` and `uv run mypy --strict src tests` exit 0 on three consecutive runs.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch|print\("` over both members prints nothing.
   - `grep -rnE "random\.(random|seed|choice|randint|uniform)\(" examples/14-*/src` prints nothing. `grep -rn "random" examples/15-*` prints nothing.
   - `grep -rnE "\bcopy\b|deepcopy" examples/15-*/src` prints nothing.
3. Every test name cited in rows 75-84 is defined exactly once across `examples/*/tests` (`grep -rhoE "def test_\w+" examples/*/tests | sort | uniq -d` lists none of them).
4. Every mypy-API test asserts exit status and an exact code set (`grep -c "_codes("` at least 4 in each `test_static.py`), and no test asserts a line number. Every `# type: ignore[...]` names a code.
5. Deletion tables (H1a, H1b): every row, deleted in a scratch copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed"; the rows marked as executor checks are resolved or moved to Corrections with the orchestrator's agreement.
6. ch14-15 drafted, one figure each, captions 20-45 words including `Figure N.1:`, 1,900-2,500 prose words each (validate.py).
7. `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere. `grep -c "^## When not to use it"` is 1 in each, and `grep -c "^## How it works"` is 0. `validate.py` passes the `pattern` spine.
8. Thesis:
   - ch14 names State as surviving (`grep -ciE "surviv"` at least 1) and says the transition table is the design.
   - ch15 says Command survives and the plain deferred call dissolves into `functools.partial` (`dissolv` and `surviv` each at least 1).
9. Non-overlap:
   - ch14 has no `singledispatch` teaching and no Visitor framing. It points to "Naming patterns for teams and AI assistants", "The three-way split: dissolve, survive, disambiguate", "Shortcut patterns: dict dispatch, function tables, and EAFP", "Protocol, duck typing, and structural typing with mypy" and "Mediator and Chain of Responsibility" by title.
   - ch15 has no excerpt of the three-way split's `Booking`/`Amendment` or deque-of-partials code, no re-teaching of "frozen is shallow" or partial equality, and no `copy` module. It points to "The three-way split: dissolve, survive, disambiguate", "Strategy: the callable", "Dataclasses and value semantics", "State and finite state machines", "Visitor, Memento, and Interpreter", "Observer" and "asyncio and the patterns" by title.
   - Neither chapter re-teaches the evidence method, which is pointed to "Proving it works: pytest, pytest-mock, and mypy".
10. Voice:
    - `scan.sh --tier ban --fail` exits 0 over both chapters, READMEs, cards and SVGs, with `--stats` reviewed against the house-voice rubric.
    - Contractions are used: uncontracted `does not|do not|is not|are not|did not|cannot` at most 3 per chapter outside code and output.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ)"` over prose (front matter `part:` slug excluded) prints nothing.
11. `grep -c $'\u2014'` is 0 over every file touched in r07, including this plan.
12. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Lisp|Dylan|Smalltalk|capstone|PDP-|\br0[0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/1[45]-*.md`, the new READMEs and cards prints nothing.
13. Idiomatic scan: 0 ban-tier in both members.
14. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`, never hand-edited.
15. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run (API output prints `<string>:N` matching the snippet), apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
16. Each experiment is performed in a scratch copy and changes one thing. The prose quotes the observed result, and the handback includes the raw filtered output.
17. Attribution (standing rule: credit every source a chapter leans on, by author and work, where the idea is used; nothing copied; quotations exact from fetched pages; a missing credit is blocking):
    - ch14 credits GoF and quotes the typing docs (`assert_never`) and the random docs exactly.
    - ch15 credits GoF and Percival and Gregory ("Commands and Command Handler") and quotes the collections docs and the What's New `frozendict` sentence exactly.
    - GoF claims appear only if verified, with the bracketed fallbacks applied. Each prose agent lists the sources it checked.
    - Every book cited is already in `bibliography.html` and in hub `books.yml` `referenced_by` (decision 6).
18. Claims:
    - Every factual sentence in ch14-15 maps to a named test, a recorded run (`run: H5` or a file under `_plans/evidence/`) or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0. The claims table lists rows 1-84, with 75-84 resolved, and each `source:` URL appears in its chapter.
    - No `run: G*` token appears in rows 75-84.
19. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has sixteen entries, and `diagrams/0*-*` and `diagrams/1[0-3]-*` are unchanged.
20. Reconciliation rows 75-84 are `verified` or `adjusted` with evidence. Row 1 carries the r07 note.
21. Deterministic: no test depends on wall time, the environment, memory addresses, an unseeded or shared module generator, or iteration order it didn't create. `filterwarnings = ["error"]` is still in the root config. The `-O` subprocess test passes `-I` and no environment beyond the interpreter's.
22. CI `ci-ok` is green on the PR. Merge happens only after the user's explicit approval.
23. Every self-contained mypy snippet that stands for src code (ch14 tests 10-12, ch15 test 18) has its shape checked against src by an `ast` test, or the prose says the snippet is a reduced model.

## Risks

- **Predicted messages.** r05 and r06 each mispredicted. Everything in Planning evidence was run, but the snippets were reduced models. Expect the line numbers (never asserted) and the tuple-match type text (it names the snippet's own enum) to differ. Tests match stable substrings, and differences go in "Corrections after the build".
- **The tuple-match finding can age.** A later mypy may prove the complete tuple match exhaustive. The prose states it as "mypy 2.4.1 reports" and the test pins it, so a mypy bump that changes it fails visibly rather than silently. The same applies to the wildcard finding.
- **Run-token and test-name collisions.** Decision 1 and criterion 3 guard against both. The deletion-table rows that need new tests must check their names too.
- **Two forms plus a comparison fixture** in ch14 may crowd 2,500 words. Section 8 holds at most one excerpt and about 260 words. If the floor and ceiling can't both be met, the state-object fixture's prose shrinks first, and its tests stay.
- **Duplication between the table and the match form.** It's deliberate and witnessed by the product test. The prose must say why both exist (data vs per-state data), or it reads as redundancy.
- **The probabilistic test values** depend on CPython's `Random.random()` sequence. The docs guarantee it for the same seed and the compatible seeder. The float comparison `<` with probability 0 or 1 is exact. The deletion rows for `<=` and the cap are predictions.
- **Global random state.** Test 22 reads `random.getstate()` and never seeds. If any other test or plugin draws from the module generator in the same process between the two reads, the test fails. It reads both states in one call frame around one `simulate_transit` call.
- **The `-O` subprocess test** runs a child interpreter. It must use `sys.executable` with `-I`, pass no environment-dependent paths, and keep within pytest's default time (no timeout asserted).
- **Overlap** with the three-way split (deque of partials, two-field `Amendment`), "Dataclasses and value semantics" (frozen is shallow), Memento (snapshots), Prototype (`replace`, copying), Visitor (`match` + `assert_never` over events), dict dispatch and asyncio queues. Criterion 9 greps for it, and pointers go by title only.
- **Domain row 15 wording** changes at H0 (decision 4). If the owner declines, the chapter must teach the callable-field `Amendment` as the answer, and the stale-inverse test becomes its known limitation.
- **ruff.** N818 holds (`TransitionError`, `AmendmentError`). F601 must fire only in the scratch run, never in src. B009/B010 aren't relevant. `RUF012` is not triggered by frozen dataclass `frozendict` defaults; the executor confirms.
- **Liquid.** f-strings with `{{` in excerpts need `{% raw %}`; validate.py checks.
- **Attribution.** GoF can't be quoted. The *Fluent Python* and *Architecture Patterns with Python* chapter titles were verified from the code repository and the free online edition's contents, not the publisher pages.
- **`uv.lock` race.** H1a and H1b are sequenced, and project names normalise to the package names.
