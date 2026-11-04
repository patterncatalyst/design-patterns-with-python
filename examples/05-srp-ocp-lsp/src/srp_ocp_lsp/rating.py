"""The coordinator: one quote from three collaborators."""

from collections.abc import Mapping

from srp_ocp_lsp.audit import AuditSink
from srp_ocp_lsp.domain import Consignment, RateQuote, RatingError
from srp_ocp_lsp.pricing import RateCalculator
from srp_ocp_lsp.tax import TaxRule


def quote(
    consignment: Consignment,
    *,
    calculator: RateCalculator,
    tax_rules: Mapping[str, TaxRule],
    audit: AuditSink,
) -> RateQuote:
    """Price the consignment, tax it by destination country, audit once and return the quote."""
    country = consignment.destination[:2]
    try:
        rule = tax_rules[country]
    except KeyError:
        raise RatingError(f"no tax rule for destination country {country!r}") from None
    net = calculator.price(consignment)
    result = RateQuote(consignment.id, net, rule(net))
    audit(result)
    return result
