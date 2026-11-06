"""A strangler-style router: it sends each zone to the legacy engine or to the rewrite.

It routes calls and converts no interface, so it is not the Adapter pattern. It is transitional
code: once every zone is migrated, the router and the legacy engine can be deleted.
"""

from collections.abc import Callable, Container
from dataclasses import dataclass

from refactor_or_rewrite.domain import Consignment, ConsignmentId, RateQuote, RatingError
from refactor_or_rewrite.legacy import RateEngine
from refactor_or_rewrite.rating import quote

type RateQuoter = Callable[[Consignment], RateQuote]


@dataclass(frozen=True, slots=True)
class Mismatch:
    """What each engine said for one consignment: an amount, or the refusal."""

    consignment_id: ConsignmentId
    legacy: str
    rewrite: str


@dataclass(frozen=True, slots=True)
class Router:
    """Serve migrated zones from the rewrite and every other zone from the legacy engine.

    With ``report`` set, the rewrite also runs on the zones it has not taken over. Its answer is
    compared with the legacy one and never served. Only a ``RatingError`` from the rewrite is
    caught: an error from the legacy engine propagates, because that engine is the one serving.
    """

    legacy: RateQuoter
    rewrite: RateQuoter
    migrated: Container[str]
    report: Callable[[Mismatch], None] | None = None

    def __call__(self, consignment: Consignment) -> RateQuote:
        if consignment.zone in self.migrated:
            return self.rewrite(consignment)
        served = self.legacy(consignment)
        if self.report is not None:
            self._compare(consignment, served, self.report)
        return served

    def _compare(
        self, consignment: Consignment, served: RateQuote, report: Callable[[Mismatch], None]
    ) -> None:
        try:
            shadow = str(self.rewrite(consignment).total.amount)
        except RatingError as error:
            shadow = f"RatingError: {error}"
        if shadow != str(served.total.amount):
            report(Mismatch(consignment.id, str(served.total.amount), shadow))


MIGRATED_ZONES = ("ASIA",)

quote_routed = Router(RateEngine().quote, quote, MIGRATED_ZONES)
