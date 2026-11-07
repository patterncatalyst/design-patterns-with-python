"""The Law of Demeter, on two readers of one shipment."""

import ast
import importlib
import inspect
import pkgutil
import textwrap
from collections.abc import Callable
from decimal import Decimal

import pytest
from principles_reviewed.billing import Invoice, LineItem, Shipment
from principles_reviewed.domain import ConsignmentId, Money

type Reader = Callable[[Shipment], str]


def _uncredited(consignment_id: str, *amounts: str) -> Shipment:
    identifier = ConsignmentId(consignment_id)
    lines = tuple(LineItem("charge", Money(Decimal(amount))) for amount in amounts)
    return Shipment(identifier, Invoice(identifier, lines))


@pytest.mark.parametrize(
    ("shipment", "line"),
    [
        pytest.param(_uncredited("CN-1", "30.00"), "CN-1 30.00 EUR", id="one-line"),
        pytest.param(_uncredited("CN-2", "30.00", "5.63"), "CN-2 35.63 EUR", id="two-lines"),
    ],
)
def test_both_readers_give_the_same_line_without_credits(
    reader_form: Reader, shipment: Shipment, line: str
) -> None:
    assert reader_form(shipment) == line


@pytest.mark.parametrize(
    ("reader_form", "line"),
    [
        pytest.param("delegating", "CN-3 25.00 EUR", id="delegating"),
        pytest.param("chained", "CN-3 35.63 EUR", id="chained"),
    ],
    indirect=["reader_form"],
)
def test_a_credit_reaches_only_the_reader_that_asks_the_shipment(
    reader_form: Reader, credited: Shipment, line: str
) -> None:
    assert reader_form(credited) == line


@pytest.mark.parametrize(
    ("reader_form", "names"),
    [
        pytest.param("delegating", ["amount_due", "consignment_id"], id="delegating"),
        pytest.param("chained", ["consignment_id", "invoice", "total"], id="chained"),
    ],
    indirect=["reader_form"],
)
def test_each_reader_names_the_attributes_it_depends_on(
    reader_form: Reader, names: list[str]
) -> None:
    """Measures the attribute names a reader's own source uses, not the calls made inside them."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(reader_form)))
    used = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert sorted(used) == names


def test_the_comparison_reader_is_not_part_of_the_package() -> None:
    package = importlib.import_module("principles_reviewed")
    modules = [
        importlib.import_module(info.name)
        for info in pkgutil.iter_modules(package.__path__, "principles_reviewed.")
    ]
    assert [module.__name__ for module in modules] == [
        "principles_reviewed.billing",
        "principles_reviewed.domain",
    ]
    assert [module.__name__ for module in modules if hasattr(module, "_chained_remittance")] == []
