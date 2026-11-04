from datetime import datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture
from testing_baseline.carriers import CarrierGateway, CarrierQuote, CarrierTimeoutError
from testing_baseline.domain import Consignment, Money
from testing_baseline.engine import RateEngine

if TYPE_CHECKING:
    from conftest import FakeFactory


def _usd(amount: str) -> Money:
    return Money(Decimal(amount), "USD")


def test_book_best_books_only_the_winner(
    mocker: MockerFixture, consignment: Consignment, fixed_now: datetime
) -> None:
    winner = mocker.create_autospec(CarrierGateway, instance=True)
    loser = mocker.create_autospec(CarrierGateway, instance=True)
    winner.quote.return_value = CarrierQuote("airco", _usd("10.00"))
    loser.quote.return_value = CarrierQuote("fastline", _usd("12.00"))
    winner.book.return_value = "AIRCO:CN-00000001"
    engine = RateEngine(
        {"airco": winner, "fastline": loser}, clock=lambda: fixed_now, validity=timedelta(hours=1)
    )

    assert engine.book_best(consignment) == "AIRCO:CN-00000001"

    winner.book.assert_called_once_with(consignment)
    loser.book.assert_not_called()


def test_a_plain_mock_passes_an_assertion_on_a_misspelled_method(
    mocker: MockerFixture, consignment: Consignment
) -> None:
    loser = mocker.Mock()
    loser.book(consignment)

    loser.bok.assert_not_called()

    with pytest.raises(AssertionError, match="Expected 'book' to not have been called"):
        loser.book.assert_not_called()


def test_spec_rejects_unknown_names_but_not_wrong_signatures(mocker: MockerFixture) -> None:
    gateway = mocker.Mock(spec=CarrierGateway)

    with pytest.raises(AttributeError, match="has no attribute 'bok'"):
        _ = gateway.bok

    gateway.book()
    gateway.book.assert_called_once_with()


def test_autospec_rejects_names_and_signatures(mocker: MockerFixture) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)

    with pytest.raises(AttributeError, match="has no attribute 'bok'"):
        _ = gateway.bok

    with pytest.raises(TypeError, match="missing a required argument: 'consignment'"):
        gateway.book()


def test_a_fake_rejects_unknown_names_and_wrong_signatures(make_fake: FakeFactory) -> None:
    fake = make_fake("fastline", _usd("10.00"))

    with pytest.raises(AttributeError, match="has no attribute 'bok'"):
        _ = fake.bok  # type: ignore[attr-defined]

    with pytest.raises(TypeError, match="missing 1 required positional argument: 'consignment'"):
        fake.book()  # type: ignore[call-arg]


def test_side_effect_drives_the_timeout_branch(
    mocker: MockerFixture, consignment: Consignment, fixed_now: datetime
) -> None:
    slow = mocker.create_autospec(CarrierGateway, instance=True)
    slow.quote.side_effect = CarrierTimeoutError("fastline")
    quick = mocker.create_autospec(CarrierGateway, instance=True)
    quick.quote.return_value = CarrierQuote("airco", _usd("10.00"))
    engine = RateEngine(
        {"fastline": slow, "airco": quick}, clock=lambda: fixed_now, validity=timedelta(hours=1)
    )

    quote = engine.best_quote(consignment)

    assert quote.carrier == "airco"
    assert quote.skipped == ("fastline",)
    slow.quote.assert_called_once_with(consignment)
