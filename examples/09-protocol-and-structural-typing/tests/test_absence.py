import copy
from decimal import Decimal

import pytest
from structural_typing.carriers import (
    ACCOUNT_DEFAULT,
    GATEWAYS,
    CarrierGateway,
    FastlineGateway,
    book_with,
    carriers_to_ask,
    find_gateway,
)
from structural_typing.domain import BookingError, Consignment, Money
from structural_typing.pricing import flat_rate, quote


class _NullGateway:
    """Negative fixture: a null object that does nothing and reports success."""

    def book(self, consignment: Consignment, /) -> str:
        return ""


def test_find_gateway_returns_none_for_an_unknown_code() -> None:
    assert find_gateway("UNKNOWN") is None
    assert isinstance(find_gateway("FASTLINE"), FastlineGateway)


def test_book_with_turns_absence_into_a_booking_error(consignment: Consignment) -> None:
    assert book_with("FASTLINE", consignment) == "FASTLINE:CN-00000001"
    with pytest.raises(BookingError, match="unknown carrier 'UNKNOWN'"):
        book_with("UNKNOWN", consignment)


def test_a_null_gateway_hides_a_lost_booking(consignment: Consignment) -> None:
    gateway: CarrierGateway = _NullGateway()
    reference = gateway.book(consignment)
    assert reference == ""


def test_no_discount_is_a_null_object_that_loses_nothing(consignment: Consignment) -> None:
    assert quote(consignment, flat_rate) == flat_rate(consignment)

    def ten_euro_off(consignment: Consignment, /) -> Money:
        return Money(Decimal("10.00"), "EUR")

    assert quote(consignment, flat_rate, ten_euro_off) == Money(Decimal("15.00"), "EUR")


def test_a_sentinel_separates_not_given_from_none() -> None:
    assert carriers_to_ask() == ("FASTLINE",)
    assert carriers_to_ask(account_carrier="AIRCO") == ("AIRCO",)
    assert carriers_to_ask(None) == ("AIRCO", "FASTLINE")
    assert carriers_to_ask("AIRCO") == ("AIRCO",)
    with pytest.raises(BookingError, match="unknown carrier 'ZZZ'"):
        carriers_to_ask("ZZZ")
    assert copy.copy(ACCOUNT_DEFAULT) is ACCOUNT_DEFAULT
    assert bool(ACCOUNT_DEFAULT) is True


def test_the_registry_is_a_frozendict() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        GATEWAYS["ZZZ"] = FastlineGateway  # type: ignore[index]
    assert not isinstance(GATEWAYS, dict)
    assert isinstance(GATEWAYS, frozendict)
