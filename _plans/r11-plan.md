---
title: "r11 plan: chapters 23-24 (Mediator and Chain of Responsibility; Iterator)"
order: 11
output: false
render_with_liquid: false
---

# r11: chapters 23-24, Mediator and Chain of Responsibility; Iterator

Opus-planned 2026-11-05. Branch `release/r11`, cut from main at e59db10 (the r10b merge, tagged r10b.x). This file is the source of truth for r11 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged (evidence M). `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch23: slug `23-mediator-and-chain-of-responsibility`, title "Mediator and Chain of Responsibility", part 8 (`coordinating-traversing`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.
- ch24: slug `24-iterator-generators-and-the-iterator-protocol`, title "Iterator: generators and the iterator protocol", part 8 (`coordinating-traversing`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.

## User decisions (owner confirmed 2026-11-05: all eight as recommended; decision 5, pointer only)

Standing, not a decision: step ids are `M*`. `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md`, and `grep -nE "^\| M[0-9]" _plans/*.md` matched nothing before this file.

1. **Buckets follow the canonical map.** The r02 map lists "Mediator; Chain of Responsibility" under Survives and "Iterator: a generator or `__iter__`" under Dissolves, and the ch3 table rows say the same. Each chapter names what Python removes and what remains.
   - **Chain of Responsibility survives.** The handler base class and the `successor` link dissolve into a tuple of callables. Three decisions remain: what "pass it on" means, which stage runs first, and who decides when nobody does (evidence H, I).
   - **Mediator survives.** The abstract Mediator and Colleague classes dissolve into callables. The coordination rule stays, written in one place with its state: here, release only after duty and inspection have both reported, in either order, and only once (evidence J, K).
   - **Iterator dissolves.** A generator function, or `__iter__` written as one, replaces the cursor class. What stays is a decision the language doesn't make for you: one pass or many, how much to read, and who closes the source (evidence A to G).

   **Recommend: yes.** Alternatives:
   - (b) CoR "dissolves into a tuple of callables". That's true of the mechanism, but evidence H shows a stage placed after the terminal still clears a restricted commodity, and mypy accepts it (evidence I). The order and the terminal are decisions, which is what the survives bucket means. It would also contradict the r02 map and the ch3 row.
   - (c) Mediator "dissolves into an event bus". Evidence J shows a choreography losing a settlement that arrives before inspection. A bus moves messages and decides nothing.
2. **The Chain of Responsibility form is `clear(declaration, stages, /, *, final=release)` over `type ClearanceStage = Callable[[CustomsDeclaration], Decision | None]`, with a separate `type FinalStage = Callable[[CustomsDeclaration], Decision]`.**
   - `None` means "pass it on". The first non-`None` decision wins, and later stages aren't called.
   - The terminal is a keyword parameter typed so that it can't pass. Appending to `CLEARANCE_STAGES` therefore can't land after it.
   - Comparison forms are conftest fixture params on one hold table, `chain_form` `stages|linked|match`:
     - `linked`: a GoF linked chain (`_Handler` with a `successor`) that returns `None` off the end;
     - `match`: one `match` over the declaration with a `case _` default.
   - The linked chain's `None` result on a clean declaration is the domain row 23 failing test, and it gets its own test.

   **Recommend: yes.** Alternatives:
   - (b) A 3.15 `sentinel("PASS")` instead of `None` for "pass it on". mypy 2.4.1 narrows it and reports a missing return either way (evidence L), so it buys nothing over `X | None`, which the Protocol chapter already teaches as the Null Object replacement.
   - (c) The chain as a `match` in `src`. It's the right form when the rules are closed and fixed, and the chapter says so, but then the order can't be composed by the caller, and the domain row asks for `Iterable[ClearanceStage]`.
   - (d) A linked chain in `src`. That's the GoF shape the chapter argues against.
3. **The Mediator example is a `ClearanceMediator` for one held declaration.**
   - Two colleagues report to it: billing sends a `Settlement` (Billing area entity, reused as the duty-settled message) and the inspection party sends an `Inspection(consignment_id, passed)`. Messages form a closed union `type ClearanceMessage = Settlement | Inspection`.
   - `receive` uses `match` with `assert_never`. When nothing is outstanding and nothing failed, it calls an injected `release: Callable[[HandlingEvent], None]` (in the tests, `TrackingHistory.record`) once, with a `CLEARED` event at the declaration's port.
   - The comparison fixture is `coordination_form` `mediator|choreography`. In `_Choreography`, colleague closures call each other directly: inspection tells billing, and billing releases. It passes the inspection-first row and loses a settlement that arrives first (evidence J).
   - It uses no string bus, so it doesn't repeat the Observer chapter's topic-bus witness.
   - New supporting names go into domain row 23 at M0: `Decision`, `Released`, `Held`, `FinalStage`, `CLEARANCE_STAGES`, `clear`, `check_documents`, `assess_duty`, `inspect_goods`, `release`, `describe`, `ClearanceMediator`, `Inspection`, `ClearanceMessage`, `ClearanceError`. Two are reused as is: `DocumentKind` (Documentation area) and `Settlement` (Billing area).

   **Recommend: yes.** Alternatives:
   - (b) `DutySettled` instead of reusing `Settlement`. It's narrower in meaning, but it's a new entity name, and the domain rule prefers reuse.
   - (c) A `Money` duty with part payments (a part settlement doesn't release). That's more realistic, but it adds currency handling and two tests for no new Mediator lesson. The declaration carries `duty_paid: bool`, and the chapter says once that a `Settlement` means duty paid in full.
   - (d) Mediator over booking, stowage and the carrier gateway. That's the final project's slice (domain row 39).
4. **The ch23 split is about 55/45, CoR then Mediator, joined by one story.** The chain decides whether a declaration is held; a held declaration then waits on the mediator. That gives about 1,250 CoR words and 1,000 Mediator words, in one member and one figure. **Recommend: yes.** Alternative: an even split. CoR carries the comparison forms and four mypy witnesses, and the Mediator's lesson is one rule and its order table.
5. **Async iteration: one pointer only.** ch24 names "asyncio and the patterns" by its exact title in one sentence and describes nothing from it.
   - Domain row 24 and the ch24/ch38 non-overlap rule in `shipping-domain-model.md` currently say "the async-generator `aclosing` finding is a note in ch24". The brief for r11 overrides that.
   - At M0 the orchestrator rewords that rule to "ch24 keeps sync generators; one pointer to asyncio and the patterns, by title; the `aclosing` finding is taught there", with a dated note.

   **Recommend: yes.** Alternative: keep a one-sentence `aclosing` note in ch24, as the domain file says. That's a claim about a stub chapter's ground, and reconciliation row 20 (ch38, legacy) already owns it.
6. **ch24's comparison form is a GoF cursor written to the protocol: `history_form` `iterable|self-iterator`.** `_OneShotHistory` keeps an index and returns itself from `__iter__`.
   - It runs the same traversal table as `TrackingHistory` and passes it.
   - It fails the second-pass and nested-walk tests, each with its own test (evidence E).
   - **Recommend: yes.** Alternative: a `First`/`Next`/`IsDone`/`CurrentItem` cursor class. It can't be used by `for`, `list`, `islice` or `sum` without an adapter, so a shared table would only measure the adapter.
7. **The cleanup example is a reader: `read_events(path, *, opener=open_utf8) -> Generator[HandlingEvent, None, int]`.**
   - It opens a tracking log, one `CN-1;LOADED;NLRTM` line per event, inside a `with` block and returns the line count through `yield from events_from(lines)`.
   - `type Opener = Callable[[Path], TextIO]` reuses domain row 10's supporting name. The test opener records the handle so a test can read `.closed`.

   **Recommend: yes.** Alternatives:
   - (b) A test-local generator that appends to a log in its `finally`. There's no resource in it, and it witnesses only the language.
   - (c) A paged store behind a `PageSource` callable. That's a new supporting name, and the cleanup is then synthetic.
8. **`pages(history, size)` is re-declared in the ch24 member** with the same two-line body as the ch3 example, which "What 1994 assumed, and what Python dissolves" already quotes and witnesses for laziness. ch24 gives it one sentence and that pointer by title. It measures what ch2 didn't (1,000,000 against 3, `page`, `strict=`, a size below one) and doesn't repeat the ch3 test. **Recommend: yes.** Alternative: a new name such as `paged`. Domain row 24 names `pages(history, size)`.

Also proposed for the owner (no decision needed unless declined):
- No new books. GoF, Ramalho, Slatkin, and Lott and Phillips are already in `bibliography.html`. Bracketed items below are dropped if the prose agents can't verify them.
- **Rhodes, python-patterns.guide** (index fetched 2026-11-05):
  - It has "The Iterator Pattern" (`gang-of-four/iterator/`).
  - It has **no Mediator page and no Chain of Responsibility page**. `gang-of-four/mediator/` and `gang-of-four/chain-of-responsibility/` both return HTTP 404, and neither name appears in the index.
  - So ch23 credits GoF and the Python docs only, and claims no Rhodes page. ch24 credits Rhodes for the iterable-versus-iterator split and the "file is its own iterator" twist, in paraphrase only.
- No version bump (evidence M).

## Planning evidence

The planning run is read-only, so `<scratchpad>/r11spike` was not created. Every probe ran as inline code with the session scratchpad (`<scratchpad>`) as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `<repo>/.venv/bin/python -I -c CODE`. The version is `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- mypy: `<repo>/.venv/bin/python -I -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET`. The version is `mypy 2.4.1 (compiled: yes)`. Also `pytest 9.2.0`, `ruff 0.17.3`, `uv 0.13.7`.

Snippets are reduced models. Line numbers will differ and are never asserted. Every output is a prediction for the member until the build quotes it as observed.

**A. Generator laziness, `close()`, `break` and `finally`.** `events(n)` logs `start` and `read i`, catches and re-raises `GeneratorExit`, and logs `finally`.
```
created, log: [] GEN_CREATED
first: 0 ['start', 'read 0']
after close: ['start', 'read 0', 'GeneratorExit', 'finally'] GEN_CLOSED
next after close: StopIteration None
break, before anything else: ['start', 'read 0', 'read 1', 'GeneratorExit', 'finally']
break, name still bound: ['start', 'read 0', 'read 1']
after del: ['start', 'read 0', 'read 1', 'GeneratorExit', 'finally']
inside with after break: ['start', 'read 0', 'read 1']
after with: ['start', 'read 0', 'read 1', 'GeneratorExit', 'finally']
cycle after del, gc disabled: ['start', 'read 0']
after collect: ['start', 'read 0', 'GeneratorExit', 'finally']
close before start: []
RuntimeError: generator ignored GeneratorExit
```
- Creating a generator runs nothing. Closing one that never started runs nothing, not even `finally`.
- `for x in events(5): break` over an unnamed generator ran `finally` straight after the loop. That is CPython reference counting, and the language doesn't promise it, so it is stated as observed on 3.15.2 and never asserted.
- With the generator bound to a name, `break` leaves it suspended until `del` (refcount) or `close()`. That is guaranteed while the name holds it, so it is assertable.
- `contextlib.closing` closes at the end of the block. A generator in a reference cycle waits for `gc.collect()`.
- A generator that yields from its `finally` while closing raises `RuntimeError: generator ignored GeneratorExit`.

**B. `itertools` (runtime).**
```
[(0, 1, 2), (3, 4, 5), (6,)]
strict: ValueError('batched(): incomplete batch')
n=0: ValueError('n must be at least one')
[(0, 1, 2), (3, 4, 5)]
(0, 1, 2) pulled [0, 1, 2]
[2, 3, 4] pulled [0, 1, 2, 3, 4]
[0, 1, 2] [3, 4, 5] pulled [0, 1, 2, 3, 4, 5]
[('NLRTM', 'SGSIN'), ('SGSIN', 'DEHAM')]
[]
[1, 2, 3, 4] [1, 2, 3]
islice neg: Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.
<class 'tuple'>
6 0 []
[0, 1, 2] []
['1', '2'] []
[(1, 3), (2, 4)] []
True True
zip strict: zip() argument 2 is shorter than argument 1
```
- `batched` pulled exactly one batch for the first page.
- `islice(src, 2, 5)` pulled five items to return three. Two successive `islice(g, 3)` calls on one generator continue where the first stopped.
- `pairwise` of one item is empty.
- An exhausted iterator, generator expression, `map` or `zip` is silently empty on reuse (`sum` gives 0).
- `iter(it) is it` for an iterator, and `iter([1]) is not iter([1])` for a list.

**C. `yield from`, PEP 479, delegated close, `send`.**
```
items ['a', 'b', 'c', 'd', 'e', 'f', 'g'] return 7
list() drops return: ['a', 'b', 'c', 'd', 'e']
PEP 479: RuntimeError('generator raised StopIteration') cause: StopIteration()
close via yield from: ['inner finally', 'outer finally']
5 12
```
- `total += yield from page(...)` collects each sub-generator's return value. `list()` discards the outer return value.
- A bare `next(it)` inside a generator turns the inner `StopIteration` into `RuntimeError`, with the `StopIteration` as `__cause__`.
- `close()` on the delegating generator runs the inner `finally` first.

**D. mypy on `Iterator`, `Iterable` and `Generator`** (exit 1):
```
<string>:8: error: No return value expected  [return-value]
<string>:15: error: "Iterator[int]" has no attribute "close"  [attr-defined]
<string>:16: error: Value of type variable "_SupportsCloseT" of "closing" cannot be "Iterator[int]"  [type-var]
<string>:19: error: "Iterator[int]" has no attribute "send"  [attr-defined]
<string>:20: error: Argument 1 to "len" has incompatible type "Iterator[int]"; expected "Sized"  [arg-type]
<string>:22: error: Returning Any from function declared to return "int"  [no-any-return]
<string>:22: error: No overload variant of "next" matches argument type "Iterable[int]"  [call-overload]
<string>:27: note: Revealed type is "int"
<string>:28: error: Incompatible return value type (got "int", expected "str")  [return-value]
<string>:31: note: Revealed type is "typing.Generator[int, None, None]"
<string>:34: note: Revealed type is "str"
<string>:35: error: Argument 1 to "send" of "Generator" has incompatible type "int"; expected "str"  [arg-type]
```
- A generator annotated `-> Iterator[int]` can't `return 5` (line 8). `close()`, `closing()` and `send()` need `Generator`, not `Iterator`.
- `def twice(xs: Iterator[int]) -> tuple[int, int]: return sum(xs), sum(xs)` gets **no error**: mypy can't see a second pass over an iterator.
- `yield from` of a `Generator[int, None, int]` is typed `int`.
- `Generator[int]` is accepted with the PEP 696 defaults and reveals `Generator[int, None, None]`.
- A generator annotated `-> Iterable[int]` is accepted.

**E. Iterable against iterator classes.** Under mypy (exit 1):
```
<string>:16: error: Argument 1 to "summarise" has incompatible type "Generator[str, None, None]"; expected "Collection[str]"  [arg-type]
<string>:17: error: Argument 1 to "summarise" has incompatible type "History"; expected "Collection[str]"  [arg-type]
<string>:20: error: "OnlyNext" has no attribute "__iter__" (not iterable)  [attr-defined]
<string>:21: error: Incompatible types in assignment (expression has type "History", variable has type "Iterator[str]")  [assignment]
```
At run time:
```
for over __next__ only: 'OnlyNext' object is not iterable
['a', 'b'] ['a', 'b'] True False
True True
['a', 'b'] []
list grows during iteration: ['a', 'b', 'c', 'd']
dictionary changed size during iteration
```
- A history whose `__iter__` is a generator (`yield from self._e`) walks twice. It is an `Iterable` and not an `Iterator`.
- A cursor whose `__iter__` returns `self` is empty on the second `list()`.
- Asking for `Collection[str]` makes mypy refuse a generator. It also refuses a history that has no `__len__` or `__contains__`, so the snippet for test 34 uses a sized type.

**F. `yield from` value typing and a one-shot class under mypy** (exit 1, one error):
```
<string>:11: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
```
- `with closing(events_from([])) as r` on a `Generator[str, None, int]` passes.
- A `OneShot` class whose `__iter__` returns itself is accepted wherever `Iterable[str]` is asked for. mypy can't tell one-shot from re-iterable.

**G. An unclosed file in a generator.** With `-W error::ResourceWarning`:
```
with block closed: True
bare closed: False
unraisable: ResourceWarning unclosed file <_io.TextIOWrapper name='...' mode='r' encoding='utf-8'>
```
- A generator that opens its file inside `with` closes it when the generator is collected. One that doesn't leaves it open, and the collector reports a `ResourceWarning` through `sys.unraisablehook`.
- The probe read a small system text file outside the repo, and its name is elided here. Under the root `filterwarnings = ["error"]`, pytest's unraisable-exception handling should turn that warning into a failure. This is an executor check for experiment (b) in ch24.

**H. Chain of Responsibility at run time.** The stages are `check_documents`, `assess_duty`, `inspect` and `release`; `clear` returns the first non-`None` decision, else `final`. The commodity is `850760` lithium-ion batteries (restricted).
```
tuple chain: Held(reason='inspection required')
appended after terminal stage: Released()
linked, no terminal, clean: None
tuple, clean: Released()
empty chain: Released()
held: duty unpaid
Held(reason='missing commercial invoice') stages called ['check_documents']
```
- `(check_documents, assess_duty, release) + (inspect,)` releases the batteries. A stage appended after a terminal never runs; this is domain row 23's failing test.
- A linked chain with no terminal returns `None` for a clean declaration.
- An empty chain leaves the decision to `final`.
- A lazily built chain stops pulling stages after the first decision.

**I. Chain of Responsibility under mypy** (exit 1):
```
<string>:25: error: Argument "final" to "clear" has incompatible type "Callable[[Decl], Released | Held | None]"; expected "Callable[[Decl], Released | Held]"  [arg-type]
<string>:32: error: Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"  [arg-type]
<string>:42: error: Argument 1 to "describe" has incompatible type "Released | Held | None"; expected "Released | Held"  [arg-type]
<string>:44: error: Argument 2 to "clear" has incompatible type "tuple[Callable[[Decl], str]]"; expected "Iterable[Callable[[Decl], Released | Held | None]]"  [arg-type]
```
- `clear(Decl(True), (inspect, release))` gets **no error**: `release` returns `Decision`, which is assignable to `Decision | None`, so mypy can't see a terminal placed mid-chain.
- Each of the other risks is an error: a passing stage as `final`, a missing `match` arm, the linked chain's `Decision | None` where a `Decision` is needed, and a stage with the wrong return type.

**J. Mediator against choreography.** `ClearanceMediator` tracks the outstanding set {duty, inspection}. The choreography's billing colleague accepts a settlement only after it has been told of inspection, then releases.
```
['inspect', 'pay'] mediator ['CN-1'] choreography ['CN-1']
['pay', 'inspect'] mediator ['CN-1'] choreography []
['pay', 'pay', 'inspect'] mediator ['CN-1'] choreography []
failed inspection: []
```
- Both forms pass inspection-first. The choreography loses a settlement that arrives first, and the consignment never clears.
- The mediator releases once, in either order, and also once with a duplicate settlement. A failed inspection holds the consignment even after settlement.

**K. The full ch23 candidate under mypy and at run time** (the Example spec's shapes, PEP 695 aliases):
```
<string>:77: error: Argument 1 to "assert_never" has incompatible type "Inspection"; expected "Never"  [arg-type]
```
- `case Inspection(passed=True)` followed by `case Inspection(passed=False)` **doesn't exhaust `Inspection` for mypy 2.4.1**: a `bool` field's literal patterns don't narrow the class. `case Inspection(passed=True)` then `case Inspection()` exits 0. The member uses the second form, and test 27 witnesses the first as a reduced model.
- Run time: `clear_by_match` on an unpaid battery declaration gives `Held(reason='duty unpaid')`, and `clear(d, ())` gives `Released()`. The mediator gives `[]` after a settlement alone, `['CN-1']` after the inspection, and still `['CN-1']` after a second settlement.

**L. `sentinel` (3.15) against `None` for "pass it on".**
- `sentinel` is a builtin (`PASS <class 'sentinel'>`). mypy 2.4.1 narrows `int | PASS` on `is PASS` (revealed `PASS`, then `int`; exit 0).
- A stage that falls off the end is `Missing return statement  [return]` under both `str | None` and `str | PASS`. `None` is kept (decision 2b).

**M. Upstream survey** (PyPI JSON and python.org FTP, 2026-11-05):
- PyPI, latest release and upload date: pytest 9.2.0 (2026-10-27), mypy 2.4.1 (2026-10-28), ruff 0.17.3 (2026-10-27), pytest-mock 3.17.0 (2026-10-17) and uv 0.13.7 (2026-11-03).
- CPython: the 3.15 line ends at 3.15.2, and `3.16.0/` holds only `Python-3.16.0a1.tar.xz`, a pre-release.
- Every pin is the latest stable release, so no bump is proposed.

**Sources fetched 2026-11-05.** The fetch tool can shorten or paraphrase, so prose agents re-fetch, the page text wins, and a quotation stops where the page's sentence stops.
- **The docs moved two pages under `builtins/`.** `https://docs.python.org/3/library/functions.html` and `.../library/stdtypes.html` redirect (301) to `https://docs.python.org/3/builtins/functions.html` and `https://docs.python.org/3/builtins/stdtypes.html`. Chapters cite the `builtins/` URLs. No chapter cites either page today.
- **Glossary** (https://docs.python.org/3/glossary.html, banner 3.15.2):
  - iterable: "When an iterable object is passed as an argument to the built-in function iter(), it returns an iterator for the object. This iterator is good for one pass over the set of values."
  - iterator: "Attempting this with an iterator will just return the same exhausted iterator object used in the previous iteration pass, making it appear like an empty container."
  - generator iterator: "Each yield temporarily suspends processing, remembering the execution state (including local variables and pending try-statements)."
- **Built-in functions** (`builtins/functions.html`):
  - `iter()`: "If the second argument, *sentinel*, is given, then the first argument must be a callable object." The block-reader example is usable as a mention, not as code.
  - `next()`: "If *default* is given, it is returned if the iterator is exhausted, otherwise StopIteration is raised."
- **Built-in types, `generator.close()`** (`builtins/stdtypes.html#generator.close`):
  - "Raises a GeneratorExit exception at the point where the generator function is currently suspended (equivalent to calling throw(GeneratorExit))."
  - "If the generator yields a value, a RuntimeError is raised."
  - "When a generator iterator is garbage collected before it has exited, close() is called automatically."
  - A "Changed in version 3.13" note covers the return value of `close()`.
- **Expressions, yield expressions** (https://docs.python.org/3/reference/expressions.html): "If the generator is not resumed before it is finalized (by reaching a zero reference count or by being garbage collected), the generator-iterator's close() method will be called, allowing any pending finally clauses to execute."
- **contextlib.closing** (https://docs.python.org/3/library/contextlib.html): "Return a context manager that closes thing upon completion of the block."
- **itertools** (https://docs.python.org/3/library/itertools.html, banner 3.15.2):
  - intro: "This module implements a number of iterator building blocks inspired by constructs from APL, Haskell, and SML."
  - `batched`: "Batch data from the iterable into tuples of length n. The last batch may be shorter than n." "If strict is true, will raise a ValueError if the final batch is shorter than n." "The input is consumed lazily, just enough to fill a batch." Added in 3.12; *strict* added in 3.13.
  - `islice`: "Make an iterator that returns selected elements from the iterable."
  - `pairwise`: "Return successive overlapping pairs taken from the input iterable."
  - `chain.from_iterable`: "Gets chained inputs from a single iterable argument that is evaluated lazily."
- **PEP 255**, "Simple Generators" (Schemenauer, Peters, Hetland; Final; 2.2). The fetch truncated the abstract, so the prose agent quotes only what it re-reads. "Instead a generator-iterator object is returned;" is usable as a fragment.
- **PEP 380**, "Syntax for Delegating to a Subgenerator" (Gregory Ewing; Final; 3.3): "Additionally, the subgenerator is allowed to return with a value, and the value is made available to the delegating generator." Also "The value of the `yield from` expression is the first argument to the `StopIteration` exception raised by the iterator when it terminates."
- **PEP 479**, "Change StopIteration handling inside generators" (Chris Angelico, Guido van Rossum; Final; 3.5): "This PEP proposes a change to generators: when StopIteration is raised inside a generator, it is replaced with RuntimeError."
- **Rhodes, "The Iterator Pattern"** (https://python-patterns.guide/gang-of-four/iterator/). Sections in order:
  - the verdict: Python supports the pattern at language level;
  - the `for` loop;
  - the iterable and its iterator, with `iter()`, `next()` and `StopIteration`;
  - objects that are their own iterator (files, a mailbox parser);
  - implementing an iterable and an iterator (`__iter__`, `__next__`);
  - Python's extra level of indirection (PEP 234 and the legacy `__getitem__`).

  It says little about generator functions and `yield`, and nothing about `itertools`. Its recommendation sentence, "Instead, have them pass the container and call `iter()` yourself.", is to be re-verified before any quotation. Credit it in paraphrase for the iterable/iterator split and the self-iterating file.
- **Rhodes has no Mediator or Chain of Responsibility page** (index plus two 404s).
- **GoF** isn't quotable (r06 finding). Bracketed items are used only if a prose agent verifies them in the book; otherwise the idea is described without attribution:
  - [GoF lists that a request may reach the end of the chain unhandled, receipt not guaranteed, as a CoR consequence];
  - [GoF warns that a mediator can grow monolithic];
  - [GoF distinguishes external from internal iterators];
  - [GoF raises iterators that stay robust while the aggregate changes];
  - [GoF's Iterator operations: First, Next, IsDone, CurrentItem].
- **O'Reilly**: *Fluent Python* 2nd ed. (iterators and generators) and *Effective Python* 3rd ed. (generator items). Chapter and item titles weren't checked, so they stay bracketed.

Repo facts:
- **Reconciliation.** Rows run 1-119, so r11 adds 120-133. No open row is owned by ch23 or ch24. Row 20 (ch38, async generator, legacy) isn't changed. `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** `_data/diagrams.yml` has 23 entries; r11 makes 25 (`section: "Ch. 23"` and `"Ch. 24"`).
- **Test names.** There are 517 `def test_` lines across `examples` and `spikes`. Every name in the Example spec was checked against the unique set and none collides. Three near-misses exist and aren't reused: `test_history_is_sized_and_reiterable` (ch7), `test_iterator_is_a_lazy_generator` (ch3) and `test_mypy_reports_a_missing_match_arm` (ch21). The executor re-runs `grep -rhoE "def test_\w+" examples spikes --include='*.py' | sort | uniq -d`.
- **Already taught, so not repeated** (each gets a pointer by title and at most one sentence):
  - The generator form of `pages` and its laziness test: "What 1994 assumed, and what Python dissolves".
  - The ch3 table rows (Iterator dissolves; Mediator and CoR survive) and the coordination paragraph: "The three-way split: dissolve, survive, disambiguate".
  - `__iter__` returning a fresh iterator, `__len__`, `__contains__` and truth on `TrackingHistory`: "The data model: dunder methods as the substrate". ch7 states the self-returning case in one sentence without a test, and ch24 measures it.
  - `@contextmanager` as a generator, the `try` it needs, and the 3.15 decorator change: "Context managers: deterministic cleanup". ch24 uses `contextlib.closing` only, from the consumer's side.
  - Closed unions with `match` and `assert_never`: "Composite and Flyweight" and "State and finite state machines". ch23 uses them and doesn't re-teach them. Only the `bool` literal-pattern finding (evidence K) is new.
  - Callables in a slot: "Strategy: the callable". `X | None` for "no answer": "Protocol, duck typing, and structural typing with mypy".
  - Signal, subscribers and the string-topic bus: "Observer". ch23 points to it once to separate a mediator from a signal.
  - Customs hooks per destination: "Template Method and the function alternative" already points to ch23 for "clearance stages that can stop a consignment", and "State and finite state machines" points to it for ordered stages. Neither needs a pointer back.
  - Negative fixtures, the mypy-API helper and deletion tables: "Proving it works: pytest, pytest-mock, and mypy".
- **Stubs whose ground must not be taken or described** (prose names no content for any of them):
  - "asyncio and the patterns": one pointer by exact title in ch24 only (decision 5);
  - "Shortcut patterns: dict dispatch, function tables, and EAFP": ch23 builds no dispatch table;
  - "singledispatch: the Visitor the language gives you";
  - "Visitor, Memento, and Interpreter";
  - "The GIL and performance": `Signal`, the mediator and the readers are single-threaded, said once with no claim, and the glossary's free-threading note isn't used;
  - "Final project".
- **Status board hygiene.** `r10.x` and `r10b.x` are tagged, but r10's K7, r10b's L8 and PDP-121a to PDP-122c still read `todo`/`active`, and `iteration-plan.md` marks r10b "(active)". No r11 token depends on them; the orchestrator closes them at M0.

## What is new in each chapter

**ch23 (Mediator and Chain of Responsibility survive).** "The three-way split" says only that a Mediator centralises who talks to whom and a chain decides who handles a request. This chapter witnesses both:
- **The chain as data.**
  - A tuple of `ClearanceStage` callables, where the first decision wins and later stages aren't called.
  - The order changes the answer (documents before duty).
  - The final stage always decides, and its type can't pass.
- **The two failures a chain still has.**
  - A linked chain returns `None` off the end (evidence H).
  - A stage appended after a terminal clears restricted batteries, and mypy accepts it (evidence I).
  - A closed, fixed rule set is a `match` with a default, and the chapter says when that's the better form.
- **The Mediator's rule in one place.**
  - Release needs duty and inspection, arrives once in either order, and a failed inspection holds the consignment.
  - The choreography, where colleagues call each other, loses an early settlement (evidence J).
  - A mediator decides and a signal broadcasts: one paragraph, pointing to "Observer".
- **Types.** mypy refuses a passing final stage, a stage with the wrong return type, a stage that forgets to decide, an unhandled decision and an unknown message. It can't see a terminal placed mid-chain, and it can't exhaust `True`/`False` field patterns (evidence K).

**ch24 (Iterator dissolves).** "What 1994 assumed, and what Python dissolves" shows one generator and says that it is lazy. This chapter adds:
- **The protocol, measured.**
  - `iter(it) is it`, and a `__next__`-only class isn't iterable.
  - A generator-based `__iter__` makes `TrackingHistory` re-iterable. The cursor written to the protocol is one-shot: it is empty on a second pass and cuts a nested walk short.
  - An exhausted generator looks empty, as the glossary says. mypy can't see a second pass, but `Collection` makes it refuse a generator.
- **How much to read.**
  - The first page reads 3 events, against 1,000,000 for an eager list.
  - A short last page is kept and a size below one is refused.
  - `page` reads only up to the page it returns.
  - `pairwise` finds an event that steps back in the lifecycle, and `chain.from_iterable` starts each history only when the last is done.
- **Delegation.** `yield from` hands back the line count, `list()` drops it, and mypy types it. PEP 479 turns a leaked `StopIteration` into `RuntimeError`.
- **Cleanup.**
  - A reader never started opens no file, and `close()` runs its `finally` and closes the file.
  - `break` leaves a named reader open. `contextlib.closing` closes it at the end of the block, and an abandoned one closes when collected.
  - mypy refuses `close()` and `closing()` on an `Iterator`, which is why `read_events` is annotated `Generator`.

## Approach

- **Thesis wording.**
  - ch23 says both patterns survive.
    - Python removes the handler base class with its successor link, and the abstract Mediator and Colleague classes.
    - What remains for CoR: the pass-along rule, the order and the terminal.
    - What remains for Mediator: the coordination rule and its state, in one place, so colleagues don't call each other.
  - ch24 says Iterator dissolves.
    - The cursor class is gone, replaced by a generator or a generator-based `__iter__`.
    - Three decisions remain for the designer and aren't in the language: one pass or many, how much to read, and who closes the source.
- **Credit.**
  - GoF where each pattern is introduced, in plain paraphrase that doesn't track the Intent wording.
  - Rhodes's "The Iterator Pattern" in ch24, in paraphrase. No Rhodes page is claimed in ch23.
  - The glossary, built-in functions, built-in types, expressions, `contextlib` and `itertools` docs, and PEPs 255, 380 and 479, each quoted exactly from fetched pages.
- **Domain names** come from `_plans/shipping-domain-model.md` rows 23-24, the area table and the series supporting names, plus the names in decisions 3 and 7, recorded at M0. There's no new domain area and no new carrier code.
  - Port codes are UN/LOCODEs (`NLRTM`, `SGSIN`, `DEHAM`).
  - HS codes `850760` (lithium-ion batteries, restricted) and `090111` (coffee, not roasted) are illustrative, and each chapter says so once.
  - ch23 (Documentation, Billing, Tracking): `ConsignmentId`, `DocumentKind`, `Commodity`, `CustomsDeclaration`, `Released`, `Held`, `Decision` (alias), `ClearanceStage` (alias), `FinalStage` (alias), `check_documents`, `assess_duty`, `inspect_goods`, `release`, `CLEARANCE_STAGES`, `clear`, `describe`, `Settlement`, `Inspection`, `ClearanceMessage` (alias), `ClearanceMediator`, `ClearanceError`, `HandlingKind`, `HandlingEvent`, `TrackingHistory`.
  - ch24 (Tracking): `ConsignmentId`, `HandlingKind`, `HandlingEvent` (one class with a `HandlingKind` enum; the chapter says so), `TrackingHistory`, `pages`, `page`, `out_of_order`, `events_of`, `Opener` (alias), `open_utf8`, `events_from`, `read_events`, `TrackingLogError`.
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/23-mediator-and-chain-of-responsibility` (project `mediator-chain`, package `mediator_chain`);
  - `examples/24-iterator-generators-and-the-iterator-protocol` (project `iterator-protocol`, package `iterator_protocol`).
- **mypy witnesses** copy the r10 `_run`/`_codes` helper (`mypy_path` set to the member's `src`, `--cache-dir os.devnull`, the anchored regex `re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)`).
  - Each asserts the exit status, an exact `_codes()` set and one or two stable substrings. It never asserts line numbers or optional notes.
  - Snippets import real `src` names wherever possible. Reduced models are named in the prose.
- **mypy.api raises the recursion limit** (r10 correction). Neither member has a recursion-sensitive test. Every member is still run once in reverse file order (`uv run pytest -q tests/test_static.py` followed by the other test files, last file first). The result must match the forward run's pass count (criterion 2).
- **Comparison code** (the owner's 2026-11-04 rule). Every comparison form is real, runs on the shared table **as a conftest fixture param**, and appears in at most one excerpt per chapter. The idiomatic code is the lesson.
  - ch23:
    - `chain_form` `stages|linked|match` (`_Handler` with `successor`; `_clear_by_match`);
    - `coordination_form` `mediator|choreography` (`_Choreography`).
    - The one comparison excerpt is `_Handler.handle` (its `else None`). The match form and the choreography are described in prose only.
  - ch24: `history_form` `iterable|self-iterator` (`_OneShotHistory`). The one excerpt is `_OneShotHistory.__iter__`/`__next__`.
  - All of them live in `tests/conftest.py`, because sibling test imports are blocked under `--import-mode=importlib`. Forms that fail a row on purpose (the linked chain's `None`, the choreography's lost settlement, the one-shot's second pass) get their own tests and aren't table rows.
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (M1a, M1b) name the test and say why it sees the deletion. A row whose witness was predicted, not run, is marked "executor check".
- **"Not called", "not read" and "skipped" claims** (r10 correction). Each such claim has a test that fails on a named plausible mutation:
  - stages after a decision (mutation: evaluate every stage into a list first);
  - release before both reports (mutation: don't track duty);
  - events beyond the first page (mutation: `list()` first);
  - a never-started reader opening no file (mutation: open before the generator starts);
  - the second history in `events_of` (mutation: `chain(*[list(h) for h in histories])`).
- **Determinism and garbage collection.**
  - No `mock`, `mocker`, `monkeypatch`, `print(`, `sleep` or wall clock.
  - The reader tests assert on a handle the test opener recorded, never on `id()`.
  - No test asserts that a generator was finalised before `gc.collect()` unless a bound name guarantees it is still alive. "break leaves a named reader open" is assertable; the unnamed-loop case (evidence A) is a CPython observation in prose only.
  - The abandoned-reader test deletes its names and calls `gc.collect()` explicitly before asserting. A comment says why: CPython usually closes at the last reference, and the language promises nothing.
  - The test that counts pulled events builds a counting generator in the test and never asserts bytes or time.
  - `filterwarnings = ["error"]` stays active, so an unclosed file in a test fails it.
- **Counts** of test functions and cases come from the code, and the pytest summary line wins (every iteration since r07 differed from plan arithmetic).

Rejected:
- A `Handler` or `Mediator` ABC in `src`.
- A string-topic bus anywhere in ch23 (the Observer chapter owns that witness).
- A dict dispatch table in ch23 (the shortcut-patterns chapter's ground).
- Async generators, `aclosing` or `async for` in ch24 (decision 5).
- `iter(callable, sentinel)` as an example (no domain case without a new name; it gets one sentence, sourced).
- `itertools.tee` (a thread-safety warning the book doesn't own).
- Any assertion on bytes, timing or `id()` values.
- `typing.cast` or `Any` in `src`.

## Per-chapter spec

### ch23: Mediator and Chain of Responsibility (pattern, has_example = true, bucket: survives)

Thesis:
- **Chain of Responsibility.** Its force is a request that several parties may handle, where the sender shouldn't know which one.
  - Python removes the handler class and the `successor` link: a tuple of callables, where `None` means pass it on.
  - Three things survive: what "pass it on" means, the order, and who decides when nobody does.
- **Mediator.** Its force is a group of parties whose actions depend on one another.
  - Python removes the Mediator and Colleague classes: colleagues hold a callable, the mediator's `receive`.
  - The rule survives, written once with its state, so no colleague needs to know another.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one of them from a comparison fixture):
1. `## Learning objectives` (~90), five bullets, one per close bullet.
2. `## Why this matters` (~200). Intent first: customs clearance as a sequence of checks that can each stop a consignment, then a release that needs two parties. Three failures:
   - a stage added after release clears restricted batteries (test 8);
   - a linked chain returns nothing for a clean declaration (test 6);
   - a settlement that arrives before inspection is lost by colleagues that call each other, and the consignment never clears (test 14).
3. Figure plus one paragraph (~60).
4. `## A chain is a tuple of stages` (~500). Excerpt `clear`, plus the two type aliases.
   - GoF credited for Chain of Responsibility in plain paraphrase. Bucket: survives, with one sentence pointing to "The three-way split: dissolve, survive, disambiguate".
   - `None` passes the declaration on, with one sentence pointing to "Protocol, duck typing, and structural typing with mypy" for `X | None`.
   - All three forms hold a restricted commodity, a missing document and unpaid duty (tests 1-3).
   - The first stage that decides wins (test 4), and later stages aren't called (test 7).
   - A clean declaration is released by the final stage (test 5).
   - The comparison excerpt `_Handler.handle` shows where a linked chain ends: `None` (test 6). [GoF's "receipt isn't guaranteed", if verified.]
5. `## The terminal and the order` (~400):
   - `final` is typed to always decide: mypy refuses a stage that can pass (test 20) and a stage that forgets to return (test 23).
   - Appending to `CLEARANCE_STAGES` lands before the final stage (test 9). An empty chain leaves the decision to it (test 10).
   - mypy can't see a release placed inside the chain (test 21), and at run time the batteries are cleared (test 8). Say plainly that the type system checks each stage's shape, not their order.
   - `describe` consumes a decision with `match` (test 11), and a missing arm is a mypy error (test 24).
   - When the rules are closed and fixed, one `match` with a default is the chain. It passes the same table (tests 1-4[match]), but its order lives in source and a caller can't extend it. One sentence on the form, and no dispatch-table material.
6. `## Mediator: one place decides when to release` (~550). Excerpt `ClearanceMediator.receive`, plus `_try_release` if words allow.
   - GoF credited for Mediator in plain paraphrase. Bucket: survives.
   - A held declaration waits on billing and inspection, which report through `receive`.
   - Release waits for both in either order and isn't called after the first report (test 13). It happens once, even with a duplicate settlement (test 15), and records `CLEARED` at the port (test 19).
   - A failed inspection holds the consignment (test 16). A declaration with nothing outstanding is released at once (test 17). A message for another consignment is refused (test 18).
   - The choreography form passes inspection-first (test 12[choreography]) and loses an early settlement (test 14). Describe its wiring in two sentences, with no excerpt.
   - Types: mypy refuses a message the mediator doesn't know (test 26), and can't exhaust `True`/`False` field patterns, which is why the second arm is `case Inspection()` (test 27, reduced model, one sentence).
7. `## A mediator decides, a signal broadcasts` (~180). One paragraph pointing to "Observer" by title:
   - a signal delivers to an open set and decides nothing about what they do;
   - a mediator knows its colleagues' messages and decides who acts next;
   - the release callable could be a signal's `publish`.
   - [GoF on a mediator growing monolithic, if verified], stated as the cost.
8. `## When not to use it` (~180):
   - one check (call it);
   - a fixed set of rules nobody extends (a `match` with a default);
   - parties that don't depend on each other's replies (a signal);
   - a mediator that starts making decisions belonging to a colleague (move the rule back).

   Then the sidebar, in the new form:

   <blockquote class="ai-sidebar" markdown="1"> **Assistant-written chains and mediators.** Asked for "a chain of responsibility", an assistant often writes a handler base class with a `successor` that returns nothing off the end, and asked for coordination it often wires parties to call each other. Paste a prompt that states the rules:

   > Write the clearance chain as `clear(declaration, stages, /, *, final=release)`, where each stage is a typed callable returning `Decision | None`, `None` passes the declaration on, the first decision wins, and `final` is typed `Callable[[CustomsDeclaration], Decision]` so it can't pass. Write release coordination as one `ClearanceMediator` that receives a closed union of messages through `match` with `assert_never`, releases only after duty and inspection both report, in either order, and releases once.

   If the reply puts the terminal inside the tuple or lets colleagues call each other, ask for the test that fails.</blockquote>

   The sidebar body is at most 120 words by `validate.word_count`. Every backticked name in it exists in `src`.
9. `## Build, run, observe` (~220 plus output). Each experiment runs in a fresh scratch copy: delete the copy's `.venv`, re-sync, and confirm `mediator_chain.__file__` points into the copy. Each changes one thing and is then reverted. Each runs a filter chosen by the prose agent, which then runs `uv run mypy --strict src tests`. **The filter is stated in the chapter, and the chapter quotes its complete output** (r10 correction):
   - (a) In `clear`, compute every stage's decision first (`decisions = [stage(declaration) for stage in stages]`) and return the first non-`None`. Expected: only test 7 fails, with an `assert` on the recorded stage names; mypy exits 0. The answer is the same, but the work done differs. Executor check: whether test 4 still passes. Quote as observed.
   - (b) In `_try_release`, drop the `not self._released` condition. Expected: test 15 fails, with the history holding two `CLEARED` events; mypy exits 0. Executor check: whether test 13 also fails. Quote as observed.
10. `## What you can do now` (~150): five bullets, one per objective, in the same order. Each names the artifact (the `clear` signature, test 8, `ClearanceMediator.receive`, test 14, the static witnesses). Every backticked token in the close appears earlier in the chapter.
11. `## For deeper coverage` (~120):
    - GoF (Chain of Responsibility, Mediator);
    - the Python tutorial or reference on `match` (the prose agent picks and fetches one URL and quotes nothing it didn't read);
    - PEP 695 for the aliases;
    - [Ramalho, *Fluent Python* 2nd ed., on pattern matching, if verified];
    - the bibliography link.

Figure `23-mediator-and-chain-of-responsibility` (vertical):
- Top accent box `CustomsDeclaration`.
- Below it, `clear`, then a column of stage boxes: `check_documents`, `assess_duty`, `inspect_goods`. Each has a side arrow labelled "Held: stop here" and a down arrow labelled "None: pass it on".
- Bottom of the column: `release`, "final stage: always decides".
- From a `Held` side box, an arrow leads to `ClearanceMediator`, "releases once, after both report". `Settlement` and `Inspection` boxes point into it, and it points out to `TrackingHistory.record`, labelled "CLEARED".
- A muted, dashed side box: "linked chain: falls off the end with None".
- No numbers in the SVG.

Caption draft (39 words with the prefix): "Figure 23.1: A declaration passes along an ordered tuple of clearance stages until one decides, and the final stage always does. A held consignment then waits on a mediator that releases it once, after duty and inspection both report."

### ch24: Iterator: generators and the iterator protocol (pattern, has_example = true, bucket: dissolves)

Thesis:
- Iterator's force is a consumer that pulls items one at a time without knowing how the producer stores them.
- Python builds the protocol into the data model, and a generator function writes the cursor for you. The pattern dissolves.
- Three decisions are left, and a generator doesn't make them:
  - whether the thing passed around can be walked twice (an iterable) or once (an iterator);
  - how much of the source a caller reads;
  - who closes the source when the consumer stops early.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one of them from the comparison fixture):
1. `## Learning objectives` (~90), five bullets.
2. `## Why this matters` (~200). Intent first: a tracking history read page by page by a display and a report. Three failures:
   - the first page of an eagerly listed feed reads 1,000,000 events (test 12);
   - a report walks a generator twice and its second pass finds nothing, with no error (test 7);
   - a reader abandoned with `break` still holds its file open (test 27).
3. Figure plus one paragraph (~60).
4. `## The protocol, and what a generator writes for you` (~400). Excerpt `TrackingHistory.__iter__`.
   - GoF credited for Iterator in plain paraphrase [cursor operations, if verified]. Rhodes's "The Iterator Pattern" credited in paraphrase for the iterable/iterator split.
   - Bucket: dissolves, with one sentence pointing to "What 1994 assumed, and what Python dissolves".
   - Quote the glossary's generator-iterator sentence.
   - `iter(it) is it` (test 8). A class with only `__next__` isn't iterable at run time (test 9) or for mypy (test 36).
   - Both forms walk every event in order (tests 1-2).
   - PEP 255 credited for generators.
5. `## One pass or many` (~450). The one comparison excerpt is `_OneShotHistory`.
   - The history walks twice and nests (tests 3, 5). The one-shot form is empty on the second pass and cuts a nested walk short (tests 4, 6).
   - Quote the glossary iterable sentence ("good for one pass") and the iterator sentence, ending at "making it appear like an empty container."
   - An exhausted generator looks empty (test 7). One sentence pointing to "The data model: dunder methods as the substrate" for the fresh-iterator `__iter__`.
   - mypy can't see a second pass (test 33) and accepts the one-shot form as an `Iterable` (test 37). Asking for `Collection` makes it refuse a generator (test 34). Both are reduced models, named.
6. `## Read only what you need` (~450). Excerpt `pages` and `page`.
   - One sentence pointing to "What 1994 assumed, and what Python dissolves" for `pages`.
   - Measured: the first page reads 3 events (test 11) against 1,000,000 for an eager list (test 12). Quote the `batched` laziness sentence.
   - A short last page is kept (test 13) and a size below one is refused by `batched` (test 14).
   - `page` reads only up to the page it returns (test 15), numbers pages from 1 (test 16), and returns an empty tuple past the end (test 17). Quote the `islice` first sentence.
   - `out_of_order` uses `pairwise` (tests 18-19), and `events_of` uses `chain.from_iterable` (test 20). Quote each first sentence.
   - One sentence: `strict=True` refuses a short last batch, quoting the docs. No test, because `src` doesn't use it; the sentence rests on the source and evidence B.
7. `## Delegating with yield from` (~250). Excerpt `read_events` (with `events_from` if words allow).
   - The reader parses each line (test 21). `yield from` hands the line count back (test 22), `list()` drops it (test 23), and mypy types it (test 35). Quote PEP 380.
   - A malformed line is refused with its number (test 24).
   - A `StopIteration` leaking from `next()` inside a generator becomes `RuntimeError` (test 10). Quote PEP 479, and say that `page` uses `next(..., ())` to stay clear of it.
8. `## Who closes the source` (~400):
   - A reader never started opens no file (test 25).
   - `close()` raises `GeneratorExit` at the paused `yield`, runs the `finally`, and closes the file (test 26). Quote the `generator.close()` sentences.
   - `break` leaves a named reader open (test 27), and `contextlib.closing` closes it at the end of the block (test 28; quote `closing`).
   - An abandoned reader closes when collected (test 29). Quote the yield-expressions sentence, and explain `gc.collect()` in the test.
   - One sentence: an unnamed generator in a `for` loop closed straight after `break` in a recorded run on CPython 3.15.2 (evidence A), which the language doesn't promise.
   - mypy refuses `close()` (test 30) and `closing()` (test 31) on an `Iterator`, and accepts both on the reader (test 32). That is why `read_events` is annotated `Generator[HandlingEvent, None, int]`.
   - One sentence: the asynchronous form and its own cleanup rule belong to "asyncio and the patterns", by exact title (decision 5). Nothing more.
9. `## When not to use it` (~180):
   - data already in a list that callers index or measure (pass the tuple);
   - a result needed twice (materialise once, or pass an iterable);
   - a source that must be closed at a known point (a context manager owns it, and the generator only reads);
   - a single value (return it).

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Assistant-written iterators.** Asked to "make the history iterable", an assistant often writes a cursor class whose `__iter__` returns `self`, or builds a list to return one page. Paste a prompt that states the decisions:

   > Make `TrackingHistory.__iter__` a generator so every loop gets a fresh iterator. Write `pages(history, size)` with `itertools.batched` so the first page reads only `size` events, and `page(history, number, size)` with `islice`. Write the log reader as a generator that opens its file inside `with`, annotate it `Generator[HandlingEvent, None, int]`, and close it with `contextlib.closing` where a caller may stop early.

   If the reply returns `self` from `__iter__` or builds a `list` first, ask for the test that fails.</blockquote>
10. `## Build, run, observe` (~220 plus output). The scratch-copy rules and the stated-filter rule are the same as ch23's:
    - (a) In `TrackingHistory`, create one iterator in `__init__` and return it from `__iter__`. Expected: tests 3 and 5 fail, and 1[iterable] may also fail (executor check); mypy exits 0. Quote as observed.
    - (b) In `read_events`, replace `with opener(path) as lines:` with `lines = opener(path)`. Expected: tests 26, 28 and 29 fail on `closed`, and the collector's `ResourceWarning` may add a `PytestUnraisableExceptionWarning` error (evidence G; executor check); mypy exits 0. Quote as observed.
11. `## What you can do now` (~150): five bullets mapped one to one to the objectives.
12. `## For deeper coverage` (~130):
    - GoF (Iterator);
    - Rhodes, "The Iterator Pattern";
    - the glossary entries;
    - built-in functions (`iter`, `next`) and built-in types (generator methods);
    - the expressions reference (yield expressions);
    - `itertools`, and `contextlib.closing`;
    - PEPs 255, 380 and 479;
    - [Ramalho, *Fluent Python* 2nd ed., on iterators and generators, if verified];
    - the bibliography link.

Figure `24-iterator-generators-and-the-iterator-protocol` (vertical):
- Top accent box `TrackingHistory`, "each loop gets a fresh iterator".
- Two arrows down to two `__iter__` boxes ("walk one", "walk two").
- A muted, dashed side box: "self-iterating cursor: empty on the second pass".
- Below, `pages`, "batched: reads one page at a time", then `page`, "islice: stops at the page it returns".
- A separate column on the right: `read_events`, "opens inside with", then `close()`, "GeneratorExit, finally, file closed". A side note reads "break alone: still open while named".
- No numbers in the SVG.

Caption draft (40 words with the prefix): "Figure 24.1: A tracking history hands each loop a fresh iterator, while a generator is good for one pass. Pages are pulled lazily, one batch at a time, and closing a reader runs its finally block and closes its file."

Citations, both chapters: verify each before writing, apply the bracketed fallbacks, quote no sentence unless it was checked on a fetched page, stop each quotation where the page's sentence stops, and make no comparison between languages.

## Example spec

### `examples/23-mediator-and-chain-of-responsibility` (project `mediator-chain`, package `mediator_chain`)

`pyproject.toml` in the r10 shape (`requires-python = ">=3.15"`, `uv_build`, no `[tool.*]`).

- `domain.py`:
  - `ConsignmentId = NewType("ConsignmentId", str)`.
  - `DocumentKind(Enum)`: `COMMERCIAL_INVOICE`, `DANGEROUS_GOODS_DECLARATION`.
  - `Commodity(hs_code, description, restricted: bool)`, frozen slotted.
  - `CustomsDeclaration(consignment_id, port, commodity, documents: frozenset[DocumentKind], duty_paid: bool)`, frozen slotted kw_only. Its docstring says `duty_paid` means paid in full.
  - `HandlingKind(Enum)`: the five kinds.
  - `HandlingEvent(consignment_id, kind, port)`, frozen slotted.
  - `TrackingHistory`, a plain class with `record(event, /)` and an `events` tuple property.
- `clearance.py`:
  - `Released`, `Held(reason: str)`, frozen slotted; `type Decision = Released | Held`.
  - `type ClearanceStage = Callable[[CustomsDeclaration], Decision | None]` and `type FinalStage = Callable[[CustomsDeclaration], Decision]`.
  - `check_documents`: a commercial invoice is always needed, and a dangerous goods declaration when `restricted`. The `Held` reasons are `"missing commercial invoice"` and `"missing dangerous goods declaration"`.
  - `assess_duty` (`"duty unpaid"`), `inspect_goods` (`"inspection required"` when `restricted`), and `release` (always `Released()`).
  - `CLEARANCE_STAGES: tuple[ClearanceStage, ...] = (check_documents, assess_duty, inspect_goods)`.
  - `clear(declaration, stages: Iterable[ClearanceStage], /, *, final: FinalStage = release) -> Decision`, in evidence H's shape, with a walrus.
  - `describe(decision: Decision) -> str` via `match` and `assert_never` (`"released"`, `"held: <reason>"`).
- `mediator.py`:
  - `Settlement(consignment_id)` and `Inspection(consignment_id, passed: bool)`, frozen slotted; `type ClearanceMessage = Settlement | Inspection`.
  - `ClearanceError(ValueError)`.
  - `ClearanceMediator(declaration, *, release: Callable[[HandlingEvent], None])`:
    - the outstanding set is computed from `duty_paid` and `restricted`;
    - `receive(message, /)` refuses another consignment's message with `ClearanceError(f"message for {id!r} sent to the mediator for {own!r}")`, then uses `match` (`case Settlement()`, `case Inspection(passed=True)`, `case Inspection()`, `case _: assert_never`), then calls `_try_release`;
    - `_try_release` calls `release` once, with `HandlingEvent(id, HandlingKind.CLEARED, port)`, when nothing is outstanding and nothing failed;
    - `__init__` also calls `_try_release`;
    - the docstring says single-threaded.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `declaration` factory with overrides. The default is a coffee declaration with an invoice, paid. `BATTERIES` and `COFFEE` constants.
- `chain_form` params `stages|linked|match`, each giving `Callable[[CustomsDeclaration], Decision | None]`:
  - `stages` is `lambda d: clear(d, CLEARANCE_STAGES)` written as a def, because ruff E731 forbids assigning a lambda;
  - `linked` builds `_Handler(check_documents, _Handler(assess_duty, _Handler(inspect_goods)))`;
  - `match` is `_clear_by_match`.
- `coordination_form` params `mediator|choreography`, giving an object with `settle()`, `inspect(passed)` and a `history` (a small test-local Protocol). `_Choreography` wires three closures that call each other (inspection, then billing, then release), with no bus.

`test_chain.py`:
1. `test_a_restricted_commodity_is_held_for_inspection` x `chain_form` (3): batteries with both documents, paid; `Held("inspection required")`.
2. `test_a_declaration_missing_a_document_is_held[commercial-invoice|dangerous-goods]` x `chain_form` (6).
3. `test_an_unpaid_declaration_is_held_for_duty` x `chain_form` (3).
4. `test_the_first_stage_that_decides_wins` x `chain_form` (3): no invoice and unpaid gives `"missing commercial invoice"`.
5. `test_a_clean_declaration_is_released`: `clear(coffee, CLEARANCE_STAGES)` is `Released()`.
6. `test_a_linked_chain_with_no_terminal_returns_none`: the domain row 23 failing test.
7. `test_stages_after_a_decision_are_not_called`: recording stages; the list equals the names up to the first decision.
8. `test_a_stage_added_after_release_clears_a_restricted_commodity`: `(check_documents, assess_duty, release) + (inspect_goods,)` releases the batteries (domain row 23).
9. `test_a_stage_added_to_the_chain_runs_before_the_final_stage`: `CLEARANCE_STAGES + (hold_all,)` on coffee is `Held`.
10. `test_an_empty_chain_leaves_the_decision_to_the_final_stage[release|hold]` (2).
11. `test_describe_names_every_decision[released|held]` (2).

`test_mediator.py`:
12. `test_release_follows_inspection_then_settlement` x `coordination_form` (2): one `CLEARED` event.
13. `test_the_mediator_releases_in_either_order[inspection-first|settlement-first]` (2): the history is empty after the first message and holds one `CLEARED` after the second.
14. `test_a_choreography_loses_a_settlement_that_arrives_before_inspection`: an empty history after both reports.
15. `test_a_duplicate_settlement_releases_once`.
16. `test_a_failed_inspection_holds_the_consignment`: no release after a settlement either.
17. `test_a_declaration_with_nothing_outstanding_is_released_at_once`: coffee, paid; one event at construction.
18. `test_a_message_for_another_consignment_is_refused`: `ClearanceError` matching `CN-2`; nothing released.
19. `test_release_records_a_cleared_handling_event_at_the_port`: `HandlingEvent(CN-1, CLEARED, "NLRTM")`.

`test_static.py`:
20. `test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage`: imports `src`; `{"arg-type"}`, `Argument "final" to "clear"`.
21. `test_mypy_cannot_see_release_placed_inside_the_chain`: imports `src`; exit 0, empty.
22. `test_mypy_refuses_a_stage_with_the_wrong_return_type`: imports `src`; `{"arg-type"}`.
23. `test_mypy_reports_a_stage_that_falls_off_the_end`: imports `src` (snippet defines a stage); `{"return"}`, `Missing return statement`.
24. `test_mypy_reports_a_decision_left_unhandled`: imports `src`; `{"arg-type"}`, `expected "Never"`.
25. `test_mypy_refuses_a_linked_chain_result_where_a_decision_is_needed`: reduced model (evidence I); `{"arg-type"}`.
26. `test_mypy_refuses_a_message_the_mediator_does_not_know`: imports `src`; a `HandlingEvent` passed to `receive`; `{"arg-type"}`.
27. `test_mypy_cannot_exhaust_a_match_on_true_and_false_patterns`: reduced model (evidence K); `{"arg-type"}`, `expected "Never"`.

Numbers are spec ids, not file order. The plan has 27 test functions and 42 cases:
- `test_chain.py`: 11 functions, 24 cases;
- `test_mediator.py`: 8 functions, 10 cases;
- `test_static.py`: 8 functions, 8 cases.

The executor counts from the pytest summary line and reports that number.

Also `README.md` and the card `_examples/23-mediator-and-chain-of-responsibility.md` (`order: 23`, eyebrow "Coordination · Mediator and Chain of Responsibility", a concept title with no count). None of the following appears in `src/`: `mock`, `monkeypatch`, `print(`, `Optional`, `abc`/`ABC`, `Any`, `cast`, `threading`, `asyncio`, `successor`.

Deletion table (M1a):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| first decision returns | every stage evaluated, then first non-`None` | 7 (experiment a) | later stages recorded |
| first decision returns | loop keeps the last non-`None` | 4[stages] | `"duty unpaid"` instead of the invoice reason |
| `final` used | `return Released()` | 10[hold] | the holding final stage is ignored |
| invoice check | removed | 2[commercial-invoice-stages] | released |
| dangerous goods declaration check | removed | 2[dangerous-goods-stages] | `"inspection required"`, not the document reason |
| duty check | removed | 3[stages], 4[stages] (executor names which) | not held for duty |
| inspection check | removed | 1[stages] | released |
| `inspect_goods` in `CLEARANCE_STAGES` | dropped from the tuple | 1[stages] | released |
| `describe` arm | `Held` arm removed | 11[held], member mypy | `assert_never` `[arg-type]` |
| duty outstanding | not added in `__init__` | 13[settlement-first] (executor check: or inspection-first) | released after the inspection alone |
| inspection outstanding | not added | 13[inspection-first] | released after the settlement alone |
| failed inspection holds | `_held` ignored | 16 | released after a settlement |
| release once | `not self._released` dropped | 15 (experiment b) | two `CLEARED` events |
| release at construction | `_try_release` not called in `__init__` | 17 | empty history |
| another consignment refused | check removed | 18 | `DID NOT RAISE` |
| `case Inspection()` arm | removed | 16, member mypy | `assert_never` `[arg-type]`; a failed inspection isn't handled |
| port on the event | the event uses `""` | 19 | wrong `HandlingEvent` |

### `examples/24-iterator-generators-and-the-iterator-protocol` (project `iterator-protocol`, package `iterator_protocol`)

- `domain.py`:
  - `ConsignmentId`, `HandlingKind(Enum)` (the five kinds, in lifecycle order), `HandlingEvent(consignment_id, kind, port)`, frozen slotted.
  - `TrackingHistory`, a plain class with `record(event, /)` and `__iter__(self) -> Iterator[HandlingEvent]: yield from self._events`. Its docstring says each loop gets a fresh iterator.
- `paging.py`:
  - `pages(history: Iterable[HandlingEvent], size: int) -> Iterator[tuple[HandlingEvent, ...]]`: `yield from batched(history, size, strict=False)`.
  - `page(history, number: int, size: int) -> tuple[HandlingEvent, ...]`: raises `ValueError("page numbers start at 1")` below 1, then `next(islice(pages(history, size), number - 1, None), ())`.
  - `out_of_order(events: Iterable[HandlingEvent]) -> Iterator[tuple[HandlingEvent, HandlingEvent]]`: `pairwise`, yielding pairs whose second kind comes earlier in `HandlingKind` declaration order.
  - `events_of(histories: Iterable[Iterable[HandlingEvent]]) -> Iterator[HandlingEvent]`: `chain.from_iterable`.
- `reading.py`:
  - `type Opener = Callable[[Path], TextIO]`; `open_utf8(path)`; `TrackingLogError(ValueError)`.
  - `events_from(lines: Iterable[str]) -> Generator[HandlingEvent, None, int]`: parses `id;KIND;PORT` and returns the count. A wrong field count or unknown kind raises `TrackingLogError(f"line {n}: ...")` from None.
  - `read_events(path, *, opener: Opener = open_utf8) -> Generator[HandlingEvent, None, int]`: `with opener(path) as lines: return (yield from events_from(lines))`.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `history` (three events: booked, loaded and departed at NLRTM, SGSIN and DEHAM).
- `history_form` params `iterable|self-iterator`, giving a filled `TrackingHistory` or `_OneShotHistory` (an index and `__iter__` returning `Self`).
- `counting` (a factory for a generator of N copies of one event that records how many it produced).
- `tracking_log` (writes a three-line file under `tmp_path`).
- `recording_opener` (opens with `open_utf8` and appends the handle to a list the test reads).

`test_protocol.py`:
1. `test_a_traversal_visits_every_event_in_order` x `history_form` (2).
2. `test_an_empty_history_yields_nothing` x `history_form` (2).
3. `test_a_tracking_history_can_be_walked_twice`.
4. `test_a_self_iterating_history_is_empty_on_the_second_pass`.
5. `test_nested_walks_of_a_tracking_history_are_independent`: 9 pairs from 3 events.
6. `test_a_self_iterating_history_cuts_a_nested_walk_short`: fewer than 9 pairs (the executor records the exact number).
7. `test_an_exhausted_generator_looks_empty`: `list` then `[]`; `sum` 0.
8. `test_iter_of_an_iterator_is_the_iterator_itself`: also `iter(history) is not iter(history)`.
9. `test_a_class_with_only_next_is_not_iterable`: `TypeError` matching `is not iterable`.
10. `test_stop_iteration_inside_a_generator_becomes_runtime_error`: a test-local generator; `RuntimeError` matching `generator raised StopIteration`; `__cause__` is a `StopIteration`.

`test_laziness.py`:
11. `test_the_first_page_reads_only_one_page`: 3 of 1,000,000 pulled.
12. `test_an_eager_list_reads_every_event_to_get_the_first_page`: 1,000,000 pulled (the domain row 24 failing test).
13. `test_pages_keep_a_short_last_page`: sizes 3, 3, 1.
14. `test_a_page_size_below_one_is_refused`: `ValueError` matching `n must be at least one`.
15. `test_page_reads_only_up_to_the_page_it_returns`: page 2 of size 3 pulls 6.
16. `test_page_numbers_start_at_one[zero|negative]` (2).
17. `test_a_page_past_the_end_is_empty`.
18. `test_out_of_order_finds_an_event_that_steps_back_in_the_lifecycle`: loaded then booked.
19. `test_out_of_order_is_empty_for_fewer_than_two_events[none|one]` (2).
20. `test_events_of_starts_each_history_only_when_the_last_is_done`: two counting sources; after the first history's events, the second has produced 0.

`test_reading.py`:
21. `test_read_events_parses_each_line`.
22. `test_yield_from_hands_the_line_count_to_the_caller`: a test-local delegating generator receives 3.
23. `test_list_drops_a_generators_return_value`.
24. `test_a_malformed_line_is_refused_with_its_number[too-few-fields|unknown-kind]` (2): matching `line 2`.
25. `test_a_reader_never_started_opens_no_file`: the recorded handle list is empty after the call.
26. `test_closing_a_reader_closes_its_file`: after one `next` and `close()`, the handle is closed and the state is `GEN_CLOSED`.
27. `test_breaking_out_of_a_loop_leaves_a_named_reader_open`: `break`; the handle isn't closed; the test closes the reader at the end.
28. `test_contextlib_closing_closes_the_reader_at_the_end_of_the_block`: open inside the block after `break`, closed after it.
29. `test_an_abandoned_reader_closes_its_file_when_collected`: `del` and `gc.collect()`, with a comment saying why.

`test_static.py`:
30. `test_mypy_refuses_close_on_an_iterator`: imports `src`; `{"attr-defined"}`, `has no attribute "close"`.
31. `test_mypy_refuses_contextlib_closing_on_an_iterator`: imports `src`; `{"type-var"}`.
32. `test_mypy_accepts_contextlib_closing_on_a_reader`: imports `src`; exit 0, empty.
33. `test_mypy_cannot_see_a_second_pass_over_an_iterator`: reduced model (evidence D); exit 0, empty.
34. `test_mypy_refuses_a_generator_where_a_collection_is_needed`: reduced model (evidence E); `{"arg-type"}`.
35. `test_mypy_types_the_value_of_yield_from`: imports `src` (`events_from`); `{"assignment"}`.
36. `test_mypy_refuses_a_class_with_only_next_in_a_for_loop`: reduced model; `{"attr-defined"}`, `(not iterable)`.
37. `test_mypy_accepts_a_self_iterating_history_as_an_iterable`: reduced model (evidence F); exit 0, empty.

The plan has 37 test functions and 42 cases:
- `test_protocol.py`: 10 functions, 12 cases;
- `test_laziness.py`: 10 functions, 12 cases;
- `test_reading.py`: 9 functions, 10 cases;
- `test_static.py`: 8 functions, 8 cases.

The executor counts from the pytest summary line.

Also `README.md` and the card `_examples/24-iterator-generators-and-the-iterator-protocol.md` (`order: 24`, eyebrow "Traversal · Iterator", a concept title). None of the following appears in `src/`: `mock`, `monkeypatch`, `print(`, `Optional`, `Any`, `cast`, `async`, `await`, `threading`, `tee`.

Deletion table (M1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| fresh iterator per loop | one iterator stored in `__init__` | 3, 5 (experiment a) | second pass empty; nested walk short |
| lazy paging | `batched(list(history), size)` | 11 | 1,000,000 pulled |
| page number check | removed | 16[all] | `islice`'s message, not `page numbers start at 1` |
| lazy `page` | `list(pages(...))[number - 1]` | 15 (and 17: `IndexError`) | everything pulled |
| `next(..., ())` default | no default | 17 | `StopIteration` escapes (executor names the exact failure) |
| lifecycle comparison | `>` and `<` swapped | 18 | wrong pair |
| lazy `events_of` | `chain(*[list(h) for h in histories])` | 20 | second source started early |
| return count | `return None` | 22, member mypy (`[return-value]`) | `None` instead of 3 |
| malformed line | check removed | 24[all] | `IndexError` or `KeyError`, not `TrackingLogError` |
| line number in the error | dropped | 24[all] | no `line 2` |
| `with` around the opener | `lines = opener(path)` | 26, 28, 29 (experiment b) | handle not closed; possible unraisable `ResourceWarning` |
| lazy open | a plain function opens, then returns a generator | 25 | a handle recorded at call time |
| `Generator` annotation | `Iterator[HandlingEvent]` | member mypy, 32 | `[return-value]` on `return`; `closing` refused |

## Steps and status

Step ids are `M*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| M0 | This plan file. PDP-123a-c and 124a-c `active` in `iteration-plan.md` (dated note); r11 marked active and r10b closed. Reconciliation rows 120-133 `open` with a dated r11 note. Domain rows 23-24 updated with the supporting names and decisions 1-8; the ch24/ch38 non-overlap rule reworded (decision 5) with a dated note. ch23-24 stub `description` lines written. r10's K7, r10b's L8 and PDP-121a to 122c closed. Decisions recorded | - | done |
| M1a | ch23 member, card, README; one `uv lock`; three green runs plus one reverse-file-order run; the deletion table, each row in a fresh scratch copy with its `.venv` removed and re-synced (confirm `__file__`) | M0 | done |
| M1b | ch24 member, card, README; one `uv lock` after M1a (sequenced for `uv.lock`); three green runs plus one reverse-order run; deletion table | M1a | done |
| M2 | Witness results into rows 120-133 (the claims audit resolves). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | M1b | done |
| M3 | Two figures, specs `diagrams/specs/23-*.py` and `24-*.py`, `_data/diagrams.yml` (single owner; 25 entries); figures 00-22 unchanged; every name drawn exists in `src` or the standard library | M2 | todo |
| M4 | ch23-24 `status = "drafted"` (`kind` stays `pattern`) | M3 | todo |
| M5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly (stopping where the page's sentence stops), runs its two experiments in fresh scratch copies with the filter it states in the chapter, quotes that filter's complete output passed through `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table (claim, then test, run or source URL) | M3, M4 | todo |
| M6 | Opus validation; up to two repair rounds. Includes a seam scan after every cut (lost antecedents, a dangling "either" or "it") and a check that close bullets map one to one to objectives | M5 | todo |
| M7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r11.x` on main; notes-only release | M6 | todo |

Reconciliation rows (step M0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 120 | 23 | A chain is a tuple of stages: every form holds a restricted commodity, a missing document and unpaid duty; the first decision wins; later stages aren't called; the final stage releases a clean declaration | `test_a_restricted_commodity_is_held_for_inspection`, `test_a_declaration_missing_a_document_is_held`, `test_an_unpaid_declaration_is_held_for_duty`, `test_the_first_stage_that_decides_wins`, `test_stages_after_a_decision_are_not_called`, `test_a_clean_declaration_is_released` |
| 121 | 23 | A linked chain with no terminal returns `None`; mypy refuses that result where a decision is needed, a passing stage as the final stage, a stage with the wrong return type and a stage that falls off the end | `test_a_linked_chain_with_no_terminal_returns_none`, `test_mypy_refuses_a_linked_chain_result_where_a_decision_is_needed`, `test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage`, `test_mypy_refuses_a_stage_with_the_wrong_return_type`, `test_mypy_reports_a_stage_that_falls_off_the_end` |
| 122 | 23 | A stage added after release clears a restricted commodity and mypy can't see it; a stage added to the chain runs before the final stage; an empty chain leaves the decision to the final stage; a decision left unhandled is a mypy error | `test_a_stage_added_after_release_clears_a_restricted_commodity`, `test_mypy_cannot_see_release_placed_inside_the_chain`, `test_a_stage_added_to_the_chain_runs_before_the_final_stage`, `test_an_empty_chain_leaves_the_decision_to_the_final_stage`, `test_describe_names_every_decision`, `test_mypy_reports_a_decision_left_unhandled` |
| 123 | 23 | The mediator releases once, after duty and inspection, in either order; a failed inspection holds; nothing outstanding releases at once; another consignment's message is refused; release records `CLEARED` at the port | `test_release_follows_inspection_then_settlement`, `test_the_mediator_releases_in_either_order`, `test_a_duplicate_settlement_releases_once`, `test_a_failed_inspection_holds_the_consignment`, `test_a_declaration_with_nothing_outstanding_is_released_at_once`, `test_a_message_for_another_consignment_is_refused`, `test_release_records_a_cleared_handling_event_at_the_port` |
| 124 | 23 | Colleagues that call each other lose a settlement that arrives before inspection | `test_a_choreography_loses_a_settlement_that_arrives_before_inspection`, `test_release_follows_inspection_then_settlement` |
| 125 | 23 | mypy refuses a message the mediator doesn't know, and can't exhaust a class through `True` and `False` field patterns | `test_mypy_refuses_a_message_the_mediator_does_not_know`, `test_mypy_cannot_exhaust_a_match_on_true_and_false_patterns` |
| 126 | 24 | The protocol: both forms visit every event in order; `iter` of an iterator is itself; a `__next__`-only class isn't iterable at run time or for mypy | `test_a_traversal_visits_every_event_in_order`, `test_an_empty_history_yields_nothing`, `test_iter_of_an_iterator_is_the_iterator_itself`, `test_a_class_with_only_next_is_not_iterable`, `test_mypy_refuses_a_class_with_only_next_in_a_for_loop`, `source: https://python-patterns.guide/gang-of-four/iterator/`, `source: https://peps.python.org/pep-0255/` |
| 127 | 24 | One pass or many: the history walks twice and nests; a self-iterating cursor is empty on the second pass and cuts a nested walk short; an exhausted generator looks empty; mypy can't see a second pass and accepts the cursor, but refuses a generator where a collection is needed | `test_a_tracking_history_can_be_walked_twice`, `test_nested_walks_of_a_tracking_history_are_independent`, `test_a_self_iterating_history_is_empty_on_the_second_pass`, `test_a_self_iterating_history_cuts_a_nested_walk_short`, `test_an_exhausted_generator_looks_empty`, `test_mypy_cannot_see_a_second_pass_over_an_iterator`, `test_mypy_accepts_a_self_iterating_history_as_an_iterable`, `test_mypy_refuses_a_generator_where_a_collection_is_needed`, `source: https://docs.python.org/3/glossary.html` |
| 128 | 24 | The first page reads one page against 1,000,000 events for an eager list; a short last page is kept; a size below one is refused; `page` reads only up to its page, numbers from 1 and is empty past the end | `test_the_first_page_reads_only_one_page`, `test_an_eager_list_reads_every_event_to_get_the_first_page`, `test_pages_keep_a_short_last_page`, `test_a_page_size_below_one_is_refused`, `test_page_reads_only_up_to_the_page_it_returns`, `test_page_numbers_start_at_one`, `test_a_page_past_the_end_is_empty`, `source: https://docs.python.org/3/library/itertools.html` |
| 129 | 24 | `pairwise` finds an event that steps back in the lifecycle and is empty below two events; `chain.from_iterable` starts each history only when the last is done | `test_out_of_order_finds_an_event_that_steps_back_in_the_lifecycle`, `test_out_of_order_is_empty_for_fewer_than_two_events`, `test_events_of_starts_each_history_only_when_the_last_is_done` |
| 130 | 24 | `yield from` hands the subgenerator's return value to the caller, `list()` drops it and mypy types it; a malformed line is refused with its number | `test_read_events_parses_each_line`, `test_yield_from_hands_the_line_count_to_the_caller`, `test_list_drops_a_generators_return_value`, `test_mypy_types_the_value_of_yield_from`, `test_a_malformed_line_is_refused_with_its_number`, `source: https://peps.python.org/pep-0380/` |
| 131 | 24 | A reader never started opens no file; `close()` closes it; `break` leaves a named reader open; `contextlib.closing` closes it at the end of the block; an abandoned reader closes when collected; mypy refuses `close` and `closing` on an `Iterator` and accepts them on a `Generator` | `test_a_reader_never_started_opens_no_file`, `test_closing_a_reader_closes_its_file`, `test_breaking_out_of_a_loop_leaves_a_named_reader_open`, `test_contextlib_closing_closes_the_reader_at_the_end_of_the_block`, `test_an_abandoned_reader_closes_its_file_when_collected`, `test_mypy_refuses_close_on_an_iterator`, `test_mypy_refuses_contextlib_closing_on_an_iterator`, `test_mypy_accepts_contextlib_closing_on_a_reader`, `source: https://docs.python.org/3/builtins/stdtypes.html`, `source: https://docs.python.org/3/reference/expressions.html` |
| 132 | 24 | A `StopIteration` raised inside a generator becomes `RuntimeError` | `test_stop_iteration_inside_a_generator_becomes_runtime_error`, `source: https://peps.python.org/pep-0479/` |
| 133 | 23-24 | The "Build, run, observe" experiments behave as quoted | `run: M5` |

## Corrections after the build
- Step M1b: member `iterator-protocol`, 37 test functions, 42 cases, as planned; every predicted mypy message matched (evidence D-F). Test 6's cut-short nested walk gives 2 pairs. mypy 2.4.1 narrows `handle.closed` after `assert not handle.closed` and flags later lines `[unreachable]`, so the reading tests read it through a `_closed` helper; `next(iter(()))` is `Never`, so test 10 uses an empty `list[int]`. Experiment (a) also fails test 8. Experiment (b) (drop the `with`) fails tests 26-29 as predicted, plus three tests on the default opener through `PytestUnraisableExceptionWarning` (unclosed file, under `filterwarnings = ["error"]`): 8 failed, 34 passed, mypy 0. The eager-pages row also fails test 15. Evidence A (unnamed-generator `break` timing) is not asserted.
- Step M1a: member `mediator-chain`, 27 test functions, 42 cases, as planned; every predicted mypy message matched. A failed `Inspection` now also discards "inspection" from the outstanding set and sets `_failed`, so the `_failed` check has its own witness (`test_a_failed_inspection_holds_the_consignment`); behaviour at the interface is unchanged. `is not None` -> truthiness in `clear` is an equivalent mutant (decisions are always truthy); the chapter keeps `is not None` because it names "pass it on", and the pass-on deletion row is the real witness. Test 14 runs on a `choreography` fixture alone; test 21 uses `(release, inspect_goods)`. Test 13 asserts through a `_kinds` helper because mypy 2.4.1 narrows `history.events` to `tuple[()]` after an `== ()` assert and then rejects the next comparison. Experiment (b) (drop the released check) fails only `test_a_duplicate_settlement_releases_once`.

(None yet. The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.)

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs, and passes one run with the test files listed in reverse order (`tests/test_static.py` first), with the same pass count.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch"` over both members prints nothing.
   - `grep -rn "print("` over both members prints nothing.
   - `grep -rnE "^\s*(from abc|import abc)|\bABC\b|\bAny\b|cast\(|threading|asyncio|successor"` over `examples/23-*/src` prints nothing.
   - `grep -rnE "\bAny\b|cast\(|\basync\b|\bawait\b|aclosing|threading|\btee\b"` over `examples/24-*/src` prints nothing.
3. Every test name cited in rows 120-132 is defined exactly once across `examples/*/tests` (`grep -rhoE "def test_\w+" examples/*/tests | sort | uniq -d` lists none of them).
4. Every mypy-API test asserts its exit status and an exact code set, uses the anchored `_codes` regex, and asserts no line number or optional note. `grep -c "_codes("` is at least 5 in each `test_static.py`. Every `# type: ignore[...]` names a code.
5. Deletion tables (M1a, M1b): every row, deleted in a fresh scratch copy whose imports come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed"; executor-check rows are resolved or moved to Corrections with the orchestrator's agreement.
6. Every "not called", "not read", "skipped" or "opens no file" sentence in either chapter names a test that has a deletion-table row whose mutation makes it fail.
7. ch23-24 are drafted, with one figure each, captions of 20-45 words including `Figure N.1:`, and at most 2,500 prose words each by `validate.py` (an error above; a warning below 1,900 is reported, not padded).
8. Spine and sidebar:
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `grep -c "^## When not to use it"` is 1 in each and `grep -c "^## How it works"` is 0.
   - `## What you can do now` is the second-to-last H2, directly before `## For deeper coverage`, with as many bullets as the learning objectives.
   - Every backticked token in the close appears earlier in the chapter.
   - Each sidebar opens with a bold lead, holds a nested `>` prompt, has at most two non-quoted paragraphs, matches no `\bCheck(:| that| three| four| whether)`, is at most 120 words, and names only identifiers present in the chapter or its `src`.
   - `validate.py` passes the `pattern` spine.
