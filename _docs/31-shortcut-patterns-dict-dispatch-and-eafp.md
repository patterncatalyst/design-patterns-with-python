---
title: "Shortcut patterns: dict dispatch, function tables, and EAFP"
order: 31
layout: tutorial
sectionid: docs
part: "patterns-in-the-wild"
description: "Replace an if-chain with a table of callables, and read fields and shared state with one try instead of a check and a read."
---

## Learning objectives

By the end of this chapter you can:

- Replace an if-chain over document kinds with a read-only table of callables, and test that it covers every kind.
- Choose between a table, `match` and `singledispatch` by what is dispatched on and who owns the set.
- Keep only the lookup inside `try`, so a handler's own errors pass through.
- Read fields EAFP-style, and say when `.get`, `getattr` defaults, `hasattr` and `suppress` hide errors.
- Force a check-then-read race with a seam and show which form survives it.

## Why this matters

A consignment needs a bill of lading, a manifest and a customs declaration, and the document to issue depends on its kind. The duty rate on the declaration comes from a cache that other threads evict from. The usual first draft of the first job is an if-chain, and of the second a membership test followed by a read. mypy accepts both, so the failures show only at run time:

- An if-chain whose last branch raises doesn't notice a kind added later.
- A `try` wrapped around the whole call reports an issuer's own bug as an unsupported kind.
- A look-first read raises when another thread evicts the key between the check and the read.

