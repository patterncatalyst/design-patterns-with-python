import typing
from collections.abc import Iterator, Sequence
from decimal import Decimal

import pytest
from adapter_facade_bridge import desk
from adapter_facade_bridge.desk import ship
from adapter_facade_bridge.domain import Booking, CarrierError, Consignment, Weight
from adapter_facade_bridge.gateways import CarrierGateway
from adapter_facade_bridge.sdks import FastlineRejectedError


def test_ship_books_each_carrier_through_one_call(
    consignment: Consignment,
    carrier: str,
    gateways: dict[str, CarrierGateway],
    expected_reference: str,
    sent_to_sdk: Sequence[object],
    expected_sent_to_sdk: Sequence[object],
) -> None:
    booking = ship(consignment, carrier, gateways=gateways)

    assert booking == Booking(carrier, expected_reference)
    assert list(sent_to_sdk) == list(expected_sent_to_sdk)


def _leaves(hint: object) -> Iterator[object]:
    """The classes inside a type hint, looking through unions and generic aliases."""
    arguments = typing.get_args(hint)
    if not arguments:
        yield hint
    for argument in arguments:
        yield from _leaves(argument)


def test_the_desk_names_no_sdk_type_in_its_public_surface() -> None:
    assert desk.__all__ == ["default_gateways", "ship"]
    for name in desk.__all__:
        hints = typing.get_type_hints(getattr(desk, name))
        assert hints
        for hint in hints.values():
            for leaf in _leaves(hint):
                assert getattr(leaf, "__module__", None) != "adapter_facade_bridge.sdks", (
                    name,
                    leaf,
                )


def test_a_carrier_rejection_becomes_a_carrier_error(
    consignment: Consignment, gateways: dict[str, CarrierGateway]
) -> None:
    heavy = Consignment(
        id=consignment.id,
        weight=Weight(Decimal(600)),
        origin=consignment.origin,
        destination=consignment.destination,
    )

    with pytest.raises(CarrierError, match="FASTLINE rejected CN-1") as raised:
        ship(heavy, "FASTLINE", gateways=gateways)

    assert isinstance(raised.value.__cause__, FastlineRejectedError)
