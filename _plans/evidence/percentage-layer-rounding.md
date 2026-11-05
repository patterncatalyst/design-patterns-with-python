---
title: "Evidence: percentage layers and per-layer rounding"
output: false
render_with_liquid: false
---

# Two percentage layers, applied in each order, with every layer rounding to cents

Recorded 2026-11-04 (r09) for the chapter on the Decorator pattern, on Python 3.15.2 and mypy 2.4.1.
Run from `examples/20-decorator-pattern-vs-decorator-syntax-and-proxy` with `uv run python -I <script>`;
the script imports the member's real `BaseRate`, `Discount`, `Tax` and `Money.scaled`, so each layer rounds
half-up to cents exactly as the model code does. It uses no clock and no sleep, and the random draws come
from a seeded generator, so a fresh run prints the same lines.

Each case prices a consignment with a Discount of 10 percent and a Tax of 21 percent, once with the
discount inside and once with the tax inside. In exact arithmetic the two orders agree, because both
multiply by 0.9 and 1.21. Rounding after each layer splits them by a cent on some prices.

```text
import random
import sys
from decimal import Decimal
from importlib.metadata import version

from decorator_proxy.domain import Consignment, ConsignmentId, Money, Weight
from decorator_proxy.layers import BaseRate, Discount, Tax

TEN = Decimal(10)
TWENTY_ONE = Decimal(21)


def both_ways(per_kg: Decimal, kilograms: Decimal) -> tuple[Money, Money]:
    base = BaseRate(Money(per_kg, "EUR"))
    consignment = Consignment(
        id=ConsignmentId("CN-1"), weight=Weight(kilograms), destination="NLRTM"
    )
    discount_then_tax = Tax(Discount(base, TEN), TWENTY_ONE).price(consignment)
    tax_then_discount = Discount(Tax(base, TWENTY_ONE), TEN).price(consignment)
    return discount_then_tax, tax_then_discount


def report(name: str, cases: list[tuple[Decimal, Decimal]]) -> None:
    differing = []
    for per_kg, kilograms in cases:
        a, b = both_ways(per_kg, kilograms)
        if a != b:
            differing.append((per_kg, kilograms, a.amount, b.amount))
    gaps = sorted({abs(a - b) for _, _, a, b in differing})
    print(f"{name}: {len(differing)} of {len(cases)} differ")
    if differing:
        print(f"  gap in cents, smallest to largest: {gaps[0] * 100} to {gaps[-1] * 100}")
        per_kg, kilograms, a, b = differing[0]
        print(f"  first: per_kg={per_kg} kg={kilograms} discount-then-tax={a} tax-then-discount={b}")


# Every per-kilogram price from 0.01 to 200.00 at one kilogram.
sweep = [(Decimal(cents) / 100, Decimal(1)) for cents in range(1, 20001)]
report("sweep 0.01 to 200.00 at 1 kg", sweep)

# 20,000 seeded draws: price 0.01 to 200.00, weight 1 to 1000 kg.
rng = random.Random(20261104)
draws = [(Decimal(rng.randint(1, 20000)) / 100, Decimal(rng.randint(1, 1000))) for _ in range(20000)]
report("seeded draws (seed 20261104)", draws)

print(f"python {sys.version.split()[0]}, mypy {version('mypy')}")
```

Output:

```text
sweep 0.01 to 200.00 at 1 kg: 6940 of 20000 differ
  gap in cents, smallest to largest: 1.00 to 1.00
  first: per_kg=0.05 kg=1 discount-then-tax=0.06 tax-then-discount=0.05
seeded draws (seed 20261104): 6726 of 20000 differ
  gap in cents, smallest to largest: 1.00 to 1.00
  first: per_kg=121.51 kg=511 discount-then-tax=67617.76 tax-then-discount=67617.77
python 3.15.2, mypy 2.4.1
```

Reading the output: 6,940 of the 20,000 per-kilogram prices from 0.01 to 200.00 at one kilogram differ by exactly
one cent, the first at 0.05 (discount then tax gives 0.06, tax then discount gives 0.05). Larger weights
do not widen the gap, since each layer rounds its own total once: 6,726 of 20,000 seeded draws also differ by
exactly one cent. Where the two orders agree, as at 120.00 for 100 kg, both give 130.68.
