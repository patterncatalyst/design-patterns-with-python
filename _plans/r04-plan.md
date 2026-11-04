---
title: "r04 plan: chapters 7-8 (Part 4, the Python substrate)"
order: 4
output: false
render_with_liquid: false
---

# r04: chapters 7-8

Opus-planned 2026-11-03. Branch `release/r04`. Source of truth for r04 scope, criteria and
status. Executors never edit this file; the orchestrator updates the status board.

Planning evidence (read-only `python -I -c` and `mypy.api.run(["--strict","--warn-unreachable",
"--cache-dir","/dev/null","--no-error-summary","-c",SNIPPET])`, Python 3.14.10, mypy 2.4.1).
Every item becomes a test below; the plan does not rely on any of them beyond this list.

Runtime:
- A plain class defining `__eq__` alone gets `__hash__ = None`; 3.14 messages read
  `cannot use 'W' as a set element (unhashable type: 'W')` and `cannot use 'MS' as a dict key
  (unhashable type: 'MS')`; `hash(x)` reads `unhashable type: 'MS'`.
- A `@dataclass(frozen=True)` with a hand-written `__eq__` and no `__hash__` keeps a
  field-based generated `__hash__`: two equal `Dimensions` (120,80,100) and (80,120,100) give
  `len(set) == 2`. With an explicit `__hash__` as well, the explicit one is kept (set of 1)
  whether or not `eq=False` is given. `eq=False` plus `__eq__` and no `__hash__` is unhashable.
- `@dataclass` (eq, not frozen) sets `__hash__` to None; `frozen=True` + eq generates it;
  `eq=False` keeps identity equality and `object.__hash__`.
- `order=True` compares field tuples; with a hand-written `__lt__` it raises `TypeError: Cannot
  overwrite attribute __lt__ in class Bad Consider using functools.total_ordering`.
- `slots=True`: no `__dict__`, `weakref.ref` raises `cannot create weak reference to 'S'
  object`; `weakref_slot=True` restores it.
- `dataclasses.replace` reruns `__post_init__` (`weight must be finite and positive, got -1.0`);
  `object.__setattr__` on a frozen slotted instance succeeds and bypasses the validation.
- Frozen is shallow: a `list` field can be appended to, and `hash()` raises `unhashable type: 'list'`.
- Mutable default: `mutable default <class 'list'> for field xs is not allowed: use default_factory`.
- `kw_only` positional call: `K.__init__() takes 1 positional argument but 2 were given`.
- `field(compare=False)` is excluded from `__eq__` and `__hash__` but kept in `repr`.
- `Money + 1` with an `isinstance` guard returning `NotImplemented` gives `unsupported operand
  type(s) for +: 'Money' and 'int'`; `1 + m` gives `'int' and 'Money'`; `sum([m])` gives
  `'int' and 'Money'`.
- `Decimal("2") * m` reaches `Money.__rmul__`; a class without `__rmul__` gives `unsupported operand
  type(s) for *: 'decimal.Decimal' and 'NoR'`.
- `total_ordering` stacked on a slotted dataclass adds `__le__` and `__gt__` to the class dict. With
  `__lt__` alone, `a > b` works through the reflected `__lt__` and `a <= b` raises `'<=' not
  supported between instances of 'LtOnly' and 'LtOnly'`.
- `bool()` falls back to `__len__`. A class with only `__iter__` is truthy when empty. `in` falls back to
  `__iter__`. Without `__getitem__`: `'R' object is not subscriptable`.
- With `__str__` only, `f"{x:>5}"` raises `unsupported format string passed to R.__format__`.
- A class without `__lt__`: `sorted` raises `'<' not supported between instances of 'X' and 'X'`.

mypy 2.4.1:
- `def __eq__(self, other: "Dimensions")` gives exit 1, `[override]`, with `This violates the
  Liskov substitution principle` and `It is recommended for "__eq__" to work with arbitrary
  objects`.
- `__add__(self, other: "Money")` with an `isinstance` guard returning `NotImplemented`: no
  `[unreachable]` under `--warn-unreachable`; `m + 1` is `[operator]` `Unsupported operand types
  for + ("Money" and "int")`. With `other: object`, `m + 1` passes mypy (only `1 + m` is flagged),
  so the parameter is typed with the class, not `object`.
- `m * 1.5`, `1.5 * m`, `m >= 3` are `[operator]`. `Decimal("2") * m`, `2 * m`, `m <= m` on
  `total_ordering` + slotted dataclass, `f"{m:>12}"` and `sum([m, m], start=Money(...))` (revealed
  `Money`) pass.
