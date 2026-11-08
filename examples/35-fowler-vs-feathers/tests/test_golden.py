"""Golden quotes: what the legacy engine quotes over a generated grid, recorded in a file."""

import json
from collections.abc import Callable, Mapping
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fowler_feathers.domain import Consignment, ConsignmentId
from fowler_feathers.refactored import CENT

if TYPE_CHECKING:
    from fowler_feathers.domain import RateQuote
    from fowler_feathers.legacy import AircoPrice, FastlineQuote

type QuoteFor = Callable[[Consignment], RateQuote]
type Form = Callable[[FastlineQuote, AircoPrice], QuoteFor]

GOLDEN_PATH = Path(__file__).parent / "golden" / "rate_quotes.json"

# Two zones, 0.5 kg to 30 kg in 0.5 kg steps: 120 consignments, none of them chosen.
GRID = [
    Consignment(ConsignmentId(f"{zone}-{kilograms}"), zone, kilograms)
    for zone in ("EU", "ASIA")
    for kilograms in (Decimal(halves) / 2 for halves in range(1, 61))
]

# Rows a reviewer can read, with values taken from the recorded file.
INLINE_GOLDEN = {
    "EU-0.5": "AIRCO 3.83",
    "EU-10": "AIRCO 13.86",
    "EU-30": "FASTLINE 32.51",
    "ASIA-0.5": "AIRCO 9.57",
    "ASIA-30": "FASTLINE 53.85",
}

CENT_FIRST_MISMATCHES = [
    "EU-11",
    "EU-13",
    "EU-15",
    "EU-16.5",
    "EU-17",
    "EU-18.5",
    "EU-19",
    "EU-21",
    "EU-21.5",
    "EU-23.5",
    "EU-25.5",
    "ASIA-19",
    "ASIA-19.5",
    "ASIA-20.5",
    "ASIA-23",
    "ASIA-25",
    "ASIA-25.5",
    "ASIA-26.5",
]


def _observed(quote_for: QuoteFor) -> list[tuple[str, str]]:
    """Every grid row as (id, 'CARRIER total'), in grid order."""
    quotes = [(consignment.id, quote_for(consignment)) for consignment in GRID]
    return [(row, f"{quote.carrier} {quote.total.amount}") for row, quote in quotes]


def _mismatches(observed: list[tuple[str, str]], golden: Mapping[str, str]) -> list[str]:
    """One line for every row whose quote differs from the golden one, in grid order."""
    lines = [
        f"{row}: golden {golden.get(row, 'missing')}, now {text}"
        for row, text in observed
        if golden.get(row) != text
    ]
    observed_rows = {row for row, _ in observed}
    missing = [
        f"{row}: golden {text}, now missing"
        for row, text in golden.items()
        if row not in observed_rows
    ]
    return lines + missing


def _write_golden(path: Path, golden: Mapping[str, str]) -> None:
    path.write_text(json.dumps(golden, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _read_golden(path: Path) -> dict[str, str]:
    golden: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
    return golden


def test_the_golden_file_records_the_legacy_engine(
    request: pytest.FixtureRequest,
    engine_forms: Mapping[str, Form],
    rate_cards: tuple[FastlineQuote, AircoPrice],
) -> None:
    observed = _observed(engine_forms["legacy"](*rate_cards))
    if request.config.getoption("--update-golden"):
        _write_golden(GOLDEN_PATH, dict(observed))
        pytest.skip("golden file rewritten; review the diff")
    assert _mismatches(observed, _read_golden(GOLDEN_PATH)) == []


def test_the_refactored_engine_matches_the_golden_quotes(
    engine_forms: Mapping[str, Form], rate_cards: tuple[FastlineQuote, AircoPrice]
) -> None:
    observed = _observed(engine_forms["refactored"](*rate_cards))
    assert _mismatches(observed, _read_golden(GOLDEN_PATH)) == []


@pytest.mark.parametrize("form", ["legacy", "refactored"])
def test_inline_golden_values_pin_the_rows_a_reviewer_reads(
    engine_forms: Mapping[str, Form], rate_cards: tuple[FastlineQuote, AircoPrice], form: str
) -> None:
    observed = dict(_observed(engine_forms[form](*rate_cards)))
    assert [observed[row] for row in INLINE_GOLDEN] == list(INLINE_GOLDEN.values())


@pytest.mark.parametrize(
    ("form", "expected"),
    [("cent-first", CENT_FIRST_MISMATCHES), ("round-builtin", ["EU-30", "ASIA-30"])],
)
def test_the_golden_quotes_catch_a_refactor_that_changes_rounding(
    engine_forms: Mapping[str, Form],
    rate_cards: tuple[FastlineQuote, AircoPrice],
    form: str,
    expected: list[str],
) -> None:
    mismatches = _mismatches(_observed(engine_forms[form](*rate_cards)), _read_golden(GOLDEN_PATH))
    assert [line.split(":")[0] for line in mismatches] == expected
    first = {
        "cent-first": "EU-11: golden FASTLINE 14.84, now FASTLINE 14.85",
        "round-builtin": "EU-30: golden FASTLINE 32.51, now FASTLINE 32.50",
    }
    assert mismatches[0] == first[form]


def test_round_with_two_digits_rounds_half_to_even_in_the_default_context() -> None:
    half_cent = Decimal("32.505")
    assert str(round(half_cent, 2)) == "32.50"
    assert str(half_cent.quantize(CENT, rounding=ROUND_HALF_UP)) == "32.51"


def test_the_golden_writer_sorts_and_indents(tmp_path: Path) -> None:
    golden = {"EU-1": "AIRCO 4.36", "ASIA-0.5": "AIRCO 9.57"}
    path = tmp_path / "golden.json"
    _write_golden(path, golden)
    assert path.read_text(encoding="utf-8") == (
        '{\n  "ASIA-0.5": "AIRCO 9.57",\n  "EU-1": "AIRCO 4.36"\n}\n'
    )
    assert list(_read_golden(path).items()) == [("ASIA-0.5", "AIRCO 9.57"), ("EU-1", "AIRCO 4.36")]
