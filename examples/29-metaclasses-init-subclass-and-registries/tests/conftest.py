"""Fixtures. The comparison form lives here as a fixture parameter so that a metaclass registry
runs the same table of bookings and refusals as ``CarrierBase``. Importing the two carrier modules
once makes the in-process registry exactly AIRCO and FASTLINE for every test, and no test registers
a carrier in this process: every class a test defines is refused before it reaches the registry."""

from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

import pytest
from carrier_registry import airco, fastline  # noqa: F401  (imported for the registration)
from carrier_registry.carriers import (
    CarrierBase,
    CarrierRegistrationError,
    ConsignmentId,
    DuplicateCarrierError,
    gateway_for,
)

_META_CARRIERS: dict[str, _CarrierMeta] = {}


class _CarrierMeta(ABCMeta):
    """The comparison: the same four rules as ``CarrierBase.__init_subclass__``, in a metaclass."""

    code: str

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
        /,
        *,
        code: str | None = None,
    ) -> _CarrierMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        if cls.__abstractmethods__:
            if code is not None:
                raise CarrierRegistrationError(f"{name} is abstract and cannot take code {code!r}")
            return cls
        if code is None:
            raise CarrierRegistrationError(f"{name} is concrete and needs a code")
        if code in _META_CARRIERS:
            raise DuplicateCarrierError(
                f"carrier code {code!r} is already registered to {_META_CARRIERS[code].__name__}"
            )
        cls.code = code
        _META_CARRIERS[code] = cls
        return cls

    def __contains__(cls, code: object) -> bool:
        return code in _META_CARRIERS

    def __iter__(cls) -> Iterator[str]:
        return iter(sorted(_META_CARRIERS))

    def __len__(cls) -> int:
        return len(_META_CARRIERS)


class _MetaCarrierBase(metaclass=_CarrierMeta):
    @abstractmethod
    def book(self, consignment_id: ConsignmentId, /) -> str: ...


class _MetaFastlineGateway(_MetaCarrierBase, code="FASTLINE"):
    def book(self, consignment_id: ConsignmentId, /) -> str:
        return f"FL-{consignment_id}"


class _MetaAircoGateway(_MetaCarrierBase, code="AIRCO"):
    def book(self, consignment_id: ConsignmentId, /) -> str:
        return f"AC-{consignment_id}"


class RegistryForm(Protocol):
    """What the shared table needs from a registry: a base to subclass, codes and a booking."""

    @property
    def base(self) -> type: ...

    def codes(self) -> list[str]: ...

    def book(self, code: str, consignment_id: ConsignmentId, /) -> str: ...


@dataclass(frozen=True, slots=True)
class _InitSubclassForm:
    base: type = CarrierBase

    def codes(self) -> list[str]:
        return sorted(CarrierBase.registry)

    def book(self, code: str, consignment_id: ConsignmentId, /) -> str:
        return gateway_for(code).book(consignment_id)


@dataclass(frozen=True, slots=True)
class _MetaclassForm:
    base: type = _MetaCarrierBase

    def codes(self) -> list[str]:
        return sorted(_META_CARRIERS)

    def book(self, code: str, consignment_id: ConsignmentId, /) -> str:
        booked: str = _META_CARRIERS[code]().book(consignment_id)
        return booked


@pytest.fixture(params=["init_subclass", "metaclass"])
def registry_form(request: pytest.FixtureRequest) -> RegistryForm:
    """``CarrierBase`` (``__init_subclass__``) or ``_MetaCarrierBase`` (a metaclass)."""
    if request.param == "init_subclass":
        return _InitSubclassForm()
    return _MetaclassForm()


@pytest.fixture
def meta_carrier_base() -> type[_MetaCarrierBase]:
    """The metaclass-built base, for the class-level operators."""
    return _MetaCarrierBase
