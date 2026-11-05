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


_WEIGHT_ON_EITHER_KIND = """
from composite_flyweight.domain import Shipment, Weight


def weight_of(shipment: Shipment) -> Weight:
    return shipment.weight
"""

_PARTS_ON_THE_UNION = """
from composite_flyweight.domain import Shipment


def count(shipment: Shipment) -> int:
    return len(shipment.parts)
"""

_MISSING_ARM = """
from typing import assert_never

from composite_flyweight.domain import Consignment, Shipment


def leaves(shipment: Shipment) -> int:
    match shipment:
        case Consignment():
            return 1
        case _ as unreachable:
            assert_never(unreachable)
"""

_PART_THAT_IS_NOT_A_SHIPMENT = """
from decimal import Decimal

from composite_flyweight.domain import ConsolidatedShipment, Weight

group = ConsolidatedShipment("CS-1", (Weight(Decimal(1)),))
"""

_FROZEN_HEAD = """
from composite_flyweight.domain import ConsolidatedShipment, Consignment


def change(group: ConsolidatedShipment, consignment: Consignment) -> None:
"""

_FROZEN_BODIES = {
    "add": "    group.add(consignment)\n",
    "append": "    group.parts.append(consignment)\n",
    "assign": "    group.parts = ()\n",
}

# A reduced model of the GoF form: the base class gives every component an `add`.
_COMPONENT_LEAF_ADD = """
from abc import ABC, abstractmethod
from decimal import Decimal


class Component(ABC):
    @abstractmethod
    def weight(self) -> Decimal: ...

    def add(self, component: Component, /) -> None:
        raise TypeError("cannot add to a leaf")


class Leaf(Component):
    def weight(self) -> Decimal:
        return Decimal(1)


Leaf().add(Leaf())
"""


def test_mypy_reads_weight_on_either_kind_of_shipment(tmp_path: Path) -> None:
    stdout, status = _run(_WEIGHT_ON_EITHER_KIND, tmp_path)

    assert status == 0
    assert stdout == ""


def test_mypy_refuses_parts_on_a_shipment_that_may_be_a_consignment(tmp_path: Path) -> None:
    stdout, status = _run(_PARTS_ON_THE_UNION, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"union-attr"}
    assert 'has no attribute "parts"' in stdout


def test_mypy_reports_a_missing_match_arm(tmp_path: Path) -> None:
    stdout, status = _run(_MISSING_ARM, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'expected "Never"' in stdout


def test_mypy_refuses_a_part_that_is_not_a_shipment(tmp_path: Path) -> None:
    stdout, status = _run(_PART_THAT_IS_NOT_A_SHIPMENT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert "incompatible type" in stdout


@pytest.mark.parametrize(
    ("name", "code", "needle"),
    [
        ("add", "attr-defined", '"ConsolidatedShipment" has no attribute "add"'),
        ("append", "attr-defined", 'has no attribute "append"'),
        ("assign", "misc", "is read-only"),
    ],
    ids=["add", "append", "assign"],
)
def test_mypy_refuses_adding_to_a_frozen_consolidation(
    name: str, code: str, needle: str, tmp_path: Path
) -> None:
    stdout, status = _run(_FROZEN_HEAD + _FROZEN_BODIES[name], tmp_path)

    assert status == 1
    assert _codes(stdout) == {code}
    assert needle in stdout


def test_mypy_accepts_add_on_a_component_leaf(tmp_path: Path) -> None:
    stdout, status = _run(_COMPONENT_LEAF_ADD, tmp_path)

    assert status == 0
    assert stdout == ""
