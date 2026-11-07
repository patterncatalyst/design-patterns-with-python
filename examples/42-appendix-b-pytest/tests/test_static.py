"""What mypy reports about a typed fixture."""

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


# The captured text used as a number, and then as text.
_NUMBER = """
import pytest


def total(capsys: pytest.CaptureFixture[str]) -> None:
    captured = capsys.readouterr().out + 1
"""
_TEXT = _NUMBER.replace("+ 1", '+ "!"')


def test_mypy_checks_a_typed_fixture_use(tmp_path: Path) -> None:
    """Credits ``pytest.CaptureFixture[str]``: annotating ``capsys`` as ``object`` replaces the
    first list with ``attr-defined``, because ``object`` has no ``readouterr``."""
    number, number_status = _run(_NUMBER, tmp_path)
    text, text_status = _run(_TEXT, tmp_path)

    assert [_codes(number), _codes(text)] == [["operator"], []]
    assert (number_status, text_status) == (1, 0)
