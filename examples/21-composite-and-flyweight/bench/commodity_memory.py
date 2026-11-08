"""Memory cost of a commodity held by many consignments, and of repeated port codes.

Run from this directory with ``uv run python -I bench/commodity_memory.py``. It prints a table of
approximate figures for the running interpreter. The figures are not asserted anywhere: they
change with the Python version and the allocator.
"""

import gc
import sys
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass

COUNT = 100_000
PORTS = ("NLRTM", "SGSIN", "DEHAM", "CNSHA")


@dataclass(frozen=True)
class DictBacked:
    hs_code: str
    description: str
    dangerous_goods: bool


@dataclass(frozen=True, slots=True)
class Slotted:
    hs_code: str
    description: str
    dangerous_goods: bool


@dataclass(frozen=True, slots=True, weakref_slot=True)
class SlottedWeakref:
    hs_code: str
    description: str
    dangerous_goods: bool


def traced_bytes[T](build: Callable[[], T]) -> int:
    """Bytes still allocated after ``build`` returns, as tracemalloc counts them."""
    gc.collect()
    tracemalloc.start()
    try:
        before, _peak = tracemalloc.get_traced_memory()
        kept = build()
        after, _peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    del kept
    return after - before


def copies[T](make: Callable[[], T]) -> Callable[[], list[T]]:
    return lambda: [make() for _ in range(COUNT)]


def shared[T](make: Callable[[], T]) -> Callable[[], list[T]]:
    def build() -> list[T]:
        item = make()
        return [item] * COUNT

    return build


def split_codes(text: str) -> Callable[[], list[str]]:
    return lambda: text.split(";")


def interned_codes(text: str) -> Callable[[], list[str]]:
    return lambda: [sys.intern(code) for code in text.split(";")]


def main() -> None:
    args = ("850760", "lithium-ion batteries", True)
    print(f"Python {sys.version.split()[0]}, {COUNT:,} items held in a list")
    print()
    print("sys.getsizeof of one instance (the object itself, not what it refers to)")
    probe = DictBacked(*args)
    print(f"  dict-backed instance      {sys.getsizeof(probe):>8}")
    print(f"  dict-backed __dict__      {sys.getsizeof(probe.__dict__):>8}")
    print(f"  slotted instance          {sys.getsizeof(Slotted(*args)):>8}")
    print(f"  slotted with weakref slot {sys.getsizeof(SlottedWeakref(*args)):>8}")
    print()
    print("tracemalloc, bytes allocated for the list and what it holds (list pointer included)")
    rows = [
        ("dict-backed copies", traced_bytes(copies(lambda: DictBacked(*args)))),
        ("slotted copies", traced_bytes(copies(lambda: Slotted(*args)))),
        ("slotted with weakref slot", traced_bytes(copies(lambda: SlottedWeakref(*args)))),
        ("one shared slotted instance", traced_bytes(shared(lambda: SlottedWeakref(*args)))),
    ]
    for label, size in rows:
        print(f"  {label:<28}{size:>10}  (~{size / COUNT:.0f} bytes per item)")
    print()
    print("tracemalloc, port codes drawn from four values")
    text = ";".join(PORTS[i % len(PORTS)] for i in range(COUNT))
    plain = traced_bytes(split_codes(text))
    interned = traced_bytes(interned_codes(text))
    print(f"  plain split               {plain:>10}")
    print(f"  interned                  {interned:>10}")
    held = split_codes(text)()
    print(f"  distinct objects, plain    {len({id(code) for code in held}):>10}")
    held = [sys.intern(code) for code in held]
    print(f"  distinct objects, interned {len({id(code) for code in held}):>10}")


if __name__ == "__main__":
    main()