9. Thesis: ch23 says both patterns survive (`surviv` at least 2) and names what Python removes (the handler class and its successor link; the Mediator and Colleague classes). ch24 says Iterator dissolves (`dissolv` at least 1) and names the three decisions that remain.
10. Non-overlap and pointers:
    - ch23 points to "The three-way split: dissolve, survive, disambiguate", "Protocol, duck typing, and structural typing with mypy" and "Observer" by title.
    - ch24 points to "What 1994 assumed, and what Python dissolves", "The data model: dunder methods as the substrate" and "asyncio and the patterns" by title. The asyncio pointer is one sentence and names no content (`grep -nE "aclosing|async for|AsyncGenerator"` over `_docs/24-*.md` prints nothing).
    - Neither chapter describes the content of any stub (shortcut patterns, singledispatch, Visitor/Memento/Interpreter, the GIL, asyncio beyond the title, the final project). ch23 builds no dict dispatch table and no string bus.
    - Neither re-teaches the evidence method, which is pointed to "Proving it works: pytest, pytest-mock, and mypy".
11. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, the cards, the specs and the SVGs, with `--stats` reviewed against the house-voice rubric.
    - Contractions: uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and exact quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz)"` over prose (quotations and code excluded) prints nothing. The expressions page's "finalized" is quoted verbatim, and everywhere else the prose writes "finalised".
    - Intent before mechanism in every body section. No paragraph after an excerpt re-narrates its identifiers. After every cut in M6, the next sentence is re-read for a lost antecedent.
