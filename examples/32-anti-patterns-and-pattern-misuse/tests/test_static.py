import os
import re
from pathlib import Path

import mypy.api
import pytest

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


# Reduced model: a locator that hands back object, and a caller that uses it as a tariff.
_LOCATED_USE = """
from decimal import Decimal


class Tariff:
    def price_for(self, zone: str) -> Decimal:
        return Decimal("25.00")


class Locator:
    def __init__(self) -> None:
        self._services: dict[str, object] = {}

    def get(self, name: str) -> object:
        return self._services[name]


def quote_located(locator: Locator) -> Decimal:
    return locator.get("tariff").price_for("EU")
"""

# Reduced model: the located tariff is narrowed with isinstance, and nothing is registered.
_LOCATED_MISSING = """
from decimal import Decimal


class Tariff:
    def price_for(self, zone: str) -> Decimal:
        return Decimal("25.00")


class Locator:
    def __init__(self) -> None:
        self._services: dict[str, object] = {}

    def get(self, name: str) -> object:
        return self._services[name]


def quote_located(locator: Locator) -> Decimal:
    tariff = locator.get("tariff")
    if not isinstance(tariff, Tariff):
        raise TypeError(type(tariff).__name__)
    return tariff.price_for("EU")


quote_located(Locator())
"""

# The src model: a call that leaves out the tariff.
_MISSING_TARIFF = """
from pattern_misuse.rating import Consignment, ConsignmentId, quote

quote(Consignment(ConsignmentId("CN-1"), "EU"))
"""

# Reduced model: a charge kind whose accept calls a visit method the visitor does not declare, and
# a concrete visitor that meets the method once it is declared abstract.
_NEW_VISIT_METHOD = """
from abc import ABC, abstractmethod


class Visitor(ABC):
    @abstractmethod
    def visit_flat_fee(self, charge: FlatFee) -> None: ...


class Charge(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None: ...


class FlatFee(Charge):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_flat_fee(self)


class RemoteArea(Charge):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_remote_area(self)


class NetTotal(Visitor):
    def visit_flat_fee(self, charge: FlatFee) -> None:
        pass


class RemoteAreaVisitor(Visitor):
    @abstractmethod
    def visit_remote_area(self, charge: RemoteArea) -> None: ...


class NetTotalWithRemoteArea(NetTotal, RemoteAreaVisitor):
    pass


NetTotalWithRemoteArea()
"""


def test_mypy_needs_a_type_check_to_use_a_located_service(tmp_path: Path) -> None:
    stdout, status = _run(_LOCATED_USE, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["attr-defined", "no-any-return"]
    assert '"object" has no attribute "price_for"' in stdout


def test_mypy_does_not_see_a_missing_registration(tmp_path: Path) -> None:
    stdout, status = _run(_LOCATED_MISSING, tmp_path)
    assert (status, _codes(stdout)) == (0, [])
    with pytest.raises(KeyError, match="tariff"):
        exec(_LOCATED_MISSING, {})


def test_mypy_reports_a_missing_tariff_argument(tmp_path: Path) -> None:
    stdout, status = _run(_MISSING_TARIFF, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["call-arg"]
    assert 'Missing positional argument "tariff"' in stdout


def test_mypy_reports_a_visitor_missing_a_new_visit_method(tmp_path: Path) -> None:
    stdout, status = _run(_NEW_VISIT_METHOD, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["abstract", "attr-defined"]
    assert 'Cannot instantiate abstract class "NetTotalWithRemoteArea"' in stdout
    assert '"Visitor" has no attribute "visit_remote_area"' in stdout
