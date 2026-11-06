"""Consignment area: the kinds of goods a customs declaration names."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Coffee:
    roasted: bool
    decaffeinated: bool = False


@dataclass(frozen=True, slots=True)
class InstantCoffee(Coffee):
    """Coffee with its own heading, so it needs its own registration."""


@dataclass(frozen=True, slots=True)
class TShirt:
    cotton: bool


@dataclass(frozen=True, slots=True)
class LithiumIonBattery:
    watt_hours: Decimal
