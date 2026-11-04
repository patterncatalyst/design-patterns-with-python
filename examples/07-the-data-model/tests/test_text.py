from dataclasses import dataclass
from decimal import Decimal

import pytest
from data_model.money import Money


@dataclass(frozen=True, slots=True)
class _StrOnlyMoney:
    """Negative fixture: __str__ and no __format__."""

    amount: Decimal
    currency: str

    def __str__(self) -> str:
        return f"{self.currency} {self.amount}"


def test_repr_str_and_format_serve_different_readers(price: Money) -> None:
    assert repr(price) == "Money(amount=Decimal('12.50'), currency='EUR')"
    assert str(price) == "EUR 12.50"
    assert f"{price:>12}" == "   EUR 12.50"
    plain = _StrOnlyMoney(Decimal("12.50"), "EUR")
    assert str(plain) == "EUR 12.50"
    with pytest.raises(TypeError, match="unsupported format string"):
        f"{plain:>12}"