12. There's no em-dash or en-dash in any file touched in r11, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. The quoted upstream titles (PEP 479 and the others) contain none, which the prose agents confirm when they re-fetch.
13. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Smalltalk|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/23-*.md`, `_docs/24-*.md`, the new READMEs and the cards prints nothing.
14. Idiomatic scan: 0 ban-tier in both members.
15. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`, never hand-edited. No quoted path names a system file.
16. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
17. Each experiment is performed in a fresh scratch copy (its `.venv` removed and re-synced, `__file__` confirmed) and changes one thing. The chapter states the exact filter command, and the quoted block is that command's complete output, followed by `uv run mypy --strict src tests`. The handback includes the raw output and where it differs from the prediction.
18. Attribution (credit every source a chapter leans on, by author and work, where the idea is used; nothing copied; a missing credit is blocking):
    - ch23 credits GoF (Chain of Responsibility, Mediator) in plain paraphrase and claims no Rhodes page.
    - ch24 credits GoF (Iterator) in plain paraphrase, Rhodes's "The Iterator Pattern" in paraphrase, and PEPs 255, 380 and 479 by author. It quotes the glossary, `generator.close()`, the yield-expressions sentence, `contextlib.closing` and the `itertools` sentences exactly, each stopping where the page's sentence stops.
    - GoF claims appear only if verified, with the bracketed fallbacks applied, and no GoF sentence tracks the Intent wording. Each prose agent lists the sources it checked. Every book cited is already in `bibliography.html`; anything else is flagged to the owner, not added.
