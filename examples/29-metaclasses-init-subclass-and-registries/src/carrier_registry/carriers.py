"""The carrier base class and its registry, filled as each subclass is created."""

import inspect
from abc import ABC, abstractmethod
from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar, NewType

ConsignmentId = NewType("ConsignmentId", str)


class DuplicateCarrierError(Exception):
    """Two carrier classes claimed one code."""


class CarrierRegistrationError(TypeError):
    """A carrier class was declared with a code it may not have, or without one it needs."""


class UnknownCarrierError(LookupError):
    """No carrier is registered under the code."""


_CARRIERS: dict[str, type[CarrierBase]] = {}


class CarrierBase(ABC):
    """Root of the carrier gateways. A concrete subclass names its code as a class keyword.

    A carrier exists only once its module has been imported, because the class statement is what
    registers it.
    """

    registry: ClassVar[Mapping[str, type[CarrierBase]]] = MappingProxyType(_CARRIERS)
    code: ClassVar[str]

    def __init_subclass__(cls, *, code: str | None = None) -> None:
        """Register a concrete subclass under its code, or refuse the class.

        The signature forwards no extra keywords: this class is the root of the hierarchy and has
        no cooperating mixins, so a misspelt class keyword is a call error that mypy names. Every
        refusal happens before the insertion, so a refused class leaves the registry unchanged.
        """
        super().__init_subclass__()
        if inspect.isabstract(cls):
            if code is not None:
                raise CarrierRegistrationError(
                    f"{cls.__name__} is abstract and cannot take code {code!r}"
                )
            return
        if code is None:
            raise CarrierRegistrationError(f"{cls.__name__} is concrete and needs a code")
        if code in _CARRIERS:
            raise DuplicateCarrierError(
                f"carrier code {code!r} is already registered to {_CARRIERS[code].__name__}"
            )
        cls.code = code
        _CARRIERS[code] = cls

    @abstractmethod
    def book(self, consignment_id: ConsignmentId, /) -> str:
        """Book the consignment and return the carrier's reference."""


def gateway_for(code: str) -> CarrierBase:
    """Return a gateway for the registered carrier code."""
    try:
        gateway_class = CarrierBase.registry[code]
    except KeyError:
        raise UnknownCarrierError(f"unknown carrier {code!r}") from None
    return gateway_class()
