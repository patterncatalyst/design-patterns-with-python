import json
import subprocess
import sys
from collections.abc import Callable
from decimal import Decimal

import pytest
from seams import airco, legacy
from seams.domain import Consignment

type FastlineFake = Callable[[str, Decimal], Decimal]
type AircoFake = Callable[..., int]

# The reload runs in a fresh interpreter, so no test in this process sees a replaced class.
_RELOAD_SCRIPT = """
import importlib
import json
import sys
from decimal import Decimal

import pytest
from seams import fastline, legacy

original = fastline.request_quote
old_engine = legacy.RateEngine()


def fake(zone: str, weight_kg: Decimal) -> Decimal:
    return Decimal("25.00")


with pytest.MonkeyPatch.context() as patch:
    patch.setattr(fastline, "request_quote", fake)
    importlib.reload(fastline)
    reloaded = fastline.request_quote
    overwritten = reloaded is not fake
restored = fastline.request_quote is original and fastline.request_quote is not reloaded

importlib.reload(fastline)
rebound = legacy.request_quote is fastline.request_quote

importlib.reload(legacy)
same_class = isinstance(old_engine, legacy.RateEngine)

sys.stdout.write(json.dumps([
    f"patch overwritten: {overwritten}",
    f"teardown restored pre-reload object: {restored}",
    f"from-import rebound: {rebound}",
    f"old instance is new class: {same_class}",
]))
"""


class _FakeAirco:
    def price(self, *, destination: str, grams: int) -> int:
        return 2000


class _WrongAirco:
    def quote(self, *, destination: str, grams: int) -> int:
        return 2000


def test_patching_a_module_constant_misses_a_default_captured_at_definition(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
) -> None:
    monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)
    monkeypatch.setattr(airco, "price", airco_fake)
    monkeypatch.setattr("seams.legacy.MARGIN", Decimal("2"))

    patched = legacy.RateEngine().quote(consignment)
    passed = legacy.RateEngine(margin=Decimal("2")).quote(consignment)

    assert str(patched.total.amount) == "27.50"
    assert str(passed.total.amount) == "50.00"


def test_reload_discards_a_patch_and_keeps_old_bindings() -> None:
    done = subprocess.run(
        [sys.executable, "-I", "-c", _RELOAD_SCRIPT],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout) == [
        "patch overwritten: True",
        "teardown restored pre-reload object: True",
        "from-import rebound: False",
        "old instance is new class: False",
    ]


def test_an_object_with_the_right_method_can_stand_in_for_a_module(
    monkeypatch: pytest.MonkeyPatch, consignment: Consignment, fastline_fake: FastlineFake
) -> None:
    monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)

    monkeypatch.setattr(legacy, "airco", _FakeAirco())
    quote = legacy.RateEngine().quote(consignment)
    assert (quote.carrier, str(quote.total.amount)) == ("AIRCO", "22.00")

    monkeypatch.setattr(legacy, "airco", _WrongAirco())
    engine = legacy.RateEngine()
    with pytest.raises(AttributeError, match="'_WrongAirco' object has no attribute 'price'"):
        engine.quote(consignment)
