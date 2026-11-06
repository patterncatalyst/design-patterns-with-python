"""Fixtures: the `step` fixture wires the same carrier answers into each form of the engine.

Each param is one form of the rating engine. A form takes the answers the two carriers give and
returns a function that quotes a consignment, with a record of the carrier calls it made. The
legacy form takes no parameters, so a namespace patch is its only enabling point. That is the one
place a patch appears in these tests.
"""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from functools import partial
from typing import override

import pytest
from dependency_breaking import airco, legacy, parameterised, wrapped
from dependency_breaking.domain import (
    CarrierTimeoutError,
    Consignment,
    ConsignmentId,
    Money,
    RateQuote,
)
from dependency_breaking.fastline import request_quote
from dependency_breaking.rating import quote
from dependency_breaking.wrapped import CarrierQuoter

type QuoteFor = Callable[[Consignment], RateQuote]
type Calls = list[tuple[str, str, str]]
type Step = Callable[[CarrierAnswers], tuple[QuoteFor, Calls]]


@dataclass(frozen=True, slots=True)
class CarrierAnswers:
    """What the two carriers answer: a FASTLINE price, AIRCO cents, or a FASTLINE timeout."""

    fastline_price: Decimal
    airco_cents: int
    fastline_error: str | None = None


def _fakes(
    answers: CarrierAnswers,
) -> tuple[Callable[[str, Decimal], Decimal], Callable[..., int], Calls]:
    """Two SDK-level fakes that answer as told and record every call as strings."""
    calls: Calls = []

    def fastline_fake(zone: str, weight_kg: Decimal) -> Decimal:
        calls.append(("FASTLINE", zone, str(weight_kg)))
        if answers.fastline_error is not None:
            raise CarrierTimeoutError(answers.fastline_error)
        return answers.fastline_price

    def airco_fake(*, destination: str, grams: int) -> int:
        calls.append(("AIRCO", destination, str(grams)))
        return answers.airco_cents

    return fastline_fake, airco_fake, calls


class _ExtractedCallsRateEngine:
    """The legacy body with its two SDK calls moved into methods a subclass can override."""

    def __init__(self, *, margin: Decimal = legacy.MARGIN) -> None:
        self._margin = margin

    def _fastline_quote(self, zone: str, weight_kg: Decimal) -> Decimal:
        return request_quote(zone, weight_kg)

    def _airco_price(self, zone: str, grams: int) -> int:
        return airco.price(destination=zone, grams=grams)

    def quote(self, consignment: Consignment) -> RateQuote:
        fastline_price = self._fastline_quote(consignment.zone, consignment.weight_kg)
        airco_cents = self._airco_price(consignment.zone, int(consignment.weight_kg * 1000))
        prices = {"AIRCO": Decimal(airco_cents) / 100, "FASTLINE": fastline_price}
        code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
        total = (cheapest * self._margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, code, Money(total))


class _FakeCarrierRateEngine(_ExtractedCallsRateEngine):
    """Subclass and override: both carrier calls forward to fakes."""

    def __init__(
        self,
        fastline_fake: Callable[[str, Decimal], Decimal],
        airco_fake: Callable[..., int],
    ) -> None:
        super().__init__()
        self._fastline_fake = fastline_fake
        self._airco_fake = airco_fake

    @override
    def _fastline_quote(self, zone: str, weight_kg: Decimal) -> Decimal:
        return self._fastline_fake(zone, weight_kg)

    @override
    def _airco_price(self, zone: str, grams: int) -> int:
        return self._airco_fake(destination=zone, grams=grams)


class _GramsRoundedRateEngine(parameterised.RateEngine):
    """A mutant: grams are rounded where the engine truncates them."""

    @override
    def quote(self, consignment: Consignment) -> RateQuote:
        fastline_price = self._fastline_quote(consignment.zone, consignment.weight_kg)
        airco_cents = self._airco_price(
            destination=consignment.zone, grams=round(consignment.weight_kg * 1000)
        )
        prices = {"AIRCO": Decimal(airco_cents) / 100, "FASTLINE": fastline_price}
        code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
        total = (cheapest * self._margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, code, Money(total))


