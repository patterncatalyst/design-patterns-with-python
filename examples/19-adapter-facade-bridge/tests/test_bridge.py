import ast
from collections.abc import Callable, Sequence
from decimal import Decimal
from pathlib import Path

import adapter_facade_bridge.bookings
import pytest
from adapter_facade_bridge.bookings import InsuredBooking
from adapter_facade_bridge.desk import ship
from adapter_facade_bridge.domain import Booking, BookingError, Consignment, Money
from adapter_facade_bridge.gateways import CarrierGateway


def test_every_booking_kind_works_with_every_carrier(
    place: Callable[[Consignment], Booking],
    consignment: Consignment,
    carrier: str,
    booking_kind: str,
    declared_value: Money,
    expected_reference: str,
    cover_sent_to_sdk: Sequence[object],
    expected_cover_sent_to_sdk: Sequence[object],
) -> None:
    booking = place(consignment)

    insured = booking_kind == "insured"
    assert booking == Booking(carrier, expected_reference, declared_value if insured else None)
    assert list(cover_sent_to_sdk) == (list(expected_cover_sent_to_sdk) if insured else [])


def _class_names(source: str) -> list[str]:
    return [node.name for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ClassDef)]


def test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier() -> None:
    """Two booking kinds and two carriers: the bridge declares 2 + 0 classes beyond the gateways
    (N + M, with the carriers already adapted), the class-per-pair design declares 4 + 1 (N x M)."""
    bridge = _class_names(Path(adapter_facade_bridge.bookings.__file__).read_text())
    tree = ast.parse(Path(__file__).with_name("conftest.py").read_text())
    pairs = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
        and (
            node.name == "_CarrierBooking"
            or any(
                isinstance(base, ast.Name) and base.id == "_CarrierBooking" for base in node.bases
            )
        )
    }

    assert sorted(bridge) == ["InsuredBooking", "StandardBooking"]
    assert pairs == {
        "_AircoInsuredBooking",
        "_AircoStandardBooking",
        "_CarrierBooking",
        "_FastlineInsuredBooking",
        "_FastlineStandardBooking",
    }


def test_an_insured_booking_records_the_declared_value_with_the_carrier(
    consignment: Consignment,
    carrier: str,
    gateways: dict[str, CarrierGateway],
    declared_value: Money,
    cover_sent_to_sdk: Sequence[object],
    expected_cover_sent_to_sdk: Sequence[object],
) -> None:
    booking = ship(consignment, carrier, gateways=gateways, declared_value=declared_value)

    assert booking.insured_for == declared_value
    assert list(cover_sent_to_sdk) == list(expected_cover_sent_to_sdk)


@pytest.mark.parametrize("amount", [Decimal(0), Decimal(-5)], ids=["zero", "negative"])
def test_an_insured_booking_without_a_declared_value_is_a_booking_error(
    amount: Decimal, gateways: dict[str, CarrierGateway]
) -> None:
    with pytest.raises(BookingError, match="declared value must be positive"):
        InsuredBooking(gateways["AIRCO"], Money(amount, "EUR"))
