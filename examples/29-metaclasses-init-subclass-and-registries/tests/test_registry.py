import json
import subprocess
import sys
import types
from abc import ABC, abstractmethod
from inspect import isabstract
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from carrier_registry.airco import AircoGateway
from carrier_registry.carriers import (
    CarrierBase,
    CarrierRegistrationError,
    ConsignmentId,
    DuplicateCarrierError,
    UnknownCarrierError,
    gateway_for,
)
from carrier_registry.fastline import FastlineGateway

if TYPE_CHECKING:
    from conftest import RegistryForm

_SRC = Path(__file__).resolve().parents[1] / "src"

BOOKING_ROWS = [("FASTLINE", "FL-CN-1"), ("AIRCO", "AC-CN-1")]

# (id, keywords, concrete, exception, message pattern)
REFUSAL_ROWS = [
    (
        "duplicate",
        {"code": "FASTLINE"},
        True,
        DuplicateCarrierError,
        "'FASTLINE' is already registered to",
    ),
    ("concrete-without-code", {}, True, CarrierRegistrationError, "is concrete and needs a code"),
    (
        "abstract-with-code",
        {"code": "HALF"},
        False,
        CarrierRegistrationError,
        "is abstract and cannot take code 'HALF'",
    ),
    ("unknown-keyword", {"cod": "X"}, True, TypeError, "unexpected keyword argument 'cod'"),
]

_ALL_CODES = ["AIRCO", "FASTLINE"]

_PRELUDE = f"""
import json, sys
sys.path.insert(0, {str(_SRC)!r})
"""

_IMPORT_ORDER = (
    _PRELUDE
    + """
import carrier_registry.carriers as carriers
steps = [sorted(carriers.CarrierBase.registry)]
import carrier_registry.airco
steps.append(sorted(carriers.CarrierBase.registry))
import carrier_registry.fastline
steps.append(sorted(carriers.CarrierBase.registry))
sys.stdout.write(json.dumps(steps))
"""
)

_UNDER_AN_INTERMEDIATE = (
    _PRELUDE
    + """
from abc import abstractmethod
from carrier_registry.carriers import CarrierBase


class Intermediate(CarrierBase):
    @abstractmethod
    def track(self, reference: str, /) -> str: ...


class Express(Intermediate, code="FASTLINE"):
    def book(self, consignment_id, /):
        return "EX-" + consignment_id

    def track(self, reference, /):
        return reference


holder = CarrierBase.registry["FASTLINE"]
sys.stdout.write(json.dumps([sorted(CarrierBase.registry), holder.__name__]))
"""
)


