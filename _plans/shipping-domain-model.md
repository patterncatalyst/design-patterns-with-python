---
title: "Shipping domain model"
order: 8
output: false
---

# PDP-008: shipping domain model

Internal planning file, excluded from the site. **Revise after the r01 spikes report.**
Mirrors the C# book's shipping domain (C# r01 plan table), re-expressed in idiomatic
Python 3.14: `Protocol`, frozen slotted dataclasses, plain callables, generators,
`functools.singledispatch`, `match`. Nothing here is Java-in-Python: no abstract base
classes where a `Protocol` or a function will do, no getters, no interface-per-class.

Bases: 📗 book (classic source), 📘 docs (language/library documentation), 🔬 original
research (needs a runnable experiment, see `reconciliation-plan.md`).
Buckets (the three-way split): dissolve (the language removes the need), survive
(the pattern still earns its keep), disambiguate (the name means two things in Python),
n.a. (not a pattern chapter).

## Seven domain areas

### Consignment
`ConsignmentId` (NewType over str), `Weight` (frozen dataclass, kg, validated),
`Money` (frozen dataclass over `Decimal` plus currency), `Address`, `Dimensions`,
`Consignment` (frozen, slotted; amendments through `dataclasses.replace`),
`ConsignmentStatus` (enum), `Amendment`.

### Carrier
`Carrier` (enum or frozen dataclass), `CarrierGateway` (Protocol: `book`, `track`,
`cancel`), `SailingId`, `Sailing` (departure, capacity), `CarrierError` hierarchy,
`SlotId`, `StowagePlan`.

### Rating
`RateCalculator` (Protocol: `quote(consignment) -> Quote`), `Quote`, `Tariff`
(mapping of zone and weight band to `Money`), `Surcharge`, `Discount`, `TaxRule`,
`RateRule` (callable), `RatingError`.

### Routing
`Port` (code, name), `Leg`, `Route` (sequence of `Leg`), `RoutePlanner` (callable
or Protocol), `TransitEstimate`, `Hub` (graph node), `Zone`.

### Tracking
`HandlingEvent` (frozen, tagged union by subclass or `match`-able dataclasses:
`Received`, `Loaded`, `Departed`, `Arrived`, `Delivered`, `Delayed`),
`TrackingHistory` (iterable, lazily paged), `EventFeed` (sync generator and async
generator), `Subscriber` (callable), `TransitState` (FSM states).

### Documentation
`Document` (base data), `BillOfLading`, `CommercialInvoice`, `CustomsDeclaration`,
`DocumentKind` (enum), `Renderer` (callable), `EdiSegment`, `ClearanceCheck`
(callable in a chain), `ClearanceResult`.

### Billing
`Invoice`, `LineItem`, `Ledger` (append-only), `Payment`, `Currency`,
`BillingPolicy`, `Statement`, `InvoiceNumber`.

## Chapter and appendix table

Failing test column: the test that fails (or the situation that is demonstrably
painful) before the pattern or idiom is applied, proving the problem is real. Perf
claims never appear as assertions; ch37 uses a benchmark script with recorded output.

