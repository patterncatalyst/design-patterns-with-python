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
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


# Reduced model: a self-contained class with the argument types and order of the positional
# constructor in conftest.py, without its checks.
_LEGACY = """
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class Weight:
    def __init__(self, kilograms: Decimal) -> None: ...


class Money:
    def __init__(self, amount: Decimal, currency: str) -> None: ...


class LegacyBookingRequest:
    def __init__(
        self,
        consignment_id: ConsignmentId,
        origin: str,
        destination: str,
        weight: Weight,
        carrier: str,
        service: str,
        insured: bool,
        declared_value: Money | None,
        dangerous_goods: bool,
        reference: str | None,
        notify_party: str | None,
        documents: tuple[str, ...],
    ) -> None: ...
"""

_SAME_TYPED_SWAPS = (
    _LEGACY
    + """
cn = ConsignmentId("CN-1")
weight = Weight(Decimal("1"))
ports_swapped = LegacyBookingRequest(
    cn, "SGSIN", "NLRTM", weight, "FASTLINE", "standard", False, None, False, None, None, ()
)
carrier_and_service_swapped = LegacyBookingRequest(
    cn, "NLRTM", "SGSIN", weight, "standard", "FASTLINE", False, None, False, None, None, ()
)
flags_swapped = LegacyBookingRequest(
    cn, "NLRTM", "SGSIN", weight, "FASTLINE", "standard", True, None, False, None, None, ()
)
"""
)

_DIFFERENT_TYPED_SWAP = (
    _LEGACY
    + """
cn = ConsignmentId("CN-1")
weight = Weight(Decimal("1"))
money = Money(Decimal("100"), "EUR")
swapped = LegacyBookingRequest(
    cn, "NLRTM", "SGSIN", money, "FASTLINE", "standard", True, weight, False, None, None, ()
)
"""
)


def test_mypy_cannot_see_two_same_typed_arguments_swapped(tmp_path: Path) -> None:
    stdout, status = _run(_SAME_TYPED_SWAPS, tmp_path)

    assert status == 0
    assert stdout == ""


def test_mypy_reports_swapped_arguments_of_different_types(tmp_path: Path) -> None:
    stdout, status = _run(_DIFFERENT_TYPED_SWAP, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'has incompatible type "Money"; expected "Weight"' in stdout
    assert 'has incompatible type "Weight"; expected "Money | None"' in stdout


_PREAMBLE = """
from decimal import Decimal

from builder_prototype.booking import BookingRequest
from builder_prototype.domain import ConsignmentId, Weight

cn = ConsignmentId("CN-1")
weight = Weight(Decimal("1"))
"""

_LITERAL_SWAP = (
    _PREAMBLE
    + """
BookingRequest(
    consignment_id=cn, origin="NLRTM", destination="SGSIN", weight=weight,
    carrier="standard", service="FASTLINE",
)
"""
)

_MISSING_FIELD = (
    _PREAMBLE
    + """
BookingRequest(consignment_id=cn, origin="NLRTM", weight=weight)
"""
)

_MISSPELT_KEYWORD = (
    _PREAMBLE
    + """
BookingRequest(
    consignment_id=cn, origin="NLRTM", destination="SGSIN", weight=weight, servce="express"
)
"""
)


@pytest.mark.parametrize(
    ("snippet", "codes", "fragments"),
    [
        (
            _LITERAL_SWAP,
            {"arg-type"},
            (
                'Argument "carrier" to "BookingRequest"',
                "\"Literal['standard']\"",
                'Argument "service" to "BookingRequest"',
            ),
        ),
        (_MISSING_FIELD, {"call-arg"}, ('Missing named argument "destination"',)),
        (_MISSPELT_KEYWORD, {"call-arg"}, ('did you mean "service"?',)),
    ],
    ids=["literal-swap", "missing-field", "misspelt-keyword"],
)
def test_mypy_checks_literal_fields_and_keyword_names(
    snippet: str, codes: set[str], fragments: tuple[str, ...], tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)

    assert status == 1
    assert _codes(stdout) == codes
    assert all(fragment in stdout for fragment in fragments)


# Reduced model: a fluent builder whose required steps are only checked when `build` runs.
_BUILDER = """
from typing import Self


class Booking: ...


class BookingBuilder:
    def __init__(self) -> None:
        self._origin: str | None = None
        self._destination: str | None = None

    def origin(self, origin: str) -> Self:
        self._origin = origin
        return self

    def destination(self, destination: str) -> Self:
        self._destination = destination
        return self

    def build(self) -> Booking:
        if self._origin is None or self._destination is None:
            raise ValueError("builder is missing a step")
        return Booking()


booking = BookingBuilder().origin("NLRTM").build()
"""


def test_mypy_accepts_a_builder_with_a_step_left_out(tmp_path: Path) -> None:
    stdout, status = _run(_BUILDER, tmp_path)

    assert status == 0
    assert stdout == ""


_COPY_PREAMBLE = (
    _PREAMBLE
    + """
import copy
import dataclasses

request = BookingRequest(consignment_id=cn, origin="NLRTM", destination="SGSIN", weight=weight)
"""
)

_PLAIN_CLASS = """
import copy


class Plain:
    service = "standard"


copy.replace(Plain(), service="express")
"""


@pytest.mark.parametrize(
    ("snippet", "codes", "fragment"),
    [
        (
            _COPY_PREAMBLE + "dataclasses.replace(request, wieght=weight)\n",
            {"call-arg"},
            'did you mean "weight"?',
        ),
        (
            _COPY_PREAMBLE + "copy.replace(request, wieght=weight)\n",
            {"call-arg"},
            'did you mean "weight"?',
        ),
        (
            _COPY_PREAMBLE + "copy.replace(request, origin=1)\n",
            {"arg-type"},
            'has incompatible type "int"; expected "str"',
        ),
        (_PLAIN_CLASS, {"arg-type"}, "_SupportsReplace"),
    ],
    ids=["dataclasses-name", "copy-name", "copy-type", "plain-class"],
)
def test_mypy_checks_copy_replace_like_dataclasses_replace(
    snippet: str, codes: set[str], fragment: str, tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)

    assert status == 1
    assert _codes(stdout) == codes
    assert fragment in stdout


_SHALLOW_COPY = """
import copy
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Loose:
    documents: list[str] = field(default_factory=list)


template = Loose(documents=["commercial invoice"])
clone = copy.copy(template)
clone.documents.append("dangerous goods note")
"""


def test_mypy_cannot_see_a_shallow_copy_sharing_a_list(tmp_path: Path) -> None:
    stdout, status = _run(_SHALLOW_COPY, tmp_path)

    assert status == 0
    assert stdout == ""
