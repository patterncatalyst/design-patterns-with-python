import os
import re
from pathlib import Path

import mypy.api
import pytest
from dynamic_attributes.tracking import ConsignmentId, TrackingHistory

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


def _errors(stdout: str) -> list[str]:
    return [line for line in stdout.splitlines() if " error: " in line]


_UNKNOWN_ATTRIBUTE = """
from dynamic_attributes.tracking import TrackingHistory


def probe(h: TrackingHistory) -> None:
    reveal_type(h.stauts)
    h.stauts.upper()
"""

_DECLARED_FIELD = """
from dynamic_attributes.tracking import TrackingHistory


def probe(h: TrackingHistory) -> None:
    n: int = h.status
"""

_ASSIGNMENTS = """
from dynamic_attributes.tracking import TrackingHistory


def assign_loaded(h: TrackingHistory) -> None:
    h.status = None


def assign_new(h: TrackingHistory) -> None:
    h.anything = 1
"""

# Reduced model: the cached_property form, which has no __getattr__.
_CACHED_PROPERTY_TYPO = """
from functools import cached_property


class History:
    @cached_property
    def status(self) -> str:
        return "in transit"


def probe(h: History) -> object:
    return h.stauts
"""

_MODULE_IMPORT = """
from dynamic_attributes.tracking import Anything

reveal_type(Anything)
"""


def test_mypy_types_an_unknown_attribute_by_the_getattr_return_type(tmp_path: Path) -> None:
    stdout, status = _run(_UNKNOWN_ATTRIBUTE, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"attr-defined"}
    assert len(_errors(stdout)) == 1
    assert 'Revealed type is "object"' in stdout
    assert '"object" has no attribute "upper"' in stdout


def test_mypy_keeps_the_declared_field_types(tmp_path: Path) -> None:
    stdout, status = _run(_DECLARED_FIELD, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert 'expression has type "ConsignmentStatus | None"' in stdout


def test_mypy_accepts_an_assignment_that_setattr_refuses(tmp_path: Path) -> None:
    stdout, status = _run(_ASSIGNMENTS, tmp_path)
    assert (status, _codes(stdout)) == (0, set())

    namespace: dict[str, object] = {}
    exec(_ASSIGNMENTS, namespace)
    assign_loaded = namespace["assign_loaded"]
    assign_new = namespace["assign_new"]
    assert callable(assign_loaded)
    assert callable(assign_new)
    history = TrackingHistory(ConsignmentId("CN-4"), lambda _id: [])
    assign_new(history)
    assert vars(history)["anything"] == 1
    with pytest.raises(AttributeError, match="is loaded, not assigned"):
        assign_loaded(history)


def test_mypy_reports_a_typo_on_the_cached_property_form(tmp_path: Path) -> None:
    stdout, status = _run(_CACHED_PROPERTY_TYPO, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"attr-defined"}
    assert 'maybe "status"?' in stdout


def test_mypy_accepts_any_name_imported_through_a_module_getattr(tmp_path: Path) -> None:
    stdout, status = _run(_MODULE_IMPORT, tmp_path)
    assert (status, _codes(stdout)) == (0, set())
    assert "type[dynamic_attributes.tracking.TrackingHistory]" in stdout

    namespace: dict[str, object] = {}
    with pytest.raises(ImportError, match="cannot import name 'Anything'"):
        exec("from dynamic_attributes.tracking import Anything", namespace)
