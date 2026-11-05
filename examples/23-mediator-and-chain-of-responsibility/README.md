# Mediator and Chain of Responsibility

Two patterns that coordinate who acts: a chain decides whether a declaration is held, and a mediator
decides when a held consignment is released. The chapter's thesis is that both survive. Python
removes the handler class with its next-handler link, and the Mediator and Colleague classes, because
a stage is a callable and a colleague holds the mediator's `receive`. The decisions remain: what
"pass it on" means, which stage runs first, who decides when nobody does, and the rule for release
with its state. Port codes, consignment ids and harmonised-system codes are illustrative. The
mediator is documented as single-threaded, and the example has no thread or async test.

## What it witnesses

The chain.

- `type ClearanceStage = Callable[[CustomsDeclaration], Decision | None]`: `None` passes the
  declaration on. `clear(declaration, stages, /, *, final=release)` returns the first decision, and
  stages after it aren't called. `CLEARANCE_STAGES` is a tuple of `check_documents`, `assess_duty`
  and `inspect_goods`.
- `type FinalStage = Callable[[CustomsDeclaration], Decision]` can't pass. mypy refuses a stage that
  can, and a stage that falls off the end, a stage with the wrong return type, and a `Decision`
  left unhandled by a `match`.
- Order is not typed. `(check_documents, assess_duty, release, inspect_goods)` is accepted by mypy
  and clears a restricted commodity. A stage appended to `CLEARANCE_STAGES` runs before the final
  stage, and an empty chain leaves the decision to it.
- The comparison forms are fixtures in `tests/conftest.py`: `chain_form` is `stages`, `linked` (a
  `_Handler` holding the next handler) or `match` (one `match` with a default). All three run the
  same hold table. The linked chain returns `None` off the end for a clean declaration, which has its
  own test.

The mediator.

- `ClearanceMediator(declaration, *, release=...)` computes what is outstanding from `duty_paid` and
  `restricted`. `receive` takes `type ClearanceMessage = Settlement | Inspection` and uses `match`
  with `assert_never`. It releases once, with a `CLEARED` event at the declaration's port, when
  nothing is outstanding and nothing failed. A declaration with nothing outstanding is released at
  construction. A message for another consignment raises `ClearanceError`.
- `coordination_form` is `mediator` or `choreography`. In the choreography, colleagues call each
  other: inspection tells billing, and billing releases. It passes the inspection-first row and
  loses a settlement that arrives first, and that has its own test.

Static checks.

- mypy refuses a message the mediator doesn't know. It can't exhaust a `match` on `True` and `False`
  field patterns of a class (a reduced model), which is why the mediator's second arm is
  `case Inspection()`. The linked-chain check is a reduced model too.

## Layout

- `src/mediator_chain/domain.py`: `ConsignmentId`, `DocumentKind`, `Commodity`, `CustomsDeclaration`,
  `HandlingKind`, `HandlingEvent`, `TrackingHistory`.
- `src/mediator_chain/clearance.py`: `Released`, `Held`, `Decision`, `ClearanceStage`, `FinalStage`,
  the four stages, `CLEARANCE_STAGES`, `clear`, `describe`.
- `src/mediator_chain/mediator.py`: `Settlement`, `Inspection`, `ClearanceMessage`, `ClearanceError`,
  `ClearanceMediator`.

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

`tests/test_chain.py`

- `test_a_restricted_commodity_is_held_for_inspection`: all three chain forms.
- `test_a_declaration_missing_a_document_is_held`: a missing commercial invoice and a missing
  dangerous goods declaration, in all three forms.
- `test_an_unpaid_declaration_is_held_for_duty`: all three forms.
- `test_the_first_stage_that_decides_wins`: no invoice and unpaid duty gives the invoice reason.
- `test_a_clean_declaration_is_released`: the final stage releases.
- `test_a_linked_chain_with_no_terminal_returns_none`: the comparison form's failure.
- `test_stages_after_a_decision_are_not_called`: recorded stage names stop at the decision.
- `test_a_stage_added_after_release_clears_a_restricted_commodity`: order is a decision.
- `test_a_stage_added_to_the_chain_runs_before_the_final_stage`: a holding stage wins over release.
- `test_an_empty_chain_leaves_the_decision_to_the_final_stage`: releasing and holding finals.
- `test_describe_names_every_decision`: released and held.

`tests/test_mediator.py`

- `test_release_follows_inspection_then_settlement`: both coordination forms release once.
- `test_the_mediator_releases_in_either_order`: nothing after the first report, one event after the second.
- `test_a_choreography_loses_a_settlement_that_arrives_before_inspection`: an empty history.
- `test_a_duplicate_settlement_releases_once`: one event.
- `test_a_failed_inspection_holds_the_consignment`: no release after a settlement.
- `test_a_declaration_with_nothing_outstanding_is_released_at_once`: one event at construction.
- `test_a_message_for_another_consignment_is_refused`: `ClearanceError` naming `CN-2`, nothing released.
- `test_release_records_a_cleared_handling_event_at_the_port`: `CLEARED` at `NLRTM`.

`tests/test_static.py`

- `test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage`: `[arg-type]`.
- `test_mypy_cannot_see_release_placed_inside_the_chain`: clean.
- `test_mypy_refuses_a_stage_with_the_wrong_return_type`: `[arg-type]`.
- `test_mypy_reports_a_stage_that_falls_off_the_end`: `[return]`.
- `test_mypy_reports_a_decision_left_unhandled`: `[arg-type]`, expected `Never`.
- `test_mypy_refuses_a_linked_chain_result_where_a_decision_is_needed`: `[arg-type]` (a reduced model).
- `test_mypy_refuses_a_message_the_mediator_does_not_know`: `[arg-type]`.
- `test_mypy_cannot_exhaust_a_match_on_true_and_false_patterns`: `[arg-type]` (a reduced model).

Classes and functions named with a leading underscore in `tests/conftest.py` are test fixtures and
aren't part of the model code.
