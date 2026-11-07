"""Fixtures: the drafts under review, the static gate and a loader for a draft's code.

The drafts are test data in ``tests/drafts``, written for the book and kept as ``.py.txt`` so that
ruff, mypy and pytest never collect them. They reach tests through the ``draft`` fixture. The static
gate runs ``mypy --strict`` through ``mypy.api`` and ruff through the interpreter's ``-m ruff``.
"""

import importlib.util
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

import mypy.api
import pytest
from review_gate.shape import Finding

if TYPE_CHECKING:
    type LoadModule = Callable[[str], ModuleType]

_MEMBER = Path(__file__).resolve().parents[1]
_DRAFTS = Path(__file__).resolve().parent / "drafts"

DRAFT_NAMES = ("untyped_factory", "typed_hierarchy", "rounded_callable")

_MYPY_LINE = re.compile(r"^<string>:(\d+): error: (.*)  \[([a-z-]+)\]$", re.MULTILINE)
_RUFF_LINE = re.compile(r"^draft\.py:(\d+):\d+: ([A-Z]+\d+) (.*)$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Draft:
    name: str
    text: str


class StaticGate:
    """``mypy --strict`` and ruff with the repository's rule selection, over source text."""

    def __init__(self, scratch: Path) -> None:
        self._config = scratch / "mypy.ini"
        self._config.write_text(f"[mypy]\nmypy_path = {_MEMBER / 'src'}\n")

    def mypy(self, source: str, /) -> list[Finding]:
        stdout, _stderr, _status = mypy.api.run(
            [
                "--strict",
                "--warn-unreachable",
                "--config-file",
                str(self._config),
                "--cache-dir",
                os.devnull,
                "--no-error-summary",
                "-c",
                source,
            ]
        )
        return [Finding(int(n), code, text) for n, text, code in _MYPY_LINE.findall(stdout)]

    def ruff(self, source: str, /) -> list[Finding]:
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-m",
                "ruff",
                "check",
                "--isolated",
                "--no-cache",
                "--target-version",
                "py315",
                "--line-length",
                "100",
                "--select",
                "E,F,W,I,UP,B,SIM,RUF,PT,N",
                "--output-format",
                "concise",
                "--stdin-filename",
                "draft.py",
                "-",
            ],
            input=source,
            capture_output=True,
            text=True,
            check=False,
            cwd=_MEMBER,
        )
        return [Finding(int(n), code, text) for n, code, text in _RUFF_LINE.findall(result.stdout)]

    def __call__(self, source: str, /) -> list[Finding]:
        return self.mypy(source) + self.ruff(source)


@pytest.fixture
def static_gate(tmp_path: Path) -> StaticGate:
    return StaticGate(tmp_path)


@pytest.fixture(scope="session")
def drafts() -> Mapping[str, str]:
    """Every draft's text by name."""
    return {name: (_DRAFTS / f"{name}.py.txt").read_text() for name in DRAFT_NAMES}


@pytest.fixture(params=DRAFT_NAMES)
def draft(request: pytest.FixtureRequest, drafts: Mapping[str, str]) -> Draft:
    """The comparison form: each hand-written draft in turn."""
    name = str(request.param)
    return Draft(name, drafts[name])


@pytest.fixture
def load_module(tmp_path: Path) -> LoadModule:
    """Write source to ``tmp_path`` and import it as a module with ``importlib.util``."""

    def load(source: str, /) -> ModuleType:
        path = tmp_path / "loaded_draft.py"
        path.write_text(source)
        spec = importlib.util.spec_from_file_location("loaded_draft", path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return load
