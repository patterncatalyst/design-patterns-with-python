---
title: "Shipping domain model"
order: 8
output: false
---

# PDP-008: shipping domain model

Internal planning file, excluded from the site. Revised 2026-11-03 after the r01 spikes (see spikes.md).
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
| 9 | Protocol and structural typing | 📘 📗 | dissolve (Null Object via Optional) | Carrier lookup that may find nothing; `NullGateway` vs `Optional[CarrierGateway]`; callback Protocol `RateStrategy` (PDP-011) | `Protocol`, `Quoter[T: Consignment]` (PEP 695, variance inferred, no `contravariant=True`), callback Protocol `__call__(self, c, /)` (positional-only `/` or parameter names must match), `typing.override`, `runtime_checkable` (checks name presence only: wrong signature and a non-callable attribute still pass `isinstance`), `X \| None`, mypy | mypy fails on `lookup(c).book(...)` when `None` is possible; runtime `AttributeError` on a missing carrier; a narrower `HazmatQuoter` is rejected as `Quoter[Consignment]`. Caveat: a `Mock` passed for a Protocol parameter is `Any` to mypy, so there is no static protection; recommend `create_autospec` and say so plainly |
| 10 | Context managers | 📘 | survive (Resource Acquisition) | `ManifestWriter` holding a file handle; ledger append under `async with` preview | `contextlib.contextmanager`, `ExitStack`, `__enter__/__exit__` | File handle left open after an exception mid-write; test asserts the handle is closed |
| 11 | Testing with pytest, pytest-mock, and mypy | 📗 📘 | n.a. | The rating engine under pytest with a mocked gateway | `pytest.fixture`, `parametrize`, `mocker.create_autospec(..., instance=True)`, `monkeypatch` | A mock without autospec accepts a misspelled `quote_all` call and the test passes wrongly. Same caveat as ch9: `Mock`, `Mock(spec=)`, `MagicMock(spec=)` and autospec are all `Any` to mypy, so mypy does not check them; only `create_autospec` enforces the call signature at runtime (`TypeError: missing a required argument`) |
| 12 | Strategy: the callable | 🔬 📘 | dissolve | Rate quotes priced three ways (flat, per-kg, zone) | `Callable[[Consignment], Money]`, `dict[str, Callable]`, `functools.partial` | Class-per-strategy needs three classes and a registry to pass the same table of cases a dict of functions passes |
| 13 | Template Method and the function alternative | 📗 | dissolve / survive | Customs declaration generation varying by destination | hook functions, `Protocol` with defaults, `abc.ABC` only where state is shared | A subclass forgets to call a base step; the function pipeline cannot omit it |
| 14 | State and finite state machines | 📗 📘 | survive | Consignment lifecycle FSM plus a probabilistic transit-delay machine (series parity) | frozen dataclass states, `type State = A \| B \| C` alias, transitions by `match` ending in `case _: assert_never(...)`, transition `dict`, seeded `random.Random` | Illegal transition (Delivered to Received) is accepted; adding a state fails mypy (`Argument 1 to "assert_never" has incompatible type ...; expected "Never"`) until every transition handles it; probabilistic machine's seeded run is not reproducible without injected RNG |
| 15 | Command, undo, and command queues | 📗 | survive | Booking amendments with undo; queue of pending commands | frozen `Amendment` dataclass, `apply`/`undo` callables, `collections.deque` | Undo after two amendments restores the wrong state when commands share mutable data |
| 16 | Factory Method and Abstract Factory | 🔬 📗 | dissolve | A gateway per carrier, resolved by name | `dict[Carrier, Callable[[], CarrierGateway]]`, classmethod constructors | Adding a carrier requires editing an if-chain in three places |
| 17 | Builder, dataclasses, and Prototype | 📘 📗 | dissolve | A booking request with many optional fields; amendments by `replace` | keyword-only dataclass, `field(default_factory=...)`, `replace`, `copy.copy` | Positional constructor with 12 arguments is swapped silently; shallow copy shares a list |
| 18 | Singleton: module, Borg, metaclass | 📘 📗 | dissolve / disambiguate | The tariff table: expensive to load, needed everywhere | module-level object built at import time, `functools.cache`, `threading.Lock` with double check, `Borg`, `Singleton` metaclass | Two importers see two tariff loads under the naive class; test isolation leaks state between tests. Under threads `functools.cache` is not call-once (a barrier-forced loader runs twice, PDP-015); build at import time, or use a Lock with a double check (runs once) |
| 19 | Adapter, Facade, Bridge | 📗 📘 | survive | Three carrier APIs behind one `CarrierGateway`; weight and money unit conversions | adapter classes and `functools.singledispatchmethod`-free wrappers, `Protocol` | Calling code branches on carrier name; unit mix-up (lb vs kg) passes silently |
| 20 | Decorator pattern vs decorator syntax, and Proxy | 🔬 | disambiguate | Headline spike (PDP-010): a `RateCalculator` Protocol wrapped at runtime by `FuelSurcharge`, `VolumeDiscount`, `Vat`, `HandlingFee` frozen dataclasses (no base class), vs `@retry(attempts=, on=)` / `@audited(sink)` on the function `quote_carrier()`; plus a caching proxy over a slow gateway. Open with the two one-liners `Vat(FuelSurcharge(BaseRate(...)))` vs `quote_carrier = retry(...)(quote_carrier)` | `RateCalculator`, `BaseRate`, `FuelSurcharge`, `VolumeDiscount`, `Vat`, `HandlingFee`, `compose(base, layers)` with `type Layer = Callable[[RateCalculator], RateCalculator]`, `retry` and `audited` as PEP 695 `[**P, R]` factories, `CarrierTimeoutError` (ruff N818 wants the `Error` suffix), `functools.wraps`, `ParamSpec`, `CachingGateway` | Order-matters witness uses an additive `HandlingFee` (or a cap or rounding), not discount vs VAT: pure percentage layers commute, so that demo would pass both ways. Second witness: the stack is data (layers added or removed per consignment at runtime, inner object never mutated), which a function decorator cannot do; an `@`-wrapped function has no `quote` and `@` rebinds the name at definition time (`f is not f.__wrapped__`). `__wrapped__` is not on `Callable`; reading it needs one `# type: ignore[attr-defined]` |
| 21 | Composite and Flyweight | 📗 📘 | survive | Consolidated shipments; port and commodity codes interned | `Shipment` tree of `Consignment`, `sys.intern`, `__slots__`, `weakref.WeakValueDictionary` | Total weight misses nested groups; equal port codes are distinct objects (`is` fails) |
| 22 | Observer | 📘 🔬 | dissolve / survive | Handling events raised as cargo moves | list of callables, `weakref.WeakMethod`, `Signal` helper | Subscriber raising stops delivery to later subscribers; unsubscribed bound method is kept alive |
| 23 | Mediator and Chain of Responsibility | 📗 📘 | survive | Customs clearance chain | `ClearanceCheck` callables, `Iterable[ClearanceCheck]`, `ClearanceResult` | A check added in the wrong order clears a restricted commodity; chain with no terminal default returns `None` |
| 24 | Iterator, generators, and the iterator protocol | 📘 📗 | dissolve | Paging a tracking history lazily | generator functions, `itertools.islice`, `__iter__`, `yield from`; async generator forward-pointer to ch38 | Eager list of 1M events is fully built to read the first page; iterator exhausted on second pass. Async note: `break` out of `async for` does not run the async generator's `finally`; use `contextlib.aclosing` and annotate `AsyncGenerator[...]`, not `AsyncIterator`, or mypy rejects `aclosing`/`aclose` |
| 25 | Visitor, Memento, Interpreter | 📗 🔬 | dissolve (Visitor, one of three) / survive | Visitor over `Document` kinds as singledispatch vs `match` vs classic double dispatch; Memento for an amendment rollback; Interpreter for tariff rule expressions | `singledispatch` (replaces Visitor but has no double dispatch: dispatch on the first argument, then `match` on the second, as in `load_plan(cargo, vehicle)`), `type Document = A \| B \| C` union + `match` + `assert_never` for a closed hierarchy (singledispatch gives no exhaustiveness check), frozen snapshot dataclass, small `Expr` tree | New document kind silently ignored by singledispatch but fails mypy under union + `match` + `assert_never`; mutated memento corrupts rollback |
| 26 | Decorators done right | 📘 🔬 | survive | Decorating the Documentation renderers (not the rating path): `@timed_render`, parametrised `@cached_for(seconds)`, a class decorator registering `DocumentKind`, stacking order | `functools.wraps`, `ParamSpec`, `Callable[P, R]`, class decorators | Decorated function loses `__name__`/signature; parametrised decorator used bare silently drops the function; wrong stack order changes cache behaviour |
| 27 | Descriptors and properties | 📘 | survive | Validated `Weight` kg field reused across `Consignment`, `Dimensions`, `Container` | `__set_name__`, `__get__`, `__set__`, `property`, `cached_property` | Copy-pasted property validators drift; a validator on one field is missing on another |
| 28 | singledispatch | 📘 🔬 | survive | Customs tariff code lookup by commodity type, and `singledispatchmethod` on a `Packaging` hierarchy (not Document kinds) | `functools.singledispatch`, `singledispatchmethod`, `register`, type-annotation registration (`A \| B` registers both), `register(Later, fn)`, `object` fallback | Unregistered type falls to the default silently; registration order import-dependent. Caveats from PDP-012: define classes before registering (a forward reference raises `TypeError: Invalid annotation ... unresolved forward reference` at registration on 3.14, no `from __future__ import annotations` needed); use an `object` fallback for open-ended dispatch because mypy does not model dispatch (registering `int` against a `Cargo` fallback is `[misc]`; return types must match the fallback, `[arg-type]`); registrations are global, process-wide state; no exhaustiveness check |
| 29 | Metaclasses, `__init_subclass__`, and registries | 📘 🔬 | dissolve | Auto-registered carrier adapters by `carrier_code` (PDP-013: `Carrier`, `RoadCarrier`, `Northwind(code="NWD")`, `Meridian(code="MRD")`, `DuplicateCarrierError`). Lead with `__init_subclass__`; the metaclass (`CarrierMeta`) is the second half | `__init_subclass__(cls, *, code=None, **kwargs)` (mypy checks class keywords; no `type: ignore`), `ClassVar[dict[str, type[Carrier]]]`, `type`, `abc.ABCMeta`; metaclass only for abstractness validation at creation (`__init_subclass__` runs before `ABCMeta` computes `__abstractmethods__`), `__prepare__` / namespace rewriting, class-level dunders (`__call__`, `__getitem__`, `__instancecheck__`) | Forgotten manual registration means carrier unavailable at runtime; duplicate code raises and keeps the original; unknown class keyword raises `TypeError`; metaclass conflict when mixing. With a metaclass mypy never checks class keywords and needs two targeted ignores (`[attr-defined]`, `[assignment]`); `-> Self` in a metaclass `__new__` is rejected |
| 30 | Dynamic attributes and Proxy | 📘 🔬 | survive | Lazy `TrackingRecord` that fetches fields on first access via `__getattr__`; not the gateway proxy used in ch20 | `__getattr__`, `__getattribute__`, `__setattr__`, `object.__getattribute__` | Infinite recursion in `__getattr__`; typo attribute returns `None` instead of raising |
| 31 | Shortcut patterns: dict dispatch and EAFP | 🔬 📘 | dissolve | Dispatch table for document types; EAFP vs LBYL when reading an EDI segment | `dict[DocumentKind, Callable]`, `try/except KeyError`, `dict.get`, `contextlib.suppress` | LBYL check-then-use race in a shared cache; if-chain misses a new kind |
| 32 | Anti-patterns and pattern misuse | 📗 | n.a. | The over-abstracted rating engine (factory of strategy of visitor for a flat fee) | the ch1 rating function vs an eight-class version | Eight-class version needs 6 files touched for a new surcharge; simple version needs 1 |
| 33 | Seams in Python | 🔬 | n.a. | A legacy `RateEngine` with module-level imports and a hard-wired carrier call | `unittest.mock.patch`, `monkeypatch`, module attributes, `importlib` | Test of legacy engine hits the real carrier call; patch applied to the wrong namespace has no effect |
| 34 | Dependency-breaking techniques | 🔬 📗 | n.a. | Breaking the same engine's dependencies (parameterise, extract callable, wrap) | `functools.partial`, injected callable, `Protocol` | Characterisation test pins current behaviour before each break, none may change |
| 35 | Fowler vs Feathers | 📗 | n.a. | The same engine under Fowler (refactor with tests) and Feathers (get under test first) | characterisation tests, `pytest` golden values | Refactor without characterisation changes a rounding rule and a golden test fails |
| 36 | Refactor or rewrite | 📗 | n.a. | The rate engine: refactor or rewrite | same engine, strangler-style adapter | Rewrite diverges from legacy on a boundary weight; parity test fails |
| 37 | The GIL and performance | 📘 🔬 | disambiguate | Rating a batch of consignments (CPU-bound) vs fetching carrier tracking (I/O-bound): threads vs processes vs asyncio | `threading`, `Barrier`, `dis`, `concurrent.futures.ProcessPoolExecutor`, `asyncio`, `bench/gil_bench.py` with recorded output (`gil_bench.out.txt`); no free-threading | The natural `self.count += 1` race did not reproduce in 600 runs on 3.14 (4 threads x 5000, default and 1 us switch interval), so it is a prose claim only ("the GIL does not make `+=` atomic"). Demonstrate with a seam: `dis` shows LOAD_ATTR / BINARY_OP / STORE_ATTR, a `between=` hook plus `Barrier(2)` loses an update every time (1, not 2), a Lock gives 8000 of 8000. Tests assert correctness and forced interleavings only; speed claims come from the benchmark script output, never assertions; prose also covers pool start-up, pickling and memory costs of processes |
| 38 | asyncio and the patterns | 🔬 | survive / dissolve | Handling-event feed as an async generator (Iterator), `async with` gateway session, coroutine Commands, Observer over an async queue | `async def`, `AsyncGenerator[...]` (not `AsyncIterator`), `contextlib.aclosing`, `asynccontextmanager`, `asyncio.Queue` with None sentinel, `asyncio.Event`, `asyncio.gather`, `TaskGroup` with `except*`, `asyncio.timeout(0)` | Deterministic tests via `Event`, `sleep(0)` and `gather`, no wall-clock: forgotten `await` returns a coroutine not a result; `break` out of `async for` skips the generator's `finally` unless wrapped in `aclosing`; cancelled task leaves a session open; an `await` between read and write loses updates (5 workers give 1; no await or `asyncio.Lock` gives 5). Never assert that something finishes inside a timeout; `sleep(0)` creation order is a CPython detail, say so |
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
  `RateCalculator` Protocol (`FuelSurcharge`, `VolumeDiscount`, `Vat`, `HandlingFee`),
  contrasted with `@retry` / `@audited(sink)` on `quote_carrier()`. The overlap case (a
  decorator function that returns a wrapper object) gets one paragraph in ch20, not a
  section; the syntax-specific teaching (`functools.wraps`, `ParamSpec`) stays in ch26. ch26 uses only the Documentation renderers (`@timed_render`,
  `@cached_for`, class decorator for `DocumentKind`) and never touches `RateCalculator`.
