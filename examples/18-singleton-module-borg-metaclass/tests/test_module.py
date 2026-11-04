import dataclasses
import importlib
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from singleton.domain import RatingError, TariffTable
from singleton.loads import LOAD_LOG
from singleton.quoting import quote

_SRC = Path(__file__).resolve().parents[1] / "src"

_PRELUDE = f"""
import json, sys, threading
from decimal import Decimal
sys.path.insert(0, {str(_SRC)!r})
"""

_LAZY_CODE = (
    _PRELUDE
    + """
import singleton.quoting
from singleton.loads import LOAD_LOG
before = list(LOAD_LOG)
loaded_before = "singleton.tariff_table" in sys.modules
price = singleton.quoting.quote_standard("EUROPE", Decimal("10"))
sys.stdout.write(json.dumps({
    "before": before,
    "loaded_before": loaded_before,
    "after": list(LOAD_LOG),
    "loaded_after": "singleton.tariff_table" in sys.modules,
    "price": str(price),
}))
"""
)

_RACE_CODE = (
    _PRELUDE
    + """
import singleton.quoting
from singleton.loads import LOAD_LOG

THREADS = 8
start = threading.Barrier(THREADS, timeout=10)
quotes = []

def worker():
    start.wait()
    quotes.append(singleton.quoting.quote_standard("EUROPE", Decimal("10")))

threads = [threading.Thread(target=worker) for _ in range(THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=10)
report = {"loads": list(LOAD_LOG), "quotes": sorted({str(q) for q in quotes})}
report["count"] = len(quotes)
sys.stdout.write(json.dumps(report))
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


def test_every_importer_gets_the_one_tariff_table() -> None:
    first = importlib.import_module("singleton.tariff_table")
    second = importlib.import_module("singleton.tariff_table")
    assert first is second
    assert first.TARIFF is second.TARIFF
    assert LOAD_LOG.count("tariff") == 1


def test_a_lazy_import_loads_the_table_on_first_use() -> None:
    result = _run_isolated(_LAZY_CODE)
    assert result == {
        "before": [],
        "loaded_before": False,
        "after": ["tariff"],
        "loaded_after": True,
        "price": "12.00",
    }


def test_threads_racing_on_a_lazy_import_load_the_table_once() -> None:
    """Eight threads reach the first use together.

    This race is not forced: nothing makes the threads overlap inside the import. The test asserts
    only the outcome, and the claim rests on the import system's own rule that exactly one thread
    performs the import (PEP 810).
    """
    result = _run_isolated(_RACE_CODE)
    assert result == {"loads": ["tariff"], "quotes": ["12.00"], "count": 8}


def test_quote_takes_the_table_it_is_given(small_table: TariffTable) -> None:
    other = TariffTable(frozendict({"EUROPE": Decimal("5.00")}))
    before = list(LOAD_LOG)
    assert quote("EUROPE", Decimal("10"), table=small_table) == Decimal("12.00")
    assert quote("EUROPE", Decimal("10"), table=other) == Decimal("50.00")
    assert before == LOAD_LOG


def test_an_unknown_zone_is_a_rating_error(small_table: TariffTable) -> None:
    with pytest.raises(RatingError, match="no rate for zone 'MARS'") as caught:
        small_table.rate_for("MARS")
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__


def test_the_tariff_table_is_a_frozen_value(small_table: TariffTable) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        small_table.rates = frozendict()  # type: ignore[misc]
