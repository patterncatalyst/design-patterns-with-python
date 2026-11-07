"""Tests written from the requirement: they say what the engine should do, not what it did."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from fowler_feathers.domain import CarrierTimeoutError, Consignment, ConsignmentId

if TYPE_CHECKING:
    from fowler_feathers.domain import RateQuote
    from fowler_feathers.legacy import AircoPrice, FastlineQuote

type QuoteFor = Callable[[Consignment], RateQuote]
type Form = Callable[[FastlineQuote, AircoPrice], QuoteFor]


@dataclass(frozen=True, slots=True)
class IntentRow:
    """The two carrier answers (euros, cents) and the quote the requirement asks for."""

    zone: str
    fastline_price: str
    airco_cents: int
    carrier: str
    total: str
    weight_kg: str = "12.5"
    grams: int = 12500


INTENT_ROWS = {
    "fastline-cheaper": IntentRow("EU", "25.00", 2800, "FASTLINE", "27.50"),
    "airco-cheaper": IntentRow("ASIA", "60.00", 5450, "AIRCO", "59.95"),
    "tie-goes-to-airco": IntentRow("EU", "20.00", 2000, "AIRCO", "22.00"),
    "margin-applied": IntentRow("EU", "30.00", 4000, "FASTLINE", "33.00"),
    # AIRCO answers 1 cent only for 0 g; any other weight gets a price FASTLINE beats.
    "grams-truncated": IntentRow("EU", "30.00", 1, "AIRCO", "0.01", "0.0006", 0),
}


def _fixed_answers(row: IntentRow) -> tuple[FastlineQuote, AircoPrice]:
    def fastline(zone: str, weight_kg: Decimal) -> Decimal:
        return Decimal(row.fastline_price)

    def airco(*, destination: str, grams: int) -> int:
        return row.airco_cents if grams == row.grams else 1_000_000

    return fastline, airco


def _consignment(zone: str, weight_kg: str = "12.5") -> Consignment:
    return Consignment(ConsignmentId("CN-1"), zone, Decimal(weight_kg))


@pytest.mark.parametrize("form", ["legacy", "refactored", "cent-first", "round-builtin"])
@pytest.mark.parametrize("row_id", list(INTENT_ROWS))
def test_the_intent_rows_pass_every_engine_and_both_rounding_refactors(
    engine_forms: Mapping[str, Form], form: str, row_id: str
) -> None:
    row = INTENT_ROWS[row_id]
    fastline, airco = _fixed_answers(row)
    quote = engine_forms[form](fastline, airco)(_consignment(row.zone, row.weight_kg))
    assert (quote.carrier, str(quote.total.amount)) == (row.carrier, row.total)


@pytest.mark.parametrize("form", ["legacy", "refactored"])
def test_every_engine_lets_a_carrier_timeout_fail_the_quote(
    engine_forms: Mapping[str, Form], form: str
) -> None:
    def fastline(zone: str, weight_kg: Decimal) -> Decimal:
        raise CarrierTimeoutError(f"FASTLINE did not answer for {zone!r}")

    def airco(*, destination: str, grams: int) -> int:
        return 2800

    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer"):
        engine_forms[form](fastline, airco)(_consignment("EU"))
