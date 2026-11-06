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


# The src model, type-checked only: a class keyword of the wrong type.
_WRONG_KEYWORD_TYPE = """
from carrier_registry.carriers import CarrierBase


class WrongType(CarrierBase, code=1): ...
"""

# The src model, type-checked only: a misspelt class keyword.
_MISSPELT_KEYWORD = """
from carrier_registry.carriers import CarrierBase


class Misspelt(CarrierBase, cod="X"): ...
"""

# Reduced model: a registry metaclass that takes a code keyword. It registers whatever it is given.
_META_REGISTRY = """
from abc import ABCMeta

REGISTRY: dict[object, str] = {}


class CarrierMeta(ABCMeta):
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
        /,
        *,
        code: str | None = None,
    ) -> CarrierMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        if code is not None:
            REGISTRY[code] = name
        return cls


class MetaBase(metaclass=CarrierMeta): ...


class Fastline(MetaBase, code=1): ...
"""

# Reduced model: a second metaclass under an ABC base.
_METACLASS_CONFLICT = """
from abc import ABC


class Other(type): ...


class Conflicted(ABC, metaclass=Other): ...
"""

# Reduced model: Self in a metaclass __new__, which is valid at run time.
_SELF_IN_META_NEW = """
from typing import Self


class CarrierMeta(type):
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, object], /) -> Self:
        return super().__new__(mcs, name, bases, namespace)


class Gateway(metaclass=CarrierMeta): ...
"""

# Reduced model: a registry of metaclass instances, and a call through it. The class definitions
# come first, so the run-time half can reuse them without the type-checker-only line.
_META_REGISTRY_CALL = """
from abc import ABCMeta

REGISTRY: dict[str, CarrierMeta] = {}


class CarrierMeta(ABCMeta):
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
        /,
        *,
        code: str | None = None,
    ) -> CarrierMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        if code is not None:
            REGISTRY[code] = cls
        return cls


class MetaBase(metaclass=CarrierMeta):
    def book(self, reference: str, /) -> str:
        return reference


class Fastline(MetaBase, code="F"): ...


"""
_CALLED_FROM_THE_REGISTRY = (
    _META_REGISTRY_CALL
    + """\
reveal_type(REGISTRY["F"]())
REGISTRY["F"]().bok("CN-1")
"""
)
_CALLED_AT_RUN_TIME = _META_REGISTRY_CALL + 'REGISTRY["F"]().bok("CN-1")\n'

# Reduced model: a metaclass __call__ that declares another return type.
_META_CALL = """
class Meta(type):
    def __call__(cls, *args: object, **kwargs: object) -> int:
        return 1


class G(metaclass=Meta):
    def __init__(self, reference: str) -> None:
        self.reference = reference


"""
_CALL_REVEALED = _META_CALL + 'reveal_type(G("x"))\n'
_CALL_AT_RUN_TIME = _META_CALL + 'result = G("x")\n'


def test_mypy_checks_the_type_of_a_class_keyword(tmp_path: Path) -> None:
    stdout, status = _run(_WRONG_KEYWORD_TYPE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'Argument "code" to "__init_subclass__" of "CarrierBase"' in stdout


def test_mypy_reports_a_misspelt_class_keyword(tmp_path: Path) -> None:
    stdout, status = _run(_MISSPELT_KEYWORD, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"call-arg"}
    assert 'did you mean "code"?' in stdout


def test_mypy_does_not_check_metaclass_class_keywords(tmp_path: Path) -> None:
    stdout, status = _run(_META_REGISTRY, tmp_path)

    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    namespace: dict[str, object] = {}
    exec(_META_REGISTRY, namespace)
    registry = namespace["REGISTRY"]
    assert isinstance(registry, dict)
    assert list(registry) == [1]


def test_mypy_reports_a_metaclass_conflict(tmp_path: Path) -> None:
    stdout, status = _run(_METACLASS_CONFLICT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"metaclass"}
    assert "Metaclass conflict" in stdout
    with pytest.raises(TypeError, match="metaclass conflict"):
        exec(_METACLASS_CONFLICT, {})


def test_mypy_refuses_self_in_a_metaclass_new(tmp_path: Path) -> None:
    stdout, status = _run(_SELF_IN_META_NEW, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"misc"}
    assert "Self type cannot be used in a metaclass" in stdout
    namespace: dict[str, object] = {}
    exec(_SELF_IN_META_NEW, namespace)
    assert "Gateway" in namespace


def test_mypy_types_a_class_called_from_a_metaclass_registry_as_any(tmp_path: Path) -> None:
    stdout, status = _run(_CALLED_FROM_THE_REGISTRY, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert 'Revealed type is "Any"' in stdout
    with pytest.raises(AttributeError, match="bok"):
        exec(_CALLED_AT_RUN_TIME, {})


def test_mypy_ignores_a_metaclass_call_return_type(tmp_path: Path) -> None:
    stdout, status = _run(_CALL_REVEALED, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert 'Revealed type is "__main__.G"' in stdout
    namespace: dict[str, object] = {}
    exec(_CALL_AT_RUN_TIME, namespace)
    assert namespace["result"] == 1
