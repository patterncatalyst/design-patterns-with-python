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


_UNGUARDED = """
from structural_typing.carriers import find_gateway
from structural_typing.domain import Consignment


def book(code: str, c: Consignment) -> str:
    return find_gateway(code).book(c)
"""

_WALRUS = """
from structural_typing.carriers import find_gateway
from structural_typing.domain import Consignment


def book(code: str, c: Consignment) -> str:
    if (gateway := find_gateway(code)) is not None:
        return gateway.book(c)
    return ""
"""

_MATCH = """
from structural_typing.carriers import find_gateway
from structural_typing.domain import Consignment


def book(code: str, c: Consignment) -> str:
    match find_gateway(code):
        case None:
            return ""
        case gateway:
            return gateway.book(c)
"""

_EARLY_RETURN = """
from structural_typing.carriers import find_gateway
from structural_typing.domain import Consignment


def book(code: str, c: Consignment) -> str:
    gateway = find_gateway(code)
    if gateway is None:
        return ""
    return gateway.book(c)
"""

_ASSERT = """
from structural_typing.carriers import find_gateway
from structural_typing.domain import Consignment


def book(code: str, c: Consignment) -> str:
    gateway = find_gateway(code)
    assert gateway is not None
    return gateway.book(c)
"""


@pytest.mark.parametrize(
    ("snippet", "status", "codes"),
    [
        (_UNGUARDED, 1, {"union-attr"}),
        (_WALRUS, 0, set()),
        (_MATCH, 0, set()),
        (_EARLY_RETURN, 0, set()),
        (_ASSERT, 0, set()),
    ],
    ids=["unguarded", "walrus", "match", "early-return", "assert"],
)
def test_mypy_requires_a_branch_for_absence(
    snippet: str, status: int, codes: set[str], tmp_path: Path
) -> None:
    stdout, actual = _run(snippet, tmp_path)
    assert actual == status
    assert _codes(stdout) == codes
    if status:
        assert 'Item "None" of "CarrierGateway | None" has no attribute "book"' in stdout


_SENTINEL_UNGUARDED = """
from structural_typing.carriers import ACCOUNT_DEFAULT


def shout(preferred: str | ACCOUNT_DEFAULT | None) -> str:
    return preferred.upper()
"""

_SENTINEL_NARROWED = """
from structural_typing.carriers import ACCOUNT_DEFAULT


def shout(preferred: str | ACCOUNT_DEFAULT | None) -> str:
    if preferred is ACCOUNT_DEFAULT or preferred is None:
        return ""
    return preferred.upper()
"""


def test_mypy_requires_a_branch_for_the_sentinel(tmp_path: Path) -> None:
    stdout, status = _run(_SENTINEL_UNGUARDED, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"union-attr"}
    assert 'Item "sentinel" of' in stdout
    assert 'Item "None" of' in stdout
    stdout, status = _run(_SENTINEL_NARROWED, tmp_path)
    assert status == 0
    assert stdout == ""


_NARROW_QUOTER_AS_GENERAL = """
from structural_typing.domain import Consignment
from structural_typing.pricing import HazmatQuoter, price_all

price_all(HazmatQuoter(), [])
"""

_GENERAL_QUOTER_AS_NARROW = """
from structural_typing.pricing import GeneralQuoter, price_hazmat

price_hazmat(GeneralQuoter(), [])
"""


def test_mypy_infers_quoter_variance(tmp_path: Path) -> None:
    stdout, status = _run(_NARROW_QUOTER_AS_GENERAL, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert "have conflicts" in stdout
    stdout, status = _run(_GENERAL_QUOTER_AS_NARROW, tmp_path)
    assert status == 0
    assert stdout == ""


_WITHOUT_SLASH = """
from typing import Protocol

from structural_typing.domain import Consignment, Money
from structural_typing.pricing import per_kg


class KwRule(Protocol):
    def __call__(self, consignment: Consignment) -> Money: ...


rule: KwRule = per_kg
"""

_WITH_SLASH = """
from structural_typing.pricing import PricingRule, per_kg

rule: PricingRule = per_kg
"""


def test_mypy_matches_callback_parameter_names_without_slash(tmp_path: Path) -> None:
    stdout, status = _run(_WITHOUT_SLASH, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert '"KwRule.__call__" has type' in stdout
    stdout, status = _run(_WITH_SLASH, tmp_path)
    assert status == 0
    assert stdout == ""


_PROTOCOL_USE = """
from structural_typing.carriers import CarrierGateway
from structural_typing.domain import Consignment


class QuoteOnly:
    def quote(self, consignment: Consignment, /) -> str:
        return ""


gateway: CarrierGateway = QuoteOnly()
"""

_ABC_CONSTRUCTION = """
from structural_typing.carriers import CarrierBase


class Half(CarrierBase):
    code = "HALF"


Half()
"""

_DECLARED_PROTOCOL = """
from structural_typing.carriers import CarrierGateway


class Declared(CarrierGateway):
    pass


Declared()
"""

_OVERRIDE_TYPO = """
from typing import override

from structural_typing.carriers import CarrierBase
from structural_typing.domain import Consignment


class Typo(CarrierBase):
    code = "TYPO"

    @override
    def boook(self, consignment: Consignment, /) -> str:
        return ""
"""


@pytest.mark.parametrize(
    ("snippet", "codes", "message"),
    [
        (
            _PROTOCOL_USE,
            {"assignment"},
            'expression has type "QuoteOnly", variable has type "CarrierGateway"',
        ),
        (_ABC_CONSTRUCTION, {"abstract"}, "Cannot instantiate abstract class"),
        (_DECLARED_PROTOCOL, {"abstract"}, "Cannot instantiate abstract class"),
        (
            _OVERRIDE_TYPO,
            {"misc"},
            "marked as an override, but no base method was found",
        ),
    ],
    ids=["protocol-use", "abc-construction", "declared-protocol", "override-typo"],
)
def test_mypy_checks_protocols_at_use_and_abcs_at_construction(
    snippet: str, codes: set[str], message: str, tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == 1
    assert _codes(stdout) == codes
    assert message in stdout


_CONFLICTING_MEMBER = """
from structural_typing.carriers import CarrierGateway


class WrongParameter:
    def book(self, consignment: int, /) -> str:
        return ""


gateway: CarrierGateway = WrongParameter()
"""


def test_mypy_explains_a_conflicting_member_but_not_a_wholly_absent_one(tmp_path: Path) -> None:
    """mypy 2.4.1 adds no 'missing protocol member' note when the one required member is absent."""
    stdout, status = _run(_PROTOCOL_USE, tmp_path)
    assert status == 1
    assert "protocol member" not in stdout
    assert "note:" not in stdout
    stdout, status = _run(_CONFLICTING_MEMBER, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert 'Following member(s) of "WrongParameter" have conflicts' in stdout


_NULL_GATEWAY = """
from structural_typing.carriers import CarrierGateway
from structural_typing.domain import Consignment


class NullGateway:
    def book(self, consignment: Consignment, /) -> str:
        return ""


gateway: CarrierGateway = NullGateway()
"""


def test_mypy_accepts_a_null_gateway(tmp_path: Path) -> None:
    stdout, status = _run(_NULL_GATEWAY, tmp_path)
    assert status == 0
    assert stdout == ""
