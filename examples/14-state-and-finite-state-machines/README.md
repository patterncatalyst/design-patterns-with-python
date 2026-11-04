# State and finite state machines

A consignment lifecycle (booked, loaded, in transit, cleared, delivered) written two ways, with a
test for every claim about what each form checks. The chapter's thesis is that State survives:
no language feature says which transitions are legal, so the lifecycle has to be written down in
one place and checked. What Python 3.15 changes is the shape of that place.

## What it witnesses

The table form.

- `TRANSITIONS` is a read-only `frozendict` from a status and an event kind to the next status.
  An absent pair is a `TransitionError` that names the event and the status.
- Tests walk the table as a graph: every status is reachable from booked, and delivered is
  terminal. A mutable `status` field accepts delivered to booked and nothing refuses it.
- mypy checks the type of each entry, so a swapped key or a wrong value is `[dict-item]`. It does
  not check legality, so a well-typed delivered-to-booked entry passes. A repeated key keeps the
  last value.

The match form.

- Frozen dataclass states hold only their own data: `InTransit` has `delay_days` and `Delivered`
  has no such field. `apply_event` matches on the state, guards each legal arm on the event kind,
  lists every state in one illegal arm and ends in `assert_never`.
- A state added to the union or an enum member added to a status match is an `[arg-type]` error
  naming it. A wildcard illegal arm hides the new state, and a tuple match is not proved
  exhaustive even when it is complete. `assert_never` still raises when asserts are stripped.
- The table and the match give the same answer for every status and event kind.

The state-object form (a test fixture).

- One object per state, each deciding the next state, passes the same lifecycle table. Adding an
  operation to the Protocol is a `[return-value]` error at each return site, and a state class
  that nothing returns is never checked.

The probabilistic variant.

- `sail_one_day` and `simulate_transit` draw from an injected `random.Random`. The same seed gives
  the same voyage, a shared generator gives a different second run, the bounds hold and the module
  generator is left alone. The voyage lengths and delay probabilities are illustrative.

## Layout

- `src/state_machines/domain.py`: `ConsignmentId`, `HandlingKind`, `ConsignmentStatus`,
  `HandlingEvent`, `TransitionError`.
- `src/state_machines/table.py`: `TRANSITIONS`, `next_status`.
- `src/state_machines/states.py`: `Booked`, `Loaded`, `InTransit`, `Cleared`, `Delivered`,
  `ConsignmentState`, `status_of`, `apply_event`, `track`.
- `src/state_machines/transit.py`: `sail_one_day`, `simulate_transit`.

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

`tests/test_lifecycle.py`

- `test_the_lifecycle_runs_booked_to_delivered`: both forms reach each status along the legal histories.
- `test_an_illegal_event_is_a_transition_error`: both forms refuse the illegal histories with the same message.
- `test_delivered_is_terminal`: every event kind from delivered is refused, in both forms.
- `test_the_two_forms_agree_on_every_status_and_event`: for every status and kind, both give the same status or the same refusal.
- `test_every_status_is_reachable_from_booked`: a breadth-first walk over `TRANSITIONS`.
- `test_the_transition_table_is_read_only`: assignment raises `TypeError` and the table is not a `dict`.
- `test_an_event_for_another_consignment_is_refused`: `track` names both consignments.
- `test_track_folds_a_history_into_the_final_state`: the final state and the state before the last event.
- `test_a_state_keeps_the_location_of_the_event_that_produced_it`: states carry their event's location.
- `test_each_state_carries_only_its_own_data`: `delay_days` exists on `InTransit` only, and assignment raises.
- `test_every_state_and_event_is_frozen`: each state and `HandlingEvent` refuses assignment.
- `test_a_transition_error_hides_the_key_error`: the `KeyError` is suppressed.
- `test_a_status_field_accepts_an_illegal_transition`: a mutable status field goes from delivered to booked.

`tests/test_state_objects.py`

- `test_state_objects_pass_the_same_lifecycle_table`: the object form gives the same results and messages.
- `test_state_objects_agree_with_the_transition_table`: for every status and kind, the objects and the table agree.

`tests/test_transit.py`

- `test_a_seeded_transit_is_reproducible`: seed 7 gives 11 delay days twice, seed 2026 gives 3.
- `test_a_shared_generator_gives_a_different_second_run`: 11, then 5.
- `test_transit_delay_bounds`: probability 0 is never delayed, probability 1 stops at the day cap.
- `test_a_draw_equal_to_the_probability_is_not_a_delay`: the comparison is strict.
- `test_a_draw_below_the_probability_is_a_delay`: a delay adds a delay day and no sailed day.
- `test_the_day_cap_bounds_the_number_of_draws`: a counting generator sees exactly the cap.
- `test_a_voyage_stops_drawing_once_the_schedule_is_sailed`: a counting generator sees exactly the scheduled days.
- `test_sailing_a_day_leaves_the_earlier_state_unchanged`: `InTransit` is replaced, not mutated.
- `test_the_model_leaves_the_module_generator_alone`: `random.getstate()` is equal before and after.

`tests/test_static.py`

- `test_mypy_reports_a_state_missing_from_the_match`: `[arg-type]` naming `Held`, and naming the enum member.
- `test_mypy_cannot_see_a_state_swallowed_by_a_wildcard`: clean.
- `test_mypy_cannot_prove_a_tuple_match_exhaustive`: `[arg-type]` on a complete tuple match.
- `test_mypy_checks_table_entry_types_but_not_legality`: `[dict-item]` twice, then clean for an illegal pair.
- `test_a_repeated_table_key_keeps_the_last_value`: runtime.
- `test_assert_never_raises_even_when_asserts_are_stripped`: a child interpreter with `-O`.
- `test_mypy_reports_an_operation_missing_from_a_state_object`: `[return-value]` with a note naming the member.
- `test_mypy_accepts_a_state_object_nothing_returns`: clean.
- `test_the_static_snippets_mirror_the_source`: the snippets' states and arms are the ones in `states.py`.

Classes named with a leading underscore in the test modules are test fixtures and aren't part of
the model code.
