---
title: "r08 plan: chapters 16-18 (Part 6, creating objects under control)"
order: 8
output: false
render_with_liquid: false
---

# r08: chapters 16-18, factories, Builder and Prototype, Singleton

Opus-planned 2026-11-04. Branch `release/r08` (from main at 2506655). This file is the source of truth for r08 scope, criteria and status. Executors never edit it; the orchestrator updates the status board. There's no toolchain work this iteration: Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged, and `uv.lock` changes only because three members are added.

## User decisions (2026-11-04, confirmed by the owner)

Owner answers 2026-11-04: every decision below takes the recommended option (all three chapters in r08, built in sequence, Singleton splitting to r08b only if a third repair round is needed; chapter 18 owns the cache-under-threads trap, `LoadOnce` with an injected lock, and PEP 810 `lazy import`; I step ids; generic `CarrierKit[R]`; the listed supporting names; the GoF creator hierarchy count; both chapter 17 comparison fixtures; Borg, metaclass and `__new__` as test fixtures; *Python Cookbook* 1st ed. added with a hub PR at I0b (superseded the same day, see below); domain rows 16-18 updated at I0).

Each decision carries a recommendation. Nothing below is built until the owner answers.

1. **Step ids are `I*`.** `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md` (`scripts/validate.py` lines 730-731 glob them all, and the row regex at line 696 needs `| <id> | ... | done |`). `G*` (r06) and `H*` (r07) are taken and `done`, so a reused id would resolve against an old row without proof. r08 uses `I0`, `I0b`, `I1a`, `I1b`, `I1c`, `I2`-`I7`; `grep -nE "^\| I[0-9]" _plans/*.md` matched nothing before this file.

   **Recommend: yes.** The alternative is to scope `run:` tokens per plan in `validate.py`, which is a script change plus a self-test case.

2. **Three chapters in one iteration.** The roadmap groups 16-18 as r08. The three members are independent (no shared code), all three are pattern chapters in Part 6, and r05 shipped three chapters. The risk is executor and validator load, not design coupling.
   - (a) Keep all three in r08, with the members built in sequence (I1a, I1b, I1c, one `uv lock` each) and three prose agents in parallel at I5.
   - (b) Split: r08 ships chapters 16-17, and chapter 18 moves to its own iteration (r08b, step ids `J*`). Chapter 18 carries the most new evidence (lazy imports, threads, three comparison fixtures).

   **Recommend: (a).** Fall back to (b) only if I1c's deletion table or the I6 validation needs a third repair round; the orchestrator can then cut chapter 18 out of the PR without touching 16-17.

3. **Chapter 16's Abstract Factory is a generic frozen kit, tied by the reference type, behind a small Protocol.**
   - `CarrierKit[R]` is a frozen slotted kw-only dataclass whose fields are the family's constructors: `gateway: Callable[[CarrierSettings], CarrierGateway[R]]`, `label_printer: Callable[[], LabelPrinter[R]]`, `rates: Callable[[], RateSource]`, plus one method `ship(...) -> Shipment` that uses only its own products.
   - The gateway returns a carrier-specific `NewType` reference (`FastlineReference`, `AircoReference`) and the label printer takes it, so a kit that mixes a Fastline gateway with an Airco label printer is a mypy error (`Cannot infer value of type parameter "R" of "CarrierKit"  [misc]`, planning evidence).
   - The registry is `KITS: Mapping[str, Shipper]` (a `frozendict`), where `Shipper` is a one-method Protocol. Typing it as `CarrierKit[str]` is rejected (the kit is invariant in `R`), and typing it as a union of kits makes every use an error, so the parameter is hidden behind `ship`.
   - The measured limits are the lesson: mypy ties products that pass values to each other, and nothing else. A rate source exchanges nothing with the other products, so a kit with another carrier's rates is accepted; a label printer typed to take any `str` fits every family. One kit value, chosen once, is what keeps those consistent.

   **Recommend: yes.** Alternatives:
   - (b) A plain kit with Protocol-typed fields and no type parameter. Simpler, but mypy accepts every mix, so the chapter's only family check would be a runtime test.
   - (c) The GoF shape: a `CarrierKit` Protocol with `create_gateway`, `create_label_printer` and `create_rates`, and one kit class per carrier. It adds two classes per carrier and gives mypy nothing more than (b).

4. **New supporting names, recorded in domain rows 16-18 at I0.** No new domain area and no new carrier codes (`FASTLINE` and `AIRCO` only).
   - Chapter 16 (Carrier, Rating): `CarrierSettings`, `FastlineReference`, `AircoReference`, `CarrierGateway[R]` (a generic form of the series Protocol, `book` only), `LabelPrinter[R]`, `RateSource`, `FastlineLabelPrinter`, `AircoLabelPrinter`, `FastlineRates`, `AircoRates`, `GatewayFactory`, `GATEWAYS`, `make_gateway`, `CarrierKit`, `Shipper`, `Shipment`, `FASTLINE_KIT`, `AIRCO_KIT`, `KITS`, `ship`, `UnknownCarrierError`. `CarrierQuote` and `Money` are reused.
   - Chapter 17 (Consignment, Billing names reused): `BookingRequest` (twelve fields, listed in the example spec), `CarrierCode`, `ServiceLevel`, `BookingError`, `TEMPLATES`, `from_template`.
   - Chapter 18 (Rating): `TariffTable`, `tariff_table` (module), `TARIFF`, `load_tariff`, `LOAD_LOG` (in `loads.py`), `quote`, `quote_standard`, `LoadOnce`, `NOT_LOADED`, `RatingError`.

   **Recommend: yes.** The alternative for chapter 16 anchors the products in existing entities (a `BillOfLading` writer for the label, a `Tariff` for the rates). It reuses more names but makes the family's value exchange (reference to label) less obvious, and `BillOfLading` belongs to Template Method and Documentation chapters.

5. **Factory Method counts for reconciliation row 1.** Row 1 moved "type and line counts" to the Factory chapter. Chapter 16 keeps a GoF creator hierarchy as a test-only comparison fixture (`_BookingDesk(ABC)` with an abstract `create_gateway`, and `_FastlineDesk`, `_AircoDesk`). It runs the same behaviour table as the registry, and an `ast` test counts three creator classes in the fixture against none in `factories.py`, in the r06 row 65 shape. Row 1 gets the note "Factory Method counts witnessed by row 85 (r08)".

   **Recommend: yes.** If no, row 1 gets "Factory Method dissolve witnessed by row 85; no count", and test 5 is dropped.

6. **Chapter 17 has two comparison fixtures on one booking table.** The kw-only `BookingRequest` is the lesson. Beside it, test-only:
   - `_LegacyBookingRequest`, a twelve-argument positional constructor with the same checks. It shows the silent swap: two `str`, two `bool` or two port codes swapped positionally pass mypy and build a wrong request (planning evidence).
   - `_BookingRequestBuilder`, a fluent GoF builder. It shows the cost Builder adds: a required step left out is a `ValueError` at `build()`, and mypy reports nothing, where the dataclass call is `[call-arg] Missing named argument "destination"`.
   - All three forms run the same four-case booking table (`[keyword|positional|builder]`), so the comparison is measured. Chapter 17 shows at most one short excerpt of each fixture inside the six-excerpt limit.

   **Recommend: yes.** Alternative (b): the positional fixture only, with the fluent builder described in prose. That leaves "Builder dissolves" without the measured cost of the builder itself.

7. **Chapter 18 owns the thread finding, bounded.** Domain row 18 says "Chapter 18 owns this finding", and row 37 says "Refers back to chapter 18 for `functools.cache` not being call-once"; CLAUDE.md says "build at import time or use a Lock with a double check". So chapter 18 teaches:
   - `functools.cache` runs a loader twice when two threads arrive together (a `Barrier` inside the loader forces it);
   - `LoadOnce[T]` with a double-checked `threading.Lock` runs it once. The lock is injected (`lock=`, default `threading.Lock()`), so a test passes a gated lock whose `__enter__` waits on a `Barrier(2)`: both threads have passed the first check before either takes the lock, and deleting the inner check gives two loads every time (planning evidence, 3 runs).
   - Out of scope, pointed to "The GIL and performance" by title: the GIL, `+=` atomicity, threads against processes, free-threaded builds, and the thread-safety of `dict` or `deque`.

   **Recommend: yes.** Alternative (b): point forward only, with `functools.cache` named in one sentence. That contradicts domain row 18 and leaves CLAUDE.md's "Lock with a double check" untaught.

8. **Chapter 18 uses PEP 810 `lazy import` as the lazy rung.** The r05 plan reserved it ("`lazy import` (it belongs with module singletons)"). The ladder is:
   1. a module built at import time (the default; one sentence and a pointer to "What 1994 assumed, and what Python dissolves" for the shape already shown there);
   2. `lazy from singleton import tariff_table` at the importer, which defers the load to first use and keeps it once. PEP 810 says "Exactly one thread performs the import" (fetched 2026-11-04);
   3. the table passed in as a parameter, which is how tests and tenants get their own;
   4. `LoadOnce` only when the load needs something that exists only at run time.

   **Recommend: yes.**

9. **Borg, the metaclass and the `__new__` form are test-only comparison fixtures.** `src/` holds the module, the lazy importer, `quote` with an injected table, and `LoadOnce`. `tests/test_variants.py` holds `_TariffBorg`, `_SingletonMeta`/`_MetaTariffTable` and `_NewTariffTable`. All of them, plus the module and `LoadOnce`, run one behaviour table ("every caller reads the same rates"), and each fixture gets one test for what it costs:
   - Borg instances share state but are distinct and compare unequal;
   - the metaclass silently ignores a second call's arguments, and mypy types every call by `__init__`;
   - the `__new__` form reruns `__init__` on every call and overwrites the shared instance.

   The `__new__` form isn't in the chapter title. It's included because it's the form assistants most often write, and the sidebar checks for it. Metaclass mechanics (`__call__`, conflicts with `ABCMeta`, `__prepare__`) are pointed to "Metaclasses, __init_subclass__, and registries" by title.

   **Recommend: yes.** Alternative (b): Borg and the metaclass in `src/` as taught variants. That puts two forms the chapter argues against beside the default as if they were equals.

