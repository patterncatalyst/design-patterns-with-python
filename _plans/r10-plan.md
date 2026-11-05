---
title: "r10 plan: chapters 21-22 (composing structure; coordinating parties)"
order: 10
output: false
render_with_liquid: false
---

# r10: chapters 21-22, Composite and Flyweight; Observer

Opus-planned 2026-11-05. Branch `release/r10`, cut from main at 275780d (r09.x). This file is the source of truth for r10 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration: Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged. `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch21: slug `21-composite-and-flyweight`, title "Composite and Flyweight", part 7 (`composing-adapting-structure`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.
- ch22: slug `22-observer`, title "Observer", part 8 (`coordinating-traversing`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.

## User decisions (confirmed by the owner 2026-11-05: all five as recommended)

Each decision carries a recommendation. Nothing below is built until the owner answers.

Standing, not a decision: step ids are `K*`. `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md`. `grep -nE "^\| K[0-9]" _plans/*.md` matched nothing before this file.

1. **All three patterns stay "survives".** This is the r02 canonical map ("Composite; Flyweight; Observer (delivery order, failure isolation, subscriber lifetime)") and the ch3 table rows. Each chapter names one survivor:
   - **Composite.** The recursive structure is the decision: what a leaf and a group both answer, where the total is computed, and which tree invariants hold (no empty group, no consignment twice).
   - **Flyweight.** The decision is about identity and lifetime: who builds the shared object, how long it lives, and why immutability makes sharing safe.
   - **Observer.** Three things survive: the delivery contract (order, isolation, re-entrancy) and subscriber lifetime.

   What Python removes is stated in each chapter:
   - Composite: the Component base class (a closed union plus `match`, or a Protocol).
   - Flyweight: the factory class (a function, a `WeakValueDictionary` or `functools.cache`), plus `sys.intern` for strings.
   - Observer: the Observer interface (a callable).

   **Recommend: yes.** Alternatives:
   - (b) Flyweight "dissolves" because `sys.intern` and the small-int cache are built in. That's true only for strings and ints. Evidence F shows a domain value still needs a factory and a lifetime decision. It would also contradict the r02 map and the ch3 table row.
   - (c) Observer "dissolves into callbacks". Evidence J to M show four failure modes that a bare list of callables has, and ch3 already states this one survives.

2. **The Composite example is a `ConsolidatedShipment` of consignments, built bottom-up as a frozen tree, with the GoF component classes as a test-only comparison fixture.**
   - This is domain row 21 ("Consolidated shipments (a consignment of consignments)"), and ch3's prose already names `ConsolidatedShipment`.
   - Leaves are `Consignment`. Groups are `ConsolidatedShipment(id, parts: tuple[Shipment, ...])`, with `type Shipment = Consignment | ConsolidatedShipment`.
   - Both answer `.weight`, which is the uniform interface (Rhodes's symmetry point). Operations that differ, such as flattening to the manifest's consignments, use `match` with `assert_never` over the closed union.
   - A mutable `_Component` hierarchy is a fixture param on the same weight table (`tree_form` `frozen-union|component-classes`). Its leaf `add` raises only when the program runs, and its group can contain itself (evidence C).

   **Recommend: yes.** Alternatives:
   - (b) Packages and pallets. `Package` and `Pallet` aren't domain entities. `Container` is one, but the descriptors and singledispatch chapters own its kinds.
   - (c) A rate rule tree. That collides with domain row 25 (Interpreter's "small `Expr` tree" over `Tariff` and `Surcharge`).

3. **The ch21 split is about 55/45, joined by one story: the tree's leaves share flyweights.**
   - Composite gets about 1,150 body words and Flyweight about 900, in one member and one figure.
   - The join: a consolidation of many consignments repeats the same commodity and the same port codes. Each `Consignment` holds a shared `Commodity` from a pool and interned port codes.
   - Two supporting names go into domain row 21 at K0:
     - `Shipment`, a role alias named for the role like `Layer` (domain rule on aliases);
     - `CommodityPool`, the Flyweight factory.

   **Recommend: yes.** Alternatives:
   - (b) An even split. Composite carries more design content (invariants, the match arm, the GoF comparison), and Flyweight's memory figures are short.
   - (c) Flyweight as a short coda of about 400 words. That's too small to measure the three factory forms and state the lifetime trade-off honestly.

4. **The Observer form is a generic `Signal[E]` per event source, with a plain list of callables as the comparison fixture.**
   - `subscribe(subscriber) -> Unsubscribe` keeps subscription order and ignores a duplicate.
   - Bound methods are held through `weakref.WeakMethod`, so an abandoned `TrackingHistory` isn't kept alive. Plain functions and lambdas are held strongly, because a weak reference to a temporary lambda dies at once (evidence J).
   - `publish` does three things:
     - it iterates a snapshot;
     - it delivers to every subscriber and then raises one `ExceptionGroup` for the failures;
     - it queues an event published during delivery, so every subscriber sees events in publication order (evidence L).
   - `_ListSignal`, a list of callables iterated live, runs the shared delivery table as the `signal_form` fixture param `signal|plain-list`. Its hazards get their own tests.
   - A string-topic event bus appears only as a reduced-model mypy witness (exit 0 on a typo and a wrong payload; evidence N). It isn't a runtime fixture.
   - `Signal` is a supporting name already listed in domain row 22 ("`Signal` helper").

   **Recommend: yes.** Alternatives:
   - (b) Strong references only, with an explicit `Unsubscribe` (and perhaps a context manager). It's simpler and avoids the "a subscriber nobody else holds is dropped" surprise. But it can't witness domain row 22's failing test ("an unsubscribed bound method is kept alive") except as the problem, and the lifetime half of the survives claim goes untaught.
   - (c) A `WeakSet` of observer objects with a `notify` method. That brings back the Observer interface, and the set promises no order (the docs call a set "an unordered collection"), which defeats the ordering contract.

5. **Ownership of `weakref`, threads and async delivery.**
   - **ch21** owns `weakref.WeakValueDictionary` as a Flyweight pool and the "drops what nobody holds" lifetime.
   - **ch22** owns `weakref.WeakMethod`, weak references and garbage collection in a subscriber registry, and the reference-cycle case.
   - **ch8** ("Dataclasses and value semantics") keeps the finding that slotted dataclasses refuse weak references until `weakref_slot=True` (reconciliation row 43). ch21 and ch22 each give it one sentence and a pointer by title, and each runs its own runtime test on its own API.
   - **Threads and async delivery are out of scope in ch22.** `Signal` is documented as single-threaded, in one sentence with no claim attached.
     - Domain row 38 keeps "Observer over an async queue" for "asyncio and the patterns", which is a stub. ch22 doesn't describe what that chapter contains.
     - "The GIL and performance" is also a stub and gets no pointer.
   - The weak pool's possible double build under threads gets one sentence pointing to "Singleton: module, Borg, and metaclass" (drafted and verified, row 94), with no new claim.

   **Recommend: yes.** Alternative (b): ch22 adds a lock and a thread test. That needs a `Barrier` seam and about 300 words the chapter doesn't have, and it takes ground from the GIL chapter.

Also proposed for the owner (no decision needed unless declined):
- No new books. Every book cited is already in `bibliography.html` (GoF, Ramalho, Slatkin, Lott and Phillips). Bracketed items below are dropped if the prose agents can't verify them.
- Rhodes, python-patterns.guide (index fetched 2026-11-05):
  - It has "The Composite Pattern" and "The Flyweight Pattern" pages, and **no Observer page**.
  - "The Prebound Method Pattern" isn't about callbacks or subscribers, so it isn't cited.
  - ch22 credits GoF and the Python docs only.

## Planning evidence

All probes were read-only. Because this planning run is read-only, no scratch directory or file was created, so `.../scratchpad/plan10` doesn't exist. Every probe ran as inline code with the session scratchpad as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `uv run --project <repo> python -I -c CODE`. The version is `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- mypy: `uv run --project <repo> python -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET`. The version is `mypy 2.4.1 (compiled: yes)`.

Snippets are reduced models. Line numbers will differ and are never asserted. Every output is a prediction for the member until the build quotes it as observed.

**A. A recursive union and `match` under mypy.** The snippet had `Consignment` and `ConsolidatedShipment(parts: tuple["Part", ...])` with `type Part = Consignment | ConsolidatedShipment`, plus `total` with a full `match`, a `missing_arm` without the `ConsolidatedShipment` case, and a bad part.
```
<string>:45: error: Argument 1 to "assert_never" has incompatible type "ConsolidatedShipment"; expected "Never"  [arg-type]
<string>:48: note: Revealed type is "tuple[__main__.Consignment | __main__.ConsolidatedShipment, ...]"
<string>:49: error: Argument 2 to "ConsolidatedShipment" has incompatible type "tuple[Weight]"; expected "tuple[Consignment | ConsolidatedShipment, ...]"  [arg-type]
```
- The forward reference to the alias inside the tuple resolves; there's no error on it.
- The full `match` passes.
- A recursive Protocol (`children(self) -> Iterable["Shippable"]`) also checks. A class without `children` is `[assignment]` with `is missing following "Shippable" protocol member:` / `children`.
- A plain mutable class attribute satisfies a read-only `@property` Protocol member (no error).

**B. Union attributes and immutability under mypy** (same model, `kilograms` a property on the group):
```
<string>:17: note: Revealed type is "decimal.Decimal"
<string>:18: error: Item "Consignment" of "Consignment | ConsolidatedShipment" has no attribute "parts"  [union-attr]
<string>:20: error: "Consignment" has no attribute "add"  [attr-defined]
<string>:22: error: "tuple[Consignment | ConsolidatedShipment, ...]" has no attribute "append"  [attr-defined]
<string>:23: error: Property "parts" defined in "ConsolidatedShipment" is read-only  [misc]
```
- Line 17 shows that `s.kilograms` on the union is `Decimal`: the uniform interface type-checks without narrowing.
- `[misc]` for a frozen field matches ch8's recorded code.

**C. The GoF transparent form** (`Component(ABC)` declaring `add`, which raises in `Leaf`, overridden in `Group` over a list):
- Under mypy: exit 0. `leaf.add(Leaf(...))` and `g.add(g)` are both accepted.
- At run time, a group that contains itself gives `self-containing mutable group: RecursionError maximum recursion depth exceeded`.
- The frozen, bottom-up tree can't express either one: a group's parts exist before the group does.

**D. The Composite at run time.** CN-1 is 10 kg, a nested group holds 2.5 kg and 4 kg, and CN-2 is 7.25 kg.
```
total 23.75 naive 17.25
leaf 1 empty 0
eq True hash eq True
FrozenInstanceError cannot assign to field 'parts'
recursionlimit 1000
```
- The naive total sums direct consignments only (domain row 21's failing test).
- **Depth** (a `weight` property recursing through a generator; recursion limit 1000): 100, 300 and 400 levels are fine, and 500, 900 and 1000 raise `RecursionError`. Equality and hash of two separately built 3,000-level trees also raise `RecursionError`.
- This is CPython 3.15.2 behaviour and approximate. The member's test uses 5,000 levels. Prose says "a few hundred levels" and never names a threshold as a rule.
- `node == node` on one deep tree printed `True` (an identity shortcut), so the test compares two separately built trees.

**E. `sys.getsizeof` and instance memory.** One commodity has three fields (`"850760"`, `"lithium-ion batteries"`, `True`). Figures are bytes, approximate, and dated to 3.15.2 on 2026-11-05.
- `sys.getsizeof`:
  - dict-backed instance 48, plus `__dict__` 296;
  - slotted instance 56, with no `__dict__`;
  - slotted with `weakref_slot` 72.
- **`getsizeof` makes the slotted instance look bigger.** It counts only "the memory consumption directly attributed to the object" (sys docs, quoted below).
- Reading `__dict__` on 100,000 dict-backed instances allocated `6400000` bytes, because inline values are materialised into a dict. Measuring by touching `__dict__` changes what you measure.
- `tracemalloc` current bytes for 100,000 items in a list, identical across three runs:

  | Form | Bytes |
  | --- | --- |
  | dict-backed copies | 10404488 (~96 bytes each over the list) |
  | slotted copies | 6401344 (~56) |
  | slotted with `weakref_slot` | 8001344 (~72) |
  | one shared slotted instance | 800376 (the list's pointers only) |

- Slots trim each instance by a constant. Sharing removes the instances. These figures go only into the benchmark script's recorded output (K1a), never into a test assertion.

**F. Interning.** `"NLRTM;SGSIN;NLRTM".split(";")`:
```
split equal True same object False
interned same True ia is a False
joined same False literal vs joined False
intern(joined) is literal True
bytes TypeError: intern() argument must be str, not bytes
subclass TypeError: can't intern Code
ids equal 1
```
- That split strings are distinct objects is CPython behaviour (single-character strings are cached), stated as observed on 3.15.2.
- **Writing `x is "NLRTM"` in source emits `SyntaxWarning: "is" with 'str' literal`.** Under `filterwarnings = ["error"]` a test must never compare to a literal with `is`.
- For 100,000 port codes drawn from four values (two runs, identical): plain split `5402456` bytes with 100,000 distinct objects; interned `801040` bytes with 4 distinct objects.

**G. Flyweight factories.**
```
cache same True CacheInfo(hits=1, misses=1, maxsize=None, currsize=1)
equal distinct True False
weakref slotted: cannot create weak reference to 'Commodity' object
weak pool same True len 1
after del, before collect 0
after collect 0
cache holds 1
mutable shared: second line sees False
replace gives new object, cached unchanged True
mutable hash: unhashable type: 'MutableCommodity'
```
- CPython's reference counting emptied the weak pool on `del`, before `gc.collect()`.
- The data model says "Do not depend on immediate finalization of objects when they become unreachable", so every lifetime test calls `gc.collect()` deliberately before asserting, and the prose says why.
- mypy 2.4.1 exits 0 on a `WeakValueDictionary[str, X]`, `WeakSet[X]` or `WeakMethod` over a slotted `X` without `weakref_slot`; all three raise `TypeError` at run time. ch8 already witnesses the `weakref.ref` case.

**H. `frozendict`:** `'frozendict' object does not support item assignment`.

**J. Observer lifetime.**
```
strong list keeps owner alive: True
dead-to-the-app subscriber still called: [('history', 'Loaded')]
plain ref to bound method alive: False
WeakMethod alive while owner alive: True
WeakMethod after owner gone: None
WeakMethod(lambda): argument should be a bound method, not <class 'function'>
ref to temp lambda alive: False
cyclic owner before collect: True
cyclic owner after collect: False
WeakSet len 3
WeakSet after drop 1
finalize: ['gone']
```
- "WeakSet after drop 1": the `for o in objs` loop variable still held the last observer. **A stray local keeps a subscriber alive in a test.** Lifetime tests build subscribers in a helper function or `del` every name.
- `WeakMethod` equality and hash:
  - while the owner lives: `WeakMethod eq True hash eq True is False`, and a new `WeakMethod` finds the dict entry;
  - after the owner dies: `callback fired ['callback']`, `dead eq False dead self eq True`, and the hash is cached, so `d.get(a)` still finds the entry.
- So the `WeakMethod` is both the registry key and the callback argument that removes it.
- Slotted owners: `WeakMethod`, `WeakSet.add` and `WeakValueDictionary` assignment each raise `TypeError: cannot create weak reference to 'SlottedHistory' object`.

**K. Failure isolation** (subscribers `a`, `boom` raising `RuntimeError("history store down")`, then `b`):
```
naive stops at [('a', 'Departed')] RuntimeError('history store down')
isolated: [('a', 'Departed'), ('b', 'Departed')] [RuntimeError('history store down')]
except*: (RuntimeError('history store down'),)
```

**L. Re-entrancy.**
```
live list, subscribe during notify: [('a', 'Loaded'), ('adder', 'Loaded'), ('late', 'Loaded')]
snapshot, subscribe during notify: [('a', 'Loaded'), ('adder', 'Loaded')] now 3
live list, unsubscribe during notify: [('remover', 'Loaded'), ('b', 'Loaded')]
snapshot, unsubscribe during notify: [('remover', 'Loaded'), ('a', 'Loaded'), ('b', 'Loaded')]
nested publish order: [('echo', 'Departed'), ('echo', 'Loaded')]
```
- On a live list, a subscriber added during delivery gets the current event, and an unsubscribe skips the next subscriber.
- A live **dict** raises `RuntimeError: dictionary changed size during iteration` for both an add and a remove.
- With immediate nested delivery, a subscriber records the nested event before the outer one.
- A queued signal (a `deque` plus a `_delivering` flag) with a raising subscriber gave:
  ```
  group ['store down on Loaded', 'store down on Departed']
  [('customs', 'Loaded'), ('history', 'Loaded'), ('customs', 'Departed'), ('history', 'Departed')]
  delivering reset False pending 0
  ```

**M. `Signal[E]` under mypy** (the full candidate from the Example spec, PEP 695 class, `inspect.ismethod` branch):
```
<string>:79: error: Argument 1 to "publish" of "Signal" has incompatible type "str"; expected "HandlingEvent"  [arg-type]
<string>:81: error: Argument 1 to "subscribe" of "Signal" has incompatible type "Callable[[str], None]"; expected "Callable[[HandlingEvent], None]"  [arg-type]
```
- Otherwise exit 0.
- `inspect.ismethod(handler)` (and `isinstance(handler, types.MethodType)`) narrows to `types.MethodType`. `WeakMethod` then reveals `weakref.WeakMethod[types.MethodType]` and `wm()` gives `types.MethodType | None`, so **that branch loses the subscriber's signature**, and mypy accepts it into a `Callable[[], Subscriber | None]` slot.
- Without narrowing, `weakref.WeakMethod(handler)` keeps it: `weakref.WeakMethod[def (__main__.Loaded)]`. A stored bool (`is_method = inspect.ismethod(h)`) doesn't narrow, and keeps `WeakMethod[def (int)]`.
- The check that matters, the signature at `subscribe`, holds either way.
- `print` is accepted as a `Callable[[Loaded], None]`.

**N. A string-topic bus** (`defaultdict[str, list[Callable[[Any], None]]]`, `publish(topic: str, payload: Any)`): exit 0 on `publish("handling.laoded", ...)`, `publish("handling.loaded", 42)` and a subscriber typed `(event: int)`. Typing the handler `Callable[[object], None]` instead rejects every specific subscriber: `Argument 2 to "subscribe" has incompatible type "Callable[[dict[str, str]], None]"; expected "Callable[[object], None]"  [arg-type]`.

Sources fetched 2026-11-05. The fetch tool can paraphrase punctuation, so prose agents re-fetch and the page text wins.
- **`weakref`** (https://docs.python.org/3/library/weakref.html, banner 3.15.2):
  - "A weak reference to an object is not enough to keep the object alive: when the only remaining references to a referent are weak references, garbage collection is free to destroy the referent and reuse its memory for something else."
  - `WeakMethod`: "Since a bound method is ephemeral, a standard weak reference cannot keep hold of it."
  - `WeakSet`: "Set class that keeps weak references to its elements. An element will be discarded when no strong reference to it exists any more."
  - `WeakValueDictionary`: "Mapping class that references values weakly. Entries in the dictionary will be discarded when no strong reference to the value exists any more."
  - "When `__slots__` are defined for a given type, weak reference support is disabled unless a `'__weakref__'` string is also present in the sequence of strings in the `__slots__` declaration."
- **`sys.intern`** (https://docs.python.org/3/library/sys.html): "Enter *string* in the table of “interned” strings and return the interned string – which is *string* itself or a copy." and "Interned strings are not immortal; you must keep a reference to the return value of `intern()` around to benefit from it." The dictionary-lookup sentence is also usable.
- **`sys.getsizeof`**: "Only the memory consumption directly attributed to the object is accounted for, not the memory consumption of objects it refers to."
- **Data model** (https://docs.python.org/3/reference/datamodel.html):
  - `__slots__`: "*__slots__* allow us to explicitly declare data members (like properties) and deny the creation of `__dict__` and *__weakref__* (unless explicitly declared in *__slots__* or available in a parent.)"
  - "The space saved over using `__dict__` can be significant."
  - Objects: "Do not depend on immediate finalization of objects when they become unreachable (so you should always close files explicitly)." The CPython implementation-detail note on reference counting with "(optional) delayed detection of cyclically linked garbage" is also usable.
- **functools** (https://docs.python.org/3/library/functools.html):
  - `cache`: "Simple lightweight unbounded function cache."
  - `lru_cache`: "The cache keeps references to the arguments and return values until they age out of the cache or until the cache is cleared."
- **Rhodes, "The Composite Pattern"** (https://python-patterns.guide/gang-of-four/composite/). Its sections:
  - the intro: give containers and contents shared methods;
  - the UNIX file system, with symmetry and where it breaks;
  - "On hierarchies";
  - Tkinter's `winfo_children()`, where leaves return an empty list so recursion needs no `isinstance`;
  - "to inherit, or not?": Python allows any means to symmetry, including mypy or plain duck typing.

  Credit it for the symmetry framing, in paraphrase.
- **Rhodes, "The Flyweight Pattern"** (https://python-patterns.guide/gang-of-four/flyweight/):
  - it opens with `intern()`;
  - it covers intrinsic against extrinsic state;
  - it lists built-in flyweights (`bool`, small ints, the empty string and the empty tuple);
  - it prefers a factory function over caching in `__new__`;
  - it suggests `WeakValueDictionary` against unbounded growth;
  - **it doesn't discuss `__slots__`.**

  Credit it for the intern framing, factory-over-`__new__`, and the weak-dictionary remedy, in paraphrase only.
- **Python docs, built-in types** (`set`): the prose agent fetches and quotes the "unordered collection" wording before using it.
- **GoF**: not quotable (r06 finding). Bracketed items are used only if a prose agent verifies them in the book; otherwise the idea is described without attribution:
  - [GoF discusses where to declare child-management operations, trading transparency against safety];
  - [GoF separates intrinsic from extrinsic state for Flyweight];
  - [GoF gives Dependents and Publish-Subscribe as other names for Observer];
  - [GoF raises dangling references to deleted subjects, and update protocols].
- **O'Reilly**: *Fluent Python* 2nd ed. (on `weakref` and `__slots__`) and *Effective Python* 3rd ed. Chapter and item titles weren't checked, so they stay bracketed.

Repo facts:
- **Reconciliation.** Rows run 1-106, so r10 adds 107-119. No open row is owned by ch21 or ch22. Row 43 (ch8, slots drop weak references) is cited, not changed. `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** `_data/diagrams.yml` has 21 entries; r10 makes 23 (`section: "Ch. 21"` and `"Ch. 22"`).
- **Test names.** 459 `def test_` names exist across `examples` and `spikes`. Every name in the Example spec was grepped and none collides. One planned name, `test_a_consignment_weight_must_be_positive_and_finite`, exists from r09 and was renamed. The executor re-runs `grep -rhoE "def test_\w+" examples spikes --include='*.py' | sort | uniq -d`.
- **Already taught, so not repeated** (each gets a pointer by title and at most one sentence):
  - The ch3 Composite, Flyweight and Observer table rows and the coordination paragraph: "The three-way split: dissolve, survive, disambiguate".
  - That Composite fails the dissolve test because the recursive structure is the force: "What 1994 assumed, and what Python dissolves".
  - `slots=True`, `weakref_slot`, frozen as a `__setattr__` guard, frozen hashing, values against entities (`eq=False`): "Dataclasses and value semantics". The member uses them and doesn't re-teach them.
  - Special-method lookup and `__eq__`/`__hash__`: "The data model: dunder methods as the substrate".
  - Callback Protocols and positional-only `/`: "Protocol, duck typing, and structural typing with mypy".
  - Closures and bound callables in a slot: "Strategy: the callable".
  - Events recorded and published instead of an undo stack: "Command, undo, and command queues" already points to Observer. ch22 needs no pointer back.
  - `functools.cache` not call-once under threads: "Singleton: module, Borg, and metaclass".
  - Negative fixtures, the mypy-API helper and deletion tables: "Proving it works: pytest, pytest-mock, and mypy".
- **Stubs whose ground must not be taken or described.** Prose names no content for any of these:
  - "Iterator: generators and the iterator protocol". ch21 flattens with a recursive function returning a tuple, not a generator, and says nothing about generators.
  - "Mediator and Chain of Responsibility".
  - "Visitor, Memento, and Interpreter" (the `Expr` tree).
  - "Descriptors and properties" and "singledispatch: the Visitor the language gives you" (`Container` and `Commodity` kinds).
  - "The GIL and performance" and "asyncio and the patterns".
- **Status board hygiene.** `r09.x` is tagged, but `_plans/r09-plan.md` shows J7 `todo`, and r08's I6 and I7 may also read `todo`. No r10 token depends on them; the orchestrator closes them at K0.

## What is new in each chapter

**ch21 (Composite and Flyweight survive).** Two earlier chapters say only that Composite survives because the structure is the force, and that Flyweight shares immutable state. This chapter adds:
- **The uniform question, measured.** A consignment and a consolidation both answer `.weight`, and mypy types it on the union without narrowing (evidence B).
  - A flat sum misses nested groups: 17.25 kg against 23.75 kg (evidence D).
  - Where the two kinds differ, `match` over a closed union makes a missing arm a mypy error.
- **Invariants a tree must keep.** No empty group, and no consignment counted twice. A frozen tree built bottom-up can't be rewired or made to contain itself.
  - The GoF component classes run the same weight table, but they accept `leaf.add` and `group.add(group)` under mypy and fail only when the program runs (evidence C).
- **Flyweight as identity and lifetime.**
  - A pool returns one `Commodity` per code.
  - A `WeakValueDictionary` drops what nobody holds, and `functools.cache` keeps everything it made. Both run one table.
  - Frozen equality means callers never need `is`, which is why sharing is safe. A mutable shared value changes every consignment that holds it.
- **Memory, measured honestly.** Slots trim each instance by a constant and sharing removes instances (evidence E, benchmark output only). `getsizeof` misleads, and interning port codes keeps four objects out of 100,000.

**ch22 (Observer survives).** "The three-way split" names delivery order, failure isolation and subscriber lifetime as what survives. This chapter witnesses each:
- **Order and isolation.**
  - Subscribers run in subscription order, and a duplicate is ignored.
  - One failing subscriber no longer stops the rest; the failures arrive afterwards as one `ExceptionGroup`.
  - A plain list stops at the first failure.
- **Lifetime.**
  - A plain list keeps an abandoned `TrackingHistory` alive and still calls it. `WeakMethod` drops it once its owner goes.
  - The trade-offs are each tested:
    - a subscriber nobody else holds is dropped;
    - a lambda is held strongly;
    - a lambda closing over its owner keeps the owner alive;
    - a slotted owner is refused at `subscribe`;
    - a reference cycle holds a subscriber until the collector runs.
- **Re-entrancy.**
  - A subscriber added during delivery gets the next event, and an unsubscribe during delivery skips no one.
  - An event published during delivery waits its turn, so every subscriber sees events in publication order. Immediate nested delivery reverses them (evidence L).
- **Types.**
  - mypy checks the subscriber's event type and the published event.
  - A string-topic bus with `Any` payloads accepts typos (reduced model).
  - mypy is silent on a slotted subscriber that will fail at run time.

## Approach

- **Thesis wording.**
  - ch21 says Composite and Flyweight survive.
    - Python removes the Component base class and the factory class.
    - The decisions remain. For Composite: what both kinds answer, where totals are computed, and which invariants hold. For Flyweight: who builds a shared value, how long it lives, and why immutability makes sharing safe.
    - `sys.intern` is the language's own flyweight for strings.
  - ch22 says Observer survives.
    - The Observer interface dissolves into a callable.
    - The contract doesn't: in what order subscribers are called, whether one failure stops the rest, what happens when a subscriber publishes or subscribes during delivery, and how long the signal keeps a subscriber alive.
- **Credit.**
  - GoF where each pattern is introduced, in plain paraphrase that doesn't track the Intent wording.
  - Rhodes's Composite and Flyweight pages in ch21. There's no Rhodes page for Observer, so ch22 doesn't claim one.
  - The `weakref`, `sys`, data-model and `functools` docs, quoted exactly from fetched pages.
- **Domain names** come from `_plans/shipping-domain-model.md` rows 21-22 plus the supporting names below, recorded in those rows at K0. There's no new domain area and no new carrier code.
  - Port codes are UN/LOCODEs (`NLRTM`, `SGSIN`, `DEHAM`, `CNSHA`).
  - HS codes (`850760` lithium-ion batteries, `090111` coffee, not roasted, `610910` cotton T-shirts) are illustrative, and the chapter says so once.
  - ch21 (Consignment, Routing): `ConsignmentId`, `Weight`, `Commodity`, `Consignment`, `ConsolidatedShipment`, `Shipment` (alias), `PortCall`, `consignments`, `carries_dangerous_goods`, `CommodityPool`, `CATALOGUE`, `port_code`, `route`, `ConsolidationError`, `UnknownCommodityError`, `PortCodeError`.
  - ch22 (Tracking): `ConsignmentId`, `HandlingKind`, `HandlingEvent` (one class with a `HandlingKind` enum; the chapter says so), `TrackingHistory`, `Signal`, `Subscriber` (alias), `Unsubscribe` (alias).
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/21-composite-and-flyweight` (project `composite-flyweight`, package `composite_flyweight`);
  - `examples/22-observer` (project `observer`, package `observer`).
- **mypy witnesses** copy the r09 `_run`/`_codes` helper with the anchored regex `re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)`.
  - Each asserts the exit status, an exact `_codes()` set and one or two stable substrings. It never asserts line numbers or optional notes.
  - Snippets import real `src` names wherever possible. Reduced models are named in the prose.
- **Comparison code** (the owner's 2026-11-04 rule). Every comparison form is real, runs on the shared table **as a conftest fixture param**, and appears in at most one excerpt per chapter. The idiomatic code is the lesson.
  - ch21:
    - `tree_form` `frozen-union|component-classes` (`_Component`, `_ComponentLeaf`, `_ComponentGroup`);
    - `pool_form` `weak-pool|cache` (a fresh `functools.cache` over the catalogue built inside the fixture, so no cache outlives a test);
    - `_flat_weight`, which fails the table on purpose and has its own test.
  - ch22: `signal_form` `signal|plain-list` (`_ListSignal`). Its hazards have their own tests because they fail the table on purpose.
  - All of them live in `tests/conftest.py`, because sibling test imports are blocked under `--import-mode=importlib`.
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (K1a, K1b) name the test and say why it sees the deletion. A row whose witness was predicted, not run, is marked "executor check".
- **Determinism and garbage collection.**
  - No `mock`, `mocker`, `monkeypatch`, `print(`, `sleep` or wall clock.
  - Every lifetime test drops its names with `del` (or builds the subscriber in a helper so no local survives), then calls `gc.collect()` deliberately before asserting. A comment says why: CPython usually frees an object at its last reference, but the language promises nothing (data model, quoted), and a reference cycle waits for the collector.
  - The cycle test uses a `collector_paused` fixture: it records `gc.isenabled()`, calls `gc.disable()`, yields, and re-enables only if it was enabled. Automatic collection therefore can't run between "still alive" and `gc.collect()`.
  - No test asserts that an object is gone *before* `gc.collect()`.
  - No test compares to a string literal with `is` (evidence F's `SyntaxWarning` would become an error).
  - Registries are `frozendict` typed as `Mapping`. Pools and signals are instances created per test, with no module-level instance.
  - `filterwarnings = ["error"]` stays active.
- **Memory figures** come only from `examples/21-composite-and-flyweight/bench/commodity_memory.py`, which uses `tracemalloc` and the `getsizeof` comparison. Its scrubbed output is recorded in `_plans/evidence/flyweight-memory.md` with the Python version and date. Tests assert structure only (`is`, `__slots__`, no `__dict__`), never bytes. The script is type-checked by `uv run mypy --strict src tests bench` in K1a; ruff already covers it.
- **Counts** of test functions and cases come from the code, and the pytest summary line wins (r07, r08 and r09 all differed from plan arithmetic).

Rejected:
- An `abc.ABC` Component in `src` (decision 2).
- Overriding `__new__` to cache flyweights (Rhodes's own advice against it; a call that looks like construction returns a shared object).
- A generator traversal of the tree (the Iterator chapter's ground).
- A global or module-level signal or pool.
- A thread-safe signal (decision 5).
- Any assertion on bytes, timing or `id()` values.
- `typing.cast` or `Any` in `src`.
- A third-party event library.

## Per-chapter spec

### ch21: Composite and Flyweight (pattern, has_example = true, bucket: survives)

Thesis:
- Composite's force is a caller that must treat one consignment and a consolidation of them the same way.
  - Python removes the Component base class: a closed union with one shared attribute, `match` where the kinds differ.
  - The design is what survives: the shared question, where the total is computed, and the invariants a tree keeps.
- Flyweight's force is many references to equal immutable values.
  - Python gives a factory function, a weak pool, `functools.cache` and `sys.intern`.
  - What survives is deciding identity and lifetime, and making the shared value immutable so sharing can't be observed except through memory.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one of them from a comparison fixture):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - a total that sums direct consignments and misses a nested consolidation (test 2: 17.25 against 23.75 kg);
   - a consignment counted twice because it sits in two groups (test 7);
   - a mutable commodity shared by every consignment, changed through one of them (test 20).
3. Figure plus one paragraph (~60).
4. `## One question for a consignment and a consolidation` (~450). Excerpt `ConsolidatedShipment` and `Shipment`:
   - GoF credited for Composite in paraphrase; Rhodes's "The Composite Pattern" credited for symmetry by any means. Bucket: survives. One sentence pointing to "What 1994 assumed, and what Python dissolves".
   - Both kinds answer `.weight` (test 3), and the total includes nested groups (test 1, both forms). The flat sum misses them (test 2).
   - mypy reads `.weight` on the union (test 26) and refuses `.parts` on it (test 27).
5. `## Where the kinds differ: match over a closed union` (~300). Excerpt `consignments`:
   - Flattening lists every consignment in order (test 4). Dangerous goods anywhere are flagged (test 5).
   - A missing arm is a mypy error at `assert_never` (test 28). One sentence pointing to "Protocol, duck typing, and structural typing with mypy" for a Protocol alternative when the set of kinds is open.
6. `## Invariants: built bottom-up, frozen, counted once` (~400):
   - A consolidation needs parts (test 6), and a consignment appears once (test 7). The tree can't be rewired (test 8; mypy, test 30). It compares by value (test 11). One sentence pointing to "Dataclasses and value semantics" for frozen and hashing.
   - [GoF's transparency against safety, if verified]: the component fixture accepts `leaf.add` under mypy (test 31) and refuses it only when the program runs (test 9). Its group can contain itself (test 10). At most one short excerpt of `_ComponentLeaf.add`.
   - One sentence: a pathologically deep tree hits the recursion limit (test 12), and the domain nests a few levels.
7. `## Flyweight: one commodity, many consignments` (~550). Excerpt `CommodityPool`:
   - GoF credited for Flyweight in paraphrase; Rhodes's "The Flyweight Pattern" for the factory function and the weak dictionary. Intrinsic state (the commodity) against extrinsic state (each consignment's weight and ports).
   - The pool returns one object per code (test 14, both forms) and refuses an unknown code (test 15).
   - Lifetime: the weak pool drops a commodity nobody holds (test 16, with `gc.collect()` explained), and the cache keeps all (test 17). Quote the `WeakValueDictionary` and `functools` sentences.
   - Pool values need a weak-reference slot (test 18): one sentence pointing to "Dataclasses and value semantics", and quote the `weakref` `__slots__` sentence.
   - Equal commodities needn't be the same object (test 19), which is why sharing is safe. A mutable shared value isn't (test 20).
   - The pool is single-threaded. One sentence pointing to "Singleton: module, Borg, and metaclass" for the race on a cache.
8. `## Memory: slots trim, sharing removes, interning for strings` (~300):
   - `getsizeof` against `tracemalloc` (`run:` evidence file; quote the `getsizeof` docs sentence). Slotted commodities have no `__dict__` (test 21). Quote the data-model slots sentence.
   - Port codes: equal and distinct after a split (test 22), and one object after `sys.intern` (test 23). Quote the `sys.intern` entry. A malformed code is refused (test 24).
   - Say plainly that equality works without interning; interning only saves memory and lookups.
9. `## When not to use it` (~180):
   - a flat list of consignments that never nests (a tuple and `sum`);
   - a tree where leaves and groups share no question (two types, no union);
   - a handful of commodities (no pool);
   - mutable values (never share them);
   - an `is` check on codes (compare with `==`).

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written trees and flyweights.** An assistant asked for "a composite" may write a `Component` base class with `add` and `remove` on every leaf, a group that sums only its direct children, a mutable list of children anyone can append to, or a flyweight factory that caches in `__new__` and never lets go. Check: do leaf and group answer the same question without `isinstance`; does the total recurse; can a group be empty, contain itself or count a consignment twice; are shared values frozen; does the pool's lifetime match how long the values are needed; does any code compare codes with `is`.</blockquote>

   Each check maps to tests 3, 1-2, 6-10, 19-20, 16-17 and 22-23.
10. `## Build, run, observe` (~220 plus output). Each experiment runs in a fresh scratch copy (delete the copy's `.venv`, re-sync, and confirm `composite_flyweight.__file__` points into the copy), with one change, reverted. Run `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'`, then `uv run mypy --strict src tests`, three times:
    - (a) Delete the duplicate check in `ConsolidatedShipment.__post_init__`. Expected: test 7 (both params) fails with `DID NOT RAISE`; mypy exits 0. Executor check: whether any other test fails. Quote as observed.
    - (b) Remove `weakref_slot=True` from `Commodity`. Expected: tests 14[weak-pool], 15[weak-pool] (executor check: 15 raises before the lookup only if the code exists) and 16 fail with `TypeError: cannot create weak reference to 'Commodity' object`. Test 21 may fail if it asserts `__weakref__` in the slots. mypy exits 0. Quote as observed.
11. `## For deeper coverage` (~130): GoF (Composite, Flyweight); Rhodes, both pages; the `weakref` docs; `sys.intern`; the data model on `__slots__`; [Ramalho, *Fluent Python* 2nd ed., on `__slots__` and weak references, chapter titles only if verified]; the bibliography link.

Figure `21-composite-and-flyweight` (vertical):
- Top accent box `ConsolidatedShipment`, "weight: sums every part, nested or not".
- It branches to `Consignment` boxes and a nested `ConsolidatedShipment` with its own `Consignment` boxes. The label is "Shipment = Consignment | ConsolidatedShipment".
- Every `Consignment` has an arrow to one shared `Commodity` box below, "one object per code, frozen".
- That box hangs from `CommodityPool`, "weak values: dropped when nobody holds them".
- A side box: "port codes: sys.intern, one object per code".
- No numbers in the SVG.

Caption draft (36 words with prefix): "Figure 21.1: A consolidation answers the same question as a consignment. Its weight recurses through nested groups, while every consignment points to one shared, frozen commodity from a pool that lets go of commodities nobody holds."

### ch22: Observer (pattern, has_example = true, bucket: survives)

Thesis:
- Observer's force is a subject that must tell an open set of parties about changes without knowing them.
  - Python removes the Observer interface: a subscriber is any callable that takes the event, and mypy checks its type.
- The pattern survives because a list of callables decides nothing about four things, and each one breaks:
  - the order subscribers run in;
  - whether one failure stops the rest;
  - what happens when a subscriber subscribes, unsubscribes or publishes during delivery;
  - how long the subject keeps a subscriber alive.
- `Signal` writes each decision down and tests it.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one from the plain-list fixture):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - a tracking store that raises and stops every later subscriber (test 5);
   - a `TrackingHistory` the application dropped, still alive and still being called (test 8);
   - a subscriber that publishes during delivery, so a later subscriber records `DELIVERED` before `CLEARED` (test 20).
3. Figure plus one paragraph (~60).
4. `## A subscriber is a callable` (~300):
   - GoF credited for Observer in paraphrase. [Other names, if verified.] Bucket: survives. One sentence pointing to "The three-way split: dissolve, survive, disambiguate".
   - `type Subscriber[E] = Callable[[E], None]`. mypy refuses a subscriber for another event type (test 22) and a wrong event (test 23). One sentence pointing to "Protocol, duck typing, and structural typing with mypy" for callback Protocols.
   - A string-topic bus with `Any` payloads accepts a typo and a wrong payload (test 24, reduced model).
   - `HandlingEvent` is one class with a `HandlingKind` enum here; say so.
5. `## Order and failure` (~450). Excerpt `Signal.publish`:
   - Subscribers run in subscription order (test 1, both forms). An unsubscribe stops delivery (test 2, both forms), and subscribing twice delivers once (test 3).
   - One failure doesn't stop the rest (test 4), every failure is reported after delivery as one `ExceptionGroup` (test 6), and the plain list stops (test 5).
   - The signal recovers after a failed delivery (test 21). `TrackingHistory` records events in order (test 7).
6. `## How long a subscriber lives` (~550). Excerpt `Signal.subscribe`:
   - The plain list keeps an abandoned subscriber alive (test 8). `WeakMethod` drops it when its owner goes (test 9). Quote the `WeakMethod` and opening `weakref` sentences, and explain `gc.collect()` in the tests (quote the data-model finalisation sentence).
   - Trade-offs:
     - a subscriber nobody else holds is dropped (test 10);
     - lambdas are held strongly, because a weak reference to one dies at once (test 11);
     - a lambda that closes over its owner keeps the owner alive (test 12);
     - a slotted owner without a weak-reference slot is refused at `subscribe` (test 13), and mypy can't see it (test 25), with one sentence pointing to "Dataclasses and value semantics";
     - a reference cycle keeps a subscriber until the collector runs (test 14).
   - Unsubscribing after the owner has gone is harmless (test 15).
   - One sentence: `inspect.ismethod` narrows to `types.MethodType` for mypy, so the weak branch is checked at `subscribe`, not after it (evidence M, recorded).
7. `## Subscribing and publishing during delivery` (~350):
   - Delivery iterates a snapshot. A subscriber added during delivery gets the next event (test 16), and an unsubscribe during delivery skips no one (test 17). The plain list skips one (test 18).
   - A nested publish is queued and delivered after the current event (test 19). Immediate delivery reverses the order (test 20).
   - One sentence: `Signal` assumes one thread; delivery on another thread or an event loop is out of scope here. No pointer to the stubs' content.
8. `## When not to use it` (~180):
   - a fixed set of parties known when the subject is built (call them directly, or hold a tuple of callables);
   - one subscriber (pass a callable);
   - parties that must coordinate replies (a mediator decides; name the pattern without a chapter claim);
   - delivery that must survive a crash (a durable queue, not an in-memory signal).

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written observers.** An assistant asked for "an event system" may write an `Observer` base class with `update`, a global bus keyed by strings with `Any` payloads, a list of callbacks iterated while it changes, a loop that stops at the first exception, or a registry that holds every bound method forever. Check: is a subscriber a typed callable; does one failure reach the caller without stopping the rest; is delivery over a snapshot; are nested events queued; does the signal keep an abandoned subscriber alive, and does any lambda close over one.</blockquote>

   Each check maps to tests 22 and 24, 4-6, 16-18, 19-20 and 8-12.
9. `## Build, run, observe` (~220 plus output). Same scratch-copy rules, the same filter, then mypy, three times:
   - (a) In `publish`, iterate `self._subscribers.values()` instead of a `tuple` snapshot. Expected: test 16 fails with `RuntimeError: dictionary changed size during iteration` (evidence L). Tests 17 and 15 may also fail (executor check). mypy exits 0. Quote as observed.
   - (b) In `subscribe`, hold every subscriber strongly (drop the `WeakMethod` branch). Expected: tests 9, 10 and 14 fail on the subscriber count, and test 13 fails with `DID NOT RAISE`. mypy exits 0. Quote as observed.
10. `## For deeper coverage` (~130): GoF (Observer); the `weakref` docs; the data model on object lifetime; PEP 654 (exception groups); PEP 695; [Ramalho, *Fluent Python* 2nd ed., on weak references, if verified]; the bibliography link.

Figure `22-observer` (vertical):
- Top accent box `Signal.publish(event)`, "queued: nested events wait their turn".
- Below it, a snapshot box "subscribers, in subscription order".
- It fans out to three subscriber boxes: `TrackingHistory.record` ("bound method: held through WeakMethod"), `lambda` ("held strongly") and a failing subscriber ("error collected, delivery continues").
- They converge on a bottom box `ExceptionGroup`, "raised after every subscriber has run".
- A muted side box: "plain list: stops at a failure, keeps every subscriber alive".
- No numbers in the SVG.

Caption draft (37 words with prefix): "Figure 22.1: What a signal decides. Each event reaches every subscriber in order from a snapshot, nested events wait their turn, failures are gathered and raised afterwards, and bound methods are held weakly so abandoned subscribers can go."

Citations, both chapters: verify each before writing, apply the bracketed fallbacks, quote no sentence unless it was checked on a fetched page, and make no comparison between languages.

## Example spec

### `examples/21-composite-and-flyweight` (project `composite-flyweight`, package `composite_flyweight`)

`pyproject.toml` in the r09 shape (`requires-python = ">=3.15"`, no `[tool.*]`).

- `domain.py`:
  - `ConsignmentId = NewType("ConsignmentId", str)`.
  - `Weight(kilograms: Decimal)`, frozen slotted: finite and positive, else `ValueError`; `__add__`.
  - `Commodity(hs_code: str, description: str, dangerous_goods: bool)`, `@dataclass(frozen=True, slots=True, weakref_slot=True)`.
  - `PortCall(port: str, sequence: int)`, frozen slotted.
  - `Consignment(id, weight, commodity, origin: str, destination: str)`, frozen slotted kw_only.
  - `ConsolidatedShipment(id: str, parts: tuple[Shipment, ...])`, frozen slotted:
    - `__post_init__` raises `ConsolidationError` for empty `parts`, and for any `ConsignmentId` appearing twice anywhere beneath (by flattening);
    - a `weight` property sums `part.weight` over `parts`.
  - `type Shipment = Consignment | ConsolidatedShipment`.
  - `ConsolidationError(ValueError)`.
- `consolidation.py`:
  - `consignments(shipment: Shipment) -> tuple[Consignment, ...]`, using `match` and `assert_never`, in depth-first order;
  - `carries_dangerous_goods(shipment: Shipment) -> bool`.
- `flyweights.py`:
  - `CATALOGUE: Mapping[str, tuple[str, bool]] = frozendict({...})`, three illustrative HS codes.
  - `UnknownCommodityError(LookupError)`.
  - `CommodityPool(catalogue: Mapping[str, tuple[str, bool]] = CATALOGUE)`:
    - `_pool: weakref.WeakValueDictionary[str, Commodity]`;
    - `get(self, hs_code: str, /) -> Commodity` (EAFP on the pool; an unknown code raises `UnknownCommodityError(f"unknown commodity {hs_code!r}")` from None);
    - `__len__`.
  - `PortCodeError(ValueError)`.
  - `port_code(text: str) -> str` validates `[A-Z]{2}[A-Z2-9]{3}` with `fullmatch` and returns `sys.intern(text)`.
  - `route(line: str) -> tuple[PortCall, ...]` splits on `;` and numbers the calls from 1.
- `py.typed`, `__init__.py`.
- `bench/commodity_memory.py`: evidence E's `getsizeof` and `tracemalloc` comparisons (dict-backed, slotted, slotted with weakref slot, shared; plain against interned port codes). It prints a table with the Python version. It isn't collected by pytest (the name has no `test_` prefix, and `testpaths` covers `examples`; the executor confirms it isn't collected).

`tests/conftest.py`:
- `pool` (a fresh `CommodityPool`).
- `nested` (evidence D's tree: CN-1 10 kg, a nested group of CN-3 2.5 kg and CN-4 4 kg, then CN-2 7.25 kg, with one commodity dangerous inside the nested group).
- `tree_form` params `frozen-union|component-classes`, giving a callable that returns the total weight of the `nested` structure as built in that form. Fixture classes: `_Component(ABC)` with abstract `weight()` and an `add` that raises `TypeError`, `_ComponentLeaf`, and `_ComponentGroup` with a list.
- `pool_form` params `weak-pool|cache`, giving `Callable[[str], Commodity]`. The cache form wraps a fresh closure in `functools.cache` per test and raises the same `UnknownCommodityError`.
- `_flat_weight(group)`.
- `collector_paused` isn't needed here.

`test_composite.py`:
1. `test_the_total_weight_includes_nested_consolidations` x `tree_form` (2): 23.75 kg.
2. `test_a_flat_sum_misses_nested_consolidations`: 17.25 against 23.75.
3. `test_a_consignment_and_a_consolidation_answer_weight_the_same_way[consignment|consolidation]` (2): one function over `Shipment` reads `.weight` with no `isinstance`.
4. `test_consignments_lists_every_leaf_in_order`: CN-1, CN-3, CN-4, CN-2.
5. `test_a_consolidation_with_dangerous_goods_anywhere_is_flagged[top-level|nested|none]` (3).
6. `test_a_consolidation_must_have_parts`.
7. `test_a_consignment_may_appear_only_once_in_a_consolidation[same-level|nested]` (2).
8. `test_a_frozen_consolidation_cannot_be_rewired`: `FrozenInstanceError`; `parts` is a `tuple`.
9. `test_a_component_leaf_refuses_add_only_when_the_program_runs`: `TypeError`.
10. `test_a_mutable_component_group_can_contain_itself`: `group.add(group)` succeeds; `weight()` raises `RecursionError`.
11. `test_consolidations_compare_by_value`: two separately built equal trees are equal and hash equal.
12. `test_a_pathologically_deep_consolidation_hits_the_recursion_limit`: 5,000 levels, `RecursionError` on `.weight`.
13. `test_weight_refuses_zero_negative_and_non_finite_values[zero|negative|nan|infinity]` (4).

`test_flyweight.py`:
14. `test_the_pool_returns_one_commodity_per_code` x `pool_form` (2): `is` for the same code and `is not` for different codes.
15. `test_an_unknown_commodity_code_is_refused` x `pool_form` (2): matching `unknown commodity '999999'`.
16. `test_the_weak_pool_drops_a_commodity_nobody_holds`: `len(pool) == 1`, then `del` and `gc.collect()` give 0. A new `get` is equal and is a new object (compared through a kept `id` only where the first object is still referenced; the executor uses `weakref.ref` instead of `id`).
17. `test_a_cache_keeps_every_commodity_it_has_made`: after `del` and `gc.collect()`, a `weakref.ref` to the first result is still alive.
18. `test_a_pool_needs_commodities_that_accept_weak_references`: a test-local `@dataclass(frozen=True, slots=True)` value put into a `WeakValueDictionary` raises `TypeError` matching `cannot create weak reference`.
19. `test_equal_commodities_need_not_be_the_same_object`: `==`, equal hashes, `is not`, and a set of both has length 1.
20. `test_a_shared_mutable_commodity_changes_every_consignment`: a test-local mutable dataclass shared by two lines; a change through one is seen through the other; the frozen `Commodity` raises `FrozenInstanceError`.
21. `test_commodities_have_no_instance_dict`: `not hasattr(c, "__dict__")`, and `"__weakref__" in Commodity.__slots__`.
22. `test_split_port_codes_are_equal_but_distinct_objects`: `"NLRTM;SGSIN;NLRTM".split(";")`, with items 0 and 2 `==` and `is not` (CPython 3.15.2 behaviour, stated in the docstring).
23. `test_interned_port_codes_are_one_object`: `route("NLRTM;SGSIN;NLRTM")`, with ports 1 and 3 `is` the same object.
24. `test_a_malformed_port_code_is_refused[lowercase|too-short]` (2).
25. `test_the_commodity_catalogue_is_read_only`: `# type: ignore[index]`; `TypeError` matching `does not support item assignment`.

`test_static.py`:
26. `test_mypy_reads_weight_on_either_kind_of_shipment`: imports `src`; exit 0, empty.
27. `test_mypy_refuses_parts_on_a_shipment_that_may_be_a_consignment`: imports `src`; `{"union-attr"}`, `has no attribute "parts"`.
28. `test_mypy_reports_a_missing_match_arm`: imports `src`; `{"arg-type"}`, `expected "Never"`.
29. `test_mypy_refuses_a_part_that_is_not_a_shipment`: imports `src`; `{"arg-type"}`.
30. `test_mypy_refuses_adding_to_a_frozen_consolidation[add|append|assign]` (3): imports `src`. Expected codes are `{"attr-defined"}`, `{"attr-defined"}` and `{"misc"}` with `is read-only`.
31. `test_mypy_accepts_add_on_a_component_leaf`: reduced model (evidence C); exit 0, empty.

Numbers are spec ids, not file order. The plan has 31 test functions and 44 cases:
- `test_composite.py`: 13 functions, 21 cases (1: 2; 2: 1; 3: 2; 4: 1; 5: 3; 6: 1; 7: 2; 8-12: 5; 13: 4);
- `test_flyweight.py`: 12 functions, 15 cases (14: 2; 15: 2; 16-23: 8; 24: 2; 25: 1);
- `test_static.py`: 6 functions, 8 cases.

The executor counts from the pytest summary line and reports that number.

K1a also writes `_plans/evidence/flyweight-memory.md`: the bench script's output from a fresh run, scrubbed with `host_ids.py filter`, plus the Python and mypy versions and the date. The chapter quotes this file only.

Also `README.md` and the card `_examples/21-composite-and-flyweight.md` (`order: 21`, eyebrow "Structure · Composite and Flyweight"). No `mock`, `monkeypatch`, `print(` (except in `bench/`), `Optional`, `abc`/`ABC`, `Any`, `cast`, `float` or `__new__` in `src/`.

Deletion table (K1a):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `Weight` finite and positive | `__post_init__` removed | 13[all] | no `ValueError` |
| recursive `weight` | sums only `Consignment` parts | 1[frozen-union], 3[consolidation] | the total is 17.25 |
| non-empty `parts` | check removed | 6 | no `ConsolidationError` |
| consignment once | check removed | 7[all] | no `ConsolidationError` (experiment a) |
| `match` arm for groups in `consignments` | arm removed | 4, 5[nested], member mypy | nested consignments missing; `assert_never` `[arg-type]` |
| `carries_dangerous_goods` | checks top level only | 5[nested] | returns `False` |
| `frozen` on `ConsolidatedShipment` | `frozen=False` | 8, 11, member mypy (test 30[assign] snippet) | assignment succeeds; unhashable |
| pool reuses entries | always builds | 14[weak-pool] | `is` fails |
| weak values in the pool | plain `dict` | 16 | length stays 1 after `gc.collect()` |
| `weakref_slot=True` | removed | 14[weak-pool], 16, 21 (executor names exactly which) | `TypeError` (experiment b) |
| `slots=True` | removed | 21 | `__dict__` present |
| unknown code | `KeyError` let through | 15[weak-pool] | not `UnknownCommodityError` |
| `sys.intern` in `port_code` | returns `text` | 23 | ports 1 and 3 aren't the same object |
| port code pattern | check removed | 24[all] | no `PortCodeError` |
| `frozendict` catalogue | `dict` | 25 | assignment succeeds |

### `examples/22-observer` (project `observer`, package `observer`)

- `domain.py`:
  - `ConsignmentId`.
  - `HandlingKind(Enum)`: `BOOKED`, `LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED`.
  - `HandlingEvent(consignment_id, kind, port: str)`, frozen slotted.
- `signal.py`, in evidence M's shape:
  - `type Subscriber[E] = Callable[[E], None]` and `type Unsubscribe = Callable[[], None]`.
  - `class Signal[E]` with:
    - `_subscribers: dict[object, Callable[[], Subscriber[E] | None]]`, `_pending: deque[E]` and `_delivering: bool`;
    - `subscribe(self, subscriber: Subscriber[E], /) -> Unsubscribe`. If `inspect.ismethod`, the key and reference are `weakref.WeakMethod(subscriber, self._forget)`; otherwise the key is the subscriber and the reference is a strong getter from a small `_strong` helper (no lambda assignment, ruff E731). It uses `setdefault`, so a duplicate is ignored, and returns an `unsubscribe` closure;
    - `_forget(self, key: object) -> None`, which is `pop(key, None)`;
    - `publish(self, event: E, /) -> None`: append; return if delivering; otherwise drain the queue over a `tuple` snapshot per event, collecting `Exception`s, with `finally` resetting `_delivering`; then raise `ExceptionGroup("subscribers failed", errors)` if there were any;
    - `__len__`, which counts live references.
- `tracking.py`: `TrackingHistory`, a plain class (an entity, weakly referenceable) with `record(self, event: HandlingEvent, /) -> None` and an `events` property returning a tuple.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `event(kind)` helper, consignment `CN-1`, port `NLRTM`.
- `signal_form` params `signal|plain-list`, giving a fresh `Signal[HandlingEvent]` or `_ListSignal` (a `list` of callables, `subscribe` appends and returns a remover, `publish` iterates the live list with no `try`).
- `collector_paused` (see Approach).
- `Recorder` (a test-local subscriber class with `record`).

`test_delivery.py`:
1. `test_subscribers_are_called_in_subscription_order` x `signal_form` (2).
2. `test_an_unsubscribed_subscriber_gets_no_more_events` x `signal_form` (2).
3. `test_subscribing_twice_delivers_once`.
4. `test_one_failing_subscriber_does_not_stop_the_rest`: the later subscriber receives the event; `ExceptionGroup` with one `RuntimeError`.
5. `test_a_plain_list_stops_at_the_first_failing_subscriber`.
6. `test_every_failure_is_reported_after_delivery[one|two]` (2): `.exceptions` matches the raised errors in order.
7. `test_tracking_history_records_events_in_order`.

`test_lifetime.py` (every test drops its names and calls `gc.collect()` before asserting):
8. `test_a_plain_list_keeps_an_abandoned_subscriber_alive`: `weakref.ref(history)()` is alive and is still called.
9. `test_a_bound_method_subscriber_is_dropped_when_its_owner_goes`: `len(signal) == 0`; publishing reaches no one.
10. `test_a_subscriber_nobody_else_holds_is_dropped`: `signal.subscribe(TrackingHistory().record)`.
11. `test_a_lambda_subscriber_is_held_strongly`.
12. `test_a_lambda_that_closes_over_its_owner_keeps_it_alive`.
13. `test_a_slotted_subscriber_without_a_weakref_slot_is_refused`: `TypeError` matching `cannot create weak reference`, at `subscribe`.
14. `test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs`: uses `collector_paused`; alive after `del`, gone after `gc.collect()`.
15. `test_unsubscribe_is_safe_after_the_owner_has_gone`.

`test_reentrancy.py`:
16. `test_a_subscriber_added_during_delivery_gets_the_next_event`.
17. `test_unsubscribing_during_delivery_does_not_skip_another_subscriber`.
18. `test_a_plain_list_skips_a_subscriber_when_one_unsubscribes_during_delivery`.
19. `test_an_event_published_during_delivery_waits_its_turn`: a test-local releaser publishes `DELIVERED` on `CLEARED`; the history records `CLEARED` then `DELIVERED`.
20. `test_an_immediately_delivered_nested_event_arrives_out_of_order`: the plain list's history records `DELIVERED` then `CLEARED`.
21. `test_the_signal_accepts_new_events_after_a_failed_delivery`.

`test_static.py`:
22. `test_mypy_refuses_a_subscriber_for_another_event_type`: imports `src`; `{"arg-type"}`, `expected "Callable[[HandlingEvent], None]"`.
23. `test_mypy_refuses_publishing_the_wrong_event`: imports `src`; `{"arg-type"}`.
24. `test_mypy_accepts_a_typo_in_a_string_topic_bus[typo-topic|wrong-payload]` (2): reduced model (evidence N); exit 0, empty.
25. `test_mypy_cannot_see_a_subscriber_that_refuses_weak_references`: imports `src`; a test-local slotted class's method passed to `subscribe`; exit 0, empty.

The plan has 25 test functions and 29 cases:
- `test_delivery.py`: 7 functions, 10 cases;
- `test_lifetime.py`: 8 functions, 8 cases;
- `test_reentrancy.py`: 6 functions, 6 cases;
- `test_static.py`: 4 functions, 5 cases.

The executor counts from the pytest summary line.

Also `README.md` and the card (`order: 22`, eyebrow "Coordination · Observer"). No `mock`, `monkeypatch`, `print(`, `Optional`, `Any`, `cast`, `sleep`, `threading` or `asyncio` in `src/`.

Deletion table (K1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| duplicate ignored | `self._subscribers[key] = ...` with a fresh key per call | 3 | delivered twice (executor check: a `WeakMethod` key is equal for the same method, so the executor forces a distinct key) |
| failure isolation | `try`/`except` removed | 4, 6[all] | delivery stops; a bare `RuntimeError` |
| `ExceptionGroup` raised | errors dropped | 4, 6[all] | `DID NOT RAISE` |
| `finally` resets `_delivering` | plain assignment after the loop | 21 | the next publish is queued forever |
| snapshot | live `values()` | 16 (experiment a) | `RuntimeError: dictionary changed size during iteration` |
| queued nested publish | delivered immediately | 19 | history order reversed |
| `WeakMethod` for bound methods | strong for all | 9, 10, 14, 13 (experiment b) | subscriber stays; no `TypeError` |
| `WeakMethod` callback removes the entry | callback dropped | 9 (via `len`), executor check | dead entry counted (`__len__` counts live references; the executor confirms which test sees it) |
| `_forget` tolerates a missing key | `del self._subscribers[key]` | 15 | `KeyError` |
| unsubscribe | returns a no-op | 2[signal] | still delivered |

## Steps and status

Step ids are `K*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| K0 | This plan file. PDP-121a-c and 122a-c `active` in `iteration-plan.md` (dated note). Reconciliation rows 107-119 `open` with a dated r10 note. Domain rows 21-22 updated with the supporting names and decisions 1-5. ch21-22 stub `description` lines written. r09's J7 (and r08's I6 and I7 if still `todo`) closed. Decisions recorded | - | done |
| K1a | ch21 member, card, README, `bench/commodity_memory.py`, `_plans/evidence/flyweight-memory.md`; one `uv lock`; three green runs; `mypy --strict src tests bench`; the deletion table, each row in a fresh scratch copy with its `.venv` removed and re-synced (confirm `__file__`) | K0 | done |
| K1b | ch22 member, card, README; one `uv lock` after K1a (sequenced); three green runs; deletion table | K1a | todo |
| K2 | Witness results into rows 107-119 (the claims audit resolves). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | K1b | todo |
| K3 | Two figures, specs `diagrams/specs/21-*.py` and `22-*.py`, `_data/diagrams.yml` (single owner; 23 entries); figures 00-20 unchanged; every name drawn exists in `src` | K2 | todo |
| K4 | ch21-22 `status = "drafted"` (`kind` stays `pattern`) | K3 | todo |
| K5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly, runs its two experiments in scratch copies, quotes fresh output filtered by `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table (claim, then test, run or source URL) | K3, K4 | todo |
| K6 | Opus validation; up to two repair rounds | K5 | todo |
| K7 | PR, `ci-ok` green, ask the user before merge; tag r10.x; notes-only release | K6 | todo |

Reconciliation rows (step K0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 107 | 21 | A consignment and a consolidation answer `weight` the same way; the total includes nested groups in both the frozen and the component forms; a flat sum misses them; mypy reads `weight` on the union and refuses `parts` on it | `test_the_total_weight_includes_nested_consolidations`, `test_a_flat_sum_misses_nested_consolidations`, `test_a_consignment_and_a_consolidation_answer_weight_the_same_way`, `test_mypy_reads_weight_on_either_kind_of_shipment`, `test_mypy_refuses_parts_on_a_shipment_that_may_be_a_consignment` |
| 108 | 21 | Flattening over a closed union lists every consignment in order and finds dangerous goods anywhere; a missing `match` arm and a wrong part type are mypy errors | `test_consignments_lists_every_leaf_in_order`, `test_a_consolidation_with_dangerous_goods_anywhere_is_flagged`, `test_mypy_reports_a_missing_match_arm`, `test_mypy_refuses_a_part_that_is_not_a_shipment` |
| 109 | 21 | A consolidation needs parts, counts each consignment once, can't be rewired and compares by value; a pathologically deep tree hits the recursion limit; weights are positive and finite | `test_a_consolidation_must_have_parts`, `test_a_consignment_may_appear_only_once_in_a_consolidation`, `test_a_frozen_consolidation_cannot_be_rewired`, `test_mypy_refuses_adding_to_a_frozen_consolidation`, `test_consolidations_compare_by_value`, `test_a_pathologically_deep_consolidation_hits_the_recursion_limit`, `test_weight_refuses_zero_negative_and_non_finite_values` |
| 110 | 21 | The GoF component form passes the weight table, but mypy accepts `add` on a leaf, which fails only when the program runs, and a mutable group can contain itself | `test_mypy_accepts_add_on_a_component_leaf`, `test_a_component_leaf_refuses_add_only_when_the_program_runs`, `test_a_mutable_component_group_can_contain_itself` |
| 111 | 21 | A pool returns one commodity per code and refuses an unknown one; a weak pool drops a commodity nobody holds and a cache keeps all; pool values need a weak-reference slot | `test_the_pool_returns_one_commodity_per_code`, `test_an_unknown_commodity_code_is_refused`, `test_the_weak_pool_drops_a_commodity_nobody_holds`, `test_a_cache_keeps_every_commodity_it_has_made`, `test_a_pool_needs_commodities_that_accept_weak_references`, `source: https://docs.python.org/3/library/weakref.html` |
| 112 | 21 | Frozen equality makes sharing safe (equal needn't be identical); a shared mutable value changes every holder; slotted commodities have no instance dict; the catalogue is read-only | `test_equal_commodities_need_not_be_the_same_object`, `test_a_shared_mutable_commodity_changes_every_consignment`, `test_commodities_have_no_instance_dict`, `test_the_commodity_catalogue_is_read_only`, `source: https://docs.python.org/3/reference/datamodel.html` |
| 113 | 21 | Split port codes are equal but distinct objects; interned codes are one object; malformed codes are refused; memory figures for slots, sharing and interning are as recorded (approximate, 3.15.2) | `test_split_port_codes_are_equal_but_distinct_objects`, `test_interned_port_codes_are_one_object`, `test_a_malformed_port_code_is_refused`, `source: https://docs.python.org/3/library/sys.html`, `run: _plans/evidence/flyweight-memory.md` |
| 114 | 22 | Subscribers run in subscription order, a duplicate is delivered once, an unsubscribe stops delivery, and the history records in order; mypy checks subscriber and event types; a string-topic bus accepts typos | `test_subscribers_are_called_in_subscription_order`, `test_subscribing_twice_delivers_once`, `test_an_unsubscribed_subscriber_gets_no_more_events`, `test_tracking_history_records_events_in_order`, `test_mypy_refuses_a_subscriber_for_another_event_type`, `test_mypy_refuses_publishing_the_wrong_event`, `test_mypy_accepts_a_typo_in_a_string_topic_bus` |
| 115 | 22 | One failing subscriber doesn't stop the rest; every failure arrives afterwards as one `ExceptionGroup`; the signal recovers; a plain list stops at the first failure | `test_one_failing_subscriber_does_not_stop_the_rest`, `test_every_failure_is_reported_after_delivery`, `test_the_signal_accepts_new_events_after_a_failed_delivery`, `test_a_plain_list_stops_at_the_first_failing_subscriber`, `source: https://peps.python.org/pep-0654/` |
| 116 | 22 | A plain list keeps an abandoned subscriber alive; `WeakMethod` drops it; a subscriber nobody holds is dropped; lambdas are strong and a closing lambda keeps its owner; a slotted owner is refused at run time and mypy can't see it; a cycle waits for the collector; unsubscribe after the owner has gone is safe | `test_a_plain_list_keeps_an_abandoned_subscriber_alive`, `test_a_bound_method_subscriber_is_dropped_when_its_owner_goes`, `test_a_subscriber_nobody_else_holds_is_dropped`, `test_a_lambda_subscriber_is_held_strongly`, `test_a_lambda_that_closes_over_its_owner_keeps_it_alive`, `test_a_slotted_subscriber_without_a_weakref_slot_is_refused`, `test_mypy_cannot_see_a_subscriber_that_refuses_weak_references`, `test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs`, `test_unsubscribe_is_safe_after_the_owner_has_gone`, `source: https://docs.python.org/3/library/weakref.html` |
| 117 | 22 | Delivery runs over a snapshot: a subscriber added during delivery gets the next event and an unsubscribe skips no one, while a plain list skips one; nested events are queued in order, and immediate delivery reverses them | `test_a_subscriber_added_during_delivery_gets_the_next_event`, `test_unsubscribing_during_delivery_does_not_skip_another_subscriber`, `test_a_plain_list_skips_a_subscriber_when_one_unsubscribes_during_delivery`, `test_an_event_published_during_delivery_waits_its_turn`, `test_an_immediately_delivered_nested_event_arrives_out_of_order` |
| 118 | 21-22 | Lifetime tests don't depend on immediate finalisation: names are dropped and `gc.collect()` runs before each assertion | `source: https://docs.python.org/3/reference/datamodel.html`, `test_the_weak_pool_drops_a_commodity_nobody_holds`, `test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs` |
| 119 | 21-22 | The "Build, run, observe" experiments behave as quoted | `run: K5` |

## Corrections after the build
- Step K1a: member 31 functions, 44 cases, as planned. `mypy.api.run` raises the process recursion limit, so the deep-tree test passed alone and failed after any static test; a `recursion_limit` fixture pins it to 1000 and restores it (tests 10, 12). Test 12 builds the 5,000-level tree through `object.__new__`/`object.__setattr__` because `__post_init__` flattens recursively. `domain.py` carries a private `_consignment_ids` match to avoid an import cycle. Test 15 asserts `__suppress_context__` (witnesses `from None`). Bench figures within a few hundred bytes of evidence E; `getsizeof` values identical. `verify.sh` doesn't run mypy on `bench/`; checked by hand.
- Step K1a, experiment (b) differs: removing `weakref_slot=True` also fails tests 7, 11, 12, 17 and 21 (the pool builds every commodity); test 15[weak-pool] still passes (the unknown code raises before any weak reference).
- Tooling, 2026-11-05 (owner): validate.py's word floor is now a warning and the 2,500 ceiling an error; CLAUDE.md records the new sidebar content rule and chapter structure from lgtm-professional-voice (#94-#96). r10 chapters follow them; chapters 0-20 are retrofitted later.

(Empty. The orchestrator records here every message, count or value that differs from Planning evidence or this spec, with the step that found it.)

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` (ch21 also covers `bench`) on three consecutive runs.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch"` over both members prints nothing.
   - `grep -rn "print("` over both members' `src` and `tests` prints nothing.
   - `grep -rnE "^\s*(from abc|import abc)|\bABC\b|\bAny\b|cast\(|\bfloat\b|__new__" examples/21-*/src` prints nothing.
   - `grep -rnE "\bAny\b|cast\(|threading|asyncio|sleep" examples/22-*/src` prints nothing.
3. Every test name cited in rows 107-118 is defined exactly once across `examples/*/tests` (`grep -rhoE "def test_\w+" examples/*/tests | sort | uniq -d` lists none of them).
4. Every mypy-API test asserts its exit status and an exact code set, uses the anchored `_codes` regex, and asserts no line number or optional note. `grep -c "_codes("` is at least 4 in each `test_static.py`. Every `# type: ignore[...]` names a code.
5. Deletion tables (K1a, K1b): every row, deleted in a fresh scratch copy whose imports come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed"; executor-check rows are resolved or moved to Corrections with the orchestrator's agreement.
6. ch21-22 are drafted, with one figure each, captions of 20-45 words including `Figure N.1:`, and 1,900-2,500 prose words each (validate.py).
7. `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere. `grep -c "^## When not to use it"` is 1 in each and `grep -c "^## How it works"` is 0. `validate.py` passes the `pattern` spine.
8. Thesis: each chapter says its patterns survive (`surviv` at least 1 in each) and names what Python removes (the Component base class, the factory class, the Observer interface). ch21 says equality works without interning.
9. Non-overlap and pointers:
   - ch21 points to "What 1994 assumed, and what Python dissolves", "Dataclasses and value semantics", "Protocol, duck typing, and structural typing with mypy" and "Singleton: module, Borg, and metaclass" by title.
   - ch22 points to "The three-way split: dissolve, survive, disambiguate", "Protocol, duck typing, and structural typing with mypy" and "Dataclasses and value semantics" by title.
   - Neither chapter describes the content of any stub chapter (Iterator, Mediator and Chain of Responsibility, Visitor/Memento/Interpreter, descriptors, singledispatch, the GIL, asyncio). ch21 uses no generator for traversal.
   - Neither re-teaches the evidence method, which is pointed to "Proving it works: pytest, pytest-mock, and mypy".
10. Voice:
    - `scan.sh --tier ban --fail` exits 0 over both chapters, READMEs, cards and SVGs, with `--stats` reviewed against the house-voice rubric.
    - Contractions: uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and exact quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz)"` over prose (front matter, quotations and code excluded) prints nothing. The data model's "finalization" is quoted verbatim, and everywhere else the prose writes "finalisation".
