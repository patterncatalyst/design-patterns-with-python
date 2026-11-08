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

A consignment needs a bill of lading, a manifest and a customs declaration, and the document to issue depends on its kind. The duty rate on the declaration comes from a cache that other threads evict from. The usual first draft of the first job is an if-chain, and of the second a membership test followed by a read. Both work until something changes around them, and mypy accepts both forms, so the failure shows only when the code runs or a test forces it.

An if-chain whose last branch raises doesn't notice a kind that was added later, and mypy accepts it (`test_an_if_chain_whose_else_raises_misses_a_new_kind`, `test_mypy_accepts_an_if_chain_whose_else_raises`).

A `try` wrapped around the whole call reports an issuer's own bug as an unsupported kind (`test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind`).

A look-first read raises when another thread evicts the key between the check and the read (`test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`).

{% include excalidraw.html name="31-shortcut-patterns-dict-dispatch-and-eafp" caption="Figure 31.1: Issuing a document looks the kind up in a read-only table and calls the issuer outside the try. Reading a duty rate asks forgiveness, so an eviction by another thread reloads the rate instead of raising KeyError." %}

Read the left lane from the top down. `issue(kind, consignment_id)` leads to the accent box `issuers[kind]` ("one lookup inside the try", "KeyError becomes UnsupportedDocumentError"), fed by an arrow from the box `ISSUERS` ("frozendict, read-only", "a test walks every DocumentKind"). Below it, `issuer(consignment_id)` ("outside the try: its own errors pass through") leads to "reference". The right lane has two sources. `_LookFirstDutyRateCache.rate_for`, the comparison form, has an arrow down to a dashed box, "look first: in, then read", where "an eviction in the gap raises KeyError". `DutyRateCache.rate_for(hs_code)` has an arrow down to the accent box "ask forgiveness: read once", which loads and stores the rate on a `KeyError`.

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

The table is a `frozendict`, which is new in 3.15. [PEP 814](https://peps.python.org/pep-0814/), by Victor Stinner and Donghee Na, says "A new public immutable type frozendict is added to the builtins module." A dispatch table is a constant, so a type that refuses assignment suits it: `test_the_issuer_table_is_read_only` shows the `TypeError`, and that `ISSUERS` isn't a `dict`: PEP 814 says `frozendict` is "not a dict subclass". Each kind issues its own reference (`test_issue_gives_each_kind_its_reference`), and a caller can pass another table by keyword while the default stays as it was (`test_a_table_passed_by_the_caller_replaces_the_default`).

A missing kind raises `UnsupportedDocumentError` with the `KeyError` suppressed (`test_an_unsupported_kind_raises_unsupported_document_error`). Text arrives too, from a form or a file, and `parse_kind` turns it into a kind or refuses it with the same error (`test_parse_kind_reads_a_document_kind_from_its_value`, `test_parse_kind_refuses_an_unknown_value`).

What mypy 2.4.1 checks is the shape of the table. An entry whose signature doesn't fit `DocumentIssuer` is reported as `[dict-item]` (`test_mypy_checks_an_issuers_signature_in_the_table`), a lookup with the wrong key type as `[index]` (`test_mypy_checks_the_key_type_of_a_table_lookup`), and an assignment into `ISSUERS` as `[index]` (`test_mypy_refuses_assignment_into_the_issuer_table`). Calling the result of `.get` without a branch for `None` is `[misc]` (`test_mypy_requires_a_branch_after_dict_get`). What it doesn't check is totality. A table with two of the three kinds type-checks and fails when the third is asked for (`test_mypy_accepts_a_table_that_misses_a_kind`), so a test walks the enum instead:

```python
def test_every_document_kind_has_an_issuer() -> None:
    assert [kind.name for kind in DocumentKind if kind not in ISSUERS] == []
```

## Table, match or singledispatch

Three forms can pick behaviour by a value, and the choice follows what is dispatched on and who owns the set of cases.

A `match` over an enum with `assert_never` closes the set, and mypy reports a missing arm. The same reduced model holds a chain with no `else`, where mypy reports the missing return (`test_mypy_reports_a_missing_arm_in_a_match_and_an_if_chain_without_else`, with the codes `[arg-type]` and `[return]`). A chain that ends in an `else` that raises gets no report at all (`test_mypy_accepts_an_if_chain_whose_else_raises`, also a reduced model). Both snippets restate a shape and don't import the example. [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) covers `match` as the closed-set form.

A table wins when the set is data. A caller supplies its own, as above, and a kind that arrives as text is looked up like any other key.

`singledispatch` dispatches on the type of the first argument, so it can't tell the members of one enum apart: all three `DocumentKind` members reach the same implementation, and the registry holds `DocumentKind` and `object` (`test_singledispatch_sends_every_document_kind_to_one_implementation`). It's the form for an open set of types, covered in [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}).

ruff 0.17.4 checks one spelling of the shape. Its SIM116 suggests a dictionary for a chain over string literals and says nothing about the same chain over enum members (`test_ruff_flags_an_if_chain_over_literals_but_not_over_enum_members`). The linter is a hint, so it can't stand in for the totality test.

