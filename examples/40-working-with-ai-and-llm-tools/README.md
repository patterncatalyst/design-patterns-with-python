# Working with AI and LLM tools

Three gates for reviewing a draft of pricing code, run over three drafts that were written for this
book. The drafts are text files in `tests/drafts/`, kept as `.py.txt`, and each opens with a comment
saying so. No test calls a model or the network.
The model client appears only as a Protocol with a recorded fake behind it.

## What it witnesses

The idiomatic module is `pricing.py`: `PricingRule` is a callable type, the rules sit in a read-only
`frozendict`, and `per_kg` rounds half up to the cent. The three drafts are measured against it:

| Draft | Static gate (`mypy --strict`, ruff) | Shape review | Behaviour oracle |
| --- | --- | --- | --- |
| `untyped_factory` | fails | fails | fails |
| `typed_hierarchy` | passes | fails | passes |
| `rounded_callable` | passes | passes | fails |

`shape.py` is the shape review. `review` parses a draft with `ast` and returns sorted `Finding`s for
four rules: `single-method-base`, `static-only-class`, `accessor-pair` and `instance-in-new`. The
rules are a checklist of four shapes and nothing more.

The behaviour oracle is `oracle` in `tests/test_gates.py`. It runs a draft's `price` over `GRID`,
a grid of consignments, and compares each answer with `EXPECTED_ROWS`, the idiomatic answers recorded as
literals. Both drafts that round with the context default or with `round()` differ on exactly three
rows, the ones whose product ends in a half cent. The oracle imports the draft's text as a module
with `importlib.util`, so it runs the draft's code: run it where a mistake costs nothing.

`assistant.py` holds the `Assistant` Protocol, the `RecordedAssistant` fake that replays recorded
replies and refuses a prompt it has no reply for, and `propose`, which gates each reply and sends
the findings back in the next prompt. `propose` stops at the first accepted reply and gives up after
its attempts.

## Layout

- `src/review_gate/domain.py`: `ConsignmentId`, `RatingError`, `Weight`, `Money`, `Consignment`.
- `src/review_gate/pricing.py`: `PricingRule`, `CENT`, `flat`, `per_kg`, `RULES`, `price`.
- `src/review_gate/shape.py`: `Finding`, `ShapeRule`, the four rules, `SHAPE_RULES`, `review`.
- `src/review_gate/assistant.py`: `Assistant`, `RecordedAssistant`, `Gate`, `Review`, `propose`.
- `tests/drafts/`: the three drafts, as data.
- `tests/conftest.py`: the `draft` fixture (one param per draft), the `static_gate` fixture and the
  `load_module` fixture.

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

`tests/test_gates.py`

- `test_each_draft_fails_exactly_the_gates_in_the_table`: the table above, once per draft.
- `test_the_idiomatic_module_passes_every_gate`
- `test_every_draft_says_it_was_written_for_the_book`
- `test_the_static_gate_reports_the_untyped_draft`: `UP037`, `UP045`, `no-untyped-call` and
  `no-untyped-def`.
- `test_mypy_and_ruff_pass_the_typed_hierarchy`
- `test_the_shape_review_names_the_typed_hierarchy_rules`
- `test_the_shape_review_names_the_untyped_draft_rules`
- `test_the_oracle_lists_the_half_cent_rows`: for the two drafts that round differently.

`tests/test_shape.py`

- `test_each_shape_rule_fires_on_its_minimal_case`: one case per rule.
- `test_shape_rules_stay_quiet_on_a_callable_class_and_a_frozen_dataclass`
- `test_a_getter_without_a_setter_is_not_an_accessor_pair`
- `test_findings_come_back_in_line_order`

`tests/test_assistant.py`

- `test_a_rejected_reply_is_sent_back_with_its_findings`
- `test_the_loop_stops_at_the_first_accepted_reply`
- `test_the_loop_gives_up_after_its_attempts`
- `test_an_unrecorded_prompt_is_refused`
- `test_the_package_imports_no_network_module`: no import of `socket`, `ssl`, `http`, `urllib`,
  `asyncio` or `subprocess` in the package.

`tests/test_static.py`

- `test_mypy_refuses_an_assistant_without_reply`

The tests use no mocks and no patching, and none sleeps or reads a clock. The static gate runs
`mypy --strict --warn-unreachable` through `mypy.api`, and ruff through the interpreter's `-m ruff`
with the repository's rule selection.
