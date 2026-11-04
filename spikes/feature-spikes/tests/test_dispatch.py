"""PDP-012 evidence: singledispatch on Python 3.15."""

import os
import textwrap
from dataclasses import dataclass
from functools import singledispatch
from pathlib import Path
from typing import Any

import pytest
from feature_spikes import dispatch
from feature_spikes.dispatch import (
    Container,
    HazmatDrum,
    Labeller,
    Pallet,
    Parcel,
    Ship,
    Truck,
    customs_label,
    handling,
    load_plan,
)
from mypy import api as mypy_api


def test_registered_by_annotation_picks_most_specific() -> None:
    assert customs_label(Pallet("P1", 3)) == "pallet P1 (3 layers)"
    assert customs_label(Container("C1", 2)) == "container C1 (2 TEU)"
    assert customs_label(HazmatDrum("D1", "UN1203")) == "HAZMAT UN1203 D1"


def test_unregistered_subclass_falls_back_to_base_registration() -> None:
    assert customs_label(Parcel("X1", 500)) == "general cargo X1"
    assert Parcel not in customs_label.registry


def test_union_annotation_registers_every_member() -> None:
    assert Pallet in handling.registry
    assert Parcel in handling.registry
    assert handling(Parcel("X1", 5)) == "forklift or hand sort"
    assert handling(Pallet("P1", 1)) == "forklift or hand sort"
    assert handling(Container("C1", 1)) == "standard handling"


def test_singledispatchmethod_dispatches_on_first_argument_after_self() -> None:
    labeller = Labeller("DOCK")
    assert labeller.render(Container("C1", 1)) == "DOCK: box C1"
    assert labeller.render(Parcel("X1", 1)) == "DOCK: loose X1"
    assert labeller.render(HazmatDrum("D1", "UN1")) == "DOCK: D1"


def test_open_extension_from_another_module() -> None:
    # This test module is not feature_spikes.dispatch. The registration below
    # extends the shared function without editing the module that defines it.
    @dataclass(frozen=True)
    class Reefer(Container):
        celsius: int

    assert dispatch.customs_label(Reefer("R1", 1, -18)) == "container R1 (1 TEU)"
    dispatch.customs_label.register(Reefer, lambda cargo: f"reefer {cargo.celsius}C")
    assert dispatch.customs_label(Reefer("R1", 1, -18)) == "reefer -18C"
    assert dispatch.customs_label(Container("C1", 1)) == "container C1 (1 TEU)"


def test_register_annotation_naming_later_class_fails_at_registration() -> None:
    # Since Python 3.14 annotation evaluation is deferred (PEP 649), but register() reads
    # them immediately, so a class defined further down is still unresolved.
    source = textwrap.dedent(
        """
        from functools import singledispatch

        @singledispatch
        def f(x: object) -> str:
            return "object"

        @f.register
        def _(x: Later) -> str:
            return "later"

        class Later: ...
        """
    )
    namespace: dict[str, Any] = {}
    with pytest.raises(TypeError, match="unresolved forward reference"):
        exec(source, namespace)


def test_register_annotation_works_once_class_exists_with_no_future_import() -> None:
    source = textwrap.dedent(
        """
        from functools import singledispatch

        @singledispatch
        def f(x: object) -> str:
            return "object"

        class Early: ...

        @f.register
        def _(x: Early) -> str:
            return "early"

        class Later: ...

        @f.register
        def _(x: "Later") -> str:  # a string works because Later now exists
            return "later"

        def explicit(x: object) -> str:
            return "explicit"

        f.register(Later, explicit)  # explicit class argument: later registration overrides
        """
    )
    namespace: dict[str, Any] = {}
    exec(source, namespace)
    assert namespace["f"](namespace["Early"]()) == "early"
    assert namespace["f"](namespace["Later"]()) == "explicit"
    assert "__future__" not in source


def test_register_string_annotation_for_not_yet_defined_name_fails() -> None:
    source = textwrap.dedent(
        """
        from functools import singledispatch

        @singledispatch
        def f(x: object) -> str:
            return "object"

        @f.register
        def _(x: "Later") -> str:
            return "later"

        class Later: ...
        """
    )
    with pytest.raises(TypeError, match="unresolved forward reference"):
        exec(source, {})


def test_dispatch_on_first_argument_then_match_on_second() -> None:
    box = Container("C1", 1)
    assert load_plan(box, Ship("Aurora")) == "crane C1 onto Aurora"
    assert load_plan(box, Truck("TR-1")) == "chassis C1 onto TR-1"
    assert load_plan(Parcel("X1", 1), Truck("TR-1")) == "hand-load X1"
    assert load_plan(Parcel("X1", 1), Ship("Aurora")) == "X1: parcels do not sail alone"
    assert load_plan(Pallet("P1", 1), Ship("Aurora")) == "P1: no plan for Pallet"


def _mypy(tmp_path: Path, source: str) -> tuple[str, int]:
    target = tmp_path / "snippet.py"
    target.write_text(textwrap.dedent(source))
    stdout, _stderr, status = mypy_api.run(["--strict", f"--cache-dir={os.devnull}", str(target)])
    return stdout.replace(str(target), "snippet.py"), status


SNIPPET_HEAD = """
    from dataclasses import dataclass
    from functools import singledispatch

    @dataclass(frozen=True)
    class Cargo:
        reference: str

    @dataclass(frozen=True)
    class Pallet(Cargo):
        layers: int

    @singledispatch
    def label(cargo: Cargo) -> str:
        return "general"
"""


def test_mypy_strict_accepts_annotation_and_union_registrations(tmp_path: Path) -> None:
    out, status = _mypy(
        tmp_path,
        SNIPPET_HEAD
        + """
    @dataclass(frozen=True)
    class Parcel(Cargo):
        grams: int

    @label.register
    def _(cargo: Pallet) -> str:
        return "pallet"

    @label.register
    def _(cargo: Pallet | Parcel) -> str:
        return "either"

    label(Pallet("P", 1))
    """,
    )
    assert status == 0, out


def test_mypy_flags_what_runtime_accepts(tmp_path: Path) -> None:
    out, status = _mypy(
        tmp_path,
        SNIPPET_HEAD
        + """
    @label.register
    def _(cargo: int) -> str:
        return "int"

    label(3)
    """,
    )
    assert status == 1
    assert 'Dispatch type "int" must be subtype of fallback function first argument "Cargo"' in out
    assert 'Argument 1 to "label" has incompatible type "int"; expected "Cargo"' in out
    # Runtime disagrees: the registration is legal and the call dispatches.
    runtime_label = singledispatch(lambda cargo: "fallback")
    runtime_label.register(int, lambda cargo: "int")
    assert runtime_label(3) == "int"


def test_mypy_checks_registered_return_type_against_fallback(tmp_path: Path) -> None:
    out, status = _mypy(
        tmp_path,
        SNIPPET_HEAD
        + """
    @label.register
    def _(cargo: Pallet) -> int:
        return 1
    """,
    )
    assert status == 1
    assert 'Argument 1 to "register" of "_SingleDispatchCallable" has incompatible type' in out


def test_mypy_does_not_flag_unregistered_subclass_or_object_fallback(tmp_path: Path) -> None:
    out, status = _mypy(
        tmp_path,
        """
        from functools import singledispatch

        @singledispatch
        def describe(value: object) -> str:
            return "something"

        @describe.register
        def _(value: int) -> str:
            return "int"

        describe(1.5)
        """,
    )
    assert status == 0, out
