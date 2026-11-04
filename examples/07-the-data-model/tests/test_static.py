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


_NARROWED_EQ = """
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Carton:
    length_cm: int

    def __eq__(self, other: "Carton") -> bool:
        return self.length_cm == other.length_cm

    def __hash__(self) -> int:
        return hash(self.length_cm)
"""

_BAD_OPERANDS = """
from decimal import Decimal

from data_model.money import Money

price = Money(Decimal("12.50"), "EUR")
price * 1.5
1.5 * price
price >= 3
price + 1
"""

_ACCEPTED = """
from decimal import Decimal

from data_model.money import ConsignmentId, Money, RateQuote
from data_model.tracking import TrackingHistory

price = Money(Decimal("12.50"), "EUR")
doubled = Decimal("2") * price
ordered = price <= price
text = f"{price:>12}"
total = sum([price, price], start=Money(Decimal("0.00"), "EUR"))
quotes = [RateQuote(ConsignmentId("CN-00000001"), price, price)]
by_total = sorted(quotes, key=lambda q: q.total)
history = TrackingHistory(())
last = ""
for event in history:
    last = event.location
"""

_UNORDERED_MONEY = """
from dataclasses import dataclass
from decimal import Decimal

from data_model.money import ConsignmentId


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str


@dataclass(frozen=True, slots=True)
class RateQuote:
    consignment_id: ConsignmentId
    net: Money

    @property
    def total(self) -> Money:
        return self.net


def cheapest(quotes: list[RateQuote]) -> list[RateQuote]:
    return sorted(quotes, key=lambda q: q.total)
"""

_BROKEN_HASH_CONTRACT = """
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Carton:
    length_cm: int
    width_cm: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Carton):
            return NotImplemented
        return sorted((self.length_cm, self.width_cm)) == sorted((other.length_cm, other.width_cm))


cartons = {Carton(1, 2), Carton(2, 1)}
"""


def test_mypy_rejects_an_eq_that_narrows_its_argument(tmp_path: Path) -> None:
    stdout, status = _run(_NARROWED_EQ, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"override"}
    assert "This violates the Liskov substitution principle" in stdout
    assert 'It is recommended for "__eq__" to work with arbitrary objects' in stdout


def test_mypy_rejects_operands_the_methods_do_not_accept(tmp_path: Path) -> None:
    stdout, status = _run(_BAD_OPERANDS, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"operator"}
    assert len(stdout.splitlines()) == 4


def test_mypy_accepts_the_protocols_the_types_define(tmp_path: Path) -> None:
    stdout, status = _run(_ACCEPTED, tmp_path)
    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    stdout, status = _run(_UNORDERED_MONEY, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"arg-type", "return-value"}


def test_mypy_cannot_see_a_broken_hash_contract(tmp_path: Path) -> None:
    stdout, status = _run(_BROKEN_HASH_CONTRACT, tmp_path)
    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
