---
title: "Evidence: the seeded transit-delay model"
output: false
render_with_liquid: false
---

# Mean delay over 10,000 seeds

Recorded 2026-11-04 (r07) for the chapter on State and finite state machines, on Python 3.15.2.
Run from `examples/14-state-and-finite-state-machines` with `uv run python -I <script>`; the script
imports the member's real `InTransit` and `simulate_transit`. Each run sails a 21-day voyage with a
delay probability of 0.2 from its own `random.Random(seed)`, seeds 0 to 9999, with a cap of 200 days.
The expected delay is the negative-binomial mean, 21 x 0.2 / 0.8 = 5.25. This is recorded evidence
only and no test asserts it.

```text
import random
from statistics import fmean

from state_machines.states import InTransit
from state_machines.transit import simulate_transit

P, SCHEDULED, MAX_DAYS = 0.2, 21, 200
delays = [
    simulate_transit(
        InTransit("NLRTM"),
        rng=random.Random(seed),
        delay_probability=P,
        scheduled_days=SCHEDULED,
        max_days=MAX_DAYS,
    ).delay_days
    for seed in range(10_000)
]
print("runs", len(delays))
print("mean delay", round(fmean(delays), 4))
print("expected", SCHEDULED * P / (1 - P))
print("min", min(delays), "max", max(delays))
print("seeds 1, 7, 42, 2026:", [delays[s] for s in (1, 7, 42, 2026)])
```

Output:

```text
runs 10000
mean delay 5.2758
expected 5.25
min 0 max 19
seeds 1, 7, 42, 2026: [7, 11, 9, 3]
```
