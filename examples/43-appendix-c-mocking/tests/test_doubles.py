"""Making a double: what each form refuses, and what it wraps."""

import asyncio
from decimal import Decimal

import pytest
from mocking_reference.carriers import CarrierGateway, CarrierQuote, ConsignmentId, FastlineGateway
from pytest_mock import MockerFixture

CN1 = ConsignmentId("CN-1")


def test_spec_set_refuses_setting_a_name_the_spec_lacks(mocker: MockerFixture) -> None:
    loose = mocker.Mock(spec=CarrierGateway)
    strict = mocker.Mock(spec_set=CarrierGateway)

    loose.cancel = "set"
    with pytest.raises(AttributeError, match="Mock object has no attribute 'cancel'"):
        strict.cancel = "set"
    with pytest.raises(AttributeError, match="Mock object has no attribute 'cancel'"):
        _ = strict.cancel

    assert loose.cancel == "set"


def test_seal_stops_new_attributes_on_a_configured_mock(mocker: MockerFixture) -> None:
    gateway = mocker.Mock()
    gateway.book.return_value = "FASTLINE:CN-1"

    mocker.seal(gateway)

    assert gateway.book(CN1) == "FASTLINE:CN-1"
    with pytest.raises(AttributeError, match="quote"):
        gateway.quote(CN1, Decimal("1"))


def test_an_assertion_typo_raises_instead_of_passing(mocker: MockerFixture) -> None:
    gateway = mocker.Mock()
    unchecked = mocker.Mock(unsafe=True)

    with pytest.raises(AttributeError, match="assret_called_once"):
        gateway.assret_called_once()

    unchecked.assret_called_once()
    assert unchecked.assret_called_once.call_count == 1
    with pytest.raises(AttributeError, match="assret_called_once"):
        unchecked.book.assret_called_once()


def test_a_magic_mock_supports_the_magic_methods_a_mock_lacks(mocker: MockerFixture) -> None:
    magic = mocker.MagicMock()
    plain = mocker.Mock()

    assert len(magic) == 0
    with pytest.raises(TypeError, match="has no len"):
        len(plain)


def test_wraps_passes_calls_through_to_the_real_gateway(
    mocker: MockerFixture, fastline: FastlineGateway
) -> None:
    wrapper = mocker.Mock(wraps=fastline)

    quote = wrapper.quote(CN1, Decimal("10"))

    assert quote == CarrierQuote("FASTLINE", Decimal("4.50"))
    wrapper.quote.assert_called_once_with(CN1, Decimal("10"))


def test_async_mock_return_value_is_awaited(mocker: MockerFixture) -> None:
    confirm = mocker.AsyncMock(return_value="CONFIRMED:FASTLINE:CN-1")

    assert asyncio.run(confirm("FASTLINE:CN-1")) == "CONFIRMED:FASTLINE:CN-1"
    confirm.assert_awaited_once_with("FASTLINE:CN-1")
