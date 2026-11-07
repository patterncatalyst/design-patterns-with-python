"""The booking function the doubles are used on."""

from decimal import Decimal

import pytest
from mocking_reference.booking import book_cheapest
from mocking_reference.carriers import (
    CarrierGateway,
    CarrierQuote,
    CarrierTimeoutError,
    ConsignmentId,
    FastlineGateway,
)
from pytest_mock import MockerFixture

CN1 = ConsignmentId("CN-1")


def test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first(mocker: MockerFixture) -> None:
    first_code = mocker.create_autospec(CarrierGateway, instance=True)
    second_code = mocker.create_autospec(CarrierGateway, instance=True)
    first_code.quote.return_value = CarrierQuote("ZEDEX", Decimal("5.00"))
    second_code.quote.return_value = CarrierQuote("ALPHA", Decimal("5.00"))
    second_code.book.return_value = "ALPHA:CN-1"

    reference = book_cheapest(
        {"a": first_code, "b": second_code}, CN1, Decimal("1"), notify=mocker.stub()
    )

    assert reference == "ALPHA:CN-1"
    first_code.book.assert_not_called()


def test_a_carrier_that_times_out_is_skipped(mocker: MockerFixture) -> None:
    slow = mocker.create_autospec(CarrierGateway, instance=True)
    slow.quote.side_effect = CarrierTimeoutError("slow")
    notify = mocker.stub(name="notify")

    reference = book_cheapest(
        {"a-slow": slow, "b-fastline": FastlineGateway()}, CN1, Decimal("10"), notify=notify
    )

    assert reference == "FASTLINE:CN-1"
    slow.book.assert_not_called()


def test_every_carrier_timing_out_raises_lookup_error(mocker: MockerFixture) -> None:
    slow = mocker.create_autospec(CarrierGateway, instance=True)
    slow.quote.side_effect = CarrierTimeoutError("slow")
    notify = mocker.stub(name="notify")

    with pytest.raises(LookupError, match="no carrier answered for CN-1"):
        book_cheapest({"a": slow}, CN1, Decimal("1"), notify=notify)

    notify.assert_not_called()
