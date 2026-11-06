from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from dependency_breaking import legacy, parameterised
from dependency_breaking.domain import CarrierTimeoutError, Consignment
from dependency_breaking.rating import STANDARD_QUOTERS, quote, quote_standard
from dependency_breaking.wrapped import airco_quote

if TYPE_CHECKING:
    from conftest import _ExtractedCallsRateEngine


def test_the_legacy_engine_needs_a_patch_to_reach_a_fake(consignment: Consignment) -> None:
    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer"):
        legacy.RateEngine().quote(consignment)


def test_a_parameterised_engine_keeps_the_real_carriers_as_defaults(
    consignment: Consignment,
) -> None:
    def fastline_fake(zone: str, weight_kg: Decimal) -> Decimal:
        return Decimal("25.00")

    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer"):
        parameterised.RateEngine().quote(consignment)
    # AIRCO is forgotten: the default reaches the real SDK.
    with pytest.raises(CarrierTimeoutError, match="AIRCO did not answer"):
        parameterised.RateEngine(fastline_quote=fastline_fake).quote(consignment)


def test_airco_quote_converts_kilograms_and_cents() -> None:
    grams_seen: list[int] = []

    def airco_fake(*, destination: str, grams: int) -> int:
        grams_seen.append(grams)
        return 2800

    assert airco_quote("EU", Decimal("12.5"), price=airco_fake) == Decimal("28.00")
    assert grams_seen == [12500]


def test_the_function_form_needs_its_quoters(consignment: Consignment) -> None:
    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'quoters'"):
        quote(consignment)  # type: ignore[call-arg]


def test_standard_quoters_name_both_carriers() -> None:
    assert sorted(STANDARD_QUOTERS) == ["AIRCO", "FASTLINE"]
    with pytest.raises(TypeError, match="does not support item assignment"):
        STANDARD_QUOTERS["EXPRESS"] = STANDARD_QUOTERS["AIRCO"]  # type: ignore[index]


def test_quote_standard_binds_the_standard_quoters(consignment: Consignment) -> None:
    assert quote_standard.func is quote
    assert quote_standard.keywords == {"quoters": STANDARD_QUOTERS}
    with pytest.raises(CarrierTimeoutError, match="AIRCO did not answer"):
        quote_standard(consignment)


def test_a_misspelt_override_falls_through_to_the_real_carrier(
    consignment: Consignment, extracted_calls_engine: type[_ExtractedCallsRateEngine]
) -> None:
    # A base class taken from a fixture is a variable to mypy, so the subclass is unchecked.
    class Misspelt(extracted_calls_engine):  # type: ignore[valid-type, misc]
        def _fastline_quote(self, zone: str, weight_kg: Decimal) -> Decimal:
            return Decimal("25.00")

        def _airco_prices(self, zone: str, grams: int) -> int:
            return 2800

    with pytest.raises(CarrierTimeoutError, match="AIRCO did not answer"):
        Misspelt().quote(consignment)
