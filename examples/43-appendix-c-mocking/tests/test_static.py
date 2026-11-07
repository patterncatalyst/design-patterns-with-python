"""What mypy reports about mocks: their types, and what a stub is accepted for."""

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


def _revealed(stdout: str) -> list[str]:
    return re.findall(r'Revealed type is "(.*)"$', stdout, re.MULTILINE)


def _codes(stdout: str) -> list[str]:
    return sorted(set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)))


_MOCK_UNION = (
    "unittest.mock.MagicMock | unittest.mock.AsyncMock | unittest.mock.NonCallableMagicMock"
)

_SNIPPET = """
from pytest_mock import MockerFixture


class Gateway:
    def book(self) -> str:
        return "x"


def check(mocker: MockerFixture) -> None:
    reveal_type({call})
"""


@pytest.mark.parametrize(
    ("call", "revealed"),
    [
        pytest.param('mocker.patch("os.getcwd")', _MOCK_UNION, id="patch"),
        pytest.param('mocker.patch.object(Gateway, "book")', _MOCK_UNION, id="patch.object"),
        pytest.param('mocker.spy(Gateway(), "book")', "pytest_mock.plugin.SpyType", id="spy"),
        pytest.param("mocker.stub()", "unittest.mock.MagicMock", id="stub"),
        pytest.param("mocker.Mock()", "Any", id="Mock"),
    ],
)
def test_mypy_types_mocker_objects_as_mocks(call: str, revealed: str, tmp_path: Path) -> None:
    """Credits pytest-mock's annotations: ``patch`` and ``patch.object`` are a union of mock
    classes, ``spy`` is ``SpyType``, ``stub`` is ``MagicMock`` and ``Mock`` is ``Any``."""
    stdout, status = _run(_SNIPPET.format(call=call), tmp_path)

    assert _revealed(stdout) == [revealed]
    assert status == 0


_CALLBACK = """
from decimal import Decimal

from mocking_reference.booking import book_cheapest
from mocking_reference.carriers import ConsignmentId, FastlineGateway
from pytest_mock import MockerFixture


{callback}


def check(mocker: MockerFixture) -> None:
    book_cheapest(
        {{"f": FastlineGateway()}}, ConsignmentId("CN-1"), Decimal("1"), notify={argument}
    )
"""
_STUB = _CALLBACK.format(callback="", argument="mocker.stub()")
_WRONG = _CALLBACK.format(callback="def notify(reference: int) -> None: ...", argument="notify")


def test_mypy_accepts_a_stub_where_a_callback_is_expected(tmp_path: Path) -> None:
    """Credits the ``Notify`` annotation: the stub is accepted because mock classes are
    assignable to anything, and a callback taking an ``int`` is refused as an ``arg-type``."""
    stub, stub_status = _run(_STUB, tmp_path)
    wrong, wrong_status = _run(_WRONG, tmp_path)

    assert [_codes(stub), _codes(wrong)] == [[], ["arg-type"]]
    assert (stub_status, wrong_status) == (0, 1)
    assert "Callable[[str], None]" in wrong
