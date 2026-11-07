"""Spies and stubs: record real behaviour, or record a callback."""

import asyncio
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from mocking_reference.booking import book_cheapest
from mocking_reference.carriers import (
    CarrierGateway,
    CarrierQuote,
    CarrierTimeoutError,
    ConsignmentId,
    FastlineGateway,
    confirm,
)
from pytest_mock import MockerFixture

CN1 = ConsignmentId("CN-1")
TEN = Decimal("10")


def test_spy_keeps_the_real_behaviour_and_records_returns(
    mocker: MockerFixture, fastline: FastlineGateway
) -> None:
    spy = mocker.spy(fastline, "quote")

    quote = fastline.quote(CN1, TEN)

    assert quote == CarrierQuote("FASTLINE", Decimal("4.50"))
    spy.assert_called_once_with(CN1, TEN)
    assert spy.spy_return == quote
    assert spy.spy_return_list == [quote]


def test_spy_records_the_exception_it_let_through(
    mocker: MockerFixture, fastline: FastlineGateway
) -> None:
    spy = mocker.spy(fastline, "quote")

    with pytest.raises(CarrierTimeoutError) as raised:
        fastline.quote(CN1, Decimal("501"))

    assert spy.spy_exception is raised.value
    assert spy.spy_return is None


def test_stub_records_a_callback(mocker: MockerFixture, fastline: FastlineGateway) -> None:
    notify = mocker.stub(name="notify")

    book_cheapest({"fastline": fastline}, CN1, TEN, notify=notify)

    notify.assert_called_once_with("FASTLINE:CN-1")


def test_resetall_resets_patches_spies_and_autospecs_but_not_stubs(
    mocker: MockerFixture, fastline: FastlineGateway
) -> None:
    patched = mocker.patch.object(FastlineGateway, "book", return_value="PATCHED")
    spy = mocker.spy(fastline, "quote")
    autospec = mocker.create_autospec(CarrierGateway, instance=True)
    stub = mocker.stub(name="notify")
    alias = mocker.Mock()
    fastline.book(CN1)
    fastline.quote(CN1, TEN)
    autospec.quote(CN1, TEN)
    stub("x")
    alias("x")

    mocker.resetall()

    counts: list[int] = [
        patched.call_count,
        spy.call_count,
        autospec.quote.call_count,
        stub.call_count,
        alias.call_count,
    ]
    assert counts == [0, 0, 0, 1, 1]


def test_autospec_of_an_async_function_records_the_await(mocker: MockerFixture) -> None:
    confirm_double: MagicMock = mocker.create_autospec(confirm)
    confirm_double.return_value = "CONFIRMED:FASTLINE:CN-1"

    result = asyncio.run(confirm_double("FASTLINE:CN-1"))

    assert result == "CONFIRMED:FASTLINE:CN-1"
    confirm_double.assert_awaited_once_with("FASTLINE:CN-1")
