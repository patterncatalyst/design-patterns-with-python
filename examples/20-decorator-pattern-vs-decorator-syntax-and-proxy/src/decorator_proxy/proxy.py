"""Proxy: the gateway's own interface, with access to it controlled."""

from typing import Protocol

from decorator_proxy.domain import CarrierQuote, Consignment


class CarrierGateway(Protocol):
    def quote(self, consignment: Consignment, /) -> CarrierQuote: ...

    def book(self, consignment: Consignment, /) -> str: ...


class CarrierGatewayProxy:
    """Asks the gateway for each consignment's quote once, and forwards every booking.

    The cache is a plain dict and is not safe to share between threads.
    """

    def __init__(self, inner: CarrierGateway) -> None:
        self._inner = inner
        self._quotes: dict[Consignment, CarrierQuote] = {}

    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        if consignment not in self._quotes:
            self._quotes[consignment] = self._inner.quote(consignment)
        return self._quotes[consignment]

    def book(self, consignment: Consignment, /) -> str:
        return self._inner.book(consignment)
