---
title: "r15 plan: chapters 31-32 (Shortcut patterns: dict dispatch, function tables, and EAFP; Anti-patterns and pattern misuse)"
order: 15
output: false
render_with_liquid: false
---

# r15: chapters 31-32, Shortcut patterns: dict dispatch, function tables, and EAFP; Anti-patterns and pattern misuse

Opus-planned 2026-11-06. Branch `release/r15`, cut from main at dfec2a8 (the r14 merge). This file is the source of truth for r15 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4, uv 0.13.7 and uv_build 0.13.7 match PyPI and python.org (checked 2026-11-06: pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, ruff 0.17.4 of 2026-11-05, mypy 2.4.1 of 2026-10-28, uv and uv-build 0.13.7 of 2026-11-03; python.org lists 3.15.0 to 3.15.2). R0 re-checks before any edit. `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch31: slug `31-shortcut-patterns-dict-dispatch-and-eafp`, title "Shortcut patterns: dict dispatch, function tables, and EAFP", part 10 (`patterns-in-the-wild`), `kind = "pattern"`, `has_example = true`, `status = "stub"`. The stub carries a `## How it works` heading that the draft drops.
- ch32: slug `32-anti-patterns-and-pattern-misuse`, title "Anti-patterns and pattern misuse", part 10 (`patterns-in-the-wild`), `kind = "argument"`, `has_example = false` (R0 sets `true`, decision 1), `status = "stub"`. The stub carries a `## The argument` heading that the draft drops.

`validate.py` SPINE:
- `pattern`: Learning objectives, Why this matters, Build, run, observe, When not to use it, What you can do now, For deeper coverage, plus exactly one `<blockquote class="ai-sidebar" markdown="1">`.
- `argument`: Learning objectives, Why this matters, What you can do now, For deeper coverage. No sidebar count is enforced; one figure is required (any kind but `appendix`).

`has_example` is metadata only: `validate.py` never reads it.

Work items: PDP-131a-c (ch31 example, figure, prose) and PDP-132a-c (ch32), `todo` in `_plans/iteration-plan.md`.

## User decisions (to be confirmed by the owner)

Standing, not a decision: step ids are `R*`. `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md`. The letters in use are A, G to N, P, Q and S; `grep -nE '^\| R[0-9]' _plans/*.md` matched nothing before this file.

1. **Kinds and buckets.**
   - **ch31 is a pattern chapter that dissolves.** The three-way split chapter's table row reads "If-chain dispatch | Dissolves | A dict of callables, with EAFP", and domain row 31 says dissolve. EAFP is the idiom that comes with it. The outline lists "EAFP vs LBYL" in its disambiguation column, but the book's map is the three-way split chapter's table, so the bucket sentence says dissolves.
   - **ch32 stays `argument` with `has_example = true`**, as ch3 already is.
     - Its H2s add `## Build, run, observe` and `## When the structure earns its place`.
     - No `## When not to use it`: ch32 isn't a pattern chapter.

   **Recommend: yes.** Alternative: make ch32 `pattern`. Anti-patterns have no bucket, and validate would demand "When not to use it".

2. **ch32 gets one AI sidebar in the prompt form.** It states the problem, gives a ready-to-paste prompt, and has at most one review line.
   - No sentence says what assistants or models produce, because nothing in this iteration backs such a claim.
   - Legacy row 25 (LLM output fails mypy or the idiom scan) and the review of generated code stay with "Working with AI and LLM tools". ch32 points there once by title and describes nothing.

   **Recommend: yes.** Alternative: no sidebar, as in chapters 1 to 4. The outline promises "pattern-shaped LLM output" here, and the prompt is the least claim-heavy way to honour it.

3. **ch31's domain (domain row 31, Documentation area).**
   - **`documents.py`**:
     - `ConsignmentId`;
     - `DocumentKind` with the decorators chapter's members and values: `BILL_OF_LADING = "bill of lading"`, `MANIFEST = "manifest"`, `CUSTOMS_DECLARATION = "customs declaration"`;
     - `UnsupportedDocumentError(LookupError)` (new);
     - `type DocumentIssuer = Callable[[ConsignmentId], str]` (new);
     - `issue_bill_of_lading`, `issue_manifest` and `issue_customs_declaration`, giving `BL-CN-1`, `MF-CN-1` and `CD-CN-1`;
     - `ISSUERS: Mapping[DocumentKind, DocumentIssuer] = frozendict({...})`;
     - `issue(kind, consignment_id, /, *, issuers=ISSUERS) -> str`;
     - `parse_kind(raw: str) -> DocumentKind`.
   - **`declarations.py`**:
     - `CustomsError(ValueError)`, reused from the Template Method chapter;
     - frozen slotted `CustomsDeclaration(consignment_id, hs_code, declared_value: Decimal, origin: str | None)`;
     - `declaration_from(record: Mapping[str, str]) -> CustomsDeclaration` (new).
   - **`duties.py`**:
     - `DutyRateCache(load, *, rates: MutableMapping[str, Decimal] | None = None)` (new), with `rate_for(hs_code) -> Decimal` (EAFP) and `evict(hs_code) -> None` (`pop(hs_code, None)`);
     - `duty_for(declaration, cache) -> Decimal`.
   - HS codes `0901.21` and `6109.10` and the rates are illustrative, as in the singledispatch chapter.
   - The decorators chapter's `DocumentKindError` isn't reused: it means "registered twice" there.

   **Recommend: yes.** Alternative: reuse `DocumentKindError` for an unsupported kind. One name would then carry two meanings across the book.

