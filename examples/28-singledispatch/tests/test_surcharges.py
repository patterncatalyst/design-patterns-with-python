from decimal import Decimal

import pytest
from singledispatch_visitor.money import Money
from singledispatch_visitor.surcharges import (
    DryContainer,
    ReeferContainer,
    SurchargeError,
    SurchargeSchedule,
    TankContainer,
)


@pytest.mark.parametrize(
    ("container", "expected"),
    [
        (DryContainer("C-1"), "0.00 EUR"),
        (ReeferContainer("C-2", Decimal(-18)), "200.00 EUR"),
        (TankContainer("C-3"), "150.00 EUR"),
    ],
    ids=["dry", "reefer", "tank"],
)
def test_surcharge_dispatches_on_the_container_kind(
    schedule: SurchargeSchedule, container: object, expected: str
) -> None:
    assert str(schedule.surcharge(container, 5)) == expected


def test_singledispatchmethod_dispatches_on_the_first_argument_after_self(
    schedule: SurchargeSchedule,
) -> None:
    reefer = ReeferContainer("C-2", Decimal(-18))

    assert schedule.surcharge(reefer, 1) == Money(Decimal("40.00"), "EUR")
    assert schedule.surcharge(reefer, 5) == Money(Decimal("200.00"), "EUR")
    with pytest.raises(SurchargeError, match="no surcharge rule for int"):
        schedule.surcharge(5, DryContainer("C-1"))
