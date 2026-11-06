"""Cost of reading a rate from a mapping three ways, for a present key and an absent one.

Run from this directory with ``uv run python -I bench/lookup_cost.py``. It prints the best of five
repeats of one million calls per form. The figures are illustrative, depend on the interpreter and
the machine, and are not asserted anywhere. Pytest does not collect this file.
"""

import sys
import timeit
from collections.abc import Callable
from decimal import Decimal

CALLS = 1_000_000
REPEATS = 5
MISSING = Decimal(0)
RATES = {"0901.21": Decimal("8.0")}


def eafp(rates: dict[str, Decimal], code: str) -> Decimal:
    try:
        return rates[code]
    except KeyError:
        return MISSING


def look_first(rates: dict[str, Decimal], code: str) -> Decimal:
    if code in rates:
        return rates[code]
    return MISSING


def with_get(rates: dict[str, Decimal], code: str) -> Decimal:
    return rates.get(code, MISSING)


FORMS: dict[str, Callable[[dict[str, Decimal], str], Decimal]] = {
    "eafp": eafp,
    "lbyl": look_first,
    "get": with_get,
}


def nanoseconds_per_call(form: Callable[[dict[str, Decimal], str], Decimal], code: str) -> float:
    best = min(
        timeit.repeat(
            lambda: form(RATES, code),
            number=CALLS,
            repeat=REPEATS,
        )
    )
    return best / CALLS * 1e9


def main() -> None:
    sys.stdout.write(
        f"Python {sys.version.split()[0]}, best of {REPEATS} repeats of {CALLS:,} calls\n"
    )
    for code in ("0901.21", "6109.10"):
        for name, form in FORMS.items():
            sys.stdout.write(f"{code} {name:<5}{nanoseconds_per_call(form, code):>8.1f} ns/call\n")


if __name__ == "__main__":
    main()
