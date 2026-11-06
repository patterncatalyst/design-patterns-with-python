"""What mypy checks at the router: the rewrite must take a consignment, like the legacy engine."""

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


# A rewrite of the wrong shape: it takes a zone and a weight where the legacy engine takes a
# consignment.
_WRONG_SHAPE = """
from decimal import Decimal

from refactor_or_rewrite.domain import ConsignmentId, Money, RateQuote, Weight
from refactor_or_rewrite.legacy import RateEngine
from refactor_or_rewrite.strangler import Router


def by_weight(zone: str, weight: Weight) -> RateQuote:
    return RateQuote(ConsignmentId("CN-1"), Money(Decimal("1.00")))


Router(RateEngine().quote, by_weight, ("ASIA",))
"""

# The same call with the real rewrite, whose keyword-only tariff parameter has a default.
_RIGHT_SHAPE = """
from refactor_or_rewrite.legacy import RateEngine
from refactor_or_rewrite.rating import quote
from refactor_or_rewrite.strangler import Router

Router(RateEngine().quote, quote, ("ASIA",))
"""


def test_mypy_requires_the_rewrite_to_take_a_consignment(tmp_path: Path) -> None:
    wrong, wrong_status = _run(_WRONG_SHAPE, tmp_path)
    right, right_status = _run(_RIGHT_SHAPE, tmp_path)

    assert [_codes(wrong), _codes(right)] == [["arg-type"], []]
    assert (wrong_status, right_status) == (1, 0)
    assert 'expected "Callable[[Consignment], RateQuote]"' in wrong
