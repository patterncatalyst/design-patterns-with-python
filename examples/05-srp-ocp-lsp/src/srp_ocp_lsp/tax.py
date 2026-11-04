"""Destination tax: a rule is a callable, the table of rules is data."""

from collections.abc import Callable, Mapping
from decimal import ROUND_HALF_UP, Decimal
from types import MappingProxyType

from srp_ocp_lsp.domain import Money

type TaxRule = Callable[[Money], Money]


def percent(rate: Decimal) -> TaxRule:
    """A rule that taxes a net amount at ``rate`` percent, rounded half up to cents."""

    def rule(net: Money) -> Money:
        tax = net.amount * rate / Decimal(100)
        return Money(tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), net.currency)

    return rule


# Illustrative rates for the example, not statutory ones.
TAX_RULES: Mapping[str, TaxRule] = MappingProxyType(
    {
        "SG": percent(Decimal("9")),
        "NL": percent(Decimal("21")),
    }
)
