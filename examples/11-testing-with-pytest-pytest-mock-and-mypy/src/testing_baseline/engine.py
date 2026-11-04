"""Pick the cheapest carrier, deterministically, and book only that one."""

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta

from testing_baseline.carriers import CarrierGateway, CarrierQuote, CarrierTimeoutError
from testing_baseline.domain import Consignment, ConsignmentId, Money, RatingError

VALIDITY_VARIABLE = "RATE_QUOTE_VALIDITY_MINUTES"
DEFAULT_VALIDITY_MINUTES = 30


@dataclass(frozen=True, slots=True)
class RateQuote:
    """The winning price, how long it holds and which carriers did not answer."""

    consignment_id: ConsignmentId
    carrier: str
    total: Money
    valid_until: datetime
    skipped: tuple[str, ...]


class RateEngine:
    """Ask every carrier, skip the ones that time out and keep the cheapest answer."""

    def __init__(
        self,
        gateways: Mapping[str, CarrierGateway],
        *,
        clock: Callable[[], datetime],
        validity: timedelta,
    ) -> None:
        self._gateways = gateways
        self._clock = clock
        self._validity = validity

    def _choose(self, consignment: Consignment) -> tuple[str, RateQuote]:
        answers: list[tuple[str, CarrierQuote]] = []
        skipped: list[str] = []
        for code in sorted(self._gateways):
            try:
                answers.append((code, self._gateways[code].quote(consignment)))
            except CarrierTimeoutError:
                skipped.append(code)
        if not answers:
            raise RatingError("no carrier answered")
        code, best = min(answers, key=lambda answer: (answer[1].amount, answer[1].carrier))
        return code, RateQuote(
            consignment_id=consignment.id,
            carrier=best.carrier,
            total=best.amount,
            valid_until=self._clock() + self._validity,
            skipped=tuple(skipped),
        )

    def best_quote(self, consignment: Consignment) -> RateQuote:
        return self._choose(consignment)[1]

    def book_best(self, consignment: Consignment) -> str:
        """Book the winner and nobody else."""
        code, _quote = self._choose(consignment)
        return self._gateways[code].book(consignment)


def validity_from_env(environ: Mapping[str, str] = os.environ) -> timedelta:
    """How long a quote holds, from `RATE_QUOTE_VALIDITY_MINUTES` (default 30 minutes)."""
    raw = environ.get(VALIDITY_VARIABLE)
    if raw is None:
        return timedelta(minutes=DEFAULT_VALIDITY_MINUTES)
    if not raw.isdecimal() or int(raw) <= 0:
        raise ValueError(f"{VALIDITY_VARIABLE} must be a positive integer, got {raw!r}")
    return timedelta(minutes=int(raw))
