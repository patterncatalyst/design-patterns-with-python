import types
from abc import ABCMeta
from typing import TYPE_CHECKING, Protocol

import pytest
from carrier_registry.carriers import CarrierBase

if TYPE_CHECKING:
    from conftest import _MetaCarrierBase

_ALL_CODES = ["AIRCO", "FASTLINE"]


class _OtherMeta(type): ...


class _Compatible(ABCMeta): ...


class _TrackingProtocol(Protocol):
    def track(self, reference: str, /) -> str: ...


@pytest.mark.parametrize("base", [CarrierBase, _TrackingProtocol], ids=["abc", "protocol"])
def test_a_second_metaclass_conflicts_with_the_bases_metaclass(base: type) -> None:
    with pytest.raises(TypeError, match="metaclass conflict"):
        types.new_class("Conflicted", (base,), {"metaclass": _OtherMeta})
    assert sorted(CarrierBase.registry) == _ALL_CODES


def test_a_metaclass_derived_from_abcmeta_resolves_the_conflict() -> None:
    resolved = types.new_class("Resolved", (CarrierBase,), {"metaclass": _Compatible})
    assert type(resolved) is _Compatible
    assert sorted(CarrierBase.registry) == _ALL_CODES


def test_only_a_metaclass_gives_the_class_object_operators(
    meta_carrier_base: type[_MetaCarrierBase],
) -> None:
    assert "AIRCO" in meta_carrier_base
    assert list(meta_carrier_base) == _ALL_CODES
    assert len(meta_carrier_base) == 2
    with pytest.raises(TypeError, match="is not a container or iterable"):
        "AIRCO" in CarrierBase  # type: ignore[operator]  # noqa: B015
