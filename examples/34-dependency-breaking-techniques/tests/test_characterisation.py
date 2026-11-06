from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from dependency_breaking.domain import CarrierTimeoutError, Consignment, ConsignmentId

if TYPE_CHECKING:
    from conftest import CarrierAnswers, Step


@dataclass(frozen=True, slots=True)
class Row:
    """One consignment, what the two carriers answer, and what the engine quotes today."""

    id: str
    zone: str
    weight_kg: Decimal
    fastline_price: Decimal
    airco_cents: int
    carrier: str
    total: str
    calls: list[tuple[str, str, str]]


CHARACTERISATION_ROWS = [
    Row(
        "fastline-cheaper",
        "EU",
        Decimal("12.5"),
        Decimal("25.00"),
        2800,
        "FASTLINE",
        "27.50",
        [("AIRCO", "EU", "12500"), ("FASTLINE", "EU", "12.5")],
    ),
    Row(
        "airco-cheaper",
        "ASIA",
        Decimal("12.5"),
        Decimal("60.00"),
        5450,
        "AIRCO",
        "59.95",
        [("AIRCO", "ASIA", "12500"), ("FASTLINE", "ASIA", "12.5")],
    ),
    Row(
        "tie-goes-to-airco",
        "EU",
        Decimal("1"),
        Decimal("20.00"),
        2000,
        "AIRCO",
        "22.00",
        [("AIRCO", "EU", "1000"), ("FASTLINE", "EU", "1")],
    ),
    Row(
        "margin-rounds-half-up",
        "EU",
        Decimal("1"),
        Decimal("10.15"),
        2000,
        "FASTLINE",
        "11.17",
        [("AIRCO", "EU", "1000"), ("FASTLINE", "EU", "1")],
    ),
    Row(
        "grams-truncated",
        "EU",
        Decimal("0.0006"),
        Decimal("30.00"),
        1,
        "AIRCO",
        "0.01",
        [("AIRCO", "EU", "0"), ("FASTLINE", "EU", "0.0006")],
    ),
]


def _observed(
    step: Step, carrier_answers: type[CarrierAnswers], row: Row
) -> tuple[str, str, list[tuple[str, str, str]]]:
    """What a form of the engine quotes for a row, and the carrier calls it made."""
    quote_for, calls = step(carrier_answers(row.fastline_price, row.airco_cents))
    quote = quote_for(Consignment(ConsignmentId("CN-1"), row.zone, row.weight_kg))
    return quote.carrier, str(quote.total.amount), sorted(calls)


@pytest.mark.parametrize(
    "row", CHARACTERISATION_ROWS, ids=[row.id for row in CHARACTERISATION_ROWS]
)
def test_every_step_matches_the_characterisation_table(
    step: Step, carrier_answers: type[CarrierAnswers], row: Row
) -> None:
    assert _observed(step, carrier_answers, row) == (row.carrier, row.total, row.calls)


def test_every_step_lets_a_carrier_timeout_fail_the_quote(
    step: Step, carrier_answers: type[CarrierAnswers], consignment: Consignment
) -> None:
    answers = carrier_answers(
        Decimal("25.00"), 2800, fastline_error="FASTLINE did not answer for 'EU'"
    )
    quote_for, _calls = step(answers)

    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer for 'EU'"):
        quote_for(consignment)


@pytest.mark.parametrize(
    ("mutant", "failing"),
    [("grams-rounded", ["grams-truncated"]), ("half-even", ["margin-rounds-half-up"])],
)
def test_the_table_catches_a_step_that_changes_behaviour(
    mutant_steps: dict[str, Step],
    carrier_answers: type[CarrierAnswers],
    mutant: str,
    failing: list[str],
) -> None:
    mutant_step = mutant_steps[mutant]

    failed = [
        row.id
        for row in CHARACTERISATION_ROWS
        if _observed(mutant_step, carrier_answers, row) != (row.carrier, row.total, row.calls)
    ]

    assert failed == failing
