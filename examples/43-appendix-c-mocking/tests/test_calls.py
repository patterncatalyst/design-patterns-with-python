"""Configuring a double and reading back what was called."""

from decimal import Decimal
from unittest import mock

import pytest
from mocking_reference.booking import book_cheapest
from mocking_reference.carriers import (
    CarrierGateway,
    CarrierQuote,
    CarrierTimeoutError,
    ConsignmentId,
)
from pytest_mock import MockerFixture

CN1 = ConsignmentId("CN-1")
ONE = Decimal("1")


def test_side_effect_iterable_returns_each_value_then_raises_stop_iteration(
    mocker: MockerFixture,
) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)
    gateway.quote.side_effect = [CarrierQuote("FASTLINE", ONE), CarrierTimeoutError("late")]

    assert gateway.quote(CN1, ONE) == CarrierQuote("FASTLINE", ONE)
    with pytest.raises(CarrierTimeoutError, match="late"):
        gateway.quote(CN1, ONE)
    with pytest.raises(StopIteration):
        gateway.quote(CN1, ONE)


def test_side_effect_callable_computes_the_return_value(mocker: MockerFixture) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)

    def per_kilogram(consignment_id: ConsignmentId, weight_kg: Decimal, /) -> CarrierQuote:
        return CarrierQuote("PERKG", weight_kg * 2)

    gateway.quote.side_effect = per_kilogram

    assert [gateway.quote(CN1, Decimal(kg)).total for kg in (1, 5)] == [Decimal("2"), Decimal("10")]


def test_mock_calls_records_calls_in_order_with_call_objects(mocker: MockerFixture) -> None:
    airco = mocker.create_autospec(CarrierGateway, instance=True)
    fastline = mocker.create_autospec(CarrierGateway, instance=True)
    airco.quote.return_value = CarrierQuote("AIRCO", Decimal("12.00"))
    fastline.quote.return_value = CarrierQuote("FASTLINE", Decimal("9.00"))
    fastline.book.return_value = "FASTLINE:CN-1"
    manager = mocker.Mock()
    manager.attach_mock(airco, "airco")
    manager.attach_mock(fastline, "fastline")
    notify = mocker.stub(name="notify")

    book_cheapest({"fastline": fastline, "airco": airco}, CN1, Decimal("20"), notify=notify)

    assert manager.mock_calls == [
        mock.call.airco.quote(CN1, Decimal("20")),
        mock.call.fastline.quote(CN1, Decimal("20")),
        mock.call.fastline.book(CN1),
    ]
    assert fastline.mock_calls == [mock.call.quote(CN1, Decimal("20")), mock.call.book(CN1)]


def test_call_args_list_and_any_match_arguments(mocker: MockerFixture) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)

    gateway.quote(ConsignmentId("CN-1"), Decimal("1"))
    gateway.quote(ConsignmentId("CN-2"), Decimal("2"))

    assert gateway.quote.called
    assert gateway.quote.call_count == 2
    assert gateway.quote.call_args == mock.call("CN-2", Decimal("2"))
    assert gateway.quote.call_args_list == [
        mock.call("CN-1", mock.ANY),
        mock.call(mock.ANY, Decimal("2")),
    ]
    gateway.quote.assert_any_call("CN-1", Decimal("1"))


def test_assert_has_calls_checks_a_contiguous_ordered_run(mocker: MockerFixture) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)
    for number in ("CN-1", "CN-2", "CN-3"):
        gateway.book(ConsignmentId(number))

    gateway.book.assert_has_calls([mock.call("CN-2"), mock.call("CN-3")])
    with pytest.raises(AssertionError, match="Calls not found"):
        gateway.book.assert_has_calls([mock.call("CN-1"), mock.call("CN-3")])
    with pytest.raises(AssertionError, match="Calls not found"):
        gateway.book.assert_has_calls([mock.call("CN-3"), mock.call("CN-2")])
    gateway.book.assert_has_calls([mock.call("CN-3"), mock.call("CN-1")], any_order=True)


@pytest.mark.parametrize(
    ("clear_return_value", "after_reset"),
    [
        pytest.param(False, "configured", id="default"),
        pytest.param(True, "unconfigured", id="return_value=True"),
    ],
)
def test_reset_mock_clears_calls_but_keeps_return_value(
    mocker: MockerFixture, clear_return_value: bool, after_reset: str
) -> None:
    double = mocker.Mock(return_value="configured")
    double()

    double.reset_mock(return_value=clear_return_value)

    assert (double.call_count, double.mock_calls) == (0, [])
    answer = double()
    assert ("configured" if answer == "configured" else "unconfigured") == after_reset
