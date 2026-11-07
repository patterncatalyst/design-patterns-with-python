"""Shape review: four rules over a draft's syntax tree, each from a pattern the book teaches.

The rules are a checklist of four shapes. A draft that passes them can still be wrong.
"""

import ast
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class Finding:
    line: int
    rule: str
    advice: str


type ShapeRule = Callable[[ast.Module], Iterator[Finding]]

type _Function = ast.FunctionDef | ast.AsyncFunctionDef


def _classes(tree: ast.Module) -> Iterator[ast.ClassDef]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            yield node


def _methods(cls: ast.ClassDef) -> list[_Function]:
    return [node for node in cls.body if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)]


def _decorated_with(function: _Function, *names: str) -> bool:
    return any(isinstance(d, ast.Name) and d.id in names for d in function.decorator_list)


def _derives_from_abc(cls: ast.ClassDef) -> bool:
    return any(
        (isinstance(base, ast.Name) and base.id == "ABC")
        or (isinstance(base, ast.Attribute) and base.attr == "ABC")
        for base in cls.bases
    )


def single_method_base(tree: ast.Module) -> Iterator[Finding]:
    """An abstract base with one abstract method is a callable type (Strategy: the callable)."""
    for cls in _classes(tree):
        methods = _methods(cls)
        if (
            _derives_from_abc(cls)
            and len(methods) == 1
            and _decorated_with(methods[0], "abstractmethod")
        ):
            yield Finding(cls.lineno, "single-method-base", "use a callable type alias")


def static_only_class(tree: ast.Module) -> Iterator[Finding]:
    """A class whose methods are all static or class methods is a module (Factory Method and
    Abstract Factory; Shortcut patterns: dict dispatch, function tables, and EAFP)."""
    for cls in _classes(tree):
        methods = _methods(cls)
        if methods and all(_decorated_with(m, "staticmethod", "classmethod") for m in methods):
            yield Finding(cls.lineno, "static-only-class", "use module-level functions")


def accessor_pair(tree: ast.Module) -> Iterator[Finding]:
    """A ``get_x`` with a matching ``set_x`` is an attribute (Anti-patterns and pattern misuse)."""
    for cls in _classes(tree):
        methods = _methods(cls)
        names = {m.name for m in methods}
        for method in methods:
            if method.name.startswith("get_") and f"set_{method.name[4:]}" in names:
                yield Finding(method.lineno, "accessor-pair", "use a plain attribute")


def instance_in_new(tree: ast.Module) -> Iterator[Finding]:
    """A ``__new__`` that stores on ``cls`` is a hand-built singleton (Singleton: module, Borg,
    and metaclass)."""
    for cls in _classes(tree):
        for method in _methods(cls):
            if method.name == "__new__" and _stores_on_cls(method):
                yield Finding(method.lineno, "instance-in-new", "use a module-level instance")


def _stores_on_cls(function: _Function) -> bool:
    return any(
        isinstance(node, ast.Assign)
        and any(
            isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "cls"
            for t in node.targets
        )
        for node in ast.walk(function)
    )


SHAPE_RULES: tuple[ShapeRule, ...] = (
    single_method_base,
    static_only_class,
    accessor_pair,
    instance_in_new,
)


def review(source: str, /, *, rules: Sequence[ShapeRule] = SHAPE_RULES) -> list[Finding]:
    """Findings from every rule, sorted by line: ``ast.walk`` yields nodes in no fixed order."""
    tree = ast.parse(source)
    return sorted(finding for rule in rules for finding in rule(tree))