| Ch | Title | Basis | Bucket | Shipping example | Key Python types and names | Failing test that proves the problem |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Prerequisites and the toolchain | 📘 | n.a. | Build and test a Consignment value | `Consignment`, `ConsignmentId`, `Weight`, `replace` | Invalid weight and mutation attempts are rejected; equality and hash hold |
| 1 | Patterns as decisions under forces | 📗 | n.a. | The rating problem stated as competing forces (carrier rates, surcharges, tax) | `RateCalculator`, `Quote`, `Tariff` | A rating function with every rule inline fails the "add a surcharge without editing it" test |
| 2 | What 1994 assumed, and what Python dissolves | 🔬 | n.a. | Argument chapter: the same quote done in a 1994 shape and a Python shape | `Callable[[Consignment], Quote]`, `RateCalculator` | Comparison harness: class-per-strategy vs function, same behaviour table (see reconciliation) |
| 3 | The three-way split | 🔬 | n.a. | Classify the book's patterns as dissolve/survive/disambiguate with a shipping case each | one table, runnable witness per row | Each row has a witness test that passes only with the claimed mechanism |
| 4 | Naming patterns for teams and AI | 📗 | n.a. | Naming across the consignment lifecycle | `ConsignmentFactory` vs `make_consignment`, `RateStrategy` vs `rate_rule` | A name-lint test flags misleading pattern suffixes on types that are not that pattern |
| 5 | SRP, OCP, and LSP | 📗 | survive | A RateCalculator doing pricing, tax, and audit, split | `RateCalculator`, `TaxRule`, `audit` callable | Adding a tax rule requires editing the calculator; a subclass that raises on zero weight breaks substitution |
| 6 | ISP, DIP, and DI without a framework | 📗 📘 | survive | `CarrierGateway` passed in as a constructor argument, wired by a plain composition root | `CarrierGateway` Protocol, `functools.partial`, `build_app()` | Booking test cannot run without a live carrier; fat protocol forces fakes to stub unused methods |
| 7 | The data model | 📘 | n.a. | Dunder methods on `Weight`, `Money`, `Route` | `__eq__`, `__hash__`, `__lt__`, `__iter__`, `__len__`, `__repr__` | `Money + Money` and sorting `Quote`s fail without `__add__` and ordering; sets of equal weights duplicate |
| 8 | Dataclasses and value semantics | 📘 📗 | dissolve (Value Object) | `Money`, `Weight`, `SlotId` as frozen slotted dataclasses | `@dataclass(frozen=True, slots=True, order=True)`, `field`, `__post_init__` | Mutable consignment aliased between two bookings changes both; unhashable key in a dict |
| 9 | Protocol and structural typing | 📘 📗 | dissolve (Null Object via Optional) | Carrier lookup that may find nothing; `NullGateway` vs `Optional[CarrierGateway]` | `Protocol`, `runtime_checkable`, `Optional`, `X \| None`, mypy | mypy fails on `lookup(c).book(...)` when `None` is possible; runtime `AttributeError` on a missing carrier |
| 10 | Context managers | 📘 | survive (Resource Acquisition) | `ManifestWriter` holding a file handle; ledger append under `async with` preview | `contextlib.contextmanager`, `ExitStack`, `__enter__/__exit__` | File handle left open after an exception mid-write; test asserts the handle is closed |
| 11 | Testing with pytest, pytest-mock, and mypy | 📗 📘 | n.a. | The rating engine under pytest with a mocked gateway | `pytest.fixture`, `parametrize`, `mocker.create_autospec`, `monkeypatch` | A mock without autospec accepts a misspelled `quote_all` call and the test passes wrongly |
| 12 | Strategy: the callable | 🔬 📘 | dissolve | Rate quotes priced three ways (flat, per-kg, zone) | `Callable[[Consignment], Money]`, `dict[str, Callable]`, `functools.partial` | Class-per-strategy needs three classes and a registry to pass the same table of cases a dict of functions passes |
| 13 | Template Method and the function alternative | 📗 | dissolve / survive | Customs declaration generation varying by destination | hook functions, `Protocol` with defaults, `abc.ABC` only where state is shared | A subclass forgets to call a base step; the function pipeline cannot omit it |
| 14 | State and finite state machines | 📗 📘 | survive | Consignment lifecycle FSM plus a probabilistic transit-delay machine (series parity) | `Enum`, transition `dict`, `match`, `assert_never`, seeded `random.Random` | Illegal transition (Delivered to Received) is accepted; probabilistic machine's seeded run is not reproducible without injected RNG |
| 15 | Command, undo, and command queues | 📗 | survive | Booking amendments with undo; queue of pending commands | frozen `Amendment` dataclass, `apply`/`undo` callables, `collections.deque` | Undo after two amendments restores the wrong state when commands share mutable data |
| 16 | Factory Method and Abstract Factory | 🔬 📗 | dissolve | A gateway per carrier, resolved by name | `dict[Carrier, Callable[[], CarrierGateway]]`, classmethod constructors | Adding a carrier requires editing an if-chain in three places |
| 17 | Builder, dataclasses, and Prototype | 📘 📗 | dissolve | A booking request with many optional fields; amendments by `replace` | keyword-only dataclass, `field(default_factory=...)`, `replace`, `copy.copy` | Positional constructor with 12 arguments is swapped silently; shallow copy shares a list |
| 18 | Singleton: module, Borg, metaclass | 📘 📗 | dissolve / disambiguate | The tariff table: expensive to load, needed everywhere | module-level object, `functools.cache`, `Borg`, `Singleton` metaclass | Two importers see two tariff loads under the naive class; test isolation leaks state between tests |
| 19 | Adapter, Facade, Bridge | 📗 📘 | survive | Three carrier APIs behind one `CarrierGateway`; weight and money unit conversions | adapter classes and `functools.singledispatchmethod`-free wrappers, `Protocol` | Calling code branches on carrier name; unit mix-up (lb vs kg) passes silently |
| 20 | Decorator pattern vs decorator syntax, and Proxy | 🔬 | disambiguate | Headline spike: a `RateCalculator` Protocol wrapped at runtime by discount, surcharge, and tax decorator objects, vs `@retry` / `@audited` on the function `quote()`; plus a caching proxy over a slow gateway | `RateCalculator`, `DiscountedCalculator`, `SurchargedCalculator`, `TaxedCalculator`, `functools.wraps`, `CachingGateway` | Stacking order of runtime wrappers changes the total and a function decorator cannot be composed per instance (witness pair) |
| 21 | Composite and Flyweight | 📗 📘 | survive | Consolidated shipments; port and commodity codes interned | `Shipment` tree of `Consignment`, `sys.intern`, `__slots__`, `weakref.WeakValueDictionary` | Total weight misses nested groups; equal port codes are distinct objects (`is` fails) |
| 22 | Observer | 📘 🔬 | dissolve / survive | Handling events raised as cargo moves | list of callables, `weakref.WeakMethod`, `Signal` helper | Subscriber raising stops delivery to later subscribers; unsubscribed bound method is kept alive |
| 23 | Mediator and Chain of Responsibility | 📗 📘 | survive | Customs clearance chain | `ClearanceCheck` callables, `Iterable[ClearanceCheck]`, `ClearanceResult` | A check added in the wrong order clears a restricted commodity; chain with no terminal default returns `None` |
| 24 | Iterator, generators, and the iterator protocol | 📘 📗 | dissolve | Paging a tracking history lazily | generator functions, `itertools.islice`, `__iter__`, `yield from` | Eager list of 1M events is fully built to read the first page; iterator exhausted on second pass |
| 25 | Visitor, Memento, Interpreter | 📗 🔬 | dissolve (Visitor, one of three) / survive | Visitor over `Document` kinds via singledispatch vs `match` vs classic double dispatch; Memento for an amendment rollback; Interpreter for tariff rule expressions | `singledispatch`, `match`, frozen snapshot dataclass, small `Expr` tree | New document kind silently ignored by one of the three dispatchers; mutated memento corrupts rollback |
| 26 | Decorators done right | 📘 🔬 | survive | Decorating the Documentation renderers (not the rating path): `@timed_render`, parametrised `@cached_for(seconds)`, a class decorator registering `DocumentKind`, stacking order | `functools.wraps`, `ParamSpec`, `Callable[P, R]`, class decorators | Decorated function loses `__name__`/signature; parametrised decorator used bare silently drops the function; wrong stack order changes cache behaviour |
| 27 | Descriptors and properties | 📘 | survive | Validated `Weight` kg field reused across `Consignment`, `Dimensions`, `Container` | `__set_name__`, `__get__`, `__set__`, `property`, `cached_property` | Copy-pasted property validators drift; a validator on one field is missing on another |
| 28 | singledispatch | 📘 🔬 | survive | Customs tariff code lookup by commodity type, and `singledispatchmethod` on a `Packaging` hierarchy (not Document kinds) | `functools.singledispatch`, `singledispatchmethod`, `register`, type-annotation registration | Unregistered type falls to the default silently; registration order import-dependent |
| 29 | Metaclasses, `__init_subclass__`, and registries | 📘 🔬 | dissolve | Auto-registered carrier adapters by `carrier_code` | `__init_subclass__`, `type`, `abc.ABCMeta`, registry `dict` | Forgotten manual registration means carrier unavailable at runtime; metaclass conflict when mixing |
| 30 | Dynamic attributes and Proxy | 📘 🔬 | survive | Lazy `TrackingRecord` that fetches fields on first access via `__getattr__`; not the gateway proxy used in ch20 | `__getattr__`, `__getattribute__`, `__setattr__`, `object.__getattribute__` | Infinite recursion in `__getattr__`; typo attribute returns `None` instead of raising |
| 31 | Shortcut patterns: dict dispatch and EAFP | 🔬 📘 | dissolve | Dispatch table for document types; EAFP vs LBYL when reading an EDI segment | `dict[DocumentKind, Callable]`, `try/except KeyError`, `dict.get`, `contextlib.suppress` | LBYL check-then-use race in a shared cache; if-chain misses a new kind |
| 32 | Anti-patterns and pattern misuse | 📗 | n.a. | The over-abstracted rating engine (factory of strategy of visitor for a flat fee) | the ch1 rating function vs an eight-class version | Eight-class version needs 6 files touched for a new surcharge; simple version needs 1 |
| 33 | Seams in Python | 🔬 | n.a. | A legacy `RateEngine` with module-level imports and a hard-wired carrier call | `unittest.mock.patch`, `monkeypatch`, module attributes, `importlib` | Test of legacy engine hits the real carrier call; patch applied to the wrong namespace has no effect |
| 34 | Dependency-breaking techniques | 🔬 📗 | n.a. | Breaking the same engine's dependencies (parameterise, extract callable, wrap) | `functools.partial`, injected callable, `Protocol` | Characterisation test pins current behaviour before each break, none may change |
| 35 | Fowler vs Feathers | 📗 | n.a. | The same engine under Fowler (refactor with tests) and Feathers (get under test first) | characterisation tests, `pytest` golden values | Refactor without characterisation changes a rounding rule and a golden test fails |
| 36 | Refactor or rewrite | 📗 | n.a. | The rate engine: refactor or rewrite | same engine, strangler-style adapter | Rewrite diverges from legacy on a boundary weight; parity test fails |
| 37 | The GIL and performance | 📘 🔬 | disambiguate | Rating a batch of consignments (CPU-bound) vs fetching carrier tracking (I/O-bound): threads vs processes vs asyncio | `threading`, `concurrent.futures.ProcessPoolExecutor`, `asyncio`, a benchmark script with recorded output; no free-threading | Tests assert correctness only (same results from all three); speed claims come from the benchmark script output, never assertions |
| 38 | asyncio and the patterns | 🔬 | survive / dissolve | Handling-event feed as an async generator (Iterator), `async with` gateway session, coroutine Commands, Observer over an async queue | `async def`, `AsyncIterator`, `async with`, `asyncio.Queue`, `asyncio.Event`, `asyncio.gather`, `TaskGroup` | Deterministic tests via `Event` and `gather`, no sleep: forgotten `await` returns a coroutine not a result; cancelled task leaves a session open |
| 39 | Final project | 🔬 | n.a. | Booking, rating, routing, tracking, clearance, invoice end to end | all seven areas wired through a composition root | End-to-end acceptance test fails until every stage is integrated |
| 40 | Working with AI and LLM tools | 🔬 | n.a. | Reviewing LLM-generated pattern code in the shipping domain | a Java-in-Python generated `RateStrategyFactory`, then the idiomatic version | Review checklist test: generated code fails mypy strict or idiom scan; the corrected version passes |
| A | Build and toolchain reference (uv, ruff, mypy) | 📘 | n.a. | Commands used across the book | `uv`, `ruff`, `mypy --strict` | n.a. (reference) |
| B | pytest reference | 📘 | n.a. | Fixtures and parametrisation used in the examples | `pytest` | n.a. (reference) |
| C | pytest-mock and unittest.mock reference | 📘 | n.a. | Autospec and patch targets | `mocker`, `create_autospec` | n.a. (reference) |
| D | Test patterns (Meszaros) | 📗 | n.a. | Test doubles named in the shipping tests | fake, stub, spy, mock | n.a. (reference) |
| E | Pattern-to-force quick reference | 📗 | n.a. | One line per pattern and its force | table | n.a. (reference) |
| F | Programming principles reviewed in code | 📗 | n.a. | DRY, YAGNI, KISS, Law of Demeter on shipping code | small before/after snippets | n.a. (reference) |

## Non-overlap rules

- **ch20 vs ch26**: ch20 is the GoF Decorator as runtime object wrapping on the
  `RateCalculator` Protocol (discount, surcharge, tax), contrasted with `@retry` /
  `@audited` on `quote()`. ch26 uses only the Documentation renderers (`@timed_render`,
  `@cached_for`, class decorator for `DocumentKind`) and never touches `RateCalculator`.
- **ch25 vs ch28**: ch25 shows Visitor via singledispatch as one of three mechanisms
  over `Document` kinds. ch28 teaches singledispatch in depth on commodity types and a
  `Packaging` hierarchy; no `Document` visitor there.
- **ch20 vs ch30**: ch20 Proxy is a caching proxy over `CarrierGateway`. ch30 is a lazy
  `TrackingRecord` using `__getattr__`; no gateway there.

## Cross-cutting requirements

- Python 3.14 floor; type hints checked with `mypy --strict`.
- Tests are deterministic: no `time.sleep`, no wall-clock assertions; async tests use
  `asyncio.Event` and `gather`.
- Each example is a uv workspace member runnable from its own directory (see r01 plan).
