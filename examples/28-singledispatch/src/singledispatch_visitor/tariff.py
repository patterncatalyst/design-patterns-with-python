"""Customs area: one generic function with an implementation per commodity kind.

The fallback raises, because a kind that nobody registered is a declaration the customs team
cannot file, and a silent default would file it under the wrong heading. Codes are illustrative.
This module imports nothing from ``dangerous_goods``, which registers its own kind.
"""

from functools import singledispatch

from singledispatch_visitor.commodities import Coffee, InstantCoffee, TShirt


class TariffCodeError(LookupError):
    """A commodity kind with no registered tariff code."""


@singledispatch
def tariff_code(commodity: object) -> str:
    raise TariffCodeError(f"no tariff code for {type(commodity).__name__}")


@tariff_code.register
def _coffee(commodity: Coffee) -> str:
    roast = 2 if commodity.roasted else 1
    decaf = 2 if commodity.decaffeinated else 1
    return f"0901.{roast}{decaf}"


@tariff_code.register
def _instant_coffee(commodity: InstantCoffee) -> str:
    return "2101.11"


@tariff_code.register
def _tshirt(commodity: TShirt) -> str:
    return "6109.10" if commodity.cotton else "6109.90"
