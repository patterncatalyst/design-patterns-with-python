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


# Reduced model: a ParamSpec timer without functools.wraps, which still keeps the static signature.
_PARAMSPEC_WITHOUT_WRAPS = """
from collections.abc import Callable


def timer[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


@timer
def render_bill(bill: str, /, *, width: int = 72) -> str:
    return bill[:width]


render_bill("BL-1", width=30)
render_bill("BL-1", width="30")
"""

# Reduced model: the same timer with its annotations left out.
_UNTYPED_DECORATOR = """
def timer(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@timer
def render_bill(bill: str) -> str:
    return bill
"""

# Reduced model: a factory whose window is positional, used without calling it.
_POSITIONAL_FACTORY_USED_BARE = """
from collections.abc import Callable


def cached_for[**P, R](seconds: float) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        return func

    return decorate


@cached_for
def render_bill(bill: str) -> str:
    return bill
"""

_KEYWORD_ONLY_FACTORY_USED_BARE = """
from decorators_done_right.domain import BillOfLading
from decorators_done_right.rendering import cached_for, render_bill


@cached_for
def render(bill: BillOfLading, /) -> str:
    return render_bill(bill)
"""

# Reduced model: a decorator that supplies the first argument, typed with Concatenate. The first
# call is right and the second repeats the argument the decorator already supplied.
_CONCATENATE = """
import functools
from collections.abc import Callable
from typing import Concatenate


def with_width[**P, R](width: int) -> Callable[[Callable[Concatenate[int, P], R]], Callable[P, R]]:
    def decorate(func: Callable[Concatenate[int, P], R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(width, *args, **kwargs)

        return wrapper

    return decorate


@with_width(72)
def render(width: int, bill: str, /) -> str:
    return bill[:width]


render("B/L 1")
render(72, "B/L 1")
"""

# Reduced model: a class decorator that registers a class and forgets to return it.
_CLASS_DECORATOR_FORGETS_TO_RETURN = """
registry: list[type] = []


def register[C: type](cls: C) -> C:
    registry.append(cls)
"""

# A reduced model sits beside the src class: a decorator declared to return int. mypy doesn't
# apply a class decorator's return type, so both classes keep their own type.
_CLASS_TYPE_THROUGH_DOCUMENT_KIND = """
from typing import assert_type

from decorators_done_right.domain import BillOfLading, ConsignmentId

bill = BillOfLading("BL-1", ConsignmentId("CN-1"), "NLRTM", "SGSIN")
assert_type(bill.number, str)


def to_int(cls: type) -> int:
    return 1


@to_int
class CustomsDeclaration:
    number: str = "CD-1"


assert_type(CustomsDeclaration, type[CustomsDeclaration])
"""


def test_mypy_keeps_the_signature_through_a_wrapper_without_wraps(tmp_path: Path) -> None:
    stdout, status = _run(_PARAMSPEC_WITHOUT_WRAPS, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert stdout.count("error:") == 1
    assert 'Argument "width" to "render_bill" has incompatible type "str"; expected "int"' in stdout


def test_mypy_reports_an_untyped_decorator(tmp_path: Path) -> None:
    stdout, status = _run(_UNTYPED_DECORATOR, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"untyped-decorator", "no-untyped-def"}
    assert 'Untyped decorator makes function "render_bill" untyped' in stdout


def test_mypy_refuses_a_positional_factory_used_bare(tmp_path: Path) -> None:
    stdout, status = _run(_POSITIONAL_FACTORY_USED_BARE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'Argument 1 to "cached_for" has incompatible type' in stdout


def test_mypy_refuses_a_keyword_only_factory_used_bare(tmp_path: Path) -> None:
    stdout, status = _run(_KEYWORD_ONLY_FACTORY_USED_BARE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"call-arg", "arg-type"}
    assert "Too many positional arguments" in stdout


def test_mypy_types_a_decorator_that_supplies_an_argument(tmp_path: Path) -> None:
    stdout, status = _run(_CONCATENATE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"call-arg", "arg-type"}
    assert stdout.count("error:") == 2
    assert 'Too many arguments for "render"' in stdout


def test_mypy_reports_a_class_decorator_that_forgets_to_return(tmp_path: Path) -> None:
    stdout, status = _run(_CLASS_DECORATOR_FORGETS_TO_RETURN, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"return"}
    assert "Missing return statement" in stdout


def test_mypy_keeps_the_class_type_through_document_kind(tmp_path: Path) -> None:
    stdout, status = _run(_CLASS_TYPE_THROUGH_DOCUMENT_KIND, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""
