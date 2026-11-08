"""Three gates over hand-written drafts: static gate, shape review and behaviour oracle."""

from collections.abc import Mapping
from decimal import Decimal
from itertools import product
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

import pytest
from review_gate import pricing
from review_gate.domain import Consignment, ConsignmentId, Weight
from review_gate.shape import review

if TYPE_CHECKING:
    from conftest import Draft, LoadModule, StaticGate

_PRICING = Path(__file__).resolve().parents[1] / "src" / "review_gate" / "pricing.py"

GRID = tuple(product(("flat", "per_kg"), ("0.5", "1", "2.5", "12.5", "40")))

# The idiomatic answers, recorded as literals so that the oracle does not use the code under
# review as its own reference. Three kilogram weights give half-cent products at 0.45 a kilogram.
EXPECTED_ROWS = (
    "10.00",
    "10.00",
    "10.00",
    "10.00",
    "10.00",
    "0.23",
    "0.45",
    "1.13",
    "5.63",
    "18.00",
)

# (static gate fails, shape review fails, oracle fails) for each draft.
TABLE = {
    "untyped_factory": (True, True, True),
    "typed_hierarchy": (False, True, False),
    "rounded_callable": (False, False, True),
}


def oracle(module: ModuleType) -> list[str]:
    """Run the draft's ``price`` over the grid and list each row that differs from the record."""
    failures: list[str] = []
    for index, ((rule, kilograms), expected) in enumerate(zip(GRID, EXPECTED_ROWS, strict=True)):
        consignment = Consignment(ConsignmentId(f"CN-{index}"), "EU", Weight(Decimal(kilograms)))
        actual = module.price(rule, consignment).amount
        if actual != Decimal(expected):
            failures.append(f"CN-{index} {rule}: {expected} != {actual}")
    return failures


def test_each_draft_fails_exactly_the_gates_in_the_table(
    draft: Draft, static_gate: StaticGate, load_module: LoadModule
) -> None:
    """Credits all three gates: a draft's row changes when a gate stops reporting it, for
    example when the oracle never fails or the shape review returns nothing."""
    outcome = (
        bool(static_gate(draft.text)),
        bool(review(draft.text)),
        bool(oracle(load_module(draft.text))),
    )

    assert outcome == TABLE[draft.name]


def test_every_draft_says_it_was_written_for_the_book(draft: Draft) -> None:
    assert draft.text.startswith("# Written for the book as a draft to review.\n")


def test_the_idiomatic_module_passes_every_gate(static_gate: StaticGate) -> None:
    """Credits the rounding in ``pricing.py``: ``round(amount, 2)`` makes the oracle list rows."""
    source = _PRICING.read_text()

    assert (static_gate(source), review(source), oracle(pricing)) == ([], [], [])


def test_the_static_gate_reports_the_untyped_draft(
    drafts: Mapping[str, str], static_gate: StaticGate
) -> None:
    """Credits the rule selection in the gate: dropping ``UP`` leaves only the mypy codes."""
    findings = static_gate(drafts["untyped_factory"])

    assert sorted((f.line, f.rule) for f in findings) == [
        (11, "no-untyped-def"),
        (16, "no-untyped-def"),
        (24, "no-untyped-def"),
        (27, "no-untyped-def"),
        (30, "no-untyped-def"),
        (36, "UP037"),
        (36, "UP045"),
        (38, "UP037"),
        (52, "no-untyped-call"),
    ]


def test_mypy_and_ruff_pass_the_typed_hierarchy(
    drafts: Mapping[str, str], static_gate: StaticGate
) -> None:
    source = drafts["typed_hierarchy"]

    assert (static_gate.mypy(source), static_gate.ruff(source)) == ([], [])

    unreachable = "def f() -> str:\n    return 'a'\n    return 'b'\n"
    assert [finding.rule for finding in static_gate.mypy(unreachable)] == ["unreachable"]


def test_the_shape_review_names_the_typed_hierarchy_rules(drafts: Mapping[str, str]) -> None:
    findings = review(drafts["typed_hierarchy"])

    assert [(f.line, f.rule) for f in findings] == [
        (8, "single-method-base"),
        (27, "static-only-class"),
    ]


def test_the_shape_review_names_the_untyped_draft_rules(drafts: Mapping[str, str]) -> None:
    findings = review(drafts["untyped_factory"])

    assert [(f.line, f.rule) for f in findings] == [
        (9, "single-method-base"),
        (24, "accessor-pair"),
        (38, "instance-in-new"),
    ]


@pytest.mark.parametrize("name", ["untyped_factory", "rounded_callable"])
def test_the_oracle_lists_the_half_cent_rows(
    name: str, drafts: Mapping[str, str], load_module: LoadModule
) -> None:
    assert oracle(load_module(drafts[name])) == [
        "CN-5 per_kg: 0.23 != 0.22",
        "CN-7 per_kg: 1.13 != 1.12",
        "CN-8 per_kg: 5.63 != 5.62",
    ]
