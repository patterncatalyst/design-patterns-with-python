---
title: "r12 plan: chapters 25-26 (Visitor, Memento, and Interpreter; Decorators done right)"
order: 12
output: false
render_with_liquid: false
---

# r12: chapters 25-26, Visitor, Memento, and Interpreter; Decorators done right

Opus-planned 2026-11-05. Branch `release/r12`, cut from main at dd668d6 (the r11 merge, tagged r11.x). This file is the source of truth for r12 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged (r11 evidence M, surveyed 2026-11-05; N0 re-checks PyPI and python.org before any edit). `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch25: slug `25-visitor-memento-interpreter`, title "Visitor, Memento, and Interpreter", part 8 (`coordinating-traversing`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.
- ch26: slug `26-decorators-done-right`, title "Decorators done right", part 9 (`idiomatic-python`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.

## User decisions (awaiting the owner)

Standing, not a decision: step ids are `N*`. `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md`, and `grep -nE "^\| N[0-9]" _plans/*.md` matched nothing before this file.

1. **Buckets follow the canonical map.** The r02 map lists "Visitor: `singledispatch` for an open set, `match` + `assert_never` for a closed set" under Dissolves and "Memento; Interpreter" under Survives. The ch3 table rows say the same. Domain row 26 gives ch26 the survives bucket.
   - **Visitor dissolves.** The `accept` method on every element class and the visitor class per operation both go. A closed union of frozen events with one `match` per operation, ending in `assert_never`, replaces them. What stays is a choice the language doesn't make for you: closed set (`match`, exhaustive for mypy) or open set (`singledispatch`, extensible, silent on a missing kind) (evidence A to C).
   - **Memento survives.** The Originator, Memento and Caretaker classes shrink to a frozen snapshot dataclass and a context manager. Two decisions remain: what to capture, and what must not roll back. Here the audit trail must not roll back, and a snapshot must share nothing mutable (evidence E, F).
   - **Interpreter survives.** A class per grammar rule stays, as frozen node dataclasses under one `type` alias. The grammar and its interpretations remain design: `evaluate` and `explain` are two readings of one tree, which a closure can't give (evidence D).
   - **Decorators done right survives.** The `@` syntax is given. The discipline is not: what `functools.wraps` copies and what it gets wrong, what `ParamSpec` keeps for mypy, a factory that can't be used bare, stacking order on a cache, class decorators against `@dataclass(slots=True)`, and decorated methods (evidence G to M).

   **Recommend: yes.** Alternative: Visitor "survives" because `match` is still an operation per kind. That's the mechanism, not the pattern. The `accept` double dispatch is what the GoF form exists for, and it's gone. It would also contradict the r02 map and the ch3 row.

2. **How much singledispatch ch25 shows: one fixture form, no excerpt, two witnesses, one pointer.**
   - `src` uses `match` with `assert_never`, because the five handling events are a closed union.
   - The `singledispatch` form is a conftest fixture param on the shared journey table (decision 3).
   - Two witnesses:
     - an event with no registration silently gets the fallback's answer (domain row 25's failing test);
     - mypy exits 0 on a singledispatch visitor that misses an event (evidence A).
   - One test-local witness shows that dispatch is on the first argument only, and the chapter quotes the functools sentence.
   - The prose points to "singledispatch: the Visitor the language gives you" by exact title, in one sentence, and to "The three-way split: dissolve, survive, disambiguate", which already shows the registered `describe`.
   - Registration mechanics, union annotations, forward references, `register(cls, fn)`, the mypy `[misc]`/`[arg-type]` caveats, the fallback-signature checking (evidence A) and global registration state all stay in ch28. The ch25 prose names none of them.

   **Recommend: yes.** Alternatives:
   - (b) A singledispatch `describe` in `src` as the open-set answer. That repeats the ch3 member and draws the chapter toward ch28's ground.
   - (c) No singledispatch at all. Reconciliation row 7 and the domain row's failing test both need it.

3. **The Visitor comparison is `visitor_form` `match|singledispatch|accept` on one journey table; no `load_plan`.**
   - Each form describes the same five-event journey of `CN-1` (booked, loaded and departed at `NLRTM`; cleared and delivered at `SGSIN`) with the same five strings.
   - The `accept` form uses conftest twins: frozen slotted subclasses of the `src` events, each adding `accept`, plus an `EventVisitor[T]` Protocol and a `_Describer` visitor (evidence C).
   - The one ch25 comparison excerpt is `_AcceptingBooked.accept` with `EventVisitor`. The singledispatch form, the shallow memento and the closure tariff are described in prose only.
   - Reconciliation row 7 says "over `Document` kinds". Domain row 25 and the ch25/ch28 rule say `HandlingEvent` or `Commodity` kinds, so row 7 becomes **adjusted**: three dispatchers, one table, `HandlingEvent` kinds.
   - Domain row 25 mentions `load_plan(cargo, vessel)` for double dispatch. That needs cargo and vessel kinds the domain doesn't name, so it's replaced by one test-local witness (`singledispatch` picks by the first argument) and one sentence: a `match` on a tuple dispatches on two values. No `Vessel` kinds are introduced. N0 rewords domain row 25 to match.

   **Recommend: yes.** Alternative: dispatch on `Commodity` kinds instead. That collides with ch28's `Commodity` tariff-code lookup.

4. **The Memento storage form is a frozen `BookingSnapshot(request, documents: frozenset[DocumentKind])` with a `rollback(booking)` context manager as caretaker.**
   - `Booking` is an entity (`@dataclass(slots=True, eq=False)`) with:
     - a frozen `BookingRequest`;
     - a working `documents: set[DocumentKind]`;
     - an append-only `audit: list[str]`.
   - The snapshot captures the request and a `frozenset` of documents and leaves the audit out, because a record of a refused amendment must survive the rollback.
   - `rollback` snapshots, yields, and on an exception restores, appends `"rolled back"` and re-raises.
   - Amendments use `copy.replace` on the frozen request (since 3.13; ch17 owns it, so it's used and not taught).
   - Comparison fixture `memento_form` `snapshot|shallow|deepcopy`, run on one restore table:
     - `shallow` (`copy.copy`) shares the document set, so a document attached inside the block survives the rollback. This is domain row 25's "a mutated memento corrupts rollback".
     - `deepcopy` restores the audit too, erasing the refused attempt, and copies the frozen request it could share. The copy docs say deep copy "may copy too much".
     - Both get their own tests.
   - ch15 already says a frozen request is a safe snapshot. ch25 points to "Command, undo, and command queues" once and takes the case it handed over: state spread over fields, some mutable, where no inverse exists.

   **Recommend: yes.** Alternatives:
   - (b) A stack of snapshots for multi-level undo. Undo stacks are ch15's ground.
   - (c) Pickle or `vars()` dictionaries as mementos. They're untyped and mypy can't check them.
   - (d) An `Invoice` of `LineItem`s (the Billing area also lists Memento). Domain row 25 names booking rollback, and ch26 may need `LineItem`.

5. **Interpreter evaluates trees only and parses no text.**
   - The grammar: `type Expr = PerKg | Flat | Add | Max | OverWeight`, frozen slotted node dataclasses. With deferred annotations (since 3.14), the recursive fields name `Expr` without quotes (evidence D).
   - Two interpretations, each one `match` ending in `assert_never`:
     - `evaluate(expr, consignment) -> Money`;
     - `explain(expr) -> str`.
   - `STANDARD_TARIFF` is the one tree: over 1,000 kg, 1.10 EUR per kg plus 25.00 EUR; otherwise the larger of 1.20 EUR per kg and 45.00 EUR. The rates are illustrative.
   - The comparison is `rule_form` `tree|closure`. Closure combinators return `PricingRule` callables and price the same four consignments. Two closures built the same way aren't equal, and a closure can't be explained, so both facts get their own tests.
   - One sentence says that parsing a rule language is a separate problem and isn't built here. [GoF leaves parsing out of Interpreter, if verified.]

   **Recommend: yes.** Alternative: a one-line rule parser (`per_kg 1.20 max flat 45.00`). It adds about 40 lines, an error type and four tests, and roughly 250 words the chapter doesn't have.

6. **The ch25 split is about 40/30/30 (Visitor, Memento, Interpreter), in one member and one figure.**
   - Visitor gets about 900 words: it carries the dissolve thesis, three forms and three static witnesses.
   - Memento and Interpreter get about 650 each.
   - The three are joined by one through-line: `evaluate` is a visitor over a closed grammar, and the snapshot is the value a visitor never needs.

   **Recommend: yes.** Alternative: even thirds. Visitor carries the bucket argument and the open/closed choice.

7. **ch26 uses Documentation renderers, not `LineItem` formatting.**
   - `render_bill(bill: BillOfLading, /, *, width: int = 72) -> str` is the decorated function.
   - `DocumentKind` (`BILL_OF_LADING`, `MANIFEST`, `CUSTOMS_DECLARATION`) is registered by a class decorator, `document_kind(kind, *, registry=DOCUMENT_TYPES)`, on `BillOfLading` and `Manifest`.
   - Renderers and the registry share one area. Domain row 26 and the ch20/ch26 non-overlap rule allow both choices; this one never touches `RateCalculator` or `Invoice`.

   **Recommend: yes.** Alternative: `LineItem` formatting (`format_line(item)`). It's natural for the cache, but then the class decorator registering `DocumentKind` sits in a second area, and the final project (domain row 39) owns `Invoice`/`LineItem` wiring.

8. **Parametrised decorators take keyword-only arguments, so bare use fails at definition.**
   - The factory is `cached_for[**P, R](*, seconds: float, clock: Clock = time.monotonic)`.
   - The comparison is `_cached_for_positional(seconds)` in conftest. Used bare, it binds the name to its inner `decorate`, and a call returns a function instead of text, with no error (evidence J; domain row 26's failing test).
   - With the `*`, the same misuse is `TypeError: cached_for() takes 0 positional arguments but 1 was given` when the module loads. mypy refuses both forms.
   - The one ch26 comparison excerpt is the positional factory and its bare use. The `wraps`-less wrapper is described in prose.

   **Recommend: yes.** Alternatives:
   - (b) A dual-form decorator (`@cached_for` or `@cached_for(seconds=...)`) with `@overload`. That's twice the code and two typed paths, and it hides the misuse instead of refusing it.
   - (c) Positional `seconds`, relying on mypy. The runtime failure stays silent wherever mypy doesn't run.

9. **ch26's comparison form is `wrapper_form` `wraps|bare` on one rendering table.**
   - Both forms wrap `render_bill` with the same `ParamSpec` timer and render identical text for two bills.
   - The bare form then fails its own tests: its own `__name__`, no docstring, no `__wrapped__`, and `inspect.signature` gives `(*args: P.args, **kwargs: P.kwargs) -> R`.
   - mypy still keeps the bare form's signature (evidence H), which is the lesson: `wraps` serves runtime tools and `ParamSpec` serves mypy.
   - Reconciliation row 6 ("a `functools.wraps`-less wrapper loses `__name__` and signature") resolves here.

   **Recommend: yes.** Alternative: an untyped bare wrapper as the comparison. It mixes two losses into one table, and `[untyped-decorator]` gets its own static witness anyway.

10. **ch26 scope: Concatenate in, methods in (short), descriptors out.**
    - **Concatenate.** One section of about 250 words on a decorator that supplies an argument (`issued_at(clock, number)`). mypy types it right (`def (str) -> str`). `functools.wraps` makes `inspect.signature` report the original two parameters, and `bind` refuses a call that works (evidence I). `functools.partial` reports the remaining parameter and is checked by mypy. The rule: `wraps` assumes the wrapper takes the wrapped function's arguments.
    - **Methods.** About 200 words:
      - a function wrapper binds `self`, because functions are descriptors (quote the descriptor guide);
      - a class-based wrapper without `__get__` doesn't;
      - `functools.cache` on a method keeps the instance alive until the cache is cleared (quote the FAQ and ruff's B019).
    - `cached_property`, `__set_name__` and writing `__get__` stay in "Descriptors and properties", named by title once.

    **Recommend: yes.** Alternatives:
    - (b) Drop Concatenate. Then the chapter misses its sharpest "done right" finding.
    - (c) Drop methods. Then B019, which the repo's own ruff config enforces, goes unexplained.

Also proposed for the owner (no decision needed unless declined):
- No new books. GoF, Ramalho (*Fluent Python* 2nd ed., O'Reilly 2022, confirmed in the O'Reilly catalogue) and Slatkin (*Effective Python* 3rd ed.) are in `bibliography.html`. Chapter titles weren't visible, so they stay bracketed.
- **Rhodes, python-patterns.guide** (index fetched 2026-11-05):
  - `gang-of-four/visitor/`, `gang-of-four/memento/` and `gang-of-four/interpreter/` each return HTTP 404, and none of the three names appears in the index.
  - ch25 therefore claims no Rhodes page.
  - ch26 claims none either: "The Decorator Pattern" page is about the GoF pattern, and ch20 already credits it.
- At N2, a dated r12 note in `_plans/spikes.md` says that mypy 2.4.1 now types a singledispatch function by its fallback signature (evidence A), which updates PDP-012's "mypy does not model dispatch". It's for r13 (ch28), and no r12 prose uses it.

## Planning evidence

The planning run is read-only, so `<scratchpad>/r12plan` was not created. Every probe ran as inline code with the session scratchpad (`<scratchpad>`) as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `<repo>/.venv/bin/python -I -c CODE`. The version is `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- mypy: `<repo>/.venv/bin/python -I -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET`. The version is `mypy 2.4.1 (compiled: yes)`.
- ruff: `<repo>/.venv/bin/ruff check --isolated --no-cache --select B019 --target-version py315 --stdin-filename renderer.py`, with the snippet on standard input. The version is ruff 0.17.3.

Snippets are reduced models. Line numbers will differ and are never asserted. Every output is a prediction for the member until the build quotes it as observed.

**A. singledispatch under mypy.** The fallback is typed `HandlingEvent` (a three-class union). It registers `Booked` returning `str`, `Loaded` returning `int`, and `int`. It never registers `Delivered`. A `match` function omits `Delivered`. Exit 1:
```
<string>:29: error: Argument 1 to "register" of "_SingleDispatchCallable" has incompatible type "Callable[[Loaded], int]"; expected "Callable[..., str]"  [arg-type]
<string>:34: error: Dispatch type "int" must be subtype of fallback function first argument "Booked | Loaded | Delivered"  [misc]
<string>:37: note: Revealed type is "functools._SingleDispatchCallable[str, def (event: __main__.Booked | __main__.Loaded | __main__.Delivered) -> str]"
<string>:38: note: Revealed type is "str"
<string>:39: error: Argument 1 to "describe" has incompatible type "str"; expected "Booked | Loaded | Delivered"  [arg-type]
<string>:48: error: Argument 1 to "assert_never" has incompatible type "Delivered"; expected "Never"  [arg-type]
```
- **mypy says nothing about the unregistered `Delivered`.** The missing `match` arm is an error.
- New against PDP-012: mypy 2.4.1 types the singledispatch function by its fallback's signature and checks call arguments against it (line 39). That's ch28's ground and isn't used in r12.

**B. singledispatch at run time.**
```
unrecognised event
['Booked', 'object']
TypeError: no description for Delivered
booked/int booked/str fallback
either
```
- With an `object` fallback, an unregistered `Delivered` gets `"unrecognised event"` silently, and the registry holds only `Booked` and `object`.
- A raising fallback fails only when the program runs.
- Dispatch reads the first argument only (`two(1, Booked(...))` falls back).
- A union annotation registers both classes (ch28's ground, not used).

**C. The GoF accept form.** An `EventVisitor[T]` Protocol with `visit_booked` and `visit_delivered`. A `Describer` that lacks `visit_delivered`. Exit 1:
```
<string>:26: error: Argument 1 to "accept" of "Booked" has incompatible type "Describer"; expected "EventVisitor[Never]"  [arg-type]
<string>:26: error: Argument 1 to "accept" of "Delivered" has incompatible type "Describer"; expected "EventVisitor[Never]"  [arg-type]
```
- Twins built as frozen slotted subclasses of the events (`_AcceptingBooked(Booked)` adding `accept`) type-check under `--strict` (exit 0), with `isinstance(event, _AcceptingBooked | _AcceptingDelivered)` narrowing.
- At run time, `describe_by_accept(twin)` and the `match` `describe(twin)` both give `CN-1 delivered at SGSIN`. A twin is not equal to the `src` event (dataclass `__eq__` compares classes).

**D. Interpreter.** Nodes `PerKg`, `Flat`, `Add`, `Max`, `OverWeight` under `type Expr`. Recursive fields are unquoted, relying on deferred annotations. Under mypy (exit 1):
```
<string>:39: error: Argument 1 to "assert_never" has incompatible type "Over"; expected "Never"  [arg-type]
<string>:50: error: Argument 2 to "Sum" has incompatible type "str"; expected "PerKg | Flat | Sum | Larger | Over"  [arg-type]
```
That earlier probe used the names `Sum`/`Larger`/`Over`, so the member's message will name its own classes. At run time, with the decision 5 tree:
```
10 45.00 EUR
100 120.00 EUR
1000 1200.00 EUR
2000 2225.00 EUR
over 1000 kg: 1.10 EUR per kg + 25.00 EUR; otherwise the larger of 1.20 EUR per kg and 45.00 EUR
ValueError: cannot add USD to EUR
AssertionError: Expected code to be unreachable, but got: 'x'
```
- Two equal trees compare equal with equal hashes. `Add.__match_args__` is `('left', 'right')`, and `Add.__annotations__` resolves to `{'left': Expr, 'right': Expr}`.
- Two `per_kg(Decimal(1))` closures are not equal (`False`).
- `max` over a `Money` with a hand-written `__lt__` (currency-checked) type-checks (revealed `Money`, exit 0).

**E. Memento forms at run time.** Booking: 100 kg to `SGSIN`, with a commercial invoice. Inside the block: attach a dangerous goods declaration, reweigh to 1,200 kg, redirect to `"Hamburg"` (refused).
```
snapshot
  AmendmentError: not a UN/LOCODE: 'Hamburg'
  request: 100 SGSIN
  documents: ['COMMERCIAL_INVOICE']
  audit: ['attached dangerous goods declaration', 'reweighed to 1200 kg', "refused redirect to 'Hamburg'", 'rolled back']
shallow
  AmendmentError: not a UN/LOCODE: 'Hamburg'
  request: 100 SGSIN
  documents: ['COMMERCIAL_INVOICE', 'DANGEROUS_GOODS_DECLARATION']
  audit: ['attached dangerous goods declaration', 'reweighed to 1200 kg', "refused redirect to 'Hamburg'", 'rolled back']
deepcopy
  AmendmentError: not a UN/LOCODE: 'Hamburg'
  request: 100 SGSIN
  documents: ['COMMERCIAL_INVOICE']
  audit: ['rolled back']
snapshot shares request: True deepcopy shares: False
```
- All three restore the request.
- The shallow form keeps the attached document because it shares the set. The deep form erases the refused attempt from the audit.
- Separate probe:
  - `copy.copy(b)` shares `documents` (`True`);
  - `copy.deepcopy(frozendict(...)) is fd` is `False`, while `copy.copy(fd) is fd` is `True`;
  - `copy.deepcopy` of a frozen dataclass returns a new, equal object;
  - assigning to a frozen field raises `FrozenInstanceError cannot assign to field 'destination'`.
- The probe model type-checks apart from one untyped helper in the probe.

**F. Memento under mypy** (exit 1):
```
<string>:15: error: Property "destination" defined in "BookingSnapshot" is read-only  [misc]
<string>:16: error: "frozenset[DocumentKind]" has no attribute "add"  [attr-defined]
<string>:18: error: Unexpected keyword argument "destinaton" for "replace"; did you mean "destination"?  [call-arg]
<string>:18: note: "replace" defined in "copy"
<string>:19: note: Revealed type is "__main__.BookingSnapshot"
```
mypy checks `copy.replace` keywords against the dataclass fields.

**G. `functools.wraps` at run time.** `render_bill(bill: str, /, *, width: int = 72) -> str` with a docstring and a `kind` attribute, wrapped by a bare wrapper and by a `wraps` wrapper:
```
('__module__', '__name__', '__qualname__', '__doc__', '__annotate__', '__type_params__') ('__dict__',)
bare wrapper bare.<locals>.wrapper None __main__ None False (*args, **kwargs) ()
wrapped render_bill render_bill Render a bill of lading as text. __main__ BILL_OF_LADING True (bill: str, /, *, width: int = 72) -> str ()
(*args, **kwargs) -> str
True
False
(T,) ()
{'kind': 'BILL_OF_LADING', '__wrapped__': <function render_bill at 0x...>}
```
- **Surprise:** on 3.15.2, `WRAPPER_ASSIGNMENTS` holds `__annotate__`, not `__annotations__`. The functools page still lists `__annotations__`. PEP 749 specifies the change (Sources).
- `inspect.signature(f, follow_wrapped=False)` gives `(*args, **kwargs) -> str`: the return annotation comes through the copied `__annotate__`. This is recorded and not asserted.
- `wrapped(wrapped(f)).__wrapped__ is f` is `False`, because it points one level down, and `inspect.unwrap` reaches `f`. `__type_params__` is copied. The wrapper's `__dict__` holds the copied `kind` and `__wrapped__`. The address was masked.

**H. `ParamSpec` without `wraps`, and an untyped decorator.** Run time:
```
wrapper None (*args: P.args, **kwargs: P.kwargs) -> R
```
mypy (exit 1):
```
<string>:13: note: Revealed type is "def (str, *, width: int =) -> str"
<string>:14: error: Argument "width" to "render_bill" has incompatible type "str"; expected "int"  [arg-type]
<string>:15: error: Function is missing a type annotation  [no-untyped-def]
<string>:17: error: Untyped decorator makes function "g" untyped  [untyped-decorator]
```
`ParamSpec` keeps the static signature without `wraps`, and `wraps` keeps the runtime one. They're read by different tools (r09 evidence F, extended).

**I. Concatenate and `inspect.signature`.** `with_width(72)` supplies the first argument of `render(width: int, bill: str, /)`, uses `functools.wraps`, and returns `Callable[P, R]` from `Callable[Concatenate[int, P], R]`. mypy (exit 1):
```
<string>:22: note: Revealed type is "def (str) -> str"
<string>:24: error: Too many arguments for "render"  [call-arg]
<string>:24: error: Argument 1 to "render" has incompatible type "int"; expected "str"  [arg-type]
```
Run time:
```
(width: int, bill: str, /) -> str
bind: missing a required argument: 'bill'
72
```
- **`inspect.signature` follows `__wrapped__` and reports parameters the wrapper doesn't take.** `bind('B/L 1')` fails although the call works.
- `functools.partial(issued_at, fixed)` gives `(number: str, /) -> str` at run time, and mypy reveals `functools.partial[str]` and refuses `stamp(fixed, 'BL-1')` (`[call-arg]`, `[arg-type]`) and `stamp(1)` (`[arg-type]`). A partial has no `__name__`.
- Setting `w.__signature__` on a `wraps` wrapper is `"_Wrapped[[int], int, [int], int]" has no attribute "__signature__"  [attr-defined]`, so the member doesn't take that route.

**J. A parametrised decorator used bare.** mypy (exit 1):
```
<string>:21: error: Argument 1 to "cached_for" has incompatible type "Callable[[str], str]"; expected "float"  [arg-type]
<string>:25: error: Too many positional arguments for "cached_kw"  [call-arg]
<string>:25: error: Argument 1 to "cached_kw" has incompatible type "Callable[[str], str]"; expected "float"  [arg-type]
```
Run time:
```
function wrapper True decorate
TypeError: cached_kw() takes 0 positional arguments but 1 was given
```
- The positional factory used bare binds `render` to `decorate`. `render('bl-1')` returns a function named `wrapper` with no error.
- The keyword-only factory fails at the `def`.

**K. `cached_for` with an injected clock, and stacking with `timed_render`.** The clock is a `FakeClock` with `advance`, and the renderer advances it by 2:
```
render_outer ['BL-1'] [('render_outer', 2.0), ('render_outer', 0.0)]
render_inner ['BL-1'] [('render_inner', 2.0)]
after expiry: ['BL-1']
TypeError: cannot use 'tuple' as a dict key (unhashable type: 'list')
```
- With the timer outside the cache, every call is timed, the hit as `0.0`. With the timer inside, only the miss is timed.
- After the window, the function renders again.
- The model type-checks under `--strict` (exit 0) with `entries: dict[Hashable, tuple[float, R]]`. No `Any` and no `cast`.
- The unhashable-key message is the 3.15.2 wording.

**L. Class decorators.**
- Run time:
  - `@dataclass(frozen=True, slots=True)` above `@document("BOL")` registers a class that is **not** the one bound to the name (`False`). The registered class has no `__slots__`, while the bound class has them.
  - With the class decorator above the dataclass, it registers the bound class (`True`).
  - Beneath a non-slots `@dataclass(frozen=True)`, it registers the bound class (`True`).
- mypy (exit 1):
  ```
  <string>:19: error: Missing return statement  [return]
  <string>:28: note: Revealed type is "def (number: str) -> __main__.BillOfLading"
  <string>:29: note: Revealed type is "str"
  <string>:31: error: Argument 1 to "document" has incompatible type "type[Manifest]"; expected "DocumentKind"  [arg-type]
  ```
  - `def document[C: type](kind) -> Callable[[C], C]` keeps the class's own type.
  - A `register` that forgets `return cls` is `[return]`.
  - Using the factory bare is `[arg-type]`.

**M. Decorated methods.**
```
instance alive after del + collect: True
CacheInfo(hits=0, misses=1, maxsize=None, currsize=1)
after cache_clear: True
TypeError: R2.render() missing 1 required positional argument: 'number'
BL-1 False True
```
- `@functools.cache` on a method keeps the instance alive through `del` and `gc.collect()` until `cache_clear()`.
- A class-based wrapper (`__call__` and `update_wrapper`, no `__get__`) doesn't bind `self`. A function wrapper does, because functions have `__get__`.
- ruff, exit 1. Nothing for `cached_property`:
  ```
  B019 Use of `functools.lru_cache` or `functools.cache` on methods can lead to memory leaks
   --> renderer.py:5:5
  B019 Use of `functools.lru_cache` or `functools.cache` on methods can lead to memory leaks
    --> renderer.py:9:5
  Found 2 errors.
  ```
- The root config selects `B`, so a test that defines a cached method needs `# noqa: B019`.

**Sources fetched 2026-11-05.** curl with tags stripped. Prose agents re-fetch, the page text wins, and a quotation stops where the page's sentence stops.
- **python-patterns.guide**: Visitor, Memento and Interpreter pages are 404, and none of the names is in the index.
- **functools** (https://docs.python.org/3/library/functools.html, banner 3.15.2):
  - `update_wrapper`:
    - "Update a wrapper function to look like the wrapped function."
    - "To allow access to the original function for introspection and other purposes (e.g. bypassing a caching decorator such as @lru_cache), this function automatically adds a __wrapped__ attribute to the wrapper that refers to the function being wrapped."
    - "If the wrapper function is not updated, the metadata of the returned function will reflect the wrapper definition rather than the original function definition, which is typically less than helpful."
    - "Changed in version 3.4: The __wrapped__ attribute now always refers to the wrapped function, even if that function defined a __wrapped__ attribute."
    - The `WRAPPER_ASSIGNMENTS` parenthesis lists `__annotations__`, unlike 3.15.2 (evidence G).
  - `wraps`: "Without the use of this decorator factory, the name of the example function would have been 'wrapper', and the docstring of the original example() would have been lost." ch20 already quotes this, so ch26 quotes `update_wrapper` instead.
  - `cache`: "If a method is cached, the self instance argument is included in the cache."
  - `singledispatch`: "note that the dispatch happens on the type of the first argument".
- **PEP 749**, "Implementing PEP 649" (Jelle Zijlstra; Final; 3.14), section "Wrappers that provide __annotations__": "functools.update_wrapper() (and therefore functools.wraps()) will copy only the __annotate__ attribute from the wrapped object to the wrapper."
- **inspect** (https://docs.python.org/3/library/inspect.html):
  - On `follow_wrapped`: "Pass False to get a signature of callable specifically (callable.__wrapped__ will not be used to unwrap decorated callables.)"
  - `unwrap`: "It follows the chain of __wrapped__ attributes returning the last object in the chain."
  - Also "signature() uses this to stop unwrapping if any object in the chain has a __signature__ attribute defined."
- **typing** (https://docs.python.org/3/library/typing.html):
  - `Concatenate`: "Concatenate can be used in conjunction with Callable and ParamSpec to annotate a higher-order callable which adds, removes, or transforms parameters of another callable."
  - `ParamSpec`: "They are used to forward the parameter types of one callable to another callable – a pattern commonly found in higher order functions and decorators." The sentence contains an en dash, so a prose agent quotes only the part before it or paraphrases it.
  - `assert_never`: "Ask a static type checker to confirm that a line of code is unreachable."
- **PEP 612**, "Parameter Specification Variables" (Mark Mendoza; Final; 3.10): "This PEP proposes typing.ParamSpec and typing.Concatenate to support expressing these kinds of relationships."
- **dataclasses** (https://docs.python.org/3/library/dataclasses.html), `slots`: "If true (the default is False), __slots__ attribute will be generated and new class will be returned instead of the original one."
- **Compound statements** (https://docs.python.org/3/reference/compound_stmts.html):
  - "Decorator expressions are evaluated when the function is defined, in the scope that contains the function definition."
  - "Multiple decorators are applied in nested fashion."
  - "Class decorators were introduced in PEP 3129."
- **Descriptor guide** (https://docs.python.org/3/howto/descriptor.html): "To support automatic creation of methods, functions include the __get__() method for binding methods during attribute access."
- **Programming FAQ**, "How do I cache method calls?" (https://docs.python.org/3/faq/programming.html): "The disadvantage is that instances are kept alive until they age out of the cache or until the cache is cleared."
- **ruff B019** (https://docs.astral.sh/ruff/rules/cached-instance-method/): "Using the functools.lru_cache and functools.cache decorators on methods can lead to memory leaks, as the global cache will retain a reference to the instance, preventing it from being garbage collected."
- **copy** (https://docs.python.org/3/library/copy.html):
  - `replace`: "Creates a new object of the same type as obj, replacing fields with values from changes." (Added in 3.13.)
  - "Because deep copy copies everything it may copy too much, such as data which is intended to be shared between copies."
- **PEP 443**, "Single-dispatch generic functions" (Łukasz Langa; Final; 3.4): "When the implementation is chosen based on the type of a single argument, this is known as single dispatch."
- **PEP 634**, "Structural Pattern Matching: Specification" (Brandt Bucher, Guido van Rossum; Final; 3.10), and **PEP 636**, "Structural Pattern Matching: Tutorial" (Daniel F Moisset; Final; 3.10). Pointer only.
- **PEP 318** (Kevin D. Smith, Jim J. Jewett, Skip Montanaro, Anthony Baxter; Final; 2.4), **PEP 3129** "Class Decorators" (Collin Winter; Final; 3.0: "This PEP proposes class decorators, an extension to the function and method decorators introduced in PEP 318."), and **PEP 695** (Eric Traut; Final; 3.12).
- **GoF** isn't quotable (r06 finding). Bracketed items are used only if a prose agent verifies them in the book; otherwise the idea is described without attribution:
  - [Visitor makes adding an operation easy and adding an element class hard];
  - [Visitor relies on double dispatch];
  - [Memento keeps the originator's encapsulation; the caretaker never looks inside];
  - [Interpreter suits simple grammars where efficiency isn't critical, and leaves parsing out].
- **O'Reilly**: *Fluent Python* 2nd ed. is confirmed in the catalogue, and its decorator chapter title wasn't visible. *Effective Python* 3rd ed. items weren't checked. Both stay bracketed.

Repo facts:
- **Reconciliation.** Rows run 1-133, so r12 adds 134-146. Three open legacy rows belong to r12:
  - row 6 (ch26, `wraps`-less wrapper, moved by r09 decision 5);
  - row 7 (ch25, three dispatchers "over `Document` kinds", adjusted by decision 3);
  - row 8 (ch25, `assert_never` makes a missing arm a type error).

  `CLAIMS_FIRST_ENFORCED = 47`, so rows 6-8 are legacy. N2 still gives them test tokens and a status.
- **Figures.** `_data/diagrams.yml` has 25 entries; r12 makes 27 (`section: "Ch. 25"` and `"Ch. 26"`).
- **Test names.** There are 579 unique `def test_` names across `examples` and `spikes`. Three duplicates already exist (`test_money_addition_needs_one_currency`, `test_money_refuses_to_order_across_currencies`, `test_weight_must_be_positive_and_finite`), and r12 reuses none of them.
  - Every name in the Example spec was checked against the set.
  - The near-misses aren't reused: `test_visitor_is_singledispatch_without_accept` (ch3), `test_decorators_preserve_name_doc_and_wrapped` (spike), `test_mypy_reports_a_missing_match_arm` (ch21), `test_stacking_order_changes_result` (spike), `test_syntax_stacking_order_decides_whether_each_attempt_is_audited` (ch20), `test_a_frozen_request_is_a_safe_snapshot` (ch15).
  - The executor re-runs `grep -rhoE "def test_\w+" examples spikes --include='*.py' | sort | uniq -d`.
- **Already taught, so not repeated** (each gets a pointer by title and at most one sentence):
  - The ch3 table rows and the singledispatch `describe` with no `accept`: "The three-way split: dissolve, survive, disambiguate".
  - Closed unions with `match` and `assert_never`: "Composite and Flyweight". ch25 uses them and doesn't re-teach them. Only the open/closed comparison and the silent fallback are new.
  - A frozen request as a safe snapshot, and undo by inverse: "Command, undo, and command queues" (it points to ch25 for whole-object rollback).
  - `copy.replace`, `copy.copy`, `copy.deepcopy` on a booking request: "Builder, dataclasses, and Prototype". ch25 measures only what deepcopy copies that a snapshot shares.
  - `@contextmanager` and its `try`: "Context managers: deterministic cleanup".
  - Callables as pricing rules (`PricingRule`): "Strategy: the callable".
  - `Money.__lt__`, `__add__`: "The data model: dunder methods as the substrate".
  - The `@` rebinding at definition time, `retry`/`audited`, `@audited` over `@retry`, a decorator returning a non-function, and the one-sentence `wraps`/`ParamSpec` witness: "Decorator the pattern vs @decorator the syntax, and Proxy". ch26 goes deeper and doesn't repeat its tests.
  - `functools.cache` not call-once under threads: "Singleton: module, Borg, and metaclass". The caches here are single-threaded, said once.
  - Negative fixtures, the mypy-API helper and deletion tables: "Proving it works: pytest, pytest-mock, and mypy".
- **Stubs whose ground must not be taken or described** (prose names no content for any of them):
  - "singledispatch: the Visitor the language gives you": one pointer from ch25 (decision 2);
  - "Descriptors and properties": one pointer from ch26 (`cached_property`, writing `__get__`);
  - "Metaclasses, __init_subclass__, and registries": one pointer from ch26 for the other registry form, describing nothing;
  - "Shortcut patterns: dict dispatch, function tables, and EAFP": neither chapter builds a dispatch table in `src`, and the `DOCUMENT_TYPES` registry is never used to dispatch;
  - "Dynamic attributes: __getattr__ and Proxy as a feature";
  - "The GIL and performance";
  - "Final project".
- **Status board hygiene.** r11.x is tagged, but r11's M6 and M7 still read `todo`, PDP-123a to PDP-124c read `active`, and `iteration-plan.md` marks r11 "(active)". The orchestrator closes them at N0. The stray "(None yet...)" line in r11's Corrections is left alone: it's history.

## What is new in each chapter

**ch25 (Visitor dissolves; Memento and Interpreter survive).** "The three-way split" shows one singledispatch `describe` and names the buckets. This chapter witnesses them:
- **Visitor, closed against open.**
  - Three forms give the same five descriptions.
  - `match` with `assert_never` makes a missing event a mypy error and raises at run time for a foreign object.
  - `singledispatch` answers an unregistered event with its fallback, silently, and mypy accepts it.
  - The `accept` form also catches a missing visit method, at the price of an `accept` on every event class.
  - Dispatch is on the first argument only.
- **Memento, what to capture.**
  - A frozen snapshot of the request and a `frozenset` of documents rolls a failed batch back and keeps the audit.
  - A shallow copy shares the document set and corrupts the rollback.
  - A deep copy erases the audit and copies values it could share. mypy refuses changes to a snapshot.
- **Interpreter, a grammar with two readings.**
  - One frozen tree is priced by `evaluate` and written out by `explain`.
  - Closures price the same but can't be compared or explained.
  - mypy reports a node left out of `evaluate` and a child that isn't an expression. Currencies don't mix.

**ch26 (survives).** "Decorator the pattern vs @decorator the syntax, and Proxy" uses `wraps` and `ParamSpec` and points here. This chapter adds:
- **What `wraps` copies, and what it gets wrong.**
  - It copies name, qualified name, docstring, module and `__dict__`, adds `__wrapped__` one level down, and lets `inspect.unwrap` reach the original.
  - Since 3.14 it copies `__annotate__` (PEP 749).
  - `inspect.signature` follows `__wrapped__`, which is right for a pass-through wrapper and wrong for one that supplies an argument.
- **What mypy reads.** `ParamSpec` keeps the signature even without `wraps`. An untyped decorator erases it. `Concatenate` types a decorator that removes a parameter, and `functools.partial` is the honest form at run time too.
- **Factories that can't be misused.** A positional factory used bare silently binds the name to its inner decorator, and a keyword-only one fails at definition.
- **A cache with a clock.**
  - `cached_for(seconds=..., clock=...)`: one entry per argument, expiry at the window, unhashable arguments refused, no sleeps.
  - The timer outside the cache times every call, and inside it times only misses.
- **Class decorators.** One registers a class at definition, refuses a second class for a kind, and binds the name to `None` if it forgets to return (mypy `[return]`). Beneath `@dataclass(slots=True)` it registers a class that gets thrown away.
- **Methods.**
  - A function wrapper binds `self`; a class-based one doesn't.
  - `functools.cache` on a method keeps the instance alive (B019).

## Approach

- **Thesis wording.**
  - ch25 says Visitor dissolves and Memento and Interpreter survive (decision 1). It names what Python removes and what remains for each.
  - ch26 says the syntax is a given and the discipline is the design that survives. It never calls the `@` syntax "the Decorator pattern".
- **Credit.**
  - GoF where each ch25 pattern is introduced, in plain paraphrase that doesn't track the Intent wording.
  - No Rhodes page in either chapter.
  - The functools, inspect, typing, dataclasses, copy, compound-statements, descriptor-guide and FAQ pages, PEPs 443, 612, 634, 636, 695, 749, 318 and 3129, and the ruff rule page, each quoted exactly from fetched pages or credited by author and title.
- **Domain names** come from `_plans/shipping-domain-model.md` rows 25-26, the area table and the series supporting names, plus the names below, recorded at N0. There's no new domain area, no new carrier code and no `Vessel` kind.
  - Port codes are UN/LOCODEs (`NLRTM`, `SGSIN`, `DEHAM`). Rates and fees are illustrative, said once per chapter.
  - ch25:
    - Tracking: `ConsignmentId`, `ConsignmentStatus`, the events `Booked`, `Loaded`, `Departed`, `Cleared`, `Delivered` under `type HandlingEvent` (the family form; the chapter says so), `describe`, `status_after`.
    - Consignment and Rating: `Weight`, `Consignment`, `Money`, `PricingRule` (closure comparison only), `PerKg`, `Flat`, `Add`, `Max`, `OverWeight`, `Expr` (alias), `evaluate`, `explain`, `STANDARD_TARIFF`, `RatingError` not needed (a currency mismatch is `ValueError` from `Money`).
    - Booking and Documentation: `BookingRequest`, `Booking`, `BookingSnapshot`, `rollback`, `DocumentKind`, `AmendmentError`.
  - ch26 (Documentation): `ConsignmentId`, `DocumentKind`, `BillOfLading`, `Manifest`, `render_bill`, `Clock` (alias), `TimingSink` (alias), `timed_render`, `cached_for`, `document_kind`, `DOCUMENT_TYPES`, `DocumentKindError`.
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/25-visitor-memento-interpreter` (project `visitor-memento-interpreter`, package `visitor_memento_interpreter`);
  - `examples/26-decorators-done-right` (project `decorators-done-right`, package `decorators_done_right`).
- **mypy witnesses** copy the r11 `_run`/`_codes` helper from `examples/23-mediator-and-chain-of-responsibility/tests/test_static.py` (`mypy_path` set to the member's `src`, `--cache-dir os.devnull`, and the anchored regex `re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)`).
  - Each asserts the exit status, an exact `_codes()` set and one or two stable substrings. It never asserts line numbers or optional notes.
  - Snippets import real `src` names wherever possible. Reduced models are named in the prose.
- **mypy.api raises the recursion limit** (r10 correction). Neither member has a recursion-sensitive test: the tariff tree is three levels deep. Every member is still run once in reverse file order, with the same pass count (criterion 2).
- **Comparison code** (the owner's 2026-11-04 rule). Every comparison form is real, runs on the shared table **as a conftest fixture param**, and appears in at most one excerpt per chapter.
  - ch25:
    - `visitor_form` `match|singledispatch|accept`;
    - `memento_form` `snapshot|shallow|deepcopy`;
    - `rule_form` `tree|closure`.
    - The one excerpt is the accept twin and `EventVisitor`.
  - ch26:
    - `wrapper_form` `wraps|bare`;
    - plus the negative fixture `_cached_for_positional`.
    - The one excerpt is `_cached_for_positional` and its bare use.
  - All forms live in `tests/conftest.py`, because sibling test imports are blocked under `--import-mode=importlib`. Forms that fail a row on purpose get their own tests and aren't table rows: the silent fallback, the shallow and deep mementos, the closure's inequality, the bare wrapper's metadata, and the positional factory.
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (N1a, N1b) name the test and say why it sees the deletion. A row whose witness was predicted, not run, is marked "executor check".
- **"Not called", "not rendered again" and "not timed" claims.** Each has a test that fails on a named plausible mutation:
  - a cache hit isn't rendered again (mutation: `<` becomes `<=` on the age, or no lookup);
  - a hit isn't timed with the timer inside (mutation: the stack order swapped in the test's composition);
  - the audit isn't rolled back (mutation: capture `audit` in the snapshot, experiment a).
- **Determinism.**
  - No `mock`, `mocker`, `monkeypatch`, `print(`, `sleep`, `time.time`, `perf_counter` or `datetime.now` in tests. Every clock is a test `FakeClock` with `advance`.
  - `src` defaults may name `time.monotonic` and `time.perf_counter`. Tests always inject.
  - The method-cache test holds a `weakref`, deletes the instance, calls `gc.collect()` and asserts it's alive. Then it calls `cache_clear()`, collects again and asserts it's gone. A comment says the cache's strong reference is what keeps it.
  - Registry tests pass their own `registry` dict and never touch `DOCUMENT_TYPES`, except the one test that reads the import-time registration.
  - `filterwarnings = ["error"]` stays active.
- **Counts** of test functions and cases come from the code, and the pytest summary line wins.

Rejected:
- An `accept` method or a visitor class in `src`.
- A singledispatch function in `src` (decision 2).
- A dict dispatch table anywhere in `src` (the shortcut-patterns chapter's ground).
- A text parser (decision 5).
- A dual-form `@overload` decorator (decision 8).
- Setting `__signature__` on a wrapper (mypy `[attr-defined]`; evidence I).
- `cached_property` or a hand-written descriptor in ch26 `src`.
- `typing.cast` or `Any` in `src`.
- Threads.
- Any assertion on elapsed wall time, `id()` or memory.

## Per-chapter spec

### ch25: Visitor, Memento, and Interpreter (pattern, has_example = true, buckets: Visitor dissolves; Memento and Interpreter survive)

Thesis:
- **Visitor.** Its force is many operations over a fixed family of kinds, added without editing the kinds.
  - Python removes `accept` and the visitor class: each operation is a function with `match` over a closed union.
  - What remains is the closed-or-open decision: `match` with `assert_never` reports a missing kind, while `singledispatch` lets others extend the set and says nothing when a kind is missing.
- **Memento.** Its force is restoring an object to an earlier state without exposing it.
  - A frozen snapshot is the memento, and a context manager is the caretaker.
  - What to capture, and what mustn't roll back, remain decisions.
- **Interpreter.** Its force is rules written as sentences in a small grammar.
  - Frozen node dataclasses are the grammar, and each interpretation is one `match`.
  - The grammar and its readings remain design.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one from a comparison fixture):
1. `## Learning objectives` (~100), five bullets, one per close bullet:
   - choose `match` or `singledispatch` by closed or open set;
   - say what `accept` costs;
   - snapshot and roll back a booking;
   - pick what a memento captures;
   - evaluate and explain a tariff tree.
2. `## Why this matters` (~200). Intent first: a tracking feed with five event kinds, booking batches that fail midway, and tariff rules a pricing team writes. Three failures:
   - a delivered event answered by a fallback with no error (test 3);
   - a rollback that keeps a document attached inside the failed block (test 9);
   - a closure tariff nobody can read back (test 23).
3. Figure plus one paragraph (~60).
4. `## Visitor: one function per operation` (~500). Excerpt `describe`.
   - GoF credited for Visitor in plain paraphrase. Bucket: dissolves, with one sentence pointing to "The three-way split: dissolve, survive, disambiguate".
   - One sentence pointing to "Composite and Flyweight" for `match` and `assert_never`.
   - Every form describes the journey the same way (test 1). `status_after` maps each event (test 2).
   - mypy reports an event left out (test 21). At run time, `describe` raises for an object outside the union (test 4); quote the 3.15.2 `AssertionError` text.
   - The one comparison excerpt is the accept twin and `EventVisitor`. It catches a missing visit method too (test 23 static), and it puts an `accept` on every event class (test 6). [GoF on double dispatch, if verified.]
5. `## Closed or open` (~350):
   - When others add kinds, `singledispatch` is the form. One sentence pointing to "singledispatch: the Visitor the language gives you", by exact title, describing nothing from it.
   - An event with no registration gets the fallback's answer (test 3), and mypy exits 0 (test 22). That is the price of an open set.
   - Dispatch is on the first argument only (test 5; quote the functools sentence). Two-axis dispatch is a `match` on a tuple, in one sentence.
   - Quote PEP 443's definition of single dispatch.
6. `## Memento: a frozen snapshot and a rollback` (~600). Excerpt `BookingSnapshot`, `Booking.snapshot`/`restore` and `rollback`.
   - GoF credited for Memento in plain paraphrase [encapsulation and the caretaker, if verified]. Bucket: survives.
   - One sentence pointing to "Command, undo, and command queues": a frozen request is already a safe snapshot, and this case adds mutable working state with no inverse.
   - Rollback restores the request in every form (test 7) and the documents in the snapshot form (test 8). It re-raises (test 11). A block that succeeds keeps its changes (test 12). The audit survives (test 10).
   - The shallow form keeps the attached document (test 9). The deep form erases the audit (test 13) and copies the frozen request a snapshot shares (test 14). Quote the copy docs' "may copy too much".
   - mypy refuses to change a snapshot (test 24), and the run time refuses too (test 15).
7. `## Interpreter: a tariff as a tree` (~550). Excerpt the node classes, `Expr` and `evaluate`.
   - GoF credited for Interpreter in plain paraphrase. Bucket: survives.
   - One sentence: with deferred annotations (since 3.14), node fields name `Expr` before it's defined.
   - The tree and the closures price 10, 100, 1,000 and 2,000 kg alike: 45.00, 120.00, 1,200.00 and 2,225.00 EUR (test 16). 1,000 kg isn't over the limit, and 10 kg pays the minimum charge.
   - `explain` writes the rule back (test 17). Equal trees compare and hash equal (test 18), and closures built the same way don't (test 19). That's the survive argument: the rules are data with more than one reading.
   - Mixed currencies are refused (test 20). mypy reports a node left out of `evaluate` (test 25) and a child that isn't an expression (test 26).
   - One sentence: `evaluate` is itself a visitor over a closed grammar. One sentence: parsing isn't built here.
8. `## When not to use it` (~180):
   - a single operation over the kinds (write it inline);
   - a frozen originator (keep the old value; no snapshot class);
   - an undo with a cheap inverse (Command);
   - a rule set that never changes and nobody reads back (a plain function is enough).

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Assistant-written visitors, mementos and interpreters.** Asked for "a visitor", an assistant often adds an `accept` method to every event class and a visitor class per operation, and asked for rollback it often saves `copy.copy(booking)`. Paste a prompt that states the forms:

   > Over the closed `HandlingEvent` union, write each operation as one function using `match` that ends in `case _: assert_never(...)`, with no `accept` methods. Snapshot a `Booking` into a frozen `BookingSnapshot` holding the request and a `frozenset` of documents, leave the audit out, and restore it in a `rollback` context manager that re-raises. Write tariff rules as frozen node dataclasses under `type Expr`, with `evaluate` and `explain` each a single `match`.

   If the reply adds `accept` or snapshots with `copy.copy`, ask for the test that fails.</blockquote>

   The sidebar body is at most 120 words by `validate.word_count`. Every backticked name in it exists in `src`.
9. `## Build, run, observe` (~220 plus output). Each experiment runs in a fresh scratch copy: delete the copy's `.venv`, run `uv sync --locked --all-packages`, and confirm `visitor_memento_interpreter.__file__` points into the copy. Each changes one thing, then is reverted. Each runs a filter chosen by the prose agent, followed by `uv run mypy --strict src tests`. **The filter is stated in the chapter, and the chapter quotes its complete output:**
   - (a) Add `audit: tuple[str, ...]` to `BookingSnapshot`, capture it in `snapshot()`, and restore it as a list in `restore()`. Expected: test 10 fails, with the audit holding only `"rolled back"`; mypy exits 0. Executor check: whether test 12 or any `memento_form` row also fails. Quote as observed.
   - (b) Delete the `Delivered` arm from `describe`. Expected: test 1[match] (and 1[accept], whose twins subclass the `src` events, if it routes through `describe`; executor check) fails with `AssertionError: Expected code to be unreachable`. mypy exits 1 with `[arg-type]`, `expected "Never"`, in `src`. Quote as observed.
10. `## What you can do now` (~150): five bullets, one per objective, in the same order. Each names its artifact: `describe` with test 21, test 3, `rollback` with test 9, test 13, and `evaluate`/`explain` with test 19. Every backticked token in the close appears earlier in the chapter.
11. `## For deeper coverage` (~130):
    - GoF (Visitor, Memento, Interpreter);
    - PEPs 443, 634 and 636;
    - the `functools`, `copy` and `typing` (`assert_never`) docs;
    - PEP 749 for deferred annotations;
    - [Ramalho, *Fluent Python* 2nd ed., on pattern matching, if verified];
    - the bibliography link.

Figure `25-visitor-memento-interpreter` (vertical, three columns):
- **Left column.** `HandlingEvent` (accent), then `describe`, "match, assert_never: a missing kind is a type error".
  - A muted, dashed side box: "singledispatch: an unregistered kind gets the fallback".
  - A second muted, dashed box: "accept: a method on every event class".
- **Middle column.** `Booking`, then `snapshot()`, then `BookingSnapshot` "frozen: request, documents".
  - `rollback` with an arrow back to `Booking`, labelled "restores on error".
  - A side note: "audit: not captured".
- **Right column.** `Expr` (accent) over the small tree `OverWeight`, then `Add` (`PerKg`, `Flat`) and `Max` (`PerKg`, `Flat`).
  - Two arrows out: `evaluate` "Money" and `explain` "text".
- No numbers in the SVG.

Caption draft (40 words with the prefix): "Figure 25.1: Each operation over the closed event union is one match that mypy checks for every kind. A booking rolls back from a frozen snapshot that leaves the audit alone, and one tariff tree is both priced and explained."

### ch26: Decorators done right (pattern, has_example = true, bucket: survives)

Thesis: the `@` syntax rebinds a name at definition time, and that part is the language's. Doing it right is the design that survives:
- `functools.wraps` for runtime tools, and knowing when it misleads them;
- `ParamSpec` for mypy;
- factories that can't be used bare;
- stacking chosen for what a cache should hide;
- class decorators placed above `@dataclass(slots=True)`;
- wrappers that bind on methods without keeping instances alive.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one from a comparison fixture):
1. `## Learning objectives` (~100), five bullets:
   - preserve identity and signature;
   - type a decorator for mypy, including one that supplies an argument;
   - write a factory that refuses bare use;
   - build and stack a cache with a clock;
   - place class decorators and decorate methods safely.
2. `## Why this matters` (~200). Intent first: a portal renders bills of lading, caches them for five minutes and times the work. Three failures:
   - a renderer that reports itself as `wrapper` with no docstring (test 3);
   - a factory used bare that returns a function where text was expected, with no error (test 16);
   - a document class registered beneath `@dataclass(slots=True)` that isn't the class the code uses (test 21).
3. Figure plus one paragraph (~60).
4. `## What wraps copies` (~450). Excerpt `timed_render`.
   - One sentence pointing to "Decorator the pattern vs @decorator the syntax, and Proxy" for the rebinding and the factories.
   - Quote `update_wrapper`'s first sentence and its `__wrapped__` sentence.
   - Both forms render the same text (test 1). `wraps` keeps name, qualified name, docstring and module (test 2), while the bare form reports `wrapper` and no docstring (test 3). The `__dict__` is copied and `__wrapped__` added (test 5). `__wrapped__` goes one level down, and `inspect.unwrap` reaches the original (test 6; quote `unwrap`).
   - `inspect.signature` follows `__wrapped__` (test 4).
   - Since Python 3.14 the copied attribute is `__annotate__` (test 7; quote PEP 749). The functools page still lists `__annotations__`; state it as observed on 3.15.2.
5. `## What mypy reads` (~400):
   - `ParamSpec` keeps the signature without `wraps` (test 26), and an untyped decorator erases it (test 27). The two tools read different things.
   - `Concatenate` types a decorator that supplies an argument (test 30; quote the typing sentence and PEP 612). `wraps` then makes `inspect.signature` report the original parameters, and `bind` refuses a working call (test 8). `functools.partial` reports what remains (test 9).
   - The rule: `wraps` assumes the wrapper takes the same arguments.
6. `## Factories that refuse to be used bare` (~300). The one comparison excerpt is `_cached_for_positional` and its bare use.
   - Bare, it binds the name to its inner decorator and returns a function (test 16). mypy refuses it (test 28).
   - The keyword-only `cached_for` fails at the `def` (test 17), and mypy refuses that too (test 29). Quote the compound-statements sentence on decorators evaluated at definition.
7. `## A cache with a clock, and the order of the stack` (~400). Excerpt `cached_for`.
   - Within the window the text is cached (test 10). At the limit and past it, it renders again (test 11). One entry per argument (test 12). Unhashable arguments are refused with the 3.15.2 message (test 13). The window must be positive (test 14). `timed_render` reports clock time, also when rendering raises (test 15).
   - Stacking: with the timer outside, both calls are timed. With it inside, only the miss is (test 18). Say which one a dashboard wants, and quote "applied in nested fashion".
   - Single-threaded, said once.
8. `## Class decorators` (~300). Excerpt `document_kind` and its use on `BillOfLading`.
   - Registration happens at definition (test 19), and a second class for a kind is refused (test 20).
   - Forgetting `return cls` binds the name to `None` (test 22), and mypy reports `[return]` (test 31). The class keeps its type (test 32).
   - Beneath `@dataclass(slots=True)`, the decorator registers a class that gets thrown away (test 21; quote the dataclasses `slots` sentence), so `document_kind` goes on top. Quote PEP 3129's abstract.
   - One sentence pointing to "Metaclasses, __init_subclass__, and registries" by title for the other registry form, describing nothing.
9. `## Decorating methods` (~200):
   - A function wrapper binds `self` (test 23; quote the descriptor-guide sentence). A class-based wrapper doesn't (test 24).
   - `functools.cache` on a method keeps the instance alive until the cache is cleared (test 25). Quote the functools cache sentence, the FAQ sentence and ruff's B019 text.
   - One sentence pointing to "Descriptors and properties" for `cached_property`.
10. `## When not to use it` (~180):
    - behaviour that varies per object at run time (the Decorator pattern; point to it by title);
    - a decorator that supplies an argument (`functools.partial`);
    - a cache over data that must be fresh, or over unhashable arguments;
    - a registry nobody reads.

    Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Assistant-written decorators.** Asked for "a caching decorator", an assistant often writes an untyped wrapper without `functools.wraps`, takes the window as a positional argument, and caches a method on `self`. Paste a prompt that states the rules:

    > Write `cached_for` as a PEP 695 `[**P, R]` factory with keyword-only `seconds` and an injected `clock`, its wrapper decorated with `functools.wraps(func)` and typed `Callable[P, R]`. Put `timed_render` inside the cache so only misses are timed. Where a decorator would supply an argument, use `functools.partial`. Put `document_kind` above `@dataclass(slots=True)`, and never put `functools.cache` on a method.

    If the reply drops `wraps` or the `*`, ask for the test that fails.</blockquote>
11. `## Build, run, observe` (~220 plus output). The scratch-copy rules and the stated-filter rule are the same as ch25's (confirm `decorators_done_right.__file__`):
    - (a) Remove `@wraps(func)` from `timed_render`'s wrapper. Expected: the metadata tests that use `src` `timed_render` (2, 4, 5, 6 and 7; the executor names which) fail, and test 1 still passes. mypy exits 0, because `ParamSpec` still carries the signature. Quote as observed.
    - (b) Make `cached_for`'s `seconds` positional (drop the `*`). Expected:
      - test 17 fails with `DID NOT RAISE`;
      - test 29's code set changes, so it fails;
      - member mypy exits 1 with `[unused-ignore]` on the `# type: ignore[call-arg, arg-type]` that test 17 carries (executor check).

      Quote as observed.
12. `## What you can do now` (~150): five bullets mapped one to one to the objectives. They name `wraps` with test 3, test 8, test 16, `cached_for` with test 18, and `document_kind` with test 21.
13. `## For deeper coverage` (~130):
    - PEPs 318, 3129, 612, 695 and 749;
    - the functools, inspect, typing and dataclasses docs;
    - the compound-statements reference;
    - the descriptor guide;
    - the programming FAQ on caching methods;
    - the ruff B019 page;
    - [Ramalho, *Fluent Python* 2nd ed., and Slatkin, *Effective Python* 3rd ed., on decorators, if verified];
    - the bibliography link.

Figure `26-decorators-done-right` (vertical):
- Top accent box `render_bill`.
- Two stacks side by side:
  - left: `timed_render` over `cached_for`, "timer outside: every call timed";
  - right: `cached_for` over `timed_render`, "timer inside: only misses timed".
- Below, a row of two boxes:
  - `functools.wraps` "copies name, doc, dict; adds __wrapped__", with an arrow to `inspect.signature` "follows __wrapped__";
  - `ParamSpec` with an arrow to "mypy".
- A muted, dashed side box: "supplies an argument: signature misleads; use partial".
- Bottom: `document_kind` above `dataclass(slots=True)`, "registers the class the name holds".
- No numbers in the SVG.

Caption draft (41 words with the prefix): "Figure 26.1: The order of a stack decides what a cache hides from a timer. functools.wraps keeps a renderer's identity for runtime tools, ParamSpec keeps its signature for mypy, and a class decorator belongs above a slotted dataclass."

Citations, both chapters: verify each before writing, apply the bracketed fallbacks, quote no sentence unless it was checked on a fetched page, stop each quotation where the page's sentence stops, and make no comparison between languages.

## Example spec

### `examples/25-visitor-memento-interpreter` (project `visitor-memento-interpreter`, package `visitor_memento_interpreter`)

`pyproject.toml` in the r11 shape (`requires-python = ">=3.15"`, `uv_build`, no `[tool.*]`).

- `domain.py`:
  - `ConsignmentId = NewType("ConsignmentId", str)`.
  - `ConsignmentStatus(Enum)`: `BOOKED`, `LOADED`, `IN_TRANSIT`, `CLEARED`, `DELIVERED`.
  - `DocumentKind(Enum)`: `COMMERCIAL_INVOICE`, `DANGEROUS_GOODS_DECLARATION`.
  - `Money(amount: Decimal, currency: str)`, frozen slotted:
    - `__add__` and `__lt__` raise `ValueError("cannot add USD to EUR")`-style messages across currencies;
    - `times(factor)` rounds to cents;
    - `__str__` gives `"120.00 EUR"`.
  - `Weight(kilograms: Decimal)`, finite and positive.
  - `Consignment(id, weight, destination)`, frozen slotted kw_only.
  - `AmendmentError(Exception)`.
- `events.py`:
  - `Booked`, `Loaded`, `Departed`, `Cleared`, `Delivered`, each `(consignment_id, port)`, frozen slotted; `type HandlingEvent = ...`.
  - `describe(event) -> str` via `match` and `case _: assert_never(event)`. The strings are `"CN-1 booked at NLRTM"`, `"loaded at"`, `"departed"` (with no "at"), `"cleared customs at"` and `"delivered at"`.
  - `status_after(event) -> ConsignmentStatus` (`Departed` gives `IN_TRANSIT`), the same shape.
- `memento.py`:
  - `BookingRequest(consignment_id, kilograms: Decimal, destination: str)`, frozen slotted kw_only.
  - `BookingSnapshot(request, documents: frozenset[DocumentKind])`, frozen slotted.
  - `Booking`, `@dataclass(slots=True, eq=False)`, with `request`, `documents: set[DocumentKind]` and `audit: list[str]`. Methods:
    - `attach(kind)` and `reweigh(kilograms)`, each appending to `audit`; `reweigh` uses `copy.replace`;
    - `redirect(destination)`, which appends `"refused redirect to 'Hamburg'"` and raises `AmendmentError("not a UN/LOCODE: 'Hamburg'")` unless the destination is five uppercase letters;
    - `snapshot()` and `restore(snapshot)`.
  - `rollback(booking)`, a `@contextmanager`: snapshot, yield; on `Exception`, restore, append `"rolled back"` and re-raise. Its docstring says the audit is deliberately not captured.
- `tariff.py`:
  - `PerKg(rate: Money)`, `Flat(amount: Money)`, `Add(left: Expr, right: Expr)`, `Max(left, right)`, `OverWeight(kilograms: Decimal, then: Expr, otherwise: Expr)`, frozen slotted; `type Expr = ...` after the classes.
  - `evaluate(expr, consignment) -> Money` and `explain(expr) -> str`, each a `match` ending in `assert_never`. The text format is evidence D's.
  - `STANDARD_TARIFF: Expr` (decision 5).
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `JOURNEY` (the five `src` events of `CN-1`) and `DESCRIPTIONS` (the five strings).
- `visitor_form` params `match|singledispatch|accept`, each giving `(events, describe)`:
  - `match` is the `src` events with `describe`;
  - `singledispatch` is a `@singledispatch` fallback on `object` returning `"unrecognised event"`, with five registrations;
  - `accept` uses the twins `_AcceptingBooked` to `_AcceptingDelivered` (frozen slotted subclasses adding `accept[T]`), `EventVisitor[T]` (a Protocol) and `_Describer`, with an entry point that narrows with `isinstance` against the twin union (no `cast`).
  - The executor picks the fixture type, for example a small generic dataclass. Keep `Any` out.
- `booking` factory: 100 kg to `SGSIN` with a commercial invoice.
- `memento_form` params `snapshot|shallow|deepcopy`, each giving `Callable[[Booking], AbstractContextManager[None]]`. `snapshot` is `rollback`. `_shallow_rollback` and `_deep_rollback` follow evidence E.
- `rule_form` params `tree|closure`, each giving `Callable[[Consignment], Money]`. `closure` builds `_per_kg`, `_flat`, `_add`, `_max` and `_over_weight` as `PricingRule` closures, written as defs (ruff E731).
- `consignment` factory taking kilograms.

`test_visitor.py`:
1. `test_every_visitor_form_describes_a_journey_the_same_way` x `visitor_form` (3).
2. `test_status_after_maps_each_event_to_a_consignment_status[booked|loaded|departed|cleared|delivered]` (5).
3. `test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback`: a test-local singledispatch with four registrations; `Delivered` gives `"unrecognised event"`. Domain row 25's failing test.
4. `test_describe_refuses_an_object_outside_the_union`: `AssertionError` matching `Expected code to be unreachable`. The test carries one `# type: ignore[arg-type]`.
5. `test_singledispatch_dispatches_on_the_first_argument_only`: test-local, as in evidence B.
6. `test_the_accept_form_puts_an_accept_method_on_every_event_class`: all five twins have `accept`, and none of the `src` classes do.

`test_memento.py`:
7. `test_rollback_restores_the_request_after_a_failed_amendment` x `memento_form` (3): 100 kg to `SGSIN` after the evidence E block.
8. `test_rollback_restores_the_attached_documents`.
9. `test_a_shallow_memento_keeps_a_document_attached_after_rollback`: domain row 25's "a mutated memento corrupts rollback".
10. `test_rollback_keeps_the_audit_trail`: the four entries of evidence E.
11. `test_rollback_re_raises_the_amendment_error`: matching `not a UN/LOCODE`.
12. `test_a_block_that_succeeds_keeps_its_changes`.
13. `test_a_deepcopy_memento_erases_the_audit_trail_on_rollback`: `["rolled back"]`.
14. `test_a_snapshot_shares_the_frozen_request_and_a_deepcopy_copies_it`.
15. `test_a_snapshot_cannot_be_changed_at_run_time`: `FrozenInstanceError`.

`test_tariff.py`:
16. `test_every_rule_form_prices_the_same_consignments` x `rule_form` (2) x `[10|100|1000|2000]` (4).
17. `test_explain_writes_the_tariff_as_text`.
18. `test_equal_tariff_trees_compare_and_hash_equal`.
19. `test_closures_built_the_same_way_are_not_equal`.
20. `test_a_rule_in_another_currency_is_refused`: `ValueError` matching `cannot add USD to EUR`.

`test_static.py`:
21. `test_mypy_reports_an_event_left_out_of_a_match`: imports `src`; `{"arg-type"}`, `expected "Never"`.
22. `test_mypy_accepts_a_singledispatch_visitor_that_misses_an_event`: imports `src` events; exit 0, empty.
23. `test_mypy_reports_a_visitor_class_missing_a_visit_method`: reduced model (evidence C); `{"arg-type"}`.
24. `test_mypy_refuses_to_change_a_snapshot`: imports `src`; `{"misc", "attr-defined"}`, `is read-only`.
25. `test_mypy_reports_a_tariff_node_left_out_of_evaluate`: imports `src`; `{"arg-type"}`, `"OverWeight"; expected "Never"`.
26. `test_mypy_refuses_a_node_whose_child_is_not_an_expression`: imports `src`; `{"arg-type"}`.

Numbers are spec ids, not file order. The plan has 26 test functions and 41 cases:
- `test_visitor.py`: 6 functions, 12 cases;
- `test_memento.py`: 9 functions, 11 cases;
- `test_tariff.py`: 5 functions, 12 cases;
- `test_static.py`: 6 functions, 6 cases.

The executor counts from the pytest summary line.

Also `README.md` and the card `_examples/25-visitor-memento-interpreter.md`: `order: 25`, eyebrow "Coordination · Visitor, Memento and Interpreter", and a concept title with no count. None of the following appears in `src/`: `mock`, `monkeypatch`, `print(`, `Optional`, `abc`/`ABC`, `Any`, `cast`, `singledispatch`, `accept`, `deepcopy`, `threading`.

Deletion table (N1a):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `Delivered` arm in `describe` | removed | 1[match] (experiment b), member mypy | `AssertionError`; `[arg-type]` `Never` |
| `Departed` maps to `IN_TRANSIT` | maps to `LOADED` | 2[departed] | wrong status |
| `assert_never` default | `case _: return ""` | 4 | `DID NOT RAISE` |
| `documents` captured as `frozenset` | the live set stored (with `# type: ignore`) | 8 (executor check), 24 | a document survives the rollback |
| `request` restored | not restored | 7[snapshot] | 1,200 kg after rollback |
| `documents` restored | not restored | 8 | document still attached |
| audit not captured | captured and restored (experiment a) | 10 | refused attempt erased |
| re-raise | `raise` removed | 11 | `DID NOT RAISE` |
| restore only on error | restore in `finally` | 12 | changes undone |
| `"rolled back"` appended | removed | 10 | three entries, not four |
| UN/LOCODE check | removed | 7[snapshot], 11 | no error, no rollback |
| `OverWeight` strict `>` | `>=` | 16[1000-*] | 1,225.00 instead of 1,200.00 |
| `Max` arm | returns left | 16[10-tree] | 12.00 instead of 45.00 |
| currency check in `Money.__add__` | removed | 20 | `DID NOT RAISE` |
| `OverWeight` arm in `evaluate` | removed | 16[*-tree], member mypy | `AssertionError`; `[arg-type]` |
| `explain` format | `Max` text changed | 17 | text differs |

### `examples/26-decorators-done-right` (project `decorators-done-right`, package `decorators_done_right`)

- `domain.py`:
  - `ConsignmentId`.
  - `DocumentKind(Enum)`: `BILL_OF_LADING`, `MANIFEST`, `CUSTOMS_DECLARATION`.
  - `DocumentKindError(ValueError)`.
  - `DOCUMENT_TYPES: dict[DocumentKind, type]`.
  - `document_kind[C: type](kind, *, registry: dict[DocumentKind, type] = DOCUMENT_TYPES) -> Callable[[C], C]`. It raises `DocumentKindError(f"{kind.name} is already registered to {existing.__qualname__}")` on a duplicate.
  - `BillOfLading(number, consignment_id, port_of_loading, port_of_discharge)` and `Manifest(number, consignment_ids: tuple[ConsignmentId, ...])`. Each is `@document_kind(...)` **above** `@dataclass(frozen=True, slots=True)`.
- `rendering.py`:
  - `type Clock = Callable[[], float]` and `type TimingSink = Callable[[str, float], None]`.
  - `render_bill(bill, /, *, width: int = 72) -> str`: one line, `textwrap.shorten` to `width`, with a docstring.
  - `timed_render[**P, R](sink, *, clock: Clock = time.perf_counter)`, which reports `func.__name__` and the elapsed clock time in `finally`.
  - `cached_for[**P, R](*, seconds: float, clock: Clock = time.monotonic)`:
    - raises `ValueError(f"seconds must be positive, got {seconds}")`;
    - keys on `(args, frozenset(kwargs.items()))`;
    - serves an entry while `now - stored < seconds`;
    - its docstring says single-threaded and hashable arguments only.
  - Both use `functools.wraps`.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `FakeClock` (`now`, `__call__`, `advance`) and the `clock` fixture.
- `bill` factory.
- `wrapper_form` params `wraps|bare`, each a `ParamSpec` timer decorator (`bare` omits `wraps`) applied to `render_bill`.
- `_cached_for_positional(seconds)`, the negative fixture of decision 8.
- `recording_sink`.

`test_wraps.py`:
1. `test_both_wrapper_forms_render_the_same_text` x `wrapper_form` (2) x two bills (2).
2. `test_wraps_keeps_the_name_qualname_doc_and_module`.
3. `test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring` (row 6).
4. `test_inspect_signature_follows_wrapped_to_the_original_parameters`: `(bill: BillOfLading, /, *, width: int = 72) -> str` against the bare `(*args: P.args, **kwargs: P.kwargs) -> R` (row 6).
5. `test_wraps_copies_the_function_dict_and_adds_wrapped`.
6. `test_wrapped_points_one_level_down_and_unwrap_reaches_the_original`.
7. `test_wraps_copies_annotate_rather_than_annotations`: reads `functools.WRAPPER_ASSIGNMENTS`.
8. `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters`: test-local `issued_at` under a `Concatenate` decorator. The signature shows both parameters, and `bind(number)` raises `TypeError` matching `missing a required argument`.
9. `test_partial_reports_the_parameters_that_remain`.

`test_factories.py`:
10. `test_cached_for_returns_the_cached_text_within_the_window`: one render for two calls.
11. `test_cached_for_renders_again_once_the_window_has_passed[at-the-limit|past-it]` (2).
12. `test_cached_for_keeps_one_entry_per_argument`.
13. `test_cached_for_refuses_an_unhashable_argument`: `TypeError` matching `unhashable type`.
14. `test_cached_for_refuses_a_window_that_is_not_positive[zero|negative]` (2).
15. `test_timed_render_reports_the_elapsed_clock_time[rendered|raised]` (2): `2.0` both times.
16. `test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator`: the name is `decorate`, and the call returns a callable named `render_bill`'s wrapper, not text. Domain row 26's failing test.
17. `test_a_keyword_only_factory_used_bare_fails_at_definition`: `TypeError` matching `takes 0 positional arguments`. The test carries one `# type: ignore[call-arg, arg-type]`.
18. `test_stacking_order_decides_whether_a_cache_hit_is_timed[timer-outside-2|timer-inside-1]` (2).

`test_classes.py`:
19. `test_document_kind_registers_the_class_at_definition`: `DOCUMENT_TYPES[DocumentKind.BILL_OF_LADING] is BillOfLading`.
20. `test_document_kind_refuses_a_second_class_for_a_kind`: own registry; `DocumentKindError` matching `already registered`.
21. `test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class`: own registry.
22. `test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none`: test-local; one `# type: ignore[return]` on the helper.

`test_methods.py`:
23. `test_a_function_wrapper_binds_self_on_a_method`.
24. `test_a_class_based_wrapper_does_not_bind_self`: `TypeError` matching `missing 1 required positional argument`.
25. `test_functools_cache_on_a_method_keeps_the_instance_alive`: `# noqa: B019`, with `weakref`, `gc.collect()` and `cache_clear()`.

`test_static.py`:
26. `test_mypy_keeps_the_signature_through_a_wrapper_without_wraps`: reduced model (evidence H); `{"arg-type"}`.
27. `test_mypy_reports_an_untyped_decorator`: reduced model; `{"untyped-decorator", "no-untyped-def"}`.
28. `test_mypy_refuses_a_positional_factory_used_bare`: reduced model; `{"arg-type"}`.
29. `test_mypy_refuses_a_keyword_only_factory_used_bare`: imports `src`; `{"call-arg", "arg-type"}`, `Too many positional arguments`.
30. `test_mypy_types_a_decorator_that_supplies_an_argument`: reduced model (evidence I); `{"call-arg", "arg-type"}`.
31. `test_mypy_reports_a_class_decorator_that_forgets_to_return`: reduced model; `{"return"}`.
32. `test_mypy_keeps_the_class_type_through_document_kind`: imports `src`; exit 0, empty.

The plan has 32 test functions and 39 cases:
- `test_wraps.py`: 9 functions, 12 cases;
- `test_factories.py`: 9 functions, 13 cases;
- `test_classes.py`: 4 functions, 4 cases;
- `test_methods.py`: 3 functions, 3 cases;
- `test_static.py`: 7 functions, 7 cases.

The executor counts from the pytest summary line.

Also `README.md` and the card `_examples/26-decorators-done-right.md`: `order: 26`, eyebrow "Idiomatic Python · Decorators", and a concept title. None of the following appears in `src/`: `mock`, `monkeypatch`, `print(`, `Optional`, `Any`, `cast`, `RateCalculator`, `Invoice`, `LineItem`, `cached_property`, `__signature__`, `threading`, `functools.cache`, `lru_cache`.

Deletion table (N1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `wraps` in `timed_render` | removed (experiment a) | 2, 4, 5, 6 (executor names which) | `wrapper`, no `__wrapped__` |
| `wraps` in `cached_for` | removed | 6 (executor check) | unwrap chain broken |
| keyword-only `*` | removed (experiment b) | 17, 29, member mypy | `DID NOT RAISE`; code set; `[unused-ignore]` |
| window check | removed | 14[all] | `DID NOT RAISE` |
| age comparison `<` | `<=` | 11[at-the-limit] | not rendered again at the limit |
| cache lookup | skipped | 10 | rendered twice |
| per-argument key | key on `()` | 12 | second bill gets the first's text |
| timing in `finally` | after the call only | 15[raised] | no record when rendering raises |
| duplicate check | removed | 20 | `DID NOT RAISE` |
| `return cls` | removed | 19, member mypy (`[return]`) | `BillOfLading` is `None` |
| decorator above the dataclass | moved beneath | 19 | registered class is not `BillOfLading` |

## Steps and status

Step ids are `N*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| N0 | This plan file. PDP-125a-c and 126a-c `active` in `iteration-plan.md` (dated note); r12 marked active and r11 closed. Reconciliation rows 134-146 `open` with a dated r12 note; rows 6-8 noted "r12". Domain rows 25-26 updated with the supporting names and decisions 1-10 (row 25's `load_plan(cargo, vessel)` replaced per decision 3), with a dated note. ch25-26 stub `description` lines written. r11's M6-M7 and PDP-123a to 124c closed. Upstream pins re-checked. Decisions recorded | - | todo |
| N1a | ch25 member, card, README; one `uv lock`; three green runs plus one reverse-file-order run; the deletion table, each row in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`) | N0 | todo |
| N1b | ch26 member, card, README; one `uv lock` after N1a (sequenced for `uv.lock`); three green runs plus one reverse-order run; deletion table | N1a | todo |
| N2 | Witness results into rows 134-146 and rows 6-8 (row 6 verified, row 7 adjusted, row 8 verified); the spikes.md r12 note (evidence A). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | N1b | todo |
| N3 | Two figures, specs `diagrams/specs/25-*.py` and `26-*.py`, `_data/diagrams.yml` (single owner; 27 entries); figures 00-24 unchanged; every name drawn exists in `src` or the standard library | N2 | todo |
| N4 | ch25-26 `status = "drafted"` (`kind` stays `pattern`) | N3 | todo |
| N5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly, runs its two experiments in fresh scratch copies with the filter it states, quotes that filter's complete output through `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table | N3, N4 | todo |
| N6 | Opus validation; up to two repair rounds, with a seam scan after every cut and a check that close bullets map one to one to objectives | N5 | todo |
| N7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r12.x` on main; notes-only release | N6 | todo |

Reconciliation rows (step N0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 134 | 25 | Three Visitor forms (match, singledispatch, accept) describe a journey the same way; `status_after` maps every event; the accept form puts `accept` on every event class | `test_every_visitor_form_describes_a_journey_the_same_way`, `test_status_after_maps_each_event_to_a_consignment_status`, `test_the_accept_form_puts_an_accept_method_on_every_event_class` |
| 135 | 25 | A missing `match` arm is a mypy error and a foreign object raises at run time; a singledispatch visitor gives an unregistered event its fallback and mypy accepts it; an accept visitor missing a method is a mypy error; singledispatch dispatches on the first argument only | `test_mypy_reports_an_event_left_out_of_a_match`, `test_describe_refuses_an_object_outside_the_union`, `test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback`, `test_mypy_accepts_a_singledispatch_visitor_that_misses_an_event`, `test_mypy_reports_a_visitor_class_missing_a_visit_method`, `test_singledispatch_dispatches_on_the_first_argument_only`, `source: https://docs.python.org/3/library/functools.html`, `source: https://peps.python.org/pep-0443/` |
| 136 | 25 | Rollback from a frozen snapshot restores the request and documents, re-raises, keeps a successful block and keeps the audit; a snapshot can't be changed at run time or for mypy | `test_rollback_restores_the_request_after_a_failed_amendment`, `test_rollback_restores_the_attached_documents`, `test_rollback_re_raises_the_amendment_error`, `test_a_block_that_succeeds_keeps_its_changes`, `test_rollback_keeps_the_audit_trail`, `test_a_snapshot_cannot_be_changed_at_run_time`, `test_mypy_refuses_to_change_a_snapshot` |
| 137 | 25 | A shallow memento keeps a document attached after rollback; a deepcopy memento erases the audit and copies the frozen request a snapshot shares | `test_a_shallow_memento_keeps_a_document_attached_after_rollback`, `test_a_deepcopy_memento_erases_the_audit_trail_on_rollback`, `test_a_snapshot_shares_the_frozen_request_and_a_deepcopy_copies_it`, `source: https://docs.python.org/3/library/copy.html` |
| 138 | 25 | A tariff tree and closures price the same consignments; the tree explains itself and compares by value, closures don't; currencies don't mix; mypy reports a missing node and a child that isn't an expression | `test_every_rule_form_prices_the_same_consignments`, `test_explain_writes_the_tariff_as_text`, `test_equal_tariff_trees_compare_and_hash_equal`, `test_closures_built_the_same_way_are_not_equal`, `test_a_rule_in_another_currency_is_refused`, `test_mypy_reports_a_tariff_node_left_out_of_evaluate`, `test_mypy_refuses_a_node_whose_child_is_not_an_expression` |
| 139 | 26 | `wraps` keeps name, qualified name, doc, module and dict, adds `__wrapped__` one level down, copies `__annotate__`; without it the wrapper reports its own name and signature; `inspect.signature` follows `__wrapped__` | `test_both_wrapper_forms_render_the_same_text`, `test_wraps_keeps_the_name_qualname_doc_and_module`, `test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring`, `test_inspect_signature_follows_wrapped_to_the_original_parameters`, `test_wraps_copies_the_function_dict_and_adds_wrapped`, `test_wrapped_points_one_level_down_and_unwrap_reaches_the_original`, `test_wraps_copies_annotate_rather_than_annotations`, `source: https://docs.python.org/3/library/inspect.html`, `source: https://peps.python.org/pep-0749/` |
| 140 | 26 | `ParamSpec` keeps the signature for mypy without `wraps`; an untyped decorator erases it; `Concatenate` types a decorator that supplies an argument while `inspect.signature` reports the original parameters; `partial` reports what remains | `test_mypy_keeps_the_signature_through_a_wrapper_without_wraps`, `test_mypy_reports_an_untyped_decorator`, `test_mypy_types_a_decorator_that_supplies_an_argument`, `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters`, `test_partial_reports_the_parameters_that_remain`, `source: https://peps.python.org/pep-0612/` |
| 141 | 26 | A positional factory used bare binds the name to its inner decorator; a keyword-only one fails at definition; mypy refuses both | `test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator`, `test_a_keyword_only_factory_used_bare_fails_at_definition`, `test_mypy_refuses_a_positional_factory_used_bare`, `test_mypy_refuses_a_keyword_only_factory_used_bare`, `source: https://docs.python.org/3/reference/compound_stmts.html` |
| 142 | 26 | `cached_for` serves within the window, renders again at and past it, keeps one entry per argument, refuses unhashable arguments and a non-positive window; `timed_render` reports clock time, also on failure | `test_cached_for_returns_the_cached_text_within_the_window`, `test_cached_for_renders_again_once_the_window_has_passed`, `test_cached_for_keeps_one_entry_per_argument`, `test_cached_for_refuses_an_unhashable_argument`, `test_cached_for_refuses_a_window_that_is_not_positive`, `test_timed_render_reports_the_elapsed_clock_time` |
| 143 | 26 | A timer outside the cache times every call; inside it, only misses | `test_stacking_order_decides_whether_a_cache_hit_is_timed` |
| 144 | 26 | A class decorator registers at definition, refuses a duplicate, keeps the class type; forgetting to return binds `None` and mypy reports it; beneath a slotted dataclass it registers a discarded class | `test_document_kind_registers_the_class_at_definition`, `test_document_kind_refuses_a_second_class_for_a_kind`, `test_mypy_keeps_the_class_type_through_document_kind`, `test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none`, `test_mypy_reports_a_class_decorator_that_forgets_to_return`, `test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class`, `source: https://docs.python.org/3/library/dataclasses.html`, `source: https://peps.python.org/pep-3129/` |
| 145 | 26 | A function wrapper binds `self`; a class-based wrapper doesn't; `functools.cache` on a method keeps the instance alive | `test_a_function_wrapper_binds_self_on_a_method`, `test_a_class_based_wrapper_does_not_bind_self`, `test_functools_cache_on_a_method_keeps_the_instance_alive`, `source: https://docs.python.org/3/howto/descriptor.html`, `source: https://docs.python.org/3/faq/programming.html`, `source: https://docs.astral.sh/ruff/rules/cached-instance-method/` |
| 146 | 25-26 | The "Build, run, observe" experiments behave as quoted | `run: N5` |

Legacy rows at N2:
- Row 6 gets `test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring` and `test_inspect_signature_follows_wrapped_to_the_original_parameters` ("verified (r12)").
- Row 7 gets `test_every_visitor_form_describes_a_journey_the_same_way` ("adjusted (r12): over `HandlingEvent` kinds, not `Document` kinds; decision 3").
- Row 8 gets `test_mypy_reports_an_event_left_out_of_a_match` ("verified (r12)").

## Corrections after the build

(None yet. The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.)

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs, and once with the test files in reverse order (`tests/test_static.py` first), with the same pass count.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch"` over both members' `tests` prints nothing.
   - `grep -rn "print("` over both members prints nothing.
   - `grep -rnE "\bAny\b|cast\(|singledispatch|def accept|deepcopy|threading"` over `examples/25-*/src` prints nothing.
   - `grep -rnE "\bAny\b|cast\(|RateCalculator|\bInvoice\b|LineItem|cached_property|__signature__|functools\.cache|lru_cache|threading"` over `examples/26-*/src` prints nothing.
3. Every test name cited in rows 134-145 and rows 6-8 is defined exactly once across `examples/*/tests`.
4. Every mypy-API test asserts its exit status and an exact code set, uses the anchored `_codes` regex, and asserts no line number or optional note. `grep -c "_codes("` is at least 5 in each `test_static.py`. Every `# type: ignore[...]` and `# noqa` names a code.
5. Deletion tables (N1a, N1b): every row, deleted in a fresh scratch copy whose imports come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed", and executor-check rows are resolved or moved to Corrections.
6. Every "not rendered again", "not timed", "not captured" or "silently" sentence names a test with a deletion-table row (or experiment) whose mutation makes it fail.
7. ch25-26 are drafted, with one figure each, captions of 20-45 words including `Figure N.1:`, and at most 2,500 prose words each by `validate.py` (an error above; a warning below 1,900 is reported, not padded).
8. Spine and sidebar:
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `grep -c "^## When not to use it"` is 1 and `grep -c "^## How it works"` is 0 in each.
   - `## What you can do now` is the second-to-last H2, directly before `## For deeper coverage`, with as many bullets as the learning objectives.
   - Every backticked token in the close appears earlier in the chapter.
   - Each sidebar opens with a bold lead, holds a nested `>` prompt, has at most two non-quoted paragraphs, matches no `\bCheck(:| that| three| four| whether)`, is at most 120 words, and names only identifiers present in the chapter or its `src`.
   - `validate.py` passes the `pattern` spine.
9. Thesis:
   - ch25 says Visitor dissolves (`dissolv` at least 1) and Memento and Interpreter survive (`surviv` at least 2). It names what Python removes for each and what remains: closed or open; what to capture; the grammar and its readings.
   - ch26 says the discipline survives (`surviv` at least 1), and never calls the `@` syntax "the Decorator pattern" (`grep -n "Decorator pattern"` hits only the pointer sentence).
10. Non-overlap and pointers:
    - ch25 points to "The three-way split: dissolve, survive, disambiguate", "Composite and Flyweight", "Command, undo, and command queues" and "singledispatch: the Visitor the language gives you" by title. `grep -nE "register\(|forward ref|singledispatchmethod|\.registry"` over `_docs/25-*.md` prints nothing.
    - ch26 points to "Decorator the pattern vs @decorator the syntax, and Proxy", "Descriptors and properties" and "Metaclasses, __init_subclass__, and registries" by title, and describes no content of the last two. It repeats no ch20 test (no `retry`, `audited` or `quote_carrier` in `_docs/26-*.md` beyond the pointer sentence).
    - Neither chapter builds a dispatch table or describes any other stub.
11. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, the cards, the specs and the SVGs, with `--stats` reviewed against the house-voice rubric.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|memoiz)"` over prose (quotations and code excluded) prints nothing.
    - Intent before mechanism in every body section. No paragraph after an excerpt re-narrates its identifiers.
12. No em-dash or en-dash in any file touched in r12, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. The `ParamSpec` docs sentence containing an en dash is quoted only up to the dash, or paraphrased.
13. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Smalltalk|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/25-*.md`, `_docs/26-*.md`, the new READMEs and the cards prints nothing.
14. Idiomatic scan: 0 ban-tier in both members.
15. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`. Object addresses are masked by a stated filter if any appear.
16. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
17. Each experiment is performed in a fresh scratch copy and changes one thing. The chapter states the exact filter command, and the quoted block is its complete output, followed by `uv run mypy --strict src tests`.
18. Attribution:
    - ch25 credits GoF (Visitor, Memento, Interpreter) in plain paraphrase and PEPs 443, 634/636 and 749 by author, quotes the functools, copy and typing sentences exactly, and claims no Rhodes page.
    - ch26 credits PEPs 318, 3129, 612, 695 and 749 by author, and quotes the functools, inspect, typing, dataclasses, compound-statements, descriptor-guide, FAQ and ruff sentences exactly.
    - GoF claims appear only if verified. Every book cited is already in `bibliography.html`.
19. Claims:
    - Every factual sentence in ch25-26 maps to a named test, `run: N5` or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0, with rows 134-146 resolved and each `source:` URL present in its chapter.
    - No `run: M*` token appears in rows 134-146.
    - Any prose version mention (3.13, 3.14) is preceded by "since", "before", "until" or "new in", so `check_stale_versions` passes.
20. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 27 entries, and `diagrams/0*-*`, `diagrams/1*-*` and `diagrams/2[0-4]-*` are unchanged.
21. Reconciliation rows 134-146 are `verified` or `adjusted` with evidence. Rows 6 and 8 are `verified (r12)`, and row 7 is `adjusted (r12)`.
22. Deterministic:
    - No test depends on wall time, the environment, memory addresses, test order or iteration order it didn't create.
    - Every clock is injected.
    - The method-cache test asserts liveness only through a `weakref` after an explicit `gc.collect()`.
    - Registry tests use their own registry, apart from test 19.
    - `filterwarnings = ["error"]` is still in the root config.
23. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.
24. Every self-contained mypy snippet that stands for code is named in the prose as a reduced model: ch25 test 23; ch26 tests 26, 27, 28, 30 and 31.
25. Test counts in prose and handbacks come from the pytest summary line of a fresh run.
26. Every comparison form said to share a table is a conftest fixture param (`visitor_form`, `memento_form`, `rule_form`, `wrapper_form`), and each chapter shows at most one comparison excerpt.
27. Every figure label that names code (`HandlingEvent`, `describe`, `Booking`, `snapshot()`, `BookingSnapshot`, `rollback`, `Expr`, `OverWeight`, `Add`, `Max`, `PerKg`, `Flat`, `evaluate`, `explain`, `render_bill`, `timed_render`, `cached_for`, `functools.wraps`, `inspect.signature`, `ParamSpec`, `document_kind`, `dataclass(slots=True)`) exists in that chapter's `src` or the standard library, checked by grep at N3.
28. Repo-relative paths only in this plan and every r12 file: `grep -rnE "/home/|/Users/"` over the files touched in r12 prints nothing.

## Risks

- **Predicted messages and counts.** Every iteration since r05 mispredicted something. Expect differences in these places:
  - the class names in the mypy `Never` messages (evidence D used other node names);
  - which tests experiments (a) and (b) fail in each chapter;
  - the `[unused-ignore]` prediction in ch26 (b);
  - whether 1[accept] fails in ch25 (b).

  Tests match codes and stable substrings only.
- **The singledispatch typing change** (evidence A). It's a typeshed or mypy behaviour that can move again. ch25 asserts only exit 0 for a missing registration, and r12 prose doesn't describe the fallback-signature checking.
- **The docs and the runtime disagree on `__annotate__`** (evidence G). Test 7 asserts the runtime constant. The prose quotes PEP 749 and states the docs' list as observed. If a later docs build fixes the list, only that sentence changes.
- **`inspect.signature` and Concatenate.** If a future CPython stops following `__wrapped__` when parameters differ, test 8 flips. It says what 3.15.2 does.
- **Twins and the shared table.** The accept twins subclass the `src` events, so `describe` (the `match` form) also accepts them. The accept form's entry point must call `accept`, not `describe`, or the table proves nothing. The deletion row for `Delivered` checks it.
- **Ruff on tests.** B019 needs `# noqa: B019` in test 25. E731 forbids assigned lambdas in conftest, so closures are defs. N818 is satisfied by `AmendmentError` and `DocumentKindError`. UP037 forbids quoted annotations: the recursive `Expr` fields rely on deferred annotations and must stay unquoted.
- **mypy narrowing in tests** (r11 correction). After `assert x == ()` or an `is` check, mypy may narrow and flag later lines `[unreachable]`. Read values through small helpers as r11 did.
- **Word budgets.**
  - ch25 carries three patterns. If it overruns, the double-dispatch sentence and the `explain` format paragraph shrink first.
  - ch26 carries six topics. If it overruns, the methods section shrinks to two sentences first, then the `__annotate__` sentence.
  - Their tests stay.
- **Stub pointers.** It's tempting to write "the singledispatch chapter shows union registration" or "descriptors explain why". Criterion 10 forbids both.
- **New supporting names.** If the owner declines `BookingSnapshot`, `OverWeight`, `document_kind` or `DocumentKindError`, N1a or N1b waits for the replacement names. Nothing else moves.
- **Liquid.** The f-strings in excerpts contain single braces only. Any `{{` needs `{% raw %}`.
- **`uv.lock` race.** N1a and N1b are sequenced.
