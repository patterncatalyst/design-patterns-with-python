---
title: "r13 plan: chapters 27-28 (Descriptors and properties; singledispatch: the Visitor the language gives you)"
order: 13
output: false
render_with_liquid: false
---

# r13: chapters 27-28, Descriptors and properties; singledispatch: the Visitor the language gives you

Opus-planned 2026-11-05. Branch `release/r13`, cut from main at bcd537c (the r12 merge, tagged r12.x). This file is the source of truth for r13 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4 and uv 0.13.7 are unchanged (r12 N0 bumped ruff to 0.17.4); P0 re-checks PyPI and python.org before any edit. `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch27: slug `27-descriptors-and-properties`, title "Descriptors and properties", part 9 (`idiomatic-python`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.
- ch28: slug `28-singledispatch`, title "singledispatch: the Visitor the language gives you", part 9 (`idiomatic-python`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.

Work items: PDP-127a-c (ch27 example, figure, prose) and PDP-128a-c (ch28), `todo` in `_plans/iteration-plan.md`.

## User decisions (owner confirmed 2026-11-06: all ten as recommended; the `@property` over `@cache` slots failure is logged privately outside the repo, nothing filed)

Standing, not a decision: step ids are `P*`. `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md`, and `grep -nE '^\| P[0-9]' _plans/*.md` matched nothing before this file. The letters in use are A, G to N and S.

1. **Buckets: ch27 survives and carries the Proxy disambiguation; ch28 says Visitor dissolves.**
   - **ch27 survives** (domain row 27). The descriptor protocol is the language's. The design that survives is:
     - one validator per rule, shared by every field that needs it;
     - the choice between `property`, a descriptor and `cached_property`;
     - where a descriptor can sit on a dataclass (frozen yes, `slots=True` no).
   - The r02 map lists `property` and `cached_property` under **Proxy, needs disambiguating**, with this chapter as a home. ch27 gives that its own section: `cached_property` is lazy initialisation with no surrogate. The section points to "Decorator the pattern vs @decorator the syntax, and Proxy" and to "The three-way split: dissolve, survive, disambiguate" by title.
   - **ch28: Visitor dissolves.** The r02 map ("Visitor: `singledispatch` for an open set"), the ch3 table row and ch25 all say so. What remains to design is the fallback, where registrations live, and who imports them.
   - Domain row 28 says "survive". P0 rewords it to "dissolve (Visitor, open set); the registration discipline is the design".

   **Recommend: yes.** Alternative: ch28 "survives" as the domain row says. That contradicts the canonical map, the ch3 row and ch25's own sentence that the open form is the dissolved Visitor.

2. **ch27's domain: one `Positive` descriptor over six `Decimal` fields in three classes (domain row 27).**
   - `Positive` validates "finite and positive" for:
     - `Consignment.kilograms`;
     - `Dimensions.length_cm`, `width_cm` and `height_cm`;
     - `Container.tare_kg` and `Container.max_payload_kg`.
   - Which dataclass each class is:
     - `Dimensions` is `@dataclass(frozen=True)`;
     - `Consignment` is `@dataclass(frozen=True, kw_only=True)`;
     - `Container` is a mutable entity, `@dataclass(eq=False)`, with `load(consignment)`.
   - None is slotted, and the chapter says why: decision 4 and evidence C.
   - Kilograms are `Decimal`, as in ch25's `BookingRequest`. There is no `Weight` class here. "When not to use it" says that a frozen value type validated once in `__post_init__` (ch8) needs no descriptor.

   **Recommend: yes.** Alternatives:
   - (b) Fields typed `Weight` (a value class) with no descriptor. That's ch8's answer, and it leaves `Dimensions` and the container limits without a shared rule.
   - (c) Descriptors on plain classes with hand-written `__init__`. That hides every dataclass interaction the reader will hit.

3. **ch27 teaches `property` first, then the descriptor.** Intent comes before mechanism:
   - `Container.payload_kg` is a read-only computed `property`;
   - a validating setter on one field is a `property` pair;
   - the second and third class that need the same rule are the force;
   - a copy-pasted setter that dropped `is_finite()` is domain row 27's failing test;
   - `Positive` follows.

   **Recommend: yes.** Alternative: the descriptor first and `property` as a special case. That's mechanism before intent.

4. **Descriptor shape: class access raises, the overloads type it, storage goes through `vars()`.**
   - `__set_name__` records `public_name` and `private_name = f"_{name}"`, as the descriptor guide does.
   - On class access, `__get__` raises `AttributeError(public_name)`. The dataclasses docs say that's how a descriptor field gets no default.
   - `__get__` is typed with two overloads: `(None, type) -> Never` and `(object, type) -> Decimal`.
   - `__set__` validates, then writes `vars(instance)[private_name]`, because `setattr` on a frozen dataclass raises `FrozenInstanceError` (evidence B).
   - The conventional `return self` on class access appears only as a test-local witness: it becomes the field's default (evidence B).

   **Recommend: yes.** Alternative: `return self` with a default sentinel. That adds a fake default that mypy and the generated `__init__` both accept.

5. **cached_property scope.**
   - In `src`, only frozen `Consignment.chargeable_kg`: the larger of actual and volumetric weight at 167 kg per cubic metre, illustrative.
   - Test-local:
     - stale over mutable state (a `cached_property` payload on a `Container` subclass);
     - the getter runs twice under two threads (since 3.12; a `Barrier`);
     - the slots `TypeError`;
     - `del` refused on a frozen class.
   - The functools page's suggestion of `@property` over `@lru_cache` gets one quoted sentence, plus a pointer to "Decorators done right" (which owns B019 and its liveness test). No test, no `src` use: evidence D shows the stack failing at class creation under `@dataclass(slots=True)` on 3.15.2, and voice rule 13 keeps that out of reader text.

   **Recommend: yes.** Alternatives:
   - (b) Drop the thread test. Then "Singleton: module, Borg, and metaclass", which owns the `functools.cache` thread finding, is the only place the reader learns caches aren't call-once.
   - (c) Use a lazy `TrackingHistory`. That's the ground of "Dynamic attributes: __getattr__ and Proxy as a feature" and of ch3's `LazyTrackingHistory`.

6. **ch28's domain (domain row 28).**
   - **Commodity kinds.** `commodities.py` holds frozen slotted `Coffee(roasted, decaffeinated=False)`, `InstantCoffee(Coffee)`, `TShirt(cotton)` and `LithiumIonBattery(watt_hours)`.
   - **The lookup.** `tariff.py` holds `tariff_code`, a `singledispatch` function with an `object` fallback that raises `TariffCodeError(LookupError)`. It registers by annotation:
     - `Coffee` gives `0901.11`, `0901.12`, `0901.21` or `0901.22`;
     - `InstantCoffee` gives `2101.11`;
     - `TShirt` gives `6109.10` or `6109.90`.
   - **The extension module.** `dangerous_goods.py` is another team's module and registers `LithiumIonBattery`, giving `8507.60`.
   - **The method.** `surcharges.py` holds `DryContainer`, `ReeferContainer(number, set_point_c)`, `TankContainer` and `SurchargeSchedule(reefer_per_day, tank_cleaning)`. Its `singledispatchmethod surcharge(container, days)` returns `Money` and its fallback raises `SurchargeError`.
   - HS codes and rates are illustrative, said once.
   - Container numbers are `"C-1"` to `"C-3"`: real owner prefixes (BIC codes) belong to real companies.

   **Recommend: yes.** Alternative: `Container` kinds for the function and `Commodity` kinds for the method. The row gives the lookup to commodities.

7. **Global registry isolation in tests.**
   - No test registers on `tariff_code` or `SurchargeSchedule.surcharge` in the test process.
   - Registration tests take a `fresh_dispatcher` fixture: function-scoped, a new raising `@singledispatch` per test.
   - The open-extension and import-order claims run in a fresh `python -I` interpreter through a `_run_isolated` helper, copied from `examples/18-singleton-module-borg-metaclass/tests/test_module.py`. The helper writes JSON with `sys.stdout.write`.
   - No test process imports `dangerous_goods`, so an unregistered battery is deterministic everywhere else.
   - Rejected:
     - copying the registry into a new dispatcher (the only type for it is typeshed's private `_SingleDispatchCallable`, and the copy hides the global state the chapter teaches);
     - `_clear_cache`;
     - `monkeypatch`.

   **Recommend: yes.** Alternative: a factory in `src` that builds a dispatcher per caller. That changes the idiom the chapter teaches.

8. **`singledispatchmethod` is in, at about 200 words.** It covers:
   - dispatch on the argument after `self` (legacy row 10);
   - the docs' rule that it's the outermost decorator;
   - mypy 2.4.1 typing the bound method as `def (*Any, **Any) -> Money`, so arguments go unchecked (evidence J).

   **Recommend: yes.** Alternative: out. Legacy row 10 and domain row 28 both need it.

9. **One comparison fixture and one comparison excerpt per chapter.**
   - **ch27: `field_form` `descriptor|property`**, on one table of extents.
     - `descriptor` is `src` `Dimensions`. `property` is the conftest twin `_PropertyDimensions`: a plain class with three correct validating property pairs.
     - Both pass the table. The excerpt is the twin's `height_cm` pair.
     - Drift isn't a table row. It's a separate test-local copy that omits `is_finite()`.
   - **ch28: `fallback_form` `raising|defaulting`**, on one table of seven commodities.
     - `raising` is `src` `tariff_code`.
     - `defaulting` is a conftest dispatcher whose fallback returns `"unclassified"`, registered with the same `src` implementations read from `tariff_code.registry`.
     - The excerpt is the defaulting fallback. The silent default is its own test (domain row 28's failing test).
   - Registration forms (annotation, `register(cls)`, `register(cls, fn)`, union) are test-local witnesses, not fixture forms.

   **Recommend: yes.** Alternative: an `isinstance` chain as ch28's comparison. That's the if-chain that "Shortcut patterns: dict dispatch, function tables, and EAFP" owns.

10. **Scope cuts.**
    - Out of both chapters:
      - ABC virtual registration and ambiguous dispatch (evidence H);
      - the first-annotation quirk (evidence I);
      - the slots and `property`-over-cache class-creation failure (evidence D);
      - reusing one descriptor instance under two names (evidence A).
    - All four are recorded here and in the P2 spikes note. The owner may report D and I upstream (`lgtm-issue-reporting`); no chapter does.
    - In both chapters: union annotations, `register(cls, fn)`, forward references, the mypy caveats, the checks against the fallback's signature, and global registration state. ch25 left these to ch28. ch26 left `cached_property`, `__set_name__` and writing `__get__` to ch27.

    **Recommend: yes.** Alternative: ABCs in, with one test. That's about 100 words the chapter doesn't have, and the book leads with `Protocol`.

Also proposed for the owner (no decision needed unless declined):
- No new books. GoF, Ramalho (*Fluent Python* 2nd ed., O'Reilly 2022, confirmed in the O'Reilly catalogue; chapter titles not visible) and Slatkin are in `bibliography.html`. Book items stay bracketed.
- **Rhodes, python-patterns.guide** (index fetched 2026-11-05). There's no Visitor, Proxy or descriptor page; `gang-of-four/visitor/`, `gang-of-four/proxy/` and `python/descriptors/` each return 404. ch27 may quote "The Factory Method Pattern" page, section "Instance attributes override class attributes": "the instance attribute wins". That's the plain rule a data descriptor overrides. ch28 claims no Rhodes page.
- At P2, a dated r13 note in `_plans/spikes.md` updates PDP-012 with:
  - the 3.15.2 forward-reference message (now with `owner=`);
  - `register(cls, fn)` going unchecked by mypy;
  - a `TYPE_CHECKING` import failing registration;
  - `singledispatchmethod` argument typing;
  - the first-annotation rule;
  - the slots crash.

## Planning evidence

The planning run is read-only, so no scratch directory was created. Every probe ran as inline code with the session scratchpad (`<scratchpad>`) as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `<repo>/.venv/bin/python -I -c CODE`, version `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- mypy: `<repo>/.venv/bin/python -I -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET`, version `mypy 2.4.1 (compiled: yes)`.
- ruff: `<repo>/.venv/bin/ruff check --isolated --no-cache --line-length 100 --select E,F,W,I,UP,B,SIM,RUF,PT,N --target-version py315 --stdin-filename NAME -`, version ruff 0.17.4.

Snippets are reduced models. Line numbers will differ and are never asserted. Object addresses are shown as `0x...`. Every output is a prediction for the member until the build quotes it as observed.

**A. A hand-written descriptor on a plain class.** `Positive` with `__set_name__`, `__get__` and `__set__`, on `Container(tare, max_gross)`:
```
2200 30480 {'_tare': Decimal('2200'), '_max_gross': Decimal('30480')}
Positive tare _tare
ValueError: tare must be positive, got -1
ValueError: tare must be positive, got NaN
ValueError: tare must be positive, got Infinity
data desc wins: 2200
non-data: from dict
AttributeError: 'Positive' object has no attribute 'public'
```
- A data descriptor beats an instance-dict entry with its name. A plain non-data descriptor loses to one.
- A descriptor assigned after the class exists never gets `__set_name__`.
- One instance assigned to two names takes the second name: `C(Decimal(-1), Decimal(1))` reports `b must be positive`, and `c.a` reads `c.b`'s value. Not used (decision 10).
- `Decimal('NaN') > 0` raises `decimal.InvalidOperation`, an `ArithmeticError` and not a `ValueError`, so `is_finite()` must come first.

**B. Descriptors as dataclass fields.**
- A descriptor that returns itself on class access becomes the field's default. `Container()` passes the descriptor to `__set__`: `AttributeError 'Positive' object has no attribute 'is_finite'`.
- With `__get__` raising `AttributeError` on class access:
  ```
  [True, True]
  Dimensions(length=Decimal('1'), width=Decimal('2')) {'_length': Decimal('1'), '_width': Decimal('2')}
  TypeError: Dimensions.__init__() missing 2 required positional arguments: 'length' and 'width'
  ValueError: length must be positive, got 0
  FrozenInstanceError cannot assign to field 'length'
  replace ValueError: width must be positive, got -2
  True True
  False True
  ```
  - Each field's `default is MISSING`.
  - The frozen guard refuses assignment.
  - `dataclasses.replace` re-validates.
  - Equal values compare and hash equal.
  - `hasattr(Dimensions, 'length')` is `False`, while the key is in the class `__dict__`.
- On a frozen dataclass, a descriptor that writes with `setattr` fails at construction: `FrozenInstanceError: cannot assign to field '_length_cm'`.

**C. `slots=True` replaces a descriptor field.** `@dataclass(frozen=True, slots=True)` with `length_cm: Positive = Positive()`:
```
accepted: D(length_cm=Decimal('-1')) member_descriptor
TypeError: D.__init__() missing 1 required positional argument: 'length_cm'
```
- The slot's `member_descriptor` replaces the validator, and `-1` is accepted with no error.
- mypy exits 0 on the same model (`Slotted(Decimal(-1))`).
- The data model's `__slots__` notes say why (Sources).

**D. `cached_property`.**
```
TypeError: No '__dict__' attribute on 'Dims' instance to cache 'volume' property.
TypeError: No '__dict__' attribute on 'Dims2' instance to cache 'volume' property.
frozen no slots: 8 {'length': Decimal('4'), 'volume': Decimal('8')}
FrozenInstanceError: cannot assign to field 'length'
dataclasses.FrozenInstanceError: cannot delete field 'volume'
```
- A slotted dataclass (frozen or not) fails on first access.
- A frozen, non-slotted dataclass caches by writing `__dict__` directly, and refuses `del` through the frozen `__delattr__`.
- `__slots__ = ("a", "__dict__")` works.
- `cached_property` has neither `__set__` nor `__delete__`: it's a non-data descriptor. Assignment overrides it, and an instance-dict entry wins.
- One `cached_property` assigned to two names: `TypeError: Cannot assign the same cached_property to two different names ('a' and 'b').` with the note `Error calling __set_name__ on 'cached_property' instance 'b' in 'Two'`. Not used.
- **Threads.** A getter that waits on `threading.Barrier(2, timeout=10)`, read from two threads, ran 3 of 3 times:
  ```
  getter ran 2 results [2, 2] cached 2
  ```
  `sys._is_gil_enabled()` is `True`.
- **mypy.** `@cached_property` on a `slots=True` dataclass, assigning to it, and `del` on a frozen class all exit 0. Revealed type `decimal.Decimal`.
- **`@property` over `@cache`.**
  - Under `@dataclass(slots=True)` or `@dataclass(frozen=True, slots=True)`, class creation fails on 3.15.2: `AttributeError: 'functools._lru_cache_wrapper' object has no attribute '__code__'`. The traceback runs through the dataclasses slots code.
  - `@dataclass(frozen=True)` and a plain `__slots__` class work.
  - ruff reports B019 on the stack (`Use of functools.lru_cache or functools.cache on methods can lead to memory leaks`) and nothing on `cached_property`.
  - Not used in `src` or in prose beyond one docs sentence (decision 5).

**E. mypy on the typed descriptor.** Overloaded `__get__`, `__set__(value: Decimal)`. Exit 1:
```
<string>:30: note: Revealed type is "decimal.Decimal"
<string>:31: note: Revealed type is "__main__.Positive"
<string>:32: error: Property "length" defined in "Dimensions" is read-only  [misc]
<string>:33: error: Argument 1 to "Dimensions" has incompatible type "int"; expected "Decimal"  [arg-type]
<string>:37: error: Argument "length" to "replace" of "Dimensions" has incompatible type "str"; expected "Decimal"  [arg-type]
<string>:44: error: Incompatible types in assignment (expression has type "int", variable has type "Decimal")  [assignment]
<string>:46: note: Revealed type is "decimal.Decimal"
<string>:47: error: Incompatible types in assignment (expression has type "Decimal", variable has type "int")  [assignment]
```
- **mypy reads `= Positive()` as a default.** `Dimensions()` and `Dimensions(length=Decimal(1))` get no error, with either `__get__` shape. With the raising shape and the `Never` overload, `Dimensions()` exits 0 and the revealed class-access type is `"Never"`.
- mypy types `__init__` and `replace` parameters by `__set__`'s value type.

**F. The ch27 model** (decisions 2 and 4: `Positive`, `Dimensions`, `Consignment`, `Container`, `VOLUMETRIC_KG_PER_M3 = Decimal(167)`).
- ruff flagged only one over-long `ContainerError` message line (E501), which the member wraps.
- mypy exits 0 with `chargeable_kg` revealed as `decimal.Decimal`.

Run time:
```
volume 0.96 vars before ['_kilograms', 'dimensions', 'id']
chargeable 160.32 vars after ['_kilograms', 'chargeable_kg', 'dimensions', 'id']
heavy wins 250
replace 300 ['_kilograms', 'chargeable_kg', 'dimensions', 'id']
Dimensions(length_cm=Decimal('120'), width_cm=Decimal('80'), height_cm=Decimal('100'))
True True
payload 100
ValueError: tare_kg must be positive, got 0
ContainerError: CN-3 would exceed 28000 kg in MSKU1234565
FrozenInstanceError: cannot delete field 'chargeable_kg'
data descriptor wins: 100
non-data loses: 1
AttributeError: length_cm
TypeError: Dimensions.__init__() missing 3 required positional arguments: 'length_cm', 'width_cm', and 'height_cm'
```
- 120 x 80 x 100 cm is 0.96 m3, which is 160.32 kg chargeable at 167 kg per m3. 250 kg actual wins.
- `replace` builds a fresh instance and recomputes.
- The container number in the probe was a real-looking BIC. The member uses `"C-1"` (decision 6).
- A property with no setter: `AttributeError: property 'payload_kg' of 'Container' object has no setter`. mypy reports `Property "payload_kg" defined in "Container" is read-only  [misc]`.
- A setter decorated under a different name leaves the property read-only: `property 'tare_kg' of 'Container' object has no setter`, and mypy reports `[attr-defined]` and `[untyped-decorator]`. Not used.

**G. singledispatch registration at run time.**
```
0901.21 6109.90
TariffCodeError: no tariff code for Tea
['Coffee', 'Garment', 'object']
mappingproxy
TypeError: 'mappingproxy' object does not support item assignment
register returns fn: True 8507.60
0902.30
subclass: 0901.11 _ True
union: beverage beverage ['Coffee', 'Tea', 'object']
union register(cls,fn): other
```
- `registry` is a read-only `mappingproxy`, and there is no unregister.
- `register(cls, fn)` returns `fn`.
- An unregistered subclass takes its base's implementation (`dispatch(DecafCoffee) is registry[Coffee]`).
- A union annotation registers each member, and so does `register(A | B, fn)`.

**H. ABCs (not used).**
- A virtual subclass dispatches to the ABC's implementation, including after a late `ABC.register` (the cache is invalidated).
- Two ABCs registered for one class: `RuntimeError: Ambiguous dispatch: <class '__main__.Perishable'> or <class '__main__.Hazardous'>`.
- A `runtime_checkable` Protocol registers and dispatches structurally.

**I. Annotations at registration.**
```
TypeError: Invalid annotation for 'c'. ForwardRef('Banana', owner=<function _ at 0x...>) is an unresolved forward reference.
string annotation after class: ok 0803.90
registered inside function after class: 0803.90
TypeError generic: Invalid annotation for 'c'. list[int] is not a class.
```
- A name defined after the registration fails at the decorator. Registering after the class exists works.
- A class imported only under `if TYPE_CHECKING:` fails the same way when the module is imported (`ForwardRef('LithiumIonBattery', ...)`), and mypy exits 0.
- A forward reference inside a test function passes ruff (all root rules) and mypy, and raises at run time.
- **First-annotation rule** (not used). `@register` on `def _(c) -> str` registers `str`, and on `def _(c, n: int)` registers `int`. The 3.15.2 source reads `next(iter(get_type_hints(func, format=Format.FORWARDREF).items()))`. A function with no annotations at all gives `TypeError: Invalid first argument to register(): ... Use either @register(some_class) or plain @register on an annotated function.` mypy `--strict` reports `[no-untyped-def]` for the unannotated parameter.

**J. singledispatch and singledispatchmethod under mypy.** `object` fallback returning `str`. Exit 1:
```
<string>:24: error: Argument 1 to "register" of "_SingleDispatchCallable" has incompatible type "Callable[[Garment], int]"; expected "Callable[..., str]"  [arg-type]
<string>:31: error: No overload variant of "register" of "_SingleDispatchCallable" matches argument types "type[Tea]", "int"  [call-overload]
<string>:33: note: Revealed type is "functools._SingleDispatchCallable[str, def (commodity: object) -> str]"
<string>:34: note: Revealed type is "types.MappingProxyType[Any, def (*Any, **Any) -> str]"
<string>:35: note: Revealed type is "def (*Any, **Any) -> str"
<string>:36: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
<string>:43: error: Dispatch type "int" must be subtype of fallback function first argument "Coffee | Tea | Garment"  [misc]
<string>:45: error: Argument 1 to "strict_code" has incompatible type "int"; expected "Coffee | Tea | Garment"  [arg-type]
```
- **Object fallback.** `tariff_code(42)` gets no error. A union annotation registration is accepted. A union fallback refuses a foreign call and a foreign registration.
- **Calls against the `src`-like fallback.** A `TShirt` registration returning `int`, `code: int = tariff_code(...)` and `tariff_code(c, 'EU')` give `{"arg-type", "assignment", "call-arg"}` (`Too many arguments for "tariff_code"`). `tariff_code(42)` is silent.
- **Class and function not linked.** `tariff_code.register(Tea, garment_code)`, with `garment_code(commodity: Garment)`, and `@tariff_code.register(Tea)` over a `Garment` parameter both exit 0. At run time: `AttributeError: 'Tea' object has no attribute 'cotton'`.
- Forward-reference registration exits 0, and `list[int]` registration exits 0.
- **singledispatchmethod.** The bound method is revealed as `def (*Any, **Any) -> decimal.Decimal`. `s.surcharge(container, 'three')` and `s.surcharge()` exit 0. Only the return assignment is checked (`[assignment]`). The model's run time: `TypeError: can't multiply sequence by non-int of type 'decimal.Decimal'`.

**K. The ch28 model** (decision 6). ruff is clean. mypy reports one `[return]`: a four-case `match` on `(roasted, decaffeinated)` isn't treated as exhaustive. The member writes the `Coffee` code with conditional expressions. Run time:
```
Coffee 0901.11
Coffee 0901.12
Coffee 0901.21
Coffee 0901.22
InstantCoffee 2101.11
TShirt 6109.10
TShirt 6109.90
TariffCodeError: no tariff code for LithiumIonBattery
['Coffee', 'InstantCoffee', 'TShirt', 'object']
True True
0.00 EUR 200.00 EUR 150.00 EUR
SurchargeError: no surcharge rule for int
TypeError: can't multiply sequence by non-int of type 'decimal.Decimal'
```
- The most specific registration wins (`InstantCoffee` gets `2101.11`, not its base's code).
- `dispatch(bool)` is the fallback.
- Five days at 40.00 EUR is 200.00 EUR. Tank cleaning is flat. Dry is zero.
- `surcharge(5, DryContainer(...))` dispatches on `5`, the argument after `self`, and falls back.
- `repr(SurchargeSchedule.surcharge)` is `<single dispatch method SurchargeSchedule.surcharge>`. Not asserted.

**Sources fetched 2026-11-05.** curl, tags stripped. Prose agents re-fetch, the page text wins, and a quotation stops where the page's sentence stops. Curly apostrophes on the docs pages are kept as on the page.
- **functools** (https://docs.python.org/3/library/functools.html, banner 3.15.2):
  - `cached_property`:
    - "Transform a method of a class into a property whose value is computed once and then cached as a normal attribute for the life of the instance."
    - "The cached_property decorator only runs on lookups and only when an attribute of the same name doesn’t exist."
    - "The cached value can be cleared by deleting the attribute."
    - "The getter function could run more than once on the same instance, with the latest run setting the cached value."
    - "Also, this decorator requires that the __dict__ attribute on each instance be a mutable mapping."
    - "If a mutable mapping is not available or if space-efficient key sharing is desired, an effect similar to @cached_property can also be achieved by stacking @property on top of @lru_cache."
    - The "Changed in version 3.12" sentences contain "Python 3.12", which `check_stale_versions` flags. Paraphrase them with "since 3.12" and quote What's New instead.
  - `singledispatch`:
    - "For functions annotated with types, the decorator will infer the type of the first argument automatically"
    - "To enable registering lambdas and pre-existing functions, the register() attribute can also be used in a functional form"
    - "Where there is no registered implementation for a specific type, its method resolution order is used to find a more generic implementation."
    - "The original function decorated with @singledispatch is registered for the base object type, which means it is used if no better implementation is found."
    - "To check which implementation the generic function will choose for a given type, use the dispatch() attribute"
    - "use the read-only registry attribute"
    - Union support: write "since 3.11" and don't quote the "Changed in version" line.
  - `singledispatchmethod`:
    - "note that the dispatch happens on the type of the first non-self or non-cls argument"
    - "Note that to allow for dispatcher.register, singledispatchmethod must be the outer most decorator."
- **Descriptor guide** (https://docs.python.org/3/howto/descriptor.html, banner 3.15.2). The rendered page names no author, so credit it by title only.
  - "Descriptors let objects customize attribute lookup, storage, and deletion." This sentence uses American spelling; it's a quotation, and criterion 11 excludes quotations.
  - "If an object defines __set__() or __delete__(), it is considered a data descriptor."
  - "If an instance’s dictionary has an entry with the same name as a data descriptor, the data descriptor takes precedence."
  - "If an instance’s dictionary has an entry with the same name as a non-data descriptor, the dictionary entry takes precedence."
  - "Instance lookup scans through a chain of namespaces giving data descriptors the highest priority, followed by instance variables, then non-data descriptors, then class variables, and lastly __getattr__() if it is provided."
  - "A validator is a descriptor for managed attribute access."
  - "Since the update logic is in type.__new__(), notifications only take place at the time of class creation."
- **Data model** (https://docs.python.org/3/reference/datamodel.html):
  - `__set_name__`: "Automatically called at the time the owning class owner is created."
  - `__get__`: "This method should return the computed attribute value or raise an AttributeError exception."
  - "The @property decorator is implemented as a data descriptor." The next sentence uses "behavior": quote only this one.
  - `__slots__`: "As a result, class attributes cannot be used to set default values for instance variables defined by __slots__; otherwise, the class attribute would overwrite the descriptor assignment."
- **dataclasses** (https://docs.python.org/3/library/dataclasses.html), "Descriptor-typed fields":
  - "The value for the field passed to the dataclass’s __init__() method is passed to the descriptor’s __set__() method rather than overwriting the descriptor object."
  - "If the descriptor returns a value in this case, it will be used as the field’s default."
  - "On the other hand, if the descriptor raises AttributeError in this situation, no default value will be provided for the field."
  - The `slots` sentence is the one ch26 quotes; ch27 doesn't repeat it.
- **Built-in functions, `property`** (https://docs.python.org/3/builtins/functions.html; `library/functions.html` redirects there): "If c is an instance of C, c.x will invoke the getter, c.x = value will invoke the setter, and del c.x the deleter."
- **What's New in 3.12** (https://docs.python.org/3/whatsnew/3.12.html): "This means that a cached property getter function could now run more than once for a single instance, if two threads race."
- **PEP 487**, "Simpler customisation of class creation" (Martin Teichmann; Final; 3.6): "Descriptors are defined in the body of a class, but they do not know anything about that class, they do not even know the name they are accessed with." ch27 cites PEP 487 for `__set_name__` only. The PEP's other hook belongs to "Metaclasses, __init_subclass__, and registries", and ch27 names nothing of it.
- **PEP 252**, "Making Types Look More Like Classes" (Guido van Rossum; Final; 2.2). Pointer only.
- **PEP 443**, "Single-dispatch generic functions" (Łukasz Langa; Final; 3.4):
  - "As a result, the vast majority of registered implementations can be found adjacent to either the function being overloaded, or to a newly-defined type for which the implementation is adding support."
  - "It is only in rather infrequent cases that one will have implementations registered in a module that contains neither the function nor the type(s) for which the implementation is added."
  - ch25 already quotes the PEP's definition of single dispatch; ch28 doesn't repeat it.
- **python-patterns.guide** (Brandon Rhodes; index and 404s by curl):
  - No Visitor, Proxy or descriptor page.
  - "The Factory Method Pattern" (https://python-patterns.guide/gang-of-four/factory-method/), section "Instance attributes override class attributes": "the instance attribute wins".
- **GoF** isn't quotable (r06 finding). Bracketed items are used only if a prose agent verifies them in the book; otherwise the idea is described without attribution:
  - [Visitor lets you add an operation without changing the element classes];
  - [Proxy's virtual proxy creates an expensive object on demand].
- **O'Reilly**: *Fluent Python* 2nd ed. is confirmed. Its descriptor and single-dispatch chapter titles weren't visible, so both stay bracketed.

Repo facts:
- **Reconciliation.** Rows run 1-146, so r13 adds 147-159. Two open legacy rows belong to r13:
  - row 9 (ch28: registration by annotation, including unions, on 3.15);
  - row 10 (ch28: `singledispatchmethod` dispatches on the first argument after `self`).

  `CLAIMS_FIRST_ENFORCED = 47`, so both are legacy; P2 gives them test tokens and a status. No row names ch27. Row 43 (ch8, slots and weak references) is cited by neither chapter and doesn't change.
- **Figures.** `_data/diagrams.yml` has 27 entries; r13 makes 29 (`section: "Ch. 27"` and `"Ch. 28"`).
- **Test names.** There are 640 unique `def test_` names across `examples` and `spikes`. The three known duplicates are unchanged.
  - Every name in the Example spec was checked against the set, and none clashes.
  - Near-misses not reused: `test_cached_property_is_lazy_initialisation_without_a_proxy` and `test_visitor_is_singledispatch_without_accept` (ch3), `test_functools_cache_on_a_method_keeps_the_instance_alive` (ch26), `test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback` and `test_mypy_accepts_a_singledispatch_visitor_that_misses_an_event` (ch25).
- **Already taught, so not repeated.** Each gets a pointer by title and at most one sentence:
  - **"The three-way split: dissolve, survive, disambiguate"**: the `@property`/descriptors-against-Proxy row, `LazyTrackingHistory` with `cached_property`, and the singledispatch `describe`. ch27 goes deeper on the mechanism and doesn't use `TrackingHistory`.
  - **"Dataclasses and value semantics"**: frozen as a `__setattr__` guard, `__post_init__` validation, `slots=True` and `weakref_slot`. ch27 uses them and doesn't re-teach them.
  - **"Decorator the pattern vs @decorator the syntax, and Proxy"**: the surrogate proxy and the forwarding `__getattr__` proxy. It points to ch27 for `property` and `cached_property`.
  - **"Decorators done right"**:
    - functions bind `self` because they're descriptors;
    - a class-based wrapper doesn't;
    - `functools.cache` on a method keeps the instance alive (B019 and its test).
  - **"Singleton: module, Borg, and metaclass"**: `functools.cache` isn't call-once under threads, and module state carries between tests (`cache_clear`).
  - **"Visitor, Memento, and Interpreter"**:
    - closed versus open;
    - the silent fallback and mypy accepting a missing registration;
    - first-argument dispatch;
    - PEP 443's definition.

    ch28 repeats none of their tests.
  - **"Protocol, duck typing, and structural typing with mypy"**: callback Protocols. Not needed.
  - **"Proving it works: pytest, pytest-mock, and mypy"**: the mypy-API helper and deletion tables.
- **Stubs whose ground must not be taken or described.** Prose names no content for any of them:
  - "Metaclasses, __init_subclass__, and registries": one pointer from ch27 at most, for class-creation hooks other than `__set_name__`;
  - "Dynamic attributes: __getattr__ and Proxy as a feature": one pointer from ch27, after the lookup-chain quotation;
  - "Shortcut patterns: dict dispatch, function tables, and EAFP": no dict dispatch in either `src`;
  - "The GIL and performance": the ch27 thread test asserts an outcome only;
  - "Final project".
- **Status board hygiene.**
  - r12.x is tagged, but r12's N7 still reads `todo`, PDP-125a to PDP-126c read `active`, and `iteration-plan.md` marks r12 "(active)". The orchestrator closes them at P0.
  - The stray "(None yet...)" line in r12's Corrections is history and is left alone.

## What is new in each chapter

**ch27 (survives; Proxy's lazy-initialisation sense disambiguated).** "The three-way split" shows one `cached_property`, and "Decorators done right" shows that functions are descriptors. This chapter adds:
- **One attribute, then many.**
  - A read-only computed `property` and a validating property pair.
  - The same rule on six fields in three classes as one `Positive` descriptor that learns each field's name in `__set_name__`.
  - A copy-pasted setter that drifts.
- **Lookup precedence.** A data descriptor beats the instance dictionary, and an instance-dictionary entry beats a non-data descriptor. Class access is the `instance is None` case.
- **Descriptors on dataclasses.**
  - Class access decides the default.
  - A frozen class refuses a descriptor that writes with `setattr`.
  - `replace` re-validates.
  - `slots=True` replaces the descriptor silently.
  - mypy types fields by `__set__`'s value, and reads every descriptor field as defaulted.
- **`cached_property` as lazy initialisation.**
  - Computed on first read and stored in `__dict__`.
  - It needs that `__dict__`, can't be cleared on a frozen class, and goes stale over mutable state.
  - Since 3.12 its getter can run twice under threads.

**ch28 (Visitor dissolves).** "Visitor, Memento, and Interpreter" shows that an open set trades the exhaustiveness check for extension. This chapter adds:
- **Registration.**
  - By annotation, and the most specific class wins.
  - An unregistered subclass silently takes its base class's code.
  - Unions register each member. `register(cls, fn)` registers an existing function.
  - `dispatch()` and the read-only `registry`.
- **The fallback is a decision.** A raising fallback names the unregistered kind, and a defaulting one answers silently.
- **What fails at definition, and what mypy can't see.**
  - A forward reference, or a `TYPE_CHECKING`-only import, raises at registration.
  - A generic alias is refused.
  - mypy accepts all of these, and also a `register(cls, fn)` whose class and parameter differ.
- **What mypy 2.4.1 checks.**
  - Calls and return types against the fallback's signature.
  - A union fallback refuses foreign kinds and so closes the set.
  - Nothing about a kind never registered.
- **Global state.**
  - Another module's registration exists only once that module is imported.
  - The registry can't be edited or undone, so tests use fresh dispatchers and fresh interpreters.
- **`singledispatchmethod`.** It dispatches on the argument after `self`, and mypy doesn't check its arguments.

## Approach

- **Thesis wording.**
  - ch27 says the descriptor protocol is the language's and the design survives (decision 1). It says `cached_property` is lazy initialisation with no surrogate, disambiguating Proxy.
  - ch28 says Visitor dissolves into `singledispatch` for an open set. What remains is the fallback, where registrations live and who imports them.
- **Credit.**
  - GoF for Visitor (ch28) and Proxy (ch27), in plain paraphrase.
  - Rhodes's Factory Method page in ch27 only.
  - The functools, descriptor-guide, data-model, dataclasses, builtins and What's New pages.
  - PEPs 487, 252 and 443 by author and title.
  - Every quotation is exact, from fetched pages.
- **Domain names** come from `_plans/shipping-domain-model.md` rows 27-28, the area table and the series supporting names, plus the names below, recorded at P0. There's no new domain area and no new carrier code.
  - **ch27** (Consignment area): `ConsignmentId`, `Positive`, `Dimensions`, `Consignment`, `Container`, `ContainerError`, `VOLUMETRIC_KG_PER_M3`, `chargeable_kg`, `payload_kg`, `load`.
  - **ch28** (Consignment area kinds, Customs lookup, Rating surcharge):
    - commodity kinds `Coffee`, `InstantCoffee`, `TShirt`, `LithiumIonBattery`;
    - `tariff_code`, `TariffCodeError`, the `dangerous_goods` module;
    - container kinds `DryContainer`, `ReeferContainer`, `TankContainer`;
    - `SurchargeSchedule`, `surcharge`, `SurchargeError`, `Money`.
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/27-descriptors-and-properties` (project `descriptors-and-properties`, package `descriptors_properties`);
  - `examples/28-singledispatch` (project `singledispatch-visitor`, package `singledispatch_visitor`).
- **mypy witnesses** copy the r12 `_run`/`_codes` helper from `examples/26-decorators-done-right/tests/test_static.py`:
  - `mypy_path` set to the member's `src`;
  - `--cache-dir os.devnull`;
  - the anchored regex `re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)`.

  Each asserts the exit status, an exact `_codes()` set and one or two stable substrings. It never asserts line numbers or optional notes; a requested `reveal_type` note may be matched by substring.
- **Static-test mutation rule (from the r12 Corrections).** Every static test names, in the Example spec, the thing its prose credits and a plausible mutation of that thing that makes the test fail.
  - A test that imports `src` names a `src` mutation.
  - A reduced-model test credits mypy only, and the prose names it as a reduced model.
  - **An exit-0 test must also exercise the hazard at run time.** Its snippet is executed in a fresh namespace (`exec(snippet, namespace)` with `namespace: dict[str, object] = {}`), or the `src` call it type-checks is run, and the runtime half is asserted too. Without that, a meaningless snippet would pass. Removing the hazard from the snippet (for example dropping `slots=True`) must fail the test.
  - A prose sentence may claim no more than the test's mutation can falsify.
- **Repair rule (from the r12 Corrections).** After every repair to a sentence, the validator re-reads the paragraph and the close bullets that depend on it, so a repair can't make another sentence false. Scope words ("every", "only", "never", "all", "both", "silently") must each name the test that witnesses the whole scope, or be cut.
- **Excerpt rule (from the r12 Corrections).** An excerpt can't break an owner decision:
  - no `slots=True` on a class that holds a `Positive` field or a `cached_property`;
  - no registration on a `src` dispatcher inside a test excerpt;
  - no second comparison excerpt.

  N6-style validation checks each excerpt against decisions 4, 7 and 9.
- **Comparison code** (the owner's 2026-11-04 rule). Every comparison form is real, runs on the shared table **as a conftest fixture param**, and appears in at most one excerpt per chapter:
  - ch27 `field_form` `descriptor|property`; the excerpt is the twin's `height_cm` pair.
  - ch28 `fallback_form` `raising|defaulting`; the excerpt is the defaulting fallback.

  Forms live in `tests/conftest.py`, because sibling test imports are blocked under `--import-mode=importlib`. A form that fails a row on purpose gets its own test and isn't a table row: the drifted copy, the defaulting fallback's silent answer, the stale cache.
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (P1a, P1b) name the test and say why it sees the deletion. A row whose witness was predicted but not run is marked "executor check".
- **"Silently", "not called", "not stored" and "stale" claims.** Each has a test that fails on a named mutation:
  - not stored before first read (mutation: `chargeable_kg` computed in `__post_init__`);
  - stale over mutable state (mutation: the test's class uses `property`);
  - the defaulting form answers silently (mutation: its fallback raises);
  - unregistered before import (mutation: `tariff.py` imports `dangerous_goods`).
- **Determinism.**
  - No `mock`, `mocker`, `monkeypatch`, `print(`, `sleep`, `time.time`, `perf_counter` or `datetime.now` in tests.
  - The thread test uses `threading.Barrier(2, timeout=10)` inside the getter. A healthy run never reaches the guard timeout. The test asserts the exact getter count, `2`.
  - Isolated runs use `sys.executable -I -c` and JSON on stdout, as ch18 does.
  - No test process imports `dangerous_goods`. No test registers on a `src` dispatcher.
  - `filterwarnings = ["error"]` stays active.
- **Counts** of test functions and cases come from the code, and the pytest summary line wins.

Rejected:
- `slots=True` on any ch27 class with a `Positive` field or a `cached_property`.
- `property` over `functools.cache` or `lru_cache` anywhere in `src`.
- `__getattr__` or `__getattribute__` in either `src`.
- A dict dispatch table, a union type alias as ch28's fallback type in `src`, ABCs, `_clear_cache`, registry copying, `typing.cast`, `Any`.
- Registering on a `src` dispatcher from a test process.

## Per-chapter spec

### ch27: Descriptors and properties (pattern, has_example = true, bucket: survives; Proxy's lazy-initialisation sense disambiguated)

Thesis: Python's attribute lookup calls `__get__` and `__set__` for you, and `property` and `cached_property` are descriptors already written. The design that survives:
- one validator per rule, shared by every field that needs it;
- `property` for one attribute, a descriptor for a rule, `cached_property` for a value whose inputs can't change;
- placement against `@dataclass`: frozen works if the descriptor writes through `vars()`, and `slots=True` removes it.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one from a comparison fixture):

1. `## Learning objectives` (~100), five bullets, one per close bullet:
   - choose `property`, a descriptor or `cached_property` for an attribute;
   - write a validating descriptor with `__set_name__`;
   - predict which of descriptor and instance dictionary wins a lookup;
   - put a descriptor on a dataclass and type it for mypy;
   - cache a computed value without a proxy, and know when it goes stale.
2. `## Why this matters` (~180). Intent first: weights and extents arrive from carrier feeds and must be finite and positive everywhere. Three failures:
   - a setter copied to a third field without its finiteness check accepts infinity (test 6);
   - a slotted dataclass silently drops the validator (test 29);
   - a cached payload reads 100 kg after a second load (test 24).
3. Figure plus one paragraph (~60).
4. `## One attribute: property` (~250). Excerpt `Container.payload_kg` and `load`.
   - The computed property is recomputed after each load (test 8). A property with no setter refuses assignment with the 3.15.2 message (test 7). `load` refuses a consignment over the limit (test 9).
   - Then the comparison excerpt, the property twin's `height_cm` pair: one validating property per field. Both forms pass the same table (test 1).
   - The drifted copy accepts infinity (test 6), which is the force for the next section.
   - Quote the builtins `property` sentence.
5. `## A rule for many fields: a descriptor` (~450). Excerpt `Positive`.
   - Quote the descriptor guide's "A validator is a descriptor for managed attribute access." and PEP 487's sentence (Teichmann) on descriptors not knowing their name.
   - `__set_name__` gives each field its own name and storage (test 4). The data-model `__set_name__` sentence and the guide's "only at class creation" sentence are quoted.
   - Six fields in three classes share one class (test 5). Each refuses a bad value with its own name in the message (test 2), on construction and on assignment (test 3).
   - Class access is the `instance is None` case, and `Positive` raises there (test 12). Quote the data-model `__get__` sentence.
   - The GoF credit isn't needed here: this isn't a catalogue pattern.
6. `## Who wins a lookup` (~250):
   - Quote the guide's two precedence sentences and the lookup-chain sentence. The data-model sentence says `property` is a data descriptor.
   - A value planted in the instance dictionary doesn't shadow `Positive` (test 10), and does shadow `cached_property` (test 11).
   - One clause from Rhodes: for plain class attributes "the instance attribute wins"; a data descriptor is the exception.
   - One sentence pointing to "Dynamic attributes: __getattr__ and Proxy as a feature" for the last link in the chain, describing nothing.
7. `## Descriptors in a dataclass` (~400). Excerpt `Dimensions`.
   - Quote the dataclasses descriptor-typed-fields sentences. A field whose descriptor raises on class access has no default (test 13). One that returns itself becomes the default (test 14).
   - A frozen class refuses a descriptor that writes with `setattr` (test 15), which is why `Positive` writes through `vars()`. Assignment after construction is refused (test 16). `replace` validates (test 17). Equal values compare and hash equal (test 18).
   - mypy types each field by `__set__`'s value (test 26), and reads `= Positive()` as a default whatever `__get__` does (test 27). Both are said as observed on mypy 2.4.1.
   - `slots=True` replaces the descriptor with a slot and accepts `-1` (test 29), and mypy exits 0. Quote the data-model `__slots__` sentence. One sentence pointing to "Dataclasses and value semantics" for what `slots=True` costs elsewhere.
8. `## cached_property: lazy initialisation without a proxy` (~420). Excerpt `Consignment.chargeable_kg`.
   - Bucket sentence: Proxy's lazy-initialisation sense needs no surrogate. One pointer each to "Decorator the pattern vs @decorator the syntax, and Proxy" and "The three-way split: dissolve, survive, disambiguate". [GoF on the virtual proxy, if verified.]
   - Quote the functools "computed once" and "only runs on lookups" sentences.
   - The value isn't in `__dict__` before the first read and is after (test 19). It's the larger of actual and volumetric weight (test 20). `replace` recomputes (test 23).
   - Costs:
     - it needs a `__dict__` (test 21; quote "requires that the __dict__ attribute ... be a mutable mapping");
     - a frozen class refuses `del`, the documented way to clear it (test 22; quote "can be cleared by deleting the attribute");
     - over mutable state it goes stale (test 24), which is why `payload_kg` is a `property`;
     - since 3.12 the getter can run twice when two threads race (test 25; quote What's New 3.12 and the functools "could run more than once" sentence), and nothing in this member shares a consignment between threads;
     - mypy accepts it on a slotted class (test 28).
   - One sentence: the functools page suggests `@property` over `@lru_cache` where there's no `__dict__`, and "Decorators done right" shows what a method cache keeps alive. No test, no excerpt.
9. `## When not to use it` (~150):
   - a value type validated once in `__post_init__` (frozen and slotted, no descriptor);
   - one field in one class (a `property`);
   - a value derived from state that changes (a `property`, not `cached_property`);
   - a slotted class (no descriptor field, no `cached_property`).

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Specifying managed attributes.** Asked to "validate the weights", an assistant often copies a setter into every class and turns on `slots=True` for speed. Paste a prompt that states the forms:

   > Validate every positive `Decimal` field with one `Positive` descriptor that learns its name in `__set_name__`, raises `AttributeError` on class access and stores through `vars(instance)`, on dataclasses without `slots=True`. Use `@property` for a value computed from state that changes, and `functools.cached_property` only on a frozen class. Never copy a validating setter from one property to another.

   If the reply adds `slots=True` or a setter per field, ask for the test that fails.</blockquote>

   The sidebar body is at most 120 words by `validate.word_count`. Every backticked name in it exists in `src` or the standard library.
10. `## Build, run, observe` (~200 plus output).
    - Each experiment runs in a fresh scratch copy: delete the copy's `.venv`, run `uv sync --locked --all-packages`, and confirm `descriptors_properties.__file__` points into the copy.
    - Each changes one thing, then is reverted.
    - Each runs a filter chosen by the prose agent, followed by `uv run mypy --strict src tests`. **The filter is stated in the chapter, and the chapter quotes its complete output.**

    Experiments:
    - (a) In `Positive.__set__`, write with `setattr(instance, self.private_name, value)` instead of `vars(instance)[...]`.
      - Expected: every test that builds a `Dimensions` or `Consignment` fails with `FrozenInstanceError: cannot assign to field '_length_cm'`, or `'_kilograms'`. Tests on `Container` alone pass. mypy exits 0.
      - Executor check: the exact failing set, and that no test module builds a frozen instance at import (which would be a collection error).
      - Quote as observed.
    - (b) Add `slots=True` to `Dimensions`.
      - Expected:
        - the invalid `[descriptor-*]` rows of test 1 and test 2[dimensions-height_cm] fail with `DID NOT RAISE`;
        - test 4 fails because `vars()` needs a `__dict__`;
        - mypy exits 0.
      - Executor check: the exact `vars()` message, and whether any `Consignment` test fails.
      - Quote as observed.
11. `## What you can do now` (~140): five bullets, one per objective, in the same order. They name `payload_kg` with test 7, `Positive` with test 5, test 11, `Dimensions` with test 29, and `chargeable_kg` with test 24. Every backticked token in the close appears earlier in the chapter.
12. `## For deeper coverage` (~110):
    - the descriptor guide;
    - the data model's "Implementing Descriptors" and `__slots__`;
    - the functools, dataclasses and builtins pages;
    - PEPs 252 and 487;
    - Rhodes's Factory Method page;
    - [Ramalho, *Fluent Python* 2nd ed., on descriptors, if verified];
    - the bibliography link.

Figure `27-descriptors-and-properties` (vertical):
- Top accent box `Positive`, with three lines: `__set_name__` "learns the field name", `__get__`, `__set__` "validates, stores in vars()".
- Arrows down to three boxes: `Consignment` (`kilograms`), `Dimensions` (`length_cm`, `width_cm`, `height_cm`) and `Container` (`tare_kg`, `max_payload_kg`).
- Below, a three-step lookup column: "data descriptor: Positive, property", then "instance __dict__", then "non-data descriptor: cached_property".
- A side box `chargeable_kg` "cached_property: computed on first read, then read from __dict__".
- A muted, dashed box: "slots=True: a slot replaces the descriptor".
- No numbers in the SVG.

Caption draft (38 words with the prefix): "Figure 27.1: One Positive descriptor validates six fields in three classes. A lookup tries data descriptors, then the instance dictionary, then non-data descriptors, so a cached property is read from the dictionary after its first computation."

### ch28: singledispatch: the Visitor the language gives you (pattern, has_example = true, bucket: Visitor dissolves)

Thesis: for an open set of kinds, Visitor's `accept` and visitor class dissolve into one generic function. Each implementation is registered for a class, and `dispatch` picks the most specific by the method resolution order. The design that remains:
- what the fallback does;
- registering by annotation so the class and the parameter can't disagree;
- defining classes before registering;
- knowing that a registration exists only once its module is imported, process-wide and for good.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one from a comparison fixture):

1. `## Learning objectives` (~100), five bullets:
   - register implementations by annotation and predict which one runs;
   - choose what the fallback does;
   - say what fails at registration and what mypy checks;
   - extend the set from another module and test it in isolation;
   - dispatch a method on its argument.
2. `## Why this matters` (~170). Intent first: a customs declaration needs a tariff code per commodity kind, and the dangerous goods team adds kinds the customs team doesn't own. Three failures:
   - a defaulting fallback writes "unclassified" on a battery declaration (test 3);
   - instant coffee is declared under its base class's code when its own registration is missing (test 5);
   - a `TYPE_CHECKING` import passes mypy and breaks the import (test 17, experiment b).
3. Figure plus one paragraph (~60).
4. `## One function, one implementation per kind` (~380). Excerpt `tariff_code` with the `Coffee` and `InstantCoffee` registrations.
   - GoF credited for Visitor in plain paraphrase [adding an operation without changing element classes, if verified]. Bucket: dissolves, with one sentence pointing to "Visitor, Memento, and Interpreter" for the closed-set form and the first-argument rule.
   - Quote the functools "infer the type of the first argument" sentence. Registered commodities get their codes (test 1).
   - The most specific registration wins (test 4), and an unregistered subclass silently takes its base's code (test 5). Quote the MRO sentence and the "registered for the base object type" sentence.
   - `dispatch()` and the read-only `registry` show the choice (tests 6, 7; quote both functools phrases).
   - A union annotation registers each member, since 3.11 (test 8). `register(cls, fn)` registers an existing function (test 9; quote the "functional form" sentence).
5. `## The fallback is a decision` (~250). The one comparison excerpt is the defaulting fallback.
   - Both forms give the seven commodities the same codes (test 1).
   - The defaulting form answers an unregistered battery with "unclassified" and nothing raises (test 3). The raising form names the kind (test 2).
   - Say which a customs declaration wants. `object` as the fallback type keeps the set open (section 7).
6. `## What fails when the module loads` (~250):
   - An annotation naming a class defined later raises `TypeError` at registration, and so does a class imported only under `TYPE_CHECKING` (test 17 and experiment b; the message quoted with its address masked by a stated `sed`). Define or import the class at run time first.
   - A generic alias is refused, and the class is passed to `register` instead (test 10).
   - mypy accepts the forward reference (test 17).
7. `## What mypy checks, and what it can't` (~300):
   - mypy 2.4.1 types the function by its fallback's signature. It checks the return type of each registration, the call's arity and the result's use (test 14), but with an `object` fallback any argument passes.
   - A union fallback refuses a foreign argument and refuses registering a kind outside the union (test 15, reduced model). That closes the set, and the closed set is the `match` form's ground.
   - `register(cls, fn)` with a class that differs from the function's parameter passes mypy and fails at run time (test 16, reduced model). Prefer the annotation form.
   - mypy says nothing about a kind that's never registered. One clause pointing to "Visitor, Memento, and Interpreter", which shows it.
8. `## Another module extends the set` (~330). Excerpt `dangerous_goods.py`.
   - Quote PEP 443's two "adjacent" and "infrequent" sentences (Langa): this registration is the infrequent case, so it exists only once someone imports it.
   - In a fresh interpreter, a battery raises `TariffCodeError` before `dangerous_goods` is imported and gets `8507.60` after (test 11). Every importer of `tariff_code` sees it.
   - The registry can't be edited and has no unregister (test 7), so a registration made in a test lasts for the rest of the process. The tests register only on fresh dispatchers and check cross-module registration in a fresh interpreter. One sentence pointing to "Singleton: module, Borg, and metaclass" for module state carried between tests.
9. `## singledispatchmethod` (~200). Excerpt `SurchargeSchedule.surcharge`.
   - It dispatches on the container kind (test 12) and on the argument after `self`, whatever follows (test 13). Quote the functools "first non-self or non-cls argument" and "outer most decorator" sentences.
   - mypy doesn't check the method's arguments (test 18), said as observed on mypy 2.4.1.
10. `## When not to use it` (~140):
    - a closed set one team owns (`match` with `assert_never`; point to "Visitor, Memento, and Interpreter");
    - dispatch on a value, not a type (a mapping; point to "Shortcut patterns: dict dispatch, function tables, and EAFP" by title, describing nothing);
    - a single kind (a function);
    - registrations nobody is sure will be imported.

    Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Specifying a generic function.** Asked for "a lookup per commodity type", an assistant often returns a default code for unknown kinds and imports classes under `TYPE_CHECKING`. Paste a prompt that states the rules:

    > Write `tariff_code` with `functools.singledispatch` and an `object` fallback that raises `TariffCodeError`. Register each commodity kind with an annotated implementation, not `register(cls, fn)`, and import every class an annotation names at run time. In tests, never register on `tariff_code`: use a fresh dispatcher, and check another module's registrations in a fresh interpreter.

    If the fallback returns a default code, ask which test catches an unregistered kind.</blockquote>
11. `## Build, run, observe` (~180 plus output). The scratch-copy and stated-filter rules are the same as ch27's (confirm `singledispatch_visitor.__file__`).
    - (a) Delete the `InstantCoffee` registration from `tariff.py`.
      - Expected:
        - test 1[raising-instant] and [defaulting-instant] fail with `'0901.21' == '2101.11'`;
        - test 4 fails (`KeyError` or an identity check; executor check);
        - test 6's key set fails;
        - mypy exits 0.
      - Quote as observed.
    - (b) In `dangerous_goods.py`, move the `LithiumIonBattery` import under `if TYPE_CHECKING:`.
      - Expected: test 11 fails, its assertion showing the isolated run's stderr ending `is an unresolved forward reference.` (address masked). No other test fails. mypy exits 0.
      - Executor check: that ruff isn't part of the stated filter.
      - Quote as observed.
12. `## What you can do now` (~140): five bullets mapped one to one to the objectives. They name `tariff_code` with test 5, test 3, test 16, `dangerous_goods` with test 11, and `surcharge` with test 13.
13. `## For deeper coverage` (~110):
    - PEP 443;
    - the functools page;
    - GoF (Visitor);
    - [Ramalho, *Fluent Python* 2nd ed., on single dispatch, if verified];
    - the bibliography link.

Figure `28-singledispatch` (vertical):
- Top accent box `tariff_code`.
- Beneath, a registry row: `Coffee`, `InstantCoffee`, `TShirt`, `object` "fallback: raises TariffCodeError".
- An arrow labelled `dispatch(InstantCoffee)` reaching `InstantCoffee` before `Coffee` before `object`.
- To the side, a separate module box `dangerous_goods` with an arrow into the registry, labelled "registers LithiumIonBattery when imported".
- Lower, `SurchargeSchedule.surcharge` over `DryContainer`, `ReeferContainer`, `TankContainer`, "dispatch on the argument after self".
- A muted, dashed note: "mypy: checks calls against the fallback, not which kinds are registered".
- No numbers in the SVG.

Caption draft (41 words with the prefix): "Figure 28.1: tariff_code picks the most specific registered class and falls back to a function that raises. A registration made in another module exists only after that module is imported, and a method dispatches on the argument after self."

Citations, both chapters: verify each before writing, apply the bracketed fallbacks, quote no sentence unless it was checked on a fetched page, stop each quotation where the page's sentence stops, and make no comparison between languages.

## Example spec

### `examples/27-descriptors-and-properties` (project `descriptors-and-properties`, package `descriptors_properties`)

`pyproject.toml` in the r12 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`).

- `fields.py`: `Positive` (decision 4, evidence F). Its docstring says class access raises so a dataclass field has no default, and that storage goes through `vars()` so frozen dataclasses accept it.
- `cargo.py`:
  - `ConsignmentId = NewType("ConsignmentId", str)`.
  - `VOLUMETRIC_KG_PER_M3 = Decimal(167)`, illustrative.
  - `ContainerError(Exception)`.
  - `Dimensions`: `@dataclass(frozen=True)`, three `Positive` fields, and `volume_m3` as a `property` (cm cubed over 1,000,000).
  - `Consignment`: `@dataclass(frozen=True, kw_only=True)`, with `id`, `kilograms: Positive = Positive()` and `dimensions`, plus `@cached_property chargeable_kg` (the larger of `kilograms` and volume times the factor).
  - `Container`: `@dataclass(eq=False)`, with `number: str`, `tare_kg` and `max_payload_kg` as `Positive`, and `consignments: list[Consignment] = field(default_factory=list)`. It has:
    - `payload_kg` as a `property` (the sum of `kilograms`, `Decimal(0)` start);
    - `load(consignment)`, which raises `ContainerError(f"{id} would exceed {max_payload_kg} kg in {number}")` when payload plus the new kilograms is strictly greater than the maximum.
  - Each class's docstring says why it isn't slotted.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `dimensions` (120, 80, 100 cm), `consignment(kilograms)` and `container` (`"C-1"`, 2200, 28000) factories.
- `field_form` params `descriptor|property`, each giving a constructor from three `Decimal`s to an object with the three extents. `property` is `_PropertyDimensions` (decision 9). Typed with a small Protocol; no `Any`.
- `EXTENT_ROWS`: `valid`, `length-zero`, `width-negative`, `height-nan`, `height-infinity`.

`test_fields.py`:
1. `test_every_field_form_validates_the_same_extents` x `field_form` (2) x `EXTENT_ROWS` (5) = 10: values read back, or `ValueError` matching `<field> must be positive`.
2. `test_a_positive_field_refuses_a_bad_value_on_every_class[consignment-kilograms|dimensions-height_cm|container-tare_kg|container-max_payload_kg]` (4).
3. `test_assignment_to_a_container_field_is_validated`: `tare_kg = Decimal(0)` raises, and the old value stays.
4. `test_set_name_gives_each_field_its_own_storage`: `vars(dimensions) == {"_length_cm": ..., "_width_cm": ..., "_height_cm": ...}`.
5. `test_one_descriptor_class_validates_every_field`: the six class-dict entries are all `Positive`, read through `vars(cls)` and not getattr.
6. `test_a_copy_pasted_property_validator_drifts`: a test-local copy whose `height_cm` setter omits `is_finite()` accepts `Decimal("Infinity")`, and `src` `Dimensions` refuses it. Domain row 27's failing test.
7. `test_a_property_without_a_setter_refuses_assignment`: `AttributeError` matching `has no setter`.
8. `test_payload_is_recomputed_after_each_load`: 100, then 350.
9. `test_load_refuses_a_consignment_over_the_max_payload[at-the-limit|over]` (2): exactly 28,000 kg is accepted, and 28,050 raises `ContainerError` matching `would exceed 28000 kg`.

`test_lookup.py`:
10. `test_a_data_descriptor_takes_precedence_over_the_instance_dict`: `vars(c)["kilograms"] = Decimal(999)`; `c.kilograms` is still 100.
11. `test_an_instance_dict_entry_takes_precedence_over_cached_property`.
12. `test_class_access_to_a_positive_field_raises_attribute_error`: on `Container`, matching `tare_kg`.

`test_dataclasses.py`:
13. `test_a_descriptor_field_has_no_default_when_class_access_raises`: every `fields(Dimensions)` default is `MISSING`, and `Dimensions()` raises `TypeError` matching `missing 3 required positional arguments`. Carries one `# type: ignore[call-arg]` only if mypy asks for it (it won't, evidence E): executor check, with no unused ignore.
14. `test_a_descriptor_that_returns_itself_on_class_access_becomes_the_default`: a test-local subclass of `Positive` whose `__get__` returns `self`. `Box()` raises `AttributeError` matching `has no attribute 'is_finite'`.
15. `test_a_frozen_dataclass_refuses_a_descriptor_that_writes_with_setattr`: `FrozenInstanceError` matching `cannot assign to field '_length_cm'`.
16. `test_a_frozen_dataclass_refuses_assignment_to_a_descriptor_field`: matching `cannot assign to field 'length_cm'`. One `# type: ignore[misc]`.
17. `test_replace_validates_the_new_value`.
18. `test_equal_dimensions_compare_and_hash_equal`.

`test_cached.py`:
19. `test_chargeable_weight_is_computed_on_first_access_and_stored`: `"chargeable_kg" not in vars(c)` before the first read and in it after.
20. `test_chargeable_weight_is_the_larger_of_actual_and_volumetric_weight[bulky|heavy]` (2): 100 kg gives `Decimal("160.32")`, and 250 kg gives 250.
21. `test_cached_property_needs_an_instance_dict`: a test-local `@dataclass(frozen=True, slots=True)` raises `TypeError` matching `No '__dict__' attribute`.
22. `test_a_frozen_dataclass_cannot_clear_a_cached_property`: `FrozenInstanceError` matching `cannot delete field 'chargeable_kg'`.
23. `test_replace_recomputes_the_chargeable_weight`: 300 after `replace(kilograms=300)`.
24. `test_a_cached_property_over_mutable_state_goes_stale`: a test-local `Container` subclass with `cached_property` `payload_kg` reads 100 after the second load, and `src` reads 350.
25. `test_a_cached_property_getter_can_run_twice_under_threads`: two threads and `Barrier(2, timeout=10)` in the getter. The getter count is 2. The docstring cites the 3.12 change.

`test_static.py` (each row: credited thing; mutation that fails it):
26. `test_mypy_types_a_positive_field_by_its_set_value`: imports `src`; `{"arg-type", "assignment", "misc"}` (`Dimensions(120, ...)`, `container.tare_kg = 5`, `dimensions.length_cm = Decimal(1)`), plus a revealed `decimal.Decimal`. Credits `Positive.__set__`'s annotation. Mutation: `value: object` makes the code set lose `arg-type` and `assignment`.
27. `test_mypy_reads_a_descriptor_field_as_a_default`: imports `src`; `Dimensions()` exits 0, empty output, paired with the run-time `TypeError`. Credits mypy's reading of `= Positive()`. Mutation: declaring a field without the descriptor default gives `[call-arg]`.
28. `test_mypy_accepts_cached_property_on_a_slotted_dataclass`: reduced model; exits 0, and `exec` of the same snippet raises `TypeError` `No '__dict__' attribute`. Mutation: dropping `slots=True` from the snippet fails the runtime half.
29. `test_mypy_accepts_a_descriptor_field_on_a_slotted_dataclass`: snippet imports `src` `Positive`; exits 0, and `exec` accepts `Decimal(-1)` with the class attribute's type named `member_descriptor`. Mutation: dropping `slots=True` gives `ValueError` and fails the test. Domain row 27's silent failure.

Numbers are spec ids, not file order. The plan has 29 test functions and 44 cases:
- `test_fields.py`: 9 functions, 22 cases;
- `test_lookup.py`: 3 functions, 3 cases;
- `test_dataclasses.py`: 6 functions, 6 cases;
- `test_cached.py`: 7 functions, 8 cases;
- `test_static.py`: 4 functions, 4 cases.

The executor counts from the pytest summary line.

Also `README.md` and the card `_examples/27-descriptors-and-properties.md`: `order: 27`, eyebrow "Idiomatic Python · Descriptors", and a concept title with no count. None of the following appears in `src/`: `mock`, `monkeypatch`, `print(`, `Optional`, `Any`, `cast`, `slots=True`, `__slots__`, `lru_cache`, `functools.cache`, `__getattr__`, `__getattribute__`, `__init_subclass__`, `threading`, `TrackingHistory`.

Deletion table (P1a):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `is_finite()` in `__set__` | removed | 1[descriptor-height-nan], 1[descriptor-height-infinity] | `InvalidOperation` is not `ValueError`; infinity accepted |
| `> 0` | `>= 0` | 1[descriptor-length-zero] | `DID NOT RAISE` |
| private name per field | fixed `"_value"` | 4, 1[descriptor-valid] | one slot shared; values read back wrong |
| field name in the message | generic message | 2[all] | `match` fails |
| `vars()` write | `setattr` (experiment a) | frozen tests (executor names them) | `FrozenInstanceError` |
| class access raises | `return self` | 12, 13 | no `AttributeError`; a default appears |
| `Positive` on `Container` fields | plain annotations | 2[container-*], 3, 5 | no validation on the entity |
| `frozen=True` on `Dimensions` | removed | 16 | `DID NOT RAISE` |
| `payload_kg` recomputed | `cached_property` | 8 | 100 after the second load |
| `load` limit `>` | `>=` | 9[at-the-limit] | refused at exactly 28,000 kg |
| `load` check | removed | 9[over] | `DID NOT RAISE` |
| `max` in `chargeable_kg` | returns `kilograms` | 20[bulky] | 100, not 160.32 |
| volumetric factor | 166 | 20[bulky] | 159.36 |
| `chargeable_kg` lazy | computed in `__post_init__` (via `vars()`) | 19 | present before the first read |
| no `slots=True` on `Dimensions` | added (experiment b) | 1, 2[dimensions-height_cm], 4 | validator replaced |

### `examples/28-singledispatch` (project `singledispatch-visitor`, package `singledispatch_visitor`)

- `money.py`: `Money(amount: Decimal, currency: str)`, frozen slotted, with `times(days: int) -> Money` rounding to cents and `__str__` giving `"200.00 EUR"`.
- `commodities.py`: `Coffee(roasted: bool, decaffeinated: bool = False)`, `InstantCoffee(Coffee)`, `TShirt(cotton: bool)`, `LithiumIonBattery(watt_hours: Decimal)`, all frozen slotted.
- `tariff.py`:
  - `TariffCodeError(LookupError)`.
  - `@singledispatch def tariff_code(commodity: object) -> str`, raising `TariffCodeError(f"no tariff code for {type(commodity).__name__}")`.
  - Annotated registrations for `Coffee` (conditional expressions, evidence K), `InstantCoffee` and `TShirt`.
  - It imports nothing from `dangerous_goods`. Its docstring says the fallback raises on purpose.
- `dangerous_goods.py`: imports `tariff_code` and `LithiumIonBattery` at run time and registers `8507.60` by annotation. Its docstring says the registration exists once this module is imported.
- `surcharges.py`: `DryContainer(number)`, `ReeferContainer(number, set_point_c: Decimal)`, `TankContainer(number)`, `SurchargeError(LookupError)`, and `SurchargeSchedule(reefer_per_day: Money, tank_cleaning: Money)`, frozen slotted. `@singledispatchmethod surcharge(self, container: object, days: int) -> Money` has:
  - a fallback raising `SurchargeError(f"no surcharge rule for {type(container).__name__}")`;
  - a dry container giving zero in the reefer rate's currency;
  - a reefer giving `reefer_per_day.times(days)`;
  - a tank giving `tank_cleaning`.
- `py.typed`, `__init__.py` (imports no submodule).

`tests/conftest.py`:
- `COMMODITY_CODES`, seven rows: `coffee-green`, `coffee-green-decaf`, `coffee-roasted`, `coffee-roasted-decaf`, `instant`, `tshirt-cotton`, `tshirt-other`, with codes `0901.11`, `0901.12`, `0901.21`, `0901.22`, `2101.11`, `6109.10`, `6109.90`.
- `fallback_form` params `raising|defaulting` (decision 9). `defaulting` registers `tariff_code.registry[cls]` for `Coffee`, `InstantCoffee` and `TShirt` on a new dispatcher whose fallback returns `"unclassified"`.
- `fresh_dispatcher`: a new raising `@singledispatch` per test (decision 7).
- `schedule`: 40.00 EUR per reefer day, 150.00 EUR tank cleaning, illustrative.

`test_tariff.py`:
1. `test_every_fallback_form_gives_registered_commodities_their_codes` x `fallback_form` (2) x `COMMODITY_CODES` (7) = 14.
2. `test_a_raising_fallback_names_an_unregistered_kind`: `TariffCodeError` matching `no tariff code for LithiumIonBattery`.
3. `test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently`: `"unclassified"`, no exception. Domain row 28's failing test.
4. `test_the_most_specific_registration_wins`: `tariff_code.dispatch(InstantCoffee) is tariff_code.registry[InstantCoffee]`, and it isn't `registry[Coffee]`.
5. `test_an_unregistered_subclass_gets_its_base_class_code`: a fresh dispatcher with only `registry[Coffee]` registered gives `InstantCoffee(roasted=True)` `"0901.21"`.
6. `test_dispatch_and_registry_show_the_chosen_implementation`: keys `{object, Coffee, InstantCoffee, TShirt}`; `dispatch(bool) is registry[object]`.
7. `test_the_registry_is_read_only`: `TypeError` matching `does not support item assignment`, and no `unregister` attribute. One `# type: ignore[index]` if mypy asks (executor check).

`test_registration.py` (all on `fresh_dispatcher`):
8. `test_a_union_annotation_registers_each_member`.
9. `test_register_with_a_class_and_a_function_registers_the_function`: returns the function, which is then dispatched to.
10. `test_a_generic_alias_is_refused_at_registration`: `TypeError` matching `is not a class`.
11. `test_another_module_extends_the_set_when_it_is_imported`: `_run_isolated`. Before: the `TariffCodeError` message; after `import singledispatch_visitor.dangerous_goods`: `"8507.60"`; the registry keys include `LithiumIonBattery`. Domain row 28's import-order failing test.

`test_surcharges.py`:
12. `test_surcharge_dispatches_on_the_container_kind[dry|reefer|tank]` (3): five days give `0.00 EUR`, `200.00 EUR` and `150.00 EUR`.
13. `test_singledispatchmethod_dispatches_on_the_first_argument_after_self`: the same reefer with 1 and 5 days takes the same implementation; `surcharge(5, DryContainer("C-1"))` raises `SurchargeError` matching `no surcharge rule for int`. Carries one `# type: ignore` only if mypy asks (it won't, evidence J): executor check. Closes legacy row 10.

`test_static.py` (each row: credited thing; mutation that fails it):
14. `test_mypy_checks_calls_and_registrations_against_the_fallback`: imports `src`; `{"arg-type", "assignment", "call-arg"}`. Stdout doesn't contain `Argument 1 to "tariff_code"` (the `tariff_code(42)` line). Credits `tariff_code`'s `object` fallback. Mutation: retyping the fallback to a union of the kinds adds that message and fails the test.
15. `test_mypy_refuses_a_kind_outside_a_union_fallback`: reduced model; `{"misc", "arg-type"}`, `must be subtype of fallback function first argument`. Mutation: widening the snippet's fallback to `object` empties the set.
16. `test_mypy_accepts_a_registered_class_that_differs_from_the_parameter`: reduced model; exits 0, and `exec` raises `AttributeError` matching `has no attribute 'cotton'`. Mutation: the annotation form with the right class makes the runtime half pass the call, so the test fails.
17. `test_mypy_accepts_a_forward_reference_that_fails_at_registration`: reduced model; exits 0, and `exec` raises `TypeError` matching `unresolved forward reference`. Mutation: defining the class first fails the runtime half.
18. `test_mypy_does_not_check_the_arguments_of_a_singledispatchmethod`: imports `src`; `schedule.surcharge(ReeferContainer(...), "three")` exits 0, and the same call at run time raises `TypeError` matching `can't multiply sequence`. Credits the `singledispatchmethod` decoration. Mutation: a plain typed method gives `[arg-type]`.

Numbers are spec ids, not file order. The plan has 18 test functions and 33 cases:
- `test_tariff.py`: 7 functions, 20 cases;
- `test_registration.py`: 4 functions, 4 cases;
- `test_surcharges.py`: 2 functions, 4 cases;
- `test_static.py`: 5 functions, 5 cases.

The executor counts from the pytest summary line.

Test 11's isolated code and experiment (b) are the only places `dangerous_goods` is imported at run time. `grep -n "dangerous_goods" tests/` hits only inside `_run_isolated` code strings and `test_static.py` snippets that mypy reads.

Also `README.md` and the card `_examples/28-singledispatch.md`: `order: 28`, eyebrow "Idiomatic Python · singledispatch", and a concept title. None of the following appears in `src/`: `mock`, `monkeypatch`, `print(`, `Optional`, `Any`, `cast`, `TYPE_CHECKING`, `isinstance`, `HandlingEvent`, `DocumentKind`, `abc`, `_clear_cache`, a `dict[` dispatch table, `match`.

Deletion table (P1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `InstantCoffee` registration | removed (experiment a) | 1[*-instant], 4, 6 | `0901.21` from the base class |
| `Coffee` roasted branch | inverted | 1[*-coffee-*] | wrong subheading |
| `Coffee` decaf branch | ignored | 1[*-decaf] | `0901.11` for decaf |
| `TShirt` cotton branch | inverted | 1[*-tshirt-*] | swapped codes |
| raising fallback | returns `"unclassified"` | 2 | `DID NOT RAISE` |
| kind named in the message | generic | 2 | `match` fails |
| `dangerous_goods` registration | removed | 11 | still `TariffCodeError` after import |
| run-time import in `dangerous_goods` | under `TYPE_CHECKING` (experiment b) | 11 | `TypeError` at import |
| reefer `times(days)` | flat rate | 12[reefer] | 40.00, not 200.00 |
| tank cleaning | `Money` zero | 12[tank] | 0.00 |
| dry zero | reefer rate | 12[dry] | 40.00 |
| surcharge fallback raises | returns zero | 13 | `DID NOT RAISE` |
| `object` fallback type | union of kinds | 14 | `tariff_code(42)` now reported |
| `singledispatchmethod` | plain typed method with `match` | 18, 12 | mypy reports `[arg-type]` |

## Steps and status

Step ids are `P*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| P0 | This plan file. PDP-127a-c and 128a-c `active` in `iteration-plan.md` (dated note); r13 marked active and r12 closed; PDP-125a to 126c closed; r12's N7 closed. Reconciliation rows 147-159 `open` with a dated r13 note; rows 9-10 noted "r13". Domain rows 27-28 updated with the supporting names and decisions 1-10 (row 28's bucket reworded per decision 1), with a dated note. ch27-28 stub `description` lines written. Upstream pins re-checked. Decisions recorded | - | done |
| P1a | ch27 member, card, README; one `uv lock`; three green runs plus one reverse-file-order run; the deletion table, each row in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`), deleted after use | P0 | done |
| P1b | ch28 member, card, README; one `uv lock` after P1a (sequenced for `uv.lock`); three green runs plus one reverse-order run; deletion table | P1a | done |
| P2 | Witness results into rows 147-158 and rows 9-10 (both verified (r13)); the dated r13 note in `_plans/spikes.md` (evidence D, I, J). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | P1b | done |
| P3 | Two figures, specs `diagrams/specs/27-*.py` and `28-*.py`, `_data/diagrams.yml` (single owner; 29 entries); figures 00-26 unchanged; every name drawn exists in `src` or the standard library | P2 | done |
| P4 | ch27-28 `status = "drafted"` (`kind` stays `pattern`) | P3 | done |
| P5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly, runs its two experiments in fresh scratch copies with the filter it states, quotes that filter's complete output through `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table that names, for each static-test citation, the mutation that fails it | P3, P4 | done |
| P6 | Opus validation; up to two repair rounds, with a seam scan and a dependent-sentence re-read after every cut, a check that close bullets map one to one to objectives, and an excerpt check against decisions 4, 7 and 9 | P5 | todo |
| P7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r13.x` on main; notes-only release | P6 | todo |

Reconciliation rows (step P0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 147 | 27 | One `Positive` descriptor validates every positive field of `Consignment`, `Dimensions` and `Container`, on construction and assignment, each with its own name and storage; a property form passes the same table and a copy-pasted property drifts | `test_every_field_form_validates_the_same_extents`, `test_a_positive_field_refuses_a_bad_value_on_every_class`, `test_assignment_to_a_container_field_is_validated`, `test_set_name_gives_each_field_its_own_storage`, `test_one_descriptor_class_validates_every_field`, `test_a_copy_pasted_property_validator_drifts`, `source: https://docs.python.org/3/howto/descriptor.html`, `source: https://peps.python.org/pep-0487/` |
| 148 | 27 | A property with no setter refuses assignment; a computed property is recomputed after each load; a load over the limit is refused | `test_a_property_without_a_setter_refuses_assignment`, `test_payload_is_recomputed_after_each_load`, `test_load_refuses_a_consignment_over_the_max_payload`, `source: https://docs.python.org/3/builtins/functions.html` |
| 149 | 27 | A data descriptor takes precedence over the instance dictionary, an instance-dictionary entry over `cached_property`; class access to `Positive` raises | `test_a_data_descriptor_takes_precedence_over_the_instance_dict`, `test_an_instance_dict_entry_takes_precedence_over_cached_property`, `test_class_access_to_a_positive_field_raises_attribute_error`, `source: https://docs.python.org/3/reference/datamodel.html`, `source: https://python-patterns.guide/gang-of-four/factory-method/` |
| 150 | 27 | On a dataclass, class access decides a descriptor field's default; a frozen class refuses a `setattr`-writing descriptor and assignment; `replace` validates; equal values hash equal; `slots=True` replaces the descriptor | `test_a_descriptor_field_has_no_default_when_class_access_raises`, `test_a_descriptor_that_returns_itself_on_class_access_becomes_the_default`, `test_a_frozen_dataclass_refuses_a_descriptor_that_writes_with_setattr`, `test_a_frozen_dataclass_refuses_assignment_to_a_descriptor_field`, `test_replace_validates_the_new_value`, `test_equal_dimensions_compare_and_hash_equal`, `test_mypy_accepts_a_descriptor_field_on_a_slotted_dataclass`, `source: https://docs.python.org/3/library/dataclasses.html` |
| 151 | 27 | `cached_property` computes on first read and stores in `__dict__`, needs that `__dict__`, can't be cleared on a frozen class, is recomputed by `replace`, goes stale over mutable state and can run its getter twice under threads | `test_chargeable_weight_is_computed_on_first_access_and_stored`, `test_chargeable_weight_is_the_larger_of_actual_and_volumetric_weight`, `test_cached_property_needs_an_instance_dict`, `test_a_frozen_dataclass_cannot_clear_a_cached_property`, `test_replace_recomputes_the_chargeable_weight`, `test_a_cached_property_over_mutable_state_goes_stale`, `test_a_cached_property_getter_can_run_twice_under_threads`, `source: https://docs.python.org/3/library/functools.html`, `source: https://docs.python.org/3/whatsnew/3.12.html` |
| 152 | 27 | mypy types a descriptor field by `__set__`'s value, reads it as defaulted, and accepts `cached_property` on a slotted dataclass | `test_mypy_types_a_positive_field_by_its_set_value`, `test_mypy_reads_a_descriptor_field_as_a_default`, `test_mypy_accepts_cached_property_on_a_slotted_dataclass` |
| 153 | 28 | A raising and a defaulting fallback give registered commodities the same codes; the raising one names an unregistered kind and the defaulting one answers silently | `test_every_fallback_form_gives_registered_commodities_their_codes`, `test_a_raising_fallback_names_an_unregistered_kind`, `test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently` |
| 154 | 28 | The most specific registration wins, an unregistered subclass takes its base's code, `dispatch` and the read-only `registry` show the choice, a union registers each member and `register(cls, fn)` registers a function | `test_the_most_specific_registration_wins`, `test_an_unregistered_subclass_gets_its_base_class_code`, `test_dispatch_and_registry_show_the_chosen_implementation`, `test_the_registry_is_read_only`, `test_a_union_annotation_registers_each_member`, `test_register_with_a_class_and_a_function_registers_the_function`, `source: https://docs.python.org/3/library/functools.html` |
| 155 | 28 | A forward reference fails at registration and mypy accepts it; a generic alias is refused | `test_mypy_accepts_a_forward_reference_that_fails_at_registration`, `test_a_generic_alias_is_refused_at_registration` |
| 156 | 28 | Another module's registration exists only once that module is imported | `test_another_module_extends_the_set_when_it_is_imported`, `source: https://peps.python.org/pep-0443/` |
| 157 | 28 | `singledispatchmethod` dispatches on the container kind, the argument after `self` | `test_surcharge_dispatches_on_the_container_kind`, `test_singledispatchmethod_dispatches_on_the_first_argument_after_self` |
| 158 | 28 | mypy checks calls and registrations against the fallback, refuses kinds outside a union fallback, accepts a mismatched `register(cls, fn)` and doesn't check a `singledispatchmethod`'s arguments | `test_mypy_checks_calls_and_registrations_against_the_fallback`, `test_mypy_refuses_a_kind_outside_a_union_fallback`, `test_mypy_accepts_a_registered_class_that_differs_from_the_parameter`, `test_mypy_does_not_check_the_arguments_of_a_singledispatchmethod` |
| 159 | 27-28 | The "Build, run, observe" experiments behave as quoted | `run: P5` |

Legacy rows at P2:
- Row 9 gets `test_every_fallback_form_gives_registered_commodities_their_codes` and `test_a_union_annotation_registers_each_member` ("verified (r13)").
- Row 10 gets `test_singledispatchmethod_dispatches_on_the_first_argument_after_self` ("verified (r13)").

## Corrections after the build
- Step P5: ch27 2,371 words, ch28 2,328 words. Before quoting, the orchestrator made two assertions deterministic so failure lines don't depend on set ordering: `test_one_descriptor_class_validates_every_field` compares a list of type names, and `test_dispatch_and_registry_show_the_chosen_implementation` compares sorted registry names. Each prose agent re-ran its affected experiment twice and confirmed identical output apart from the duration. Ch27 experiment (b) fails 9 tests (34 passed); experiment (a) fails 7 with 15 fixture-setup errors. Ch28 experiment 1 (delete the `InstantCoffee` registration) gives 3 failed and 15 errors at fixture setup (`KeyError` in the defaulting fixture), not the plan's `'0901.21' == '2101.11'`; experiment 2 (`TYPE_CHECKING` import) fails only the fresh-interpreter test, with mypy clean. Fluent Python is cited by topic in both chapters (the plan's fallback).
- Step P3: both figures drawn and rendered; figures 00-26 byte-identical. Captions are the plan drafts (36 and 39 words with the prefix; the plan's 38 and 41 were miscounts). Figure 27 adds an arrow from `chargeable_kg` into the non-data descriptor box and a note "attribute lookup on an instance". Figure 28's registry reads `TShirt`, `InstantCoffee`, `Coffee`, `object`, `LithiumIonBattery` ("after the import"), so the amber chain runs InstantCoffee to Coffee to object; the orchestrator added the battery box so the `dangerous_goods` arrow ends at the registration it makes (backed by `test_another_module_extends_the_set_when_it_is_imported`). The mypy ghost box keeps its text as title `mypy` and a detail line.
- Step P1b: member `singledispatch-visitor` (package `singledispatch_visitor`, no `[tool.*]` table), 18 test functions, 33 cases, as planned. The "plain typed method with `match`" deletion row fails only test 18 (mypy now reports `[arg-type]`), not 12: the `case _` still dispatches correctly at run time. Removing the `InstantCoffee` registration shows as 15 fixture-setup errors (the defaulting fixture reads `registry[InstantCoffee]`) plus failures in tests 4, 6 and 11. The `src` forward-reference message names its function: `owner=<function _lithium_ion_battery at 0x...>`; test 17's snippet uses `_`, matching evidence I, and masks `0x[0-9a-f]+`. Test 9 holds `register(TShirt, fn)`'s result as `object` (mypy 2.4.1's stub otherwise gives `[comparison-overlap]` and `[unreachable]`). Test 10 uses the annotation form for `list[int]` (ruff PT012 forbids a `def` inside `pytest.raises`). `COMMODITY_CODES` lives in `test_tariff.py`. Tests 7-10 witness standard-library behaviour, with nothing in `src` to delete. Every other message matched evidence I and J.
- Step P2: rows 147-158 resolve to existing tests (their `source:` tokens resolve once the chapters link them); legacy rows 9 and 10 verified; the dated r13 note is in `_plans/spikes.md`.
- Step P1a: member `descriptors-properties` (package `descriptors_properties`), 29 test functions, 43 cases (the plan's 44 was a sum error; its per-file numbers give 43). The project is named after its package so the member needs no `[tool.uv.build-backend]` table (the prerequisites chapter says members carry no tool configuration); the orchestrator renamed it from `descriptors-and-properties`. `EXTENT_ROWS` lives in `test_fields.py` (runtime `from conftest import` fails under importlib mode). `cargo.py` carries one file-level `# ruff: noqa: RUF009` with a reason (a descriptor default in a dataclass). Test 24: `Container.load` reads `payload_kg` itself, so the stale witness adds cargo with `consignments.append` after the first read and reads 100 against 350 live; prose says "cargo added after the first read". Test 25 adds a third read after the join so a plain `property` fails it. Experiment (a) (`setattr` in `__set__`) fails 7 tests and errors 15 in fixture setup, all `FrozenInstanceError: cannot assign to field '_length_cm'`; experiment (b) (`slots=True` on `Dimensions`) fails 9, including tests 5, 6 and 17, and test 4 reads `TypeError: vars() argument must have __dict__ attribute`; no `Consignment` test fails. Every static test has a mutation of its credited code that fails it. All predicted messages and values matched.

(None yet. The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.)

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs, and once with the test files in reverse order (`tests/test_static.py` first), with the same pass count.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch"` over both members' `tests` prints nothing.
   - `grep -rn "print("` over both members prints nothing.
   - `grep -rnE "\bAny\b|cast\(|slots=True|__slots__|lru_cache|functools\.cache|__getattr__|__getattribute__|__init_subclass__|threading|TrackingHistory"` over `examples/27-*/src` prints nothing.
   - `grep -rnE "\bAny\b|cast\(|TYPE_CHECKING|isinstance|HandlingEvent|DocumentKind|_clear_cache|\bmatch\b"` over `examples/28-*/src` prints nothing.
   - `grep -rn "dangerous_goods" examples/28-*/tests` hits only inside isolated-run code strings and mypy snippet strings.
3. Every test name cited in rows 147-158 and rows 9-10 is defined exactly once across `examples/*/tests`.
4. Every mypy-API test asserts its exit status and an exact code set, uses the anchored `_codes` regex, and asserts no line number or optional note. `grep -c "_codes("` is at least 4 in each `test_static.py`. Every `# type: ignore[...]` and `# noqa` names a code. There are no unused ignores.
5. **Every static test can fail on a mutation of the thing its prose credits.** The P1a/P1b handback lists each static test with its credited thing and runs the named mutation in a scratch copy, quoting the failing line. Every exit-0 test also asserts the hazard at run time on the same snippet or `src` call. A test whose mutation doesn't fail it is rewritten, or its prose claim is narrowed, before P5.
6. Deletion tables (P1a, P1b): every row, deleted in a fresh scratch copy whose imports come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed", and executor-check rows are resolved or moved to Corrections.
7. Every "silently", "stale", "not stored", "only once imported" or "takes precedence" sentence names a test with a deletion-table row (or experiment) whose mutation makes it fail. Scope words ("every", "all", "only", "never", "both") name the test that covers the whole scope, or are cut.
8. ch27-28 are drafted, with one figure each, captions of 20-45 words including `Figure N.1:`, and at most 2,500 prose words each by `validate.py` (an error above; a warning below 1,900 is reported, not padded).
9. Spine and sidebar:
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `grep -c "^## When not to use it"` is 1 and `grep -c "^## How it works"` is 0 in each.
   - `## What you can do now` is the second-to-last H2, directly before `## For deeper coverage`, with as many bullets as the learning objectives.
   - Every backticked token in the close appears earlier in the chapter.
   - Each sidebar opens with a bold lead, holds a nested `>` prompt, has at most two non-quoted paragraphs, matches no `\bCheck(:| that| three| four| whether)`, is at most 120 words, and names only identifiers present in the chapter, its `src` or the standard library.
   - `validate.py` passes the `pattern` spine.
10. Thesis:
    - ch27 says the design survives (`surviv` at least 1) and disambiguates Proxy's lazy-initialisation sense (`disambiguat` or "no surrogate" at least 1), without calling `cached_property` a proxy.
    - ch28 says Visitor dissolves (`dissolv` at least 1) and names what remains: the fallback, where registrations live, who imports them.
11. Non-overlap and pointers:
    - ch27 points to "Decorator the pattern vs @decorator the syntax, and Proxy", "The three-way split: dissolve, survive, disambiguate", "Dataclasses and value semantics", "Decorators done right" and "Dynamic attributes: __getattr__ and Proxy as a feature" by title.
      - `grep -nE "__init_subclass__|metaclass|__getattribute__"` over `_docs/27-*.md` prints nothing.
      - `__getattr__` appears only in the lookup-chain quotation and the pointer.
      - No B019 test or `weakref` liveness claim is repeated.
    - ch28 points to "Visitor, Memento, and Interpreter", "Singleton: module, Borg, and metaclass" and "Shortcut patterns: dict dispatch, function tables, and EAFP" by title, and describes nothing of the last.
      - It repeats no ch25 test (no `HandlingEvent`, `describe` or `Delivered` in `_docs/28-*.md` beyond the pointer sentence).
      - It quotes neither PEP 443's single-dispatch definition nor the functools first-argument sentence, which ch25 owns.
    - Neither chapter builds a dispatch table or describes any other stub.
12. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, the cards, the specs and the SVGs, with `--stats` reviewed against the house-voice rubric (rules 94-96: intent before mechanism, a minimal example first for a subtle mechanism, no re-narrated code, close on the objective payoff).
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|memoiz)"` over prose (quotations and code excluded) prints nothing. `initialisation` is the reader form.
    - No paragraph after an excerpt re-narrates its identifiers.
13. No em-dash or en-dash in any file touched in r13, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. A quoted dash is written "[en dash]" in plans and is never quoted in chapters.
14. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Smalltalk|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/27-*.md`, `_docs/28-*.md`, the new READMEs and the cards prints nothing.
15. Idiomatic scan: 0 ban-tier in both members.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`. Object addresses (the ForwardRef `owner=` text) are masked by a stated `sed` filter.
17. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Each experiment is performed in a fresh scratch copy, changes one thing, and is deleted afterwards. The chapter states the exact filter command, and the quoted block is its complete output, followed by `uv run mypy --strict src tests`.
19. Attribution:
    - ch27 credits the descriptor guide by title, PEPs 252 and 487 by author, and Rhodes by name, and quotes the functools, data-model, dataclasses, builtins and What's New 3.12 sentences exactly.
    - ch28 credits GoF (Visitor) in plain paraphrase and PEP 443 by author, quotes the functools sentences exactly, and claims no Rhodes page.
    - GoF claims appear only if verified. Every book cited is already in `bibliography.html`.
20. Claims:
    - Every factual sentence in ch27-28 maps to a named test, `run: P5` or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0, with rows 147-159 resolved and each `source:` URL present in its chapter.
    - No `run: N*` token appears in rows 147-159.
    - Any prose version mention (3.11, 3.12) is preceded by "since", "before", "until" or "new in", so `check_stale_versions` passes. No quotation containing "Python 3.12" is used.
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 29 entries, and `diagrams/0*-*`, `diagrams/1*-*` and `diagrams/2[0-6]-*` are unchanged.
22. Reconciliation rows 147-159 are `verified` or `adjusted` with evidence. Rows 9 and 10 are `verified (r13)`.
23. Deterministic:
    - No test depends on wall time, the environment, memory addresses, test order or iteration order it didn't create.
    - The thread test uses a `Barrier` and asserts an exact count.
    - No test process imports `dangerous_goods` or registers on a `src` dispatcher.
    - `filterwarnings = ["error"]` is still in the root config.
24. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.
25. Every self-contained mypy snippet that stands for code is named in the prose as a reduced model: ch27 test 28; ch28 tests 15, 16 and 17.
26. Test counts in prose and handbacks come from the pytest summary line of a fresh run.
27. Every comparison form said to share a table is a conftest fixture param (`field_form`, `fallback_form`), and each chapter shows at most one comparison excerpt.
28. Every figure label that names code (`Positive`, `__set_name__`, `__get__`, `__set__`, `Consignment`, `Dimensions`, `Container`, `kilograms`, `length_cm`, `width_cm`, `height_cm`, `tare_kg`, `max_payload_kg`, `chargeable_kg`, `cached_property`, `property`, `tariff_code`, `Coffee`, `InstantCoffee`, `TShirt`, `LithiumIonBattery`, `TariffCodeError`, `dangerous_goods`, `dispatch`, `SurchargeSchedule`, `surcharge`, `DryContainer`, `ReeferContainer`, `TankContainer`) exists in that chapter's `src` or the standard library, checked by grep at P3.
29. Repo-relative paths only in this plan and every r13 file: `grep -rnE "/home/|/Users/"` over the files touched in r13 prints nothing.

## Risks

- **Predicted messages and counts.** Every iteration since r05 mispredicted something. Expect differences in these places:
  - which tests ch27 experiment (a) fails, and whether any are collection errors;
  - the `vars()` message in ch27 (b);
  - whether ch28 test 4 fails with `KeyError` or an assertion in experiment (a);
  - whether test 7 or 13 needs a `# type: ignore`.

  Tests match codes and stable substrings only.
- **A static test that no mutation can fail** (r12 correction). Criterion 5 makes each credited mutation a run, not a claim. The likely weak spots are tests 27 and 28 in ch27 and test 14 in ch28; their runtime halves and the absence check are what make them bite.
- **mypy behaviour can move.** mypy reads a descriptor field as defaulted (evidence E), the `singledispatchmethod` `Any` signature and the unchecked `register(cls, fn)` (J) all come from typeshed or plugin behaviour. Prose says "mypy 2.4.1" for each, and only those sentences change if a release fixes them.
- **The thread test.** It depends on `cached_property` holding no lock (removed in 3.12). A future lock would deadlock the barrier until its 10-second guard expires, then fail with `BrokenBarrierError`. That's a clear signal, not a hang.
- **Defects kept out of prose** (evidence D, I). If the owner wants either in a chapter, it goes through `lgtm-issue-reporting` first, and the chapter states the technique, never the defect.
- **Ruff on tests.**
  - The forward-reference test and the snippets pass every root rule (evidence I).
  - E731 forbids assigned lambdas, so the defaulting fallback and test-local implementations are `def`s.
  - N818 is satisfied by `ContainerError`, `TariffCodeError` and `SurchargeError`.
- **mypy narrowing in tests** (r11 correction). After `assert "chargeable_kg" not in vars(c)`, mypy may flag later lines `[unreachable]`. Read values through small helpers. Class access typed `Never` also makes following lines unreachable, so test 12 reads it inside `pytest.raises` and nothing follows in that block.
- **Exhaustiveness on bool tuples** (evidence K). A `match` on `(roasted, decaffeinated)` is `[return]` under mypy 2.4.1, so `src` uses conditional expressions. This is noted for the executor, and the prose doesn't mention it.
- **Word budgets.** Both chapters run close to 2,500.
  - ch27 shrinks first: the Rhodes clause, then the thread paragraph to one sentence, then the `return self` default sentence.
  - ch28 shrinks first: the `dispatch`/`registry` sentences, then the generic-alias sentence.
  - Their tests stay.
- **Stub pointers.** It's tempting to write "metaclasses run `__set_name__` too" or "`__getattr__` is the last resort". Criterion 11 limits ch27 to the quotation and a title pointer.
- **New supporting names.** If the owner declines `Positive`, `InstantCoffee`, `dangerous_goods`, `SurchargeSchedule` or the container kinds, P1a or P1b waits for the replacements. Nothing else moves.
- **Liquid.** The f-strings in excerpts contain single braces only. Any `{{` needs `{% raw %}`.
- **`uv.lock` race.** P1a and P1b are sequenced.
