---
title: "r02 plan: chapters 1-4 (Parts 1-2)"
order: 2
output: false
render_with_liquid: false
---

# r02: chapters 1-4

Opus-planned 2026-11-03. Branch `release/r02`. Source of truth for r02 scope, criteria
and status. Executors never edit this file; the orchestrator updates the status board.

## User decisions (2026-11-03, binding)

1. **Canonical three-way map adopted** (below). It supersedes the Notion PRD table; every
   later pattern chapter names the same bucket.
2. **Witness scope:** chapter 3's example tests the dissolve and disambiguate rows plus the
   Command split; survive rows are argued from the force and verified in their own chapters.
3. **One shared example:** `examples/03-three-way-split` (package `three_way_split`), owned
   by chapter 3 (`has_example = true`); chapter 2 quotes it and links its example page.

## Approach

- Chapters 1 and 4: no code (series precedent). Chapter 2: short excerpts copied byte for
  byte from the chapter 3 member. Chapter 3: the member plus "Build, run, observe".
- No "before" code for contrast: chapter 2 describes the 1994 class structure in prose.
- One figure per chapter, drawn after the example is green with its real names.
- No `ai-sidebar` in chapters 1-4 (pattern chapters only); chapter 4 uses plain sections.
- No cross-language comparison; GoF's sample languages are never named.

Rejected: docs only (leaves 🔬 claims unverified); spike evidence only (spikes are not reader
code and lack the core dissolve claims); two members (duplicate witnesses); a class-vs-function
harness in chapter 2 (contrast code); a name-lint test for chapter 4 (brittle, proves nothing).

## Canonical three-way map

**Dissolves**
- Strategy: a callable or `functools.partial` ("Strategy: the callable").
- Iterator: a generator or `__iter__` ("Iterator: generators and the iterator protocol";
  async form in "asyncio and the patterns").
- Factory Method: a class or function in a dict ("Factory Method and Abstract Factory").
- Template Method: a function taking hook callables; an ABC hook only where steps share state
  ("Template Method and the function alternative").
- Builder: a keyword-only dataclass; Prototype: `dataclasses.replace` / `copy`
  ("Builder, dataclasses, and Prototype").
- Visitor: `singledispatch` for an open set, `match` + `assert_never` for a closed set
  ("Visitor, Memento, and Interpreter"; "singledispatch: the Visitor the language gives you").
