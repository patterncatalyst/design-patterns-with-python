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


_OVERRIDE_FINAL = """
from template_method.declarer import NetherlandsDeclarer
from template_method.domain import Consignment, CustomsDeclaration


class Overriding(NetherlandsDeclarer):
    def declare(self, consignment: Consignment) -> CustomsDeclaration:
        raise NotImplementedError
"""


def test_mypy_rejects_overriding_the_final_template(tmp_path: Path) -> None:
    stdout, status = _run(_OVERRIDE_FINAL, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"misc"}
    assert 'Cannot override final attribute "declare"' in stdout


_SKIPS_BASE_STEP = """
from template_method.domain import Consignment


class Base:
    def check(self, consignment: Consignment) -> None:
        if not consignment.commodities:
            raise ValueError("no commodities")


class Forgetful(Base):
    def check(self, consignment: Consignment) -> None:
        return None
"""


def test_mypy_accepts_an_override_that_skips_the_base_step(tmp_path: Path) -> None:
    stdout, status = _run(_SKIPS_BASE_STEP, tmp_path)
    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


_HOOKS_HEAD = """
from decimal import Decimal
from functools import partial

from template_method.domain import Commodity, Money
from template_method.hooks import EU_CLASSIFICATION, EU_SCHEDULE, CustomsHooks
from template_method.hooks import lookup_tariff_code, schedule_duty
"""

_MISSING_REQUIRED = (
    _HOOKS_HEAD
    + """
hooks = CustomsHooks(country="NL", duty=partial(schedule_duty, schedule=EU_SCHEDULE))
"""
)

_WRONG_SIGNATURE = (
    _HOOKS_HEAD
    + """
def duty(total: Money, rate: Decimal) -> Money:
    return total


hooks = CustomsHooks(
    country="NL",
    classify=partial(lookup_tariff_code, EU_CLASSIFICATION, country="NL"),
    duty=duty,
)
"""
)


@pytest.mark.parametrize(
    ("snippet", "code", "message"),
    [
        (_MISSING_REQUIRED, "call-arg", 'Missing named argument "classify" for "CustomsHooks"'),
        (_WRONG_SIGNATURE, "arg-type", 'Argument "duty" to "CustomsHooks" has incompatible type'),
    ],
    ids=["missing-required", "wrong-signature"],
)
def test_mypy_checks_hooks_at_construction(
    snippet: str, code: str, message: str, tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == 1
    assert _codes(stdout) == {code}
    assert message in stdout


_STRUCTURAL_MATCH = """
from typing import Protocol

from template_method.domain import Commodity, Consignment


class DestinationRules(Protocol):
    def classify(self, commodity: Commodity, /) -> str: ...

    def extra_documents(self, consignment: Consignment, /) -> tuple[str, ...]:
        return ()


class Structural:
    def classify(self, commodity: Commodity, /) -> str:
        return "0000.00"


rules: DestinationRules = Structural()
"""


def test_mypy_requires_every_protocol_member_for_a_structural_match(tmp_path: Path) -> None:
    stdout, status = _run(_STRUCTURAL_MATCH, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert "is missing following" in stdout
    assert "extra_documents" in stdout