11. There's no em-dash or en-dash in any file touched in r10, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0.
12. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Smalltalk|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/21-*.md`, `_docs/22-*.md`, the new READMEs and the cards prints nothing.
13. Idiomatic scan: 0 ban-tier in both members.
14. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`, never hand-edited. The memory evidence file is scrubbed and names the CPU only by class, if at all.
15. Every excerpt matches its source byte for byte. Every quoted pytest, mypy or bench output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
16. Each experiment is performed in a fresh scratch copy (its `.venv` removed and re-synced, `__file__` confirmed) and changes one thing. The run uses exactly `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests`, three times. The prose quotes the observed result, and the handback includes the raw filtered output and states where it differs from the prediction.
17. Attribution (credit every source a chapter leans on, by author and work, where the idea is used; nothing copied; a missing credit is blocking):
    - ch21 credits GoF (Composite, Flyweight) in plain paraphrase and Rhodes's "The Composite Pattern" and "The Flyweight Pattern". It quotes `sys.intern`, `sys.getsizeof`, the `weakref` `WeakValueDictionary` and `__slots__` sentences, the data-model `__slots__` passage and the `functools` cache sentences exactly.
    - ch22 credits GoF (Observer) and claims no Rhodes page. It quotes the `weakref` opening and `WeakMethod` sentences and the data-model finalisation sentence exactly, and credits PEP 654.
    - GoF claims appear only if verified, with the bracketed fallbacks applied, and no GoF sentence tracks the Intent wording. Each prose agent lists the sources it checked. Every book cited is already in `bibliography.html`; anything else is flagged to the owner, not added.
