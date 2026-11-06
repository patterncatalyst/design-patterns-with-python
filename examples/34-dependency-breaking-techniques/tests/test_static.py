import os
import re
from pathlib import Path

import mypy.api

_SRC = Path(__file__).resolve().parents[1] / "src"


def _run(snippet: str, tmp_path: Path) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
            "--warn-unreachable",
            "--config-file",
            str(config),
            "--cache-dir",
            os.devnull,
            "--no-error-summary",
            "-c",
            snippet,
        ]
    )
    return stdout, status


def _codes(stdout: str) -> list[str]:
    return sorted(set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)))


# A fake that takes its parameters positionally where the SDK's shape is keyword-only.
_WRONG_AIRCO = """
from dependency_breaking import parameterised


def wrong(zone: str, grams: int) -> int:
    return 1


parameterised.RateEngine(airco_price=wrong)
"""

_MISSING_QUOTERS = """
from decimal import Decimal

from dependency_breaking.domain import Consignment, ConsignmentId
from dependency_breaking.rating import quote

quote(Consignment(ConsignmentId("CN-1"), "EU", Decimal("12.5")))
"""

# Reduced model: a base class with a method to override, and a subclass whose override is
# misspelt. The second snippet is the same code without the decorator.
_MISSPELT_OVERRIDE = """
from decimal import Decimal
from typing import override


class Engine:
    def _fastline_quote(self, zone: str, weight_kg: Decimal) -> Decimal:
        raise TimeoutError(zone)


class Fake(Engine):
    @override
    def _fastline_qoute(self, zone: str, weight_kg: Decimal) -> Decimal:
        return Decimal("25.00")
"""
_MISSPELT_PLAIN = _MISSPELT_OVERRIDE.replace("    @override\n", "")


def test_mypy_checks_a_fake_passed_as_a_constructor_argument(tmp_path: Path) -> None:
    stdout, status = _run(_WRONG_AIRCO, tmp_path)

    assert status == 1
    assert _codes(stdout) == ["arg-type"]
    assert "AircoPrice" in stdout


def test_mypy_reports_a_missing_quoters_argument(tmp_path: Path) -> None:
    stdout, status = _run(_MISSING_QUOTERS, tmp_path)

    assert status == 1
    assert _codes(stdout) == ["call-arg"]
    assert 'Missing named argument "quoters"' in stdout


def test_mypy_reports_a_misspelt_override_only_with_the_override_decorator(
    tmp_path: Path,
) -> None:
    decorated, decorated_status = _run(_MISSPELT_OVERRIDE, tmp_path)
    plain, plain_status = _run(_MISSPELT_PLAIN, tmp_path)

    assert [_codes(decorated), _codes(plain)] == [["misc"], []]
    assert (decorated_status, plain_status) == (1, 0)
    assert "no base method was found with this name" in decorated
