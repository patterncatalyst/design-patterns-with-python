---
title: "Evidence: threads racing on a lazy import"
output: false
render_with_liquid: false
---

# Twenty subprocess runs of the lazy-import race

Recorded 2026-11-04 (r08) for the chapter on Singleton, on Python 3.15.2. Run from
`examples/18-singleton-module-borg-metaclass` with `uv run python <script>`. Each of the twenty
runs starts a fresh `python -I` interpreter and runs the same code as the member's
`test_threads_racing_on_a_lazy_import_load_the_table_once`: eight threads released together by a
`Barrier(8)` call `quote_standard`, whose first use reifies `lazy from singleton import
tariff_table`. The race is not forced, because nothing makes the threads overlap inside the import,
so this is recorded evidence only and the test asserts the outcome. The claim that exactly one
thread performs the import rests on PEP 810.

```python
"""Run the lazy-import race of the member's test twenty times, each in a fresh -I interpreter."""

import json
import subprocess
import sys

CODE = """
import json, sys, threading
from decimal import Decimal
import singleton.quoting
from singleton.loads import LOAD_LOG

THREADS = 8
start = threading.Barrier(THREADS, timeout=10)
quotes = []

def worker():
    start.wait()
    quotes.append(singleton.quoting.quote_standard("EUROPE", Decimal("10")))

threads = [threading.Thread(target=worker) for _ in range(THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=10)
sys.stdout.write(json.dumps({"loads": list(LOAD_LOG), "quotes": sorted({str(q) for q in quotes}), "count": len(quotes)}))
"""

ok = 0
for n in range(1, 21):
    done = subprocess.run(
        [sys.executable, "-I", "-c", CODE], capture_output=True, text=True, timeout=60, check=False
    )
    result = json.loads(done.stdout)
    good = result == {"loads": ["tariff"], "quotes": ["12.00"], "count": 8}
    ok += good
    print(
        f"run {n:2d}: loads={result['loads']} distinct quotes={result['quotes']} callers={result['count']}"
    )
print("runs with exactly one load:", ok, "of 20")
```

Output:

```text
run  1: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  2: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  3: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  4: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  5: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  6: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  7: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  8: loads=['tariff'] distinct quotes=['12.00'] callers=8
run  9: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 10: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 11: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 12: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 13: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 14: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 15: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 16: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 17: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 18: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 19: loads=['tariff'] distinct quotes=['12.00'] callers=8
run 20: loads=['tariff'] distinct quotes=['12.00'] callers=8
runs with exactly one load: 20 of 20
```