18. Claims:
    - Every factual sentence in ch21-22 maps to a named test, a recorded run (`run: K5` or a file under `_plans/evidence/`) or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0. The claims table lists rows 1-119, with 107-119 resolved, and each `source:` URL appears in its chapter.
    - No `run: J*` or `I*` token appears in rows 107-119.
19. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 23 entries, and `diagrams/0*-*`, `diagrams/1*-*` and `diagrams/20-*` are unchanged.
20. Reconciliation rows 107-119 are `verified` or `adjusted` with evidence.
21. Deterministic:
    - No test depends on wall time, the environment, memory addresses, byte counts, test order or iteration order it didn't create.
    - Every lifetime assertion follows `del` and `gc.collect()`, and the cycle test pauses the collector and restores its state.
    - No `is` comparison with a string literal appears in any test.
    - `filterwarnings = ["error"]` is still in the root config.
    - Every fixture builds fresh pools, caches and signals per test.
22. CI `ci-ok` is green on the PR. Merge happens only after the user's explicit approval.
23. Every self-contained mypy snippet that stands for code (ch21 test 31; ch22 test 24) is named in the prose as a reduced model. Snippets that import `src` need nothing more.
24. Test counts in prose and handbacks come from the pytest summary line of a fresh run, never from this plan's arithmetic.
25. Every comparison form said to share a table is a conftest fixture param (`tree_form`, `pool_form`, `signal_form`), and each chapter shows at most one comparison excerpt.
26. Every figure label that names code (`ConsolidatedShipment`, `Consignment`, `Commodity`, `CommodityPool`, `Signal.publish`, `TrackingHistory.record`, `ExceptionGroup`) exists in that chapter's `src` or the standard library, checked by grep at K3.