19. Claims:
    - Every factual sentence in ch23-24 maps to a named test, a recorded run (`run: M5`) or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0. The claims table lists rows 1-133, with 120-133 resolved, and each `source:` URL appears in its chapter.
    - No `run: K*` or `L*` token appears in rows 120-133.
20. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 25 entries, and `diagrams/0*-*`, `diagrams/1*-*`, `diagrams/20-*`, `diagrams/21-*` and `diagrams/22-*` are unchanged.
21. Reconciliation rows 120-133 are `verified` or `adjusted` with evidence.
22. Deterministic:
    - No test depends on wall time, the environment, memory addresses, byte counts, test order or iteration order it didn't create.
    - No test asserts finalisation before `gc.collect()` except through a name that holds the generator.
    - Every reader test closes what it opens, so `filterwarnings = ["error"]` sees no `ResourceWarning` in a green run. `filterwarnings = ["error"]` is still in the root config.
23. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.
24. Every self-contained mypy snippet that stands for code is named in the prose as a reduced model: ch23 tests 25 and 27; ch24 tests 33, 34, 36 and 37. Snippets that import `src` need nothing more.
25. Test counts in prose and handbacks come from the pytest summary line of a fresh run, never from this plan's arithmetic.
26. Every comparison form said to share a table is a conftest fixture param (`chain_form`, `coordination_form`, `history_form`), and each chapter shows at most one comparison excerpt.
27. Every figure label that names code (`CustomsDeclaration`, `clear`, `check_documents`, `assess_duty`, `inspect_goods`, `release`, `ClearanceMediator`, `Settlement`, `Inspection`, `TrackingHistory.record`, `TrackingHistory`, `pages`, `page`, `read_events`, `close()`) exists in that chapter's `src` or the standard library, checked by grep at M3.
28. Repo-relative paths only in this plan and every r11 file: `grep -rnE "/home/|/Users/"` over the files touched in r11 prints nothing.