4. **ch31's one comparison form is `cache_form` `eafp|lbyl`, on `CACHE_ROWS`.**
   - The look-first form is the conftest class `_LookFirstDutyRateCache`, whose `rate_for` is `if hs_code in self._rates: return self._rates[hs_code]`. Its `rate_for` is the one comparison excerpt.
   - Fail-on-purpose forms get their own tests, not table rows:
     - the if-chain whose `else` raises (domain row 31's failing test);
     - `_issue_broadly`, which wraps the call in the `try`;
     - the `getattr` default;
     - the `singledispatch` over enum members.
   - `match` and if-chain totality appear only as mypy reduced models.

   **Recommend: yes.** Alternative: `dispatch_form` `table|match`. That would make legacy row 28's race a fail-on-purpose test, when it's the one place a shared table of cases measures a real difference.

5. **The race is forced through a storage seam, not a hook in `src`.**
   - `DutyRateCache` takes its storage as a `MutableMapping`.
   - The conftest `_HandoverRates(dict[str, Decimal])` parks the first read on a `threading.Barrier(2, timeout=10)`, waiting twice so that another thread evicts in between. `__contains__` answers first and then parks; `__getitem__` parks first and then reads.
   - Under the look-first form the check says yes, the evictor removes the key, and the read raises `KeyError: '0901.21'`. Under EAFP the single read misses and reloads.
   - No `sleep`. Every wait has a 10 s guard that a healthy run never reaches.

   **Recommend: yes.** Alternative: a `between=` hook parameter in `src` (the r01 spike's form). It adds a parameter that exists only for tests.

6. **`contextlib.suppress` stays out of `src`.**
   - `evict` uses `pop(hs_code, None)`, the non-raising method that already exists.
   - `suppress` is taught by:
     - a test showing that the block ends at the first exception, so a second statement never runs (the docs' "resumes execution with the first statement following the end of the with statement");
     - ruff's SIM105, which suggests it for `try`/`except`/`pass`.
   - "Context managers: deterministic cleanup" already quotes the docs' "very specific errors" sentence, and ch31 doesn't re-quote it.

   **Recommend: yes.** Alternative: `with suppress(KeyError): del self._rates[hs_code]` in `src`. It's correct, but less direct than `pop`.

7. **Legacy row 28's speed half is benchmark-only.**
   - `examples/31-*/bench/lookup_cost.py` (`timeit`, best of five, one million calls) prints present-key and absent-key timings for the EAFP, look-first and `get` forms.
   - Its scrubbed output goes in `_plans/evidence/eafp-lookup-cost.md`, with the Python version and date.
   - The chapter quotes that file as illustrative, and no test asserts time.
   - The row closes **adjusted (r15)**:
     - EAFP removes the gap between check and read (forced race test);
     - it doesn't make a miss load once (two readers that both miss both load, test 15);
     - it's cheaper on a hit and dearer on a miss (bench).

   **Recommend: yes.** Alternative: drop the speed half and defer it to "The GIL and performance".

8. **ch32 covers the outline's three anti-patterns, one witness set each, with the AI throughline in the sidebar (decision 2).**
   - **Over-abstraction.**
     - The `src` function `quote(consignment, tariff)` is ch1's one-carrier rating function, written in code for the first time.
     - The comparison form `rating_form` `function|engine` runs on `QUOTE_ROWS`. The engine is a conftest `_RateEngine` built from `_PricingStrategyFactory`, `_PricingStrategy`, `_FlatFeeStrategy`, `_Charge`, `_FlatFeeCharge`, `_FuelSurcharge`, `_ChargeVisitor` and `_NetTotalVisitor`, with a `get_tariff` getter.
     - The comparison excerpt is `_RateEngine.quote`.
   - **Getters and setters.** The conftest `_AccessorConsignment` has `get_zone` and `set_zone`, set against the frozen `Consignment`.
   - **Service locator.** The conftest `_ServiceLocator` (`register`, `get -> object`) and `_LocatedRateEngine(locator)`.
   - **Not covered, beyond one clause each:**
     - singleton-everything ("Singleton: module, Borg, and metaclass");
     - the one-implementation interface ("Naming patterns for teams and AI assistants", "ISP, DIP, and dependency injection without a framework", "Protocol, duck typing, and structural typing with mypy" all state it);
     - `isinstance` ladders (not in the outline; "Visitor, Memento, and Interpreter" owns `match`).

   **Recommend: yes.** Alternative: add `isinstance` ladders as a fourth witness. The word budget can't carry it, and the outline doesn't promise it.

9. **ch32 measures with stated tools, not "files touched".**
   - `ast` gives class and function counts and the lines of `ast.unparse` output with docstrings removed, for `quote` against the engine definitions. The engine names are listed in the test module as `ENGINE_DEFINITIONS`, and conftest is parsed from its path.
   - The fuel surcharge's footprint is the sorted list of definitions whose source mentions `fuel`, found with `ast.get_source_segment`.
   - Python-level calls for one quote are counted by `sys.setprofile` "call" events, filtered by `co_filename` to the `src` module or conftest, and compared as ordered `co_qualname` lists.
   - The engine lives in one conftest file, so domain row 32's "6 files touched vs 1" can't be measured. R0 adjusts the row to the measured footprint and the visitor witness.
   - No sentence claims how many tests a design "needs".

   **Recommend: yes.** Alternative: put the engine in `src` as a package of several files and diff before and after copies. That breaks the conftest comparison rule and duplicates the code.

10. **No cross-language wording in ch32.** The thesis is temporal: the class-per-role structure is what the 1994 assumptions required. Reader text never names another language, and test names avoid "Bean": `_AccessorConsignment`, not `_ConsignmentBean`. Criterion 14's grep enforces this.

    **Recommend: yes.**

11. **Scope cuts.** Recorded here and in the R2 spikes note, not in either chapter:
    - the async version of the check-then-use gap (an `await` between check and read; "asyncio and the patterns" owns it);
    - why the natural race is rare under the GIL (planning evidence H; "The GIL and performance" owns it, with one title pointer and nothing described);
    - call-once loading on a miss (one sentence pointing to "Singleton: module, Borg, and metaclass", which owns `functools.cache` not being call-once);
    - filesystem time-of-check races;
    - `except*` and exception groups under `suppress`;
    - `AttributeError.name` and `.obj` narrowing (one clause at most);
    - free-threading.

    **Recommend: yes.**

Also proposed for the owner (no decision needed unless declined):
- **No new books.**
  - `bibliography.html` has GoF, Fowler's *Patterns of Enterprise Application Architecture*, *Fluent Python* 2nd ed., *Effective Python* 3rd ed., *Architecture Patterns with Python* and Martin's *Agile Software Development*.
  - Book items stay bracketed:
    - [GoF, Visitor, Consequences: adding a new concrete element class is hard, because every visitor gains an operation; paraphrase only];
    - [Ramalho, *Fluent Python* 2nd ed., on mappings and on EAFP];
    - [Slatkin, *Effective Python* 3rd ed., on `try`/`except`/`else`];
    - [Percival and Gregory, *Architecture Patterns with Python*, on dependency injection].
  - Koenig's "Patterns and Antipatterns" (1995) and Brown et al., *AntiPatterns* (1998), aren't in the bibliography: no attribution, describe the idea only.
- **Web sources fetched 2026-11-06** (evidence N): Fowler's injection article (ch6 already cites it for injection styles, and ch32 quotes a different sentence) and Mark Seemann's "Service Locator is an Anti-Pattern".
- **At R2, a dated r15 note in `_plans/spikes.md`** records evidence D, F, H and K and the `frozendict` key-error code difference (evidence B).

## Planning evidence

The planning run was read-only, so no scratch directory was created. Every probe ran as inline code with the session scratchpad (`<scratchpad>`) as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `<repo>/.venv/bin/python -I -c CODE`, version `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- mypy: `<repo>/.venv/bin/python -I -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET`, version `mypy 2.4.1 (compiled: yes)`.
- ruff: `<repo>/.venv/bin/ruff check --isolated --no-cache --line-length 100 --select E,F,W,I,UP,B,SIM,RUF,PT,N --target-version py315 --output-format concise --stdin-filename probe.py -`, version ruff 0.17.4. One probe added `BLE,TRY,PERF`. `python -I -m ruff` with the same arguments and stdin also works (evidence F), which the ruff witness tests use.

Snippets are reduced models. Line numbers will differ and are never asserted. Every output is a prediction for the member until the build quotes it as observed.

**A. Pins.** `pytest 9.2.0 2026-10-27`, `pytest-mock 3.17.0 2026-10-17`, `ruff 0.17.4 2026-11-05`, `mypy 2.4.1 2026-10-28`, `uv 0.13.7 2026-11-03`, `uv-build 0.13.7 2026-11-03`. python.org: 3.15.0, 3.15.1, 3.15.2. No bump.

**B. mypy on dispatch tables.** `DocumentKind` (three members), `type Renderer = Callable[[Doc], str]`, and a table annotated `Mapping[DocumentKind, Renderer]`. Exit 1:
```
<string>:28: note: Revealed type is "frozendict[__main__.DocumentKind, def (d: __main__.Doc) -> str]"
<string>:29: error: Dict entry 0 has incompatible type "DocumentKind": "Callable[[Doc, int], str]"; expected "DocumentKind": "Callable[[Doc], str]"  [dict-item]
<string>:30: error: Dict entry 0 has incompatible type "DocumentKind": "Callable[[Doc], int]"; expected "DocumentKind": "Callable[[Doc], str]"  [dict-item]
<string>:31: error: Incompatible types in assignment (expression has type "frozendict[str, Callable[[Doc], str]]", variable has type "Mapping[DocumentKind, Callable[[Doc], str]]")  [assignment]
<string>:32: error: Dict entry 0 has incompatible type "DocumentKind": "Callable[[Doc, int], str]"; expected "DocumentKind": "Callable[[Doc], str]"  [dict-item]
<string>:33: error: Dict entry 0 has incompatible type "DocumentKind": "Callable[[Doc, int], str]"; expected "DocumentKind": "Callable[[Doc], str]"  [dict-item]
<string>:34: error: Invalid index type "str" for "Mapping[DocumentKind, Callable[[Doc], str]]"; expected type "DocumentKind"  [index]
<string>:36: note: Revealed type is "(def (__main__.Doc) -> str) | None"
<string>:38: error: Unsupported target for indexed assignment ("frozendict[DocumentKind, Callable[[Doc], str]]")  [index]
```
- **Wrong signatures.** Line 29 has an extra parameter, line 30 the wrong return type, and lines 32-33 have the same entries in a dict literal and in `MappingProxyType`. All give `[dict-item]`.
- **Wrong key type.**
  - A string key in a `frozendict(...)` literal gives `[assignment]`, where a dict literal and `MappingProxyType` give `[dict-item]`. A separate probe confirmed this, including `frozendict(manifest=bl)`. It's a code difference, not a defect.
  - A string index gives `[index]`.
- **A missing key gives nothing.** Line 35, `RENDERERS[DocumentKind.CUSTOMS_DECLARATION]` on a two-entry table, has no error. Totality needs a test.
- `frozendict` is typed generically by mypy 2.4.1 on 3.15, with no ignores.

**C. Table messages at run time.**
```
KeyError: <DocumentKind.CUSTOMS_DECLARATION: 'customs-declaration'>
TypeError: 'frozendict' object does not support item assignment
TypeError: 'mappingproxy' object does not support item assignment
TypeError: 'frozendict' object does not support item deletion
<class 'frozendict'> False True
['BILL_OF_LADING', 'CUSTOMS_DECLARATION']
```
- `isinstance(t, dict)` is `False`, and `isinstance(t, collections.abc.Mapping)` is `True`.
- `frozendict(a=1) | {"b": 2}` is a new `frozendict`.
- The totality probe `sorted(k.name for k in DocumentKind if k not in t)` prints a list, never a set. The member's `KeyError` repr uses ch26's values, for example `'customs declaration'`.

**D. Totality: if-chains and `match` under mypy.** Exit 1:
```
<string>:9: error: Missing return statement  [return]
<string>:23: error: Missing return statement  [return]
<string>:36: error: Argument 1 to "assert_never" has incompatible type "Literal[DocumentKind.CUSTOMS_DECLARATION]"; expected "Never"  [arg-type]
<string>:38: error: Missing return statement  [return]
```
- **Reported:**
  - a two-arm `is` chain with no `else` (line 9);
  - a two-arm `==` chain with no `else` (line 23);
  - a two-arm `match` with `assert_never` (line 36);
  - a two-arm `match` without it (line 38).
- **Silent:** a two-arm chain ending in `else: raise ValueError(kind)`, the defensive form.
- A dict is silent too (evidence B). The if-chain that misses a new kind (domain row 31) is therefore the raising-`else` chain, which mypy accepts and the run time refuses.

**E. Writing into the table, `.get`, `singledispatch` on enum values, and parsing.** mypy, exit 1:
```
<string>:10: error: Unsupported target for indexed assignment ("Mapping[DocumentKind, Callable[[str], str]]")  [index]
<string>:12: error: "None" not callable  [misc]
<string>:13: note: Revealed type is "def (str) -> str"
```
`.get(kind, default_issuer)` is typed without `None`.

Run time:
```
['one implementation', 'one implementation']
['DocumentKind', 'object']
DocumentKind.MANIFEST True False
ValueError: 'nope' is not a valid DocumentKind
```
- `singledispatch` registers `DocumentKind` as one type, so every member reaches one implementation: it dispatches on type, not value.
- `"manifest" in DocumentKind` tests values on 3.15.

**F. ruff.**

Root rule set:
```
probe.py:5:8: SIM118 [*] Use `key in dict` instead of `key in dict.keys()`
probe.py:11:5: SIM108 Use ternary operator `rate = cache[code] if code in cache else 0` instead of `if`-`else`-block
probe.py:11:5: SIM401 Use `rate = cache.get(code, 0)` instead of an `if` block
probe.py:19:5: SIM105 Use `contextlib.suppress(KeyError)` instead of `try`-`except`-`pass`
probe.py:26:5: SIM116 Use a dictionary instead of consecutive `if` statements
probe.py:38:5: E722 Do not use bare `except`
```
- SIM116 fired on three `==` comparisons against string literals.
- A look-first `if code in cache.keys(): return cache[code]` gets SIM118 only. SIM401 needs the assignment form.
- `except Exception` passes the root rules.

With `BLE,TRY,PERF` added, only this fires:
```
probe.py:41:12: BLE001 Do not catch blind exception: `Exception`
```
- An enum chain (`is` or `==` against `DocumentKind` members, three arms) gets no SIM116.
- A `try` around `table[kind](ref)` with `except KeyError` gets nothing, not even TRY300.

The rule names come from `ruff rule`:
- SIM401 `if-else-block-instead-of-dict-get`
- SIM116 `if-else-block-instead-of-dict-lookup`
- SIM105 `suppressible-exception`
- SIM118 `in-dict-keys`
- BLE001 `blind-except`
- TRY300 `try-consider-else`
- PERF203 `try-except-in-loop`

**G. The forced race.**

Hook model (`between=` after the check, `Barrier(2)` waited twice, evictor pops in the gap):
```
lbyl (["KeyError: '0901.21'"], [], {})
eafp ([Decimal('8.0')], ['0901.21'], {'0901.21': Decimal('8.0')})
get_form ([Decimal('8.0')], ['0901.21'], {'0901.21': Decimal('8.0')})
200 ok
```
Storage-seam model (decision 5; `_HandoverRates` parks the first `__contains__` after answering, or the first `__getitem__` before reading):
```
lbyl (["KeyError: '0901.21'"], [], {})
eafp (['8.0'], ['0901.21'], {'0901.21': Decimal('8.0')})
300 ok
```
Exceptions are caught inside the reader thread and recorded as strings, so pytest's unhandled-thread-exception warning, which `filterwarnings = ["error"]` would turn into a failure, never fires.

**H. The natural race (not used in prose as a number).** Two threads with no seam:
```
0.005 [0, 0, 0, 0, 0]
1e-06 [0, 0, 0, 0, 0]
call-between 0.005 [0, 0, 0, 0, 0]
call-between 1e-06 [0, 0, 0, 0, 0]
```
- Each line is five runs of 200,000 checks. One thread checks `"k" in cache` and then reads it. The other adds and pops `"k"` in a loop.
- The runs used switch intervals of 5 ms and 1 µs, with and without a call between check and read. `sys._is_gil_enabled()` is `True`.
- Zero `KeyError`s. This is consistent with the r01 finding for `+=`. The test forces the race. The prose says the seam forces what timing can't, and points to "The GIL and performance" once by title.

**I. Lookup cost (illustrative, recorded only, never asserted).** `timeit`, best of five repeats of one million calls:
```
0901.21 eafp     30.6 ns/call
0901.21 lbyl     45.2 ns/call
0901.21 get      36.9 ns/call
6109.10 eafp    123.4 ns/call
6109.10 lbyl     30.4 ns/call
6109.10 get      34.7 ns/call
```
The first three are present keys and the last three absent ones. R1a re-measures through `bench/lookup_cost.py`, and the chapter quotes only `_plans/evidence/eafp-lookup-cost.md`.

**J. Errors that `getattr` defaults, `hasattr` and `suppress` hide.** A frozen `CustomsDeclaration` whose `duty` property reads a missing `self.rate`:
```
getattr default: 0
hasattr: False
AttributeError: 'CustomsDeclaration' object has no attribute 'rate' | name: rate | obj is d: True
narrowed re-raises: 'CustomsDeclaration' object has no attribute 'rate'
suppress ok
```
- The default and `hasattr` both hide the bug. Direct access names `rate`, not `duty`.
- A narrowed handler (`e.name != "duty"`) re-raises. This is a scope cut beyond one clause.

**K. The ch32 model** (decisions 8 and 9). The function form is `quote` over a frozen `Tariff(flat_fee_by_zone: frozendict[str, Decimal], fuel_fee, tax_rate, currency)`, with tax quantised to the cent. The engine has nine classes. Zones `EU` 25.00 and `ASIA` 60.00, fuel 4.50, tax 0.21:
```
EU RateQuote(consignment_id='CN-1', total=Money(amount=Decimal('35.70'), currency='EUR')) True
ASIA RateQuote(consignment_id='CN-1', total=Money(amount=Decimal('78.05'), currency='EUR')) True
function (0, 1, 5) engine (9, 17, 52)
fuel footprint function ['quote']
fuel footprint engine ['_ChargeVisitor.visit_fuel', '_FlatFeeStrategy.charges', '_FuelCharge', '_FuelCharge.accept', '_NetTotalVisitor.visit_fuel']
4 ['<lambda>', 'quote', '__create_fn__.<locals>.__init__', '__create_fn__.<locals>.__init__']
14 ['<lambda>', '_RateEngine.quote', '_NetTotalVisitor.__init__', '_FlatFeeStrategy.charges', '_FlatFeeCharge.__init__', '_FuelCharge.__init__', '_FlatFeeCharge.accept', '_NetTotalVisitor.visit_flat_fee', '_FuelCharge.accept', '_NetTotalVisitor.visit_fuel', '_RateEngine.get_tariff', '_RateEngine.get_tariff', '__create_fn__.<locals>.__init__', '__create_fn__.<locals>.__init__']
```
- **What the counts mean.** The triples are classes, functions and non-blank lines.
  - The member counts lines of `ast.unparse` output without docstrings, so its numbers will differ.
  - Each quote matches across the forms (`True`).
- **Call counts.**
  - Without the test's own lambda and the generated dataclass `__init__`s, the function makes 1 call and the engine 11.
  - The member filters by `co_filename`, because generated dataclass `__init__`s report `__create_fn__.<locals>.__init__`, an implementation detail.
- **Names.** The member renames `_FuelCharge` to `_FuelSurcharge` (decision 8), which keeps "fuel" in its name.

**L. mypy and ruff on the engine; the cost of a new charge kind.**
- **mypy on the whole model** (domain, function and nine-class engine): `mypy exit 0`.
- **ruff on the same model:** `I001`, and `UP037` three times on quoted forward references. All are fixable. Nothing names the structure. No type checker or linter reports over-abstraction.
- **A new charge kind** (`accept` calls `visitor.visit_remote_area`), then the method declared abstract on a visitor subclass:
  ```
  <string>:16: error: "_ChargeVisitor" has no attribute "visit_remote_area"  [attr-defined]
  <string>:24: error: Cannot instantiate abstract class "_NetTotalVisitor" with abstract attribute "visit_remote_area"  [abstract]
  ```
- **The same at run time:**
  ```
  AttributeError: '_ChargeVisitor' object has no attribute 'visit_remote_area'
  TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'
  ```

**M. Service locator and accessors.** mypy, exit 1:
```
<string>:17: error: Returning Any from function declared to return "Decimal"  [no-any-return]
<string>:17: error: "object" has no attribute "price_for"  [attr-defined]
<string>:24: error: Missing positional argument "tariff" in call to "quote"  [call-arg]
```
- `quote_located_checked("EU")` (line 25) narrows with `isinstance` and gets no error, though nothing is registered.
- At run time a missing parameter is `TypeError: quote() missing 1 required positional argument: 'tariff'`. The located call raises `KeyError: 'tariff'` at first use; the member's test confirms the message.

Accessors:
```
bean eq False hashable True
dc eq True
FrozenInstanceError: cannot assign to field 'weight_kg'
```
The member's accessor class is `_AccessorConsignment` with a `zone`, and the message becomes `cannot assign to field 'zone'`.

**N. Sources fetched 2026-11-06.** curl with `-L`, tags stripped, whitespace collapsed. Prose agents re-fetch, the page text wins, and a quotation stops where the page's sentence stops. Curly quotes are kept as on the page.
- **Glossary** (https://docs.python.org/3/glossary.html, banner "Python 3.15.2 documentation"):
  - EAFP: "Easier to ask for forgiveness than permission." and "This common Python coding style assumes the existence of valid keys or attributes and catches exceptions if the assumption proves false."
    - Don't quote "This clean and fast style ...": "fast" is benchmark-only (decision 7).
    - Don't quote the sentence naming another language.
  - LBYL: "Look before you leap." and "In a multi-threaded environment, the LBYL approach can risk introducing a race condition between “the looking” and “the leaping”."
    - The next sentence (`if key in mapping: return mapping[key] can fail if another thread removes key from mapping after the test, but before the lookup.`) may be quoted: it's exactly test 13.
    - "This issue can be solved with locks or by using the EAFP approach."
- **Built-in functions** (https://docs.python.org/3/library/functions.html):
  - `hasattr`: "(This is implemented by calling getattr(object, name) and seeing whether it raises an AttributeError or not.)"
  - `getattr`: "If the named attribute does not exist, default is returned if provided, otherwise AttributeError is raised."
- **Built-in types** (https://docs.python.org/3/library/stdtypes.html):
  - `dict.get`: "Return the value for key if key is in the dictionary, else default. If default is not given, it defaults to None, so that this method never raises a KeyError."
  - `frozendict`: "A frozendict has a similar API to the dict API, with the following differences:" (stop at "differences").
- **contextlib** (https://docs.python.org/3/library/contextlib.html), `suppress`: "Return a context manager that suppresses any of the specified exceptions if they occur in the body of a with statement and then resumes execution with the first statement following the end of the with statement." The "very specific errors" sentence is already quoted by "Context managers: deterministic cleanup"; don't re-quote it.
- **Compound statements** (https://docs.python.org/3/reference/compound_stmts.html), `try`: "Exceptions in the else clause are not handled by the preceding except clauses."
- **types** (https://docs.python.org/3/library/types.html), `MappingProxyType`: "Read-only proxy of a mapping."
- **Library FAQ** (https://docs.python.org/3/faq/library.html), "What kinds of global value mutation are thread-safe?": "In practice, it means that operations on shared variables of built-in data types (ints, lists, dicts, etc) that “look atomic” really are." Use at most once in ch31, and only if the word budget allows. Point to "The GIL and performance" for the rest.
- **PEP 814**, "Add frozendict built-in type" (Victor Stinner, Donghee Na; Final; Python 3.15): "A new public immutable type frozendict is added to the builtins module." The Strategy and State chapters cite PEP 814 by number only; ch31 credits the authors.
- **PEP 8** (https://peps.python.org/pep-0008/; Guido van Rossum, Barry Warsaw, Alyssa Coghlan): "For simple public data attributes, it is best to expose just the attribute name, without complicated accessor/mutator methods." and "In that case, use properties to hide functional implementation behind simple data attribute access syntax."
- **Martin Fowler, "Inversion of Control Containers and the Dependency Injection pattern"** (https://martinfowler.com/articles/injection.html): "The basic idea behind a service locator is to have an object that knows how to get hold of all of the services that an application might need." and "The key difference is that with a Service Locator every user of a service has a dependency to the locator." The ISP and DIP chapter cites the article for injection styles and quotes neither sentence.
- **Mark Seemann, "Service Locator is an Anti-Pattern"** (https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/, 2010): "In short, the problem with Service Locator is that it hides a class' dependencies, causing run-time errors instead of compile-time errors, as well as making the code more difficult to maintain because it becomes unclear when you would be introducing a breaking change." Quote only up to "compile-time errors," and say once that in this book the static check is mypy.
- **GoF** isn't quotable (r06 finding). The Visitor consequence is paraphrased only, and only if checked at validation.

**O. Repo facts.**
- **Reconciliation.**
  - Rows run 1-173, so r15 adds 174-187.
  - Legacy row 28 (ch31: "EAFP beats LBYL for shared mutable state and costs little when the key is present") is the only open legacy row for ch31 or ch32. `CLAIMS_FIRST_ENFORCED = 47`, so it's legacy.
  - Row 25 (ch40: LLM output) is not touched.
- **Figures.** `_data/diagrams.yml` has 31 entries; r15 makes 33.
- **Test names.**
  - 737 unique `def test_` names across `examples` and `spikes`, with the three known duplicates unchanged.
  - All names in the Example spec were checked, and none clashes.
  - Near-misses not reused:
    - `test_suppress_swallows_only_the_named_exception` (ch10);
    - `test_an_unknown_zone_is_a_rating_error` (ch18);
    - `test_mypy_reports_a_visitor_class_missing_a_visit_method` (ch25);
    - `test_the_carrier_registry_is_a_read_only_view` (ch29);
    - `test_an_unknown_rule_name_is_a_rating_error` (ch12).
- **Promises made to these chapters, which ch31 must honour:**
  - "The three-way split" (objective, map row, "Beyond the catalogue"): dict dispatch and EAFP; "a missing key is handled by the exception or by `.get`"; "Keep the branch when cases need different arguments or the order of the tests matters".
  - "Strategy: the callable" and "State and finite state machines" each say "For dispatch tables as a general technique, see" this chapter.
  - "singledispatch: the Visitor the language gives you": "Dispatch on a value, such as a service level, is a lookup in a mapping, and [this chapter] is the place to look."
  - The part blurb: "The shortcuts Python offers in place of full patterns (dict dispatch, function tables, EAFP) and the anti-patterns that come from misusing the catalogue."
  - **Circularity rule.** The Strategy, State and singledispatch chapters defer the general technique here, so ch31 owns it and never points back to them for it. ch31 points to "Visitor, Memento, and Interpreter" for `match` with `assert_never`, and to "singledispatch: the Visitor the language gives you" for dispatch on type. Neither defers those topics back.
  - No chapter points to ch32, so it has no circular pointers.
- **Already taught, so not repeated.** Each gets a pointer by title and at most one sentence:
  - "Context managers: deterministic cleanup": `suppress` narrows one exception, plus the docs' "very specific errors" sentence.
  - "Strategy: the callable": `RATE_RULES` over `frozendict` and `RatingError ... from None`. Not pointed to (circularity).
  - "Dynamic attributes: __getattr__ and Proxy as a feature": `hasattr` triggers a load. ch31's `hasattr` point is different (a property's bug hidden); no pointer is needed.
  - "Patterns as decisions under forces": the rating forces, the one-carrier case and the count-the-edits test. ch32 points to it, and its function is that chapter's argued function.
  - "Dataclasses and value semantics": frozen dataclasses.
  - "Descriptors and properties": `property`.
  - "ISP, DIP, and dependency injection without a framework": injection, Fowler's article and the composition root.
  - "Singleton: module, Borg, and metaclass": module globals and call-once.
  - "Visitor, Memento, and Interpreter": Visitor dissolving.
  - "Factory Method and Abstract Factory": factories as functions.
  - "Naming patterns for teams and AI assistants": one implementation means the name is premature.
- **Stubs whose ground must not be taken or described:**
  - "Seams in Python" and "Dependency-breaking techniques": the legacy `RateEngine` and `monkeypatch`. ch32's engine is the test-only `_RateEngine` and has nothing to do with the legacy one.
  - "Fowler vs Feathers" and "Refactor or rewrite".
  - "The GIL and performance": GIL mechanics and the rarity of natural races.
  - "asyncio and the patterns": the `await` gap.
  - "Working with AI and LLM tools": reviewing generated code, legacy row 25.
  - "Final project".
- **Status board hygiene.** r14 is merged (dfec2a8), but r14's Q7 still reads `todo`, PDP-129a to PDP-130c read `active`, and `iteration-plan.md` marks r14 "(active)". The orchestrator closes them at R0.

## What is new in each chapter

**ch31 (if-chain dispatch dissolves; EAFP is the idiom).** "The three-way split" gives two sentences, and three chapters defer "dispatch tables as a general technique" here. This chapter adds:
- **A table of callables over an enum.** It's read-only (`frozendict`). mypy checks the signatures and key types of the entries, but not totality, so a test covers totality.
- **Choosing between a table, `match` and `singledispatch`.**
  - mypy reports a missing arm in `match` and in a chain without `else`, but not in a chain whose `else` raises.
  - A table wins when the set is data: passed by the caller, parsed from text, or walked by a test.
  - `singledispatch` dispatches on type, so every enum member reaches one implementation.
- **Narrow `try`.** Only the lookup goes inside it, so an issuer's own `KeyError` isn't reported as an unknown kind.
- **EAFP on fields and shared state.**
  - A missing required field names itself, and an optional one is read with `.get`.
  - `getattr` defaults and `hasattr` hide a property's bug.
  - `suppress` ends its block at the first exception.
  - ruff's SIM rules point at the idioms.
- **The look-first race.** It's forced through a storage seam: the look-first form raises, and EAFP reloads. EAFP still loads twice when two readers miss. The cost is benchmark-only.

**ch32 (an argument: measure the structure against the forces).** "Patterns as decisions under forces" argues the one-carrier case in prose. This chapter writes it in code and measures it:
- **The rating function and a class-per-role engine.** The engine is a factory of strategies of visitors for a flat fee, and both pass the same table.
- **What the structure costs, measured.** Classes, functions and lines (by `ast`); the fuel surcharge in one definition against five; Python calls per quote; and mypy and ruff passing both.
- **What a new charge costs.** The visitor fails at run time, and declaring the method makes every concrete visitor abstract.
- **Getters and setters.** An accessor consignment has no value equality and lets a quoted consignment change. PEP 8 says expose the attribute and grow it into a property.
- **A service locator.** It moves a missing dependency from mypy to the first quote, and needs a type check to use what it returns.
- **When the structure earns its place.** The forces from "Patterns as decisions under forces".

## Approach

- **Thesis wording.**
  - ch31 says if-chain dispatch dissolves into a table of callables. What remains is totality, which a test checks because mypy doesn't, and where the `try` goes. EAFP is the idiom for reading fields and shared state: one operation and no gap.
  - ch32 says an anti-pattern is a structure kept after its forces left. The measure is the plain function against the same table, with counts that tools don't report.
- **Credit.**
  - PEP 814 (Stinner and Na) and PEP 8 (van Rossum, Warsaw, Coghlan) by author and title.
  - The glossary, built-ins, built-in types, contextlib, compound statements, types and library FAQ pages.
  - Fowler's injection article and Seemann's post by author and title.
  - GoF and book items only if verified (bracketed). Every quotation is exact, from fetched pages.
- **Domain names** come from `_plans/shipping-domain-model.md` rows 31-32, the area table and the series supporting names, plus the names in decisions 3 and 8, recorded at R0. There's no new domain area and no new carrier code.
  - **ch31** (Documentation area, with Rating's `RatingError` unused):
    - `ConsignmentId`, `DocumentKind`, `DocumentIssuer` (new), `ISSUERS` (new), `issue`, `parse_kind` (new), `UnsupportedDocumentError` (new);
    - `CustomsDeclaration`, `CustomsError`, `declaration_from` (new);
    - `DutyRateCache` (new), `duty_for` (new).
    - Test-only: `_LookFirstDutyRateCache`, `_HandoverRates`, `_issue_broadly`, `_issue_by_chain`, `_DutyBearingDeclaration`.
  - **ch32** (Rating area):
    - `ConsignmentId`, `Money`, `Consignment` (`id`, `zone`), `Tariff`, `RateQuote`, `RatingError`, `quote`.
    - Test-only: `_RateEngine`, `_PricingStrategyFactory`, `_PricingStrategy`, `_FlatFeeStrategy`, `_Charge`, `_FlatFeeCharge`, `_FuelSurcharge`, `_ChargeVisitor`, `_NetTotalVisitor`, `_AccessorConsignment`, `_ServiceLocator`, `_LocatedRateEngine`.
- **One uv member per chapter.** Each is standalone and named after its package (the r13 correction), so no member needs a `[tool.*]` table:
  - `examples/31-shortcut-patterns-dict-dispatch-and-eafp` (project `shortcut-patterns`, package `shortcut_patterns`), plus `bench/lookup_cost.py`;
  - `examples/32-anti-patterns-and-pattern-misuse` (project `pattern-misuse`, package `pattern_misuse`).
- **mypy witnesses** copy the r14 `_run` helper from `examples/30-dynamic-attributes-and-proxy/tests/test_static.py`: `mypy_path` set to the member's `src` and `--cache-dir os.devnull`.
  - **Change from r14:** `_codes(stdout)` returns `sorted(set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)))`, a list. A failing assertion then prints in a fixed order, because a set of strings prints in a per-process hash order (r14 Q5).
  - Each test asserts the exit status, an exact `_codes()` list and one or two stable substrings. It never asserts line numbers or optional notes.
- **ruff witnesses** run `sys.executable -I -m ruff check --isolated --no-cache --select SIM,E722 --output-format concise --stdin-filename probe.py -` with the snippet on stdin and `check=False`. They assert the sorted list of codes parsed from `^probe\.py:\d+:\d+: ([A-Z]+\d+) ` and nothing else.
- **Static-test mutation rule (r12-r14).** Every static test names, in the Example spec, the thing its prose credits and a plausible mutation of that thing that makes the test fail.
  - **An exit-0 test also exercises the hazard at run time.** It `exec`s the snippet in a fresh namespace, or runs the `src` call it type-checks, and asserts `_codes(stdout) == []`.
  - A reduced-model test credits mypy only, and the prose names it as a reduced model.
- **Repair rule (r12).** After every repair, the validator re-reads the paragraph and the close bullets that depend on it. Scope words ("every", "only", "never", "all", "both", "silently", "race-free") each name the test that witnesses the whole scope, or are cut. "Race-free" may not appear: EAFP removes one gap (test 14), not every race (test 15).
- **Excerpt rule.** No excerpt can break an owner decision:
  - no `suppress` in a ch31 `src` excerpt;
  - no hook parameter in `DutyRateCache`;
  - no second comparison excerpt;
  - no ch32 excerpt from the engine other than `_RateEngine.quote`;
  - no reader-facing text naming another language.

  R6 checks each excerpt against decisions 4-10.
- **Comparison code** (the owner's 2026-11-04 rule). Every comparison form is real, runs on the shared table as a conftest fixture param, and appears in at most one excerpt per chapter (decisions 4 and 8). Shared row tables live in the test module that uses them; conftest holds only fixtures and forms (the r13 importlib correction). Test modules import conftest types only under `TYPE_CHECKING` and get classes through fixtures (the r14 Q1a precedent).
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (R1a, R1b) name the test and say why it sees the deletion. A row whose witness was predicted but not run is marked "executor check".
- **Determinism.**
  - No `mock`, `mocker`, `monkeypatch`, `print(` (outside `bench/`), `sleep`, `time.time`, `perf_counter` or `datetime.now` in tests.
  - Threads catch exceptions inside the thread and record a string.
  - Every `Barrier` has `timeout=10`, and every `join` has `timeout=30`.
  - Failing assertions compare lists or tuples of strings, never a set repr.
  - `sys.setprofile` is set and cleared in a `try`/`finally` inside one test, and filtered by `co_filename`.
  - `filterwarnings = ["error"]` stays active.
- **Counts** of test functions and cases come from the code, and the pytest summary line wins.

Rejected:
- In ch31's `src`: `suppress`, a hook parameter, `hasattr`, `getattr` with a default, `except Exception`, `match`, `singledispatch`, `isinstance`, `Any`, `cast`, `TYPE_CHECKING`.
- Anything in ch32's `src` but the rating function and its domain types.
- Measuring "files touched".
- Claims about model output.
- Timing in tests.

## Per-chapter spec

### ch31: Shortcut patterns: dict dispatch, function tables, and EAFP (pattern, has_example = true, bucket: dissolves)

Thesis: an if-chain that picks behaviour by a value dissolves into a read-only table of callables. What remains to design:
- totality: mypy checks every entry's type but not that every kind has one, so a test does;
- where the `try` goes: around the lookup only;
- how shared state is read: once, asking forgiveness, because a check followed by a read leaves a gap another thread can use.

Sections (about 2,450 prose words, max 2,500; at most six excerpts, at most one from a comparison fixture):

1. `## Learning objectives` (~100), five bullets, one per close bullet:
   - replace an if-chain over document kinds with a read-only table of callables, and test that it covers every kind;
   - choose between a table, `match` and `singledispatch` by what is dispatched on and who owns the set;
   - keep only the lookup inside `try`, so a handler's own errors pass through;
   - read fields EAFP-style, and say when `.get`, `getattr` defaults, `hasattr` and `suppress` hide errors;
   - force a check-then-read race with a seam and show which form survives it.
2. `## Why this matters` (~170). Intent first: a consignment needs a bill of lading, a manifest and a customs declaration issued by kind, and duty rates are read from a cache other threads evict from. Three failures:
   - an if-chain whose `else` raises misses a kind that was added later, and mypy accepts it (tests 8, 26);
   - a `try` around the whole call reports an issuer's bug as an unsupported kind (test 6);
   - a look-first read raises when another thread evicts between check and read (test 13).
3. Figure plus one paragraph (~50).
4. `## A table of callables` (~380). Excerpt `ISSUERS` and `issue`.
   - Bucket sentence: dissolves. One pointer to "The three-way split: dissolve, survive, disambiguate".
   - PEP 814 (Stinner and Na) sentence. The table is read-only (test 4), each kind issues its reference (test 2), and a missing kind raises `UnsupportedDocumentError` with the `KeyError` suppressed (test 3).
   - mypy checks an entry's signature (test 22), a lookup's key type (test 23), assignment (test 27) and the `None` from `.get` (test 28). It accepts a table that misses a kind (test 24), so `test_every_document_kind_has_an_issuer` (test 1) guards totality.
   - Quote the `types` "Read-only proxy" sentence only if `MappingProxyType` is mentioned; the member uses `frozendict`.
5. `## Table, match or singledispatch` (~300):
   - mypy reports a missing arm in a `match` with `assert_never` and in a chain without `else`, but accepts a chain whose `else` raises (tests 25, 26, reduced models). One pointer to "Visitor, Memento, and Interpreter".
   - A table wins when the set is data: a caller passes another table (test 7), and a kind arrives as text (tests 10, 11).
   - `singledispatch` dispatches on type, so every member of `DocumentKind` reaches one implementation (test 9). One pointer to "singledispatch: the Visitor the language gives you".
   - ruff suggests a dictionary for a chain over string literals, not over enum members (test 29).
   - Where cases need different arguments, keep the branch. This honours the three-way split chapter's sentence; say it without pointing back.
6. `## Asking forgiveness` (~330):
   - Quote the glossary's EAFP definition and its "assumes the existence of valid keys or attributes" sentence.
   - `declaration_from` reads required fields with `try`/`except KeyError` and names the missing one (tests 17, 18), and reads the optional `origin` with `.get`. Quote the `dict.get` sentence.
   - The `try` holds only the lookup: an issuer's own `KeyError` passes through `issue` (test 5), and `_issue_broadly` reports it as an unsupported kind (test 6). Quote the compound-statements `else` sentence for the `try`/`except`/`else` form.
   - ruff's root rules flag neither form (evidence F).
7. `## Exceptions that hide bugs` (~250):
   - `getattr` with a default and `hasattr` both turn a property's own `AttributeError` into "absent" (test 19). Quote the built-ins `hasattr` sentence.
   - `suppress` ends its block at the first exception, so a second statement never runs (test 20). Quote the contextlib "resumes execution" sentence. One pointer to "Context managers: deterministic cleanup" for narrowing it to one exception.
   - ruff points at the idioms: SIM118, SIM401 and SIM105 (test 30). `except Exception` passes the root rule set (BLE001 isn't selected). Say so in one clause.
8. `## The look-first race` (~330). The comparison excerpt is `_LookFirstDutyRateCache.rate_for`.
   - Both forms pass the same table (tests 12, 16).
   - Quote the glossary's LBYL race sentence and its `if key in mapping` sentence.
   - A storage seam parks the first read until an evictor has run. The look-first form raises `KeyError` (test 13), and EAFP reloads (test 14). Say that the test forces the interleaving because waiting for it is unreliable. One title pointer to "The GIL and performance", describing nothing.
   - Scope: EAFP removes this gap, but two readers that both miss both load (test 15). One pointer to "Singleton: module, Borg, and metaclass" for loading once.
   - Cost: quote `_plans/evidence/eafp-lookup-cost.md` as illustrative, with version and date. A hit is cheaper and a miss dearer (decision 7). No test asserts it.
9. `## When not to use it` (~150):
   - two or three cases that need different arguments or a fixed order (keep the branch);
   - a closed set where mypy should report a missing kind (`match` with `assert_never`);
   - an open set extended by type (`singledispatch`);
   - an operation that does work before it fails, or a miss that's common and costly to handle, where a check first is clearer.

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Specifying a dispatch table.** Asked to "handle each document kind", an assistant can write an if-chain whose `else` raises, which mypy accepts when a kind is added. Paste a prompt that states the form:

   > Dispatch on `DocumentKind` through a read-only `frozendict` typed `Mapping[DocumentKind, DocumentIssuer]`, with a test that every kind has an entry. Put only the lookup inside `try`/`except KeyError`, raise `UnsupportedDocumentError` from `None`, and call the issuer outside the `try`. Read shared state with one lookup in `try`/`except KeyError`, never `in` followed by indexing, and don't use `getattr` defaults or `hasattr` on properties.

   If the reply wraps the call in the `try`, ask which `KeyError` it means to catch.</blockquote>

   The sidebar body is at most 120 words by `validate.word_count`. Every backticked name exists in `src` or the standard library. The opening sentence describes a form, not what assistants do. R6 rewords it if it reads as a claim about model behaviour.
10. `## Build, run, observe` (~180 plus output).
    - Each experiment runs in a fresh scratch copy: delete the copy's `.venv`, run `uv sync --locked --all-packages`, and confirm `shortcut_patterns.__file__` points into the copy.
    - Each changes one thing, then is reverted.
    - Each states, in the chapter, the filter `uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|tests/.*Error$|[0-9]+ (passed|failed|errors?))'`, followed by `uv run mypy --strict src tests`. pytest prints exception lines with `E` and three spaces and continuation lines with seven or nine; each width is a separate alternative (r13 and r14 corrections).
    - The chapter quotes the complete filtered output.

    Experiments:
    - (a) In `issue`, move the call into the `try` (`return issuers[kind](consignment_id)` inside it).
      - Expected: test 5 fails with `UnsupportedDocumentError: no issuer for 'manifest'` where `KeyError` was expected. mypy exits 0, and ruff stays silent.
      - Executor check: the exact `E` lines and whether pytest prints the module-qualified exception name.
    - (b) In `DutyRateCache.rate_for`, replace `try`/`except KeyError` with `if hs_code in self._rates: return self._rates[hs_code]` before the load.
      - Expected: test 14 fails, showing the recorded `KeyError: '0901.21'`. Every table row still passes. mypy exits 0.
      - Executor check: run the filter twice and confirm identical output apart from the duration.
11. `## What you can do now` (~130): five bullets, one per objective, in the same order. They name:
    - `ISSUERS` with test 1;
    - tests 25 and 9;
    - `issue` with test 5;
    - test 19;
    - `DutyRateCache` with tests 13 and 14.

    Every backticked token in the close appears earlier in the chapter.
12. `## For deeper coverage` (~100):
    - the glossary entries EAFP, LBYL and thread-safe;
    - the `dict`, `frozendict` and `contextlib` pages;
    - PEP 814 and PEP 8 (not needed here; ch32 cites it);
    - [Ramalho, *Fluent Python* 2nd ed., on mappings, if verified];
    - [Slatkin, *Effective Python* 3rd ed., on `try`/`except`/`else`, if verified];
    - the bibliography link.

Figure `31-shortcut-patterns-dict-dispatch-and-eafp` (vertical, two lanes):
- **Left lane, top:** `issue(kind, consignment_id)`, then the accent box `issuers[kind]` with "one lookup inside try; KeyError becomes UnsupportedDocumentError", then `issuer(consignment_id)` with "outside the try: its own errors pass through", then "reference".
- **Left side box:** `ISSUERS` with "frozendict, read-only; a test checks every DocumentKind".
- **Right lane, top:** `DutyRateCache.rate_for(hs_code)`. It splits:
  - a muted, dashed box "look first: in, then read; an eviction in the gap raises KeyError";
  - an accent box "ask forgiveness: read once; on KeyError, load and store".
- No digits in the SVG.

Caption draft (about 40 words with the prefix): "Figure 31.1: Issuing a document looks the kind up once in a read-only table and calls the issuer outside the try. Reading a duty rate asks forgiveness, so an eviction can't land between a check and the read." R3 counts and adjusts.

### ch32: Anti-patterns and pattern misuse (argument, has_example = true)

Thesis: an anti-pattern here is a pattern's structure kept after its forces have gone. The test is the one from "Patterns as decisions under forces": price the same consignments with the plain function and with the class-per-role design, count what each costs, and ask which change the structure makes cheaper. mypy and ruff pass both, so the counting is the reader's job.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one from the comparison fixture):

1. `## Learning objectives` (~100), five bullets:
   - measure a design against the plain function on the same table: classes, definitions, lines, calls, and where one rule lives;
   - say what a Visitor costs when a new charge kind arrives;
   - replace getter and setter pairs with fields, frozen dataclasses and properties;
   - explain how a service locator moves a missing dependency from mypy to run time, and pass the dependency instead;
   - write a prompt that keeps generated code to the shape the forces justify.
2. `## Why this matters` (~180). Intent first:
   - the one-carrier rating case from "Patterns as decisions under forces" (one pointer by title);
   - an anti-pattern as a recurring structure whose consequences outweigh its benefits in the context at hand (no attribution, decision note);
   - three failures: a new charge kind breaks the engine at run time (test 7); a setter lets a quoted consignment change its quote (test 10); a located engine with nothing registered fails at its first quote (test 12).
3. Figure plus one paragraph (~50).
4. `## The rating function and its overbuilt twin` (~360).
   - Excerpt `quote` from `src`. It's the chapter's function, written for the first time.
   - The comparison excerpt is `_RateEngine.quote`. Both forms quote the same table (test 1) and refuse an unknown zone with the same `RatingError` (test 2).
   - Paraphrase the 1994 assumption: behaviour reached a call site only inside an object of a declared class. A callable now carries it. Point to "Strategy: the callable" and "Visitor, Memento, and Interpreter" by title, one clause each.
5. `## Measuring what the structure costs` (~380):
   - The `ast` counts of classes, functions and lines (test 3). Say how they're counted: `ast.unparse` without docstrings.
   - The fuel surcharge lives in one definition of the function and five of the engine (test 4). One quote makes one Python-level call in the function and eleven in the engine (test 5), counted with `sys.setprofile`.
   - mypy `--strict` and ruff pass both forms (`run: R1b`): they check types and style, not proportion.
6. `## What a new charge costs` (~280):
   - A new charge kind whose `accept` calls a missing visit method fails at run time (test 6), and mypy reports it as `[attr-defined]` (test 16, reduced model).
   - Declaring the method makes every concrete visitor abstract (test 7, test 16's `[abstract]`). Paraphrase GoF's Visitor consequence, if verified.
   - In the function the same change is one edit (experiment b). Tie it to the count-the-edits test without re-arguing it.
7. `## Getters and setters` (~250):
   - Quote PEP 8's "simple public data attributes" and "use properties" sentences.
   - `_AccessorConsignment` compares by identity (test 8). Its setter changes a consignment after it was quoted, so a re-quote differs: the reproducibility force from "Patterns as decisions under forces" (test 9).
   - The frozen `Consignment` compares by value (test 8) and refuses the assignment (test 10).
   - The `get_tariff` getter in the engine adds two of the eleven calls. Point to "Dataclasses and value semantics" and "Descriptors and properties" by title, one clause each.
8. `## A service locator` (~280):
   - Quote Fowler's "basic idea" and "key difference" sentences, then Seemann's "hides a class' dependencies" sentence (stopping after "compile-time errors"). In this book the static check is mypy.
   - The located engine constructs with nothing registered and fails at its first quote (test 11). It quotes once a tariff is registered (test 12).
   - mypy needs a type check before using what the locator returns (test 13). It doesn't see a missing registration (test 14), but it reports a missing `tariff` argument to `quote` (test 15).
   - One pointer to "ISP, DIP, and dependency injection without a framework" for passing dependencies.
9. `## When the structure earns its place` (~150):
   - the three shapes in "Patterns as decisions under forces" and the force behind each;
   - a Protocol when a participant holds state or offers several operations;
   - a Visitor-like split when many operations range over a stable set of kinds (and then `match`, per "Visitor, Memento, and Interpreter");
   - an interface with one implementation adds a name and no seam, as "Naming patterns for teams and AI assistants" argues (one clause).

   Then the sidebar (decision 2):

   <blockquote class="ai-sidebar" markdown="1"> **Specifying the shape the forces justify.** A request for "a flexible rating engine" leaves the structure open, and a factory, strategy and visitor for one flat fee all type-check. Paste a prompt that states the forces:

   > Price a consignment with one function, `quote(consignment, tariff)`, over a frozen `Tariff`. Use frozen dataclasses with public fields, no `get_` or `set_` methods, and pass every dependency as a parameter. Add a class or a Protocol only when a second implementation exists today, and name the change it makes cheaper.

   If the reply adds a class, ask which change it makes cheaper.</blockquote>
10. `## Build, run, observe` (~180 plus output). The scratch-copy and stated-filter rules are the same as ch31's (confirm `pattern_misuse.__file__`). These experiments are the count-the-edits test as a run.
    - (a) In conftest, add an abstract `visit_remote_area` to `_ChargeVisitor`.
      - Expected:
        - the engine rows of tests 1 and 2 fail with `TypeError: Can't instantiate abstract class _NetTotalVisitor without an implementation for abstract method 'visit_remote_area'`;
        - test 5 fails;
        - test 3's engine counts change;
        - mypy reports `[abstract]` and exits 1.
      - Executor check: the exact failing set, and whether some failures show as setup `ERROR`.
    - (b) In `src`, add `remote_area_fee: Decimal = Decimal("0.00")` to `Tariff` and add it to `net` in `quote`.
      - Expected: all tests pass and mypy exits 0.
      - Executor check: whether test 3's function line count changes. If it does, the prose says so. The function's footprint stays one definition.
11. `## What you can do now` (~130): five bullets mapped one to one to the objectives. They name:
    - tests 3 and 4;
    - test 7;
    - `_AccessorConsignment` with test 9;
    - `_ServiceLocator` with tests 11 and 15;
    - the sidebar's prompt.
12. `## For deeper coverage` (~100):
    - Fowler's injection article and Seemann's post;
    - PEP 8;
    - [GoF, Visitor, Consequences, if verified];
    - [Percival and Gregory, *Architecture Patterns with Python*, on dependency injection, if verified];
    - [Martin, *Agile Software Development*, on needless complexity, if verified];
    - the bibliography link.

Figure `32-anti-patterns-and-pattern-misuse` (two columns, vertical flow in each):
- **Left, accent:** `quote(consignment, tariff)` with "flat fee, fuel surcharge and tax in one definition", then "RateQuote".
- **Right, muted:** a chain `_RateEngine.quote`, then `_PricingStrategyFactory`, then `_FlatFeeStrategy.charges`, then `_FlatFeeCharge` and `_FuelSurcharge`, then `accept`, then `_NetTotalVisitor.visit_*`, then "RateQuote".
- **A dashed box beside the right column:** "a new charge kind: a new class, a new visit method, every visitor changes".
- **A bottom bar across both:** "same table of quotes; mypy and ruff pass both".
- No digits in the SVG.

Caption draft (about 38 words with the prefix): "Figure 32.1: The same quote from one function and from a factory, strategy and visitor. Both pass the same table and the same type check; the engine spreads one surcharge across several definitions, and a new charge kind changes every visitor."

Citations, both chapters: verify each before writing, apply the bracketed fallbacks, quote no sentence unless it was checked on a fetched page, stop each quotation where the page's sentence stops, and make no comparison between languages.

## Example spec

### `examples/31-shortcut-patterns-dict-dispatch-and-eafp` (project `shortcut-patterns`, package `shortcut_patterns`)

`pyproject.toml` in the r14 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`).

- **`documents.py`** (decision 3, evidence B-E):
  - `issue` reads:
    ```
    try:
        issuer = issuers[kind]
    except KeyError:
        raise UnsupportedDocumentError(f"no issuer for {kind.value!r}") from None
    return issuer(consignment_id)
    ```
  - `parse_kind` wraps `DocumentKind(raw)` and raises `UnsupportedDocumentError(f"unknown document kind {raw!r}") from None`.
  - Docstrings say why the call sits outside the `try`, and that mypy doesn't check that every kind has an entry.
- **`declarations.py`:**
  - `_required(record, name) -> str` uses `try`/`except KeyError` and raises `CustomsError(f"declaration is missing {name!r}") from None`.
  - `declaration_from` reads `consignment_id`, `hs_code` and `declared_value` (as `Decimal`) through it, and `origin` through `record.get("origin")`.
- **`duties.py`:**
  - `DutyRateCache.__init__(self, load: Callable[[str], Decimal], *, rates: MutableMapping[str, Decimal] | None = None)`.
  - `rate_for` uses EAFP and stores the loaded rate. `evict` uses `self._rates.pop(hs_code, None)`.
  - `duty_for(declaration, cache) -> Decimal` gives `(declaration.declared_value * cache.rate_for(declaration.hs_code) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
  - Docstrings say that one read leaves no gap between check and use, and that a miss can load twice under threads.
- **`bench/lookup_cost.py`** (decision 7): `timeit`, best of five repeats of one million calls, present and absent keys, three forms, printing the Python version. It isn't collected by pytest. mypy covers it by hand (`uv run mypy --strict src tests bench`), as ch21 did.
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- `_LookFirstDutyRateCache(DutyRateCache)` overriding `rate_for` with the look-first form.
- `_HandoverRates(dict[str, Decimal])` with the parking seam (decision 5, evidence G).
- A `recording_load` fixture: a loader that appends each code and returns `Decimal("8.0")`.
- `cache_form` params `eafp|lbyl`, each giving a constructor `(load, rates) -> DutyRateView`, where `DutyRateView` is a small Protocol with `rate_for` and `evict`. No `Any`.

`test_dispatch.py`:
1. `test_every_document_kind_has_an_issuer`: `[k.name for k in DocumentKind if k not in ISSUERS] == []`.
2. `test_issue_gives_each_kind_its_reference` x 3 kinds: `BL-CN-1`, `MF-CN-1`, `CD-CN-1`.
3. `test_an_unsupported_kind_raises_unsupported_document_error`: a two-entry table; matches `no issuer for 'customs declaration'`; `__suppress_context__` is `True`.
4. `test_the_issuer_table_is_read_only`: `TypeError` matching `does not support item assignment`, and `not isinstance(ISSUERS, dict)`. One coded ignore if mypy asks (executor check).
5. `test_an_issuers_own_key_error_passes_through_issue`: a test-local issuer raising `KeyError("port")`; `pytest.raises(KeyError, match="port")`.
6. `test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind`: test-local `_issue_broadly` raises `UnsupportedDocumentError` for the same issuer.
7. `test_a_table_passed_by_the_caller_replaces_the_default`.
8. `test_an_if_chain_whose_else_raises_misses_a_new_kind`: test-local `_issue_by_chain` handles two kinds; `CUSTOMS_DECLARATION` raises `ValueError`. Domain row 31's failing test.
9. `test_singledispatch_sends_every_document_kind_to_one_implementation`: a list of three equal results, and `sorted(t.__name__ for t in f.registry) == ["DocumentKind", "object"]`.
10. `test_parse_kind_reads_a_document_kind_from_its_value` x 3.
11. `test_parse_kind_refuses_an_unknown_value`: matches `unknown document kind 'nope'`, with the context suppressed.

`test_eafp.py` (holds `CACHE_ROWS`):

12. `test_every_cache_form_reads_loads_and_evicts_the_same_way` x `cache_form` (2) x `CACHE_ROWS` (`hit`, `miss`, `evicted`) = 6. Each row asserts the rate and the loader's recorded codes as a list.
13. `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`: `(out, loads) == (["KeyError: '0901.21'"], [])`.
14. `test_an_eafp_read_reloads_when_another_thread_evicts_first`: `(out, loads) == (["8.0"], ["0901.21"])`.
15. `test_two_eafp_readers_that_both_miss_both_load`: a loader parked on `Barrier(2)`; `loads == ["0901.21", "0901.21"]`.
16. `test_evicting_an_absent_code_is_not_an_error` x `cache_form` (2).
17. `test_declaration_from_reads_required_fields_and_an_optional_origin`: with and without `origin` (`None`).
18. `test_a_missing_required_field_names_the_field` x (`consignment_id`, `hs_code`, `declared_value`).
19. `test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property`: test-local `_DutyBearingDeclaration`; `getattr(..., "duty", Decimal(0)) == 0`, `hasattr` is `False`, and direct access raises `AttributeError` matching `has no attribute 'rate'`.
20. `test_suppress_skips_the_rest_of_its_block_after_the_first_exception`: `with suppress(KeyError): del rates["absent"]; del rates["0901.21"]` leaves `sorted(rates) == ["0901.21"]`.
21. `test_duty_for_applies_the_cached_rate_to_the_declared_value`: `Decimal("100.00")` at 7.5 gives `Decimal("7.50")`.

`test_static.py` (each row: credited thing; mutation that fails it):

22. `test_mypy_checks_an_issuers_signature_in_the_table`: imports `src`; an issuer taking `(ConsignmentId, int)` gives `["dict-item"]`. Credits `DocumentIssuer`. Mutation: the alias as `Callable[..., object]` empties the list.
23. `test_mypy_checks_the_key_type_of_a_table_lookup`: imports `src`; `ISSUERS["manifest"]` gives `["index"]`. Mutation: `Mapping[object, DocumentIssuer]` empties it.
24. `test_mypy_accepts_a_table_that_misses_a_kind`: imports `src`; a two-entry table exits 0 with `[]`, and at run time `issue` raises `UnsupportedDocumentError`. Credits mypy's silence (why test 1 exists). Mutation: the snippet replaced by a two-arm `match` with `assert_never` gives `["arg-type"]`.
25. `test_mypy_reports_a_missing_arm_in_a_match_and_an_if_chain_without_else`: reduced model; `["arg-type", "return"]`. Mutation: adding the third arm empties the list.
26. `test_mypy_accepts_an_if_chain_whose_else_raises`: reduced model; exit 0, `[]`; `exec` raises `ValueError`. Mutation: deleting the `else` gives `["return"]`.
27. `test_mypy_refuses_assignment_into_the_issuer_table`: imports `src`; `["index"]` and `Unsupported target for indexed assignment`. Mutation: annotating `ISSUERS` as `dict[...]` empties the list.
28. `test_mypy_requires_a_branch_after_dict_get`: imports `src`; `ISSUERS.get(kind)(cid)` gives `["misc"]` and `"None" not callable`. Mutation: `.get(kind, issue_manifest)` empties it.
29. `test_ruff_flags_an_if_chain_over_literals_but_not_over_enum_members`: `["SIM116"]` for the string chain, `[]` for the enum chain.
30. `test_ruff_suggests_get_suppress_and_plain_membership`: `["SIM105", "SIM118", "SIM401"]` (sorted; SIM108 is excluded by `--select SIM401,SIM105,SIM118`).

Numbers are spec ids, not file order. Planned: 30 test functions and 42 cases:
- `test_dispatch.py`: 11 functions, 15 cases;
- `test_eafp.py`: 10 functions, 18 cases;
- `test_static.py`: 9 functions, 9 cases.

The executor counts from the pytest summary line, and R1a records any difference.

Also `README.md` and the card `_examples/31-shortcut-patterns-dict-dispatch-and-eafp.md`: `order: 31`, eyebrow "Patterns in the wild · Dispatch tables and EAFP", and a concept title with no count. None of the following appears in `src/`: `suppress`, `hasattr`, `getattr(`, `except Exception`, `match `, `singledispatch`, `isinstance`, `Any`, `cast`, `TYPE_CHECKING`, `mock`, `monkeypatch`, `print(`, `Optional`, `between`.

Deletion table (R1a):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `CUSTOMS_DECLARATION` entry | removed | 1, 2[customs] | totality list non-empty; `UnsupportedDocumentError` |
| `frozendict` | plain dict | 4 | `DID NOT RAISE`; `isinstance` dict |
| `UnsupportedDocumentError ... from None` | bare `KeyError` | 3 | wrong exception type |
| call outside `try` | inside (experiment a) | 5 | `UnsupportedDocumentError` instead of `KeyError` |
| `parse_kind` `except` | removed | 11 | `ValueError`, not `UnsupportedDocumentError` |
| EAFP `rate_for` | look-first (experiment b) | 14 | `KeyError: '0901.21'` recorded |
| store on miss | removed | 12[eafp-miss] | two loads |
| `pop(hs_code, None)` | `del` | 16[eafp] | `KeyError` |
| `_required` `except` | removed | 18 | `KeyError`, not `CustomsError` |
| `.get("origin")` | index | 17 | `KeyError: 'origin'` |
| duty quantise | removed | 21 | `Decimal('7.500')` (executor check) |

### `examples/32-anti-patterns-and-pattern-misuse` (project `pattern-misuse`, package `pattern_misuse`)

- **`rating.py`** (evidence K):
  - `ConsignmentId`;
  - `Money(amount: Decimal, currency: str)`, frozen slotted;
  - `Consignment(id, zone)`, frozen slotted;
  - `Tariff(flat_fee_by_zone: frozendict[str, Decimal], fuel_fee: Decimal, tax_rate: Decimal, currency: str = "EUR")`;
  - `RateQuote(consignment_id, total: Money)`;
  - `RatingError(LookupError)`;
  - `quote(consignment, tariff) -> RateQuote`:
    - looks up the flat fee with `try`/`except KeyError` and raises `RatingError(f"no flat fee for zone {zone!r}") from None`;
    - adds `fuel_fee`;
    - adds tax quantised to the cent.
  - `STANDARD_TARIFF` with `EU` 25.00 and `ASIA` 60.00, fuel 4.50, tax 0.21.
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- The nine engine classes of decision 8. `_RateEngine(factory, tariff)` has `get_tariff` and `quote`, raising the same `RatingError`.
- `_AccessorConsignment(consignment_id, zone)` with `get_zone` and `set_zone`, and `_quote_accessor(consignment, tariff)` adapting it.
- `_ServiceLocator` with `register(name, service: object)` and `get(name) -> object`, on an instance dict, not a class attribute, so no state crosses tests.
- `_LocatedRateEngine(locator)`, whose `quote` narrows with `if not isinstance(tariff, Tariff): raise TypeError(...)`.
- `rating_form` params `function|engine`, each giving `(Consignment) -> RateQuote` over `STANDARD_TARIFF`.
- Fixtures expose `engine_parts` (a frozen dataclass of the engine classes, typed through `TYPE_CHECKING` imports) for tests 6 and 7.

`test_forms.py` (holds `QUOTE_ROWS`):
1. `test_every_rating_form_quotes_the_same_table` x `rating_form` (2) x `QUOTE_ROWS` (`EU` 35.70, `ASIA` 78.05) = 4.
2. `test_every_rating_form_refuses_an_unknown_zone` x 2: matches `no flat fee for zone 'POLAR'`.

`test_measure.py` (holds `ENGINE_DEFINITIONS`; parses conftest from `Path(__file__).with_name("conftest.py")` and `src` through `inspect.getsource`):

3. `test_the_engine_needs_more_classes_functions_and_lines_than_the_function`: exact tuples `(0, 1, L_f)` and `(9, 17, L_e)` from the build (evidence K predicts 0/1 and 9/17).
4. `test_the_fuel_surcharge_lives_in_one_definition_of_the_function`: `["quote"]` against the sorted engine list of five (names after the `_FuelSurcharge` rename).
5. `test_one_engine_quote_makes_more_python_calls_than_the_function`: exact ordered `co_qualname` lists filtered by file: `["quote"]` and the eleven engine calls.
6. `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`: `AttributeError` matching `has no attribute 'visit_remote_area'`.
7. `test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract`: `TypeError` matching `without an implementation for abstract method 'visit_remote_area'`.

`test_misuse.py`:

8. `test_an_accessor_consignment_has_no_value_equality`: `(accessor_a == accessor_b, frozen_a == frozen_b) == (False, True)`.
9. `test_a_setter_lets_a_quoted_consignment_change_its_quote`: totals before and after `set_zone("ASIA")` are `["35.70", "78.05"]`.
10. `test_a_frozen_consignment_refuses_assignment`: `FrozenInstanceError` matching `cannot assign to field 'zone'`.
11. `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`: construction succeeds, and `quote` raises `KeyError` matching `tariff`.
12. `test_a_located_engine_quotes_once_its_tariff_is_registered`: equals `quote(..., STANDARD_TARIFF)`.

`test_static.py`:

13. `test_mypy_needs_a_type_check_to_use_a_located_service`: reduced model; `["attr-defined", "no-any-return"]`. Mutation: an `isinstance` narrowing empties the list.
14. `test_mypy_does_not_see_a_missing_registration`: reduced model; exit 0, `[]`; `exec` raises `KeyError`. Mutation: the locator replaced by a parameter and the call left without it gives `["call-arg"]`.
15. `test_mypy_reports_a_missing_tariff_argument`: imports `src`; `quote(consignment)` gives `["call-arg"]` and `Missing positional argument "tariff"`. Mutation: a default `tariff=STANDARD_TARIFF` empties the list.
16. `test_mypy_reports_a_visitor_missing_a_new_visit_method`: reduced model; `["abstract", "attr-defined"]`. Mutation: implementing `visit_remote_area` on the concrete visitor and declaring it on the base empties the list.

The claim that mypy and ruff pass the engine is witnessed by `run: R1b` (`verify.sh` runs `mypy --strict src tests`, and ruff covers conftest).

Planned: 16 test functions and 21 cases:
- `test_forms.py`: 2 functions, 6 cases;
- `test_measure.py`: 5 functions, 5 cases;
- `test_misuse.py`: 5 functions, 5 cases;
- `test_static.py`: 4 functions, 4 cases (plus mutation runs at R1b).

The pytest summary line wins.

Also `README.md` and the card `_examples/32-anti-patterns-and-pattern-misuse.md`: `order: 32`, eyebrow "Patterns in the wild · Anti-patterns", and a concept title. None of the following appears in `src/`: `ABC`, `abstractmethod`, `Factory`, `Strategy`, `Visitor`, `get_`, `set_`, `Locator`, `Any`, `cast`, `mock`, `monkeypatch`, `print(`, `Optional`.

Deletion table (R1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `RatingError ... from None` | bare `KeyError` | 2[function] | wrong exception type |
| tax quantise | removed | 1[function-*] | totals differ from the engine row (executor check) |
| fuel fee in `quote` | removed | 1[function-*] | totals differ |
| `frozen=True` on `Consignment` | removed | 10 | `DID NOT RAISE` |
| `tariff` parameter required | defaulted | 15 | empty code list |

## Steps and status

Step ids are `R*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| R0 | Bookkeeping, all with dated notes, plus re-checking the upstream pins and recording the decisions. In `iteration-plan.md`: PDP-131a-c and 132a-c `active`, r15 active, r14 closed, PDP-129a to 130c closed. In r14's plan: Q7 closed. In `chapters.toml`: ch32 `has_example = true`. In the reconciliation plan: rows 174-187 `open`, row 28 noted "r15". In the domain model: rows 31-32 get the supporting names and decisions 1-11, and row 32's "eight-class ... 6 files touched" is adjusted to the measured footprint (decision 9). ch31-32 stub `description` lines are written | - | todo |
| R1a | ch31 member, card, README, `bench/lookup_cost.py` and `_plans/evidence/eafp-lookup-cost.md` (scrubbed, version and date); one `uv lock`; three green runs plus one reverse-file-order run; `mypy --strict src tests bench`; the deletion table, each row in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`), deleted after use | R0 | todo |
| R1b | ch32 member, card and README; one `uv lock` after R1a (sequenced for `uv.lock`); three green runs plus one reverse-order run; the deletion table; each static mutation run | R1a | todo |
| R2 | Witness results into rows 174-186 and legacy row 28 (adjusted (r15)). The dated r15 note in `_plans/spikes.md` (evidence B's code difference, D, F, H, K). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | R1b | todo |
| R3 | Two figures, specs `diagrams/specs/31-*.py` and `32-*.py`, and `_data/diagrams.yml` (single owner; 33 entries). Figures 00-30 unchanged. Every name drawn exists in `src`, conftest or the standard library | R2 | todo |
| R4 | ch31-32 `status = "drafted"` (`kind` stays `pattern` and `argument`) | R3 | todo |
| R5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly; runs its two experiments in fresh scratch copies with the filter it states; quotes that filter's complete output through `python3 scripts/host_ids.py filter`; and hands back the sources checked plus a per-paragraph claims table that names, for each static-test citation, the mutation that fails it | R3, R4 | todo |
| R6 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also checks that close bullets map one to one to objectives, an excerpt check against decisions 4-10, a pointer-circularity check (criterion 11), and a cross-language word check (criterion 14) | R5 | todo |
| R7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r15.x` on main; notes-only release | R6 | todo |

Reconciliation rows (step R0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 174 | 31 | A read-only table of callables issues each document kind; a test checks every kind has an entry; a missing kind raises `UnsupportedDocumentError` with the `KeyError` suppressed; a caller can pass another table | `test_every_document_kind_has_an_issuer`, `test_issue_gives_each_kind_its_reference`, `test_an_unsupported_kind_raises_unsupported_document_error`, `test_the_issuer_table_is_read_only`, `test_a_table_passed_by_the_caller_replaces_the_default`, `source: https://peps.python.org/pep-0814/` |
| 175 | 31 | An if-chain whose `else` raises misses a new kind; `singledispatch` sends every enum member to one implementation; a kind parses from its value and an unknown value is refused | `test_an_if_chain_whose_else_raises_misses_a_new_kind`, `test_singledispatch_sends_every_document_kind_to_one_implementation`, `test_parse_kind_reads_a_document_kind_from_its_value`, `test_parse_kind_refuses_an_unknown_value` |
| 176 | 31 | mypy checks a table entry's signature, a lookup's key type, assignment and the `None` from `.get`; it accepts a table that misses a kind and a chain whose `else` raises, and reports a missing arm in a `match` and in a chain without `else` | `test_mypy_checks_an_issuers_signature_in_the_table`, `test_mypy_checks_the_key_type_of_a_table_lookup`, `test_mypy_accepts_a_table_that_misses_a_kind`, `test_mypy_reports_a_missing_arm_in_a_match_and_an_if_chain_without_else`, `test_mypy_accepts_an_if_chain_whose_else_raises`, `test_mypy_refuses_assignment_into_the_issuer_table`, `test_mypy_requires_a_branch_after_dict_get` |
| 177 | 31 | An issuer's own `KeyError` passes through `issue`, and a `try` around the call reports it as an unsupported kind; a missing required field names itself and an optional one reads as `None` | `test_an_issuers_own_key_error_passes_through_issue`, `test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind`, `test_declaration_from_reads_required_fields_and_an_optional_origin`, `test_a_missing_required_field_names_the_field`, `source: https://docs.python.org/3/glossary.html`, `source: https://docs.python.org/3/library/stdtypes.html`, `source: https://docs.python.org/3/reference/compound_stmts.html` |
| 178 | 31 | A `getattr` default and `hasattr` hide a property's own `AttributeError`; `suppress` skips the rest of its block; ruff flags an if-chain over literals but not over enum members and suggests `.get`, `suppress` and plain membership | `test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property`, `test_suppress_skips_the_rest_of_its_block_after_the_first_exception`, `test_ruff_flags_an_if_chain_over_literals_but_not_over_enum_members`, `test_ruff_suggests_get_suppress_and_plain_membership`, `source: https://docs.python.org/3/library/functions.html`, `source: https://docs.python.org/3/library/contextlib.html` |
| 179 | 31 | EAFP and look-first caches pass the same table; with an eviction forced between check and read the look-first form raises and EAFP reloads; two EAFP readers that both miss both load; evicting an absent code is not an error; duty applies the cached rate | `test_every_cache_form_reads_loads_and_evicts_the_same_way`, `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`, `test_an_eafp_read_reloads_when_another_thread_evicts_first`, `test_two_eafp_readers_that_both_miss_both_load`, `test_evicting_an_absent_code_is_not_an_error`, `test_duty_for_applies_the_cached_rate_to_the_declared_value`, `source: https://docs.python.org/3/glossary.html` |
| 180 | 31 | On the recorded run, an EAFP lookup is cheaper than look-first for a present key and dearer for an absent one (illustrative, benchmark only) | `run: _plans/evidence/eafp-lookup-cost.md` |
| 181 | 32 | The rating function and the class-per-role engine quote the same table and refuse an unknown zone the same way | `test_every_rating_form_quotes_the_same_table`, `test_every_rating_form_refuses_an_unknown_zone` |
| 182 | 32 | The engine needs more classes, functions and lines than the function, spreads the fuel surcharge across more definitions and makes more Python calls per quote, counted with `ast` and `sys.setprofile` | `test_the_engine_needs_more_classes_functions_and_lines_than_the_function`, `test_the_fuel_surcharge_lives_in_one_definition_of_the_function`, `test_one_engine_quote_makes_more_python_calls_than_the_function` |
| 183 | 32 | A new charge kind breaks the engine's visitor at run time, declaring its visit method makes every concrete visitor abstract, and mypy reports both | `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`, `test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract`, `test_mypy_reports_a_visitor_missing_a_new_visit_method` |
| 184 | 32 | An accessor consignment has no value equality and its setter changes a quoted consignment's quote; a frozen consignment compares by value and refuses assignment | `test_an_accessor_consignment_has_no_value_equality`, `test_a_setter_lets_a_quoted_consignment_change_its_quote`, `test_a_frozen_consignment_refuses_assignment`, `source: https://peps.python.org/pep-0008/` |
| 185 | 32 | A located engine fails at its first quote when nothing is registered and quotes once a tariff is; mypy needs a type check to use a located service and doesn't see a missing registration, but reports a missing `tariff` argument | `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`, `test_a_located_engine_quotes_once_its_tariff_is_registered`, `test_mypy_needs_a_type_check_to_use_a_located_service`, `test_mypy_does_not_see_a_missing_registration`, `test_mypy_reports_a_missing_tariff_argument`, `source: https://martinfowler.com/articles/injection.html`, `source: https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/` |
| 186 | 32 | mypy `--strict` and ruff pass both the rating function and the engine | `run: R1b` |
| 187 | 31-32 | The "Build, run, observe" experiments behave as quoted | `run: R5` |

Legacy row at R2:
- Row 28 gets `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`, `test_an_eafp_read_reloads_when_another_thread_evicts_first`, `test_two_eafp_readers_that_both_miss_both_load` and `run: _plans/evidence/eafp-lookup-cost.md`, marked "adjusted (r15)". EAFP removes the gap between check and read, but doesn't make a miss load once. It's cheaper on a hit and dearer on a miss, and the speed is benchmark-only.

## Corrections after the build

(None yet. The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.)

Lessons carried from r11-r14, which this plan applies up front:
- **Counts.** Per-file counts are summed from the spec, and the pytest summary line wins (r13 P1a, r14 Q1a).
- **Members.** The project is named after its package, with no `[tool.*]` table (r13 P1a).
- **Shared tables.** They live in the test module, not in conftest (`from conftest import` fails under importlib mode; r13 P1a). Conftest types are imported under `TYPE_CHECKING`, and classes come through fixtures (r14 Q1a).
- **Determinism.**
  - Assertions that can fail compare lists or tuples, never a set repr, not even of strings (r13 P5, r14 Q5). `_codes()` now returns a sorted list.
  - Experiment filters match pytest's `E` plus 3, 7 and 9 spaces as separate alternatives (r13 P6, r14 Q5 and Q6).
- **mypy.** It narrows after `assert` and flags later lines `[unreachable]`, so values are read through small helpers (r11). `mypy.api.run` can raise the process recursion limit (r10 K1a). Nothing here recurses, but tests never depend on the limit.
- **Static tests.** Every exit-0 static test asserts `_codes(stdout) == []` and a runtime half (r13 P6).
- **Prose repairs.**
  - A repair can make a dependent sentence false, so the validator re-reads the paragraph and the close (r12 N6).
  - A scope word needs a test that covers the whole scope (r11). "Race-free" isn't used.
- **Pointers.** No pointer may send the reader back to a chapter that defers the topic here (r14 Q6 round 1, `__call__`). ch31 never points to the Strategy or State chapters for dispatch tables.
- **GoF and Rhodes.** GoF paraphrases are checked at validation (r11 M5, r12 N5). Unverified attributions are dropped (r14 Q5's "ghost variant").

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` (ch31 also `bench`) on three consecutive runs, and once with the test files in reverse order (`tests/test_static.py` first), with the same pass count.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch"` over both members' `tests` prints nothing.
   - `grep -rn "print("` over both members prints nothing outside `examples/31-*/bench/`.
   - `grep -rnE "suppress|hasattr|getattr\(|except Exception|\bmatch\b|singledispatch|isinstance|\bAny\b|cast\(|TYPE_CHECKING|between"` over `examples/31-*/src` prints nothing.
   - `grep -rnE "\bABC\b|abstractmethod|Factory|Strategy|Visitor|def get_|def set_|Locator|\bAny\b|cast\("` over `examples/32-*/src` prints nothing.
3. Every test name cited in rows 174-186 and row 28 is defined exactly once across `examples/*/tests`.
4. Every mypy-API test asserts:
   - its exit status;
   - an exact sorted code list, through the anchored `_codes` regex;
   - no line number and no optional note.

   Also:
   - every ruff test asserts a sorted code list;
   - `grep -c "_codes("` is at least 7 in ch31's `test_static.py` and at least 4 in ch32's;
   - every `# type: ignore[...]` and `# noqa` names a code, and there are no unused ignores.
5. **Every static test can fail on a mutation of the thing its prose credits.** The R1a/R1b handback lists each static test with its credited thing, runs the named mutation in a scratch copy and quotes the failing line. Every exit-0 test also asserts the hazard at run time.
6. Deletion tables (R1a, R1b): every row, deleted in a fresh scratch copy whose imports come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed", and executor-check rows are resolved or moved to Corrections.
7. Every "silently", "accepts", "hides", "raises", "reloads", "both load" or "fails at the first quote" sentence names a test with a deletion-table row, experiment or mutation that makes it fail. Scope words ("every", "all", "only", "never", "both") name the test that covers the whole scope, or are cut. "Race-free" appears nowhere.
8. ch31-32 are drafted, with:
   - one figure each;
   - captions of 20-45 words including `Figure N.1:`;
   - at most 2,500 prose words each by `validate.py` (an error above; a warning below 1,900 is reported, not padded).
9. Spine and sidebar:
   - **ch31:** `validate.py` passes the `pattern` spine; `grep -c '<blockquote class="ai-sidebar"'` is 1; `grep -c "^## When not to use it"` is 1; `grep -c "^## How it works"` is 0.
   - **ch32:** `validate.py` passes the `argument` spine; it has `## Build, run, observe` and `## When the structure earns its place`; `grep -c '<blockquote class="ai-sidebar"'` is 1 (decision 2); `grep -c "^## The argument"` is 0.
   - In both:
     - `{: .ai-sidebar}` appears nowhere;
     - `## What you can do now` is the second-to-last H2, directly before `## For deeper coverage`, with as many bullets as the learning objectives;
     - every backticked token in the close appears earlier in the chapter.
   - Each sidebar:
     - opens with a bold lead and holds a nested `>` prompt;
     - has at most two non-quoted paragraphs;
     - matches no `\bCheck(:| that| three| four| whether)`;
     - is at most 120 words;
     - names only identifiers present in the chapter, its `src`, conftest or the standard library;
     - makes no claim about what assistants or models produce.
10. Thesis:
    - ch31 says if-chain dispatch dissolves (`dissolv` at least 1) and names what remains (totality, where the `try` goes, one read of shared state).
    - ch32 measures the structure against the function on the same table and says mypy and ruff pass both.
11. Non-overlap and pointers:
    - ch31 points to "The three-way split: dissolve, survive, disambiguate", "Visitor, Memento, and Interpreter", "singledispatch: the Visitor the language gives you", "Context managers: deterministic cleanup", "Singleton: module, Borg, and metaclass" and "The GIL and performance" by title.
      - It doesn't link "Strategy: the callable" or "State and finite state machines" (circularity): `grep -nE "12-strategy|14-state"` over `_docs/31-*.md` prints nothing.
      - It doesn't re-quote the contextlib "very specific errors" sentence.
    - ch32 points to "Patterns as decisions under forces" and "Working with AI and LLM tools" by title, and to at most five others, with one clause each.
    - Neither chapter describes asyncio, the GIL's mechanics, `monkeypatch`, the legacy `RateEngine` or LLM output.
12. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, the cards, the specs and the SVGs, with `--stats` reviewed against the house-voice rubric.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|memoiz|characteriz)"` over prose (quotations and code excluded) prints nothing.
    - No paragraph after an excerpt re-narrates its identifiers.
13. No em-dash or en-dash in any file touched in r15, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0.
14. `grep -nE "Java|C#|C\+\+|\.NET|Smalltalk|\bBean\b|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]|magic method|Bobby|Koenig"` over `_docs/31-*.md`, `_docs/32-*.md`, the new READMEs and the cards prints nothing. Quotations are exempt only if their own text contains the word; none of the planned ones do.
15. Idiomatic scan: 0 ban-tier in both members outside `examples/31-*/bench/`. Bench `print` hits are triaged as in r10 K1a. The ch32 conftest engine is the subject of the chapter: its hits are listed in the R1b handback and accepted only for names in decision 8.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`. The benchmark output names no CPU model and gives the kernel as `major.minor` only.
17. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Each experiment:
    - runs in a fresh scratch copy, changes one thing, and is deleted afterwards;
    - has its exact filter command stated in the chapter, matching pytest's `E` plus 3, 7 and 9 spaces as separate alternatives;
    - is quoted as that filter's complete output, followed by `uv run mypy --strict src tests`;
    - is run twice with identical output apart from the duration.
19. Attribution:
    - ch31 credits PEP 814 by author and quotes the glossary, built-ins, built-in types, contextlib and compound-statement sentences exactly.
    - ch32 credits PEP 8 by author, Fowler and Seemann by name and title, and quotes them exactly.
    - GoF and book claims appear only if verified. Every book cited is already in `bibliography.html`.
20. Claims:
    - Every factual sentence in ch31-32 maps to a named test, `run: R1b`, `run: R5`, the evidence file, or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0, with rows 174-187 resolved and each `source:` URL present in its chapter.
    - Any prose version mention (3.15) is preceded by "since", "before", "until" or "new in", so `check_stale_versions` passes.
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 33 entries, and `diagrams/0*-*`, `diagrams/1*-*`, `diagrams/2*-*` and `diagrams/30-*` are unchanged.
22. Reconciliation rows 174-187 are `verified` or `adjusted` with evidence. Row 28 is `adjusted (r15)`.
23. Deterministic:
    - No test depends on wall time, the environment, memory addresses, test order or iteration order it didn't create.
    - Every `Barrier` has a timeout, every `join` has a timeout, and no thread lets an exception escape.
    - `sys.setprofile` is always cleared in `finally`.
    - `filterwarnings = ["error"]` is still in the root config.
24. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.
25. Every self-contained mypy snippet that stands for code is named in the prose as a reduced model: ch31 tests 25 and 26; ch32 tests 13, 14 and 16.
26. Test counts in prose and handbacks come from the pytest summary line of a fresh run.
27. Every comparison form said to share a table is a conftest fixture param (`cache_form`, `rating_form`), and each chapter shows at most one comparison excerpt.
28. Every figure label that names code exists in that chapter's `src`, conftest or the standard library, checked by grep at R3.
29. Repo-relative paths only in this plan and every r15 file: `grep -rnE "/home/|/Users/"` over the files touched in r15 prints nothing.

## Risks

- **Predicted messages and counts.** Every iteration since r05 mispredicted something. Expect differences in these places:
  - ch32's exact `ast` line counts (the member counts `ast.unparse` output, not the planning model's source lines);
  - the call list after the `_FuelSurcharge` rename;
  - which tests ch32 experiment (a) fails and whether some show as `ERROR`;
  - whether ch32 experiment (b) changes test 3's function line count;
  - the module-qualified exception name in ch31 experiment (a)'s `E` lines;
  - whether test 4 (ch31) needs a coded ignore.

  Tests match codes and stable substrings only.
- **The storage seam depends on `dict` subclass dispatch.** `in` and `[]` on a `dict` subclass call the overridden `__contains__` and `__getitem__`. This held on 3.15.2 (evidence G, 300 out of 300 runs). If a future CPython bypassed overrides for these operations, test 13 would fail loudly, not pass wrongly.
- **Threads under pytest.** An exception escaping a thread becomes a warning, which `filterwarnings = ["error"]` turns into a failure. Readers catch and record. The 10 s barrier guard turns a deadlock into `BrokenBarrierError`, never a hang.
- **`sys.setprofile` and pytest plugins.** No profiling or coverage plugin is installed. The filter by `co_filename` keeps pytest's frames out. If a plugin is ever added, test 5 could see extra frames from the same file only if the plugin calls into it, which it doesn't.
- **`co_qualname` of generated dataclass `__init__`** is an implementation detail. The file filter excludes those frames, so no assertion names them.
- **mypy behaviour can move.** The prose says "mypy 2.4.1" for:
  - the totality results;
  - the `frozendict` key-error code;
  - the located-service codes.
- **ruff behaviour can move.** SIM116's literal-only scope is ruff 0.17.4's. The prose says "ruff 0.17.4" once.
- **Benchmark numbers vary by machine.** They go only into the evidence file and one illustrative sentence, with version and date, and never into a test. Host details are scrubbed, so only a CPU class appears if any.
- **Not upstream defects, kept out of prose as defects.**
  - `frozendict` key mismatches reported as `[assignment]`, not `[dict-item]`, is a context-inference difference.
  - SIM116 skipping enum chains is a design choice.
  - The glossary's "clean and fast" wording isn't quoted.

  None is filed. If the owner wants one reported, it goes through `lgtm-issue-reporting`.
- **Word budgets.** ch31 carries two topics and runs close to 2,500.
  - ch31 shrinks first: the library FAQ quotation, then the `parse_kind` paragraph to a sentence, then the cost sentence.
  - ch32 shrinks first: the "When the structure earns its place" list to two items, then the second Fowler quotation.
  - Their tests stay.
- **Cross-language drift in ch32.** The outline's own words ("Java-in-Python") can't appear. Criterion 14 is the guard, and R6 reads for it.
- **Stub pointers.** It's tempting to explain why the natural race is rare, or that `await` makes the gap easy to hit. Criterion 11 forbids describing those chapters.
- **New supporting names.** If the owner declines `UnsupportedDocumentError`, `DocumentIssuer`, `DutyRateCache` or the test-only engine names, R1a or R1b waits for the replacements. Nothing else moves.
- **Liquid.** The f-strings in excerpts contain single braces only. Any `{{` needs `{% raw %}`.
- **`uv.lock` race.** R1a and R1b are sequenced.
