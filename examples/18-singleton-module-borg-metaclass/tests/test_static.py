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


# Reduced model: a self-contained metaclass singleton with the shape of the fixture in conftest.py,
# without its bookkeeping.
_META = """
from typing import Any


class SingletonMeta(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]


class TariffTable(metaclass=SingletonMeta):
    def __init__(self, source: str) -> None:
        self.source = source
"""

_META_CASES = {
    "second-call": (
        _META
        + """
first = TariffTable("a.csv")
second = TariffTable("b.csv")
source: str = second.source
""",
        set(),
        "",
    ),
    "missing-argument": (
        _META + "\nbroken = TariffTable()\n",
        {"call-arg"},
        'Missing positional argument "source" in call to "TariffTable"',
    ),
}


@pytest.mark.parametrize("case", list(_META_CASES), ids=list(_META_CASES))
def test_mypy_types_a_metaclass_singleton_call_by_init(case: str, tmp_path: Path) -> None:
    snippet, codes, fragment = _META_CASES[case]
    stdout, status = _run(snippet, tmp_path)
    assert _codes(stdout) == codes
    assert fragment in stdout
    assert status == (1 if codes else 0), stdout


# Reduced model: the Borg of conftest.py, with and without `__slots__`.
_BORG = """
from typing import ClassVar


class Borg:
    {slots}
    _shared_state: ClassVar[dict[str, object]] = {{}}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state
"""

_BORG_CASES = {
    "plain": ("", set(), ""),
    "slotted": ('__slots__ = ("rates",)', {"misc"}, 'that is not in "__slots__"'),
}


@pytest.mark.parametrize("case", list(_BORG_CASES), ids=list(_BORG_CASES))
def test_mypy_accepts_borg_state_unless_the_class_has_slots(case: str, tmp_path: Path) -> None:
    slots, codes, fragment = _BORG_CASES[case]
    stdout, status = _run(_BORG.format(slots=slots), tmp_path)
    assert _codes(stdout) == codes
    assert fragment in stdout
    assert status == (1 if codes else 0), stdout


_LAZY = """
lazy from singleton import tariff_table


def zone_count() -> int:
    return tariff_table.TARIF
"""


def test_mypy_still_checks_attributes_through_a_lazy_import(tmp_path: Path) -> None:
    stdout, status = _run(_LAZY, tmp_path)
    assert _codes(stdout) == {"attr-defined", "no-any-return"}
    assert 'Module has no attribute "TARIF"; maybe "TARIFF"?' in stdout
    assert status == 1
