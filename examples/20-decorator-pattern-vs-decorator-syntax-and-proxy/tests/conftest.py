"""Fixtures. The forwarding proxy, a comparison form, lives here as a fixture parameter so that it
runs the same behaviour table as the explicit proxy in the model code."""

from collections import Counter
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import pytest
from decorator_proxy.domain import (
    CarrierQuote,
    CarrierTimeoutError,
    Consignment,
    ConsignmentId,
    Money,
    Weight,
)
from decorator_proxy.proxy import CarrierGateway, CarrierGatewayProxy

QUOTED = CarrierQuote("AIRCO", Money(Decimal("48.00"), "EUR"))


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(id=ConsignmentId("CN-1"), weight=Weight(Decimal(10)), destination="NLRTM")


@pytest.fixture
def quoted() -> CarrierQuote:
    """What every scripted gateway answers once it stops timing out."""
    return QUOTED


@pytest.fixture
def calls() -> Counter[str]:
    """How often each gateway method was called. Fills as the test runs."""
    return Counter()


class ScriptedGateway:
    """Times out on the first ``failures`` quotes, then answers. No clock is involved."""

    def __init__(self, failures: int, calls: Counter[str]) -> None:
        self._failures = failures
        self._calls = calls

    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        self._calls["quote"] += 1
        if self._calls["quote"] <= self._failures:
            raise CarrierTimeoutError(f"no answer for {consignment.id}")
        return QUOTED

    def book(self, consignment: Consignment, /) -> str:
        self._calls["book"] += 1
        return f"AC-{consignment.id}"


@pytest.fixture
def make_gateway(calls: Counter[str]) -> Callable[[int], CarrierGateway]:
    """Build a scripted gateway that times out on its first n quotes."""
    return lambda failures: ScriptedGateway(failures, calls)


# Comparison: a proxy that forwards what it does not define. It caches `quote` as the explicit
# proxy does, so that the two forms share one table.
class _ForwardingGatewayProxy:
    def __init__(self, inner: CarrierGateway) -> None:
        self._inner = inner
        self._quotes: dict[Consignment, CarrierQuote] = {}

    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        if consignment not in self._quotes:
            self._quotes[consignment] = self._inner.quote(consignment)
        return self._quotes[consignment]

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._inner, name)


@pytest.fixture(params=["explicit", "forwarding"])
def make_proxy(request: pytest.FixtureRequest) -> Callable[[CarrierGateway], CarrierGateway]:
    """Wrap a gateway in the parametrised proxy form."""
    if request.param == "explicit":
        return CarrierGatewayProxy
    return _ForwardingGatewayProxy


@pytest.fixture
def explicit_proxy(make_gateway: Callable[[int], CarrierGateway]) -> CarrierGateway:
    return CarrierGatewayProxy(make_gateway(0))


@pytest.fixture
def forwarding_proxy(make_gateway: Callable[[int], CarrierGateway]) -> Any:
    """Typed `Any`, because that is what the form hands its callers."""
    return _ForwardingGatewayProxy(make_gateway(0))
