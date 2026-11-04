import os
import re
from pathlib import Path

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


_NONE_EXIT = """
from pathlib import Path

from context_managers.manifest import ManifestWriter


def write(path: Path) -> int:
    with ManifestWriter(path) as out:
        raise ValueError(out.name)
    return 1
"""

_BOOL_EXIT = """
from pathlib import Path
from types import TracebackType
from typing import TextIO


class Swallowing:
    def __enter__(self) -> TextIO:
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return True


def write(path: Path) -> int:
    with Swallowing() as out:
        raise ValueError(out.name)
    return 1
"""


@pytest.mark.parametrize(
    ("snippet", "status", "codes"),
    [
        pytest.param(_NONE_EXIT, 1, {"unreachable"}, id="none-exit"),
        pytest.param(_BOOL_EXIT, 0, set[str](), id="bool-exit"),
    ],
)
def test_mypy_reads_exit_return_type_for_reachability(
    snippet: str, status: int, codes: set[str], tmp_path: Path
) -> None:
    stdout, actual = _run(snippet, tmp_path, "--warn-unreachable")
    assert actual == status
    assert _codes(stdout) == codes
    if codes:
        assert "Statement is unreachable" in stdout
    else:
        assert stdout == ""


_CLASS_TARGET = """
from pathlib import Path
from typing import TextIO, assert_type

from context_managers.manifest import ManifestWriter


def write(path: Path) -> None:
    with ManifestWriter(path) as out:
        assert_type(out, TextIO)
"""

_GENERATOR_TARGET = """
from pathlib import Path
from typing import TextIO, assert_type

from context_managers.manifest import manifest_file


def write(path: Path) -> None:
    with manifest_file(path) as out:
        assert_type(out, TextIO)
"""

_STACK_TARGET = """
from contextlib import ExitStack
from pathlib import Path
from typing import TextIO, assert_type

from context_managers.manifest import ManifestWriter


def write(path: Path) -> None:
    with ExitStack() as stack:
        out = stack.enter_context(ManifestWriter(path))
        assert_type(out, TextIO)
"""


@pytest.mark.parametrize(
    "snippet",
    [
        pytest.param(_CLASS_TARGET, id="class"),
        pytest.param(_GENERATOR_TARGET, id="generator"),
        pytest.param(_STACK_TARGET, id="exit-stack"),
    ],
)
def test_mypy_types_the_with_target(snippet: str, tmp_path: Path) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


_MISSING_TRY = """
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO


@contextmanager
def leaky(path: Path) -> Iterator[TextIO]:
    handle = path.open("w", encoding="utf-8")
    yield handle
    handle.close()
"""


def test_mypy_cannot_see_a_missing_try(tmp_path: Path) -> None:
    stdout, status = _run(_MISSING_TRY, tmp_path)
    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""