- `sum([m, m])` with no start gives two `[list-item]` errors whose text says `expected "bool"`
  (typeshed's first `sum` overload). The prose quotes the line only if a fresh run matches, and gives
  no explanation it can't test.
- `sorted([RateQuote(...)])` is `[type-var]`; `sorted(quotes, key=lambda q: q.net)` where `Money`
  has no `__lt__` is `[arg-type]` plus `[return-value]`.
- Not indexable: `[index]` `Value of type "H" is not indexable`; iteration reveals the element type.
- Frozen assignment `[misc]` `Property "a" defined in "S" is read-only`; `replace(s, b=3)`
  `[call-arg]` `Unexpected keyword argument "b" for "replace" of "S"`; kw_only positional
  `[call-arg]` `Too many positional arguments for "S"`; frozen slotted extra attribute `[attr-defined]`.
- `Money < Money` without ordering: `[operator]` `Unsupported left operand type for < ("Money")`.
  `order=True` against an int: `[operator]`.
- Exit 0 (mypy can't see it): a mutable dataclass as a dict key or set element; an
  eq-only class as a dict key; `weakref.ref` of a slotted dataclass; a mutable list default on a
  dataclass field; a frozen dataclass with a custom `__eq__` and generated hash in a set.

Repo facts: both chapters are `kind = "hands-on"`, `has_example = true`, `status = "stub"`. The
stubs' `## How it works` heading is a placeholder and is replaced. The reconciliation plan has
rows 1-36; this iteration adds 37-46. `_data/diagrams.yml` has seven entries. Ramalho's *Fluent
Python* (2nd ed., O'Reilly, 2022) is in both `bibliography.html` and the hub's `books.yml`.

## User decisions (2026-11-03, confirmed by the owner)

1. **One ai-sidebar per chapter** (r03 decision 1 parity). Chapter 7: inside
   `## When a dunder costs more than it buys` (substrate, no bucket). Chapter 8: inside
   `## When not to use it` (it carries the Value Object bucket). Both stay `kind = "hands-on"`;
   grep criteria 5 and 6 enforce the headings and sidebars. Framed as review practice ("may",
   checklist wording), with no empirical claims about LLM behaviour.
2. **Chapter 7 types are frozen slotted dataclasses**, with hand-written dunders only where the
   chapter teaches them. Negative fixtures (plain classes, missing dunders) live in `tests/` and
   are named as fixtures in one prose sentence, as r03 did.
3. **Bibliography: add Evans.** Row for *Domain-Driven Design: Tackling Complexity in the Heart of
   Software*, Eric Evans (Addison-Wesley, 2003), topic "Value Object, entities", with markup that
   matches the existing rows. The hub `books.yml` Evans entry gets `design-patterns-with-python` in
   `referenced_by` through the hub PR. Fowler's *Patterns of Enterprise Application Architecture*
   (2002) stays inline. The chapter 8 prose agent owns the `bibliography.html` edit.

## Approach

- **Chapter 7 is a substrate chapter, not a pattern chapter: no bucket.** Its thesis is that every
  operator, builtin and f-string is a call the interpreter makes on the type, and a type joins a
  protocol by defining the method. Prose doesn't label chapter 7 dissolve, survive or disambiguate.
  The domain-model row stays `n.a.`.
- **Chapter 8: Value Object dissolves.** The force is a value compared by content, shared without
  defensive copies, usable as a key, with an invariant that holds for its life. The structure it
  replaces is private fields with accessors, a hand-written constructor, an equality and hash pair
  kept in sync by discipline, and copy-with-change methods. The thesis wording is used verbatim
  once: "a feature resolves the force without the pattern's structure". What remains is the
  invariant (`__post_init__`), field types that are themselves immutable (frozen is shallow), and
  the choice between value and entity (`eq=False` for `StowagePlan`).
- **Split between the two chapters.** Chapter 7 covers the dunders a class writes by hand: the
  equality and hash contract, operators, `NotImplemented` and reflected operands,
  `total_ordering`, the container methods, and text. Chapter 8 covers what `@dataclass` generates
  and its switches (`frozen`, `slots`, `weakref_slot`, `order`, `eq=False`, `kw_only`,
  `field(compare=False)`, `default_factory`, `__post_init__`, `replace`). Chapter 7 states the
  frozen-dataclass hash trap once, because it is part of the hash contract. Chapter 8 doesn't
  repeat it.
- **Non-overlap.** Chapter 7 has no `Protocol` or structural typing (Protocol chapter) and no
  generator: `TrackingHistory.__iter__` returns `iter(self.events)`, and paging and `yield`
  belong to the Iterator chapter. It has no descriptors, `__getattr__` or
  `__set_name__`. `with` gets one sentence naming `__enter__`/`__exit__`, pointing to "Context
  managers: deterministic cleanup" by title. Chapter 8 uses `replace` only for value semantics
  (amend means a new value; `__post_init__` reruns). It has no argument about many optional
  fields, no `copy`, and no Builder or Prototype framing; one pointer goes to "Builder,
  dataclasses, and Prototype" by title.
- **One uv member per chapter.** `examples/07-the-data-model` (project `data-model`, package
  `data_model`) and `examples/08-dataclasses-and-value-semantics` (project `value-semantics`,
  package `value_semantics`). The package must not be named `dataclasses`. Each member is
  standalone and re-declares its own small domain module, as 05 and 06 did. Neither imports
  `examples/00-prerequisites` or another member. The two `Money` types differ on purpose
  (chapter 8's `Money` has no ordering), and the prose never compares them.
- **mypy witnesses** use r03's API pattern (`mypy.api.run(["--strict","--cache-dir",os.devnull,
  "--no-error-summary","-c",SNIPPET])` with the member's `src` on the path, as in
  `examples/05-srp-ocp-lsp/tests/test_lsp.py`). Each asserts the exit status, the exact code set
  (`_codes()`), and one or two key substrings. Inline `# type: ignore[code]` comments in tests are
  static witnesses too: strict mode's `warn_unused_ignores` fails the member mypy run if mypy
  stops flagging the line.
- **Negative witness rule.** Every behavioural or contract check in model code has a test that
  fails when the check is deleted. This is proven by the deletion table in steps 1a/1b.
- **No global-state mutation.** No `monkeypatch`, no `mock.patch`, no module-level mutable
  tables.

Rejected:
- Plain-class chapter 7 types (becomes contrast code for chapter 8).
- `__radd__` that accepts `0` so `sum()` works without `start=` (a hack; the chapter shows
  `start=`).
- `__bool__` on `Money` (zero-is-falsy surprises; named as a cost instead).
- `order=True` on `Money` (it compares across currencies).
- `unsafe_hash` (no witness need; not taught).
- `NamedTuple` comparisons (unwitnessed; out of scope).
- `object.__setattr__` normalisation in `__post_init__`: it's documented as possible but hides a
  mutation inside an immutable type. The chapter normalises in `Money.of` and validates by
  reading only.
- `field(compare=False)` on an entity's non-id fields (confuses value versus entity).
- Bucket labels in chapter 7.

## Per-chapter spec

### Chapter 7: The data model: dunder methods as the substrate (hands-on, has_example = true)

Thesis: syntax is a call on the type. `==`, `hash()` and set membership, `+` and `*`, `<` and
`sorted`, `len`, `bool`, `for`, `in`, `repr`, `str` and format specs each invoke a named
method, looked up on the class. A shipping value answers each one correctly, or fails somewhere
far from its definition: equal cartons booked twice in a set, a rate times a factor that raises
in a report, quotes that won't sort.

Sections (spine headings exact; about 2,200 prose words; at most six code excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): the failures above, each one a missing or wrong method; the
   interpreter calls the type, so the type is where the fix goes.
3. Figure include plus one paragraph reading it (~60).
4. `## Syntax is a call on the type` (~220) plus a table (rows not counted). Columns: Syntax |
   Method | Fallback. Rows: `a == b`; `hash(a)`, set, dict key; `a + b`; `factor * price`;
   `a < b`; `len(h)`; `bool(h)`; `for e in h`; `x in h`; `repr`/`str`/`format`. Lookup is on the
   type, not the instance (witness 1).
5. `## Equality and hashing: one contract` (~400). Default identity equality (fixture). `Weight`
   gets value equality and a hash from its dataclass declaration, with a one-sentence pointer to
   "Dataclasses and value semantics" for what the declaration generates. Defining `__eq__` alone
   sets `__hash__` to None. `Dimensions`: a carton may be stowed on any face, so equality compares
   the sorted extents while the fields keep the declared orientation. That is why it isn't
   normalised at construction (say so). `__hash__` hashes the same key. The trap: a frozen
   dataclass with a custom `__eq__` and no `__hash__` keeps a field hash, mypy is silent, and the
   set has two entries. `__eq__` takes `object` and returns `NotImplemented` for foreign types:
   fresh mypy output for the narrowed `__eq__` snippet, `<string>:N` lines.
6. `## Arithmetic and the NotImplemented handshake` (~400): excerpts `Money.__add__`, `__mul__`
   and `__rmul__`. Same currency or `ValueError`; a foreign type gets `NotImplemented`, then
   Python tries the reflected method, then raises `TypeError`. `factor * price` walks the figure.
   `sum()` starts from `0`, so it needs `start=`. mypy sees operand types (`[operator]` on
   `price * 1.5`, `price >= 3`). The parameter is typed `Money`, not `object`, so mypy still
   rejects `price + 1`. Say it as a fact witnessed by test 17, not as advice from nowhere.
7. `## Ordering: one method and total_ordering` (~300): `Money.__lt__` (same currency or
   `ValueError`); with `__lt__` alone, `>` works by reflection while `<=` fails (fixture);
   `functools.total_ordering` derives the rest; sorting `RateQuote`s by `total` (runtime and
   mypy); `sorted(quotes)` fails because `RateQuote` defines no order, and shouldn't.
8. `## Containers: length, iteration, membership, truth` (~250): `TrackingHistory.__len__`,
   `__iter__` returning a fresh iterator per call (re-iterable; generators and paging are covered
   in "Iterator: generators and the iterator protocol"). `in` falls back to `__iter__`; `bool`
   falls back to `__len__`; an iterable without `__len__` is truthy when empty (fixture);
   iterable isn't subscriptable (`[index]`). One sentence: `with` calls `__enter__` and
   `__exit__`, covered in "Context managers: deterministic cleanup".
9. `## Text: repr, str, and format` (~170): the dataclass `repr` for developers, `__str__` for a
   manifest line, `__format__` delegating to `str` so `f"{price:>12}"` aligns. Without
   `__format__`, a spec raises (fixture).
10. `## When a dunder costs more than it buys` (~200): an operator whose meaning a reader has to
    look up (`Money * Money`, `consignment + consignment`); `__bool__` on an amount; equality
    across types (`Money == Decimal`) that breaks hashing. Then the one sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written dunders.** An
    assistant may type `__eq__` with the class instead of `object`, define `__eq__` without
    `__hash__`, or add `__radd__` that accepts `0` to make `sum()` work. Check: does `__eq__` take
    `object` and return `NotImplemented` for foreign types; do equal values hash equal (a set
    test, not a reading); are operands typed so mypy rejects the ones the method refuses; is
    `start=` used rather than a special case in `__radd__`.</blockquote> (Each check corresponds
    to a test; no claim about how often assistants do this.)
11. `## Build, run, observe` (~250 plus output): commands as in chapter 5. Fresh `uv run pytest
    -v` and `uv run mypy --strict src tests`, filtered with `python3 scripts/host_ids.py filter`
    (`<repo>`). Two experiments, each in a scratch copy, changing one thing, then reverted:
    (a) Delete `Dimensions.__hash__`. Expected: `test_a_turned_carton_is_one_set_element` fails
    with a set of size 2, and mypy still reports success.
    (b) Delete `Money.__rmul__`. Expected: `test_a_factor_times_money_uses_the_reflected_method`
    fails with `TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'Money'`, and
    mypy reports `[operator]` on that test line.
    Record the real results. If one differs, the claim is wrong: record it and adjust before
    drafting.
12. `## For deeper coverage` (~150): *Fluent Python* 2nd ed. chapters on the data model, a
    Pythonic object and operator overloading [name chapter titles only if verified against the
    O'Reilly table of contents, else "by topic"]; Python Language Reference "Data model",
    sections "Basic customization" (the `__hash__` = None rule) and "Emulating numeric types"
    (reflected operands); the `NotImplemented` constant; `functools.total_ordering`; PEP 207 (rich
    comparisons); *Effective Python* 3rd ed. by topic; `{{ '/bibliography/' | relative_url }}`.

Figure `07-the-data-model` (vertical): the top accent box is `factor * price`. Below it,
`Decimal.__mul__(factor, price)` / "left operand's type asks first", then an arrow labelled
"NotImplemented" to `Money.__rmul__(price, factor)` / "reflected method answers", then an arrow
to `Money` result. A side branch from the reflected box, labelled "NotImplemented again", leads
to `TypeError` / "only when both decline". There are no numbers in the SVG. Caption draft (36
words with the prefix): "Figure 7.1: How Python evaluates factor times price. The interpreter
asks the left operand's type first; Decimal returns NotImplemented for Money, so Money's
reflected method answers, and only when both decline does the expression raise TypeError."

Citations (verify each before writing; bracketed fallback if not verifiable):
- Python Language Reference, Data model (docs.python.org/3/reference/datamodel.html):
  special-method lookup on the type ("Special method lookup"); the `__eq__`-without-`__hash__`
  rule; reflected operands and `NotImplemented`. Quote no sentence verbatim unless checked.
- PEP 207 (Rich Comparisons, 2000) for `NotImplemented` in comparisons [else docs only].
- Ramalho, *Fluent Python* 2nd ed. (O'Reilly, 2022) [chapter titles only if verified].
- No cross-language comparison, no "magic methods" as a pejorative.

### Chapter 8: Dataclasses and value semantics (hands-on, has_example = true)

Thesis: Value Object dissolves. One `@dataclass(frozen=True, slots=True)` declaration writes the
constructor, `repr`, equality, hash and assignment guard that the pattern's structure used to
spell out, so a feature resolves the force without the pattern's structure. Three things stay with
the author: the invariant, field types that are themselves immutable, and whether a type is a value
at all or an entity with identity.

Sections (about 2,250 prose words; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): one consignment shared by two booking requests and reweighed
   for one of them changes both; a slot key that can't go in a dict; a stowage plan that double
   books.
3. Figure plus one paragraph (~60).
4. `## Value Object: the force and the structure` (~250): Fowler (PoEAA, 2002) and Evans (2003)
   with attribution; the force; the structure; bucket stated: dissolves, with the thesis wording.
   Not a GoF catalogue entry (one clause).
5. `## One declaration: frozen and slotted` (~330): excerpts `Weight`, `SlotId`. What's
   generated; `FrozenInstanceError` and mypy's `[misc]` read-only error (fresh output); frozen
   guards `__setattr__`, and `object.__setattr__` gets past it, which is why normalisation doesn't
   go through it; `slots=True` drops `__dict__` and weak references, `weakref_slot=True` puts the
   latter back, and mypy doesn't see the `weakref` failure.
6. `## Hashing follows from frozen` (~250): frozen + eq generates `__hash__`; eq without frozen
   sets it to None, so a mutable `SlotId` can't be a dict key and mypy doesn't flag it (fresh
   exit-0 run); frozen is shallow: a `list` field mutates and makes the value unhashable, so use
   `tuple`.
7. `## Values and entities` (~330): the aliasing fixture; with a frozen `Consignment`, amending
   is `replace`, which returns a new value and reruns `__post_init__`; the other booking keeps the
   old one. `StowagePlan` is an entity: `@dataclass(eq=False, slots=True)` keeps identity
   equality and an identity hash, `reservations` uses `field(default_factory=dict)`, and a mutable
   default is refused when the class is created (mypy is silent). `BookingRequest.remarks` with
   `field(compare=False)`: a retried request with a different driver remark is the same booking,
   so a dict keyed by request deduplicates it. Pointer to "Builder, dataclasses, and Prototype" for
   construction with many options.
8. `## Ordering: order=True and when to write it yourself` (~250): `SlotId` sorts by bay, row,
   tier because field order is the meaning; on `Money`, `order=True` would compare across
   currencies without complaint (fixture); `order=True` refuses a hand-written `__lt__` and its
   message names `functools.total_ordering`. `Money` here defines no order, and mypy reports
   `[operator]` on `<`.
9. `## Invariants: validate in __post_init__, normalise before` (~200): excerpt `Money`.
   `__post_init__` only reads (currency code, whole cents); `Money.of` quantises before
   construction; `kw_only=True` on `Consignment` (mypy `[call-arg]`); mypy checks `replace`
   keyword names.
10. `## When not to use it` (~200): a type with a lifecycle and identity (`StowagePlan`) isn't a
    value; data that has to change in place as one aggregate; a value whose equality isn't
    field-by-field (custom equality, covered with the hash contract in "The data model: dunder
    methods as the substrate"). Then the one sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written value types.** An
    assistant may produce private fields with accessor methods, a mutable dataclass used as a
    dict key, a `list` field inside a frozen class, `order=True` on an amount with a currency, or
    `object.__setattr__` in `__post_init__` to normalise. Check: is the type frozen and slotted;
    are field types immutable; does `__post_init__` only read; is ordering meaningful field by
    field; does a test put two equal values in a set.</blockquote>
11. `## Build, run, observe` (~250 plus output). Two experiments, each in a scratch copy:
    (a) Remove `frozen=True` from `SlotId`. Expected: tests that key a dict or set by `SlotId`
    fail with the 3.14 `cannot use 'SlotId' as a dict key (unhashable type: 'SlotId')` message,
    and mypy says nothing about hashing.
    (b) Add `order=True` to `Money`. Expected: `test_order_true_would_compare_money_across_currencies`
    fails with `DID NOT RAISE`, and mypy reports an unused `type: ignore` (`[unused-ignore]`).
    Record the real results and adjust if they differ.
12. `## For deeper coverage` (~150): *Fluent Python* 2nd ed. chapter on data class builders
    [title only if verified, else by topic]; Evans 2003 (Value Objects and Entities); Fowler, PoEAA
    2002 ("Value Object"); Fowler's bliki "ValueObject" only if the URL verifies [else omit]; PEP
    557; the `dataclasses` docs (frozen instances, `__post_init__`, `replace`, mutable default
    values, `slots`/`weakref_slot`, `kw_only`); *Effective Python* 3rd ed. by topic; bibliography
    link.

Figure `08-dataclasses-and-value-semantics` (vertical): the top accent box is
`@dataclass(frozen=True, slots=True, order=True)` / `class SlotId: bay, row, tier`. Under it, one
row of generated-method boxes: `__init__`, `__repr__`, `__eq__` and `__hash__`, `__lt__` ... `__ge__`,
`__setattr__` raising `FrozenInstanceError`, `__slots__`. Arrows converge on a box "Value Object
force: compared by content, safe to share, usable as a key". A side box (light fill), "left to
you", lists the invariant in `__post_init__`, immutable field types, value or entity. Caption draft
(38 words with the prefix): "Figure 8.1: One declaration, the Value Object's structure. A frozen,
slotted, ordered dataclass writes the constructor, repr, equality, hash, ordering and the
assignment guard for SlotId; the invariant, immutable field types and the value-or-entity choice
stay with you."

Citations: Evans (2003) and Fowler (2002) as above; PEP 557; `dataclasses` docs; Ramalho. No
cross-language comparison. Don't credit anyone with the term "value semantics" [unattributed].

## Example spec

### `examples/07-the-data-model` (project `data-model`, package `data_model`)

`pyproject.toml` in the ch3/ch5 shape, no `[tool.*]` tables; the project name normalises to the
package name.

- `cargo.py`: `Weight(kilograms: float)` (frozen slotted; `__post_init__` raises `ValueError`
  unless finite and positive; no hand-written dunders). `Dimensions(length_cm: int, width_cm:
  int, height_cm: int)` (frozen slotted; `__post_init__` positive ints; private
  `_extents() -> tuple[int, ...]` = sorted; `__eq__(self, other: object) -> bool` returning
  `NotImplemented` for non-`Dimensions`; `__hash__` = `hash(self._extents())`; docstring: a
  carton may be stowed on any face).
- `money.py`: `ConsignmentId = NewType(...)`; `@functools.total_ordering` over
  `@dataclass(frozen=True, slots=True) Money(amount: Decimal, currency: str)`:
  `__add__(self, other: Money) -> Money` (guard `NotImplemented`; `ValueError("cannot add USD to
  EUR")`); `__mul__(self, factor: Decimal | int) -> Money` (guard; quantised to cents,
  `ROUND_HALF_UP`); `__rmul__` delegating to `__mul__`; `__lt__(self, other: Money) -> bool`
  (guard; `ValueError("cannot compare USD with EUR")`); `__str__` gives `"EUR 12.50"`;
  `__format__(self, spec: str) -> str` gives `format(str(self), spec)`. `RateQuote(consignment_id,
  net: Money, tax: Money)` (frozen slotted, `total` property, no ordering).
- `tracking.py`: `HandlingKind` enum (BOOKED, LOADED, DEPARTED, CLEARED, DELIVERED);
  `HandlingEvent(consignment_id, kind, location)` (one class plus enum, as in chapter 6);
  `TrackingHistory(events: tuple[HandlingEvent, ...])` (frozen slotted; `__len__`; `__iter__ ->
  Iterator[HandlingEvent]` returning `iter(self.events)`; no `__bool__`, `__contains__` or
  `__getitem__`).
- `py.typed`, `__init__.py`.

`tests/conftest.py`: a EUR `price` (`Money(Decimal("12.50"), "EUR")`), three quotes with
different totals, a three-event history at `"NLRTM"`/`"SGSIN"`.

`test_equality.py` (fixtures here: `_IdentityWeight` plain slotted class with no `__eq__`;
`_EqOnlyWeight` plain class with `__eq__` only; `_FieldHashDimensions` frozen slotted dataclass
with `Dimensions`' `__eq__` and no `__hash__`; `_InstanceLen` plain class):
1. `test_special_methods_are_looked_up_on_the_type`: `obj.__len__ = lambda: 3` on an instance;
   `len(obj)` raises `TypeError` matching `has no len`.
2. `test_equal_weights_are_one_set_element`: `len({Weight(1.5), Weight(1.5)}) == 1`;
   `_IdentityWeight` gives 2 and `!=`.
3. `test_defining_eq_alone_makes_a_class_unhashable`: `vars(_EqOnlyWeight)["__hash__"] is
   None`; a set raises `TypeError` matching `unhashable type: '_EqOnlyWeight'`.
4. `test_a_turned_carton_is_one_set_element`: (120,80,100) == (80,120,100), equal hashes, set of
   1; `repr` keeps the declared order; (120,80,90) is unequal; `d == (120, 80, 100)` is `False`
   and `d.__eq__((120, 80, 100)) is NotImplemented`.
5. `test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash`: `_FieldHashDimensions` instances
   are equal and form a set of 2.

`test_arithmetic.py`:
6. `test_money_adds_within_one_currency_only`: EUR sum exact; USD raises `ValueError` matching
   `cannot add USD to EUR`; `price + 1` and `1 + price` (each `# type: ignore[operator]`) raise
   `TypeError` matching `'Money' and 'int'` and `'int' and 'Money'`.
7. `test_a_factor_times_money_uses_the_reflected_method`: `Decimal("2") * price ==
   Money(Decimal("25.00"), "EUR")`; `2 * price` equal; `price * Decimal("0.333")` quantised.
8. `test_sum_needs_a_money_start`: `sum(prices, start=Money(Decimal("0.00"), "EUR"))` exact;
   `sum(prices)` with the ignore code mypy reports (expected `[list-item]`) raises `TypeError`
   matching `'int' and 'Money'`.

`test_ordering.py` (fixture `_LtOnlyMoney`: frozen slotted dataclass with `__lt__` only):
9. `test_total_ordering_derives_the_other_comparisons`: `<=`, `>`, `>=` on `Money`; `"__le__" in
   vars(Money)`; `_LtOnlyMoney`: `>` is `True` through reflection, `<=` raises `TypeError`
   matching `'<=' not supported`.
10. `test_money_refuses_to_order_across_currencies`: `ValueError` matching `cannot compare USD
    with EUR` for `<` and `<=`; `price < 3` (`# type: ignore[operator]`) raises `TypeError`.
11. `test_quotes_sort_by_total_but_not_by_themselves`: `sorted(quotes, key=lambda q: q.total)`
    in the expected order; `sorted(quotes)` (`# type: ignore[type-var]`) raises `TypeError`
    matching `'<' not supported between instances of 'RateQuote' and 'RateQuote'`.

`test_containers.py` (fixture `_IterOnlyHistory`: `__iter__` only):
12. `test_history_is_sized_and_reiterable`: `len == 3`; `list(h) == list(h)`; an event `in h`;
    an absent event `not in h`; `[e.kind for e in h]` in order.
13. `test_empty_history_is_falsy_through_len`: `not TrackingHistory(())`; `"__bool__" not in
    vars(TrackingHistory)`; empty `_IterOnlyHistory` is truthy.
14. `test_history_is_not_subscriptable`: `h[0]` (`# type: ignore[index]`) raises `TypeError`
    matching `'TrackingHistory' object is not subscriptable`.

`test_text.py` (fixture `_StrOnlyMoney`):
15. `test_repr_str_and_format_serve_different_readers`: `repr(price) ==
    "Money(amount=Decimal('12.50'), currency='EUR')"`; `str(price) == "EUR 12.50"`;
    `f"{price:>12}" == "   EUR 12.50"`; `f"{x:>12}"` on `_StrOnlyMoney` raises `TypeError`
    matching `unsupported format string`.

`test_static.py` (mypy API; snippets type-check apart from the intended error):
16. `test_mypy_rejects_an_eq_that_narrows_its_argument`: exit 1, `{"override"}`, contains `This
    violates the Liskov substitution principle` and `It is recommended for "__eq__" to work with
    arbitrary objects`.
17. `test_mypy_rejects_operands_the_methods_do_not_accept`: `price * 1.5`, `1.5 * price`,
    `price >= 3`, `price + 1`: exit 1, `{"operator"}`, four error lines.
18. `test_mypy_accepts_the_protocols_the_types_define`: `Decimal("2") * price`, `price <=
    price`, `f"{price:>12}"`, `sum(..., start=...)`, `sorted(quotes, key=lambda q: q.total)`,
    `for e in history`: exit 0, empty stdout. Plus a local `Money` without `__lt__` sorted by key:
    exit 1, `{"arg-type", "return-value"}`.
19. `test_mypy_cannot_see_a_broken_hash_contract`: a frozen dataclass with a custom `__eq__` and
    no `__hash__`, used in a set: exit 0, empty stdout.

Also `README.md` ("What it witnesses", ch5 style) and card `_examples/07-the-data-model.md`
(`order: 7`, eyebrow "Python substrate · The data model"). No `yield`, `Protocol`,
`__getattr__`, `__get__`, `__set_name__`, `__enter__`, `print(`, `monkeypatch`, or `mock.patch` in
the source.

### `examples/08-dataclasses-and-value-semantics` (project `value-semantics`, package `value_semantics`)

- `values.py`: `ConsignmentId = NewType`. `Weight(kilograms: float)`: `frozen=True, slots=True,
  order=True`; `__post_init__` reads only. `Money(amount: Decimal, currency: str)`: frozen
  slotted, no order; `__add__` same currency with a `NotImplemented` guard; `__post_init__`
  checks currency `[A-Z]{3}` and whole cents, `ValueError` messages naming the field;
  `@classmethod of(cls, amount: str, currency: str) -> Money` quantises `ROUND_HALF_UP`.
  `SlotId(bay: int, row: int, tier: int)`: frozen slotted ordered; `__post_init__` checks `bay
  >= 1`, `row >= 0`, `tier >= 1`.
- `booking.py`: `Consignment(id, weight, destination)` (frozen slotted kw_only; destination a
  UN/LOCODE). `BookingRequest(consignment, insured: bool = False, remarks: str =
  field(default="", compare=False))` (frozen slotted kw_only).
- `stowage.py`: `@dataclass(eq=False, slots=True) StowagePlan(sailing: str, reservations:
  dict[SlotId, ConsignmentId] = field(default_factory=dict))`. `reserve(slot, consignment_id)`
  raises `ValueError` matching `already holds` on a taken slot. `occupied() -> list[SlotId]`
  returns `sorted(self.reservations)`.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: a consignment to `"SGSIN"`, a request for it, three slots.

`test_values.py` (fixtures: `_FrozenWithList` frozen dataclass with `codes: list[str]`;
`_WeakrefWeight` with `weakref_slot=True`):
1. `test_equal_values_are_interchangeable`: `Weight`, `Money`, `SlotId`: equality, equal hashes,
   dict lookup by a freshly built equal key.
2. `test_a_frozen_value_refuses_assignment`: `w.kilograms = 2.0` (`# type: ignore[misc]`) raises
   `FrozenInstanceError` matching `cannot assign to field 'kilograms'`.
3. `test_frozen_is_a_setattr_guard_not_a_seal`: `object.__setattr__(w, "kilograms", -5.0)`
   succeeds and the invalid value is visible.
4. `test_frozen_is_shallow`: `_FrozenWithList(...).codes.append(...)` mutates; `hash()` raises
   `TypeError` matching `unhashable type: 'list'`.
5. `test_slots_remove_dict_and_weakref_until_asked`: `not hasattr(w, "__dict__")`;
   `weakref.ref(w)` raises `TypeError` matching `cannot create weak reference to 'Weight'`;
   `weakref.ref(_WeakrefWeight(1.0))` works.

`test_aliasing.py` (fixtures: `_MutableConsignment` and `_MutableBooking`, plain `@dataclass`):
6. `test_a_mutable_consignment_aliased_between_bookings_changes_both`: reweighing through
   booking A is visible through booking B.
7. `test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old`: `replace(c,
   weight=...)` gives a new object; request B's consignment is unchanged; the original is unchanged.
8. `test_replace_runs_post_init`: `replace(Weight(1.0), kilograms=-1.0)` and `replace(slot,
   bay=0)` raise `ValueError`.
9. `test_a_mutable_dataclass_is_not_a_dict_key`: fixture `_MutableSlotId`: `__hash__ is None`;
   a dict raises `TypeError` matching `cannot use '_MutableSlotId' as a dict key`.

`test_generated.py` (fixture `_OrderedMoney` with `order=True`):
10. `test_order_true_sorts_by_field_order`: slots sort by bay, then row, then tier; `max` of
    weights.
11. `test_order_true_would_compare_money_across_currencies`: `_OrderedMoney(Decimal("3"), "EUR")
    < _OrderedMoney(Decimal("5"), "USD")` is `True` with no error; real `Money` `<`
    (`# type: ignore[operator]`) raises `TypeError` (`pytest.raises`).
12. `test_order_true_refuses_a_hand_written_lt`: building such a class raises `TypeError`
    matching `Cannot overwrite attribute __lt__`.
13. `test_compare_false_keeps_remarks_out_of_equality`: requests differing only in `remarks`
    are equal, hash equal, collapse to one dict key; `repr` shows both remarks.
14. `test_kw_only_rejects_positional_arguments`: positional `Consignment(...)` (ignore code as
    mypy reports, expected `[call-arg]`) raises `TypeError` matching `positional argument`.
15. `test_money_validates_and_of_normalises`: `Money.of("12.505", "EUR").amount ==
    Decimal("12.51")`; `Money(Decimal("12.505"), "EUR")` and `Money(Decimal("1.00"), "eur")`
    raise `ValueError`.
16. `test_stowage_plan_is_an_entity`: two plans for one sailing are unequal, each equals itself,
    a set holds 2; `reserve` then a conflicting `reserve` raises `ValueError` matching `already
    holds`; the plans don't share `reservations`; `occupied()` is sorted.
17. `test_mutable_default_is_refused_at_class_creation`: defining a class with
    `reservations: dict[...] = {}` raises `ValueError` matching `use default_factory`.

`test_static.py`:
18. `test_mypy_checks_the_generated_methods[frozen-assignment|kw-only-positional|replace-unknown-field|money-has-no-order]`:
    exit 1. Codes, in order: `{"misc"}`, `{"call-arg"}`, `{"call-arg"}`, `{"operator"}`.
    Substrings, in order: `Property "kilograms" defined in "Weight" is read-only`, `Too many
    positional arguments for "Consignment"`, `Unexpected keyword argument "kilos" for "replace"
    of "Weight"`, `Unsupported left operand type for < ("Money")`.
19. `test_mypy_cannot_see_value_semantics_mistakes[mutable-dict-key|mutable-default|slots-weakref]`:
    exit 0, empty stdout.

Also `README.md` and card `_examples/08-dataclasses-and-value-semantics.md` (`order: 8`, eyebrow
"Python substrate · Dataclasses, Value Object"). No `Protocol`, `copy`, `unsafe_hash`,
`object.__setattr__` in `src/`, `monkeypatch`, `mock.patch`, or `print(`.

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| 0 | This plan file; PDP-107a..c and 108a..c `active`. Domain-model row 7: names `Weight`, `Money`, `Dimensions`, `RateQuote`, `TrackingHistory`, `HandlingEvent`, `HandlingKind`, `functools.total_ordering`, `NotImplemented`, `__mul__`/`__rmul__`, `__format__`; failing column: "`factor * price` fails without `__rmul__`; quotes don't sort by total without `Money.__lt__`; a custom `__eq__` without `__hash__` leaves equal cartons as two set elements". Row 8: add `SlotId`, `StowagePlan`, `BookingRequest`, `Consignment`, `replace`, `field(compare=False)`, `field(default_factory=dict)`, `eq=False`, `kw_only`; `order=True` on `Weight` and `SlotId`, not `Money`. Reconciliation rows 37-46 `open`. Decision 3 bibliography row recorded as pending | - | **done** |
| 1a | ch7 member, card, README; gates; three consecutive green runs; **deletion table**: in a scratch copy delete each check (`Dimensions.__hash__`, the `Dimensions.__eq__` guard, the `Money.__add__` currency check, the `Money.__add__` guard, `Money.__rmul__`, the `Money.__lt__` currency check, `@total_ordering`, `TrackingHistory.__len__`, `TrackingHistory.__iter__`, `Money.__format__`) and record the failing test id for each. Handback has test names, the table, and scrubbed output | 0 | **done** |
| 1b | ch8 member, card, README; one `uv lock` after both members exist (sequenced after 1a); gates; deletion table: `frozen=True` on `Weight` and on `SlotId`, each `__post_init__` check, the `Money.of` quantise, `compare=False`, `kw_only=True`, `eq=False` on `StowagePlan`, `default_factory`, the `reserve` conflict check; plus adding `order=True` to `Money` | 1a | **done** |
| 2 | Witness results into reconciliation rows 37-46; a failed witness changes the thesis before prose | 1b | **done** |
| 3 | Two figures, specs `diagrams/specs/07-the-data-model.py` and `08-dataclasses-and-value-semantics.py`, `_data/diagrams.yml` (single owner; `section: "Ch. 7"`/`"Ch. 8"`); figures 00-06 unchanged | 1b | todo |
| 4 | ch7 and ch8 `status = "drafted"` in `scripts/chapters.toml` (kind stays `hands-on`) | 3 | todo |
| 5 | Two prose agents in parallel. Verify attributions; run the experiments in a scratch copy; quote fresh filtered output. The ch8 agent edits `bibliography.html` (decision 3). Each lists the sources it checked | 3,4 | todo |
| 6 | Opus validation; up to two repair rounds | 5 | todo |
| 7 | PR, `ci-ok` green, ask the user before merge; tag r04.x; notes-only release; hub PR for the Evans `referenced_by` (decision 3) | 6 | todo |

Reconciliation rows (step 0):

| # | Ch | Claim | Verified by |
| --- | --- | --- | --- |
| 37 | 7 | Operators and builtins call the special method on the type; an instance attribute named `__len__` is ignored | ch7 test 1 |
| 38 | 7 | Equal values must hash equal: `__eq__` alone sets `__hash__` to None; a custom `__eq__` in a frozen dataclass keeps a field hash and breaks set membership; mypy is silent | ch7 tests 2-5, 19 |
| 39 | 7 | Returning `NotImplemented` hands the operation to the other operand: `factor * price` reaches `Money.__rmul__`; foreign operands raise `TypeError`; `sum()` needs `start=`; mypy checks operand types when the parameter is typed with the class | ch7 tests 6-8, 17, 18 |
| 40 | 7 | `total_ordering` derives `<=`, `>`, `>=`; with `__lt__` alone `>` works by reflection and `<=` fails; sorting quotes by total needs `Money.__lt__` at runtime and under mypy | ch7 tests 9-11, 18 |
| 41 | 7 | `bool` falls back to `__len__` and `in` to `__iter__`; an iterable without `__len__` is truthy when empty; iterable isn't subscriptable | ch7 tests 12-14 |
| 42 | 7 | mypy requires `__eq__` to accept `object`, reporting `[override]` with the LSP note | ch7 test 16 |
| 43 | 8 | A frozen slotted dataclass supplies Value Object's equality, hash and immutability (dissolve); frozen is a `__setattr__` guard and is shallow; slots drop weak references until `weakref_slot` | ch8 tests 1-5 |
| 44 | 8 | A mutable consignment shared between bookings aliases; `replace` gives a new value and reruns `__post_init__`; a mutable eq dataclass is unhashable and mypy accepts it as a key | ch8 tests 6-9, 19 |
| 45 | 8 | `order=True` orders by field tuple, would order `Money` across currencies, and refuses a hand-written `__lt__` | ch8 tests 10-12 |
| 46 | 8 | `compare=False`, `kw_only`, `eq=False` and `default_factory` behave as documented; mypy checks frozen assignment, kw_only, `replace` keywords and missing order, but not mutable defaults or weakrefs to slotted instances | ch8 tests 13-19 |

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`.
2. Each new member: `uv run pytest` and `uv run mypy --strict src tests` exit 0 on three
   consecutive runs; `grep -rnE "time\.sleep|perf_counter|time\.time\(|monkeypatch|mock\.patch|runtime_checkable|random"`
   over both members prints nothing.
3. Every mypy-API test asserts exit status and an exact code set: `grep -c "_codes("` is at least
   4 in each member's `tests/test_static.py`; every `# type: ignore[...]` in the tests names a
   code (no bare ignores).
4. Deletion tables from steps 1a and 1b: every listed check, when deleted (or for `Money`,
   when `order=True` is added), makes at least one named test fail; no row reads "nothing failed".
5. `validate.py` and `--self-test` exit 0; ch7 and ch8 drafted, one figure each, captions 20-45
   words including the `Figure N.1:` prefix, 1,900-2,500 prose words (target about 2,200).
6. `grep -c '<blockquote class="ai-sidebar"'` is 1 for ch7 and for ch8; `{: .ai-sidebar}` appears
   nowhere; `grep -c "^## When a dunder costs more than it buys"` is 1 in ch7;
   `grep -c "^## When not to use it"` is 1 in ch8; `grep -c "^## How it works"` is 0 in both.
7. Thesis wording: ch8 contains "a feature resolves the force without the pattern's structure"
   (or the same clause adapted to the sentence) and names the bucket as dissolves;
   `grep -ciE "dissolv|surviv|disambiguat"` over ch7 prints 0.
8. Non-overlap: `grep -nE "yield|Protocol|__getattr__|__get__|__set__\b|__set_name__|__enter__|__exit__"`
   over `examples/07-the-data-model/src` prints nothing; `grep -c "__enter__" _docs/07-*.md` is
   at most 1; `grep -nE "Builder|Prototype|copy\.copy|unsafe_hash"` over
   `examples/08-dataclasses-and-value-semantics/src` prints nothing; the ch8 prose mentions
   Builder or Prototype only in the one pointer sentence.
9. Voice: `scan.sh --tier ban --fail` exits 0 over ch7, ch8, both READMEs, both cards and both
   SVGs; `--stats` reviewed; `only`, `never`, `always`, `every` checked against the code;
   contractions used in prose (uncontracted `does not|do not|is not|are not|did not` at most 3 per
   chapter outside code and quoted output).
10. `grep -c $'\u2014'` is 0 over every file touched in r04, including this plan.
11. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|capstone|PDP-|\br0[0-9]\b|spike|[Cc]hapter [0-9]|magic method"`
    over `_docs/0[78]-*.md`, both READMEs and both cards prints nothing.
12. Idiomatic scan 0 ban-tier in both members.
13. `python3 scripts/host_ids.py check` exits 0; quoted output shows `<repo>`.
14. Every code excerpt matches its source byte for byte; every quoted pytest or mypy output comes
    from a fresh run of the exact command or snippet (mypy-API output prints `<string>:N` and the
    line numbers match the test's snippet), apart from scrubbing and duration.
15. Each experiment is performed in a scratch copy and changes one thing; prose quotes the
    observed failing test id and message, or the observed absence of a failure; handback includes
    raw filtered output.
16. Attribution (standing rule: credit every source a chapter leans on, by author and work where the idea is used, and put every book in `bibliography.html`; never copy wording, examples or structure; a missing credit is blocking): ch8 names Fowler (PoEAA, 2002) and Evans (2003) for Value Object;
    `bibliography.html` has the Evans row (decision 3); Fluent Python chapter titles appear only if
    verified; bracketed fallbacks applied; each prose agent lists checked sources.
17. `scripts/site-build.sh` succeeds and `git status` is clean afterwards; both figures and example
    pages render; `_data/diagrams.yml` has nine entries; `diagrams/0[0-6]-*` unchanged.
18. Reconciliation rows 37-46 are `verified` or `adjusted`, with evidence.
19. CI `ci-ok` green on the PR; merge only after the user's explicit approval.

## Risks

- **Fixture explosion.** Each chapter has about 19 test functions and several fixtures. Keep
  fixtures one-purpose, `_`-prefixed and docstringed "Negative fixture: ..."; prose names the
  convention once.
- **3.14 message drift.** Unhashable messages changed format in 3.14 (`cannot use 'X' as a set
  element (...)`). Match on the stable `unhashable type: 'X'` substring in tests; quote the full
  message only from a fresh run.
- **Misleading `sum()` mypy message** (`expected "bool"`). Assert the code set, and don't explain
  typeshed internals in prose.
- **`other: Money` vs `other: object`.** `object` silences mypy on `price + 1`; test 17 fails if an
  executor "fixes" the annotation to `object`. `__eq__` alone must take `object` (test 16).
- **`total_ordering` over `slots=True`.** The decorator order matters (`total_ordering` outermost,
  applied to the class `dataclass` returns). Verified working; keep the order.
- **The Dimensions equality rule reads as arbitrary.** The docstring and prose give the stowage
  reason and say that normalising at construction would be simpler if the declared orientation
  didn't matter.
- **Overlap with the Protocol, Iterator, context manager, descriptor and `__getattr__` chapters,
  and with Builder/Prototype.** Criterion 8 greps; pointers by title only.
- **Thesis slip** ("the data model dissolves", or a bucket on ch7): criterion 7.
- **mypy-API snippets with accidental extra errors** (`[empty-body]`, `[no-untyped-def]`): use
  real bodies and exact code sets.
- **Snippets need the member's `src` on the mypy path**: copy r03's helper.
- **The `uv.lock` race** (1a, 1b sequenced); the project names must normalise to the package names.
- **Liquid**: f-strings in prose code with `{{` need `{% raw %}`; none are expected, and
  validate.py checks.
- **Word budget**: at most six excerpts per chapter; the ch7 table rows don't count, so the prose
  around the table must still reach 1,900.
- **Re-rendering all specs could alter figures 00-06**: criterion 17 diffs them.
- **Attribution**: Evans vs Fowler priority (Fowler's PoEAA predates the DDD book; don't claim
  who coined the term); Fluent Python chapter titles; PEP 207 scope. Fallbacks and criterion 16.
