from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, assert_type

import pytest
from testing_baseline.carriers import CarrierGateway
from testing_baseline.domain import Consignment, Money, RatingError
from testing_baseline.engine import RateEngine

if TYPE_CHECKING:
    from conftest import FakeFactory


def _usd(amount: str) -> Money:
    return Money(Decimal(amount), "USD")


def _engine(gateways: dict[str, CarrierGateway], now: datetime, *, minutes: int = 30) -> RateEngine:
    return RateEngine(gateways, clock=lambda: now, validity=timedelta(minutes=minutes))


@pytest.mark.parametrize(
    ("fastline", "airco", "winner"),
    [
        pytest.param("10.00", "12.00", "fastline", id="fastline-cheaper"),
        pytest.param("12.00", "10.00", "airco", id="airco-cheaper"),
        pytest.param("10.00", "10.00", "airco", id="tie-goes-to-airco"),
    ],
)
def test_best_quote_picks_the_cheapest_carrier(
    fastline: str,
    airco: str,
    winner: str,
    consignment: Consignment,
    fixed_now: datetime,
    make_fake: FakeFactory,
) -> None:
    engine = _engine(
        {
            "fastline": make_fake("fastline", _usd(fastline)),
            "airco": make_fake("airco", _usd(airco)),
        },
        fixed_now,
    )

    quote = engine.best_quote(consignment)

    assert quote.carrier == winner
    assert quote.skipped == ()


def test_a_tie_is_broken_by_the_carrier_code_in_the_quote(
    consignment: Consignment, fixed_now: datetime, make_fake: FakeFactory
) -> None:
    """Mapping keys are account aliases here, so the iteration order says nothing about the code."""
    engine = _engine(
        {
            "account-1": make_fake("fastline", _usd("10.00")),
            "account-2": make_fake("airco", _usd("10.00")),
        },
        fixed_now,
    )

    assert engine.best_quote(consignment).carrier == "airco"


def test_quote_validity_comes_from_the_injected_clock(
    consignment: Consignment, fixed_now: datetime, make_fake: FakeFactory, quote_log: Path
) -> None:
    engine = _engine({"fastline": make_fake("fastline", _usd("10.00"))}, fixed_now, minutes=45)

    quote = engine.best_quote(consignment)

    assert_type(quote.total, Money)
    assert quote.total == _usd("10.00")
    assert quote.consignment_id == consignment.id
    assert quote.valid_until == fixed_now + timedelta(minutes=45)
    with quote_log.open("a", encoding="utf-8") as handle:
        handle.write(f"valid_until={quote.valid_until.isoformat()}\n")


def test_a_timed_out_carrier_is_skipped(
    consignment: Consignment, fixed_now: datetime, make_fake: FakeFactory
) -> None:
    engine = _engine(
        {
            "airco": make_fake("airco", _usd("1.00"), times_out=True),
            "fastline": make_fake("fastline", _usd("10.00")),
        },
        fixed_now,
    )

    quote = engine.best_quote(consignment)

    assert quote.carrier == "fastline"
    assert quote.skipped == ("airco",)


def test_carriers_are_asked_in_code_order(
    consignment: Consignment, fixed_now: datetime, make_fake: FakeFactory
) -> None:
    engine = _engine(
        {
            "zeta": make_fake("zeta", _usd("1.00"), times_out=True),
            "fastline": make_fake("fastline", _usd("10.00")),
            "airco": make_fake("airco", _usd("1.00"), times_out=True),
        },
        fixed_now,
    )

    assert engine.best_quote(consignment).skipped == ("airco", "zeta")


def test_every_carrier_timing_out_is_a_rating_error(
    consignment: Consignment, fixed_now: datetime, make_fake: FakeFactory
) -> None:
    engine = _engine(
        {
            "airco": make_fake("airco", _usd("1.00"), times_out=True),
            "fastline": make_fake("fastline", _usd("1.00"), times_out=True),
        },
        fixed_now,
    )

    with pytest.raises(RatingError, match="no carrier answered"):
        engine.best_quote(consignment)


def test_book_best_books_the_winner_and_returns_its_reference(
    consignment: Consignment, fixed_now: datetime, make_fake: FakeFactory
) -> None:
    winner = make_fake("airco", _usd("10.00"))
    loser = make_fake("fastline", _usd("12.00"))
    engine = _engine({"airco": winner, "fastline": loser}, fixed_now)

    assert engine.book_best(consignment) == "AIRCO:CN-00000001"
    assert winner.booked == [consignment]
    assert loser.booked == []
