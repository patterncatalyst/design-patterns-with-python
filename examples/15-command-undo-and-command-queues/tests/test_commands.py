from decimal import Decimal
from functools import partial

import pytest
from command_undo.amendments import Amendment, Redirect, Reweigh, apply
from command_undo.domain import AmendmentError, BookingRequest, Weight


def kg(amount: int) -> Weight:
    return Weight(Decimal(amount))


def test_amendments_compare_by_value_and_partials_do_not() -> None:
    assert Reweigh(kg(130)) == Reweigh(kg(130))
    assert hash(Reweigh(kg(130))) == hash(Reweigh(kg(130)))
    assert repr(Redirect("MYPKG")) == "Redirect(destination='MYPKG')"
    first = partial(Reweigh, kg(130))
    second = partial(Reweigh, kg(130))
    assert first != second
    assert not hasattr(first, "undo")


def test_apply_returns_the_amendment_that_reverses_it(
    booking_request: BookingRequest, amendment: Amendment
) -> None:
    amended, inverse = apply(booking_request, amendment)
    assert amended != booking_request
    restored, again = apply(amended, inverse)
    assert restored == booking_request
    assert again == amendment


def test_a_redirect_needs_a_port_code(booking_request: BookingRequest) -> None:
    with pytest.raises(AmendmentError, match="not a port code: 'sgsin'"):
        apply(booking_request, Redirect("sgsin"))
    with pytest.raises(AmendmentError, match="not a port code: 'SGSIN '"):
        apply(booking_request, Redirect("SGSIN "))
    amended, _inverse = apply(booking_request, Redirect("MYPKG"))
    assert amended.consignment.destination == "MYPKG"


@pytest.mark.parametrize(
    "kilograms", [Decimal(0), Decimal(-1), Decimal("NaN"), Decimal("Infinity")]
)
def test_a_booked_weight_must_be_positive_and_finite(kilograms: Decimal) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        Weight(kilograms)
    assert Weight(Decimal("0.5")).kilograms == Decimal("0.5")
