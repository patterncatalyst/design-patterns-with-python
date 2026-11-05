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
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


_EVENT_LEFT_OUT = """
from typing import assert_never

from visitor_memento_interpreter.events import Booked, Cleared, Departed, HandlingEvent, Loaded


def label(event: HandlingEvent, /) -> str:
    match event:
        case Booked():
            return "booked"
        case Loaded():
            return "loaded"
        case Departed():
            return "departed"
        case Cleared():
            return "cleared"
        case _:
            assert_never(event)
"""

_SINGLEDISPATCH_MISSING_AN_EVENT = """
from functools import singledispatch

from visitor_memento_interpreter.events import Booked, Cleared, Departed, Loaded


@singledispatch
def label(event: object, /) -> str:
    return "unrecognised event"


@label.register
def _(event: Booked, /) -> str:
    return "booked"


@label.register
def _(event: Loaded, /) -> str:
    return "loaded"


@label.register
def _(event: Departed, /) -> str:
    return "departed"


@label.register
def _(event: Cleared, /) -> str:
    return "cleared"
"""

# Reduced model: an accept form with two element classes and a visitor missing one visit method.
_VISITOR_MISSING_A_METHOD = """
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Booked:
    port: str

    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_booked(self)


@dataclass(frozen=True, slots=True)
class Delivered:
    port: str

    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_delivered(self)


class EventVisitor[T](Protocol):
    def visit_booked(self, event: Booked, /) -> T: ...
    def visit_delivered(self, event: Delivered, /) -> T: ...


class Describer:
    def visit_booked(self, event: Booked, /) -> str:
        return f"booked at {event.port}"


def run(event: Booked | Delivered) -> str:
    return event.accept(Describer())
"""

_CHANGE_A_SNAPSHOT = """
from visitor_memento_interpreter.domain import DocumentKind
from visitor_memento_interpreter.memento import Booking


def run(booking: Booking) -> None:
    snapshot = booking.snapshot()
    snapshot.request = booking.request
    snapshot.documents.add(DocumentKind.COMMERCIAL_INVOICE)
"""

_NODE_LEFT_OUT_OF_EVALUATE = """
from typing import assert_never

from visitor_memento_interpreter.domain import Consignment, Money
from visitor_memento_interpreter.tariff import Add, Expr, Flat, Max, PerKg


def price(expr: Expr, consignment: Consignment, /) -> Money:
    match expr:
        case PerKg(rate):
            return rate
        case Flat(amount):
            return amount
        case Add(left, right):
            return price(left, consignment) + price(right, consignment)
        case Max(left, right):
            return max(price(left, consignment), price(right, consignment))
        case _:
            assert_never(expr)
"""

_CHILD_NOT_AN_EXPRESSION = """
from decimal import Decimal

from visitor_memento_interpreter.domain import Money
from visitor_memento_interpreter.tariff import Add, PerKg

rule = Add(PerKg(Money(Decimal(1), "EUR")), "45.00 EUR")
"""


def test_mypy_reports_an_event_left_out_of_a_match(tmp_path: Path) -> None:
    stdout, status = _run(_EVENT_LEFT_OUT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert '"Delivered"; expected "Never"' in stdout


def test_mypy_accepts_a_singledispatch_visitor_that_misses_an_event(tmp_path: Path) -> None:
    stdout, status = _run(_SINGLEDISPATCH_MISSING_AN_EVENT, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


def test_mypy_reports_a_visitor_class_missing_a_visit_method(tmp_path: Path) -> None:
    stdout, status = _run(_VISITOR_MISSING_A_METHOD, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert "EventVisitor" in stdout


def test_mypy_refuses_to_change_a_snapshot(tmp_path: Path) -> None:
    stdout, status = _run(_CHANGE_A_SNAPSHOT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"misc", "attr-defined"}
    assert "is read-only" in stdout


def test_mypy_reports_a_tariff_node_left_out_of_evaluate(tmp_path: Path) -> None:
    stdout, status = _run(_NODE_LEFT_OUT_OF_EVALUATE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert '"OverWeight"; expected "Never"' in stdout


def test_mypy_refuses_a_node_whose_child_is_not_an_expression(tmp_path: Path) -> None:
    stdout, status = _run(_CHILD_NOT_AN_EXPRESSION, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'Argument 2 to "Add" has incompatible type "str"' in stdout
