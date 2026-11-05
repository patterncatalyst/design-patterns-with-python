"""Flyweights: one shared commodity per code, and one shared string per port code."""

import re
import sys
import weakref
from collections.abc import Mapping

from composite_flyweight.domain import Commodity, PortCall

# Illustrative HS codes: lithium-ion batteries, coffee (not roasted), cotton T-shirts.
CATALOGUE: Mapping[str, tuple[str, bool]] = frozendict(
    {
        "850760": ("lithium-ion batteries", True),
        "090111": ("coffee, not roasted", False),
        "610910": ("cotton T-shirts", False),
    }
)

_PORT_CODE = re.compile(r"[A-Z]{2}[A-Z2-9]{3}")


class UnknownCommodityError(LookupError):
    """A commodity code the catalogue does not list."""


class PortCodeError(ValueError):
    """A port code that is not a five-character UN/LOCODE."""


class CommodityPool:
    """Builds each commodity once and hands the same object to every caller.

    The pool holds its commodities weakly: a commodity nobody else holds is dropped, and a later
    request builds an equal one. It is not safe to share between threads.
    """

    def __init__(self, catalogue: Mapping[str, tuple[str, bool]] = CATALOGUE) -> None:
        self._catalogue = catalogue
        self._pool: weakref.WeakValueDictionary[str, Commodity] = weakref.WeakValueDictionary()

    def get(self, hs_code: str, /) -> Commodity:
        try:
            return self._pool[hs_code]
        except KeyError:
            pass
        try:
            description, dangerous_goods = self._catalogue[hs_code]
        except KeyError:
            raise UnknownCommodityError(f"unknown commodity {hs_code!r}") from None
        commodity = Commodity(hs_code, description, dangerous_goods)
        self._pool[hs_code] = commodity
        return commodity

    def __len__(self) -> int:
        return len(self._pool)


def port_code(text: str) -> str:
    """Validate a port code and return the interned string."""
    if not _PORT_CODE.fullmatch(text):
        raise PortCodeError(f"malformed port code {text!r}")
    return sys.intern(text)


def route(line: str) -> tuple[PortCall, ...]:
    """Parse ``"NLRTM;SGSIN"`` into numbered port calls."""
    return tuple(
        PortCall(port_code(text), sequence)
        for sequence, text in enumerate(line.split(";"), start=1)
    )
