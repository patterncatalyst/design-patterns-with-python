"""Fixtures. The class-per-role engine, the accessor consignment and the service locator are the
comparison and the anti-patterns. They are over-built as the lesson, and they live here and never
in ``src``. The engine runs the same table of quotes as the rating function."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from functools import partial

import pytest
from pattern_misuse.rating import (
    STANDARD_TARIFF,
    Consignment,
    ConsignmentId,
    Money,
    RateQuote,
    RatingError,
    Tariff,
    quote,
)

type RatingForm = Callable[[Consignment], RateQuote]


class _ChargeVisitor(ABC):
    @abstractmethod
    def visit_flat_fee(self, charge: _FlatFeeCharge) -> None: ...

    @abstractmethod
    def visit_fuel(self, charge: _FuelSurcharge) -> None: ...


class _Charge(ABC):
    @abstractmethod
    def accept(self, visitor: _ChargeVisitor) -> None: ...


class _FlatFeeCharge(_Charge):
    def __init__(self, amount: Decimal) -> None:
        self.amount = amount

    def accept(self, visitor: _ChargeVisitor) -> None:
        visitor.visit_flat_fee(self)


class _FuelSurcharge(_Charge):
    def __init__(self, amount: Decimal) -> None:
        self.amount = amount

    def accept(self, visitor: _ChargeVisitor) -> None:
        visitor.visit_fuel(self)


class _NetTotalVisitor(_ChargeVisitor):
    def __init__(self) -> None:
        self.total = Decimal(0)

    def visit_flat_fee(self, charge: _FlatFeeCharge) -> None:
        self.total += charge.amount

    def visit_fuel(self, charge: _FuelSurcharge) -> None:
        self.total += charge.amount


class _PricingStrategy(ABC):
    @abstractmethod
    def charges(self, consignment: Consignment) -> list[_Charge]: ...


class _FlatFeeStrategy(_PricingStrategy):
    def __init__(self, tariff: Tariff) -> None:
        self._tariff = tariff

    def charges(self, consignment: Consignment) -> list[_Charge]:
        try:
            flat_fee = self._tariff.flat_fee_by_zone[consignment.zone]
        except KeyError:
            raise RatingError(f"no flat fee for zone {consignment.zone!r}") from None
        return [_FlatFeeCharge(flat_fee), _FuelSurcharge(self._tariff.fuel_fee)]


class _PricingStrategyFactory:
    def create(self, tariff: Tariff) -> _PricingStrategy:
        return _FlatFeeStrategy(tariff)


class _RateEngine:
    """The comparison: the same quote as ``quote``, through a factory, a strategy and a visitor."""

    def __init__(self, factory: _PricingStrategyFactory, tariff: Tariff) -> None:
        self._tariff = tariff
        self._strategy = factory.create(tariff)

    def get_tariff(self) -> Tariff:
        return self._tariff

    def quote(self, consignment: Consignment) -> RateQuote:
        visitor = _NetTotalVisitor()
        for charge in self._strategy.charges(consignment):
            charge.accept(visitor)
        net = visitor.total
        tax = (net * self.get_tariff().tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, Money(net + tax, self.get_tariff().currency))


class _RemoteAreaCharge(_Charge):
    """A new charge kind. Its visitor method is declared nowhere, which mypy reports."""

    def accept(self, visitor: _ChargeVisitor) -> None:
        visitor.visit_remote_area(self)  # type: ignore[attr-defined]


class _RemoteAreaStrategy(_FlatFeeStrategy):
    def charges(self, consignment: Consignment) -> list[_Charge]:
        return [*super().charges(consignment), _RemoteAreaCharge()]


class _RemoteAreaFactory(_PricingStrategyFactory):
    def create(self, tariff: Tariff) -> _PricingStrategy:
        return _RemoteAreaStrategy(tariff)


class _RemoteAreaVisitor(_ChargeVisitor):
    """The base after the new visit method is declared abstract."""

    @abstractmethod
    def visit_remote_area(self, charge: _RemoteAreaCharge) -> None: ...


class _NetTotalWithRemoteArea(_NetTotalVisitor, _RemoteAreaVisitor):
    """The concrete visitor that has not implemented the new method yet."""


class _AccessorConsignment:
    """A consignment with a getter and a setter for each field."""

    def __init__(self, consignment_id: ConsignmentId, zone: str) -> None:
        self._id = consignment_id
        self._zone = zone

    def get_id(self) -> ConsignmentId:
        return self._id

    def get_zone(self) -> str:
        return self._zone

    def set_zone(self, zone: str) -> None:
        self._zone = zone


def _quote_accessor(consignment: _AccessorConsignment, tariff: Tariff) -> RateQuote:
    return quote(Consignment(consignment.get_id(), consignment.get_zone()), tariff)


class _ServiceLocator:
    """A registry of services by name. The state is per instance, so nothing crosses tests."""

    def __init__(self) -> None:
        self._services: dict[str, object] = {}

    def register(self, name: str, service: object) -> None:
        self._services[name] = service

    def get(self, name: str) -> object:
        return self._services[name]


class _LocatedRateEngine:
    """An engine that finds its tariff in a locator when it quotes."""

    def __init__(self, locator: _ServiceLocator) -> None:
        self._locator = locator

    def quote(self, consignment: Consignment) -> RateQuote:
        tariff = self._locator.get("tariff")
        if not isinstance(tariff, Tariff):
            raise TypeError(f"expected a Tariff, got {type(tariff).__name__}")
        return quote(consignment, tariff)


@dataclass(frozen=True, slots=True)
class EngineParts:
    """The engine classes the measuring and extension tests use, handed over by a fixture."""

    engine: type[_RateEngine]
    factory: type[_PricingStrategyFactory]
    remote_area_factory: type[_RemoteAreaFactory]
    net_total_visitor: type[_NetTotalVisitor]
    net_total_with_remote_area: Callable[[], _NetTotalVisitor]


@pytest.fixture(params=["function", "engine"])
def rating_form(request: pytest.FixtureRequest) -> RatingForm:
    if request.param == "function":
        return partial(quote, tariff=STANDARD_TARIFF)
    return _RateEngine(_PricingStrategyFactory(), STANDARD_TARIFF).quote


@pytest.fixture
def engine() -> _RateEngine:
    return _RateEngine(_PricingStrategyFactory(), STANDARD_TARIFF)


@pytest.fixture
def engine_parts() -> EngineParts:
    return EngineParts(
        engine=_RateEngine,
        factory=_PricingStrategyFactory,
        remote_area_factory=_RemoteAreaFactory,
        net_total_visitor=_NetTotalVisitor,
        net_total_with_remote_area=_NetTotalWithRemoteArea,
    )


@pytest.fixture
def quote_accessor() -> Callable[[_AccessorConsignment], RateQuote]:
    return partial(_quote_accessor, tariff=STANDARD_TARIFF)


@pytest.fixture
def accessor_consignment() -> _AccessorConsignment:
    return _AccessorConsignment(ConsignmentId("CN-1"), "EU")


@pytest.fixture
def locator() -> _ServiceLocator:
    return _ServiceLocator()


@pytest.fixture
def located_engine(locator: _ServiceLocator) -> _LocatedRateEngine:
    return _LocatedRateEngine(locator)
