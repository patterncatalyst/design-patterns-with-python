"""What mypy checks about the build flag: sysconfig's answer is Any, and build.py wraps it."""

import os
import re
from pathlib import Path

import mypy.api

_MEMBER = Path(__file__).resolve().parents[1]
_SRC = _MEMBER / "src"


def _run(args: list[str], tmp_path: Path) -> tuple[str, int]:
    """Type-check strictly, finding the package through the member's src directory."""
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
            *args,
        ]
    )
    return stdout, status


def _codes(stdout: str) -> list[str]:
    return sorted(set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)))


# The flag compared with 1 and returned as it stands: sysconfig.get_config_var is typed Any.
_UNWRAPPED = """
import sysconfig


def gil_disabled_build() -> bool:
    return sysconfig.get_config_var("Py_GIL_DISABLED") == 1
"""


def test_mypy_types_the_build_flag_as_any(tmp_path: Path) -> None:
    """The unwrapped form is reported; the module that wraps the answer in bool() is not."""
    unwrapped, unwrapped_status = _run(["-c", _UNWRAPPED], tmp_path)
    wrapped, wrapped_status = _run([str(_SRC / "gil_and_performance" / "build.py")], tmp_path)

    assert [_codes(unwrapped), _codes(wrapped)] == [["no-any-return"], []]
    assert (unwrapped_status, wrapped_status) == (1, 0)
    assert "Returning Any from function declared to return" in unwrapped
