from decimal import Decimal
from typing import TYPE_CHECKING

from singleton.tariff_table import STANDARD_RATES

if TYPE_CHECKING:
    from conftest import RatesForm, _MetaTariffTable, _NewTariffTable, _TariffBorg


def test_every_form_gives_each_caller_the_same_rates(rates_form: RatesForm) -> None:
    first = rates_form.read()
    second = rates_form.read()
    assert first == second == STANDARD_RATES
    assert rates_form.loads() == rates_form.expected_loads


def test_borg_instances_share_state_but_are_distinct_and_unequal(
    borg: type[_TariffBorg],
) -> None:
    a = borg()
    b = borg()
    assert a is not b
    assert a != b
    assert a.__dict__ is b.__dict__
    a.rates = frozendict({"EUROPE": Decimal("9")})
    assert b.rates == frozendict({"EUROPE": Decimal("9")})
    assert borg.loads == ["borg"]


def test_a_singleton_metaclass_ignores_the_second_calls_arguments(
    meta_table: type[_MetaTariffTable],
) -> None:
    first = meta_table("standard.csv")
    second = meta_table("express.csv")
    assert first is second
    assert second.source == "standard.csv"
    assert second.rates == STANDARD_RATES
    assert meta_table.loads == ["standard.csv"]


def test_a_new_based_singleton_reruns_init_on_every_call(
    new_table: type[_NewTariffTable],
) -> None:
    first = new_table("standard.csv")
    second = new_table("express.csv")
    assert first is second
    assert first.source == "express.csv"
    assert first.rates["EUROPE"] == Decimal("2.00")
    assert new_table.loads == ["standard.csv", "express.csv"]
