import os
import re
from pathlib import Path
from typing import assert_type

import mypy.api
import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"


def _run(snippet: str, tmp_path: Path, *flags: str) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
            *flags,
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


_MOCK_PREAMBLE = """
from unittest.mock import MagicMock, Mock, create_autospec

from testing_baseline.carriers import CarrierGateway


def use(gateway: CarrierGateway) -> None: ...

"""


@pytest.mark.parametrize(
    "call",
    [
        pytest.param("use(Mock())", id="Mock"),
        pytest.param("use(Mock(spec=CarrierGateway))", id="Mock-spec"),
        pytest.param("use(MagicMock(spec=CarrierGateway))", id="MagicMock-spec"),
        pytest.param("use(create_autospec(CarrierGateway, instance=True))", id="autospec"),
    ],
)
def test_mypy_accepts_every_mock_where_a_gateway_is_expected(call: str, tmp_path: Path) -> None:
    stdout, status = _run(_MOCK_PREAMBLE + call + "\n", tmp_path)
    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


_FAKE_PREAMBLE = """
from datetime import datetime, timedelta

from testing_baseline.carriers import CarrierGateway, CarrierQuote
from testing_baseline.domain import Consignment
from testing_baseline.engine import RateEngine


def _clock() -> datetime:
    raise NotImplementedError


class QuoteOnly:
    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        raise NotImplementedError

"""

_DICT_ENTRY = (
    _FAKE_PREAMBLE
    + """
engine = RateEngine(
    {"fastline": QuoteOnly()}, clock=_clock, validity=timedelta(minutes=30)
)
"""
)

_ASSIGNMENT = _FAKE_PREAMBLE + "gateway: CarrierGateway = QuoteOnly()\n"


@pytest.mark.parametrize(
    ("snippet", "codes", "needles", "note"),
    [
        pytest.param(
            _DICT_ENTRY,
            {"dict-item"},
            [
                'Dict entry 0 has incompatible type "str": "QuoteOnly"; '
                'expected "str": "CarrierGateway"'
            ],
            False,
            id="dict-entry",
        ),
        pytest.param(
            _ASSIGNMENT,
            {"assignment"},
            [
                'expression has type "QuoteOnly", variable has type "CarrierGateway"',
                'note: "QuoteOnly" is missing following "CarrierGateway" protocol member:',
                "note:     book",
            ],
            True,
            id="assignment",
        ),
    ],
)
def test_mypy_checks_a_hand_written_fake(
    snippet: str, codes: set[str], needles: list[str], note: bool, tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == 1
    assert _codes(stdout) == codes
    for needle in needles:
        assert needle in stdout
    assert ("protocol member" in stdout) is note


_ASSERT_TYPE = """
from typing import assert_type

assert_type(1, str)
"""


def test_assert_type_is_static_only(tmp_path: Path) -> None:
    stdout, status = _run(_ASSERT_TYPE, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"assert-type"}
    assert 'Expression is of type "Literal[1]", not "str"' in stdout
    assert assert_type(1, str) == 1  # type: ignore[assert-type]
