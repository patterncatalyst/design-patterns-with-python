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
    return set(re.findall(r"\[([a-z-]+)\]", stdout))


_FROZEN_ASSIGNMENT = """
from value_semantics.values import Weight


def reweigh(w: Weight) -> None:
    w.kilograms = 2.0
"""

_KW_ONLY_POSITIONAL = """
from value_semantics.booking import Consignment
from value_semantics.values import ConsignmentId, Weight

c = Consignment(ConsignmentId("CN-00000001"), Weight(1.0), "SGSIN")
"""

_REPLACE_UNKNOWN_FIELD = """
from dataclasses import replace

from value_semantics.values import Weight

heavier = replace(Weight(1.0), kilos=2.0)
"""

_MONEY_HAS_NO_ORDER = """
from value_semantics.values import Money

cheaper = Money.of("3", "EUR") < Money.of("5", "EUR")
"""

_MUTABLE_DICT_KEY = """
from dataclasses import dataclass


@dataclass
class MutableSlotId:
    bay: int
    row: int
    tier: int


held: dict[MutableSlotId, str] = {MutableSlotId(1, 0, 1): "CN-00000001"}
"""

_MUTABLE_DEFAULT = """
from dataclasses import dataclass

from value_semantics.values import ConsignmentId, SlotId


@dataclass(eq=False, slots=True)
class SharedDefault:
    reservations: dict[SlotId, ConsignmentId] = {}
"""

_SLOTS_WEAKREF = """
import weakref

from value_semantics.values import Weight

ref = weakref.ref(Weight(1.0))
"""


@pytest.mark.parametrize(
    ("snippet", "codes", "message"),
    [
        (_FROZEN_ASSIGNMENT, {"misc"}, 'Property "kilograms" defined in "Weight" is read-only'),
        (_KW_ONLY_POSITIONAL, {"call-arg"}, 'Too many positional arguments for "Consignment"'),
        (
            _REPLACE_UNKNOWN_FIELD,
            {"call-arg"},
            'Unexpected keyword argument "kilos" for "replace" of "Weight"',
        ),
        (_MONEY_HAS_NO_ORDER, {"operator"}, 'Unsupported left operand type for < ("Money")'),
    ],
    ids=["frozen-assignment", "kw-only-positional", "replace-unknown-field", "money-has-no-order"],
)
def test_mypy_checks_the_generated_methods(
    snippet: str, codes: set[str], message: str, tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == 1
    assert _codes(stdout) == codes
    assert message in stdout


@pytest.mark.parametrize(
    "snippet",
    [_MUTABLE_DICT_KEY, _MUTABLE_DEFAULT, _SLOTS_WEAKREF],
    ids=["mutable-dict-key", "mutable-default", "slots-weakref"],
)
def test_mypy_cannot_see_value_semantics_mistakes(snippet: str, tmp_path: Path) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()


_CORRECT_USE = """
from dataclasses import replace

from value_semantics.booking import Consignment
from value_semantics.values import ConsignmentId, Money, Weight

c = Consignment(id=ConsignmentId("CN-00000001"), weight=Weight(1.0), destination="SGSIN")
heavier = replace(c, weight=Weight(2.0))
total = Money.of("3", "EUR") + Money.of("5", "EUR")
"""


def test_mypy_accepts_the_correct_use_of_the_same_values(tmp_path: Path) -> None:
    stdout, status = _run(_CORRECT_USE, tmp_path)
    assert status == 0
    assert _codes(stdout) == set()
