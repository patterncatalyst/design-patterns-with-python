"""Carrier lookup that may find nothing, and two ways to declare a gateway."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from typing import ClassVar, Protocol, override

from structural_typing.domain import BookingError, Consignment

ACCOUNT_DEFAULT = sentinel("ACCOUNT_DEFAULT")


class CarrierGateway(Protocol):
    """What a caller needs: book a consignment and get a carrier reference."""

    def book(self, consignment: Consignment, /) -> str: ...


class FastlineGateway:
    """Satisfies CarrierGateway by shape alone: no base class."""

    def book(self, consignment: Consignment, /) -> str:
        return f"FASTLINE:{consignment.id}"


class CarrierBase(ABC):
    """Shared code for carriers that declare themselves: references are built here."""

    code: ClassVar[str]

    def reference(self, consignment: Consignment) -> str:
        return f"{self.code}:{consignment.id}"

    @abstractmethod
    def book(self, consignment: Consignment, /) -> str: ...


class AircoGateway(CarrierBase):
    """Inherits the shared code and still satisfies CarrierGateway by shape."""

    code = "AIRCO"

    @override
    def book(self, consignment: Consignment, /) -> str:
        return self.reference(consignment)


GATEWAYS: Mapping[str, Callable[[], CarrierGateway]] = frozendict(
    FASTLINE=FastlineGateway, AIRCO=AircoGateway
)


def find_gateway(code: str) -> CarrierGateway | None:
    """The gateway for a carrier code, or None when the code is unknown."""
    factory = GATEWAYS.get(code)
    return None if factory is None else factory()


def book_with(code: str, consignment: Consignment) -> str:
    """Book through the named carrier. An unknown carrier is a BookingError."""
    gateway = find_gateway(code)
    if gateway is None:
        raise BookingError(f"unknown carrier {code!r}")
    return gateway.book(consignment)


def carriers_to_ask(
    preferred: str | ACCOUNT_DEFAULT | None = ACCOUNT_DEFAULT,
    *,
    account_carrier: str = "FASTLINE",
) -> tuple[str, ...]:
    """Which carriers to quote. Not given means the account's carrier, None means all of them."""
    if preferred is ACCOUNT_DEFAULT:
        return (account_carrier,)
    if preferred is None:
        return tuple(sorted(GATEWAYS))
    if preferred in GATEWAYS:
        return (preferred,)
    raise BookingError(f"unknown carrier {preferred!r}")
