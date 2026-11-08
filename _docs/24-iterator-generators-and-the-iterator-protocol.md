---
title: "Iterator: generators and the iterator protocol"
order: 24
layout: tutorial
sectionid: docs
part: "coordinating-traversing"
description: "A generator replaces the cursor class, but one pass or many, how much to read and who closes the source are decisions the language leaves to you."
---

## Learning objectives

By the end of this chapter you can:

- Write `__iter__` as a generator so every loop gets a fresh iterator.
- Tell an iterable from an iterator, and know which one survives a second pass.
- Read only the part of a source you need with `batched`, `islice`, `pairwise` and `chain.from_iterable`.
- Delegate with `yield from` and type the value it returns with `Generator`.
- Close a reader that a consumer abandons, with `close()` or `contextlib.closing`.

## Why this matters

A generator function writes the cursor for you, so the Iterator class goes away. Three choices remain: whether the object can be walked twice, how much of the source a consumer reads, and who closes the source. Each one goes wrong in the obvious version.

{% include excalidraw.html name="24-iterator-generators-and-the-iterator-protocol" described="true" caption="Figure 24.1: A tracking history gives each loop a fresh iterator, so two walks both see every event. Pages are read one batch at a time, and closing a reader closes its file." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-24-iterator-generators-and-the-iterator-protocol" markdown="1">
From the top: `TrackingHistory` ("each loop gets a fresh iterator") leads to two walks, which both lead to `pages` (`batched`, one page at a time) and then `page` (`islice`, stops at the page it returns). A dashed box beside them is the self-iterating cursor, empty on the second pass. On the right, `read_events` opens its file inside `with` and leads to `close()`, which closes the file. A dashed box below it shows that `break` alone leaves a named reader open.
</div>
</details>

## Pattern: Iterator

### The problem

A display and a report read a tracking history page by page. Both want the events one at a time and neither should care how the history stores them. The obvious version fails three ways:

- The display builds a list and slices it, so the first page of three from 1,000,000 events reads all 1,000,000.
- The report walks a generator twice, and the second pass finds nothing without raising an error.
- A caller takes the first event from a log reader and breaks out of the loop, and the file stays open.

### The solution

An **Iterator** moves the walk over a collection into a cursor object of its own, so the code that uses the collection stays ignorant of how it's built.

**Bucket: dissolves.** Python builds the cursor into the language, and a generator function writes it for you.

Use a generator-based iterator when:

- callers only need the items in order, not indexing or a length;
- the source is large, slow or unbounded, and a consumer may stop early;
- the source holds a resource, such as a file, that must be released.

### How Python models it

This is the whole of the history's iteration:

```python
    def __iter__(self) -> Iterator[HandlingEvent]:
        yield from self._events
```

A function containing `yield` returns a generator when called. The generator's suspended frame holds the position that a cursor class would keep in a field. A `for` loop calls `iter()` on the history, then `next()` on the result until it raises `StopIteration`.

The protocol has two halves. An *iterable* hands out iterators; an *iterator* holds a position, and `iter()` on an iterator returns the iterator itself. A class with `__next__` but no `__iter__` isn't iterable: a `for` loop raises `TypeError`, and mypy rejects it.

### One pass or many

The GoF cursor, written to the protocol, keeps an index and returns itself from `__iter__`:

```python
class _OneShotHistory:
    """The GoF cursor written to the protocol: an index, and `__iter__` returns itself."""

    def __init__(self, events: Iterable[HandlingEvent]) -> None:
        self._events = tuple(events)
        self._index = 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> HandlingEvent:
        if self._index >= len(self._events):
            raise StopIteration
        event = self._events[self._index]
        self._index += 1
        return event
```

It walks once correctly. The second walk is where the two differ:

| Walk over 3 events | `TrackingHistory` | Self-iterating cursor |
| --- | --- | --- |
| Second pass | 3 events again | `[]` |
| A loop inside a loop | 9 pairs | 2 pairs |

The inner loop drains the shared cursor after the outer loop has taken its first event, so only 2 pairs come out. A generator expression such as `(event for event in history)` behaves like the cursor: the first `list()` gives 3 events, the second gives `[]`, and nothing complains. The Python glossary puts it this way: "Attempting this with an iterator will just return the same exhausted iterator object used in the previous iteration pass, making it appear like an empty container."

mypy can't see either failure. It accepts two `sum()` calls over the same `Iterator[int]`, and it accepts the cursor where an `Iterable` is expected. When a function walks its argument twice, annotate it `Collection`, which a generator doesn't satisfy, or materialise the data once.

### Read only what you need

The standard library supplies the pieces for paging:

```python
def pages(history: Iterable[HandlingEvent], size: int) -> Iterator[tuple[HandlingEvent, ...]]:
    """Yield the history in tuples of `size`, reading one page at a time."""
    yield from batched(history, size, strict=False)


def page(history: Iterable[HandlingEvent], number: int, size: int) -> tuple[HandlingEvent, ...]:
    """Return page `number`, counted from 1, or an empty tuple past the end."""
    if number < 1:
        raise ValueError("page numbers start at 1")
    return next(islice(pages(history, size), number - 1, None), ())
```

Against a source of 1,000,000 events that counts what it produces:

| Call | Events produced |
| --- | --- |
| `list(source)[:3]` | 1,000,000 |
| first page of `pages(source, 3)` | 3 |
| `page(source, 2, 3)` | 6 |

`batched` keeps a short last page, so 7 events give pages of 3, 3 and 1. A page size below one raises `ValueError`, and so does page 0. A page past the end returns `()`, the default passed to `next()`, instead of raising `StopIteration`.

Two more helpers pull lazily in the same way:

- `out_of_order` uses `pairwise` to find consecutive events where the second comes earlier in the `HandlingKind` lifecycle: loaded, booked, departed gives the one pair, loaded then booked.
- `events_of` uses `chain.from_iterable`, so a second history isn't touched until the first is exhausted.

The `itertools` page marks `batched` as added in 3.12 and `strict` in 3.13; with `strict=True`, a short last batch raises `ValueError`.

### Delegating with yield from

A log reader has two jobs: parse lines into events, and report how many lines it read. `events_from` parses and returns the count, and `read_events` owns the file:

```python
def read_events(path: Path, *, opener: Opener = open_utf8) -> Generator[HandlingEvent, None, int]:
    """Open the log when the first event is asked for, and close it when the reader ends."""
    with opener(path) as lines:
        return (yield from events_from(lines))
```

`yield from` passes every event through and evaluates to the subgenerator's return value. `Generator[HandlingEvent, None, int]` records all three types: what it yields, what `send()` accepts and what it returns, and mypy rejects assigning that `int` to a `str`.

Two details catch people:

- **`list()` drops the return value.** Only a manual walk sees the count, on the `StopIteration` that ends it.
- **`StopIteration` inside a generator becomes `RuntimeError`** ([PEP 479](https://peps.python.org/pep-0479/)). A stray `next()` on an empty iterator fails loudly instead of ending the feed early.

A malformed line stops the reader with a `TrackingLogError` that names the line number.

### Who closes the source

A reader opens nothing until the first event is asked for. After that the file is open, and a consumer that stops early decides when it closes:

| Consumer | File after the loop |
| --- | --- |
| Reads to the end | Closed |
| Calls `reader.close()` | Closed |
| Wraps the reader in `contextlib.closing` | Closed at the end of the block |
| Breaks out of the loop, reader still named | Open |
| Breaks out and drops every reference | Closed when collected, at no promised time |

`close()` raises `GeneratorExit` at the suspended `yield`, the exception passes through the `with` inside `read_events`, and the file closes. `contextlib.closing` makes that call for you:

```python
    with closing(read_events(tracking_log, opener=recording_opener)) as reader:
        for _ in reader:
            break
        (handle,) = recording_opener.handles
        assert not _closed(handle)

    assert _closed(handle)
```

Use `closing`, or call `close()`, whenever a consumer may stop early and the file must close at a known point. mypy helps here: `close()` exists on `Generator` but not on `Iterator`, which is why `read_events` is annotated `Generator`.

Asynchronous generators follow the same rules with `aclose()`; see [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## When not to use it

- **Iterator.** Pass the tuple when the data is already in a list that callers index or measure. Materialise once, or pass an iterable, when a result is needed twice. When a source must close at a known point, let a context manager own it and let the generator only read. When the function produces one value, return it.

<blockquote class="ai-sidebar" markdown="1">
**Specifying an iterator.** "Make the history iterable" doesn't say whether it's walked once or many times, how much a page reads or who closes the log. State those in the prompt:

> Make `TrackingHistory.__iter__` a generator so every loop gets a fresh iterator. Write `pages(history, size)` with `itertools.batched` so the first page reads only `size` events, and `page(history, number, size)` with `islice`. Write the log reader as a generator that opens its file inside `with`, annotate it `Generator[HandlingEvent, None, int]`, and close it with `contextlib.closing` where a caller may stop early.

If the reply returns `self` from `__iter__` or builds a `list` first, ask for the test that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/24-iterator-generators-and-the-iterator-protocol
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 42 cases pass and mypy is clean. Two experiments show what the idiomatic version buys:

- **Store one iterator.** In a scratch copy, make `TrackingHistory.__init__` keep `self._walk = iter(self._events)` and have `__iter__` return it. The second-pass, nested-walk and fresh-iterator tests fail, and mypy stays green.
- **Open without `with`.** In a scratch copy, open the file in `read_events` with a plain assignment. Eight reader tests fail: the file no longer closes, and the root `filterwarnings = ["error"]` setting turns the unclosed-file `ResourceWarning` into a failure. mypy stays green again.

## What you can do now

- Write `__iter__` as a generator, as `TrackingHistory` does, so every loop gets a fresh iterator.
- Spot a single-pass object before it's walked twice, and annotate `Collection` where a function needs two passes.
- Page through a source with `pages` and `page`, which read 3 and 6 events of a million.
- Return a value through `yield from` and type it with `Generator[HandlingEvent, None, int]`.
- Close a reader with `close()` or `contextlib.closing` when a consumer stops early.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides, 1994) is the source for Iterator. Brandon Rhodes's [The Iterator Pattern](https://python-patterns.guide/gang-of-four/iterator/) covers the iterable, the iterator and objects that are their own iterator. The [glossary](https://docs.python.org/3/glossary.html) defines iterable, iterator and generator iterator. The [built-in functions](https://docs.python.org/3/builtins/functions.html) page covers `iter` and `next`, the [built-in types](https://docs.python.org/3/builtins/stdtypes.html) page covers the generator methods, and the [expressions reference](https://docs.python.org/3/reference/expressions.html) covers yield expressions. The [`itertools`](https://docs.python.org/3/library/itertools.html), [`contextlib`](https://docs.python.org/3/library/contextlib.html) and [`typing`](https://docs.python.org/3/library/typing.html) pages cover `batched`, `islice`, `pairwise`, `chain.from_iterable`, `closing` and `Generator`. [PEP 255](https://peps.python.org/pep-0255/), "Simple Generators" by Schemenauer, Peters and Hetland, introduced generators. [PEP 380](https://peps.python.org/pep-0380/), "Syntax for Delegating to a Subgenerator" by Gregory Ewing, added `yield from`. [PEP 479](https://peps.python.org/pep-0479/), by Chris Angelico and Guido van Rossum, changed `StopIteration` inside a generator. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
