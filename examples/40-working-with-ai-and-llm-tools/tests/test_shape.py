"""The four shape rules on their minimal cases, and what they leave alone."""

import pytest
from review_gate.shape import review

_SINGLE_METHOD_BASE = """\
from abc import ABC, abstractmethod


class Rule(ABC):
    @abstractmethod
    def price(self) -> int: ...
"""

_STATIC_ONLY = """\
class Rules:
    @staticmethod
    def price() -> int:
        return 1
"""

_ACCESSOR_PAIR = """\
class Rate:
    def get_rate(self) -> int:
        return 1

    def set_rate(self, rate: int) -> None:
        pass
"""

_INSTANCE_IN_NEW = """\
class Rules:
    def __new__(cls) -> "Rules":
        cls.shared = super().__new__(cls)
        return cls.shared
"""

_CALLABLE_CLASS = """\
class Flat:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __call__(self) -> int:
        return self.amount
"""

_FROZEN_DATACLASS = """\
from dataclasses import dataclass


@dataclass(frozen=True)
class Rate:
    per_kg: int

    def apply(self, kilograms: int) -> int:
        return self.per_kg * kilograms
"""

_GETTER_ONLY = """\
class Rate:
    def get_rate(self) -> int:
        return 1
"""

# An instance-in-new class first, a single-method base second: rule order is the reverse of
# line order, so only the sort puts the findings in line order.
_OUT_OF_ORDER = _INSTANCE_IN_NEW + "\n\n" + _SINGLE_METHOD_BASE


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(_SINGLE_METHOD_BASE, [(4, "single-method-base")], id="single-method-base"),
        pytest.param(_STATIC_ONLY, [(1, "static-only-class")], id="static-only-class"),
        pytest.param(_ACCESSOR_PAIR, [(2, "accessor-pair")], id="accessor-pair"),
        pytest.param(_INSTANCE_IN_NEW, [(2, "instance-in-new")], id="instance-in-new"),
    ],
)
def test_each_shape_rule_fires_on_its_minimal_case(
    source: str, expected: list[tuple[int, str]]
) -> None:
    assert [(f.line, f.rule) for f in review(source)] == expected


def test_shape_rules_stay_quiet_on_a_callable_class_and_a_frozen_dataclass() -> None:
    assert (review(_CALLABLE_CLASS), review(_FROZEN_DATACLASS)) == ([], [])


def test_a_getter_without_a_setter_is_not_an_accessor_pair() -> None:
    assert review(_GETTER_ONLY) == []


def test_findings_come_back_in_line_order() -> None:
    assert [(f.line, f.rule) for f in review(_OUT_OF_ORDER)] == [
        (2, "instance-in-new"),
        (10, "single-method-base"),
    ]
