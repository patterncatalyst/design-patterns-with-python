"""Audit: where a finished quote is reported."""

from collections.abc import Callable

from srp_ocp_lsp.domain import RateQuote

type AuditSink = Callable[[RateQuote], None]