## Risks

- **Predicted messages and counts.** Every iteration since r05 mispredicted something. Expect differences in these places:
  - test 6's exact pair count (ch24);
  - which tests each experiment fails, especially ch24 (b), where an unraisable `ResourceWarning` can surface as an error on a different test or in teardown (evidence G);
  - the mypy wording when the aliases print expanded, for example `Callable[[CustomsDeclaration], Released | Held | None]`. Tests match codes and stable substrings only, and differences go in Corrections.
- **mypy and `bool` literal patterns** (evidence K). `case Inspection(passed=False)` would fail the member's own mypy run. The member writes `case Inspection()`, and a future mypy that narrows literals flips test 27, which is fine: the test says what mypy 2.4.1 does.
- **Generator finalisation in tests.** Pytest's assertion rewriting or a traceback frame can keep a generator alive. Tests that rely on a name holding a generator assert only "still open". The abandoned-reader test deletes every name and collects. If it fails, the executor checks `gc.get_referrers` in the scratch copy before anything in `src` changes.
- **Unclosed files under `filterwarnings = ["error"]`.** A test that forgets to close a reader fails the run through an unraisable `ResourceWarning`. Every test that breaks early closes the reader before returning (test 27 closes it explicitly at the end).
- **1,000,000 pulls.** The counting generator yields one shared event object, so test 12 is fast and allocates little. No time or memory is asserted.
- **CPython details stated as such.** The immediate close after `break` over an unnamed generator, and the CPython note that iterators don't always define `__iter__` (glossary, not used), are observations or omitted. Nothing version-sensitive is asserted.
- **Docs URLs moved** (`builtins/functions.html`, `builtins/stdtypes.html`). Chapters cite the current URLs, and the claims audit needs the exact URL string in the chapter.
- **Word budgets.** ch23 carries two patterns, three comparison forms and eight static witnesses. If it overruns, the "a mediator decides, a signal broadcasts" section shrinks to two sentences first, then the `match`-form paragraph. Their tests stay. ch24 carries four topics; if it overruns, the `pairwise`/`chain` paragraph shrinks first.
- **Stub pointers.** It's tempting to write "the asyncio chapter shows `aclosing`" or "dict dispatch replaces the chain". Criterion 10 forbids both.
- **New supporting names** (decisions 3 and 7). If the owner declines `ClearanceMediator`, `Inspection` or the reuse of `Settlement`, M1a waits for the replacement names. Nothing else moves.
- **ruff.** E731 (a lambda assigned in the conftest) is avoided with defs. N818 holds (`ClearanceError`, `TrackingLogError`). `inspect_goods`, not `inspect`, avoids shadowing the standard-library module. `Self` is used for `_OneShotHistory.__iter__` (UP037 forbids a quoted annotation).
- **Liquid.** The f-strings in excerpts (`f"line {n}: ..."`, the `ClearanceError` message) contain single braces only. Any `{{` needs `{% raw %}`, and validate.py checks.
- **`uv.lock` race.** M1a and M1b are sequenced, and project names normalise to the package names.

### Critical Files for Implementation
- _plans/r10-plan.md
- _plans/shipping-domain-model.md
- _plans/reconciliation-plan.md
- scripts/validate.py
- _docs/22-observer.md (with examples/22-observer/tests/test_static.py for the mypy helper)
