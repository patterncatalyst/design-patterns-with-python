import os
import re
import subprocess
import sys
from pathlib import Path

import mypy.api
import pytest
from shortcut_patterns.documents import UnsupportedDocumentError

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


def _ruff_codes(snippet: str, select: str) -> list[str]:
    """Lint a snippet with ruff and return the sorted rule codes it reports."""
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
            "--select",
            select,
            "--output-format",
            "concise",
            "--stdin-filename",
            "probe.py",
            "-",
        ],
        input=snippet,
        capture_output=True,
        text=True,
        check=False,
    )
    return sorted(set(re.findall(r"^probe\.py:\d+:\d+: ([A-Z]+\d+) ", result.stdout, re.MULTILINE)))


# The src model: an issuer that takes a second parameter.
_WRONG_SIGNATURE = """
from collections.abc import Mapping

from shortcut_patterns.documents import ConsignmentId, DocumentIssuer, DocumentKind


def issue_with_copies(consignment_id: ConsignmentId, copies: int) -> str:
    return f"MF-{consignment_id}" * copies


table: Mapping[DocumentKind, DocumentIssuer] = {DocumentKind.MANIFEST: issue_with_copies}
"""

# The src model: a lookup with the text of a kind.
_WRONG_KEY = """
from shortcut_patterns.documents import ISSUERS

ISSUERS["manifest"]
"""

# The src model: a table annotated with the alias that misses a kind.
_MISSING_KIND = """
from collections.abc import Mapping

from shortcut_patterns.documents import (
    ConsignmentId,
    DocumentIssuer,
    DocumentKind,
    issue,
    issue_bill_of_lading,
    issue_manifest,
)

two: Mapping[DocumentKind, DocumentIssuer] = frozendict(
    {
        DocumentKind.BILL_OF_LADING: issue_bill_of_lading,
        DocumentKind.MANIFEST: issue_manifest,
    }
)
issue(DocumentKind.CUSTOMS_DECLARATION, ConsignmentId("CN-1"), issuers=two)
"""

# Reduced models: a two-arm match with assert_never, and a two-arm chain with no else.
_MISSING_ARMS = """
from enum import Enum
from typing import assert_never


class Kind(Enum):
    BILL_OF_LADING = 1
    MANIFEST = 2
    CUSTOMS_DECLARATION = 3


def by_match(kind: Kind) -> str:
    match kind:
        case Kind.BILL_OF_LADING:
            return "BL"
        case Kind.MANIFEST:
            return "MF"
        case _:
            assert_never(kind)


def by_chain(kind: Kind) -> str:
    if kind is Kind.BILL_OF_LADING:
        return "BL"
    if kind is Kind.MANIFEST:
        return "MF"
"""

# Reduced model: the same chain, ending in an else that raises.
_RAISING_ELSE = """
from enum import Enum


class Kind(Enum):
    BILL_OF_LADING = 1
    MANIFEST = 2
    CUSTOMS_DECLARATION = 3


def by_chain(kind: Kind) -> str:
    if kind is Kind.BILL_OF_LADING:
        return "BL"
    elif kind is Kind.MANIFEST:
        return "MF"
    else:
        raise ValueError(kind)


by_chain(Kind.CUSTOMS_DECLARATION)
"""

# The src model: writing into the table.
_ASSIGN_INTO_TABLE = """
from shortcut_patterns.documents import ISSUERS, DocumentKind, issue_manifest

ISSUERS[DocumentKind.MANIFEST] = issue_manifest
"""

# The src model: calling the result of get, which may be None.
_GET_THEN_CALL = """
from shortcut_patterns.documents import ISSUERS, ConsignmentId, DocumentKind


def probe(kind: DocumentKind, cid: ConsignmentId) -> str:
    return ISSUERS.get(kind)(cid)
"""

_STRING_CHAIN = """
def rate(code: str) -> int:
    if code == "0901.21":
        return 8
    elif code == "6109.10":
        return 12
    elif code == "8501.10":
        return 3
    else:
        return 0
"""

_ENUM_CHAIN = """
from enum import Enum


class Kind(Enum):
    BILL_OF_LADING = 1
    MANIFEST = 2
    CUSTOMS_DECLARATION = 3


def prefix(kind: Kind) -> str:
    if kind == Kind.BILL_OF_LADING:
        return "BL"
    elif kind == Kind.MANIFEST:
        return "MF"
    elif kind == Kind.CUSTOMS_DECLARATION:
        return "CD"
    else:
        return "XX"
"""

_IDIOMS = """
def keys(cache: dict[str, int], code: str) -> int:
    if code in cache.keys():
        return cache[code]
    return 0


def lookup(cache: dict[str, int], code: str) -> int:
    if code in cache:
        rate = cache[code]
    else:
        rate = 0
    return rate


def forget(cache: dict[str, int], code: str) -> None:
    try:
        del cache[code]
    except KeyError:
        pass
"""


def test_mypy_checks_an_issuers_signature_in_the_table(tmp_path: Path) -> None:
    stdout, status = _run(_WRONG_SIGNATURE, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["dict-item"]
    assert 'expected "DocumentKind": "Callable[[ConsignmentId], str]"' in stdout


def test_mypy_checks_the_key_type_of_a_table_lookup(tmp_path: Path) -> None:
    stdout, status = _run(_WRONG_KEY, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["index"]
    assert 'Invalid index type "str"' in stdout


def test_mypy_accepts_a_table_that_misses_a_kind(tmp_path: Path) -> None:
    stdout, status = _run(_MISSING_KIND, tmp_path)
    assert (status, _codes(stdout)) == (0, [])
    with pytest.raises(UnsupportedDocumentError, match="no issuer for 'customs declaration'"):
        exec(_MISSING_KIND, {})


def test_mypy_reports_a_missing_arm_in_a_match_and_an_if_chain_without_else(
    tmp_path: Path,
) -> None:
    stdout, status = _run(_MISSING_ARMS, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["arg-type", "return"]
    assert 'expected "Never"' in stdout
    assert "Missing return statement" in stdout


def test_mypy_accepts_an_if_chain_whose_else_raises(tmp_path: Path) -> None:
    stdout, status = _run(_RAISING_ELSE, tmp_path)
    assert (status, _codes(stdout)) == (0, [])
    with pytest.raises(ValueError, match="CUSTOMS_DECLARATION"):
        exec(_RAISING_ELSE, {})


def test_mypy_refuses_assignment_into_the_issuer_table(tmp_path: Path) -> None:
    stdout, status = _run(_ASSIGN_INTO_TABLE, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["index"]
    assert "Unsupported target for indexed assignment" in stdout


def test_mypy_requires_a_branch_after_dict_get(tmp_path: Path) -> None:
    stdout, status = _run(_GET_THEN_CALL, tmp_path)
    assert status == 1
    assert _codes(stdout) == ["misc"]
    assert '"None" not callable' in stdout


def test_ruff_flags_an_if_chain_over_literals_but_not_over_enum_members() -> None:
    assert _ruff_codes(_STRING_CHAIN, "SIM116") == ["SIM116"]
    assert _ruff_codes(_ENUM_CHAIN, "SIM116") == []


def test_ruff_suggests_get_suppress_and_plain_membership() -> None:
    assert _ruff_codes(_IDIOMS, "SIM401,SIM105,SIM118") == ["SIM105", "SIM118", "SIM401"]
