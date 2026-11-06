import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from singledispatch_visitor.commodities import Coffee, InstantCoffee, TShirt

if TYPE_CHECKING:
    from functools import _SingleDispatchCallable

_SRC = Path(__file__).resolve().parents[1] / "src"

_PRELUDE = f"""
import json, sys
from decimal import Decimal
sys.path.insert(0, {str(_SRC)!r})
"""

_EXTENSION_CODE = (
    _PRELUDE
    + """
from singledispatch_visitor.commodities import LithiumIonBattery
from singledispatch_visitor.tariff import TariffCodeError, tariff_code

battery = LithiumIonBattery(Decimal(100))
try:
    tariff_code(battery)
    before = "no error"
except TariffCodeError as error:
    before = str(error)
before_keys = sorted(kind.__name__ for kind in tariff_code.registry)

import singledispatch_visitor.dangerous_goods

sys.stdout.write(json.dumps({
    "before": before,
    "before_keys": before_keys,
    "after": tariff_code(battery),
    "after_keys": sorted(kind.__name__ for kind in tariff_code.registry),
}))
"""
)


def _run_isolated(code: str) -> dict[str, object]:
    """Run code in a fresh interpreter, so import order and test order cannot matter."""
    done = subprocess.run(
        [sys.executable, "-I", "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    result: dict[str, object] = json.loads(done.stdout)
    return result


def _beverage_or_garment(commodity: Coffee | TShirt) -> str:
    return "beverage or garment"


def _cotton_shirt(commodity: TShirt) -> str:
    return "cotton shirt"


def _generic_alias(commodity: list[int]) -> str:
    return "never registered"


def test_a_union_annotation_registers_each_member(
    fresh_dispatcher: _SingleDispatchCallable[str],
) -> None:
    fresh_dispatcher.register(_beverage_or_garment)

    assert {Coffee, TShirt} <= set(fresh_dispatcher.registry)
    assert fresh_dispatcher(Coffee(roasted=True)) == "beverage or garment"
    assert fresh_dispatcher(TShirt(cotton=False)) == "beverage or garment"
    assert fresh_dispatcher(InstantCoffee(roasted=True)) == "beverage or garment"


def test_register_with_a_class_and_a_function_registers_the_function(
    fresh_dispatcher: _SingleDispatchCallable[str],
) -> None:
    returned: object = fresh_dispatcher.register(TShirt, _cotton_shirt)

    assert returned is _cotton_shirt
    assert fresh_dispatcher.dispatch(TShirt) is _cotton_shirt
    assert fresh_dispatcher(TShirt(cotton=True)) == "cotton shirt"


def test_a_generic_alias_is_refused_at_registration(
    fresh_dispatcher: _SingleDispatchCallable[str],
) -> None:
    with pytest.raises(TypeError, match="is not a class"):
        fresh_dispatcher.register(_generic_alias)

    assert set(fresh_dispatcher.registry) == {object}


def test_another_module_extends_the_set_when_it_is_imported() -> None:
    report = _run_isolated(_EXTENSION_CODE)

    assert report["before"] == "no tariff code for LithiumIonBattery"
    assert report["before_keys"] == ["Coffee", "InstantCoffee", "TShirt", "object"]
    assert report["after"] == "8507.60"
    assert report["after_keys"] == [
        "Coffee",
        "InstantCoffee",
        "LithiumIonBattery",
        "TShirt",
        "object",
    ]