- Null Object: `X | None` checked by mypy ("Protocol, duck typing, and structural typing with mypy").
- Value Object: a frozen dataclass ("Dataclasses and value semantics").
- Metaclass registry: `__init_subclass__` ("Metaclasses, __init_subclass__, and registries").
- If-chain dispatch: a dict of callables, with EAFP ("Shortcut patterns: dict dispatch,
  function tables, and EAFP").

**Survives**
- State; Command with undo and queues (the plain deferred call dissolves); Abstract Factory.
- Adapter (duck typing removes it only when shapes already match); Facade; Bridge.
- Composite; Flyweight; Observer (delivery order, failure isolation, subscriber lifetime).
- Mediator; Chain of Responsibility; Memento; Interpreter.
- Resource acquisition ("Context managers: deterministic cleanup").

**Needs disambiguating**
- Decorator pattern vs `@decorator` syntax ("Decorator the pattern vs @decorator the syntax,
  and Proxy"; "Decorators done right").
- Singleton: module, Borg, metaclass; default answer a module built at import time
  ("Singleton: module, Borg, and metaclass"). Never say `functools.cache` makes a singleton.
- Proxy: surrogate object vs attribute interception (`__getattr__`, `property`,
  `cached_property`) ("Dynamic attributes: __getattr__ and Proxy as a feature";
  "Descriptors and properties").
- "Interface": `Protocol` (structural) vs ABC (nominal), in the Protocol chapter.

## Per-chapter spec

### Chapter 1: Patterns as decisions under forces (argument, no code)
Thesis: a pattern records a resolution of competing forces in a context; its Consequences
are the ledger of what it buys and costs. Reading patterns as decisions lets the book ask,
pattern by pattern, whether the force is still there in Python 3.14.
Sections: Learning objectives; Why this matters; figure; What a pattern records (Alexander's
definition as GoF adopted it, the template sections, Consequences); The rating problem as
forces (tariffs by zone and weight band on carriers' schedules; commercial surcharges and
discounts; destination tax; reproducible quotes for billing disputes; rules testable alone);
Which force dominates decides the shape (one function over a `Tariff` table, separate rule
callables, or a `RateCalculator` Protocol once a participant has state or several operations;
prose only); Forces outlive the structures that resolved them (bridge to the next chapter by
topic, no number); What a pattern name buys and costs (one paragraph); When the forces argue
for no pattern; For deeper coverage.
Figure `01-patterns-as-decisions-under-forces`: vertical; problem box, four force boxes
converging on an accent "Decision: where the rating rules live", then "Consequences", then
"The shape follows the dominant force". Caption draft: "The rate-quote decision under four
forces. Carrier tariffs, commercial surcharges and destination tax change on separate
schedules while every quote must stay reproducible; the chosen shape follows from which force
dominates." Cite GoF (Introduction, Consequences), Martin; bibliography link.

### Chapter 2: What 1994 assumed, and what Python dissolves (argument, excerpts)
Thesis: the 1994 catalogue assumed behaviour reaches a call site only inside an object of a
declared class; Python 3.14 makes functions, generators, modules and optional types
first-class, so the scaffolding dissolves while the force often stays. The test for every
pattern: did the force move, or only the mechanism?
Sections: Learning objectives; Why this matters; figure; The object model the catalogue
assumed (paraphrase GoF on patterns depending on language features, verify first, no language
names); Functions are objects (Strategy, deferred half of Command: `type PricingRule`, `quote(...) -> RateQuote`,
`partial(per_kg, ...)`); Generators (Iterator: `pages(history, size)`, lazy pull); Structural typing
(`CarrierGateway` Protocol; what it does not remove: an adapter when shapes differ); Modules
(`tariff_table`, one instance built at import); Absence in the type (`CarrierGateway | None`,
real mypy `[union-attr]` line); Did the force move, or only the mechanism? (Composite, State
keep their shape); For deeper coverage. Excerpts match `examples/03-three-way-split/src` byte
for byte; link `{{ '/examples/03-three-way-split/' | relative_url }}`.
Figure `02-what-1994-assumed-and-python-dissolves`: five rows, "assumed in 1994" -> Python
feature with the real name (`PricingRule`, `CarrierGateway`, `pages`, `tariff_table`,
`CarrierGateway | None`). Caption draft: "Assumptions the 1994 catalogue was written under, each
paired with the Python 3.14 feature that removes it: functions as objects, structural typing,
generators, modules imported once, and absence checked by the type checker."
Cite GoF; Fluent Python 2nd ed; Effective Python 3rd ed (by topic, never item number); PEP 544,
255, 695, data model reference, python-patterns.guide inline.

### Chapter 3: The three-way split (argument, has_example = true)
Thesis: two questions sort every catalogue pattern: does the name mean two things in Python,
and does a language feature remove the force? The map names each pattern's chapter by title.
Sections: Learning objectives; Why this matters; figure; Two questions that sort a pattern;
Patterns that dissolve (map table + prose); Patterns that survive (the force that remains,
grouped by lifecycle, structure, coordination); Names that need disambiguating (Decorator
first, then Singleton, Proxy, Protocol vs ABC); Beyond the catalogue (Null Object, Value
Object, dict dispatch and EAFP); Patterns that straddle two buckets (Command, Template Method,
Visitor); Build, run, observe; For deeper coverage. Map table columns: Pattern | Bucket | What
Python gives you | Developed in (title link `{{ '/docs/<slug>/' | relative_url }}`). Table rows
do not count toward the word floor.
Figure `03-the-three-way-split`: decision ladder (Q1 name means two things? -> disambiguate;
Q2 feature removes the force? yes dissolve / no survive) beside three bands of patterns and
idioms with real names. Caption draft: "The three-way split. Two questions sort every catalogue
pattern: does the name mean two things in Python, and does a language feature remove the
force? The answers place each pattern in dissolves, survives or needs disambiguating."
Cite GoF; Fluent Python; Effective Python; Lott & Phillips 5th ed; python-patterns.guide
inline; PEP 544, 557, 695; functools docs.

### Chapter 4: Naming patterns for teams and AI assistants (argument, no code)
Thesis: a pattern name compresses a contract that a reviewer or an assistant can check against
a diff; in Python the name should label the role and mechanism (`PricingRule`, `make_consignment`)
rather than a class suffix that drags in the 1994 structure.
Sections: Learning objectives; Why this matters; figure; A name is a checkable claim; Where the
pattern name lives in Python (type alias, docstring, PR description; PEP 8); Names across the
consignment lifecycle (Booked, Loaded, Departed, Cleared, Delivered); Names that hide the
bucket (`RateStrategy` vs `pricing_rule`, `ConsignmentFactory` vs `make_consignment`, `*Manager`,
`*Helper`); Keeping Decorator and `@decorator` apart in names (`Surcharge` vs `audited`,
`retry`); Steering an AI assistant with names; Reviewing a name an assistant attached to its
output; When a name stops matching the code; For deeper coverage. No empirical claims about
LLM behaviour (frame as review practice).
Figure `04-naming-patterns-for-teams-and-ai`: request box splitting into "names only the
pattern" (muted) and "names the role and mechanism" (`PricingRule`, `per_kg`, accent), flowing to
"Reviewer and assistant check the same contract". Caption draft: "One pattern name, two
readers. A reviewer and an AI assistant read the same name for the same contract; naming the
Python mechanism as well, a callable type alias rather than a class hierarchy, keeps both
readers on the idiomatic shape." Cite GoF, Martin Clean Code, Fowler Refactoring 2nd ed
(Mysterious Name, Rename); PEP 8 inline.

## Example: `examples/03-three-way-split` (package `three_way_split`)

Names follow the series shipping domain standard (`shipping-domain-model.md`): fictional carriers
FASTLINE and AIRCO, `Money` over `Decimal`, `Weight` from the prerequisites example.

src: `domain.py` (frozen slotted kw_only `Consignment(id: ConsignmentId, weight: Weight, zone,
destination)`; `Money` frozen dataclass with `Decimal` amount and currency; `Weight`; frozen
`Booked`, `Loaded`, `Departed`, `Cleared`, `Delivered` (a subset is fine);
`type HandlingEvent = Booked | Loaded | Departed | Cleared | Delivered`; `RateQuote`; `TrackingHistory`);
`dissolve.py` (`type PricingRule = Callable[[Consignment], Money]`, `flat_rate`, `per_kg`,
`quote(c, rule) -> RateQuote`; `CarrierGateway` Protocol `book(c, /) -> str`, `FastlineGateway`,
`AircoGateway`, `GATEWAYS: dict[str, Callable[[], CarrierGateway]]` keyed `FASTLINE` and `AIRCO`;
`pages(history, size)` generator over a `TrackingHistory`; `declare_customs(c, *, hooks) ->
CustomsDeclaration` template function with hooks per destination; `BookingRequest` kw-only
dataclass; `describe` singledispatch; `find_gateway(code) -> CarrierGateway | None`;
`CarrierBase.__init_subclass__(*, code)` + `DuplicateCarrierError`); `survive.py` (`Booking`; frozen
`Amendment` with `apply`/`undo`); `disambiguate.py` (`RateCalculator` Protocol, `BaseRate`,
additive `Surcharge` wrapping `BaseRate`; `audited(sink)` on `quote_carrier`; `TrackingHistory`
lazy loader with `cached_property`; `CarrierGatewayProxy` caching proxy via `__getattr__`;
`CarrierBase(ABC)` vs the Protocol); `tariff_table.py` (module-level `Tariff` instance
`tariff_table` built at import); `loads.py` (import-count log, separate module).

Tests (each asserts the mechanism):
- test_dissolve.py: 1 strategy slot accepts def, lambda, partial (all `PricingRule`s returning
  `Money`); 2 a class is already a factory method (`GATEWAYS`); 3 iterator is a lazy generator
  (`pages` over a counting `TrackingHistory`, `iter(g) is g`, exhausted); 4 template method is a
  function taking hooks (order of the `CustomsDeclaration` steps); 5 builder is a keyword-only
  dataclass (`BookingRequest` positional call TypeError); 6 prototype is replace; 7 visitor is
  singledispatch without `accept`; 8 null object is an optional checked by mypy
  (`mypy.api.run(["--strict","-c",SNIPPET])` on `find_gateway(code).book(...)`, assert exit 1 and
  `[union-attr]`, guarded variant passes); 9 value object is a frozen dataclass (`Money`);
  10 registry is `__init_subclass__` (duplicate raises).
- test_survive.py: 11 deferred command is a partial in a deque; 12 undo needs a command object
  (`Amendment`).
- test_disambiguate.py: 13 GoF decorator wraps an instance at runtime (`Surcharge(BaseRate(...))`);
  14 decorator syntax rebinds the name at definition time (`audited` on `quote_carrier`); 15 the two
  decorators are independent; 16 module is one instance for every importer (log shows one load of
  `tariff_table`); 17 cached_property is lazy init without a proxy (`TrackingHistory`); 18 proxy
  forwards only missing attributes (`CarrierGatewayProxy`); 19 Protocol is structural, ABC is
  nominal (`CarrierGateway` vs `CarrierBase`).
Also `README.md`, `_examples/03-three-way-split.md`; `uv.lock` updated.

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| 0 | Plan file; iteration-plan rows 101-104; canonical map + ch1-4 rows in domain model; reconciliation claims 1-4 plan; ch3 `has_example = true`; fix Part 2 blurb; note PRD table superseded in Notion | - | **done** |
| 1 | Example member + card + uv.lock; gates; handback of names and scrubbed output | 0 | todo |
| 2 | Record witness results in reconciliation; change map if any witness fails | 1 | todo |
| 3 | Four figures + `_data/diagrams.yml` (single owner); chapter 0 figure unchanged | 1 | todo |
| 4 | ch1-4 `status = "drafted"` | 3 | todo |
| 5 | Four prose agents in parallel, one file each | 3,4 | todo |
| 6 | Opus validation; up to two repair rounds | 5 | todo |
| 7 | PR, `ci-ok` green, ask user before merge; tag r02.x; release; PRD build log | 6 | todo |

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`.
2. In `examples/03-three-way-split`: `uv run pytest` and `uv run mypy --strict src tests` exit 0
   on three consecutive runs; no `time.sleep|perf_counter|time.time(` in its tests.
3. `validate.py` and `--self-test` exit 0; ch1-4 drafted, one figure each, captions 20-45 words,
   1,900-2,500 prose words.
4. `grep -c '<blockquote class="ai-sidebar"' _docs/0[1-4]-*.md` is 0 for each.
5. Voice `scan.sh --tier ban --fail` exits 0 over ch1-4, the example README and card, the four
   SVGs; `--stats` reviewed.
6. Idiomatic scan 0 ban-tier on `examples/03-three-way-split`.
7. `host_ids.py check` exits 0; quoted output uses `<repo>`.
8. ch1-4 prose has no `unlike (Java|C#|C\+\+)|in Java|in C#|capstone|PDP-|\br0[0-9]\b|spike`.
9. `scripts/site-build.sh` succeeds, `git status` clean after; four figures and the example page render.
10. `_data/diagrams.yml` has five entries, each with svg + excalidraw; `diagrams/00-*` unchanged.
11. Reconciliation claims 1-4: adjusted / verified / adjusted / verified with evidence; the
    chapter 3 map matches this plan's canonical map.
12. CI `ci-ok` green on the PR; merge only after the user's explicit approval.

## Risks

- Map drift into later chapters (the map here is canonical).
- Chapter 3 word floor (table rows don't count).
- Repetition between chapters 2 and 3: ch2 = mechanisms (why), ch3 = classification (what, where).
- Chapter 4 must make no empirical claims about LLMs (owned by "Working with AI and LLM tools").
- GoF's statement about language features must be verified before it is paraphrased.
- mypy-API witness: assert error codes, use `-c` so no temp paths leak.
- Module-singleton witness: the load log lives outside the imported module.
- Ban-tier phrases ("earns its keep", "for free"); "spike" banned in reader files; raw-wrap `{{`.
- Re-rendering every spec could change the chapter 0 figure; diff check catches it.
