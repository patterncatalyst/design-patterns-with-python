from collections.abc import Callable, Mapping
from decimal import Decimal

import pytest
from adapter_facade_bridge.desk import default_gateways, ship
from adapter_facade_bridge.domain import (
    POUND_IN_KILOGRAMS,
    Booking,
    Consignment,
    UnknownCarrierError,
    Weight,
)
from adapter_facade_bridge.gateways import CarrierGateway, FastlineGateway
from adapter_facade_bridge.sdks import AircoClient, FastlineClient


def test_a_client_whose_shape_matches_needs_no_adapter(consignment: Consignment) -> None:
    gateways = default_gateways()

    booking = ship(consignment, "AIRCO", gateways=gateways)

    assert type(gateways["AIRCO"]) is AircoClient
    assert booking.reference == "AC-CN-1"


def test_the_fastline_adapter_translates_the_booking_call(
    gateway_form: tuple[CarrierGateway, FastlineClient], consignment: Consignment
) -> None:
    gateway, client = gateway_form

    reference = gateway.book(consignment.id, consignment.weight)
    gateway.book(consignment.id, Weight.from_pounds(Decimal("1.005")))

    assert client.payloads == [
        {"ref": "CN-1", "weight_lb": "22.05"},
        {"ref": "CN-1", "weight_lb": "1.01"},
    ]
    assert reference.startswith("FL-")


def test_a_class_adapter_still_exposes_the_clients_own_methods(
    class_adapter: CarrierGateway,
) -> None:
    assert hasattr(class_adapter, "submit_shipment")
    assert not hasattr(FastlineGateway(FastlineClient()), "submit_shipment")


def test_weight_converts_between_kilograms_and_pounds_exactly() -> None:
    assert Decimal("0.45359237") == POUND_IN_KILOGRAMS
    assert Weight.from_pounds(Decimal(1)).kilograms == POUND_IN_KILOGRAMS
    assert Weight(Decimal(10)).pounds.quantize(Decimal("0.01")) == Decimal("22.05")


def test_a_pounds_api_called_with_kilograms_books_the_wrong_weight(
    consignment: Consignment,
    fastline_client: FastlineClient,
    book_by_branching: Callable[[Consignment, str], Booking],
) -> None:
    book_by_branching(consignment, "FASTLINE")

    sent = fastline_client.payloads[0]["weight_lb"]
    assert sent == "10"
    assert Weight.from_pounds(Decimal(sent)).kilograms.quantize(Decimal("0.01")) == Decimal("4.54")


def test_an_unknown_carrier_is_refused_at_the_desk(consignment: Consignment) -> None:
    with pytest.raises(UnknownCarrierError, match="unknown carrier 'NOSUCH'") as raised:
        ship(consignment, "NOSUCH", gateways=default_gateways())

    assert raised.value.__cause__ is None
    assert raised.value.__suppress_context__


def test_the_desk_registry_is_read_only() -> None:
    registry: Mapping[str, CarrierGateway] = default_gateways()

    with pytest.raises(TypeError, match="does not support item assignment"):
        registry["NOSUCH"] = AircoClient()  # type: ignore[index]

    assert not isinstance(registry, dict)


@pytest.mark.parametrize(
    "kilograms",
    [Decimal(0), Decimal(-1), Decimal("NaN")],
    ids=["zero", "negative", "nan"],
)
def test_a_consignment_weight_must_be_positive_and_finite(kilograms: Decimal) -> None:
    with pytest.raises(ValueError, match="weight must be positive and finite"):
        Weight(kilograms)
