from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from singledispatch_visitor.commodities import Coffee, InstantCoffee, LithiumIonBattery, TShirt
from singledispatch_visitor.tariff import TariffCodeError, tariff_code

if TYPE_CHECKING:
    from functools import _SingleDispatchCallable

    from conftest import TariffLookup

COMMODITY_CODES = [
    pytest.param(Coffee(roasted=False), "0901.11", id="coffee-green"),
    pytest.param(Coffee(roasted=False, decaffeinated=True), "0901.12", id="coffee-green-decaf"),
    pytest.param(Coffee(roasted=True), "0901.21", id="coffee-roasted"),
    pytest.param(Coffee(roasted=True, decaffeinated=True), "0901.22", id="coffee-roasted-decaf"),
    pytest.param(InstantCoffee(roasted=True), "2101.11", id="instant"),
    pytest.param(TShirt(cotton=True), "6109.10", id="tshirt-cotton"),
    pytest.param(TShirt(cotton=False), "6109.90", id="tshirt-other"),
]

BATTERY = LithiumIonBattery(Decimal(100))


@pytest.mark.parametrize(("commodity", "code"), COMMODITY_CODES)
def test_every_fallback_form_gives_registered_commodities_their_codes(
    fallback_form: TariffLookup, commodity: object, code: str
) -> None:
    assert fallback_form(commodity) == code


def test_a_raising_fallback_names_an_unregistered_kind() -> None:
    with pytest.raises(TariffCodeError, match="no tariff code for LithiumIonBattery"):
        tariff_code(BATTERY)


def test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently(
    defaulting_dispatcher: TariffLookup,
) -> None:
    assert defaulting_dispatcher(BATTERY) == "unclassified"


def test_the_most_specific_registration_wins() -> None:
    chosen = tariff_code.dispatch(InstantCoffee)

    assert chosen is tariff_code.registry[InstantCoffee]
    assert chosen is not tariff_code.registry[Coffee]


def test_an_unregistered_subclass_gets_its_base_class_code(
    fresh_dispatcher: _SingleDispatchCallable[str],
) -> None:
    fresh_dispatcher.register(Coffee, tariff_code.registry[Coffee])

    assert fresh_dispatcher.dispatch(InstantCoffee) is tariff_code.registry[Coffee]
    assert fresh_dispatcher(InstantCoffee(roasted=True)) == "0901.21"


def test_dispatch_and_registry_show_the_chosen_implementation() -> None:
    assert set(tariff_code.registry) == {object, Coffee, InstantCoffee, TShirt}
    assert tariff_code.dispatch(bool) is tariff_code.registry[object]


def test_the_registry_is_read_only() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        tariff_code.registry[object] = tariff_code.registry[Coffee]  # type: ignore[index]

    assert not hasattr(tariff_code, "unregister")