- **ch25 vs ch28**: ch25 shows Visitor via singledispatch as one of three mechanisms
  over `Document` kinds (no double dispatch; closed hierarchies prefer union + `match` +
  `assert_never`). ch28 teaches singledispatch in depth on commodity types and a
  `Packaging` hierarchy (registration, forward-reference, mypy and global-state caveats);
  no `Document` visitor there.
- **ch9 vs ch11**: ch9 owns the Protocol facts (positional-only `/`, inferred variance,
  `runtime_checkable` is presence-only) and states the mock-is-`Any` caveat once; ch11
  repeats the caveat only as the reason to use `create_autospec`.
- **ch24 vs ch38**: ch24 keeps sync generators; the async-generator `aclosing` finding
  is a note in ch24 and taught in full in ch38.
- **ch18 vs ch37**: ch18 owns `functools.cache` not being call-once under threads; ch37
  only refers back to it when discussing the GIL.
- **ch20 vs ch30**: ch20 Proxy is a caching proxy over `CarrierGateway`. ch30 is a lazy
  `TrackingRecord` using `__getattr__`; no gateway there.

## Cross-cutting requirements

- Python 3.14 floor; type hints checked with `mypy --strict`.
- Tests are deterministic: no `time.sleep`, no wall-clock assertions; async tests use
  `asyncio.Event` and `gather`.
- Each example is a uv workspace member runnable from its own directory (see r01 plan).