## Risks

- **Predicted messages and counts.** Every iteration since r05 mispredicted something; r09's ch20 member doubled its planned test count. Expect differences in these places:
  - the code for test 30[assign] (`[misc]` recorded for a frozen property; a slotted field may differ);
  - test 22's expected-type substring (the alias may print as `Callable[[HandlingEvent], None]` or `def (HandlingEvent)`);
  - which tests fail in experiment (a) of each chapter.

  Tests match codes and stable substrings only, and differences go in Corrections.
- **Garbage collection in tests.** Evidence J showed a loop variable keeping a subscriber alive. A pytest assertion-rewrite temporary, a traceback frame or a fixture can do the same. Subscribers are built in helpers, names are deleted, and a failing lifetime test is first checked with `gc.get_referrers` in the scratch copy before anything in `src` changes.
- **The cycle test** relies on `gc.disable()`. The fixture restores the previous state in `finally`, so a failure can't leave collection off for later tests.
- **CPython details stated as such.** Split strings being distinct objects, immediate reclamation by reference counting, the recursion threshold and every byte count are CPython 3.15.2 observations. The prose says so, and the tests avoid asserting the version-sensitive ones (no bytes, no threshold).
- **Memory figures can age, and can read as performance claims.** They live only in the bench output and the evidence file, labelled approximate and dated. No test asserts them.
- **`WeakMethod` keys after death.** Evidence J shows the hash cached and self-equality kept, so `_forget(ref)` finds the entry. If a later CPython changes that, test 9 catches it.
- **The `inspect.ismethod` narrowing** (evidence M) loses the signature on the weak branch. The chapter states it as recorded mypy 2.4.1 behaviour in one sentence. `subscribe`'s parameter type stays the checked boundary.
- **ruff.** E731 (lambda assignment) is avoided with the `_strong` helper. B023 (a closure over a loop variable) is avoided in the tests. N818 holds (`ConsolidationError`, `UnknownCommodityError`, `PortCodeError`). The bench script's `print` is allowed by the ruff config (no `T20` selected); the idiomatic scan may flag it, and the executor reports that.
- **`Shipment` and `CommodityPool` are new supporting names.** They're recorded in domain row 21 at K0 (decision 3). If the owner declines, the alias becomes `Part`, or the union is written out.
- **Word budgets.** ch21 carries two patterns, and ch22 carries four contract topics. If either overruns, the GoF comparison paragraph (ch21) and the string-bus paragraph (ch22) shrink first; their tests stay.
- **Stub pointers.** It's tempting to write "the Iterator chapter shows a generator traversal" or "asyncio and the patterns covers async observers". Criterion 9 forbids both.
- **Liquid.** f-strings with `{{` in excerpts need `{% raw %}`; validate.py checks.
- **`uv.lock` race.** K1a and K1b are sequenced, and project names normalise to the package names.
