"""PDP-013 evidence: __init_subclass__ registry versus metaclass registry."""

import os
import textwrap
from collections.abc import Iterator
from pathlib import Path

import pytest
from feature_spikes.registry import (
    Carrier,
    CarrierMeta,
    DuplicateCarrierError,
    Meridian,
    MetaCarrier,
    MetaMeridian,
    MetaNorthwind,
    MetaRoadCarrier,
    Northwind,
    RoadCarrier,
)
from mypy import api as mypy_api


@pytest.fixture(autouse=True)
def _restore_registries() -> Iterator[None]:
    carriers = dict(Carrier.registry)
    metas = dict(CarrierMeta.registry)
    yield
    Carrier.registry.clear()
    Carrier.registry.update(carriers)
    CarrierMeta.registry.clear()
    CarrierMeta.registry.update(metas)


def test_init_subclass_registers_concrete_classes_by_code() -> None:
    assert Carrier.registry == {"NWD": Northwind, "MRD": Meridian}
    assert Northwind.code == "NWD"
    assert Carrier.create("MRD").quote_cents(10) == 980


def test_metaclass_registers_concrete_classes_by_code() -> None:
    assert CarrierMeta.registry == {"NWD": MetaNorthwind, "MRD": MetaMeridian}
    assert MetaNorthwind.code == "NWD"
    assert CarrierMeta.registry["MRD"]().quote_cents(10) == 980


def test_intermediate_classes_are_not_registered() -> None:
    assert RoadCarrier not in Carrier.registry.values()
    assert MetaRoadCarrier not in CarrierMeta.registry.values()
    assert Northwind().quote_cents(10) == MetaNorthwind().quote_cents(10) == 620


def test_duplicate_code_is_rejected_by_init_subclass() -> None:
    with pytest.raises(DuplicateCarrierError, match="'NWD' already used by Northwind"):

        class Impostor(Carrier, code="NWD"):
            def quote_cents(self, kilograms: int) -> int:
                return 0

    assert Carrier.registry["NWD"] is Northwind


def test_duplicate_code_is_rejected_by_metaclass() -> None:
    with pytest.raises(DuplicateCarrierError, match="'NWD' already used by MetaNorthwind"):

        class Impostor(MetaCarrier, code="NWD"):
            def quote_cents(self, kilograms: int) -> int:
                return 0

    assert CarrierMeta.registry["NWD"] is MetaNorthwind


def test_abstract_base_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError, match="abstract"):
        Carrier()  # type: ignore[abstract]
    with pytest.raises(TypeError, match="abstract"):
        MetaCarrier()  # type: ignore[abstract]


def test_only_the_metaclass_can_see_abstractness_when_a_code_is_given() -> None:
    # __init_subclass__ runs inside type.__new__, before ABCMeta computes
    # __abstractmethods__, so it cannot tell an abstract class from a concrete one.
    class Stray(Carrier, code="STR"):
        pass

    assert Carrier.registry["STR"] is Stray
    with pytest.raises(TypeError, match="abstract"):
        Stray()  # type: ignore[abstract]

    with pytest.raises(TypeError, match="still abstract"):

        class MetaStray(MetaCarrier, code="STR"):
            pass

    assert "STR" not in CarrierMeta.registry


def test_unknown_keyword_reaches_object_init_subclass() -> None:
    with pytest.raises(TypeError, match="takes no keyword arguments"):

        class Odd(Carrier, code="ODD", flavour="x"):
            def quote_cents(self, kilograms: int) -> int:
                return 0

    assert "ODD" not in Carrier.registry


def test_unknown_code_lookup_raises_key_error() -> None:
    with pytest.raises(KeyError, match="ZZZ"):
        Carrier.create("ZZZ")


def _mypy(tmp_path: Path, source: str) -> tuple[str, int]:
    target = tmp_path / "snippet.py"
    target.write_text(textwrap.dedent(source))
    stdout, _stderr, status = mypy_api.run(["--strict", f"--cache-dir={os.devnull}", str(target)])
    return stdout.replace(str(target), "snippet.py"), status


def test_mypy_strict_accepts_both_registries_and_checks_code_keyword(tmp_path: Path) -> None:
    out, status = _mypy(
        tmp_path,
        """
        from feature_spikes.registry import Carrier, MetaCarrier

        class A(Carrier, code="AAA"):
            def quote_cents(self, kilograms: int) -> int:
                return 1

        class B(MetaCarrier, code="BBB"):
            def quote_cents(self, kilograms: int) -> int:
                return 1

        reveal_type(Carrier.registry)
        reveal_type(A.code)
        reveal_type(Carrier.create("AAA"))
        """,
    )
    assert status == 0, out
    assert "dict[str, type[feature_spikes.registry.Carrier]]" in out
    assert 'snippet.py:13: note: Revealed type is "str"' in out


def test_mypy_checks_init_subclass_keywords_but_not_metaclass_keywords(tmp_path: Path) -> None:
    out, status = _mypy(
        tmp_path,
        """
        from feature_spikes.registry import Carrier, MetaCarrier

        class A(Carrier, code=1):
            def quote_cents(self, kilograms: int) -> int:
                return 1

        class B(MetaCarrier, code=1, flavour="x"):
            def quote_cents(self, kilograms: int) -> int:
                return 1
        """,
    )
    # Friction: mypy validates class keywords against __init_subclass__ only.
    # With a metaclass it never consults the metaclass __new__ signature.
    assert status == 1
    assert (
        'snippet.py:4: error: Argument "code" to "__init_subclass__" of "Carrier" '
        'has incompatible type "int"; expected "str | None"' in out
    )
    assert "snippet.py:8" not in out
    assert "Found 1 error" in out


def test_mypy_allows_calling_abstract_type_values_from_the_registry(tmp_path: Path) -> None:
    # type[Carrier] values are callable even though Carrier is abstract: mypy
    # trusts that a registry only holds concrete classes. The runtime check is
    # the only guard, which is why the metaclass rejects abstract classes.
    out, status = _mypy(
        tmp_path,
        """
        from feature_spikes.registry import Carrier

        carrier = Carrier.registry["NWD"]()
        """,
    )
    assert status == 0, out