def _run_isolated(code: str) -> object:
    """Run code in a fresh interpreter, so import order and test order cannot matter."""
    done = subprocess.run(
        [sys.executable, "-I", "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def _define(base: type, name: str, *, concrete: bool, **keywords: str) -> type:
    """Create a subclass with ``types.new_class``, so the keywords are data."""

    def body(namespace: dict[str, object]) -> None:
        if concrete:
            namespace["book"] = lambda self, consignment_id, /: "XX-" + consignment_id

    return types.new_class(name, (base,), dict(keywords), body)


@pytest.mark.parametrize(("code", "expected"), BOOKING_ROWS)
def test_every_registry_form_books_through_the_registered_carrier(
    registry_form: RegistryForm, code: str, expected: str
) -> None:
    assert registry_form.book(code, ConsignmentId("CN-1")) == expected


@pytest.mark.parametrize(
    ("keywords", "concrete", "error", "message"),
    [row[1:] for row in REFUSAL_ROWS],
    ids=[row[0] for row in REFUSAL_ROWS],
)
def test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry(
    registry_form: RegistryForm,
    keywords: dict[str, str],
    concrete: bool,
    error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error, match=message):
        _define(registry_form.base, "Refused", concrete=concrete, **keywords)
    assert registry_form.codes() == _ALL_CODES


def test_the_registry_maps_each_code_to_its_gateway_class() -> None:
    mapping = sorted((code, cls.__name__) for code, cls in CarrierBase.registry.items())
    assert mapping == [("AIRCO", "AircoGateway"), ("FASTLINE", "FastlineGateway")]
    assert FastlineGateway.code == "FASTLINE"
    assert AircoGateway.code == "AIRCO"


def test_gateway_for_books_with_the_registered_carrier() -> None:
    gateway = gateway_for("AIRCO")
    assert type(gateway) is AircoGateway
    assert gateway.book(ConsignmentId("CN-1")) == "AC-CN-1"


def test_an_unknown_code_raises_unknown_carrier_error() -> None:
    with pytest.raises(UnknownCarrierError, match="unknown carrier 'NOPE'") as caught:
        gateway_for("NOPE")
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__


def test_the_carrier_registry_is_a_read_only_view() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        CarrierBase.registry["FASTLINE"] = AircoGateway  # type: ignore[index]
    assert CarrierBase.registry["FASTLINE"] is FastlineGateway


def test_a_duplicate_code_keeps_the_first_class() -> None:
    with pytest.raises(DuplicateCarrierError, match="registered to FastlineGateway"):
        _define(CarrierBase, "Another", concrete=True, code="FASTLINE")
    assert CarrierBase.registry["FASTLINE"] is FastlineGateway


def test_an_abstract_intermediate_class_is_not_registered() -> None:
    class Intermediate(CarrierBase):
        @abstractmethod
        def track(self, reference: str, /) -> str: ...

    assert isabstract(Intermediate)
    assert sorted(CarrierBase.registry) == _ALL_CODES


def test_a_concrete_class_without_a_code_is_refused() -> None:
    with pytest.raises(CarrierRegistrationError, match="Forgot is concrete and needs a code"):
        _define(CarrierBase, "Forgot", concrete=True)
    assert sorted(CarrierBase.registry) == _ALL_CODES


def test_isabstract_sees_abstractness_inside_init_subclass() -> None:
    seen: list[tuple[str, bool, bool]] = []

    class Root(ABC):
        def __init_subclass__(cls) -> None:
            super().__init_subclass__()
            seen.append((cls.__name__, isabstract(cls), hasattr(cls, "__abstractmethods__")))

        @abstractmethod
        def book(self, consignment_id: ConsignmentId, /) -> str: ...

    class Mid(Root): ...

    class Conc(Mid):
        def book(self, consignment_id: ConsignmentId, /) -> str:
            return consignment_id

    assert seen == [("Mid", True, False), ("Conc", False, False)]
    assert isabstract(Mid)
    assert not isabstract(Conc)


def test_set_name_runs_before_init_subclass_and_a_class_decorator_after() -> None:
    log: list[str] = []

    class Marker:
        def __set_name__(self, owner: type, name: str) -> None:
            log.append("__set_name__")

    class Root:
        def __init_subclass__(cls) -> None:
            super().__init_subclass__()
            log.append("__init_subclass__")

    def decorate[T: type](cls: T) -> T:
        log.append("decorator")
        return cls

    @decorate
    class Sub(Root):
        field = Marker()

    assert log == ["__set_name__", "__init_subclass__", "decorator"]
    assert isinstance(Sub.field, Marker)


def test_a_forgotten_manual_registration_leaves_the_carrier_unavailable() -> None:
    class Fastline:
        def book(self, consignment_id: ConsignmentId, /) -> str:
            return f"FL-{consignment_id}"

    class Airco:
        def book(self, consignment_id: ConsignmentId, /) -> str:
            return f"AC-{consignment_id}"

    manual = {"FASTLINE": Fastline}  # AIRCO was never added
    assert manual["FASTLINE"]().book(ConsignmentId("CN-1")) == "FL-CN-1"
    with pytest.raises(KeyError, match="AIRCO"):
        manual["AIRCO"]()
    assert Airco().book(ConsignmentId("CN-1")) == "AC-CN-1"


def test_a_carrier_module_registers_only_when_it_is_imported() -> None:
    assert _run_isolated(_IMPORT_ORDER) == [[], ["AIRCO"], ["AIRCO", "FASTLINE"]]


def test_a_concrete_carrier_under_an_abstract_intermediate_registers() -> None:
    assert _run_isolated(_UNDER_AN_INTERMEDIATE) == [["FASTLINE"], "Express"]