Where the cases need different arguments, keep the branch: a table of callables assumes one call signature.

## Asking forgiveness

The table lookup raises a `KeyError` on a miss, and the code that reads it has two choices: test first, or read and handle the failure. The glossary names the second one: "Easier to ask for forgiveness than permission. This common Python coding style assumes the existence of valid keys or attributes and catches exceptions if the assumption proves false." (Python documentation, [glossary](https://docs.python.org/3.15/glossary.html)). The value is one operation where there would be two, and the cost, covered at the end, is a slower miss.

<!-- fmt:off -->
```python
    try:
        issuer = issuers[kind]
    except KeyError:
        raise UnsupportedDocumentError(f"no issuer for {kind.value!r}") from None
    return issuer(consignment_id)
```
<!-- fmt:on -->

The `try` holds the lookup and nothing else. The call to the issuer comes after it, so a `KeyError` raised inside an issuer travels out of `issue` as itself (`test_an_issuers_own_key_error_passes_through_issue`). The same call inside the `try`, the form the test module keeps as `_issue_broadly`, reports that bug as "no issuer for 'manifest'" (`test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind`). The compound-statements reference gives the language-level version of the rule: "Exceptions in the else clause are not handled by the preceding except clauses." ([compound statements](https://docs.python.org/3.15/reference/compound_stmts.html)). Code that has to run only on success belongs in an `else` for that reason.

Required fields are read the same way. `_required` names the missing field in a `CustomsError`:

<!-- fmt:off -->
```python
    try:
        return record[name]
    except KeyError:
        raise CustomsError(f"declaration is missing {name!r}") from None
```
<!-- fmt:on -->

`declaration_from` calls it for `consignment_id`, `hs_code` and `declared_value` (`test_a_missing_required_field_names_the_field`) and reads the optional `origin` with `record.get("origin")`, which gives `None` when the field is absent (`test_declaration_from_reads_required_fields_and_an_optional_origin`). The built-in types page describes `get` as returning the value "if key is in the dictionary, else default", so that it "never raises a KeyError" ([built-in types](https://docs.python.org/3.15/builtins/stdtypes.html)). A missing optional field isn't an error, so `get` says so. A missing required one is, so the lookup raises and the handler names it.

## Exceptions that hide bugs

A handler that's too broad turns a bug into a missing value. Two idioms do it by design.

`getattr` with a default and `hasattr` are implemented with the exception. The built-in functions page says `hasattr` "is implemented by calling getattr(object, name) and seeing whether it raises an AttributeError or not" ([built-in functions](https://docs.python.org/3.15/builtins/functions.html)). A property whose own body reads a missing attribute raises `AttributeError` from inside, and both calls report the property as absent: the default comes back and `hasattr` says `False`, while direct access shows the real message (`test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property`).

`contextlib.suppress` ends its block at the first exception it swallows, and the documentation says it "resumes execution with the first statement following the end of the with statement" ([contextlib](https://docs.python.org/3.15/library/contextlib.html)). A second statement in the same block doesn't run. In the test, a `del` of an absent key comes first, and the `del` of the present one after it is skipped, so the rate stays (`test_suppress_skips_the_rest_of_its_block_after_the_first_exception`). One `suppress` per statement, or the non-raising method that already exists, is the safer form. That's why `evict` calls `pop(hs_code, None)`. [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) covers narrowing `suppress` to one exception.

ruff names the idioms that replace the hand-written versions. SIM118 flags `in cache.keys()`, SIM401 an `if` around a lookup that `.get` would do, and SIM105 a `try`/`except`/`pass` that `suppress` would do (`test_ruff_suggests_get_suppress_and_plain_membership`). Those are style hints. None of the three can tell which handler is too wide.

## The look-first race

The glossary entry for the other style says what goes wrong: "In a multi-threaded environment, the LBYL approach can risk introducing a race condition between “the looking” and “the leaping”. For example, the code, if key in mapping: return mapping[key] can fail if another thread removes key from mapping after the test, but before the lookup."

`DutyRateCache` is the asking-forgiveness form. It reads once and loads on a miss:

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

The comparison is a subclass in the test fixtures that looks first:

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

On one table of cases, a hit, a miss and a key evicted first, both forms give the same rates and the same loads (`test_every_cache_form_reads_loads_and_evicts_the_same_way`), and evicting an absent code is no error in either (`test_evicting_an_absent_code_is_not_an_error`). A single thread sees no difference between them on these rows.

A second thread can. The cache takes its storage as a `MutableMapping`, so the test hands it a `dict` subclass that parks the first read on a `threading.Barrier`. The look-first form has its answer from `in` when the main thread evicts the code, and the following read raises `KeyError: '0901.21'` with no load (`test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`). The EAFP form is parked before its single read, so it misses, then reloads the rate and returns it (`test_an_eafp_read_reloads_when_another_thread_evicts_first`). The test forces the interleaving because waiting for it is unreliable. See also [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}).

The scope of the guarantee is one gap. Two EAFP readers that both miss both call the loader (`test_two_eafp_readers_that_both_miss_both_load`), so asking forgiveness doesn't make a load happen once. [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) covers loading once. Duty itself is plain arithmetic on the cached rate (`test_duty_for_applies_the_cached_rate_to_the_declared_value`).

The cost differs by case, and the numbers are illustrative. On a recorded run on Python 3.15.2 (best of five repeats of one million calls, 2026-11-06), a present key cost 42.7 ns for the EAFP form, 50.4 ns for the look-first form and 51.3 ns for `get`. An absent key cost 141.5 ns for EAFP against 45.0 and 51.0, because raising and catching an exception is dearer than a failed check. On a hit EAFP was cheapest, and on a miss it was about three times dearer. No test asserts a time.

## When not to use it

Keep the branch when the cases need different arguments, or when they must run in a fixed order: a table has one call signature, and a lookup tries no cases in order. Use `match` with `assert_never` for a closed set where mypy should report a missing kind, and `singledispatch` for an open set extended by type. Look first when the operation does work before it fails, or when a miss is common and costly to handle, because the exception path on a miss is the slow one.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a dispatch table.** "Handle each document kind" leaves open how the kinds are dispatched and where the exception handling goes. Paste a prompt that states the form:

> Dispatch on `DocumentKind` through a read-only `frozendict` typed `Mapping[DocumentKind, DocumentIssuer]`, with a test that every kind has an entry. Put only the lookup inside `try`/`except KeyError`, raise `UnsupportedDocumentError` from `None`, and call the issuer outside the `try`. Read shared state with one lookup in `try`/`except KeyError`, not `in` followed by indexing, and don't use `getattr` defaults or `hasattr` on properties.

If the reply wraps the call in the `try`, ask which `KeyError` it means to catch.
</blockquote>

## Build, run, observe

The example has 30 test functions and 42 cases. From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/31-shortcut-patterns-dict-dispatch-and-eafp
uv run pytest -v
uv run mypy --strict src tests
```

All 42 cases pass and mypy reports no issues. Both experiments below run in a fresh scratch copy of the repository, so the real example doesn't change. Each prints the output of this filter, then mypy:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|errors?))'
uv run mypy --strict src tests
```

**Experiment one: move the call into the `try`.** In `issue`, replace the lookup and the call after the handler with `return issuers[kind](consignment_id)` inside the `try`. The filter, then mypy, prints:

```text
E           shortcut_patterns.documents.UnsupportedDocumentError: no issuer for 'manifest'
src/shortcut_patterns/documents.py:61: UnsupportedDocumentError
FAILED tests/test_dispatch.py::test_an_issuers_own_key_error_passes_through_issue
1 failed, 41 passed in 3.06s
Success: no issues found in 8 source files
```

One test fails: the issuer's `KeyError("port")` now comes out as an unsupported kind. The table tests and the totality test still pass, because the lookup behaves as before, and mypy exits 0 since the types haven't moved.

**Experiment two: look first.** In `DutyRateCache.rate_for`, replace the `try` and `except` with `if hs_code in self._rates: return self._rates[hs_code]` ahead of the load. The filter, then mypy, prints:

```text
E       assert (["KeyError: '0901.21'"], []) == (['8.0'], ['0901.21'])
E         At index 0 diff: ["KeyError: '0901.21'"] != ['8.0']
E         Use -v to get more diff
tests/test_eafp.py:87: AssertionError
FAILED tests/test_eafp.py::test_an_eafp_read_reloads_when_another_thread_evicts_first
1 failed, 41 passed in 2.99s
Success: no issues found in 8 source files
```

The shared table of cases still passes with the new form, so one thread sees no difference. Only the forced eviction does, and it records the `KeyError` the glossary predicts. Both experiments gave identical output on a second run, apart from the duration.

## What you can do now

- Replace an if-chain with a table: `ISSUERS`, with `test_every_document_kind_has_an_issuer` checking that no kind is missing.
- Choose the form: `test_mypy_reports_a_missing_arm_in_a_match_and_an_if_chain_without_else` for the closed set and `test_singledispatch_sends_every_document_kind_to_one_implementation` for dispatch on type.
- Keep only the lookup inside `try`: `issue`, with `test_an_issuers_own_key_error_passes_through_issue` failing when the call moves in.
- Read EAFP-style and spot the hiding places: `test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property` for the default and the property.
- Force the race: `DutyRateCache` with `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read` and `test_an_eafp_read_reloads_when_another_thread_evicts_first`.

## For deeper coverage

The Python documentation's [glossary](https://docs.python.org/3.15/glossary.html) entries for EAFP, LBYL and thread-safe are the short definitions, and the [built-in types](https://docs.python.org/3.15/builtins/stdtypes.html) page covers `dict` and `frozendict`. [PEP 814](https://peps.python.org/pep-0814/), by Victor Stinner and Donghee Na, specifies `frozendict`, and the [contextlib](https://docs.python.org/3.15/library/contextlib.html) page covers `suppress`. *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for mappings in Python, and *Effective Python*, third edition, by Brett Slatkin, for working with exceptions. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
