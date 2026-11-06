"""The router: routing by zone, shadow mode and the root binding."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from refactor_or_rewrite.domain import Consignment, ConsignmentId, RateQuote
from refactor_or_rewrite.legacy import RateEngine
from refactor_or_rewrite.rating import quote
from refactor_or_rewrite.strangler import MIGRATED_ZONES, Mismatch, Router, quote_routed

if TYPE_CHECKING:
    type Quoter = Callable[[Consignment], RateQuote]
    type Build = Callable[[str, str], Consignment]


def test_the_router_serves_migrated_zones_from_the_rewrite(
    refusing_quoter: Quoter, consignment_for: Build
) -> None:
    router = Router(refusing_quoter, quote, ("ASIA",))

    assert str(router(consignment_for("ASIA", "5")).total.amount) == "33.00"


def test_the_router_serves_other_zones_from_the_legacy_engine(
    refusing_quoter: Quoter, consignment_for: Build
) -> None:
    router = Router(RateEngine().quote, refusing_quoter, ("ASIA",))

    assert str(router(consignment_for("EU", "5")).total.amount) == "13.20"


def test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote(
    first_draft: Quoter, consignment_for: Build
) -> None:
    reports: list[Mismatch] = []
    router = Router(RateEngine().quote, first_draft, ("ASIA",), reports.append)

    served = router(consignment_for("EU", "5"))

    assert str(served.total.amount) == "13.20"
    assert reports == [Mismatch(ConsignmentId("CN-1"), "13.20", "27.50")]


def test_shadow_mode_reports_a_refusal_as_a_mismatch(consignment_for: Build) -> None:
    reports: list[Mismatch] = []
    router = Router(RateEngine().quote, quote, ("ASIA",), reports.append)

    served = router(consignment_for("AFRICA", "5"))

    assert str(served.total.amount) == "13.20"
    assert reports == [
        Mismatch(ConsignmentId("CN-1"), "13.20", "RatingError: no tariff for zone 'AFRICA'")
    ]


def test_shadow_mode_is_silent_when_the_engines_agree(consignment_for: Build) -> None:
    reports: list[Mismatch] = []
    router = Router(RateEngine().quote, quote, ("ASIA",), reports.append)

    router(consignment_for("EU", "0.5"))

    assert reports == []


def test_with_every_zone_migrated_the_legacy_engine_is_never_called(
    refusing_quoter: Quoter, consignment_for: Build
) -> None:
    router = Router(refusing_quoter, quote, ("EU", "ASIA"))

    assert [str(router(consignment_for(zone, "5")).total.amount) for zone in ("EU", "ASIA")] == [
        "13.20",
        "33.00",
    ]


def test_the_standard_router_migrates_asia_only() -> None:
    assert quote_routed.migrated == ("ASIA",)
    assert quote_routed.migrated == MIGRATED_ZONES
    assert quote_routed.rewrite is quote