{% include excalidraw.html name="31-shortcut-patterns-dict-dispatch-and-eafp" described="true" caption="Figure 31.1: Issuing a document looks the kind up in a read-only table and calls the issuer outside the try. Reading a duty rate asks forgiveness, so an eviction by another thread reloads the rate instead of raising KeyError." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-31-shortcut-patterns-dict-dispatch-and-eafp" markdown="1">
The left lane runs from the top down. `issue(kind, consignment_id)` leads to the accent box `issuers[kind]` ("one lookup inside the try", "KeyError becomes UnsupportedDocumentError"), fed by an arrow from the box `ISSUERS` ("frozendict, read-only", "a test walks every DocumentKind"). Below it, `issuer(consignment_id)` ("outside the try: its own errors pass through") leads to "reference". The right lane has two sources. `_LookFirstDutyRateCache.rate_for`, the comparison form, has an arrow down to a dashed box, "look first: in, then read", where "an eviction in the gap raises KeyError". `DutyRateCache.rate_for(hs_code)` has an arrow down to the accent box "ask forgiveness: read once", which loads and stores the rate on a `KeyError`.
</div>
</details>

The figure puts the dispatch table on the left and the two ways of reading the duty-rate cache on the right.

## A table of callables

Choosing behaviour by a value is the job an if-chain does, and a common object-oriented answer is a class per behaviour. In Python a function is already a value, so the family collapses into a mapping from the key to the callable. The force, picking behaviour by data, is still there. What dissolves is the structure built around it, which is why [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) places if-chain dispatch in the dissolves bucket.

```python
ISSUERS: Mapping[DocumentKind, DocumentIssuer] = frozendict(
    {
        DocumentKind.BILL_OF_LADING: issue_bill_of_lading,
        DocumentKind.MANIFEST: issue_manifest,
        DocumentKind.CUSTOMS_DECLARATION: issue_customs_declaration,
    }
)
```

The table is a `frozendict`, which is new in 3.15. [PEP 814](https://peps.python.org/pep-0814/), by Victor Stinner and Donghee Na, says "A new public immutable type frozendict is added to the builtins module." A dispatch table is a constant, so a type that refuses assignment suits it: assigning into `ISSUERS` raises `TypeError`, and PEP 814 says `frozendict` is "not a dict subclass". Each kind issues its own reference, and a caller can pass another table by keyword while the default stays as it was.

A missing kind raises `UnsupportedDocumentError` with the `KeyError` suppressed. Text arrives too, from a form or a file, and `parse_kind` turns it into a kind or refuses it with the same error.

mypy checks the shape of the table:

| Mistake | mypy |
| --- | --- |
| an entry whose signature doesn't fit `DocumentIssuer` | `[dict-item]` |
| a lookup with the wrong key type | `[index]` |
| an assignment into `ISSUERS` | `[index]` |
| calling the result of `.get` without a branch for `None` | `[misc]` |
| a table with two of the three kinds | accepted; fails when the third is asked for |

It doesn't check totality, so a test walks the enum instead:

```python
def test_every_document_kind_has_an_issuer() -> None:
    assert [kind.name for kind in DocumentKind if kind not in ISSUERS] == []
```

## Table, match or singledispatch

Three forms pick behaviour by a value, and the choice follows what is dispatched on and who owns the set of cases:

| Form | Dispatches on | Set | A missing case |
| --- | --- | --- | --- |
| `match` with `assert_never` | a value of a closed type | closed | mypy `[arg-type]` |
| if-chain, no `else` | a value | closed | mypy `[return]` |
| if-chain whose `else` raises | a value | closed | nothing until run time |
| table of callables | a value, possibly from text | data; a caller can supply its own | a test walks the enum |
| `singledispatch` | the type of the first argument | open, extended by type | the fallback runs |

`singledispatch` can't tell the members of one enum apart: all three `DocumentKind` members reach the same implementation. [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) covers `match` for the closed set, and [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}) the open set of types.

ruff checks one spelling of the shape. Its SIM116 suggests a dictionary for a chain over string literals and says nothing about the same chain over enum members. A linter hint can't stand in for the totality test.

Where the cases need different arguments, keep the branch: a table of callables assumes one call signature.

## Asking forgiveness

The table lookup raises a `KeyError` on a miss, and the code that reads it has two choices: test first, or read and handle the failure. The [glossary](https://docs.python.org/3/glossary.html) names the second: "Easier to ask for forgiveness than permission. This common Python coding style assumes the existence of valid keys or attributes and catches exceptions if the assumption proves false." It's one operation where there would be two, and the cost, covered at the end, is a slower miss.

<!-- fmt:off -->
```python
    try:
        issuer = issuers[kind]
    except KeyError:
        raise UnsupportedDocumentError(f"no issuer for {kind.value!r}") from None
    return issuer(consignment_id)
```
<!-- fmt:on -->

The `try` holds the lookup and nothing else. The call to the issuer comes after it, so a `KeyError` raised inside an issuer travels out of `issue` as itself. With the same call inside the `try`, that bug is reported as "no issuer for 'manifest'". The [compound statements reference](https://docs.python.org/3/reference/compound_stmts.html) gives the language-level rule: "Exceptions in the else clause are not handled by the preceding except clauses." Code that runs only on success belongs in an `else` for that reason.

Required fields are read the same way. `_required` names the missing field in a `CustomsError`:

<!-- fmt:off -->
```python
    try:
        return record[name]
    except KeyError:
        raise CustomsError(f"declaration is missing {name!r}") from None
```
<!-- fmt:on -->

`declaration_from` calls it for `consignment_id`, `hs_code` and `declared_value`, and reads the optional `origin` with `record.get("origin")`, which gives `None` when the field is absent. The [built-in types](https://docs.python.org/3/builtins/stdtypes.html) page describes `get` as returning the value "if key is in the dictionary, else default", so that it "never raises a KeyError". A missing optional field isn't an error, so `get` says so. A missing required one is, so the lookup raises and the handler names it.

## Exceptions that hide bugs

A handler that's too broad turns a bug into a missing value. Two idioms do it by design.

`getattr` with a default and `hasattr` are implemented with the exception. The [built-in functions](https://docs.python.org/3/builtins/functions.html) page says `hasattr` "is implemented by calling getattr(object, name) and seeing whether it raises an AttributeError or not". A property whose own body reads a missing attribute raises `AttributeError` from inside, and both calls report the property as absent: the default comes back and `hasattr` says `False`, while direct access shows the real message.

`contextlib.suppress` ends its block at the first exception it swallows: the [contextlib](https://docs.python.org/3/library/contextlib.html) documentation says it "resumes execution with the first statement following the end of the with statement". With a `del` of an absent key first, the `del` of a present key after it is skipped, and the rate stays. Use one `suppress` per statement, or the non-raising method that already exists, which is why `evict` calls `pop(hs_code, None)`. [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) covers narrowing `suppress` to one exception.

ruff names the idioms that replace the hand-written versions: SIM118 flags `in cache.keys()`, SIM401 an `if` around a lookup that `.get` would do, and SIM105 a `try`/`except`/`pass` that `suppress` would do. None of the three can tell which handler is too wide.

## The look-first race

The glossary entry for the other style says what goes wrong: "In a multi-threaded environment, the LBYL approach can risk introducing a race condition between “the looking” and “the leaping”. For example, the code, if key in mapping: return mapping[key] can fail if another thread removes key from mapping after the test, but before the lookup."

`DutyRateCache` asks forgiveness. It reads once and loads on a miss:

<!-- fmt:off -->
```python
    def rate_for(self, hs_code: str) -> Decimal:
        try:
            return self._rates[hs_code]
        except KeyError:
            rate = self._load(hs_code)
            self._rates[hs_code] = rate
            return rate
```
<!-- fmt:on -->

The look-first form checks, then reads:

<!-- fmt:off -->
```python
    def rate_for(self, hs_code: str) -> Decimal:
        if hs_code in self._rates:
            return self._rates[hs_code]
        rate = self._load(hs_code)
        self._rates[hs_code] = rate
        return rate
```
<!-- fmt:on -->

On a hit, a miss and a key evicted first, both forms give the same rates and the same loads, and evicting an absent code is no error in either. A single thread sees no difference.

A second thread can. The cache takes its storage as a `MutableMapping`, so a `dict` subclass can park the first read on a `threading.Barrier` while the main thread evicts the code:

| Form | Result of the eviction in the gap |
| --- | --- |
| look first | has its answer from `in`; the read raises `KeyError: '0901.21'`, no load |
| ask forgiveness | parked before its single read; misses, reloads and returns the rate |

The interleaving is forced because waiting for it is unreliable; see also [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}).

The guarantee covers one gap. Two EAFP readers that both miss both call the loader, so asking forgiveness doesn't make a load happen once. [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) covers loading once.

The cost differs by case, and the numbers are illustrative. On a recorded run on Python 3.15.2 (best of five repeats of one million calls, 2026-11-06):

| Key | EAFP | look first | `get` |
| --- | --- | --- | --- |
| present | 42.7 ns | 50.4 ns | 51.3 ns |
| absent | 141.5 ns | 45.0 ns | 51.0 ns |

Raising and catching an exception is dearer than a failed check, so EAFP is cheapest on a hit and about three times dearer on a miss.

## When not to use it

- **Different arguments or a fixed order.** Keep the branch when the cases need different arguments, or when they must run in a fixed order: a table has one call signature, and a lookup tries no cases in order.
- **A closed set** where mypy should report a missing kind wants `match` with `assert_never`; **an open set extended by type** wants `singledispatch`.
- **Costly misses.** Look first when the operation does work before it fails, or when a miss is common and costly to handle, because the exception path on a miss is the slow one.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a dispatch table.** "Handle each document kind" leaves open how the kinds are dispatched and where the exception handling goes. Paste a prompt that states the form:

> Dispatch on `DocumentKind` through a read-only `frozendict` typed `Mapping[DocumentKind, DocumentIssuer]`, with a test that every kind has an entry. Put only the lookup inside `try`/`except KeyError`, raise `UnsupportedDocumentError` from `None`, and call the issuer outside the `try`. Read shared state with one lookup in `try`/`except KeyError`, not `in` followed by indexing, and don't use `getattr` defaults or `hasattr` on properties.

If the reply wraps the call in the `try`, ask which `KeyError` it means to catch.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/31-shortcut-patterns-dict-dispatch-and-eafp
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 42 cases pass and mypy is clean. Two experiments, each in a scratch copy:

- **Move the call into the `try`.** In `issue`, replace the lookup and the call after the handler with `return issuers[kind](consignment_id)` inside the `try`. One test fails: the issuer's `KeyError("port")` now comes out as `UnsupportedDocumentError: no issuer for 'manifest'`. The table and totality checks still pass, and mypy stays green.
- **Look first.** In `DutyRateCache.rate_for`, replace the `try` and `except` with `if hs_code in self._rates: return self._rates[hs_code]` ahead of the load. Only the forced eviction fails, recording the `KeyError` the glossary predicts. mypy stays green.

## What you can do now

- Replace an if-chain with `ISSUERS`, a read-only table, and walk the enum to check that no kind is missing.
- Choose the form: `match` for a closed set, a table for a set that is data, `singledispatch` for dispatch on type.
- Keep only the lookup inside `try`, as `issue` does, so an issuer's own `KeyError` passes through.
- Read EAFP-style with `_required`, use `.get` for optional fields, and keep `getattr` defaults and `hasattr` away from properties.
- Force the race with a `Barrier` seam, and show `DutyRateCache` reloading where the look-first form raises.

## For deeper coverage

The Python documentation's [glossary](https://docs.python.org/3/glossary.html) entries for EAFP, LBYL and thread-safe are the short definitions, and the [built-in types](https://docs.python.org/3/builtins/stdtypes.html) page covers `dict` and `frozendict`. [PEP 814](https://peps.python.org/pep-0814/), by Victor Stinner and Donghee Na, specifies `frozendict`, and the [contextlib](https://docs.python.org/3/library/contextlib.html) page covers `suppress`. *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for mappings in Python, and *Effective Python*, third edition, by Brett Slatkin, for working with exceptions. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
