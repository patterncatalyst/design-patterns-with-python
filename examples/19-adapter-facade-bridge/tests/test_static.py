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


def _codes(stdout: str) -> set[str]:
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


_MATCHING_SHAPE = """
from adapter_facade_bridge.gateways import CarrierGateway
from adapter_facade_bridge.sdks import AircoClient

gateway: CarrierGateway = AircoClient()
"""

_DIFFERENT_SHAPE = """
from adapter_facade_bridge.gateways import CarrierGateway
from adapter_facade_bridge.sdks import FastlineClient

gateway: CarrierGateway = FastlineClient()
"""

# A reduced model: the units sit in a float, so the two parameter names are the only difference.
_UNITS_IN_A_FLOAT = """
from typing import Protocol


class Gateway(Protocol):
    def book(self, consignment_id: str, kilograms: float, /) -> str: ...


class PoundsClient:
    def book(self, consignment_id: str, pounds: float, /) -> str:
        return consignment_id


gateway: Gateway = PoundsClient()
"""

_FLOAT_WHERE_A_WEIGHT_BELONGS = """
from adapter_facade_bridge.domain import Money
from adapter_facade_bridge.gateways import CarrierGateway


class PoundsClient:
    def book(self, consignment_id: str, pounds: float, /) -> str:
        return consignment_id

    def insure(self, reference: str, value: Money, /) -> None: ...


gateway: CarrierGateway = PoundsClient()
"""

_MISSING_A_PRIMITIVE = """
from adapter_facade_bridge.domain import ConsignmentId, Weight
from adapter_facade_bridge.gateways import CarrierGateway


class BookOnly:
    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str:
        return consignment_id


gateway: CarrierGateway = BookOnly()
"""


def test_mypy_accepts_a_client_whose_shape_matches_the_protocol(tmp_path: Path) -> None:
    stdout, status = _run(_MATCHING_SHAPE, tmp_path)

    assert status == 0
    assert stdout == ""


def test_mypy_rejects_a_client_with_a_different_shape(tmp_path: Path) -> None:
    stdout, status = _run(_DIFFERENT_SHAPE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert '"FastlineClient"' in stdout


def test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float(tmp_path: Path) -> None:
    stdout, status = _run(_UNITS_IN_A_FLOAT, tmp_path)

    assert status == 0
    assert stdout == ""


def test_mypy_rejects_a_float_where_a_weight_belongs(tmp_path: Path) -> None:
    stdout, status = _run(_FLOAT_WHERE_A_WEIGHT_BELONGS, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert "Weight" in stdout


def test_mypy_reports_an_implementor_missing_a_primitive(tmp_path: Path) -> None:
    stdout, status = _run(_MISSING_A_PRIMITIVE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert "protocol member" in stdout
    assert "note:     insure" in stdout
