import ast
import inspect
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING

import pytest
from pattern_misuse import rating
from pattern_misuse.rating import STANDARD_TARIFF, Consignment, ConsignmentId, quote

if TYPE_CHECKING:
    from conftest import EngineParts, _RateEngine

# The engine's definitions, in the conftest module. Everything else there is a fixture or a
# separate anti-pattern.
ENGINE_DEFINITIONS = [
    "_Charge",
    "_ChargeVisitor",
    "_FlatFeeCharge",
    "_FlatFeeStrategy",
    "_FuelSurcharge",
    "_NetTotalVisitor",
    "_PricingStrategy",
    "_PricingStrategyFactory",
    "_RateEngine",
]

_CONFTEST = Path(__file__).with_name("conftest.py")
_CONSIGNMENT = Consignment(ConsignmentId("CN-1"), "EU")

type Definition = ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef


def _engine_nodes() -> tuple[str, list[ast.stmt]]:
    source = _CONFTEST.read_text()
    classes = [
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.ClassDef) and node.name in ENGINE_DEFINITIONS
    ]
    assert sorted(node.name for node in classes) == ENGINE_DEFINITIONS
    return source, list(classes)


def _function_nodes() -> tuple[str, list[ast.stmt]]:
    source = inspect.getsource(quote)
    return source, ast.parse(source).body


def _without_docstrings(nodes: list[ast.stmt]) -> ast.Module:
    module = ast.Module(body=nodes, type_ignores=[])
    for node in ast.walk(module):
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                node.body[:] = node.body[1:] or [ast.Pass()]
    return module


def _size_of(nodes: list[ast.stmt]) -> tuple[int, int, int]:
    """Classes, functions and non-blank lines of ``ast.unparse`` output without docstrings."""
    module = _without_docstrings(nodes)
    walked = list(ast.walk(module))
    classes = sum(isinstance(node, ast.ClassDef) for node in walked)
    functions = sum(isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) for node in walked)
    lines = [line for line in ast.unparse(module).splitlines() if line.strip()]
    return classes, functions, len(lines)


def _definitions(nodes: list[ast.stmt], prefix: str = "") -> Iterator[tuple[str, Definition]]:
    for node in nodes:
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            name = f"{prefix}{node.name}"
            yield name, node
            yield from _definitions(node.body, f"{name}.")


def _mentions_fuel(source: str, node: Definition) -> bool:
    """Does the definition's own name or own statements (not nested definitions) say ``fuel``?"""
    own = [
        ast.get_source_segment(source, statement) or ""
        for statement in node.body
        if not isinstance(statement, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and not (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant))
    ]
    return "fuel" in " ".join([node.name, *own]).lower()


def _fuel_definitions(source: str, nodes: list[ast.stmt]) -> list[str]:
    return sorted(name for name, node in _definitions(nodes) if _mentions_fuel(source, node))


def _python_calls(call: Callable[[], object], *files: str) -> list[str]:
    """The ``co_qualname`` of each Python-level call into code in the given files, in order."""
    names: list[str] = []

    def profile(frame: FrameType, event: str, _arg: object) -> None:
        if event == "call" and frame.f_code.co_filename in files:
            names.append(frame.f_code.co_qualname)

    sys.setprofile(profile)
    try:
        call()
    finally:
        sys.setprofile(None)
    return names


def test_the_engine_needs_more_classes_functions_and_lines_than_the_function() -> None:
    _, function_nodes = _function_nodes()
    _, engine_nodes = _engine_nodes()
    assert _size_of(function_nodes) == (0, 1, 8)
    assert _size_of(engine_nodes) == (9, 17, 57)


def test_the_fuel_surcharge_lives_in_one_definition_of_the_function() -> None:
    function_source, function_nodes = _function_nodes()
    engine_source, engine_nodes = _engine_nodes()
    assert _fuel_definitions(function_source, function_nodes) == ["quote"]
    assert _fuel_definitions(engine_source, engine_nodes) == [
        "_ChargeVisitor.visit_fuel",
        "_FlatFeeStrategy.charges",
        "_FuelSurcharge",
        "_FuelSurcharge.accept",
        "_NetTotalVisitor.visit_fuel",
    ]


def test_one_engine_quote_makes_more_python_calls_than_the_function(
    engine: _RateEngine,
) -> None:
    files = (str(Path(rating.__file__)), str(_CONFTEST))
    function_calls = _python_calls(lambda: quote(_CONSIGNMENT, STANDARD_TARIFF), *files)
    engine_calls = _python_calls(lambda: engine.quote(_CONSIGNMENT), *files)
    assert function_calls == ["quote"]
    assert engine_calls == [
        "_RateEngine.quote",
        "_NetTotalVisitor.__init__",
        "_FlatFeeStrategy.charges",
        "_FlatFeeCharge.__init__",
        "_FuelSurcharge.__init__",
        "_FlatFeeCharge.accept",
        "_NetTotalVisitor.visit_flat_fee",
        "_FuelSurcharge.accept",
        "_NetTotalVisitor.visit_fuel",
        "_RateEngine.get_tariff",
        "_RateEngine.get_tariff",
    ]


def test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time(
    engine_parts: EngineParts,
) -> None:
    engine = engine_parts.engine(engine_parts.remote_area_factory(), STANDARD_TARIFF)
    with pytest.raises(AttributeError, match="has no attribute 'visit_remote_area'"):
        engine.quote(_CONSIGNMENT)


def test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract(
    engine_parts: EngineParts,
) -> None:
    engine_parts.net_total_visitor()
    with pytest.raises(
        TypeError, match="without an implementation for abstract method 'visit_remote_area'"
    ):
        engine_parts.net_total_with_remote_area()
