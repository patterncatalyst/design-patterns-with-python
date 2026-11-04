---
title: "Evidence: the forms that fill a strategy slot"
output: false
render_with_liquid: false
---

# Name, equality, hashing and repr of each rule form

Recorded 2026-11-04 (r06) for the chapter on Strategy's table of rule forms, on Python 3.15.2.
Run from `examples/12-strategy-the-callable` with `uv run python -I <script>`; the script imports the
member's real `flat_rate`, `per_kg`, `ZoneRate` and `TARIFF`.

```text
import re
from collections.abc import Mapping
from functools import partial
from decimal import Decimal
from strategy_callable.rules import PricingRule, ZoneRate, TARIFF, per_kg, flat_rate
from strategy_callable.domain import Money
def mk(rate: Decimal) -> PricingRule:
    def rule(c): return Money(rate, "EUR")
    return rule
def lam(r): return lambda c: Money(r, "EUR")
forms = {
 "function": (flat_rate, flat_rate),
 "lambda": (lam(Decimal(1)), lam(Decimal(1))),
 "closure": (mk(Decimal(1)), mk(Decimal(1))),
 "partial": (partial(per_kg, rate=Decimal(1)), partial(per_kg, rate=Decimal(1))),
 "rule object": (ZoneRate(TARIFF), ZoneRate(TARIFF)),
}
for k,(a,b) in forms.items():
    try: n = a.__name__
    except AttributeError: n = "AttributeError"
    try: hash(a); h=True
    except TypeError: h=False
    r = repr(a)
    print(k, "name=",n, "eq=",a==b, "hashable=",h, "samehash=", (hash(a)==hash(b)) if h else None, "repr_has_addr=", bool(re.search(r"0x[0-9a-f]+", r)), "repr_equal=", repr(a)==repr(b))
```

Output:

```text
function name= flat_rate eq= True hashable= True samehash= True repr_has_addr= True repr_equal= True
lambda name= <lambda> eq= False hashable= True samehash= False repr_has_addr= True repr_equal= False
closure name= rule eq= False hashable= True samehash= False repr_has_addr= True repr_equal= False
partial name= AttributeError eq= False hashable= True samehash= False repr_has_addr= True repr_equal= True
rule object name= AttributeError eq= True hashable= True samehash= True repr_has_addr= False repr_equal= True
```
