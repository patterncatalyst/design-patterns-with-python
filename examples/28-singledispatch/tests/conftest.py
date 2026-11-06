"""Fixtures. The comparison form lives here as a fixture parameter so that it runs the same table
of commodities as the idiomatic code: ``tariff_code`` with a raising fallback, and a dispatcher
with a defaulting fallback that reuses the same implementations. ``fresh_dispatcher`` gives every
registration test its own dispatcher, because a registration on ``tariff_code`` would last for the
rest of the process."""

from collections.abc import Callable
from decimal import Decimal
from functools import singledispatch
from typing import TYPE_CHECKING

import pytest
from singledispatch_visitor.commodities import Coffee, InstantCoffee, TShirt
from singledispatch_visitor.money import Money
from singledispatch_visitor.surcharges import SurchargeSchedule
from singledispatch_visitor.tariff import tariff_code

if TYPE_CHECKING:
    from functools import _SingleDispatchCallable

type TariffLookup = Callable[[object], str]


@pytest.fixture
def defaulting_dispatcher() -> TariffLookup:
    """The comparison: the same implementations behind a fallback that answers."""

    @singledispatch
    def classify(commodity: object) -> str:
        return "unclassified"

    for kind in (Coffee, InstantCoffee, TShirt):
        classify.register(kind, tariff_code.registry[kind])
    return classify


@pytest.fixture(params=["raising", "defaulting"])
def fallback_form(
    request: pytest.FixtureRequest, defaulting_dispatcher: TariffLookup
) -> TariffLookup:
    """``tariff_code`` (raising) or the defaulting dispatcher."""
    if request.param == "raising":
        return tariff_code
    return defaulting_dispatcher


@pytest.fixture
def fresh_dispatcher() -> _SingleDispatchCallable[str]:
    """A new raising dispatcher per test, so no test registers on ``tariff_code``."""

    @singledispatch
    def classify(commodity: object) -> str:
        raise LookupError(type(commodity).__name__)

    return classify


@pytest.fixture
def schedule() -> SurchargeSchedule:
    """Illustrative rates: 40.00 EUR per reefer day, 150.00 EUR for a tank cleaning."""
    return SurchargeSchedule(
        reefer_per_day=Money(Decimal("40.00"), "EUR"),
        tank_cleaning=Money(Decimal("150.00"), "EUR"),
    )
