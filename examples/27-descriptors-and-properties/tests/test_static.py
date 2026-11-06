import os
import re
from decimal import Decimal
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


# The src model: every assignment below breaks the type of a Positive field.
_SET_TYPE = """
from decimal import Decimal

from descriptors_properties.cargo import Container, Dimensions

dimensions = Dimensions(120, Decimal(80), Decimal(100))
container = Container("C-1", Decimal(2200), Decimal(28000))
container.tare_kg = 5
dimensions.length_cm = Decimal(1)
reveal_type(dimensions.length_cm)
"""

# The src model: a descriptor field called with no arguments at all.
_NO_ARGUMENTS = """
from descriptors_properties.cargo import Dimensions

Dimensions()
"""

# Reduced model: cached_property on a slotted dataclass. Run too, because the type check is silent.
_SLOTTED_CACHED_PROPERTY = """
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property


@dataclass(frozen=True, slots=True)
class Lot:
    kilograms: Decimal

    @cached_property
    def doubled(self) -> Decimal:
        return self.kilograms * 2


Lot(Decimal(1)).doubled
"""

# Reduced model: the src descriptor on a slotted dataclass. Run too: the type check is silent.
_SLOTTED_DESCRIPTOR = """
from dataclasses import dataclass
from decimal import Decimal

from descriptors_properties.fields import Positive


@dataclass(frozen=True, slots=True)
class Slotted:
    length_cm: Positive = Positive()


slotted = Slotted(Decimal(-1))
accepted = slotted.length_cm
storage = type(vars(Slotted)["length_cm"]).__name__
"""


def test_mypy_types_a_positive_field_by_its_set_value(tmp_path: Path) -> None:
    stdout, status = _run(_SET_TYPE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type", "assignment", "misc"}
    assert stdout.count("error:") == 3
    assert 'Revealed type is "decimal.Decimal"' in stdout


def test_mypy_reads_a_descriptor_field_as_a_default(tmp_path: Path) -> None:
    stdout, status = _run(_NO_ARGUMENTS, tmp_path)

    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    with pytest.raises(TypeError, match="missing 3 required positional arguments"):
        exec(_NO_ARGUMENTS, {})


def test_mypy_accepts_cached_property_on_a_slotted_dataclass(tmp_path: Path) -> None:
    stdout, status = _run(_SLOTTED_CACHED_PROPERTY, tmp_path)

    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    namespace: dict[str, object] = {}
    with pytest.raises(TypeError, match="No '__dict__' attribute"):
        exec(_SLOTTED_CACHED_PROPERTY, namespace)


def test_mypy_accepts_a_descriptor_field_on_a_slotted_dataclass(tmp_path: Path) -> None:
    stdout, status = _run(_SLOTTED_DESCRIPTOR, tmp_path)

    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    namespace: dict[str, object] = {}
    exec(_SLOTTED_DESCRIPTOR, namespace)
    assert namespace["accepted"] == Decimal(-1)
    assert namespace["storage"] == "member_descriptor"
