---
title: "Evidence: contextlib decorator on a generator, 3.14.10 vs 3.15.2"
output: false
render_with_liquid: false
---

# `@contextmanager` used as a decorator on a generator function

Recorded 2026-11-04 (r05) for claim 59. Source of the change: What's New in Python 3.15,
contextlib entry (gh-125862), https://docs.python.org/3.15/whatsnew/3.15.html. Both runs use
`python -I` on the uv-managed interpreters.

```python
import sys
from collections.abc import Iterator
from contextlib import contextmanager

log: list[str] = []


@contextmanager
def scope() -> Iterator[None]:
    log.append("enter")
    try:
        yield
    finally:
        log.append("exit")


@scope()
def rows() -> Iterator[str]:
    for r in ("NLRTM", "SGSIN"):
        log.append(f"row {r}")
        yield r


print(sys.version.split()[0])
gen = rows()
print("before iteration:", log)
list(gen)
print("after iteration:", log)
```

```
3.15.2
before iteration: []
after iteration: ['enter', 'row NLRTM', 'row SGSIN', 'exit']
3.14.10
before iteration: ['enter', 'exit']
after iteration: ['enter', 'exit', 'row NLRTM', 'row SGSIN']
```

## `with` inside the generator

The same scope used as a `with` inside the generator function instead of as a decorator, run with `python -I` on both interpreters.

```python
from collections.abc import Iterator
from contextlib import contextmanager

log: list[str] = []


@contextmanager
def scope() -> Iterator[None]:
    log.append("enter")
    try:
        yield
    finally:
        log.append("exit")


def rows() -> Iterator[str]:
    with scope():
        for port in ("NLRTM", "SGSIN"):
            log.append(f"row {port}")
            yield port


gen = rows()
print(log)
print(list(gen))
print(log)
```

Output on 3.15.2:

```text
[]
['NLRTM', 'SGSIN']
['enter', 'row NLRTM', 'row SGSIN', 'exit']
```

Output on 3.14.10:

```text
[]
['NLRTM', 'SGSIN']
['enter', 'row NLRTM', 'row SGSIN', 'exit']
```

The outputs are identical, so the `with` inside the generator behaves the same on both.