class _HalfEvenRateEngine(parameterised.RateEngine):
    """A mutant: the margin is rounded half to even where the engine rounds half up."""

    @override
    def quote(self, consignment: Consignment) -> RateQuote:
        fastline_price = self._fastline_quote(consignment.zone, consignment.weight_kg)
        airco_cents = self._airco_price(
            destination=consignment.zone, grams=int(consignment.weight_kg * 1000)
        )
        prices = {"AIRCO": Decimal(airco_cents) / 100, "FASTLINE": fastline_price}
        code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
        total = (cheapest * self._margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        return RateQuote(consignment.id, code, Money(total))


def _legacy_step(request: pytest.FixtureRequest) -> Step:
    # The only patch in these tests: the legacy engine takes no parameters, so the names it
    # looks up in its own module are the only enabling point.
    monkeypatch: pytest.MonkeyPatch = request.getfixturevalue("monkeypatch")

    def build(answers: CarrierAnswers) -> tuple[QuoteFor, Calls]:
        fastline_fake, airco_fake, calls = _fakes(answers)
        monkeypatch.setattr("dependency_breaking.legacy.request_quote", fastline_fake)
        monkeypatch.setattr(airco, "price", airco_fake)
        return legacy.RateEngine().quote, calls

    return build


def _parameterised_step(answers: CarrierAnswers) -> tuple[QuoteFor, Calls]:
    fastline_fake, airco_fake, calls = _fakes(answers)
    engine = parameterised.RateEngine(fastline_quote=fastline_fake, airco_price=airco_fake)
    return engine.quote, calls


def _wrapped_step(answers: CarrierAnswers) -> tuple[QuoteFor, Calls]:
    fastline_fake, airco_fake, calls = _fakes(answers)
    engine = wrapped.RateEngine(
        fastline=fastline_fake, airco=partial(wrapped.airco_quote, price=airco_fake)
    )
    return engine.quote, calls


def _function_step(answers: CarrierAnswers) -> tuple[QuoteFor, Calls]:
    fastline_fake, airco_fake, calls = _fakes(answers)
    quoters: dict[str, CarrierQuoter] = {
        "FASTLINE": fastline_fake,
        "AIRCO": partial(wrapped.airco_quote, price=airco_fake),
    }
    return partial(quote, quoters=quoters), calls


def _subclass_step(answers: CarrierAnswers) -> tuple[QuoteFor, Calls]:
    fastline_fake, airco_fake, calls = _fakes(answers)
    return _FakeCarrierRateEngine(fastline_fake, airco_fake).quote, calls


def _parameterised_mutant(engine_class: type[parameterised.RateEngine]) -> Step:
    def build(answers: CarrierAnswers) -> tuple[QuoteFor, Calls]:
        fastline_fake, airco_fake, calls = _fakes(answers)
        engine = engine_class(fastline_quote=fastline_fake, airco_price=airco_fake)
        return engine.quote, calls

    return build


@pytest.fixture(params=["legacy", "parameterised", "wrapped", "function", "subclass"])
def step(request: pytest.FixtureRequest) -> Step:
    """One form of the engine, wired to the same SDK-level fakes."""
    match request.param:
        case "legacy":
            return _legacy_step(request)
        case "parameterised":
            return _parameterised_step
        case "wrapped":
            return _wrapped_step
        case "function":
            return _function_step
        case "subclass":
            return _subclass_step
        case other:
            raise AssertionError(other)


@pytest.fixture
def mutant_steps() -> dict[str, Step]:
    """Two engines that differ from the real one in one rule each."""
    return {
        "grams-rounded": _parameterised_mutant(_GramsRoundedRateEngine),
        "half-even": _parameterised_mutant(_HalfEvenRateEngine),
    }


@pytest.fixture
def carrier_answers() -> type[CarrierAnswers]:
    return CarrierAnswers


@pytest.fixture
def extracted_calls_engine() -> type[_ExtractedCallsRateEngine]:
    return _ExtractedCallsRateEngine


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(ConsignmentId("CN-1"), "EU", Decimal("12.5"))