10. **Books and online sources.**
    - GoF (all five creational patterns), credited by pattern name and the catalogue's standard sections, never quoted (r06 finding: GoF can't be opened through the O'Reilly MCP).
    - Schmidt, Stal, Rohnert and Buschmann, *Pattern-Oriented Software Architecture, Volume 2* (Wiley, 2000), already in `bibliography.html` and in hub `books.yml` with `design-patterns-with-python` in `referenced_by`. Chapter 18 credits it for double-checked locking, [only if a prose agent verifies the pattern name "Double-Checked Locking Optimization" in the book's contents].
    - Alex Martelli's Borg. The online origin is ActiveState recipe 66531, "Singleton? We don't need no stinkin' singleton: the Borg design pattern" (https://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/). The O'Reilly catalogue lists *Python Cookbook* (Martelli and Ascher, O'Reilly, 2002, 0596001673) with a recipe "Avoiding the Singleton Design Pattern with the Borg Idiom" (https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s23.html). *Python Cookbook* 2nd ed. (Martelli, Ravenscroft and Ascher, 2005, 0596007973) is also listed, and its recipe title is unverified. The 3rd edition (Beazley and Jones, 2013) is a different book.
    - Brandon Rhodes, python-patterns.guide pages "The Factory Method Pattern", "The Abstract Factory Pattern", "The Builder Pattern", "The Prototype Pattern", "The Singleton Pattern" and "The Global Object Pattern" (index fetched 2026-11-04). Online, already linked from "The three-way split: dissolve, survive, disambiguate". No bibliography change.
    - Ramalho, *Fluent Python* 2nd ed. ("Data Class Builders") and Slatkin, *Effective Python* 3rd ed. (keyword-only arguments), both already in the bibliography and hub. Credited in chapter 17 for further reading [chapter and item titles only if a prose agent verifies them].

    **Recommend:** add *Python Cookbook* (first edition, 2002) as a new book: step I0b verifies the edition and recipe title, adds the bibliography row and the hub `books.yml` entry with a `review_note`, and I7 opens the hub PR. Chapter 18 credits Martelli by name and the recipe in both places. Alternative (b): credit the ActiveState recipe only (no new book, no hub PR). That's weaker because the Cookbook recipe is the printed source.

11. **Domain rows 16-18 are updated at I0** with the decision 4 names, plus:
    - row 16: "the GoF creator hierarchy is a test-only comparison fixture"; the failing test becomes `test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate`;
    - row 17: the positional and fluent-builder fixtures; `copy.replace`, `copy.deepcopy`, `TEMPLATES`; the failing tests `test_a_positional_constructor_accepts_a_swapped_origin_and_destination` and `test_a_shallow_copy_shares_the_documents_list`;
    - row 18: `lazy import` (PEP 810), `LoadOnce` with the `NOT_LOADED` sentinel and an injected lock, and Borg, metaclass and `__new__` as test fixtures. The row keeps its "never say `functools.cache` makes a singleton" rule.

    **Recommend: yes.**

## Planning evidence

All runs were read-only, from the session scratch directory outside the repo (`.../scratchpad/r08plan`):
- Runtime: `~/.local/bin/python3.15 -I` (3.15.2). Package spikes use `PYTHONPATH=src` without `-I`.
- mypy: `uv run --no-project --python 3.15.2 --with mypy==2.4.1 python runmypy.py`, which calls `mypy.api.run(['--strict', '--warn-unreachable', '--cache-dir', os.devnull, '--no-error-summary', '-c', SNIPPET])`.
- ruff: `uv run --no-project --with ruff==0.17.3 ruff check --isolated --target-version py315`.

Each item below becomes a test or a reconciliation row. Every experiment output is a prediction until the build quotes it as observed. Snippets were reduced models; line numbers will differ and are never asserted.

mypy 2.4.1, chapter 16:
- **A `Callable` slot checks the constructor; a `type[Protocol]` slot doesn't (surprise).** `CarrierGateway` is a Protocol with `book`. `FastlineGateway()` takes no arguments; `AircoGateway(account: str)` takes one.
  - `Mapping[str, Callable[[], CarrierGateway]] = {"FASTLINE": FastlineGateway, "AIRCO": AircoGateway}`:
    `<string>:24: error: Dict entry 1 has incompatible type "str": "type[AircoGateway]"; expected "str": "Callable[[], CarrierGateway]"  [dict-item]`
  - The same classes in `Mapping[str, type[CarrierGateway]]` exit clean, and so does `BY_TYPE[code]()`. At run time `BY_TYPE["AIRCO"]()` raises `TypeError("AircoGateway.__init__() missing 1 required positional argument: 'account'")`. mypy can't check the call because a Protocol has no constructor signature.
  - A `partial(AircoGateway, "ACC-1")` fits the `Callable` slot and is rejected by the `type` slot: `Dict entry 0 has incompatible type "str": "partial[AircoGateway]"; expected "str": "type[CarrierGateway]"  [dict-item]`.
  - The Protocol itself in a `type[...]` slot: `Only concrete class can be given where "tuple[str, type[CarrierGateway]]" is expected  [type-abstract]`. Runtime `CarrierGateway()`: `TypeError('Protocols cannot be instantiated')`.
- **Classmethod constructors in the slot.** `type GatewayFactory = Callable[[CarrierSettings], CarrierGateway]` with `FastlineGateway.from_settings` and `AircoGateway.from_settings` (`-> Self`) exits clean. `reveal_type(AircoGateway.from_settings)` is `"def (settings: __main__.CarrierSettings) -> __main__.AircoGateway"`. A `from_env(cls, env: Mapping[str, str]) -> Self` in the same slot:
  `<string>:39: error: Dict entry 0 has incompatible type "str": "Callable[[Mapping[str, str]], AircoGateway]"; expected "str": "Callable[[CarrierSettings], CarrierGateway]"  [dict-item]`
- **`Self` against a hard-coded class.** A classmethod `-> "AircoGateway"` returning `AircoGateway(account)` reveals `"__main__.AircoGateway"` when called on a subclass, and the runtime gives `AircoGateway(account='A')`. The `cls(account)` / `-> Self` form reveals and returns `SandboxAircoGateway`. Returning `AircoGateway(...)` from a `-> Self` method: `Incompatible return value type (got "AircoGateway", expected "Self")  [return-value]`.
- **The GoF creator hierarchy.** An ABC `BookingDesk` with an abstract `create_gateway` and a subclass that forgets to override it: `Cannot instantiate abstract class "ForgetfulDesk" with abstract attribute "create_gateway"  [abstract]`. The complete hierarchy exits clean.
- **The if-chain in three places.** `make_gateway`, `make_labels` and `make_rates` each branch on a `str` code, and `AIRCO` was added to two of the three. mypy exits 0 with empty output. At run time, `ship("AIRCO", "CN-1", Decimal(10))` gives `('AIRCO|AC-CN-1', Decimal('12.00'))`: an Airco booking at Fastline's rate (48.00 expected). With `type CarrierCode = Literal["FASTLINE", "AIRCO"]` and a `match` ending in `assert_never`:
  `<string>:8: error: Argument 1 to "assert_never" has incompatible type "Literal['AIRCO']"; expected "Never"  [arg-type]`
- **Family consistency.**
  - A plain kit (`CarrierKit(gateway: Callable[[], CarrierGateway], labels: Callable[[], LabelPrinter])`) built with a Fastline gateway and Airco labels exits 0.
  - The generic kit (the decision 3 shape, full chapter model in `s/f10_full.py`): `FASTLINE_KIT`/`AIRCO_KIT` reveal `"__main__.CarrierKit[__main__.AircoReference]"` for Airco; the mixed kit gives `<string>:79: error: Cannot infer value of type parameter "R" of "CarrierKit"  [misc]`. A direct call `p.label(g.book("CN-1"))` with mismatched families gives `Argument 1 to "label" of "LabelPrinter" has incompatible type "FastlineRef"; expected "AircoRef"  [arg-type]`.
  - The registry typed as a union of kits makes both `ship(KITS[code], ...)` (`Cannot infer value of type parameter "R" of "ship"  [misc]`) and inline use (two `[arg-type]` errors on `"FastlineRef | AircoRef"`) fail. `KITS: Mapping[str, Shipper]` exits clean.
  - `Mapping[str, CarrierKit[str]]` with the Fastline kit: `Dict entry 0 has incompatible type "str": "CarrierKit[FastlineReference]"; expected "str": "CarrierKit[str]"  [dict-item]`.
  - **What the tie misses:** a kit with Fastline's gateway and printer and Airco's rates exits 0; a `PlainLabelPrinter.label(self, reference: str, /)` with the Airco gateway exits 0 and reveals `"__main__.CarrierKit[__main__.AircoReference]"`, because a printer that takes any `str` fits every family.

Runtime (3.15.2), chapter 16:
- `KITS["AIRCO"].ship("CN-1", Decimal(10), CarrierSettings(account="ACC-7"))` is `Shipment(label='AIRCO AC-ACC-7-CN-1', quote=CarrierQuote(carrier='AIRCO', price=Decimal('48.00')))`; Fastline gives `label='FASTLINE FL-CN-1'` and `Decimal('12.00')`.
- The hand-mixed kit (built under `# type: ignore[misc]`) gives `label='AIRCO FL-CN-1'`: a Fastline reference on an Airco label, raised by nothing.

mypy 2.4.1, chapter 17:
- **The twelve-argument positional constructor.** Swapping `origin` and `destination` (two `str`), `insured` and `dangerous_goods` (two `bool`), or `carrier` and `service` (two `str`) is silent. Only swaps across types are reported:
  `<string>:24: error: Argument 4 to "LegacyBookingRequest" has incompatible type "Money"; expected "Weight"  [arg-type]` and `<string>:25: error: Argument 8 to "LegacyBookingRequest" has incompatible type "Weight"; expected "Money | None"  [arg-type]`.
- **The kw-only dataclass** (with `Literal` carrier and service):
  - a keyword swap of `origin` and `destination` exits clean (names make it reviewable, not checked);
  - `carrier="standard", service="FASTLINE"`: `Argument "carrier" to "BookingRequest" has incompatible type "Literal['standard']"; expected "Literal['FASTLINE', 'AIRCO']"  [arg-type]`, and the matching `service` error;
  - a missing field: `Missing named argument "destination" for "BookingRequest"  [call-arg]`;
  - a misspelt keyword: `Unexpected keyword argument "servce" for "BookingRequest"; did you mean "service"?  [call-arg]` (the "did you mean" suffix is new against chapter 8's quoted output; executors confirm).
- **The fluent builder.** `BookingRequestBuilder().consignment("CN-1").origin("NLRTM").build()` exits clean; the dataclass call without `destination` gives `[call-arg] Missing named argument "destination"`.
- **`copy.replace` is checked like `dataclasses.replace` (surprise).**
  - `dataclasses.replace(r, kilogram=...)`: `Unexpected keyword argument "kilogram" for "replace" of "BookingRequest"; did you mean "kilograms"?  [call-arg]`.
  - `copy.replace(r, kilogram=...)`: `Unexpected keyword argument "kilogram" for "replace"; did you mean "kilograms"?  [call-arg]` and the note `"replace" defined in "copy"`.
  - A wrong type: `Argument "kilograms" to "replace" has incompatible type "str"; expected "Decimal"  [arg-type]` (both functions).
  - `copy.replace` and `copy.copy` both reveal `"__main__.BookingRequest"`.
  - A plain class: `Argument 1 to "replace" has incompatible type "Plain"; expected "_SupportsReplace[[int], Never]"  [arg-type]` plus `Need type annotation for "f"  [var-annotated]`.

Runtime (3.15.2), chapter 17:
- **Shallow and deep copies of a mutable template** (`documents: list[str] = field(default_factory=list)`):
  - `copy.copy` then append: the template reads `['commercial invoice', 'dangerous goods note']`, and the lists are the same object.
  - `dataclasses.replace` shares the list too (`True`), and so does `copy.replace`.
  - `copy.deepcopy`: the template keeps `['commercial invoice']`.
  - `default_factory` gives each new instance its own list; a copy or a `replace` doesn't build a new one.
- **Validation reruns.** A frozen request with `insured and declared_value is None -> ValueError` raises `ValueError('an insured booking needs a declared value')` from both `replace(f, insured=True)` and `copy.replace(f, insured=True)`.
- `copy.copy(frozen_request) is frozen_request` is `False`, and the copy is equal. `copy.copy(frozendict(a=1))` is the same object; `copy.deepcopy(frozendict(a=1))` is a new one. Not planned as a claim.
- `copy.replace` on a typo: `TypeError("LooseRequest.__init__() got an unexpected keyword argument 'consignmnt_id'. Did you mean 'consignment_id'?")`. On a plain class: `TypeError('replace() does not support Plain objects')`. A `NamedTuple` and a `datetime.date` both support it.
- A `field(init=False)` passed to `replace`: `TypeError('field chargeable is declared with init=False, it cannot be specified with replace()')`, a `TypeError`, not a `ValueError`. Not planned as a claim.
- `copy.deepcopy` of an object holding a `threading.Lock`: `TypeError("cannot pickle '_thread.lock' object")`. Not planned as a claim; a possible "When not to use it" sentence only if a prose agent re-runs it.

mypy 2.4.1, chapter 18:
- **The metaclass.** With `SingletonMeta.__call__(cls, *args: Any, **kwargs: Any) -> Any`, `reveal_type(TariffTable("a.csv"))` is `"__main__.TariffTable"`, a missing argument is `Missing positional argument "source" in call to "TariffTable"  [call-arg]`, and `TariffTable("b.csv").source` reveals `"str"`. mypy types each call by `__init__`, so the ignored second argument is invisible.
- **Borg.** `_shared_state: ClassVar[dict[str, object]] = {}` and `self.__dict__ = self._shared_state` exit clean (no `Any` needed). With `__slots__`: `Trying to assign name "__dict__" that is not in "__slots__" of type "__main__.Slotted"  [misc]`.
- **The `__new__` form.** `_instance: ClassVar[Self | None]` with `__new__(cls, source) -> Self` exits clean; annotating `ClassVar["TariffTable | None"]` instead gives `Incompatible return value type (got "TariffTable", expected "Self")  [return-value]`. The prose doesn't take a position on `Self` in `ClassVar`; the fixture uses whichever form passes the root config.
- **`LoadOnce[T]`** with `NOT_LOADED = sentinel("NOT_LOADED")`, `self._value: T | NOT_LOADED`, the outer and inner `is NOT_LOADED` checks, and `lock: AbstractContextManager[object, None] | None` defaulting to `threading.Lock()` exits clean with `--warn-unreachable`. `x: AbstractContextManager[object, None] = threading.Lock()` is accepted. `functools.cache(load)` reveals `"functools._lru_cache_wrapper[typing.Mapping[str, int]]"`.
- **`lazy import`.** `lazy import json` and `lazy from decimal import Decimal` type-check. Through `lazy from tariffs import table`, an attribute typo is still reported: `Module has no attribute "TARIF"; maybe "TARIFF"?  [attr-defined]` with `Returning Any from function declared to return "int"  [no-any-return]`. ruff 0.17.3 parses `lazy` under `py315` and asks for import sorting (`I001`) when a `lazy from` sits in the same block as an eager import; the executor runs `ruff check --fix` and keeps the result.

Runtime (3.15.2), chapter 18:
- **The naive class.** Two call sites that each construct `TariffTable()` give `LOAD_LOG == ["naive", "naive"]`.
- **The cached loader leaks between tests.** A `functools.cache` loader that reads an override, called by a first test with `OVERRIDES["ASIA"] = 9`, hands the second test `{'EUROPE': 1, 'ASIA': 9}` after the override is cleared (`1 failed, 2 passed`). `cache_clear()` resets it. The member asserts this inside one test (two phases), never across test order.
- **`functools.cache` is not call-once.** A loader that returns only once two callers are inside it (`Barrier(2)` in the body), released on two threads: `cache loads: 2 same object: False`, 3 of 3 runs.
- **`LoadOnce` with a gated lock.** The gate is a lock whose `__enter__` waits on `Barrier(2)` before acquiring, so both threads are past the first check:
  - `inner=True loads=1 same=True entries=2 later-entries=0`
  - `inner=False loads=2 same=False entries=2 later-entries=0`
  - 3 of 3 runs. After the load, a further call doesn't take the lock (`later-entries=0`). A gate on a later call would block, because a `Barrier(2)` needs two parties, so the "read without the lock" test uses a counting lock, not the gate.
  - An earlier version that set an `Event` when it saw `locked()` had a window where both threads miss each other. The `Barrier` in `__enter__` closes it. Recorded so the executor doesn't reintroduce it.
- `sentinel("NOT_LOADED")` reprs as `NOT_LOADED` and is truthy.
- **Borg.** `a is b` is `False`, `a.__dict__ is b.__dict__` is `True`, the second constructor's source is ignored by a guard (`source: a.csv`, `loads: ['a.csv']`), a subclass shares the same state, and `a == b` is `False` with different hashes. A slotted dataclass Borg raises `AttributeError("'SlotBorg' object has no attribute '__dict__' and no __dict__ for setting new attributes")`.
- **The metaclass.** `x is y` is `True`, `y.source` is `a.csv` after `TariffTable("b.csv")`, and the second call's `__init__` never ran. Mixing with `ABC` raises `TypeError: metaclass conflict: ...` (left to "Metaclasses, __init_subclass__, and registries"). A subclass gets its own instance.
- **The `__new__` form.** `TariffTable('a.csv')` then `TariffTable('b.csv')`: `init` prints twice, `a is b` is `True` and `a.source` is `'b.csv'`. The first caller's table changed under it.
- **`lazy import`.** After importing a module that holds `lazy from tariffs import table`, `LOAD_LOG` is `[]`, `"tariffs.table" not in sys.modules`, and the name is a `lazy_import` object. The first call loads it (`['table']`). Eight threads started together on first use of a lazy name whose module body waits on an `Event`: one load, 20 of 20 runs. That run is not forced, so the test asserts only the outcome, and the prose rests on PEP 810's sentence, not on the run.

What's New in 3.15 (fetched 2026-11-04, https://docs.python.org/3.15/whatsnew/3.15.html, all three parts of the page read):
- **Relevant: PEP 810 explicit lazy imports.** "When you mark an import as lazy, Python defers the actual module loading until the imported name is first used." "Lazy imports are only permitted at module scope; using `lazy` inside a function, class body, or `try`/`except`/`finally` block raises a `SyntaxError`." "In the case where loading a lazily imported module fails ... Python raises the exception at the point of first use rather than at import time." Also `-X lazy_imports` and `PYTHON_LAZY_IMPORTS` (not used by the member).
- **Relevant: PEP 661 `sentinel`.** "Sentinel objects preserve identity when copied, support use in type expressions with the `|` operator, and can be pickled when they are importable by module and name." Used for `NOT_LOADED`.
- **Relevant: PEP 814 `frozendict`** for every registry (`GATEWAYS`, `KITS`, `TEMPLATES`) and the tariff rates. "The following standard library modules have been updated to accept `frozendict`: `copy`, ...".
- Import system: "The import system now acquires per-module locks in hierarchical order (parent packages before their submodules)." A deadlock fix; not planned as a claim.
- dataclasses: only "Annotations for generated `__init__` methods no longer include internal type names." functools: only `singledispatchmethod` changes and a `reduce` deprecation. copy: no entry beyond `frozendict` support. threading: new iterator helpers (`synchronized_iterator()` and others), not used. Nothing for `__replace__`, `functools.cache` or `threading.Lock`.

Sources fetched 2026-11-04. The prose agents re-fetch them and quote exactly; the fetch tool paraphrases punctuation, so the page text wins.
- PEP 810 (https://peps.python.org/pep-0810/), Status Final: "Reification follows the existing import-lock discipline." "Exactly one thread performs the import and atomically rebinds the importing module's global to the resolved object." "If reification fails (e.g., due to an `ImportError`), the lazy object is _not_ reified or replaced." "Subsequent uses of the lazy object will re-try the reification." "Type checkers and static analyzers may treat `lazy` imports as ordinary imports for name resolution."
- copy docs (https://docs.python.org/3/library/copy.html): "A _shallow copy_ constructs a new compound object and then (to the extent possible) inserts _references_ into it to the objects found in the original." "A _deep copy_ constructs a new compound object and then, recursively, inserts _copies_ into it of the objects found in the original." `copy.replace`: "Creates a new object of the same type as _obj_, replacing fields with values from _changes_." "Added in version 3.13." "Function `copy.replace()` is more limited than `copy()` and `deepcopy()`, and only supports named tuples created by `namedtuple()`, `dataclasses`, and other classes which define method `__replace__()`."
- dataclasses docs (`replace`, `kw_only`, `__post_init__`), functools docs (`cache`, `cache_clear`), threading docs (`Lock`, `Barrier`) and the typing docs (`Self`): to be fetched by the prose agents. No sentence planned as a quote.
- python-patterns.guide index (https://python-patterns.guide/): page titles listed in decision 10.
- ActiveState recipe 66531 and the O'Reilly *Python Cookbook* recipe page: titles from a web search and the O'Reilly MCP; the prose agent fetches the recipe page before citing it.
- GoF: not quotable. Bracketed items, used only if a prose agent verifies them in the book; otherwise the idea is described without attribution:
  - [GoF says Abstract Factory makes it hard to add a new kind of product, because the factory interface fixes the set];
  - [GoF lists "isolates concrete classes" and "promotes consistency among products" among Abstract Factory's consequences];
  - [GoF's Prototype keeps a registry of prototypes cloned on request];
  - [GoF's Singleton is "subclassable" through a registry of singletons].

Repo facts:
- **Chapter status.** Chapters 16-18 are `kind = "pattern"`, `has_example = true`, `status = "stub"`, part 6 (`creating-objects-under-control`). The stubs carry `## How it works` and "Draft pending" descriptions.
- **Reconciliation.** Rows run 1-84, so r08 adds 85-96. Row 1 gets the decision 5 note. `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** `_data/diagrams.yml` has 16 entries; r08 makes 19.
- **Test-name collisions.** `test_names` reads `examples/*/tests/**/*.py`. Existing names near this ground: `test_a_class_is_already_a_factory_method`, `test_builder_is_a_keyword_only_dataclass`, `test_prototype_is_replace`, `test_module_is_one_instance_for_every_importer` (three-way split); `test_kw_only_rejects_positional_arguments`, `test_replace_runs_post_init`, `test_frozen_is_shallow`, `test_dataclasses_replace_keeps_other_fields` (dataclasses); `test_build_app_shares_one_gateway_between_booking_and_tracking`, `test_unknown_carrier_fails_at_the_composition_root` (ISP/DIP); `test_mypy_checks_each_registry_entry`, `test_the_rule_registry_is_read_only` (strategy); `test_the_static_snippets_mirror_the_source` (state machines); `test_a_booked_weight_must_be_positive_and_finite` (command). The spike tree has `test_functools_cache_does_not_make_the_loader_run_once` (not an examples name, avoided anyway). Every name below was checked against `grep -rhoE "def test_\w+" examples spikes`.
- **Already taught, so not repeated** (each gets a pointer by title and at most one sentence):
  - A class in the `GATEWAYS` dict is already a factory; a keyword-only `BookingRequest`; `replace` as Prototype; the module `tariff_table` loaded once; Borg and metaclass "have narrow uses"; "`functools.cache` doesn't make a singleton": "The three-way split: dissolve, survive, disambiguate".
  - The module singleton's shape (`TARIFF = _load()`), and "if each test needs a clean instance, or you need one per tenant, pass the object in as a parameter": "What 1994 assumed, and what Python dissolves" (it promises that chapter 18 "compares them").
  - The composition root as the one place an adapter is named, and an unknown carrier failing there: "ISP, DIP, and dependency injection without a framework".
  - `kw_only` rejecting positional arguments with `[call-arg]`, `replace` rerunning `__post_init__`, mypy checking `replace` keywords, frozen being shallow, `default_factory` and the mutable-default `ValueError`, `Money.of` as a classmethod: "Dataclasses and value semantics" (it points to chapter 17 for "many optional fields").
  - A registry of callables as a read-only `frozendict`, mypy checking each registry entry (`[dict-item]`), a class registered where an instance belongs: "Strategy: the callable".
  - `match` with `assert_never`: "State and finite state machines".
  - The `sentinel` and `X | None` absence: "Protocol, duck typing, and structural typing with mypy".
  - Negative fixtures, the mypy-API helper and deletion tables: "Proving it works: pytest, pytest-mock, and mypy".
- **Later chapters whose ground must not be taken:**
  - "Metaclasses, __init_subclass__, and registries" (metaclass `__call__` in depth, metaclass conflicts, `__init_subclass__` registries);
  - "The GIL and performance" (the GIL, `+=`, threads against processes, the tariff table under load);
  - "Composite and Flyweight" (interning and per-key shared instances);
  - "Descriptors and properties" (`cached_property`);
  - "Seams in Python: monkeypatch, injection, and duck typing" (patching module attributes, a patch in the wrong namespace);
  - "Adapter, Facade, and Bridge" (the carrier adapters and unit conversion);
  - "Visitor, Memento, and Interpreter" (snapshots);
  - "Final project" (a staged `Invoice` from `LineItem`s, the one place a builder-like accumulation might be argued).

## What is new in each chapter

**Chapter 16 (Factory Method dissolves; Abstract Factory survives).** "The three-way split" shows a class in the `GATEWAYS` dict, and the ISP/DIP chapter shows a composition root choosing one. This chapter adds:
- **The slot type, measured.** `Callable[[CarrierSettings], CarrierGateway]` checks every constructor; `type[CarrierGateway]` accepts a class that can't be called without arguments and lets the call through, which fails at run time.
- **Classmethod constructors returning `Self`**, so a named constructor builds the subclass it's called on and fits a registry slot.
- **The count.** A GoF creator hierarchy passes the same table with three classes; the registry needs none.
- **The failure Abstract Factory exists for.** A carrier added to two of three if-chains is quoted at another carrier's rate, and mypy says nothing.
- **The family as one frozen value**, chosen once, with mypy tying the products that exchange a value and missing the ones that don't.

**Chapter 17 (Builder and Prototype dissolve).** "Dataclasses and value semantics" teaches `kw_only`, `replace` and frozen fields one at a time. This chapter adds:
- **The construction problem at scale**: twelve fields, four required, and which swaps types catch (across types) and which they can't (two `str`, two `bool`).
- **Builder's own cost, measured**: a fluent builder that leaves out a step fails at `build()`, where the dataclass call fails in mypy.
- **Cross-field rules** in `__post_init__` that every copy path reruns (`replace` and `copy.replace`).
- **Prototype as a read-only table of template values** plus `replace`; `copy.copy` and `replace` share a mutable list, `deepcopy` doesn't, and an immutable field type removes the question. `copy.replace` (3.13) and `__replace__`, checked by mypy like `dataclasses.replace`.

**Chapter 18 (Singleton needs disambiguating; the default is a module).** Two earlier chapters show the module built at import time and one load. This chapter adds:
- **The ladder**: import time, then `lazy import` (3.15) for a deferred load that is still once, then a parameter for tests and tenants, then `LoadOnce` only for a load that needs run-time input.
- **Measured failures**: two loads under a naive class; a cached loader carrying one test's table into the next; `functools.cache` running a loader twice on two threads.
- **The double-checked lock with a forced interleaving**, and the sentinel that lets a loader return `None`.
- **The three class forms, measured on one table**: Borg shares state between unequal objects; the metaclass ignores a second call's arguments and mypy can't see it; the `__new__` form reruns `__init__` and rewrites the shared table.

## Approach

- **Thesis wording.**
  - Chapter 16 says Factory Method dissolves (a class or a classmethod is the factory, and a registry slot typed as a `Callable` is the creator) and Abstract Factory survives: keeping a family consistent is a design decision that no feature makes for you.
  - Chapter 17 says Builder and Prototype dissolve: a keyword-only frozen dataclass names every argument and validates once, and `replace` copies with changes. Builder survives only as staged accumulation, pointed to "Final project" in one sentence.
  - Chapter 18 says Singleton needs disambiguating. "One instance" in Python usually means a module object; "shared state" is Borg; "the class returns the same object" is the metaclass or `__new__` form. The default is a module, and "Never say `functools.cache` makes a singleton" holds.
- **Credit.** GoF where each pattern is introduced. Chapter 16 and 17 point to the python-patterns.guide pages. Chapter 18 credits Martelli for Borg (decision 10), [POSA2 for double-checked locking if verified] and PEP 810. Nothing from any book's examples is used.
- **Domain names** come from `_plans/shipping-domain-model.md` plus the decision 4 supporting names. Port codes are UN/LOCODEs (`NLRTM`, `SGSIN`, `MYPKG`). Rates, accounts and the twelve fields are illustrative, and each chapter says so once.
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/16-factory-method-and-abstract-factory` (project `factories`, package `factories`);
  - `examples/17-builder-dataclasses-and-prototype` (project `builder-prototype`, package `builder_prototype`);
  - `examples/18-singleton-module-borg-metaclass` (project `singleton`, package `singleton`).
- **mypy witnesses** copy the r07 `_run`/`_codes` helper with `tmp_path` and a `mypy.ini` that sets `mypy_path` to the member's `src`. Each asserts exit status, an exact `_codes()` set and one or two substrings, never line numbers. Wherever possible, a snippet imports the real `src` names, so deleting a check in `src` changes the snippet's result (chapter 16's family tie, chapter 17's `Literal` fields and `copy.replace`). Snippets that stand for test fixtures (the if-chain, the positional constructor, the fluent builder, the metaclass, Borg) are reduced models, and the prose says so (criterion 23).
- **Shared cases are conftest fixtures** (the r07 lesson): the carrier table in chapter 16, the four-case booking table in chapter 17, the "same rates for every caller" forms in chapter 18. Each table test reports one id per form and case.
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (I1a, I1b, I1c) name the test and say why it sees the deletion. A row whose witness was predicted, not run, is marked "executor check".
- **Global state.**
  - No `mock`, `mocker`, `monkeypatch`, `print(` or wall clock.
  - Every registry is a `frozendict` typed as `Mapping`. The one module-level mutable object is chapter 18's `LOAD_LOG`, a list in its own module that records loads (the chapter 3 precedent: a counter inside the module being loaded would reset whenever that module was rebuilt). The prose says why it exists.
  - Chapter 18 tests that need a fresh interpreter (the lazy import, threads racing on a lazy import) run `subprocess.run([sys.executable, "-I", "-c", CODE])` with the member's `src` inserted into `sys.path` inside `CODE`. In-process tests never assert whether `singleton.tariff_table` is already imported, because test order decides that.
  - Threads: every race is forced by a `threading.Barrier` (guard timeout 10 s that a healthy run never reaches), never by `sleep`. The unforced lazy-import run asserts the outcome only.
  - `filterwarnings = ["error"]` stays active.

Rejected:
- `abc.ABC` creator hierarchies or kit classes in `src` (decisions 3, 5).
- A `type[...]`-typed registry in `src` (the planning evidence shows it lets a bad call through).
- `functools.cache` or `lru_cache` as the singleton in `src`; it appears only as the measured trap.
- `importlib.reload` as a test reset: it builds a second table while old references keep the first. One sentence at most, no test.
- `copy.deepcopy` as the answer for templates: it's the comparison; the answer is immutable fields.
- `TypedDict` + `Unpack[...]` keyword assembly, `**kwargs` builders and `functools.partial` builders: out of scope.
- A per-key instance cache (multiton): Flyweight ground.
- Patching module attributes to swap the tariff: seams ground.
- `-X lazy_imports=all` and `__lazy_modules__`: one sentence at most.

## Per-chapter spec

### Chapter 16: Factory Method and Abstract Factory (pattern, has_example = true, bucket: Factory Method dissolves, Abstract Factory survives)

Thesis: Factory Method's force is code that must create an object without naming its class. A class, or a classmethod returning `Self`, already is that factory, and a registry slot typed `Callable[[CarrierSettings], CarrierGateway]` replaces the creator subclass. Abstract Factory's force is different: products that must come from the same family. Python doesn't resolve it, so the pattern survives as one frozen value per family, chosen once. mypy can hold the family together only where products pass values to each other.

Sections (about 2,350 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - an Airco booking quoted at Fastline's rate because the carrier was added to two of three if-chains (test 7);
   - a registry typed `type[CarrierGateway]` that type-checks and fails on the first Airco booking (test 6);
   - a Fastline reference printed on an Airco label by a kit someone assembled by hand (test 9).
3. Figure plus one paragraph (~60).
4. `## Factory Method dissolves` (~380). Excerpt `GatewayFactory`, `GATEWAYS` and one `from_settings`:
   - GoF credited for Factory Method by Intent, in the book's own words.
   - One sentence pointing to "The three-way split: dissolve, survive, disambiguate" for the class in a dict, and one to "ISP, DIP, and dependency injection without a framework" for the composition root.
   - Classmethod constructors returning `Self` build the subclass they're called on (test 2); a hard-coded return builds the parent.
   - The same carrier table passes for the registry and for the GoF creator fixture (test 1), and the count (test 5). At most one short excerpt of `_BookingDesk`.
   - An unknown code is an `UnknownCarrierError` (test 3), and the registries are read-only (test 4).
5. `## The slot type decides what mypy checks` (~300):
   - The `Callable` slot rejects a constructor with the wrong parameters, including a classmethod that wants an environment mapping (tests 11, 12). Fresh output.
   - The `type[CarrierGateway]` slot accepts a class that needs an argument, lets the zero-argument call through, and fails at run time (tests 6, 11[type-slot]). It rejects a `partial` and the Protocol itself (tests 11[partial-in-type-slot], 11[protocol-in-type-slot]).
   - One sentence pointing to "Strategy: the callable" for mypy checking each registry entry, with no re-teaching.
6. `## When creation comes in families` (~300). The if-chain fixture:
   - Three functions branch on the code; `AIRCO` reached two of them; the booking is quoted at 12.00 where 48.00 was due (test 7). mypy exits 0 (test 13[str-code]).
   - A `Literal` code and `match` would catch the missing arm (test 13[literal-code]); one sentence pointing to "State and finite state machines" for `assert_never`. The chapter's point is that it would catch it three times, in three places, and the family still has no single home.
   - GoF credited for Abstract Factory by Intent and Consequences, [bracketed items only if verified]. Bucket: survives.
7. `## The family as one frozen value` (~420). Excerpt `CarrierKit`, `Shipper` and the two kit values:
   - Each kit ships with its own carrier's products (test 8), and the kit is a frozen value (test 10).
   - The reference type ties the gateway to the label printer: a mixed kit is `[misc]` (test 14). The registry hides the type parameter behind `Shipper`; a registry typed by one family is rejected (test 16).
   - What the tie misses, measured: another carrier's rates, and a printer that takes any `str` (test 15). The hand-mixed kit at run time (test 9).
   - The rule: tie what exchanges values, choose the kit once, at the composition root.
8. `## Adding a carrier, adding a product` (~150): a new carrier is one kit value and one registry entry; a new product is a field on every kit, which is the Abstract Factory trade-off [GoF's "hard to add a new kind of product" only if verified].
9. `## When not to use it` (~180): one product (a registry of constructors is enough); one carrier (call the class); products that never have to match (pass them separately); configuration choices that are data (a settings value, not a type). Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written factories.** An assistant asked for "a factory" may write a `GatewayFactory` class with a `create` method per carrier, an if-chain on the carrier code repeated in each module that needs a product, a registry typed `type[CarrierGateway]`, or a classmethod that returns the base class by name. Check: is the factory a class or a `Self` classmethod in a `Callable` slot; is each family one value chosen in one place; do products that exchange values share a type that mypy can tie; is the registry read-only; does an unknown code fail with a domain error.</blockquote>

   Each check maps to tests 2 and 11, 7-8, 14-15, 4 and 3.
10. `## Build, run, observe` (~220 plus output). Experiments, each in a fresh scratch copy (delete the copy's `.venv` and re-sync, and confirm `factories.__file__` points into the copy), one change, reverted:
    - (a) Give `AIRCO_KIT` the Fastline label printer. Expected: the member mypy run reports `Cannot infer value of type parameter "R" of "CarrierKit"  [misc]`; `test_each_kit_ships_with_its_own_carriers_products[AIRCO]` fails. Quote as observed.
    - (b) Change `AircoLabelPrinter.label` to take `reference: str`. Expected: mypy exits 0 and pytest passes, apart from test 15's snippet if it relies on the printer; the tie is gone and nothing reports it. Quote as observed.
11. `## For deeper coverage` (~130): GoF (Factory Method, Abstract Factory); Rhodes, python-patterns.guide, "The Factory Method Pattern" and "The Abstract Factory Pattern"; the typing docs (`Self`, `type[]`); PEP 544; PEP 814; the bibliography link.

Figure `16-factory-method-and-abstract-factory` (vertical):
- Top accent box `ship(code, ...)`, then `KITS` "read-only: carrier code to kit".
- It forks to two kit boxes, `FASTLINE_KIT` and `AIRCO_KIT`. Under each, three product boxes: gateway, label printer, rates.
- Within each kit, an arrow gateway to label printer labelled with that carrier's reference type (`FastlineReference`, `AircoReference`); a side note "mypy ties these".
- The rates box carries "not tied: one kit value keeps it consistent".
- A small left box `GATEWAYS` "Factory Method: a constructor in a Callable slot".
- No numbers in the SVG.

Caption draft (43 words with prefix): "Figure 16.1: Factories as values. A read-only registry maps a carrier code to one kit per family; the gateway's reference type ties it to the label printer, while the rate source is held consistent only by choosing the whole kit once."

### Chapter 17: Builder, dataclasses, and Prototype (pattern, has_example = true, bucket: dissolve)

Thesis: Builder's force is an object with many parts, several optional, that must be complete and valid before anyone uses it. Prototype's force is a new object that starts as a copy of a configured one. A frozen keyword-only dataclass names every argument, defaults the optional ones and validates once in `__post_init__`; `replace` and `copy.replace` copy with changes and rerun that validation. Both patterns dissolve. What remains a decision is the field types: a mutable field makes every copy path share it.

Sections (about 2,350 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - a twelve-argument constructor called with origin and destination swapped, which builds a booking to Rotterdam from Singapore and passes mypy (test 1);
   - a fluent builder with the destination step left out, which fails only when `build()` runs (test 4);
   - a booking copied from a template whose documents list is shared, so the template gains a dangerous goods note (test 8).
3. Figure plus one paragraph (~60).
4. `## The construction problem` (~320):
   - GoF credited for Builder by Intent, in the book's own words. Bucket: dissolves.
   - The legacy constructor (at most one short excerpt of its signature). Which swaps mypy catches (across types) and which it can't (two `str`, two `bool`, two codes) (tests 13, 14). Fresh output.
   - One sentence pointing to "Dataclasses and value semantics" for `kw_only` rejecting positional calls; no re-teaching.
5. `## A keyword-only dataclass is the builder` (~400). Excerpt `BookingRequest`:
   - Twelve fields, four required (test 3). `Literal` carrier and service levels turn a keyword swap of those two into `[arg-type]`, a missing field into `[call-arg]` and a misspelling into `[call-arg]` with a suggestion (test 15). A keyword swap of origin and destination is still accepted: names make it reviewable, not checked.
   - Cross-field rules live in `__post_init__`: insured needs a declared value, dangerous goods need a dangerous goods note, origin and destination differ (test 2's table). Weight is positive and finite (test 16).
   - The three forms pass the same four-case table (test 2 `[keyword|positional|builder]`).
6. `## What a builder costs` (~260). At most one short excerpt of `_BookingRequestBuilder.build`:
   - A step left out is a `ValueError` at `build()` (test 4), and mypy accepts the chain (test 17).
   - Where a builder survives: assembling a value in stages from parts that arrive over time. One sentence pointing to "Final project".
   - One sentence crediting Ramalho ("Data Class Builders") [if verified] and Slatkin on keyword-only arguments [if verified].
7. `## Prototype: templates and replace` (~380). Excerpt `TEMPLATES` and `from_template`:
   - GoF credited for Prototype by Intent. [Registry of prototypes only if verified.] Bucket: dissolves.
   - A read-only table of template requests and `replace` give a new request (test 5); an unknown template is a `BookingError` (test 11); the table is read-only (test 12).
   - `replace` and `copy.replace` both rerun the cross-field checks (test 6). `copy.replace` is new in 3.13 and works on any class with `__replace__` (test 10); mypy checks its keywords and types like `dataclasses.replace` (test 18). The copy docs are quoted on what `copy.replace` supports.
   - One sentence pointing to "The three-way split: dissolve, survive, disambiguate" for `replace` as Prototype; this section's new ground is templates, validation and `copy.replace`.
8. `## Shallow copies share` (~300):
   - The `_LooseRequest` fixture: `copy.copy` and `replace` share the documents list, so the template changes (test 8). mypy accepts it (test 19). `default_factory` makes a fresh list only for a newly built instance.
   - `copy.deepcopy` separates it (test 7). The copy docs are quoted on shallow and deep copies.
   - The answer is the field type: a `tuple[str, ...]` field makes the template safe to share (test 9). One sentence pointing to "Dataclasses and value semantics" for frozen being shallow.
9. `## When not to use it` (~170): a value with three fields (a plain constructor is clear); objects whose construction is a process with side effects (a function); deep copies of objects holding resources such as locks or connections (build them, don't copy them); a builder kept for a fluent style alone. Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written builders.** An assistant asked for "a builder" may write a fluent `BookingRequestBuilder` whose `build()` checks for missing parts at run time, a constructor with a dozen positional parameters, a `clone()` method that copies `self.__dict__`, or a template with a `list` field copied with `copy.copy`. Check: is the product a frozen keyword-only dataclass; are cross-field rules in `__post_init__`; are closed choices `Literal` or enum types; are copies made with `replace` or `copy.replace`; are template fields immutable.</blockquote>

   Each check maps to tests 2-3, 2 and 6, 15, 5-6 and 10, 8-9.
10. `## Build, run, observe` (~220 plus output). Experiments in fresh scratch copies:
    - (a) Delete the insured-needs-a-declared-value check from `BookingRequest.__post_init__`. Expected: `test_both_constructors_pass_the_booking_table[keyword-...]` fails for the insured case, test 6 fails, the positional and builder cases still pass, and mypy exits 0. Quote as observed.
    - (b) Change `documents` to `list[str] = field(default_factory=list)`. Expected: mypy reports `[arg-type]` where the templates pass tuples, and the tuple-field test fails. Quote as observed.
11. `## For deeper coverage` (~130): GoF (Builder, Prototype); Rhodes, "The Builder Pattern" and "The Prototype Pattern"; the dataclasses docs (`kw_only`, `replace`, `__post_init__`); the copy docs (`copy.replace`, `__replace__`); PEP 557; Ramalho and Slatkin [as verified]; the bibliography link.

Figure `17-builder-dataclasses-and-prototype` (vertical):
- Top: `TEMPLATES` "read-only: name to template request".
- Then `from_template` "replace(template, ...)", feeding `BookingRequest(...)` "keyword-only, frozen".
- Then `__post_init__` "cross-field checks: insured, dangerous goods, ports".
- A side branch from `__post_init__`: "every copy path reruns it: replace, copy.replace".
- An accent box at the bottom: "a list field is shared by copy and replace; a tuple field can't be".
- No numbers in the SVG.

Caption draft (40 words with prefix): "Figure 17.1: Building and copying a booking request. A template is copied with replace into a frozen keyword-only request, whose post-init checks run on every copy path; only an immutable field type keeps copies from sharing a list."

### Chapter 18: Singleton: module, Borg, and metaclass (pattern, has_example = true, bucket: needs disambiguating, default a module)

Thesis: "Singleton" names three different things in Python: one object (a module attribute), one shared state (Borg) and one class that returns the same object (a metaclass or `__new__`). The force behind most uses is "load this once and let everyone read it", and the module answers it: import time by default, `lazy import` when the load should wait, a parameter when a test or tenant needs its own. A lock with a double check is for the rare load that needs run-time input. `functools.cache` memoises; it doesn't make a singleton.

Sections (about 2,400 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - two modules that each construct the tariff table, which loads it twice (test 5);
   - a cached tariff loader that carries one test's table into the next (test 6);
   - two threads arriving at a cached loader together, which loads it twice (test 8).
3. Figure plus one paragraph (~60).
4. `## Three things called Singleton` (~260):
   - GoF credited for Singleton by Intent. Bucket: needs disambiguating, default a module. One sentence pointing to "What 1994 assumed, and what Python dissolves" for the module shape.
   - The three meanings, and the one table every form passes (test 12).
5. `## The module, at import time or on first use` (~380). Excerpt the `quoting` module with `lazy from`:
   - Every importer gets the one table (test 1). The naive class loads per caller (test 5).
   - `lazy import` defers the load to first use (test 2), and threads racing on first use load it once (test 3). PEP 810 is quoted on "exactly one thread", and the What's New entry on module scope only.
   - Import-time errors move to first use under `lazy import`; one sentence quoting PEP 810's retry rule.
6. `## Pass the table in` (~280). Excerpt `quote`:
   - `quote` takes the table it's given (test 4), so a test builds its own. The cached loader's leak (test 6) and `cache_clear` as the reset when a cache can't be avoided (test 7).
   - One sentence pointing to "ISP, DIP, and dependency injection without a framework" for the composition root, and one to "Seams in Python: monkeypatch, injection, and duck typing" for patching module state.
7. `## Once, under threads` (~400). Excerpt `LoadOnce`:
   - `functools.cache` runs the loader twice when two threads arrive together (test 8): the functools docs on `cache` are quoted [only a sentence the prose agent finds on the page].
   - `LoadOnce` with a double-checked lock runs it once when both threads have passed the first check (test 9), and a loaded value is read without the lock (test 10). The `NOT_LOADED` sentinel lets a loader return `None` and still run once (test 11). The PEP 661 What's New sentence is quoted.
   - How the test forces the interleaving: the injected lock's `__enter__` waits on a `Barrier(2)`. One sentence pointing to "The GIL and performance" for why threads interleave at all. [POSA2 credited for double-checked locking if verified.]
8. `## Borg, the metaclass, and __new__` (~380). At most two short excerpts, from the fixtures:
   - Borg (credit Martelli, decision 10): instances share one `__dict__` but are distinct and unequal (test 13); mypy accepts it with `dict[str, object]`, and slots refuse it (test 17).
   - The metaclass: the second call's arguments are ignored (test 14), and mypy types every call by `__init__` (test 16). One sentence pointing to "Metaclasses, __init_subclass__, and registries".
   - The `__new__` form reruns `__init__` and rewrites the shared table (test 15).
   - Where each fits, in one paragraph: Borg when code must construct "its own" object yet share configuration; a class form only when the class itself must be the access point. Neither is the default.
9. `## When not to use it` (~170): state that differs per test, tenant or request (a parameter); a "singleton" that is really a cache (a cache, named as one); mutable global state that several threads write (a lock is the smaller problem); a class whose only reason to exist is to be single (a module). Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written singletons.** An assistant asked for "a singleton" may write a class that overrides `__new__` with a `_instance` attribute, a `SingletonMeta` metaclass, or a `@functools.cache` function described as making something load once. Check: could this be a module attribute, or a `lazy import` of one; does `__init__` run again on every call; are a second call's arguments silently ignored; do tests get their own instance by parameter; is anything claimed to be call-once under threads, and if so, is it a lock with a double check or the import system.</blockquote>

   Each check maps to tests 1-2, 15, 14, 4 and 6, 8-9.
10. `## Build, run, observe` (~220 plus output). Experiments in fresh scratch copies:
    - (a) Delete the inner `is NOT_LOADED` check in `LoadOnce.__call__`. Expected: mypy exits 0; `test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check` fails with two loads. Quote as observed.
    - (b) Change `lazy from singleton import tariff_table` to an eager import in `quoting.py`. Expected: `test_a_lazy_import_loads_the_table_on_first_use` fails because the load log already holds the tariff after the import; mypy exits 0. Quote as observed.
11. `## For deeper coverage` (~130): GoF (Singleton); Martelli's Borg recipe (decision 10); Rhodes, "The Singleton Pattern" and "The Global Object Pattern"; PEP 810; PEP 661; the functools docs (`cache`); the threading docs (`Lock`, `Barrier`); [POSA2 if verified]; the bibliography link.

Figure `18-singleton-module-borg-metaclass` (vertical):
- A ladder of four boxes, top to bottom: `tariff_table` "module: built at import time"; `lazy from ... import tariff_table` "built on first use, once"; `quote(..., table=...)` "passed in: tests and tenants get their own"; `LoadOnce` "lock with a double check: load needs run-time input".
- A right side column, muted: `Borg` "shared state, distinct objects"; `SingletonMeta` "second call's arguments ignored"; `__new__` "reruns __init__".
- An accent box at the bottom: "functools.cache memoises; it is not call-once".
- No numbers in the SVG.

Caption draft (42 words with prefix): "Figure 18.1: Four ways to load the tariff table once, in the order to reach for them. A module, a lazy import and a parameter cover nearly every case; the class forms on the side each cost something the tests measure."

Citations, all three chapters: verify each before writing; apply the bracketed fallbacks; quote no sentence unless it was checked on a fetched page; no comparison between languages.

## Example spec

### `examples/16-factory-method-and-abstract-factory` (project `factories`, package `factories`)

`pyproject.toml` in the r07 shape (`requires-python = ">=3.15"`, no `[tool.*]`).

- `domain.py`:
  - `ConsignmentId = NewType`.
  - `Money(amount: Decimal, currency: str)`, frozen slotted.
  - `CarrierSettings(account: str, sandbox: bool = False)`, frozen slotted kw_only.
  - `CarrierQuote(carrier: str, price: Money)`, frozen slotted.
  - `Shipment(reference: str, label: str, quote: CarrierQuote)`, frozen slotted.
  - `UnknownCarrierError(LookupError)`.
- `carriers.py`:
  - `FastlineReference`, `AircoReference` (`NewType` over `str`).
  - Protocols `CarrierGateway[R]` (`book(self, consignment_id: ConsignmentId, /) -> R`), `LabelPrinter[R]` (`label(self, reference: R, /) -> str`), `RateSource` (`quote(self, kilograms: Decimal, /) -> CarrierQuote`).
  - `FastlineGateway(endpoint: str)` and `AircoGateway(account: str)`, frozen slotted, each with `from_settings(cls, settings) -> Self` (`cls(...)`). Airco's reference includes the account; Fastline's endpoint depends on `sandbox`.
  - `FastlineLabelPrinter`, `AircoLabelPrinter`, `FastlineRates` (1.20 EUR per kg), `AircoRates` (4.80 EUR per kg).
- `factories.py`:
  - `type GatewayFactory = Callable[[CarrierSettings], CarrierGateway[str]]`.
  - `GATEWAYS: Mapping[str, GatewayFactory] = frozendict({...})` with the two `from_settings`.
  - `make_gateway(code, settings) -> CarrierGateway[str]`: `try`/`except KeyError` raises `UnknownCarrierError(f"unknown carrier {code!r}")` from None.
- `kits.py`:
  - `CarrierKit[R]`, frozen slotted kw_only, fields `gateway`, `label_printer`, `rates`; `ship(self, consignment_id, kilograms, settings) -> Shipment`.
  - `Shipper` Protocol with the same `ship` signature.
  - `FASTLINE_KIT`, `AIRCO_KIT`, `KITS: Mapping[str, Shipper] = frozendict({...})`.
  - `ship(code, consignment_id, kilograms, settings) -> Shipment`, raising `UnknownCarrierError` the same way.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: `settings` (`CarrierSettings(account="ACC-7")`); `carrier` parametrized `FASTLINE`/`AIRCO`, each giving the expected reference prefix, label prefix and price for 10 kg.

`test_factory_method.py` (comparison fixture `_BookingDesk(ABC)` with abstract `create_gateway(settings)` and `book(...)`, `_FastlineDesk`, `_AircoDesk`, `_DESKS`):
1. `test_a_registered_constructor_builds_each_carrier_gateway[registry|creator]` x the `carrier` fixture (4 cases): the same reference for each carrier through `make_gateway` and through the desk.
2. `test_a_classmethod_constructor_returns_the_subclass_it_is_called_on`: a test-local subclass of `AircoGateway`; `type(...) is` the subclass.
3. `test_an_unknown_carrier_code_is_an_unknown_carrier_error[gateways|kits]`: the code is `"NOSUCH"` (no invented carrier codes), matching `unknown carrier 'NOSUCH'`.
4. `test_the_carrier_registries_are_read_only[gateways|kits]`: `# type: ignore[index]`; `TypeError` matching `does not support item assignment`; `not isinstance(..., dict)`.
5. `test_the_creator_design_declares_three_classes_where_the_registry_declares_none`: `ast` over `factories.py` (no `ClassDef`) and over this test file (`_AircoDesk`, `_BookingDesk`, `_FastlineDesk`).
6. `test_a_type_registry_accepts_a_class_that_cannot_be_called_without_arguments`: a test-local `Mapping[str, type[CarrierGateway[str]]]`; `TypeError` matching `missing 1 required positional argument: 'account'`.

`test_if_chains.py` (fixture: `_make_gateway`, `_make_label_printer`, `_make_rates`, `_ship_by_chain`, where `AIRCO` is in the first two only):
7. `test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate`: the Airco label and a price of 12.00 where the kit gives 48.00.

`test_kits.py`:
8. `test_each_kit_ships_with_its_own_carriers_products` x the `carrier` fixture (2 cases).
9. `test_a_hand_mixed_kit_prints_one_carriers_reference_on_anothers_label`: built under `# type: ignore[misc]`; `label == "AIRCO FL-..."` shape as observed.
10. `test_every_kit_is_a_frozen_value`: `FrozenInstanceError` on assignment; equal kits from equal constructors compare equal.

`test_static.py` (snippets import `factories` through `mypy_path` except where noted):
11. `test_mypy_checks_a_constructor_slot_but_not_a_type_slot[callable-slot|type-slot|partial-in-type-slot|protocol-in-type-slot]`: `{"dict-item"}` with `"type[AircoGateway]"`; exit 0; `{"dict-item"}` with `"partial[AircoGateway]"`; `{"type-abstract"}` with `Only concrete class can be given`.
12. `test_mypy_checks_a_classmethod_constructor_against_the_slot`: a test-local `from_env` classmethod; `{"dict-item"}`, `expected "str": "Callable[[CarrierSettings], CarrierGateway[str]]"` (the executor matches the src alias's rendering).
13. `test_mypy_cannot_see_a_carrier_missing_from_an_if_chain[str-code|literal-code]`: self-contained reduced model; exit 0; then `{"arg-type"}`, `"Literal['AIRCO']"`.
14. `test_mypy_rejects_a_kit_that_mixes_reference_types`: `{"misc"}`, `Cannot infer value of type parameter "R" of "CarrierKit"`.
15. `test_mypy_accepts_kits_that_mix_untied_products[mixed-rates|plain-printer]`: exit 0 and empty, twice.
16. `test_mypy_rejects_a_kit_registry_typed_by_one_family`: `{"dict-item"}`, `"CarrierKit[FastlineReference]"; expected "str": "CarrierKit[str]"`.

16 test functions, 27 cases (1: 4; 2: 1; 3: 2; 4: 2; 5: 1; 6: 1; 7: 1; 8: 2; 9: 1; 10: 1; 11: 4; 12: 1; 13: 2; 14: 1; 15: 2; 16: 1). The executor recounts from the pytest summary line and reports the counted number, not this one.

Also `README.md` and the card `_examples/16-factory-method-and-abstract-factory.md` (`order: 16`, eyebrow "Creating objects · Factories"). No `mock`, `monkeypatch`, `print(`, `Optional`, `isinstance`, `abc` or `type[` in `src/`.

Deletion table (I1a). Each row: the check, how it's deleted, the failing test, and why that test sees the deletion.

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `UnknownCarrierError` in `make_gateway` | plain index | 3[gateways] | `KeyError`, not the domain error |
| `UnknownCarrierError` in `ship` | plain index | 3[kits] | as above |
| `frozendict` `GATEWAYS` | `dict` | 4[gateways] | assignment succeeds; `isinstance(..., dict)` |
| `frozendict` `KITS` | `dict` | 4[kits] | as above |
| `cls(...)` in `AircoGateway.from_settings` | `AircoGateway(...)` | 2, member mypy | the subclass call returns the parent; mypy `[return-value]` on `Self` |
| account in the Airco reference | dropped | 1[...-AIRCO], 8[AIRCO] | the reference prefix no longer matches |
| `sandbox` in `FastlineGateway.from_settings` | ignored | executor check: no test reads the endpoint unless one is added (`test_a_sandbox_setting_selects_the_sandbox_endpoint`); otherwise drop the branch from src | |
| the kit uses its own `label_printer` | `FastlineLabelPrinter()` hard-coded in `ship` | 8[AIRCO], member mypy | Fastline label on an Airco shipment; mypy `[arg-type]` on the reference type (executor confirms) |
| the reference tie | `LabelPrinter[R]` to `LabelPrinter[str]` in `CarrierKit` | 14 | the mixed kit type-checks (executor check: the snippet imports src) |
| `frozen=True` on `CarrierKit` | dropped | 10 | assignment succeeds |
| `AircoRates` rate | changed to Fastline's | 8[AIRCO], 7 | 48.00 no longer expected; the if-chain comparison loses its contrast |

### `examples/17-builder-dataclasses-and-prototype` (project `builder-prototype`, package `builder_prototype`)

- `domain.py`:
  - `ConsignmentId`.
  - `Weight(kilograms: Decimal)`, frozen slotted, finite and positive, `ValueError` otherwise.
  - `Money(amount: Decimal, currency: str)`, frozen slotted.
  - `BookingError(ValueError)`.
- `booking.py`:
  - `type CarrierCode = Literal["FASTLINE", "AIRCO"]`, `type ServiceLevel = Literal["standard", "express"]`.
  - `BookingRequest`, frozen slotted kw_only, twelve fields: required `consignment_id`, `origin`, `destination`, `weight`; optional `carrier: CarrierCode = "FASTLINE"`, `service: ServiceLevel = "standard"`, `insured: bool = False`, `declared_value: Money | None = None`, `dangerous_goods: bool = False`, `reference: str | None = None`, `notify_party: str | None = None`, `documents: tuple[str, ...] = ()`.
  - `__post_init__` raises `BookingError` for: `origin == destination`; `insured` without `declared_value`; `dangerous_goods` without `"dangerous goods note"` in `documents`.
- `templates.py`:
  - `TEMPLATES: Mapping[str, BookingRequest] = frozendict({"rotterdam-singapore": ..., "dangerous-goods": ...})`, each with `consignment_id=ConsignmentId("TEMPLATE")`.
  - `from_template(name, *, consignment_id, weight) -> BookingRequest` by `replace`; an unknown name raises `BookingError(f"no template {name!r}")` from None.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `booking_case` parametrized over four cases (ids `minimal`, `insured-without-value`, `dangerous-without-note`, `same-ports`), each a field mapping and either the expected field values or the expected `BookingError` message;
- `build` parametrized `keyword|positional|builder`, each a callable from the case's fields to a request (keyword: `BookingRequest(**fields)` typed through a `TypedDict`-free helper the executor writes so mypy stays strict; positional: `_LegacyBookingRequest`; builder: `_BookingRequestBuilder`). The two fixture classes live in `tests/fixtures_legacy.py`, imported by conftest (the executor confirms `--import-mode=importlib` resolves it, or keeps them in conftest).

`test_builder.py`:
1. `test_a_positional_constructor_accepts_a_swapped_origin_and_destination`: `origin == "SGSIN"` where `NLRTM` was meant; nothing raised.
2. `test_both_constructors_pass_the_booking_table` x `build` x `booking_case` (12 cases). Name kept short; the ids carry the forms.
3. `test_the_request_has_twelve_fields_and_four_are_required`: `dataclasses.fields`, `MISSING` defaults, every field `kw_only`.
4. `test_a_builder_with_a_step_left_out_fails_only_at_build`: the chain without `destination` builds the builder; `build()` raises `ValueError` naming the missing parts.
16. `test_a_requested_weight_must_be_positive_and_finite[zero|negative|nan]`.

`test_prototype.py` (fixture `_LooseRequest`, mutable slotted kw_only, `documents: list[str] = field(default_factory=list)`):
5. `test_a_template_and_replace_give_a_new_request[rotterdam-singapore|dangerous-goods]`: new id and weight, template unchanged, `is not`.
6. `test_replace_reruns_the_cross_field_checks[replace|copy-replace]`: `insured=True` on a template raises `BookingError` matching `declared value`.
7. `test_a_deep_copy_separates_the_documents_list`.
8. `test_a_shallow_copy_shares_the_documents_list[copy|replace]`: after an append through the copy, the template reads both documents and `is` holds.
9. `test_a_tuple_field_makes_the_template_safe_to_share`: a copy's `documents + (...)` leaves the template's tuple unchanged; `copy.copy(request) == request`.
10. `test_copy_replace_works_on_dataclasses_and_refuses_a_plain_class`: `copy.replace(request, service="express")`; a test-local plain class raises `TypeError` matching `does not support`.
11. `test_an_unknown_template_is_a_booking_error`.
12. `test_the_template_registry_is_read_only`.

`test_static.py`:
13. `test_mypy_cannot_see_two_same_typed_arguments_swapped`: reduced model of the legacy constructor; three swaps; exit 0 and empty.
14. `test_mypy_reports_swapped_arguments_of_different_types`: `{"arg-type"}`, `has incompatible type "Money"; expected "Weight"`.
15. `test_mypy_checks_literal_fields_and_keyword_names[literal-swap|missing-field|misspelt-keyword]`: imports src; `{"arg-type"}` with `"Literal['standard']"`; `{"call-arg"}` with `Missing named argument "destination"`; `{"call-arg"}` with `did you mean "service"?`.
17. `test_mypy_accepts_a_builder_with_a_step_left_out`: reduced model; exit 0 and empty.
18. `test_mypy_checks_copy_replace_like_dataclasses_replace[dataclasses-name|copy-name|copy-type|plain-class]`: `{"call-arg"}`, `{"call-arg"}`, `{"arg-type"}`, then `{"arg-type", "var-annotated"}` with `_SupportsReplace`.
19. `test_mypy_cannot_see_a_shallow_copy_sharing_a_list`: exit 0 and empty.

Numbers are spec ids, not file order. 19 test functions, 40 cases: `test_builder.py` 18 (1: 1; 2: 12; 3: 1; 4: 1; 16: 3), `test_prototype.py` 11 (5: 2; 6: 2; 7: 1; 8: 2; 9: 1; 10: 1; 11: 1; 12: 1), `test_static.py` 11 (13: 1; 14: 1; 15: 3; 17: 1; 18: 4; 19: 1). The executor counts from the pytest summary line and reports that number (r07 misadded once).

Also `README.md` and the card (`order: 17`, eyebrow "Creating objects · Builder and Prototype"). No `mock`, `monkeypatch`, `print(`, `Optional`, `deepcopy` or `copy.copy` in `src/` (`copy` appears only in tests).

Deletion table (I1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `Weight` finite/positive | `__post_init__` removed | 16[all] | no `ValueError` |
| origin differs from destination | removed | 2[keyword-same-ports] | no `BookingError` (the positional and builder fixtures keep their own checks, so only the keyword ids fail) |
| insured needs a declared value | removed | 2[keyword-insured-without-value], 6[all] | no `BookingError` |
| dangerous goods need the note | removed | 2[keyword-dangerous-without-note] | no `BookingError` |
| `kw_only=True` | dropped | 3, member mypy (executor check) | `kw_only` false on every field; mypy may report nothing because every call site uses keywords |
| `frozen=True` | dropped | 5 (executor check), member mypy | assignment would succeed; executor names the test that observes it or adds `test_a_booking_request_is_frozen` |
| `tuple` documents | `list` with `default_factory=list` | 9, member mypy | the template's documents change; `[arg-type]` at the tuple literals |
| `Literal` carrier | `str` | 15[literal-swap] | the snippet's swap type-checks |
| `frozendict` `TEMPLATES` | `dict` | 12 | assignment succeeds |
| unknown template `BookingError` | plain index | 11 | `KeyError` |
| `from_template` by `replace` | builds a fresh `BookingRequest` from a few template fields | 5[dangerous-goods] | the template's documents and flags are lost (executor confirms which fields the rebuild drops) |

### `examples/18-singleton-module-borg-metaclass` (project `singleton`, package `singleton`)

- `domain.py`:
  - `TariffTable(rates: frozendict[str, Decimal])`, frozen slotted; `rate_for(zone) -> Decimal` raises `RatingError(f"no rate for zone {zone!r}")` from None.
  - `RatingError`.
- `loads.py`: `LOAD_LOG: list[str] = []` and `record_load(name)` (the chapter 3 precedent; the docstring says why it lives apart).
- `tariff_table.py`: `STANDARD_RATES`, `load_tariff(rates) -> TariffTable` (calls `record_load("tariff")`), `TARIFF = load_tariff(STANDARD_RATES)` at import time.
- `quoting.py`: `lazy from singleton import tariff_table`; `quote(zone, kilograms, *, table: TariffTable) -> Decimal`; `quote_standard(zone, kilograms) -> Decimal` passes `tariff_table.TARIFF`.
- `once.py`: `NOT_LOADED = sentinel("NOT_LOADED")`; `LoadOnce[T]` with `__init__(self, load: Callable[[], T], *, lock: AbstractContextManager[object, None] | None = None)` and `__call__` with the outer and inner checks.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: `small_table` (`TariffTable(frozendict({"EUROPE": Decimal("1.20")}))`); `rates_form` parametrized `module|load-once|borg|metaclass|cache`, each giving a zero-argument callable that returns the rates a caller sees (fresh fixture instances per test; the metaclass and `__new__` fixtures clear their class-level instance in the fixture teardown so state can't leak between tests).

`test_module.py`:
1. `test_every_importer_gets_the_one_tariff_table`: two `importlib.import_module` calls, `is`, and `LOAD_LOG.count("tariff") == 1`.
2. `test_a_lazy_import_loads_the_table_on_first_use`: subprocess `-I`; prints `LOAD_LOG` after `import singleton.quoting` (`[]`), whether `singleton.tariff_table` is in `sys.modules` (`False`), then after `quote_standard` (`['tariff']`).
3. `test_threads_racing_on_a_lazy_import_load_the_table_once`: subprocess `-I`; eight threads released by a `Barrier(8)` call `quote_standard`; one load and eight equal quotes. The docstring says the race isn't forced and the claim rests on PEP 810.
4. `test_quote_takes_the_table_it_is_given`: `small_table` and a second table give different prices; `LOAD_LOG` unchanged by the call.

`test_isolation.py` (fixtures `_NaiveTariffTable`, `_cached_tariff` with an `_OVERRIDES` dict local to the test module):
5. `test_a_naive_class_loads_the_table_once_per_caller`: two call sites; two loads recorded in a local list.
6. `test_a_cached_loader_carries_one_tests_table_into_the_next`: phase one sets an override and loads; phase two clears it and still sees `ASIA`. The fixture calls `cache_clear()` in teardown.
7. `test_cache_clear_resets_the_cached_loader`.

`test_once.py` (fixtures `_GatedLock` with a `Barrier(2)` in `__enter__`, `_CountingLock`, `_run_on_threads`):
8. `test_functools_cache_runs_a_loader_twice_when_two_threads_arrive_together`: a loader with a `Barrier(2)` inside; two loads and two different objects.
9. `test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check`: `_GatedLock`; one load, the same object, two lock entries.
10. `test_a_loaded_value_is_read_without_taking_the_lock`: `_CountingLock`; one entry for the first call, none for three more.
11. `test_load_once_keeps_a_loader_that_returns_none`: a loader returning `None` runs once over three calls.

`test_variants.py` (comparison fixtures `_TariffBorg`, `_SingletonMeta`, `_MetaTariffTable`, `_NewTariffTable`):
12. `test_every_form_gives_each_caller_the_same_rates` x `rates_form` (5 cases): two callers read equal rates, and a load count of one.
13. `test_borg_instances_share_state_but_are_distinct_and_unequal`.
14. `test_a_singleton_metaclass_ignores_the_second_calls_arguments`: `source == "standard.csv"` after a second call with another source.
15. `test_a_new_based_singleton_reruns_init_on_every_call`: the first caller's object now has the second caller's source.

`test_static.py`:
16. `test_mypy_types_a_metaclass_singleton_call_by_init[second-call|missing-argument]`: reduced model; exit 0; then `{"call-arg"}` with `Missing positional argument "source"`.
17. `test_mypy_accepts_borg_state_unless_the_class_has_slots[plain|slotted]`: reduced model; exit 0; then `{"misc"}` with `that is not in "__slots__"`.
18. `test_mypy_still_checks_attributes_through_a_lazy_import`: imports src; `{"attr-defined", "no-any-return"}` with `Module has no attribute "TARIF"; maybe "TARIFF"?` (the executor adjusts the codes to the observed set if `TARIFF` is typed so that `no-any-return` doesn't arise).

18 test functions, 24 cases (1-4: 4; 5-7: 3; 8-11: 4; 12: 5; 13-15: 3; 16: 2; 17: 2; 18: 1). The executor counts from the pytest summary line.

Also `README.md` and the card (`order: 18`, eyebrow "Creating objects · Singleton"). No `mock`, `monkeypatch`, `print(`, `Optional`, `global`, `functools.cache`, `metaclass=` or `__new__` in `src/`. `time.sleep` appears nowhere; `Barrier` timeouts are guards only.

Deletion table (I1c):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `RatingError` for an unknown zone | plain index | executor names the test or adds `test_an_unknown_zone_is_a_rating_error` | `KeyError` |
| import-time `TARIFF` | built inside `quote_standard` on every call | 1, 3 | more than one load |
| `lazy from` in `quoting.py` | eager `from` | 2 | the load log holds the tariff right after the import |
| `quote` uses its `table` parameter | reads `tariff_table.TARIFF` | 4 | both tables give the standard price |
| inner `is NOT_LOADED` check | removed | 9 | two loads every time |
| outer `is NOT_LOADED` check | removed | 10 | the lock is entered on every call |
| `NOT_LOADED` sentinel | `None` as the marker | 11, member mypy (executor check) | a `None`-returning loader runs on every call |
| the injected lock is used | `threading.Lock()` always | 9 (executor check: the gate is bypassed, so the threads may not overlap and the test can pass by luck; if it passes, the row is "seen by 10", whose counting lock is then never entered) | the gate never runs |
| `frozen=True` on `TariffTable` | dropped | executor names the test or adds `test_the_tariff_table_is_a_frozen_value` | assignment succeeds |

## Steps and status

Step ids are `I*` because `--claims` resolves `run:` tokens against every plan's steps table (decision 1).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| I0 | This plan file. PDP-116a-c, 117a-c and 118a-c `active` in `iteration-plan.md` (dated note). Reconciliation rows 85-96 `open`, and the row 1 note (decision 5). Domain-model rows 16-18 updated (decisions 4 and 11). ch16-18 stub `description` lines written. Decisions recorded | - | done |
| I0b | Only if decision 10 adds *Python Cookbook*: verify the edition, recipe title and year on the publisher page; add the `bibliography.html` row and the hub `books.yml` entry (`referenced_by: design-patterns-with-python`, `review_note`) on a hub branch | I0 | dropped (decision 10 revised) |
| I1a | ch16 member, card, README; three green runs; the deletion table, each row in a fresh scratch copy with its `.venv` removed and re-synced (confirm `__file__`) | I0 | done |
| I1b | ch17 member, card, README; one `uv lock` after the member (sequenced); three green runs; deletion table | I1a | done |
| I1c | ch18 member, card, README; one `uv lock` (sequenced); three green runs; deletion table; `_plans/evidence/lazy-import-threads.md` (20 subprocess runs of test 3's code, scrubbed) | I1b | todo |
| I2 | Witness results into rows 85-96 (claims audit resolves). A failed witness changes the thesis before prose. Any message differing from Planning evidence goes in "Corrections after the build" | I1c | todo |
| I3 | Three figures, specs `diagrams/specs/16-*.py`, `17-*.py`, `18-*.py`, `_data/diagrams.yml` (single owner; `section: "Ch. 16"` to `"Ch. 18"`); figures 00-15 unchanged | I2 | todo |
| I4 | ch16-18 `status = "drafted"` (`kind` stays `pattern`) | I3 | todo |
| I5 | Three prose agents in parallel. Each re-fetches its sources and quotes exactly, runs its two experiments in scratch copies, quotes fresh output filtered by `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table (claim, then test, run or source URL) | I3, I4 | todo |
| I6 | Opus validation; up to two repair rounds (decision 2's split applies if a third is needed) | I5 | todo |
| I7 | PR, `ci-ok` green, ask the user before merge; tag r08.x; notes-only release. Hub PR only if I0b ran | I6 | todo |

Reconciliation rows (step I0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 85 | 16 | A class or a `Self` classmethod in a `Callable` registry slot is the factory method; a GoF creator hierarchy passes the same carrier table with three classes where the registry declares none; unknown codes are domain errors and the registries are read-only | `test_a_registered_constructor_builds_each_carrier_gateway`, `test_a_classmethod_constructor_returns_the_subclass_it_is_called_on`, `test_the_creator_design_declares_three_classes_where_the_registry_declares_none`, `test_an_unknown_carrier_code_is_an_unknown_carrier_error`, `test_the_carrier_registries_are_read_only` |
| 86 | 16 | A `Callable` slot checks each constructor; a `type[Protocol]` slot accepts a class that needs arguments and lets the bad call through, rejecting only partials and the Protocol itself | `test_mypy_checks_a_constructor_slot_but_not_a_type_slot`, `test_mypy_checks_a_classmethod_constructor_against_the_slot`, `test_a_type_registry_accepts_a_class_that_cannot_be_called_without_arguments` |
| 87 | 16 | A carrier added to two of three if-chains is quoted at another carrier's rate and mypy is silent on a `str` code | `test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate`, `test_mypy_cannot_see_a_carrier_missing_from_an_if_chain` |
| 88 | 16 | A frozen kit per family ships with its own products; mypy rejects a kit mixing reference types and a registry typed by one family, but accepts another carrier's rates and a printer that takes any `str`; a hand-mixed kit prints the wrong label | `test_each_kit_ships_with_its_own_carriers_products`, `test_every_kit_is_a_frozen_value`, `test_mypy_rejects_a_kit_that_mixes_reference_types`, `test_mypy_rejects_a_kit_registry_typed_by_one_family`, `test_mypy_accepts_kits_that_mix_untied_products`, `test_a_hand_mixed_kit_prints_one_carriers_reference_on_anothers_label` |
| 89 | 17 | A twelve-argument positional constructor accepts same-typed swaps silently and mypy reports only cross-type swaps; the keyword-only request, the positional constructor and a fluent builder pass the same booking table | `test_a_positional_constructor_accepts_a_swapped_origin_and_destination`, `test_mypy_cannot_see_two_same_typed_arguments_swapped`, `test_mypy_reports_swapped_arguments_of_different_types`, `test_both_constructors_pass_the_booking_table`, `test_the_request_has_twelve_fields_and_four_are_required`, `test_a_requested_weight_must_be_positive_and_finite` |
| 90 | 17 | mypy checks `Literal` fields, missing fields and misspelt keywords on the dataclass, and nothing on a builder with a step left out, which fails only at `build()` | `test_mypy_checks_literal_fields_and_keyword_names`, `test_mypy_accepts_a_builder_with_a_step_left_out`, `test_a_builder_with_a_step_left_out_fails_only_at_build` |
| 91 | 17 | Templates plus `replace` give new requests and rerun cross-field checks, as does `copy.replace`, which mypy checks like `dataclasses.replace`; `copy.copy` and `replace` share a list field, `deepcopy` separates it, a tuple field removes the problem and mypy is silent on sharing | `test_a_template_and_replace_give_a_new_request`, `test_replace_reruns_the_cross_field_checks`, `test_copy_replace_works_on_dataclasses_and_refuses_a_plain_class`, `test_mypy_checks_copy_replace_like_dataclasses_replace`, `test_a_shallow_copy_shares_the_documents_list`, `test_a_deep_copy_separates_the_documents_list`, `test_a_tuple_field_makes_the_template_safe_to_share`, `test_mypy_cannot_see_a_shallow_copy_sharing_a_list`, `test_an_unknown_template_is_a_booking_error`, `test_the_template_registry_is_read_only`, `source: https://docs.python.org/3/library/copy.html` |
| 92 | 18 | Every importer gets one table; a `lazy import` defers the load to first use and threads racing on it load once; mypy still checks attributes through it | `test_every_importer_gets_the_one_tariff_table`, `test_a_lazy_import_loads_the_table_on_first_use`, `test_threads_racing_on_a_lazy_import_load_the_table_once`, `test_mypy_still_checks_attributes_through_a_lazy_import`, `source: https://peps.python.org/pep-0810/`, `run: _plans/evidence/lazy-import-threads.md` |
| 93 | 18 | A naive class loads per caller; a cached loader carries one test's table into the next until `cache_clear`; a quote given its table needs no module state | `test_a_naive_class_loads_the_table_once_per_caller`, `test_a_cached_loader_carries_one_tests_table_into_the_next`, `test_cache_clear_resets_the_cached_loader`, `test_quote_takes_the_table_it_is_given` |
| 94 | 18 | `functools.cache` runs a loader twice when two threads arrive together; `LoadOnce`'s double-checked lock runs it once, reads a loaded value without the lock, and keeps a `None` result through the sentinel | `test_functools_cache_runs_a_loader_twice_when_two_threads_arrive_together`, `test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check`, `test_a_loaded_value_is_read_without_taking_the_lock`, `test_load_once_keeps_a_loader_that_returns_none` |
| 95 | 18 | Module, `LoadOnce`, Borg, metaclass and cache all give callers the same rates; Borg instances are distinct and unequal, the metaclass ignores a second call's arguments and mypy types it by `__init__`, `__new__` reruns `__init__`, and slots refuse Borg | `test_every_form_gives_each_caller_the_same_rates`, `test_borg_instances_share_state_but_are_distinct_and_unequal`, `test_a_singleton_metaclass_ignores_the_second_calls_arguments`, `test_a_new_based_singleton_reruns_init_on_every_call`, `test_mypy_types_a_metaclass_singleton_call_by_init`, `test_mypy_accepts_borg_state_unless_the_class_has_slots` |
| 96 | 16-18 | The "Build, run, observe" experiments behave as quoted | `run: I5` |

## Corrections after the build

- Decision 10 revised by the owner 2026-11-04: the book isn't added. Step I0b could not verify that *Python Cookbook* 1st ed. prints the Borg recipe (the O'Reilly recipe page is walled; the catalogue lists the book without contents). Chapter 18 credits Alex Martelli by name and ActiveState recipe 66531 only. No bibliography row, no hub PR.
- Step I1a: the r07 `_codes` regex `\[([a-z-]+)\]` also matched `[str]` inside generic types in mypy messages; it is anchored to the line end, `re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)`. Later members that quote generics use the anchored form.
- Step I1a: `FastlineGateway.from_settings` returning `FastlineGateway(...)` instead of `cls(...)` was seen by mypy only, so the test subclasses both gateways; `CarrierKit[R: str]` is bound (Shipment.reference is `str`), and deleting the bound is mypy-only; `FastlineGateway.endpoint` defaults to the live endpoint so the zero-argument callable-slot witness holds; one added test, `test_a_sandbox_setting_selects_the_sandbox_endpoint`. Totals 17 functions, 28 cases.
- Step I1b, planning error (the misspelt-keyword evidence row): `copy.replace(request, wieght=...)` gives `Unexpected keyword argument "wieght" for "replace"  [call-arg]` with no "did you mean"; only `dataclasses.replace` adds `did you mean "weight"?`. The member asserts each form as it prints.
- Step I1b: the comparison fixtures `_LegacyBookingRequest` and `_BookingRequestBuilder` live in `tests/conftest.py` behind fixtures (sibling imports are blocked); the builder delegates its cross-field checks to the positional fixture. Deleting `frozen=True` on `Weight` fails at collection (`ValueError: mutable default Weight for field weight`); the `tuple` documents row is caught by the field-default test and mypy, not by the template-sharing test. Added `test_a_booking_request_has_no_instance_dict`, the `isinstance(..., ValueError)` table assertion and the service half of the literal-swap witness. Totals 21 functions, 42 cases.
- Criterion 2's `\babc\b` grep also matches `from collections.abc import`; the intent (no `abc` module or `ABC` in src) holds, so the grep is read as `^\s*(from abc|import abc)|\bABC\b`.

(empty)

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the three new members.
2. Each new member: `uv run pytest` and `uv run mypy --strict src tests` exit 0 on three consecutive runs.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch|print\("` over the three members prints nothing.
   - `grep -rnE "\babc\b|ABC|type\[" examples/16-*/src` prints nothing.
   - `grep -rnE "deepcopy|copy\.copy" examples/17-*/src` prints nothing.
   - `grep -rnE "functools|metaclass=|__new__|\bglobal\b" examples/18-*/src` prints nothing.
3. Every test name cited in rows 85-96 is defined exactly once across `examples/*/tests` (`grep -rhoE "def test_\w+" examples/*/tests | sort | uniq -d` lists none of them).
4. Every mypy-API test asserts exit status and an exact code set (`grep -c "_codes("` at least 4 in each `test_static.py`), and no test asserts a line number. Every `# type: ignore[...]` names a code.
5. Deletion tables (I1a, I1b, I1c): every row, deleted in a fresh scratch copy whose imports are confirmed to come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed"; executor-check rows are resolved or moved to Corrections with the orchestrator's agreement.
6. ch16-18 drafted, one figure each, captions 20-45 words including `Figure N.1:`, 1,900-2,500 prose words each (validate.py).
7. `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere. `grep -c "^## When not to use it"` is 1 in each, and `grep -c "^## How it works"` is 0. `validate.py` passes the `pattern` spine.
8. Thesis:
   - ch16 says Factory Method dissolves and Abstract Factory survives (`dissolv` and `surviv` each at least 1).
   - ch17 says Builder and Prototype dissolve (`dissolv` at least 1).
   - ch18 says Singleton needs disambiguating and the default is a module (`disambiguat` at least 1), and never says or implies that `functools.cache` makes a singleton (`grep -niE "cache[^.]*(makes|gives|is) a singleton"` prints nothing).
9. Non-overlap:
   - ch16 doesn't re-teach the composition root, mypy's per-entry registry check or `assert_never`, and points to "The three-way split: dissolve, survive, disambiguate", "ISP, DIP, and dependency injection without a framework", "Strategy: the callable" and "State and finite state machines" by title.
   - ch17 doesn't re-teach `kw_only` rejecting positional calls, frozen being shallow or `replace` rerunning `__post_init__` on one field, and points to "Dataclasses and value semantics", "The three-way split: dissolve, survive, disambiguate" and "Final project" by title.
   - ch18 doesn't excerpt the chapter 2 or chapter 3 `tariff_table` code, teaches no GIL or `+=` material and no metaclass mechanics beyond the fixture, and points to "What 1994 assumed, and what Python dissolves", "ISP, DIP, and dependency injection without a framework", "Seams in Python: monkeypatch, injection, and duck typing", "The GIL and performance" and "Metaclasses, __init_subclass__, and registries" by title.
   - No chapter re-teaches the evidence method, which is pointed to "Proving it works: pytest, pytest-mock, and mypy".
10. Voice:
    - `scan.sh --tier ban --fail` exits 0 over the three chapters, READMEs, cards and SVGs, with `--stats` reviewed against the house-voice rubric.
    - Contractions are used: uncontracted `does not|do not|is not|are not|did not|cannot` at most 3 per chapter outside code and output.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ)"` over prose (front matter `part:` slug excluded) prints nothing.
11. `grep -c $'\u2014'` is 0 over every file touched in r08, including this plan.
12. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Lisp|Dylan|Smalltalk|capstone|PDP-|\br0[0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/1[678]-*.md`, the new READMEs and cards prints nothing.
13. Idiomatic scan: 0 ban-tier in all three members.
14. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`, never hand-edited.
15. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run (API output prints `<string>:N` matching the snippet), apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
16. Each experiment is performed in a fresh scratch copy (its `.venv` removed and re-synced, `__file__` confirmed) and changes one thing. The prose quotes the observed result, and the handback includes the raw filtered output.
17. Attribution (standing rule: credit every source a chapter leans on, by author and work, where the idea is used; nothing copied; quotations exact from fetched pages; a missing credit is blocking):
    - ch16 credits GoF (Factory Method, Abstract Factory) and Rhodes's two pages.
    - ch17 credits GoF (Builder, Prototype), Rhodes's two pages, and Ramalho and Slatkin as verified; it quotes the copy docs exactly.
    - ch18 credits GoF (Singleton), Martelli (Borg) per decision 10, Rhodes's two pages, and POSA2 as verified; it quotes PEP 810 and the What's New `sentinel` sentence exactly.
    - GoF claims appear only if verified, with the bracketed fallbacks applied. Each prose agent lists the sources it checked.
    - Every book cited is in `bibliography.html` and in hub `books.yml` `referenced_by`; a new book (I0b) has its hub PR open before I7 asks for the merge.
18. Claims:
    - Every factual sentence in ch16-18 maps to a named test, a recorded run (`run: I5` or a file under `_plans/evidence/`) or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0. The claims table lists rows 1-96, with 85-96 resolved, and each `source:` URL appears in its chapter.
    - No `run: G*` or `run: H*` token appears in rows 85-96.
19. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has nineteen entries, and `diagrams/0*-*` and `diagrams/1[0-5]-*` are unchanged.
20. Reconciliation rows 85-96 are `verified` or `adjusted` with evidence. Row 1 carries the r08 note.
21. Deterministic: no test depends on wall time, the environment, memory addresses, test order or iteration order it didn't create. Every thread race is forced by a `Barrier`, apart from test 3 in chapter 18, which asserts only the outcome and says so. Subprocess tests pass `-I`. `filterwarnings = ["error"]` is still in the root config. Every class-level instance cache in a fixture is cleared in teardown.
22. CI `ci-ok` is green on the PR. Merge happens only after the user's explicit approval.
23. Every self-contained mypy snippet that stands for code (ch16 test 13; ch17 tests 13, 14, 17; ch18 tests 16, 17) is either checked against its source by an `ast` test or named in the prose as a reduced model. Snippets that import `src` need neither.
24. Test counts in prose and handbacks come from the pytest summary line of a fresh run, never from this plan's arithmetic.

## Risks

- **Predicted messages.** r05, r06 and r07 each mispredicted (r07 three deletion witnesses). Everything in Planning evidence was run, but on reduced models. Expect the `GatewayFactory` alias's rendering in test 12, the kit's revealed type names and the lazy-import code set to differ. Tests match stable substrings, and differences go in "Corrections after the build".
- **mypy findings can age.** The `type[Protocol]` call check, the generic kit's `[misc]` message, `copy.replace` checking and the "did you mean" suffix are mypy 2.4.1 behaviour. The prose says "mypy 2.4.1 reports" and the tests pin it, so a bump fails visibly.
- **The generic kit is the hardest idea in Part 6.** Variance (`R` covariant in the gateway, contravariant in the printer, so the kit is invariant) explains why the registry hides `R`. The prose may give it one sentence and no variance lecture; if chapter 16 can't fit both floor and ceiling, the `type[]` section shrinks first, and its tests stay.
- **Chapter 17's fixtures crowd the table.** Three forms times four cases is twelve ids. If the legacy or builder fixture needs a check the dataclass lacks, the table stops being shared. The executor keeps the three forms' checks identical, and the deletion table's "only the keyword ids fail" rows depend on that.
- **Chapter 18's import state.** `singleton.tariff_table` may already be imported by earlier tests in the one pytest process. Tests 2 and 3 run in subprocesses; test 1 asserts a count of one load for the module's lifetime, which holds whatever ran first because the module is built once per process. A test that clears `LOAD_LOG` would break it, so none does.
- **`lazy import` and tooling.** ruff asks for a separate import block (I001); mypy treats lazy imports as ordinary. `--import-mode=importlib` with a `lazy from singleton import ...` inside the package: the executor confirms it resolves in-process and in the subprocess.
- **Thread tests can hang.** Every `Barrier` and `Event` wait carries a 10 s guard that raises; a hung run fails rather than blocks CI. The gated lock must wait on its barrier before acquiring, never after (planning evidence on the earlier `Event` design).
- **The metaclass and `__new__` fixtures hold class-level state** that survives between tests. Their fixtures clear it in teardown (criterion 21).
- **Overlap** with the three-way split, the 1994 chapter, ISP/DIP, dataclasses, Strategy, State, metaclasses, the GIL, seams and Flyweight. Criterion 9 greps for it, and pointers go by title only.
- **Domain rows 16-18 wording** changes at I0 (decisions 4 and 11). If the owner declines decision 3, `CarrierKit` loses its type parameter, tests 14-16 become one `test_mypy_accepts_any_mix_of_products`, and the chapter says mypy can't hold a family together.
- **Attribution.** GoF can't be quoted. Martelli's recipe title comes from a search result and the O'Reilly catalogue; the prose agent fetches the recipe before citing. POSA2's pattern name is bracketed.
- **ruff.** N818 holds (`UnknownCarrierError`, `BookingError`, `RatingError`). `RUF012` may fire on the Borg `ClassVar` dict in a fixture; the executor keeps the `ClassVar` annotation, which silences it.
- **Liquid.** f-strings with `{{` in excerpts need `{% raw %}`; validate.py checks.
- **`uv.lock` race.** I1a, I1b and I1c are sequenced, and project names normalise to the package names.
