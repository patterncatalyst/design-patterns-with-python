"""PDP-013: self-registering carriers via ``__init_subclass__`` and via a metaclass."""

from abc import ABC, ABCMeta, abstractmethod
from inspect import isabstract
from typing import Any, ClassVar


class DuplicateCarrierError(ValueError):
    """Two carrier classes claimed the same code."""


class Carrier(ABC):
    """Base class: subclasses that pass ``code=...`` register themselves."""

    registry: ClassVar[dict[str, type[Carrier]]] = {}
    code: ClassVar[str]

    def __init_subclass__(cls, *, code: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if code is None:
            return  # intermediate base: not a carrier a customer can book
        if code in Carrier.registry:
            raise DuplicateCarrierError(
                f"carrier code {code!r} already used by {Carrier.registry[code].__name__}"
            )
        cls.code = code
        Carrier.registry[code] = cls

    @classmethod
    def create(cls, code: str) -> Carrier:
        return Carrier.registry[code]()

    @abstractmethod
    def quote_cents(self, kilograms: int) -> int: ...


class RoadCarrier(Carrier):
    """Intermediate class: shared behavior, no code, never registered."""

    def quote_cents(self, kilograms: int) -> int:
        return 500 + 12 * kilograms


class Northwind(RoadCarrier, code="NWD"):
    pass


class Meridian(Carrier, code="MRD"):
    def quote_cents(self, kilograms: int) -> int:
        return 900 + 8 * kilograms


# Equivalent metaclass registry -------------------------------------------------


class CarrierMeta(ABCMeta):
    """Metaclass registry. Registers every concrete class that passes ``code=...``."""

    registry: dict[str, type[MetaCarrier]]

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        code: str | None = None,
        **kwargs: Any,
    ) -> CarrierMeta:
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if code is None:
            return cls
        if isabstract(cls):
            # Only a metaclass can see this: __init_subclass__ runs before ABCMeta
            # has computed __abstractmethods__.
            raise TypeError(f"{name} declares code {code!r} but is still abstract")
        registry = mcs.registry
        if code in registry:
            raise DuplicateCarrierError(
                f"carrier code {code!r} already used by {registry[code].__name__}"
            )
        cls.code = code  # type: ignore[attr-defined]
        registry[code] = cls  # type: ignore[assignment]
        return cls


CarrierMeta.registry = {}


class MetaCarrier(metaclass=CarrierMeta):
    code: ClassVar[str]

    @abstractmethod
    def quote_cents(self, kilograms: int) -> int: ...


class MetaRoadCarrier(MetaCarrier):
    """Intermediate class: shared behavior, no code, never registered."""

    def quote_cents(self, kilograms: int) -> int:
        return 500 + 12 * kilograms


class MetaNorthwind(MetaRoadCarrier, code="NWD"):
    pass


class MetaMeridian(MetaCarrier, code="MRD"):
    def quote_cents(self, kilograms: int) -> int:
        return 900 + 8 * kilograms
