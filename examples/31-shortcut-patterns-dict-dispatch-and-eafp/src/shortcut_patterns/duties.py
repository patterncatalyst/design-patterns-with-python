"""A duty-rate cache that other threads may evict from."""

from collections.abc import Callable, MutableMapping
from decimal import ROUND_HALF_UP, Decimal

from shortcut_patterns.declarations import CustomsDeclaration


class DutyRateCache:
    """Duty rates by HS code, loaded on a miss.

    ``rate_for`` reads the rate once. One read leaves no gap that separates a check from a use,
    so an eviction by another thread has nowhere to land. It does not make a miss load once:
    two threads that both miss both call ``load``.
    """

    def __init__(
        self,
        load: Callable[[str], Decimal],
        *,
        rates: MutableMapping[str, Decimal] | None = None,
    ) -> None:
        self._load = load
        self._rates: MutableMapping[str, Decimal] = {} if rates is None else rates

    def rate_for(self, hs_code: str) -> Decimal:
        try:
            return self._rates[hs_code]
        except KeyError:
            rate = self._load(hs_code)
            self._rates[hs_code] = rate
            return rate

    def evict(self, hs_code: str) -> None:
        """Forget a rate. An absent code is not an error."""
        self._rates.pop(hs_code, None)


def duty_for(declaration: CustomsDeclaration, cache: DutyRateCache) -> Decimal:
    """Duty owed: the declared value times the cached rate in percent, to the cent."""
    rate = cache.rate_for(declaration.hs_code)
    return (declaration.declared_value * rate / 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
