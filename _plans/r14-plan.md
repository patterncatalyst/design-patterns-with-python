---
title: "r14 plan: chapters 29-30 (Metaclasses, __init_subclass__, and registries; Dynamic attributes: __getattr__ and Proxy as a feature)"
order: 14
output: false
render_with_liquid: false
---

# r14: chapters 29-30, Metaclasses, __init_subclass__, and registries; Dynamic attributes: __getattr__ and Proxy as a feature

Opus-planned 2026-11-06. Branch `release/r14`, cut from main at a03e3a1 (the r13 merge). This file is the source of truth for r14 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4 and uv 0.13.7 match PyPI and python.org (checked 2026-11-06: uv 0.13.7 of 2026-11-03, pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, ruff 0.17.4 of 2026-11-05, mypy 2.4.1 of 2026-10-28; python.org lists 3.15.0 to 3.15.2). Q0 re-checks before any edit. `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch29: slug `29-metaclasses-init-subclass-and-registries`, title "Metaclasses, __init_subclass__, and registries", part 9 (`idiomatic-python`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.
- ch30: slug `30-dynamic-attributes-and-proxy`, title "Dynamic attributes: __getattr__ and Proxy as a feature", part 9 (`idiomatic-python`), `kind = "pattern"`, `has_example = true`, `status = "stub"`.

Work items: PDP-129a-c (ch29 example, figure, prose) and PDP-130a-c (ch30), `todo` in `_plans/iteration-plan.md`.

## User decisions (owner confirmed 2026-11-06: all ten as recommended)

Standing, not a decision: step ids are `Q*`. `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md`, and `grep -nE '^\| Q[0-9]' _plans/*.md` matched nothing before this file. The letters in use are A, G to N, P and S.

1. **Buckets: ch29 dissolves; ch30 disambiguates Proxy.**
   - **ch29 dissolves.** The ch3 table row reads "Metaclass registry | Dissolves | `__init_subclass__`", and domain row 29 says "dissolve". The design that remains:
     - which classes register;
     - what is refused at definition;
     - where registrations come from (imports);
     - how tests stay out of each other's way.
   - The metaclass is the measured comparison, plus one honest case (decision 6).
   - **ch30 disambiguates Proxy.** The ch3 row lists Proxy as "A surrogate object vs attribute interception with `__getattr__`, `property` and `cached_property`".
     - ch20 owns the surrogate and the forwarding proxy.
     - ch27 owns `property` and `cached_property`.
     - ch30 owns `__getattr__` used by the object itself for lazy loading: a virtual proxy's intent with no surrogate.

   **Recommend: yes.** Alternative: ch30 "survives". That contradicts the ch3 row and domain row 30.

2. **ch29's domain (domain row 29, Carrier area).**
   - `carriers.py` holds:
     - `ConsignmentId`;
     - `DuplicateCarrierError(Exception)` (row name);
     - `CarrierRegistrationError(TypeError)` (new);
     - `UnknownCarrierError(LookupError)` (reused from ch16, same message shape `unknown carrier 'NOPE'`);
     - the private dict `_CARRIERS`;
     - `CarrierBase(ABC)` with `registry: ClassVar[Mapping[str, type[CarrierBase]]] = MappingProxyType(_CARRIERS)`, `code: ClassVar[str]`, `__init_subclass__` and an abstract `book(consignment_id, /) -> str`;
     - `gateway_for(code) -> CarrierBase` (new).
   - `fastline.py` holds `FastlineGateway(CarrierBase, code="FASTLINE")`, booking `FL-CN-1`.
   - `airco.py` holds `AircoGateway(CarrierBase, code="AIRCO")`, booking `AC-CN-1`.
   - `__init__.py` imports no submodule, so registration depends on imports (decision 5).
   - No new carrier code: `FASTLINE` and `AIRCO` only. Test-local classes use codes `"FASTLINE"` (the duplicate) and `"HALF"`, and the isolated runs use names that aren't carrier codes.

   **Recommend: yes.** Alternatives:
   - (b) A shared abstract intermediate in `src`. That needs a new name, and the intermediate is witnessed test-locally anyway.
   - (c) `__init__.py` imports both carriers. That hides the import-order failure the chapter teaches.

3. **Registration rule: concrete needs a code, abstract can't take one, through `inspect.isabstract`.**
   - In order, `__init_subclass__` checks:
     - abstract with a code: `CarrierRegistrationError`;
     - abstract without a code: skip;
     - concrete without a code: `CarrierRegistrationError`;
     - duplicate code: `DuplicateCarrierError`, naming the class that holds the code.
     
     Only then does it set `cls.code` and insert.
   - This corrects spike 013 and domain row 29, which say `__init_subclass__` can't see abstractness (evidence D).
   - It also closes the hole in `code: str | None = None` where a concrete carrier that forgets `code=` would silently go unregistered.

   **Recommend: yes.** Alternatives:
   - (b) `code` required (ch3's form). Then abstract intermediates are impossible.
   - (c) Optional with no concreteness check. Then a forgotten code is silent.

4. **Closed `__init_subclass__` signature: `(cls, *, code: str | None = None) -> None`, calling `super().__init_subclass__()` with no `**kwargs`.**
   - mypy reports a misspelt keyword as `[call-arg]` with `did you mean "code"?`, and the runtime names it (evidence A, B).
   - With `**kwargs: object` forwarded (the data model's cooperative form), mypy is silent on `cod="X"`. The runtime then says `Odd.__init_subclass__() takes no keyword arguments`, which names neither the keyword nor the base.
   - The chapter quotes the data model's "For compatibility with other classes using __init_subclass__ ..." sentence and says why `CarrierBase` closes it: it's the root of a hierarchy with no cooperating mixins. Experiment (a) is the forwarded form.

   **Recommend: closed.** Alternative: forward `**kwargs` as the docs show, and lose the static typo report.

5. **Registry isolation in tests.**
   - The public registry is a read-only `MappingProxyType` view (test 6).
   - `tests/conftest.py` imports `fastline` and `airco` once, so the in-process registry is exactly `["AIRCO", "FASTLINE"]` for every test.
   - **No test registers a carrier in the test process.** Every refusal raises before insertion, and each refusal test asserts the registry is unchanged.
   - Successful new registrations run in a fresh `python -I` interpreter through `_run_isolated`, copied from `examples/18-singleton-module-borg-metaclass/tests/test_module.py`. These are:
     - a concrete carrier under an abstract intermediate;
     - a carrier module that registers only when imported.
   - Rejected:
     - snapshot-and-restore of `_CARRIERS` (touches a private name and hides the global state the chapter teaches);
     - `monkeypatch` (ch3's test uses it; this member doesn't);
     - a registry per root class (design creep).

   **Recommend: yes.** Alternative: an autouse fixture that restores `_CARRIERS`. It's shorter, and it couples tests to a private name.

6. **The metaclass half: a conftest comparison form, plus one honest case.**
   - `tests/conftest.py` defines:
     - `_CarrierMeta(ABCMeta)`, whose `__new__` applies the same four rules and raises the same `src` exceptions;
     - `_MetaCarrierBase(metaclass=_CarrierMeta)`;
     - `_MetaFastlineGateway` and `_MetaAircoGateway`.
   - `registry_form` `init_subclass|metaclass` runs the shared table.
   - **Honest case: class-level operators.** `_CarrierMeta` also defines `__contains__`, `__iter__` and `__len__`, so `"AIRCO" in _MetaCarrierBase`, `list(_MetaCarrierBase)` and `len(_MetaCarrierBase)` work. On `CarrierBase` the same `in` raises `TypeError: argument of type 'ABCMeta' is not a container or iterable` (evidence H).
     - Only a metaclass can provide these, because special methods are looked up on the type, and a class's type is its metaclass.
     - `EnumType` is the standard library's case.
     - The verdict: worth it when the class *is* the collection (an enum). For a carrier registry, `CarrierBase.registry` reads as well, so `src` has no metaclass.
   - One sentence on `__prepare__`: PEP 520 says ordered namespaces were "by far the most common use case", and class namespaces keep definition order since 3.6. mypy and ruff already catch a redefinition (evidence H).
   - One sentence on `__call__`: `type.__call__` runs `__new__` then `__init__`, and mypy 2.4.1 types the call by `__init__` even when a metaclass `__call__` declares `-> int` (test 25). It points to "Singleton: module, Borg, and metaclass" by title, which deferred these mechanics here.
   - The name `CarrierMeta` from domain row 29 becomes the test-only `_CarrierMeta`, matching the underscore convention for comparison fixtures.

   **Recommend: yes.** Alternatives:
   - (b) `__prepare__` as the honest case. Its only live use in this domain (refusing redefinition) is already caught by mypy `[no-redef]` and ruff F811.
   - (c) `__call__` as the honest case. That's the Singleton chapter's ground, and mypy ignores its return type.
   - (d) Abstractness validation. Refuted by evidence D.

7. **ch30's design: `__getattr__` as a ghost over declared fields (domain row 30).**
   - `tracking.py` holds `ConsignmentId`, `HandlingKind`, `ConsignmentStatus` (the ch25 values), `HandlingEvent` (frozen slotted: `consignment_id`, `kind`, `port`) and `TrackingHistory`.
   - `TrackingHistory` declares `events: tuple[HandlingEvent, ...]`, `status: ConsignmentStatus | None` and `last_port: str | None` as class annotations with no values.
   - `__init__(consignment_id, load)` stores two plain attributes. `load` is `Callable[[ConsignmentId], Iterable[HandlingEvent]]`, a parameter with no new alias.
   - `__getattr__(name) -> object`:
     - names outside `_LAZY = frozenset({"events", "status", "last_port"})` raise `AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")`;
     - otherwise it loads once and writes all three fields with `vars(self).update(...)` (bypassing `__setattr__`), then returns `vars(self)[name]`;
     - an empty load gives `status` and `last_port` `None`.
   - `__setattr__` refuses the three lazy names (`'status' is loaded, not assigned`) and passes other names to `object.__setattr__`.
   - `__dir__` returns `sorted({*object.__dir__(self), *_LAZY})`.
   - `__iter__` is explicit and iterates `self.events`.
   - No `TYPE_CHECKING` gate and no `__getattribute__` in `src`.
   - Why `__getattr__` and not `cached_property`:
     - one load fills several fields;
     - after it, the fields are plain instance-dictionary entries and `__getattr__` never runs again (test 8);
     - ch27 owns `cached_property` as lazy initialisation;
     - ch3's `LazyTrackingHistory` already shows it on one field.

   **Recommend: yes.** Alternatives:
   - (b) `src` uses `cached_property` with three properties, and `__getattr__` is the comparison. That makes ch30 a repeat of ch27.
   - (c) Gate `__getattr__` and `__setattr__` under `if not TYPE_CHECKING:` so mypy reports typos (evidence Q shows it works). It makes mypy check a different class from the one that runs, the divergence ch28 warns about. The chapter can name it in one clause. Owner's call.

8. **One comparison fixture and one comparison excerpt per chapter.**
   - **ch29: `registry_form` `init_subclass|metaclass`**, on `BOOKING_ROWS` (2) and `REFUSAL_ROWS` (4). The excerpt is `_CarrierMeta.__new__`.
   - **ch30: `history_form` `getattr|cached_property`**, on `HISTORY_ROWS` (4) plus three shared behaviour tests. `cached_property` is the conftest `_CachedTrackingHistory`: `@cached_property def _events` and three read-only `@property`s. The excerpt is its `_events` and `status` pair.
   - Forms that fail on purpose get their own tests, not table rows:
     - the forgotten manual registration;
     - the self-healing `__getattr__` that recurses;
     - the `.get(name)` form that returns `None` for a typo.

   **Recommend: yes.** Alternative: a manual dict as ch29's comparison form. That's ch16's registry, and the domain row names the metaclass.

9. **Module-level `__getattr__` in ch30 (about 190 words).**
   - `tracking.py` gets a module `__getattr__` that warns `DeprecationWarning("LazyTrackingHistory is deprecated; use TrackingHistory", stacklevel=2)` and returns `TrackingHistory` for that one name, and raises `AttributeError(f"module {__name__!r} has no attribute {name!r}")` otherwise. A module `__dir__` adds the name.
   - The prose says PEP 562's lazy-submodule use is what `lazy import` (PEP 810) now covers on the importing side. It points to "Singleton: module, Borg, and metaclass" by title and describes nothing more of it. Deprecation is the use that remains.
   - `LazyTrackingHistory` is ch3's existing name, not a new one.

   **Recommend: yes.** Alternative: out, which leaves the user's PEP 562 and PEP 810 questions to prose only.

10. **Scope cuts.**
    - Recorded here and in the Q2 spikes note, not in either chapter:
      - a refused class lingering in `__subclasses__()` until garbage collection (evidence F);
      - the `__annotate_func__` key a metaclass sees since 3.14 (evidence I);
      - a metaclass `__getitem__` that mypy reads as a type application (evidence H);
      - `__instancecheck__` and `__subclasscheck__`;
      - `__delattr__`;
      - pickling the `src` history (it needs a picklable loader, and test-module functions under importlib mode are an executor risk);
      - `typing.Protocol`'s `_ProtocolMeta` beyond the one conflict row.
    - In ch29: class keywords, refusals, `isabstract`, the `__set_name__` / `__init_subclass__` / decorator order, import-dependence, the metaclass form and its costs, and class-level operators.
    - In ch30: the two hooks, the recursion trap under `copy`, `__setattr__`, `__dir__` and suggestions, special-method lookup, `hasattr`, mypy, and module `__getattr__`.

    **Recommend: yes.**

Also proposed for the owner (no decision needed unless declined):
- **No new books.**
  - GoF, Fowler's *Patterns of Enterprise Application Architecture* (2002) and *Fluent Python* 2nd ed. are in `bibliography.html`.
  - O'Reilly confirms *Fluent Python, 2nd Edition* (2022), but its chapter titles weren't visible.
  - Book items stay bracketed: [GoF: Proxy's virtual proxy creates an expensive object on demand]; [Fowler, PoEAA: Registry, "a well-known object" others use to find services]; [Fowler, PoEAA: Lazy Load, its ghost variant, an object that loads its own fields]; [Ramalho, *Fluent Python* 2nd ed., on class metaprogramming and on dynamic attributes].
- **Rhodes, python-patterns.guide** (fetched 2026-11-06). There's no metaclass or Proxy page (`python/metaclasses/` and `gang-of-four/proxy/` return 404).
  - ch29 may quote "The Global Object Pattern" (https://python-patterns.guide/python/module-globals/) on mutable global registries.
  - ch30 may quote "The Decorator Pattern" (https://python-patterns.guide/gang-of-four/decorator-pattern/), section "Implementing: Dynamic wrapper". ch20 cites the same page for `iter()`; ch30 uses a different sentence.
- At Q2, a dated r14 note in `_plans/spikes.md` corrects PDP-013 (evidence D and G) and records evidence F, H and I. The spike code in `spikes/feature-spikes` stays as history. Its test `test_only_the_metaclass_can_see_abstractness_when_a_code_is_given` passes, but its comment's premise is wrong, and the note says so.

## Planning evidence

The planning run was read-only, so no scratch directory was created. Every probe ran as inline code with the session scratchpad (`<scratchpad>`) as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `<repo>/.venv/bin/python -I -c CODE`, version `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`. The 3.14 cross-checks used the uv-managed `python3.14` (3.14.10).
- mypy: `<repo>/.venv/bin/python -I -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET`, version `mypy 2.4.1 (compiled: yes)`.
- ruff: `<repo>/.venv/bin/ruff check --isolated --no-cache --line-length 100 --select E,F,W,I,UP,B,SIM,RUF,PT,N --target-version py315 --stdin-filename NAME -`, version ruff 0.17.4. One probe used the root config through a repo-relative `--stdin-filename`.

Snippets are reduced models. Line numbers will differ and are never asserted. Object addresses are shown as `0x...`. Every output is a prediction for the member until the build quotes it as observed.

**A. `__init_subclass__` at run time.** With `**kwargs: object` forwarded and `code: str | None = None`:
```
['FASTLINE'] FASTLINE
DuplicateCarrierError: carrier code 'FASTLINE' is already registered to FastlineGateway
True False
TypeError: Odd.__init_subclass__() takes no keyword arguments
['FASTLINE']
```
- The duplicate keeps the original (`registry["FASTLINE"] is FastlineGateway`), and the refused name isn't bound.
- An unknown keyword (`region="EU"`) reaches `object.__init_subclass__`, whose message names the subclass, not the keyword.

Closed signature, without `**kwargs`:
```
TypeError: CarrierBase.__init_subclass__() got an unexpected keyword argument 'cod'. Did you mean 'code'?
TypeError: CarrierBase.__init_subclass__() missing 1 required keyword-only argument: 'code'
TypeError: A.__init_subclass__() takes no keyword arguments
```
The second line is the required-keyword form (ch3's `code: str`). The third is `cod="X"` against the forwarding form.

**B. mypy on class keywords.** Forwarding form, exit 1:
```
<string>:14: error: Argument "code" to "__init_subclass__" of "CarrierBase" has incompatible type "int"; expected "str | None"  [arg-type]
<string>:22: note: Revealed type is "type[__main__.CarrierBase]"
<string>:24: note: Revealed type is "__main__.CarrierBase"
<string>:25: note: Revealed type is "str"
```
- `region="EU"` (line 16) and `cod="X"` (line 18) get no error with `**kwargs: object`.
- `CarrierBase.registry["D"]()` is accepted although `CarrierBase` is abstract.

Required keyword: `<string>:9: error: Missing named argument "code" for "__init_subclass__" of "CarrierBase"  [call-arg]`.

Closed signature: `<string>:12: error: Unexpected keyword argument "cod" for "__init_subclass__" of "CarrierBase"; did you mean "code"?  [call-arg]`.

**C. Order of class-creation hooks.** A descriptor with `__set_name__` on a subclass of a base with `__init_subclass__`:
```
[('set_name', 'Sub', 'f'), ('init_subclass', 'Sub', ['f'])]
```
`__set_name__` runs first. The data model's "Creating the class object" lists the steps in that order, then class decorators (Sources).

**D. `inspect.isabstract` inside `__init_subclass__`.** An ABC root, an intermediate `Mid` with no `book`, and a concrete `Conc`. The hook records `(isabstract(cls), getattr(cls, "__abstractmethods__", "unset"))`:
```
{'Mid': (True, 'unset'), 'Conc': (False, 'unset')}
True frozenset({'book'})
```
- `__abstractmethods__` isn't set yet when the hook runs, because `ABCMeta.__new__` calls `super().__new__` (which runs the hook) before `_abc_init(cls)`. Spike 013's observation is right about that.
- `inspect.isabstract` is right anyway. Its 3.15.2 source has a branch commented "It looks like ABCMeta.__new__ has not finished running yet; we're probably in __init_subclass__. We'll look for abstractmethods manually." (`Lib/inspect.py`, line 474 on the `3.15` branch).
- Same result on 3.14.10, so spike 013's "`__init_subclass__` cannot see abstractness" was wrong when it was recorded.
- With the four rules of decision 3: `Forgot is concrete and needs a code` and `Half is abstract and cannot take code 'HALF'` (evidence E).

**E. The ch29 model** (decisions 2-4: `carriers.py` with `FastlineGateway` and `AircoGateway` inline, `types.new_class` for the refusals):
```
['AIRCO', 'FASTLINE'] AC-CN-1
UnknownCarrierError: no carrier registered for 'NOPE'
TypeError: 'mappingproxy' object does not support item assignment
DuplicateCarrierError: carrier code 'FASTLINE' is already registered to FastlineGateway
CarrierRegistrationError: Forgot is concrete and needs a code
CarrierRegistrationError: Half is abstract and cannot take code 'HALF'
['AIRCO', 'FASTLINE']
```
- Every refusal leaves the registry unchanged: refusals happen before insertion (decision 5).
- mypy exits 0, revealing `typing.Mapping[str, type[__main__.CarrierBase]]` and `__main__.CarrierBase` for `gateway_for("AIRCO")`.
- ruff flagged only two E501 message lines, which the member wraps.
- The member reuses ch16's message: `unknown carrier 'NOPE'`.
- A class statement inside `pytest.raises` passes ruff with the root rules (no PT012). The spike's own `test_registry.py` already does this.

**F. A refused class lingers in `__subclasses__()` (not used).**
```
['A', 'B']
['A']
```
After `B`'s `__init_subclass__` raises, `Base.__subclasses__()` still lists `B` until `gc.collect()`. A registry built from `__subclasses__()` would see it; the dict registry doesn't. Decision 10.

**G. A metaclass registry.** `CarrierMeta(ABCMeta)` with `__new__(mcs, name, bases, namespace, /, *, code=None, **kwargs) -> CarrierMeta`, the registry typed `dict[str, type[MetaCarrierBase]]`. Exit 1:
```
<string>:9: error: "CarrierMeta" has no attribute "code"  [attr-defined]
<string>:10: error: Incompatible types in assignment (expression has type "CarrierMeta", target has type "type[MetaCarrierBase]")  [assignment]
<string>:23: error: Metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases  [metaclass]
<string>:23: note: "__main__.Other" (metaclass of "__main__.X") conflicts with "__main__.CarrierMeta" (metaclass of "__main__.MetaCarrierBase")
```
- `code=1` (line 16) and `cod="B"` (line 18) get no error: mypy never checks metaclass keywords.
- `-> Self` on the metaclass `__new__`: `<string>:5: error: Self type cannot be used in a metaclass  [misc]`.
- **The two ignores can be avoided.** Declaring `code: str` on the metaclass and typing the registry `dict[str, CarrierMeta]` exits 0 with no ignores, and `F.code` is revealed `str`. But `_META_CARRIERS["FASTLINE"]()` is revealed `Any`: the instance type is lost. The conftest form takes this shape, and test 24 measures it.
- Run-time keyword typo with a closed metaclass signature: `TypeError: CarrierMeta.__new__() got an unexpected keyword argument 'cod'. Did you mean 'code'?`. With `**kw` forwarded: `TypeError: C.__init_subclass__() takes no keyword arguments`.
- **Conflicts at run time.** All four cases give the same message:
  - a plain `type` metaclass on a `CarrierBase(ABC)` subclass;
  - on a `typing.Protocol` subclass;
  - on an `enum.Enum` subclass;
  - two unrelated metaclasses in one class's bases.

  ```
  TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
  ```
  A metaclass derived from `ABCMeta` works under `CarrierBase`: `type(OK).__mro__` is `(CarrierMeta2, ABCMeta, type, object)`.

**H. What only a metaclass can do.**
- **Class-level operators.** `CarrierMeta.__contains__`, `__iter__` and `__len__` give `True ['AIRCO'] 1` for `"AIRCO" in MetaBase`, `list(MetaBase)` and `len(MetaBase)`.
  - mypy types `list(Base)` as `list[str]` and `len(Base)` as `int`.
  - On a plain ABC, `"AIRCO" in Plain` is `[operator]` (`Unsupported right operand type for in ("type[Plain]")`) and at run time `TypeError: argument of type 'ABCMeta' is not a container or iterable`.
  - A metaclass `__getitem__` used as `Base["FASTLINE"]` is read by mypy as a type application: `"Base" expects no type arguments, but 1 given  [type-arg]` and `Name "FASTLINE" is not defined  [name-defined]`, though the run time returns the class. Not used (decision 10).
  - Enum: `EnumType 2 ['LOADED', 'DEPARTED'] True H.LOADED`. A reused member name gives `TypeError: 'LOADED' already defined as 'loaded'`.
- **`__prepare__`.** A namespace that refuses redefinition raises `DuplicateMemberError: 'book' is defined twice in the class body` at run time. mypy already reports `Name "book" already defined on line 14  [no-redef]`, and ruff F811 `Redefinition of unused `book` from line 2`. mypy also wants `__prepare__` to return `MutableMapping[str, object]` (`[override]`). Not used beyond one sentence (decision 6).
- **`__call__`.** A metaclass `__call__` declared `-> int`:
  ```
  <string>:7: note: Revealed type is "__main__.G"
  <string>:8: error: Missing positional argument "ref" in call to "G"  [call-arg]
  <string>:8: note: Revealed type is "__main__.G"
  ```
  mypy types `G("x")` by `__init__` and ignores the declared return. At run time the call returns `1`. The same holds with an `Any`-typed `__call__`.

**I. 3.15 interplay of `typing`, `abc` and metaclasses.**
- `type(typing.Protocol).__mro__` is `(_ProtocolMeta, ABCMeta, type, object)`. `typing.Generic`'s type is `type`, and `typing.NamedTuple` is a function.
- A `Protocol` plus `ABC` base works (`_ProtocolMeta`). A `Protocol` subclass with an unrelated metaclass conflicts.
- **Since 3.14, a metaclass sees no `__annotations__` in the namespace.** `namespace` holds `__annotate_func__`, on 3.14.10 and on 3.15.2 alike. `annotationlib.get_annotations(cls, format=Format.FORWARDREF)` after creation, or `format=Format.STRING` inside `__init_subclass__`, gives `{'code': 'str', 'rate': 'Later'}` (a forward reference stays a string). Nothing changed between 3.14 and 3.15. Not used (decision 10).

**J. When each hook runs (legacy row 11).**
```
fetched events
{'getattr': ['events'], 'getattribute': ['consignment_id', 'consignment_id']}
```
- `__getattr__` ran only for the missing `events`, never for the set `consignment_id`.
- `__getattribute__` ran on both reads.
- A counting subclass of the ch30 model read `status` three times and logged `[('ga', 'status'), ('gattr', 'status'), ('ga', 'status'), ('ga', 'status')]`: three `__getattribute__` calls and one `__getattr__`.

**K. The recursion trap (legacy row 12).** A `__getattr__` that reads `self._loader` for every missing name:
```
bare-new RecursionError: maximum recursion depth exceeded
copy RecursionError: maximum recursion depth exceeded
deepcopy RecursionError: maximum recursion depth exceeded
pickle PicklingError: Can't pickle <function <lambda> at 0x...>: it's not found as __main__.<lambda>
```
- The recursion limit is 1000.
- `copy` and `deepcopy` build a bare instance and look up `__setstate__`. That reaches `__getattr__`, which reads the missing `_loader`, which reaches `__getattr__` again.
- With a module-level loader, a self-healing form (writes any name) also recursed under `pickle.loads(pickle.dumps(...))`: `pickle RecursionError: maximum recursion depth exceeded`.
- The pickle docs warn of exactly this (Sources).

**L. Three fixes that hold.** Each was checked on a bare `__new__` instance, then `copy.copy`:
```
Fixed bare-new AttributeError: _loader
Fixed copy ok Fixed
Fixed2 bare-new AttributeError: events
Fixed2 copy ok Fixed2
Fixed3 bare-new AttributeError: 'Fixed3' object has no attribute '_loader'
Fixed3 copy ok Fixed3
```
- `Fixed` refuses underscore names. `Fixed2` reads through `vars(self).get`. `Fixed3` uses `object.__getattribute__`.
- The ch30 model's allow-list is a fourth: any name outside the set raises before anything is read.
- Copying a loaded history doesn't trip the `__setattr__` guard: reconstruction updates `__dict__` directly. Output: `LOADED ('BOOKED', 'LOADED') ['CN-1']`.
- A guarded form pickled with a module-level loader: unloaded `['_load', 'consignment_id']`, loaded `['_load', 'consignment_id', 'events']`.
- Legacy row 12's "only when it uses `object.__getattribute__`/`__dict__`" is therefore adjusted.

**M. A typo through `.get(name)`.** `typo: None | status: in transit`. Domain row 30's failing test.

**N. Special-method lookup.**
```
['e1', 'e2']
TypeError: 'Fwd' object is not iterable
TypeError: object of type 'Fwd' has no len()
seen during iter/len: []
```
Explicit `f.__iter__()` goes through `__getattr__`. `iter(f)` and `len(f)` reach neither `__getattribute__` nor `__getattr__`.

**O. Suggestions and `__dir__`.** Each line is `type name | e.name | e.obj is o | format_exception_only`:
```
A 'stauts' True | AttributeError: 'A' object has no attribute 'stauts'. Did you mean '.status' instead of '.stauts'?
NoDir 'stauts' True | AttributeError: stauts
PlainMsg 'stauts' True | AttributeError: no stauts
WithDir 'stauts' True | AttributeError: stauts. Did you mean '.status' instead of '.stauts'?
WithDirNoNameObj 'stauts' True | AttributeError: no stauts. Did you mean '.status' instead of '.stauts'?
```
- The interpreter sets `name` and `obj` on an `AttributeError` raised from `__getattr__`.
- The suggestion appears only when `dir()` lists the name, which is what `__dir__` provides.

**P. The ch30 model** (decision 7, before the empty-load case; `last_port` included):
```
before ['_load', 'consignment_id'] []
ConsignmentStatus.IN_TRANSIT SGSIN 3 ['CN-1']
after ['_load', 'consignment_id', 'events', 'last_port', 'status']
['BOOKED', 'LOADED', 'DEPARTED'] ['CN-1']
AttributeError: 'TrackingHistory' object has no attribute 'stauts'
AttributeError: 'TrackingHistory' object has no attribute 'stauts'. Did you mean '.status' instead of '.stauts'?
AttributeError: 'status' is loaded, not assigned
hasattr fetches: True ['CN-1', 'CN-2']
copy before load ok, loaded? False ['CN-1', 'CN-2']
deepcopy ok
in dir before load: True ['CN-1', 'CN-2']
TypeError: object of type 'TrackingHistory' has no len()
```
- One load for three fields. Iteration after the load loads nothing more.
- `hasattr` triggers a load.
- Copying an unloaded history doesn't load it.
- `dir()` lists the lazy fields without loading.
- The member adds the empty case (`status` and `last_port` are `None`). ruff, with the root rules, passed the model; `ruff format` only reflowed it.

**Q. mypy on the ch30 model.** `__getattr__ -> object`, declared fields and `__setattr__(name: str, value: object)`. Exit 1:
```
<string>:54: note: Revealed type is "__main__.ConsignmentStatus"
<string>:55: note: Revealed type is "object"
<string>:59: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
```
- Silent:
  - `print(h.stauts)`;
  - `h.status = ConsignmentStatus.BOOKED`, which the run time refuses;
  - `h.anything = 1`.
- With only `__getattr__ -> object` and no `__setattr__`: `h.stauts.upper()` is `"object" has no attribute "upper"  [attr-defined]`, and `h.anything = 1` is `"History" has no attribute "anything"  [attr-defined]`.
- With `__setattr__(name: str, value: int)`: `h.other = "x"` is `[assignment]` against `int`. mypy uses `__setattr__`'s value type for any name.
- With `__getattr__` under `if not TYPE_CHECKING:`: `"History" has no attribute "stauts"; maybe "status"?  [attr-defined]` (decision 7, alternative c).

**R. Module `__getattr__` and `lazy import`.**
- A module whose `__getattr__` warns for an old name, under `warnings.simplefilter("error")`:
  ```
  DeprecationWarning: OLD is deprecated; use NEW
  42
  AttributeError: module '__main__' has no attribute 'MISSING'
  from-import DeprecationWarning: OLD is deprecated; use NEW
  ```
  `from tracking import OLD` also goes through module `__getattr__`. The `'__main__'` comes from the probe's own `__name__`; the member names its module.
- `lazy import json` at module scope:
  ```
  False
  lazy_import
  True module
  ```
  The name is a `lazy_import` object in `globals()` until first use.
- PEP 810 doesn't mention PEP 562 or module `__getattr__`. It says `dir()` on a module is special-cased to avoid reification.
- **Executor check:** mypy on a regular module with `__getattr__(name: str) -> type[TrackingHistory]` should accept `from dynamic_attributes.tracking import Anything` (typed `type[TrackingHistory]`). This needs files, so it wasn't run. Test 26 asserts whatever mypy 2.4.1 prints, and the chapter says only that.

**Sources fetched 2026-11-06.** curl, tags stripped by paragraph. Prose agents re-fetch, the page text wins, and a quotation stops where the page's sentence stops. Curly apostrophes on the docs pages are kept as on the page.
- **Data model** (https://docs.python.org/3/reference/datamodel.html, banner 3.15.2):
  - "Whenever a class inherits from another class, __init_subclass__() is called on the parent class."
  - "The default implementation object.__init_subclass__ does nothing, but raises an error if it is called with any arguments."
  - "For compatibility with other classes using __init_subclass__, one should take out the needed keyword arguments and pass the others over to the base class, as in:" (stop at "base class").
  - The creation steps: "The type.__new__ method collects all of the attributes in the class namespace that define a __set_name__() method;" / "Those __set_name__ methods are called with the class being defined and the assigned name of that particular attribute;" / "The __init_subclass__() hook is called on the immediate parent of the new class in its method resolution order." / "After the class object is created, it is passed to the class decorators included in the class definition (if any) and the resulting object is bound in the local namespace as the defined class."
  - "The most derived metaclass is one which is a subtype of all of these candidate metaclasses. If none of the candidate metaclasses meets that criterion, then the class definition will fail with TypeError."
  - "The potential uses for metaclasses are boundless."
  - `__getattr__`: "Note that if the attribute is found through the normal mechanism, __getattr__() is not called." and "(This is an intentional asymmetry between __getattr__() and __setattr__().)". ch20 already quotes "Called when the default attribute access fails with an AttributeError" and the special-method "may still be bypassed" sentence; ch30 quotes neither.
  - `__getattribute__`: "In order to avoid infinite recursion in this method, its implementation should always call the base class method with the same name to access any attributes it needs, for example, object.__getattribute__(self, name)."
  - `__setattr__`: "If __setattr__() wants to assign to an instance attribute, it should call the base class method with the same name, for example, object.__setattr__(self, name, value)."
  - `__dir__`: "Called when dir() is called on the object."
  - Module access: "Defining module __getattr__ and setting module __class__ only affect lookups made using the attribute access syntax" (stop before the [en dash]).
- **Built-in functions, `dir`** (https://docs.python.org/3/library/functions.html): "This allows objects that implement a custom __getattr__() or __getattribute__() function to customize the way dir() reports their attributes." and "The resulting list is not necessarily complete and may be inaccurate when the object has a custom __getattr__()." The first uses American spelling; it's a quotation.
- **pickle** (https://docs.python.org/3/library/pickle.html): "At unpickling time, some methods like __getattr__(), __getattribute__(), or __setattr__() may be called upon the instance."
- **copy** (https://docs.python.org/3/library/copy.html): "Classes can use the same interfaces to control copying that they use to control pickling."
- **abc** (https://docs.python.org/3/library/abc.html): "Note that the type of ABC is still ABCMeta, therefore inheriting from ABC requires the usual precautions regarding metaclass usage, as multiple inheritance may lead to metaclass conflicts."
- **enum** (https://docs.python.org/3/library/enum.html): "EnumType is the metaclass for enum enumerations." The next sentence contains an [en dash]; don't quote it.
- **inspect source** (https://github.com/python/cpython/blob/3.15/Lib/inspect.py): the `isabstract` comment quoted in evidence D. Credit as CPython's source.
- **mypy docs, Metaclasses** (https://mypy.readthedocs.io/en/stable/metaclasses.html): "Mypy does not and cannot understand arbitrary metaclass code."
- **PEP 487**, "Simpler customisation of class creation" (Martin Teichmann; Final; 3.6):
  - "Metaclasses are a powerful tool to customize class creation. They have, however, the problem that there is no automatic way to combine metaclasses."
  - "The new mechanism should be easier to understand and use than implementing a custom metaclass, and thus should provide a gentler introduction to the full power of Python’s metaclass machinery."
  - "Especially when writing a plugin system, one likes to register new subclasses of a plugin baseclass."

  ch27 cites PEP 487 for `__set_name__` only and left the other hook to ch29.
- **PEP 3115**, "Metaclasses in Python 3000" (Talin): pointer for `__prepare__`.
- **PEP 520**, "Preserving Class Attribute Definition Order" (Eric Snow; Final; 3.6): "In fact, exactly this is by far the most common use case for using __prepare__." Its note says `__definition_order__` was removed once compact dicts landed. Paraphrase that note; don't quote it.
- **PEP 562**, "Module __getattr__ and __dir__" (Ivan Levkivskyi; Final): "A typical example is managing deprecation warnings." and "Another widespread use case for __getattr__ would be lazy submodule imports."
- **PEP 810**, explicit lazy imports (Pablo Galindo Salgado, Germán Méndez Bravo, Thomas Wouters, Dino Viehland, Brittany Reynoso, Noah Kim, Tim Stumbaugh; Final; 3.15): ch18 quotes it. ch30 names it with one pointer and doesn't re-quote ch18's sentences.
- **python-patterns.guide** (Brandon Rhodes):
  - "The Global Object Pattern": "But in every case, the Mutable Global courts all of the dangers listed above in return for the convenience of putting a resource where every module can reach it."
  - "The Decorator Pattern", "Implementing: Dynamic wrapper": "Because __getattr__() is only invoked for attributes that are in fact missing on the wrapper, the wrapper is free to offer real implementations of any methods or properties it wants to intercept."
- **GoF** isn't quotable (r06 finding). Use the bracketed items only if verified; otherwise describe the idea without attribution.

Repo facts:
- **Reconciliation.** Rows run 1-159, so r14 adds 160-173. Three open legacy rows belong to r14:
  - row 11 (ch30: `__getattr__` only on failed lookup, `__getattribute__` on every access);
  - row 12 (ch30: avoiding recursion only through `object.__getattribute__`/`__dict__`, to be adjusted, evidence L);
  - row 13 (ch29: `__init_subclass__` replaces most metaclass registries).

  `CLAIMS_FIRST_ENFORCED = 47`, so all three are legacy. Q2 gives them test tokens and a status.
- **Figures.** `_data/diagrams.yml` has 29 entries; r14 makes 31 (`section: "Ch. 29"` and `"Ch. 30"`).
- **Test names.** 687 unique `def test_` names across `examples` and `spikes`, with the three known duplicates unchanged. All 50 names in the Example spec were checked against the set, and none clashes. Near-misses not reused:
  - `test_registry_is_init_subclass` (ch3);
  - `test_duplicate_code_is_rejected_by_init_subclass`, `test_unknown_keyword_reaches_object_init_subclass` and `test_mypy_checks_init_subclass_keywords_but_not_metaclass_keywords` (spike 013);
  - `test_a_singleton_metaclass_ignores_the_second_calls_arguments` and `test_mypy_types_a_metaclass_singleton_call_by_init` (ch18);
  - `test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr` (ch20);
  - `test_cached_property_is_lazy_initialisation_without_a_proxy` (ch3).
- **Already taught, so not repeated.** Each gets a pointer by title and at most one sentence:
  - **"The three-way split: dissolve, survive, disambiguate"**: the `__init_subclass__` registry row and witness, `LazyTrackingHistory` with `cached_property`, and the Proxy row.
  - **"Factory Method and Abstract Factory"**: the `frozendict` registry of constructors and `UnknownCarrierError`. ch29 reuses the error and builds no factory.
  - **"Singleton: module, Borg, and metaclass"**: the metaclass `__call__` singleton and its cost, `lazy import` (PEP 810) with its quotations. It points to ch29 for `__call__` mechanics, so ch29 owes that one sentence.
  - **"Decorator the pattern vs @decorator the syntax, and Proxy"**: the explicit proxy, `_ForwardingGatewayProxy`, its four measured costs, and the two data-model quotations. It points to ch30 for the mechanics of `__getattr__`, `__getattribute__` and recursion.
  - **"Decorators done right"**: the class-decorator registry (`document_kind`) and its slots trap. It points to ch29 for "registering classes by other means".
  - **"Descriptors and properties"**: `__set_name__`, lookup precedence (it quotes the guide's chain ending "and lastly __getattr__() if it is provided"), and `cached_property` as lazy initialisation. It points to ch30 for the last link.
  - **"singledispatch: the Visitor the language gives you"**: global registration state and fresh-interpreter tests. ch29 uses the same technique and points there by title at most once.
- **Stubs whose ground must not be taken or described:**
  - "Shortcut patterns: dict dispatch, function tables, and EAFP": no dispatch table in either `src`, and no EAFP discussion beyond `AttributeError` being raised;
  - "Anti-patterns and pattern misuse";
  - "asyncio and the patterns";
  - "Final project".
- **Status board hygiene.** r13 is merged (a03e3a1), but r13's P7 still reads `todo`, PDP-127a to PDP-128c read `active`, and `iteration-plan.md` marks r13 "(active)". The orchestrator closes them at Q0.

## What is new in each chapter

**ch29 (metaclass registry dissolves).** "The three-way split" shows a five-line `__init_subclass__` registry, and "Factory Method and Abstract Factory" a `frozendict` of constructors. This chapter adds:
- **Class keywords.** `code=` on the class statement, and what mypy checks about it: the type, a missing keyword, and a misspelt one only with a closed signature.
- **Refusal at definition.** A duplicate keeps the first class. A concrete class without a code and an abstract class with one are refused, through `inspect.isabstract`. Abstract intermediates are skipped.
- **The order of hooks.** `__set_name__`, then `__init_subclass__`, then class decorators.
- **Where registrations come from.** A carrier module registers only when imported. A manual dict entry is forgotten silently. The registry is a read-only view, and tests register only in a fresh interpreter.
- **The metaclass form.** The same table passes. Its costs: a metaclass conflict with `ABC`, `Protocol` or `Enum`; keywords mypy never checks; `Self` refused; a registry whose values call to `Any`.
- **The honest metaclass case.** Operators on the class object, as `EnumType` gives an enum. `__prepare__`'s common use dissolved in 3.6, and `__call__`'s return type is invisible to mypy.

**ch30 (Proxy disambiguated: interception without a surrogate).** "Decorator the pattern vs @decorator the syntax, and Proxy" shows a forwarding `__getattr__` and its costs. "Descriptors and properties" shows `cached_property`. This chapter adds:
- **A self-loading object.** Declared fields, one load on first access, plain attributes afterwards, and a `cached_property` form passing the same table.
- **When each hook runs.** `__getattr__` once, on the failed lookup. `__getattribute__` on every access.
- **The recursion trap.** A `__getattr__` that reads a missing attribute recurses on a bare instance, so `copy` and `deepcopy` recurse too. An allow-list, `object.__getattribute__` or `vars()` stops it.
- **Being honest to the rest of Python.**
  - `__setattr__` guards loaded fields, and the load writes around it.
  - `__dir__` makes `dir()` and the "Did you mean" hint work.
  - `iter()` and `len()` bypass both hooks, so `__iter__` is defined.
  - `hasattr` loads.
- **What mypy sees.** Declared types kept. A typo typed as `__getattr__`'s return. Assignments accepted that the run time refuses.
- **Module `__getattr__`.** A deprecated name that warns. Its lazy-import use now belongs to `lazy import`.

## Approach

- **Thesis wording.**
  - ch29 says the metaclass registry dissolves into `__init_subclass__` (decision 1). What remains to design is what's refused, where registrations come from, and test isolation. A metaclass is for operators on the class object, and the standard library already ships the ones most code needs.
  - ch30 says Proxy is disambiguated: `__getattr__` used by an object on itself is lazy loading with no surrogate. The surrogate is "Decorator the pattern vs @decorator the syntax, and Proxy".
- **Credit.**
  - PEP 487 (Teichmann), PEP 3115 (Talin), PEP 520 (Snow), PEP 562 (Levkivskyi) and PEP 810 (Galindo Salgado and co-authors) by author and title.
  - The data model, built-ins `dir`, pickle, copy, abc and enum pages, the mypy metaclasses page and CPython's `inspect` source.
  - Rhodes's Global Object page (ch29) and Decorator page (ch30).
  - GoF and Fowler only if verified (bracketed).
  - Every quotation is exact, from fetched pages.
- **Domain names** come from `_plans/shipping-domain-model.md` rows 29-30, the area table and the series supporting names, plus the names below, recorded at Q0. There's no new domain area and no new carrier code.
  - **ch29** (Carrier area): `ConsignmentId`, `CarrierBase`, `FastlineGateway`, `AircoGateway`, `DuplicateCarrierError`, `CarrierRegistrationError` (new), `UnknownCarrierError` (from ch16), `gateway_for` (new), `registry`, `code`. Test-only: `_CarrierMeta`, `_MetaCarrierBase`, `_MetaFastlineGateway`, `_MetaAircoGateway`.
  - **ch30** (Tracking area): `ConsignmentId`, `HandlingEvent`, `HandlingKind`, `ConsignmentStatus`, `TrackingHistory`, `LazyTrackingHistory` (ch3's name, as the deprecated alias), `events`, `status`, `last_port`. Test-only: `_CachedTrackingHistory`. Port codes `NLRTM` and `SGSIN`.
- **One uv member per chapter.** Each is standalone and named after its package (the r13 correction), so no member needs a `[tool.*]` table:
  - `examples/29-metaclasses-init-subclass-and-registries` (project `carrier-registry`, package `carrier_registry`);
  - `examples/30-dynamic-attributes-and-proxy` (project `dynamic-attributes`, package `dynamic_attributes`).
- **mypy witnesses** copy the r13 `_run`/`_codes` helper from `examples/28-singledispatch/tests/test_static.py`: `mypy_path` set to the member's `src`, `--cache-dir os.devnull`, and the anchored regex `re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)`. Each asserts the exit status, an exact `_codes()` set and one or two stable substrings. It never asserts line numbers or optional notes; a requested `reveal_type` note may be matched by substring.
- **Static-test mutation rule (r12, r13).** Every static test names, in the Example spec, the thing its prose credits and a plausible mutation of that thing that makes the test fail.
  - **An exit-0 test also exercises the hazard at run time.** It `exec`s the same snippet in a fresh namespace (`namespace: dict[str, object] = {}`), or runs the `src` call it type-checks, and asserts `_codes(stdout) == set()`.
  - A reduced-model test credits mypy only, and the prose names it as a reduced model.
- **Repair rule (r12).** After every repair, the validator re-reads the paragraph and the close bullets that depend on it. Scope words ("every", "only", "never", "all", "both", "silently") each name the test that witnesses the whole scope, or are cut.
- **Excerpt rule (r12, r13).** No excerpt can break an owner decision:
  - no `metaclass=` in a `src` excerpt;
  - no `**kwargs` in `CarrierBase.__init_subclass__`;
  - no test-process registration on `CarrierBase` inside an excerpt;
  - no `__getattribute__` or `TYPE_CHECKING` in a ch30 `src` excerpt;
  - no second comparison excerpt.

  Q6 checks each excerpt against decisions 4, 5, 6 and 7.
- **Comparison code** (the owner's 2026-11-04 rule). Every comparison form is real, runs on the shared table as a conftest fixture param, and appears in at most one excerpt per chapter (decision 8). Shared row tables live in the test module that uses them; conftest holds only fixtures and forms (the r13 importlib correction).
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (Q1a, Q1b) name the test and say why it sees the deletion. A row whose witness was predicted but not run is marked "executor check".
- **"Silently", "only when imported", "never runs again", "recurses" and "loads" claims** each have a test that fails on a named mutation:
  - a concrete carrier without a code is refused (mutation: the concreteness branch deleted);
  - a carrier module registers only when imported (mutation: `fastline.py` imports `airco`);
  - `__getattr__` never runs after the load (mutation: the load stops writing `vars(self)`);
  - `copy` recurses (mutation: the trap reads `vars(self)`);
  - `hasattr` loads (mutation: `hasattr` replaced by `"status" in dir(h)` in the test).
- **Determinism.**
  - No `mock`, `mocker`, `monkeypatch`, `print(`, `sleep`, `time.time`, `perf_counter` or `datetime.now` in tests.
  - Isolated runs use `sys.executable -I -c` and JSON on stdout through `sys.stdout.write`.
  - No test process registers on `CarrierBase`.
  - Assertions on class collections compare sorted lists of `__name__` or code strings, never a set repr of classes.
  - Recursion tests assert `RecursionError` only, never a depth.
  - `filterwarnings = ["error"]` stays active, so the deprecation test uses `pytest.warns`.
- **Counts** of test functions and cases come from the code, and the pytest summary line wins.

Rejected:
- `metaclass=`, `__prepare__`, `**kwargs` in `__init_subclass__`, `__subclasses__()` and snapshot-restore of `_CARRIERS` in ch29.
- `__getattribute__`, `TYPE_CHECKING`, `cached_property`, `Any`, `cast` and any gateway in ch30's `src`.
- Pickling the `src` history in a test.
- A dict dispatch table in either `src`.

## Per-chapter spec

### ch29: Metaclasses, __init_subclass__, and registries (pattern, has_example = true, bucket: dissolves)

Thesis: a registry of subclasses needs no metaclass. `__init_subclass__` runs on the parent each time a subclass is created, takes class keywords that mypy checks, and can refuse a class before it's registered. What remains to design:
- which classes register;
- what's refused at definition;
- which modules must be imported for a registration to exist;
- how tests avoid each other's registrations.

A metaclass earns its place when the class object itself needs operators, and otherwise costs conflicts and type checking.

Sections (about 2,440 prose words, max 2,500; at most six excerpts, at most one from a comparison fixture):

1. `## Learning objectives` (~90), five bullets, one per close bullet:
   - register subclasses by a class keyword with `__init_subclass__`, and say what mypy checks about it;
   - refuse a bad carrier class at definition;
   - keep a class registry out of other tests' way;
   - name the costs of a metaclass registry;
   - say what only a metaclass can do, and when that's worth it.
2. `## Why this matters` (~170). Intent first: a booking takes a carrier code and needs the gateway class for it, and carriers are added by other teams. Three failures:
   - a manual registration left out of a dict makes a carrier unavailable at run time (test 12);
   - an abstract carrier given a code would be registered and fail on first booking (test 2, `abstract-with-code`);
   - a metaclass registry mixed with another library's base raises a metaclass conflict at import (test 15).
3. Figure plus one paragraph (~50).
4. `## A registry filled at class creation` (~380). Excerpt `CarrierBase.__init_subclass__` with the class header and `registry`.
   - Bucket sentence: dissolves. One pointer to "The three-way split: dissolve, survive, disambiguate".
   - Quote the data model's "Whenever a class inherits ..." sentence. Quote PEP 487's "plugin system" sentence (Teichmann).
   - Each carrier registers by its keyword, and the registry maps codes to classes (tests 1, 3). `gateway_for` books through it (test 4) and raises `UnknownCarrierError` for an unknown code (test 5).
   - mypy checks the keyword's type (test 19) and, because the signature takes no `**kwargs`, a misspelt keyword, with `did you mean "code"?` (test 20). Quote the data model's "For compatibility ..." sentence, and say why the root closes it. Experiment (a) is the forwarded form.
5. `## Refusing a bad carrier class` (~320):
   - A duplicate code raises and keeps the first class (test 7).
   - An abstract intermediate is skipped (test 8). A concrete class with no code is refused, so a forgotten keyword can't hide (test 9). An abstract class given a code is refused (test 2).
   - `inspect.isabstract` sees abstractness inside the hook, although `__abstractmethods__` isn't set yet (test 10). Credit CPython's `inspect` source for the branch. Experiment (b) is the `__abstractmethods__` check.
   - The hooks run in order: `__set_name__`, `__init_subclass__`, then class decorators (test 11). Quote the data model's step list. One pointer each to "Descriptors and properties" and "Decorators done right", describing nothing.
6. `## Where registrations come from` (~280):
   - In a fresh interpreter, importing `carriers` gives an empty registry, and each carrier module adds its code when imported (test 13). Someone has to import every carrier module: the failure has moved from a forgotten dict entry (test 12) to a forgotten import.
   - Quote Rhodes's Global Object sentence on the mutable global.
   - The registry is a read-only view (test 6). Tests define only classes that are refused, which raise before anything is inserted (test 2 asserts the unchanged registry). A carrier that does register is checked in a fresh interpreter (tests 13, 14).
   - One sentence pointing to "singledispatch: the Visitor the language gives you" for the same discipline on a dispatcher.
7. `## The same registry as a metaclass` (~350). The comparison excerpt is `_CarrierMeta.__new__`.
   - Both forms pass the same booking and refusal table (tests 1, 2).
   - Quote PEP 487 on combining metaclasses and the abc docs' "metaclass conflicts" sentence. A plain metaclass under an `ABC` or a `Protocol` raises the conflict (test 15). Deriving from `ABCMeta` resolves it (test 16).
   - mypy 2.4.1, on reduced models (said as such):
     - reports the conflict (test 22);
     - never checks a metaclass's class keywords, so `code=1` registers an `int` key (test 21);
     - refuses `Self` in a metaclass `__new__` (test 23);
     - types a class called from a registry of metaclass instances as `Any` (test 24).
   - Quote the mypy docs' "does not and cannot understand arbitrary metaclass code".
8. `## What only a metaclass can do` (~230):
   - Special methods are looked up on the type, and a class's type is its metaclass. So `"AIRCO" in _MetaCarrierBase`, `len()` and iteration work only through one (test 17). On `CarrierBase` the same `in` raises `TypeError`.
   - Quote the enum docs' `EnumType` sentence: that's the case worth the cost.
   - `__prepare__`: quote PEP 520 (Snow). Paraphrase that class namespaces keep definition order since 3.6.
   - `__call__`: `type.__call__` runs `__new__` then `__init__`, and mypy 2.4.1 types the call by `__init__` even when a metaclass `__call__` declares another return (test 25, reduced model). Point to "Singleton: module, Borg, and metaclass" by title.
9. `## When not to use it` (~140):
   - a fixed set one module owns (a `frozendict` of constructors; point to "Factory Method and Abstract Factory");
   - a registry whose entries aren't classes (a function and a dict);
   - a metaclass for anything `__init_subclass__`, a class decorator or a descriptor does;
   - registration that depends on modules nobody is sure will be imported.

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Specifying a class registry.** Asked for "a plugin registry", an assistant often writes a metaclass, or forwards `**kwargs` so a misspelt class keyword is never named. Paste a prompt that states the form:

   > Register carrier classes with `__init_subclass__(cls, *, code: str | None = None)` on `CarrierBase`, with no `**kwargs` and no metaclass. Use `inspect.isabstract(cls)`: an abstract class takes no code, a concrete class must have one, and a duplicate code raises `DuplicateCarrierError`. Expose the registry as a read-only `MappingProxyType`. In tests, define only classes that are refused, and check a carrier that registers in a fresh interpreter.

   If the reply adds a metaclass, ask what it does that `__init_subclass__` can't.</blockquote>

   The sidebar body is at most 120 words by `validate.word_count`. Every backticked name exists in `src` or the standard library.
10. `## Build, run, observe` (~180 plus output).
    - Each experiment runs in a fresh scratch copy: delete the copy's `.venv`, run `uv sync --locked --all-packages`, and confirm `carrier_registry.__file__` points into the copy.
    - Each changes one thing, then is reverted.
    - Each runs a filter chosen by the prose agent, followed by `uv run mypy --strict src tests`. **The filter is stated in the chapter, and the chapter quotes its complete output.** pytest continuation lines are matched as `E` plus 9 spaces (`E {9}`), as r13's correction fixed.

    Experiments:
    - (a) In `CarrierBase.__init_subclass__`, add `**kwargs: object` and pass it to `super().__init_subclass__(**kwargs)`.
      - Expected:
        - test 2[init_subclass-unknown-keyword] fails: the message is `... takes no keyword arguments`, not `unexpected keyword argument 'cod'`;
        - test 20 fails with an empty code set;
        - mypy exits 0.
      - Executor check: the exact failing set, and whether the `E {9}` line shows the class name.
      - Quote as observed.
    - (b) Replace `isabstract(cls)` with `bool(getattr(cls, "__abstractmethods__", ()))`.
      - Expected:
        - test 8 fails with `CarrierRegistrationError: ... is concrete and needs a code`;
        - test 2[init_subclass-abstract-with-code] fails with `DID NOT RAISE` and registers `HALF`;
        - mypy exits 0.
      - Executor check: whether the registered `HALF` makes later "registry unchanged" assertions fail in collection order. Run the filter twice and confirm identical output apart from the duration. If later tests are affected, say so in the prose.
      - Quote as observed.
11. `## What you can do now` (~130): five bullets, one per objective, in the same order. They name:
    - `__init_subclass__` with test 20;
    - `CarrierRegistrationError` with test 9;
    - test 13;
    - `_CarrierMeta` with test 15;
    - test 17.

    Every backticked token in the close appears earlier in the chapter.
12. `## For deeper coverage` (~100):
    - the data model's "Customizing class creation" and "Metaclasses";
    - PEPs 487, 3115 and 520;
    - the abc and enum pages;
    - the mypy metaclasses page;
    - Rhodes's Global Object page;
    - [Fowler, PoEAA, Registry, if verified];
    - [Ramalho, *Fluent Python* 2nd ed., on class metaprogramming, if verified];
    - the bibliography link.

Figure `29-metaclasses-init-subclass-and-registries` (vertical):
- Top: `class FastlineGateway(CarrierBase, code="FASTLINE")`.
- Down a column:
  - a muted, dashed box "metaclass __prepare__: namespace (metaclass only)";
  - "class body runs";
  - `type.__new__`;
  - `__set_name__`;
  - the accent box `CarrierBase.__init_subclass__`, with three lines: "isabstract: abstract takes no code", "concrete needs a code", "duplicate raises DuplicateCarrierError";
  - "class decorators".
- An arrow from the accent box into a side box `registry` "read-only view: FASTLINE, AIRCO".
- Lower, a muted, dashed box `_CarrierMeta` "same registry; conflicts with another metaclass; mypy skips its keywords".
- No numbers in the SVG.

Caption draft (about 40 words with the prefix): "Figure 29.1: Creating a carrier class runs the namespace, the class body, `__set_name__` and then `__init_subclass__`, which refuses a bad class before it reaches the read-only registry. A metaclass can do the same and conflicts with other metaclasses." P3 counts and adjusts the caption; it carries no backticks in `_data/diagrams.yml` if the existing captions don't.

### ch30: Dynamic attributes: __getattr__ and Proxy as a feature (pattern, has_example = true, bucket: needs disambiguating, Proxy)

Thesis: the catalogue's virtual proxy is a stand-in that creates the expensive object on demand. In Python an object can do that for itself: `__getattr__` runs only when ordinary lookup fails, so a history can declare its fields, load them on the first read and keep them as plain attributes. That's interception, not a surrogate. What remains to design:
- which names it may load;
- that it never reads a missing attribute while loading;
- that it stays honest to `dir()`, `copy`, special-method lookup and mypy.

Sections (about 2,450 prose words, max 2,500; at most six excerpts, at most one from a comparison fixture):

1. `## Learning objectives` (~100), five bullets:
   - load a record's fields once, on first access, with `__getattr__`;
   - predict when `__getattr__` and `__getattribute__` run;
   - keep `__getattr__` out of recursion, under `copy` too;
   - make a dynamic object honest to `dir()`, special-method lookup and mypy;
   - deprecate a module name with a module-level `__getattr__`.
2. `## Why this matters` (~160). Intent first: a tracking history comes from a carrier feed that's slow to read, and most callers only want the consignment id. Three failures:
   - a `__getattr__` that reads a missing attribute recurses as soon as the history is copied (test 11);
   - a `__getattr__` that answers every name turns a misspelt field into `None` (test 14);
   - mypy accepts a misspelt field read (test 22).
3. Figure plus one paragraph (~50).
4. `## A history that loads itself` (~370). Excerpt `TrackingHistory.__init__` and `__getattr__`.
   - Bucket sentence: Proxy is disambiguated here. One pointer to "Decorator the pattern vs @decorator the syntax, and Proxy" for the surrogate. [GoF, virtual proxy, if verified]. [Fowler, PoEAA, Lazy Load ghost, if verified].
   - Nothing loads until a field is read (test 5). One load fills all three fields (test 2), which then sit in the instance dictionary (test 6). Quote the data model's "Note that if the attribute is found through the normal mechanism, __getattr__() is not called."
   - The comparison excerpt is `_CachedTrackingHistory`'s `_events` and `status`. Both forms pass the same table (tests 1-4). The `cached_property` form needs a property per field, and one pointer to "Descriptors and properties" covers its mechanics.
   - Iteration loads (test 7).
5. `## When each hook runs` (~240):
   - Quote Rhodes's "only invoked for attributes that are in fact missing" sentence.
   - A counting subclass sees `__getattr__` once over three reads (test 8), and `__getattribute__` on every read, the set `consignment_id` included (test 9). This closes legacy row 11.
   - Quote the data model's `__getattribute__` recursion sentence. The member defines no `__getattribute__`: it costs every read, and `__getattr__` is enough.
6. `## The recursion trap` (~300):
   - A `__getattr__` that reads `self._load` for any missing name recurses on an instance whose `__init__` never ran (test 10).
   - `copy.copy` and `copy.deepcopy` build exactly such an instance and look up `__setstate__` (test 11, three cases with pickle). Quote the copy and pickle sentences.
   - Three fixes hold (test 13): refusing names outside a fixed set (the member's), `object.__getattribute__`, and `vars(self)`. This adjusts legacy row 12.
   - The member's history copies before and after loading (test 12).
   - A `__getattr__` that answers every name hides a typo as `None` (test 14). The allow-list raises instead (test 4).
7. `## Honest to the rest of Python` (~320). Excerpt `__setattr__`, `__dir__` and `__iter__`.
   - `__setattr__` refuses loaded fields (test 3), while the load writes through `vars(self)` around it. Quote the data model's `__setattr__` sentence and the "intentional asymmetry" clause.
   - `dir()` lists the lazy fields without loading (test 16). Quote the built-ins `dir` sentence. With `__dir__`, a misspelt field gets the interpreter's "Did you mean" hint, and without it, none (test 17). Say the hint's wording is the interpreter's, as observed on 3.15.2.
   - `iter()` and `len()` look on the type and reach neither hook (test 15), so `__iter__` is defined. One sentence pointing to "Decorator the pattern vs @decorator the syntax, and Proxy", which quotes the rule.
   - `hasattr` loads (test 18): checking for a field reads the feed.
8. `## What mypy sees` (~230):
   - mypy 2.4.1 keeps declared fields' types (test 23) and types any other name as `__getattr__`'s return, `object`, so a misspelt read passes and only its use is reported (test 22).
   - Because `__setattr__` takes any name, mypy accepts assigning a loaded field, which the run time refuses, and any new name (test 24).
   - The `cached_property` form reports the typo with `maybe "status"?` (test 25, reduced model).
   - One clause: a forwarding `__getattr__` typed `Any` is worse, as "Decorator the pattern vs @decorator the syntax, and Proxy" measures.
9. `## A module-level __getattr__` (~190). Excerpt the module `__getattr__` and `__dir__`.
   - Quote PEP 562's deprecation sentence (Levkivskyi). The old name warns and returns `TrackingHistory` (test 19). Other names raise (test 20). `dir()` lists the old name (test 21).
   - Quote the data model's "only affect lookups made using the attribute access syntax".
   - mypy accepts names imported through it (test 26, as observed).
   - Quote PEP 562's "lazy submodule imports" sentence. On 3.15 the importing side has `lazy import` (PEP 810): one pointer to "Singleton: module, Borg, and metaclass".
10. `## When not to use it` (~140):
    - one lazy field (`cached_property`; point to "Descriptors and properties");
    - fields that aren't known when the class is written (a mapping, not attributes);
    - wrapping another object's interface (an explicit proxy; point to "Decorator the pattern vs @decorator the syntax, and Proxy");
    - anything a `property` says more plainly.

    Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Specifying a lazy object.** Asked for "lazy loading", an assistant often writes a `__getattr__` that fetches or forwards every missing name, which recurses under `copy` and turns a typo into a fetch. Paste a prompt that states the form:

    > Declare `TrackingHistory`'s loaded fields as class annotations. Write `__getattr__` to load only the names in a fixed set, store them with `vars(self).update(...)`, and raise `AttributeError` for every other name. Refuse assignment to loaded fields in `__setattr__`, list them in `__dir__`, and define `__iter__` explicitly. For a single lazy value, use `functools.cached_property` instead.

    If `__getattr__` reads an attribute it doesn't own, ask what `copy.copy` does.</blockquote>
11. `## Build, run, observe` (~180 plus output). The scratch-copy and stated-filter rules are the same as ch29's (confirm `dynamic_attributes.__file__`).
    - (a) Delete `TrackingHistory.__dir__`.
      - Expected: test 16 fails (`assert 'status' in [...]`) and test 17 fails (no "Did you mean"). mypy exits 0.
      - Quote as observed.
    - (b) In `__getattr__`, delete the allow-list `if`/`raise`, so every missing name loads.
      - Expected:
        - test 12 fails with `RecursionError`;
        - test 4[getattr] fails (a `KeyError` from `vars(self)[name]`, not `AttributeError`);
        - test 13[allow-list] and test 17 fail;
        - mypy exits 0.
      - Executor check: the exact set, and whether the `RecursionError` lines need a stated `sed` for repeated frames (quote only the filter's lines).
      - Quote as observed.
12. `## What you can do now` (~130): five bullets mapped one to one to the objectives. They name:
    - `TrackingHistory` with test 2;
    - test 8;
    - test 11;
    - `__dir__` with test 17;
    - `LazyTrackingHistory` with test 19.
13. `## For deeper coverage` (~100):
    - the data model's "Customizing attribute access" and "Special method lookup";
    - PEPs 562 and 810;
    - the built-ins, copy and pickle pages;
    - Rhodes's Decorator page;
    - [GoF, Proxy, if verified];
    - [Fowler, PoEAA, Lazy Load, if verified];
    - [Ramalho, *Fluent Python* 2nd ed., on dynamic attributes, if verified];
    - the bibliography link.

Figure `30-dynamic-attributes-and-proxy` (vertical):
- Top: `history.status`.
- Then `__getattribute__` "normal lookup: class, instance dict".
- A split:
  - "found" goes to "value" (side);
  - "AttributeError" goes to the accent box `TrackingHistory.__getattr__`.
- Under the accent box, two branches:
  - "name in the lazy set" goes to `load(consignment_id)` "once", then `vars(self).update` "events, status, last_port", then "value";
  - "any other name" goes to `AttributeError` "with a Did you mean hint from __dir__".
- A side box: "iter(), len(): looked up on the type, bypass both".
- A muted, dashed box: "a __getattr__ that reads a missing attribute recurses (copy)".
- No numbers in the SVG.

Caption draft (about 38 words with the prefix): "Figure 30.1: A read that ordinary lookup can't answer reaches `__getattr__`, which loads the declared fields once into the instance dictionary and refuses any other name. Later reads never reach it, and `iter()` and `len()` bypass both hooks."

Citations, both chapters: verify each before writing, apply the bracketed fallbacks, quote no sentence unless it was checked on a fetched page, stop each quotation where the page's sentence stops, and make no comparison between languages.

## Example spec

### `examples/29-metaclasses-init-subclass-and-registries` (project `carrier-registry`, package `carrier_registry`)

`pyproject.toml` in the r13 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`).

- `carriers.py` (decisions 2-5, evidence E):
  - `ConsignmentId = NewType("ConsignmentId", str)`;
  - `DuplicateCarrierError(Exception)`, `CarrierRegistrationError(TypeError)`, `UnknownCarrierError(LookupError)`;
  - `_CARRIERS: dict[str, type[CarrierBase]] = {}`;
  - `CarrierBase(ABC)`:
    - `registry: ClassVar[Mapping[str, type[CarrierBase]]] = MappingProxyType(_CARRIERS)`;
    - `code: ClassVar[str]`;
    - `__init_subclass__(cls, *, code: str | None = None) -> None`, which calls `super().__init_subclass__()` and then applies the four checks in decision 3's order;
    - abstract `book(self, consignment_id: ConsignmentId, /) -> str`.
  - `gateway_for(code: str) -> CarrierBase`, raising `UnknownCarrierError(f"unknown carrier {code!r}") from None`.
  - Docstrings say:
    - why the signature takes no `**kwargs`;
    - that refusals happen before insertion;
    - that a carrier exists only once its module is imported.
- `fastline.py`: `FastlineGateway(CarrierBase, code="FASTLINE")`, `book` gives `f"FL-{consignment_id}"`.
- `airco.py`: `AircoGateway(CarrierBase, code="AIRCO")`, `book` gives `f"AC-{consignment_id}"`.
- `py.typed`, and an `__init__.py` that imports no submodule.

`tests/conftest.py`:
- Imports `carrier_registry.fastline` and `carrier_registry.airco`.
- `_CarrierMeta(ABCMeta)`:
  - `code: str`;
  - `__new__(mcs, name, bases, namespace, /, *, code: str | None = None) -> _CarrierMeta`, applying the same four rules with the `src` exceptions into `_META_CARRIERS: dict[str, _CarrierMeta]` (evidence G, no ignores);
  - `__contains__`, `__iter__` (sorted codes) and `__len__`.
- `_MetaCarrierBase(metaclass=_CarrierMeta)` with abstract `book`, plus `_MetaFastlineGateway` and `_MetaAircoGateway`.
- `registry_form` params `init_subclass|metaclass`, each giving a small frozen dataclass typed by a Protocol:
  - `base: type`;
  - `codes() -> list[str]` (sorted);
  - `book(code, consignment_id) -> str`.

  No `Any`.

`test_registry.py` (holds `BOOKING_ROWS` and `REFUSAL_ROWS`, and a `_define(base, name, *, code, concrete)` helper over `types.new_class`):
1. `test_every_registry_form_books_through_the_registered_carrier` x `registry_form` (2) x `BOOKING_ROWS` (`fastline` gives `FL-CN-1`, `airco` gives `AC-CN-1`) = 4.
2. `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry` x `registry_form` (2) x `REFUSAL_ROWS` (4) = 8. After each, `form.codes() == ["AIRCO", "FASTLINE"]`. The rows:
   - `duplicate`: `DuplicateCarrierError`, matching `'FASTLINE' is already registered to`;
   - `concrete-without-code`: `CarrierRegistrationError`, matching `is concrete and needs a code`;
   - `abstract-with-code`: `CarrierRegistrationError`, matching `is abstract and cannot take code 'HALF'`;
   - `unknown-keyword`: `TypeError`, matching `unexpected keyword argument 'cod'`.
3. `test_the_registry_maps_each_code_to_its_gateway_class`: `sorted((code, cls.__name__) ...)` and `FastlineGateway.code == "FASTLINE"`.
4. `test_gateway_for_books_with_the_registered_carrier`.
5. `test_an_unknown_code_raises_unknown_carrier_error`: matching `unknown carrier 'NOPE'`.
6. `test_the_carrier_registry_is_a_read_only_view`: `TypeError` matching `does not support item assignment`. One `# type: ignore[index]` if mypy asks (executor check).
7. `test_a_duplicate_code_keeps_the_first_class`: the message names `FastlineGateway`, and `registry["FASTLINE"] is FastlineGateway`.
8. `test_an_abstract_intermediate_class_is_not_registered`: a test-local abstract subclass with no code raises nothing, and the registry is unchanged.
9. `test_a_concrete_class_without_a_code_is_refused`.
10. `test_isabstract_sees_abstractness_inside_init_subclass`: a test-local ABC root whose hook records `(name, isabstract(cls), hasattr(cls, "__abstractmethods__"))` gives `[("Mid", True, False), ("Conc", False, False)]`. Corrects spike 013.
11. `test_set_name_runs_before_init_subclass_and_a_class_decorator_after`: a test-local root, descriptor and class decorator log `["__set_name__", "__init_subclass__", "decorator"]`.
12. `test_a_forgotten_manual_registration_leaves_the_carrier_unavailable`: a test-local dict with only one of two classes added, and a lookup of the other raises `KeyError`. Domain row 29's failing test.
13. `test_a_carrier_module_registers_only_when_it_is_imported`: `_run_isolated`, which imports `carrier_registry.carriers` and then `.airco`, then `.fastline`, and dumps the sorted codes after each: `[]`, `["AIRCO"]`, `["AIRCO", "FASTLINE"]`.
14. `test_a_concrete_carrier_under_an_abstract_intermediate_registers`: `_run_isolated`. An abstract intermediate with no code, then a concrete subclass with `code="FASTLINE"` before `fastline` is imported, gives `["FASTLINE"]` and the subclass's name.

`test_metaclass.py`:

15. `test_a_second_metaclass_conflicts_with_the_bases_metaclass[abc|protocol]` (2): a test-local `type` subclass as `metaclass=` under `CarrierBase`, and under a test-local `Protocol`. Each raises `TypeError` matching `metaclass conflict`.
16. `test_a_metaclass_derived_from_abcmeta_resolves_the_conflict`: under `CarrierBase`, an abstract class with no code. Nothing registers.
17. `test_only_a_metaclass_gives_the_class_object_operators`: `"AIRCO" in _MetaCarrierBase`, `list(_MetaCarrierBase) == ["AIRCO", "FASTLINE"]` and `len(...) == 2`. On `CarrierBase`, `in` raises `TypeError` matching `is not a container or iterable`, which needs `# type: ignore[operator]` (executor check).

`test_static.py` (each row: credited thing; mutation that fails it):

18. (no test; numbering continues at 19 to keep the reconciliation ids stable)
19. `test_mypy_checks_the_type_of_a_class_keyword`: imports `src`; `class X(CarrierBase, code=1)` gives `{"arg-type"}` and `Argument "code" to "__init_subclass__" of "CarrierBase"`. Credits `code: str | None`. Mutation: `code: object` empties the set.
20. `test_mypy_reports_a_misspelt_class_keyword`: imports `src`; `cod="X"` gives `{"call-arg"}` and `did you mean "code"?`. Credits the closed signature. Mutation: `**kwargs: object` (experiment a) empties the set.
21. `test_mypy_does_not_check_metaclass_class_keywords`: reduced model; exits 0 with `_codes == set()`. `exec` shows `code=1` registered an `int` key. Mutation: the snippet's base uses `__init_subclass__` and gives `[arg-type]`.
22. `test_mypy_reports_a_metaclass_conflict`: reduced model; `{"metaclass"}`, and `exec` raises `TypeError` `metaclass conflict`. Mutation: the snippet's metaclass derives from `ABCMeta`, which empties both halves.
23. `test_mypy_refuses_self_in_a_metaclass_new`: reduced model; `{"misc"}`, `Self type cannot be used in a metaclass`. Mutation: `-> CarrierMeta` empties the set.
24. `test_mypy_types_a_class_called_from_a_metaclass_registry_as_any`: reduced model; exit 0, `Revealed type is "Any"`, `_codes == set()`. `exec` of `registry["F"]().bok("CN-1")` raises `AttributeError`. Mutation: typing the registry `dict[str, type[MetaBase]]` gives `[attr-defined]` on `bok` (and `[assignment]`).
25. `test_mypy_ignores_a_metaclass_call_return_type`: reduced model; `__call__ -> int`; `Revealed type is "__main__.G"`, exit 0. `exec` gives `1`. Mutation: dropping the metaclass makes the runtime half return a `G`, so the test fails.

Numbers are spec ids, not file order. The plan has 23 test functions and 33 cases:
- `test_registry.py`: 14 functions, 23 cases;
- `test_metaclass.py`: 3 functions, 4 cases;
- `test_static.py`: 6 functions, 6 cases (spec ids 19-25 minus the unused 18 leave 7; executor recounts).

The executor counts from the pytest summary line. Q1a records any difference.

Also `README.md` and the card `_examples/29-metaclasses-init-subclass-and-registries.md`: `order: 29`, eyebrow "Idiomatic Python · Class registries", and a concept title with no count. None of the following appears in `src/`: `metaclass`, `__prepare__`, `**kwargs`, `__subclasses__`, `Any`, `cast`, `mock`, `monkeypatch`, `print(`, `Optional`, `TYPE_CHECKING`, `__getattr__`, `dict[str, Callable`.

Deletion table (Q1a):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| insert into `_CARRIERS` | removed | 1[init_subclass-*], 3, 4 | registry empty; `UnknownCarrierError` |
| `cls.code = code` | removed | 3 | `AttributeError` on `FastlineGateway.code` |
| duplicate check | removed | 7, 2[init_subclass-duplicate] | `DID NOT RAISE`; `AIRCO`/`FASTLINE` mapping changed (executor check: later rows) |
| concrete-needs-code branch | removed | 9, 2[init_subclass-concrete-without-code] | `DID NOT RAISE` |
| abstract-with-code branch | removed | 2[init_subclass-abstract-with-code] | `DID NOT RAISE`; `HALF` registered |
| `isabstract` | `__abstractmethods__` check (experiment b) | 8, 2[init_subclass-abstract-with-code] | intermediate refused; abstract registered |
| closed signature | `**kwargs` forwarded (experiment a) | 20, 2[init_subclass-unknown-keyword] | codes empty; message no longer names `'cod'` |
| `MappingProxyType` | plain dict | 6 | `DID NOT RAISE` |
| `from None` and `UnknownCarrierError` | bare `KeyError` | 5 | wrong exception type |
| `__init__.py` imports nothing | imports both carriers | 13 | the first dump is `["AIRCO", "FASTLINE"]` |

### `examples/30-dynamic-attributes-and-proxy` (project `dynamic-attributes`, package `dynamic_attributes`)

- `tracking.py` (decisions 7 and 9, evidence P, Q):
  - `ConsignmentId`;
  - `HandlingKind` (`BOOKED`, `LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED`);
  - `ConsignmentStatus` (ch25's values);
  - `_STATUS_AFTER: Mapping[HandlingKind, ConsignmentStatus]`;
  - `HandlingEvent` (frozen slotted);
  - `_LAZY`;
  - `TrackingHistory` as in decision 7;
  - the module `__getattr__(name: str) -> type[TrackingHistory]` and module `__dir__() -> list[str]`.
  - Docstrings say:
    - why `__getattr__` reads only its own names;
    - that the load writes around `__setattr__`;
    - that `hasattr` loads.
- `py.typed`, `__init__.py` (imports nothing).

`tests/conftest.py`:
- `_CachedTrackingHistory(consignment_id, load)`: `@cached_property def _events`, and `@property`s `events`, `status`, `last_port`. Typed with the same `load` signature.
- A `recording_load` fixture: a loader that appends each consignment id to a list it exposes, and returns events by id:
  - `CN-1`: booked, loaded, departed at `SGSIN`;
  - `CN-2`: booked;
  - `CN-3`: through delivered;
  - `CN-4`: no events.
- `history_form` params `getattr|cached_property`, each giving a constructor `(ConsignmentId, load) -> HistoryView`, where `HistoryView` is a small read-only Protocol (`events`, `status`, `last_port`, `consignment_id`, `__iter__`). No `Any`.

`test_history.py` (holds `HISTORY_ROWS`):
1. `test_every_history_form_reads_the_loaded_fields` x `history_form` (2) x `HISTORY_ROWS` (`in-transit`, `booked`, `delivered`, `empty`) = 8: event count, `status` and `last_port`, with `None` for `empty`.
2. `test_every_history_form_loads_once_for_every_field` x 2: reading the three fields twice each records one load.
3. `test_every_history_form_refuses_assignment_to_a_loaded_field` x 2: `AttributeError`.
4. `test_every_history_form_raises_attribute_error_for_a_misspelt_field` x 2: `AttributeError` matching `stauts`.
5. `test_nothing_is_loaded_until_a_field_is_read`: `sorted(vars(h)) == ["_load", "consignment_id"]`, and no loads.
6. `test_a_loaded_history_reads_its_fields_from_the_instance_dict`: after one read, `sorted(vars(h))` includes `events`, `last_port` and `status`.
7. `test_iterating_a_history_loads_it`: `[e.kind for e in h]`, one load.

`test_lookup.py`:

8. `test_getattr_runs_only_when_normal_lookup_fails`: a counting subclass reads `status` three times and `consignment_id` once, and logs `["status"]`. Legacy row 11.
9. `test_getattribute_runs_on_every_access`: a counting subclass logs `status` three times and `consignment_id` once. Legacy row 11.
10. `test_a_getattr_that_reads_a_missing_attribute_recurses`: a test-local `_SelfHealing` with `__new__` and no `__init__`; reading `events` raises `RecursionError`. Legacy row 12.
11. `test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute[copy|deepcopy|pickle]` (3): `RecursionError`. `pickle` uses a module-level loader in the test module and is an executor check under importlib mode. If pickling by reference fails, the case becomes `copy.replace`-free `copy` only and Q1b records it.
12. `test_copy_keeps_a_history_before_and_after_loading`: `copy.copy` and `copy.deepcopy` of the `src` history, unloaded (no load happens) and loaded (same fields).
13. `test_each_fix_keeps_getattr_out_of_recursion[allow-list|object-getattribute|vars]` (3): `allow-list` is `src` `TrackingHistory`; the other two are test-local. For each, `copy.copy` of a bare `__new__` instance succeeds, and reading `events` on it raises `AttributeError`, not `RecursionError`.
14. `test_a_getattr_that_returns_none_hides_a_typo`: a test-local `.get(name)` form gives `None` for `stauts`. Domain row 30's failing test.
15. `test_implicit_special_method_lookup_bypasses_getattr`: a test-local forwarding object. `list(obj.__iter__())` works, and `iter(obj)` raises `TypeError` matching `is not iterable`, with an empty hook log.
16. `test_dir_lists_the_lazy_fields_before_loading`: `{"events", "last_port", "status"} <= set(dir(h))`, and no loads.
17. `test_a_misspelt_field_suggests_the_declared_name_through_dir`: `traceback.format_exception_only` ends with `Did you mean '.status' instead of '.stauts'?`. A test-local subclass whose `__dir__` returns `object.__dir__(self)` gets no `Did you mean`.
18. `test_hasattr_loads_the_history`: `hasattr(h, "status")`, one load.

`test_module.py`:

19. `test_a_deprecated_name_warns_and_returns_the_tracking_history`: `pytest.warns(DeprecationWarning, match="LazyTrackingHistory is deprecated; use TrackingHistory")`, and the value `is TrackingHistory`. It reads through `getattr(tracking, "LazyTrackingHistory")` with ruff B009 suppressed by a coded `# noqa` with a reason, or through `importlib`: executor check.
20. `test_an_unknown_module_attribute_raises_attribute_error`: matching `module 'dynamic_attributes.tracking' has no attribute 'Missing'`.
21. `test_module_dir_lists_the_deprecated_name`.

`test_static.py` (each row: credited thing; mutation that fails it):

22. `test_mypy_types_an_unknown_attribute_by_the_getattr_return_type`: imports `src`; `reveal_type(h.stauts)` and `h.stauts.upper()` give `{"attr-defined"}`, `Revealed type is "builtins.object"` and `"object" has no attribute "upper"`. Stdout has exactly one error line. Credits `__getattr__ -> object`. Mutation: deleting `__getattr__` adds `"TrackingHistory" has no attribute "stauts"` on the read line, so the count changes.
23. `test_mypy_keeps_the_declared_field_types`: imports `src`; `n: int = h.status` gives `{"assignment"}` and `ConsignmentStatus | None`. Mutation: deleting the `status` annotation turns the message's type into `object`.
24. `test_mypy_accepts_an_assignment_that_setattr_refuses`: imports `src`; `h.status = None` and `h.anything = 1` exit 0 with `_codes == set()`. The same assignment on a real history raises `AttributeError` matching `is loaded, not assigned`. Mutation: deleting `__setattr__` gives `[attr-defined]` for `anything`.
25. `test_mypy_reports_a_typo_on_the_cached_property_form`: reduced model; `{"attr-defined"}`, `maybe "status"?`. Mutation: adding `__getattr__ -> object` to the snippet empties the set.
26. `test_mypy_accepts_any_name_imported_through_a_module_getattr`: imports `src`; `from dynamic_attributes.tracking import Anything`. Predicted exit 0 and `type[dynamic_attributes.tracking.TrackingHistory]` (executor check, evidence R). The runtime half `import`s the same name in a fresh namespace and gets `ImportError` matching `cannot import name 'Anything'`. Mutation: deleting the module `__getattr__` gives `[attr-defined]`. If mypy 2.4.1 prints otherwise, the test asserts what it prints and Q1b records it.

Numbers are spec ids, not file order. The plan has 26 test functions and 36 cases:
- `test_history.py`: 7 functions, 17 cases;
- `test_lookup.py`: 11 functions, 15 cases;
- `test_module.py`: 3 functions, 3 cases;
- `test_static.py`: 5 functions, 5 cases.

(The per-file case counts sum to 40; the executor counts from the pytest summary line, and Q1b records the true figures.)

Also `README.md` and the card `_examples/30-dynamic-attributes-and-proxy.md`: `order: 30`, eyebrow "Idiomatic Python · Dynamic attributes", and a concept title. None of the following appears in `src/`: `__getattribute__`, `cached_property`, `TYPE_CHECKING`, `Any`, `cast`, `metaclass`, `__init_subclass__`, `Gateway`, `mock`, `monkeypatch`, `print(`, `Optional`.

Deletion table (Q1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| allow-list `raise` | removed (experiment b) | 4[getattr], 12, 13[allow-list], 17 | `KeyError`; `RecursionError` under `copy` |
| load writes `vars(self)` | returns without storing | 2[getattr], 6, 8 | loads on every read; `__getattr__` logged three times |
| one load for all fields | loads only the asked field | 2[getattr], 6 | three loads |
| `__setattr__` guard | removed | 3[getattr], 24 runtime half | assignment accepted |
| `__setattr__` passes others | raises for all | 5 (construction fails) | `__init__` can't set `consignment_id` |
| `__dir__` | removed (experiment a) | 16, 17 | lazy names absent; no hint |
| explicit `__iter__` | removed | 7, 1[getattr-*] if rows iterate | `TypeError: ... is not iterable` |
| empty-load `None` | `events[-1]` | 1[getattr-empty] | `IndexError` |
| module `__getattr__` warning | removed | 19 | `DID NOT WARN` |
| module `__getattr__` raise | returns `None` | 20 | `DID NOT RAISE` |
| module `__dir__` | removed | 21 | name absent |

## Steps and status

Step ids are `Q*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| Q0 | Bookkeeping, all with dated notes, plus re-checking the upstream pins and recording the decisions. In `iteration-plan.md`: PDP-129a-c and 130a-c `active`, r14 active, r13 closed, PDP-127a to 128c closed. In r13's plan: P7 closed. In the reconciliation plan: rows 160-173 `open`, rows 11-13 noted "r14". In the domain model: rows 29-30 get the supporting names and decisions 1-10, and row 29's abstractness clause and two-ignores clause are corrected per evidence D and G. ch29-30 stub `description` lines are written | - | done |
| Q1a | ch29 member, card and README; one `uv lock`; three green runs plus one reverse-file-order run; the deletion table, each row in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`), deleted after use | Q0 | done |
| Q1b | ch30 member, card and README; one `uv lock` after Q1a (sequenced for `uv.lock`); three green runs plus one reverse-order run; the deletion table | Q1a | done |
| Q2 | Witness results into rows 160-172 and legacy rows 11-13 (11 verified (r14), 12 adjusted (r14), 13 verified (r14)). The dated r14 note in `_plans/spikes.md` (evidence D, F, G, H, I, K). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | Q1b | done |
| Q3 | Two figures, specs `diagrams/specs/29-*.py` and `30-*.py`, and `_data/diagrams.yml` (single owner; 31 entries). Figures 00-28 unchanged. Every name drawn exists in `src`, conftest or the standard library | Q2 | done |
| Q4 | ch29-30 `status = "drafted"` (`kind` stays `pattern`) | Q3 | done |
| Q5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly; runs its two experiments in fresh scratch copies with the filter it states; quotes that filter's complete output through `python3 scripts/host_ids.py filter`; and hands back the sources checked plus a per-paragraph claims table that names, for each static-test citation, the mutation that fails it | Q3, Q4 | done |
| Q6 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also a check that close bullets map one to one to objectives, and an excerpt check against decisions 4-7 | Q5 | done |
| Q7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r14.x` on main; notes-only release | Q6 | todo |

Reconciliation rows (step Q0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 160 | 29 | Concrete carriers register by a class keyword through `__init_subclass__`; the registry maps codes to classes, `gateway_for` books through it, an unknown code raises, and the registry is a read-only view | `test_every_registry_form_books_through_the_registered_carrier`, `test_the_registry_maps_each_code_to_its_gateway_class`, `test_gateway_for_books_with_the_registered_carrier`, `test_an_unknown_code_raises_unknown_carrier_error`, `test_the_carrier_registry_is_a_read_only_view`, `source: https://docs.python.org/3/reference/datamodel.html`, `source: https://peps.python.org/pep-0487/` |
| 161 | 29 | A duplicate code keeps the first class; an abstract intermediate is skipped; a concrete class without a code and an abstract class with one are refused; an unknown keyword is refused; the registry is unchanged after each refusal | `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry`, `test_a_duplicate_code_keeps_the_first_class`, `test_an_abstract_intermediate_class_is_not_registered`, `test_a_concrete_class_without_a_code_is_refused` |
| 162 | 29 | `inspect.isabstract` sees abstractness inside `__init_subclass__` before `__abstractmethods__` is set; `__set_name__` runs before `__init_subclass__`, and class decorators after | `test_isabstract_sees_abstractness_inside_init_subclass`, `test_set_name_runs_before_init_subclass_and_a_class_decorator_after`, `source: https://github.com/python/cpython/blob/3.15/Lib/inspect.py` |
| 163 | 29 | A forgotten manual registration leaves a carrier unavailable; a carrier module registers only when imported; a carrier under an abstract intermediate registers (fresh interpreter) | `test_a_forgotten_manual_registration_leaves_the_carrier_unavailable`, `test_a_carrier_module_registers_only_when_it_is_imported`, `test_a_concrete_carrier_under_an_abstract_intermediate_registers`, `source: https://python-patterns.guide/python/module-globals/` |
| 164 | 29 | A metaclass registry passes the same table; a second metaclass conflicts with `ABC` and `Protocol` bases, and one derived from `ABCMeta` doesn't; only a metaclass gives the class object operators | `test_every_registry_form_books_through_the_registered_carrier`, `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry`, `test_a_second_metaclass_conflicts_with_the_bases_metaclass`, `test_a_metaclass_derived_from_abcmeta_resolves_the_conflict`, `test_only_a_metaclass_gives_the_class_object_operators`, `source: https://docs.python.org/3/library/abc.html`, `source: https://docs.python.org/3/library/enum.html`, `source: https://peps.python.org/pep-0520/` |
| 165 | 29 | mypy checks a class keyword's type and, with a closed signature, its spelling; it doesn't check metaclass keywords, reports a metaclass conflict, refuses `Self` in a metaclass, types a call from a metaclass registry as `Any`, and ignores a metaclass `__call__`'s return type | `test_mypy_checks_the_type_of_a_class_keyword`, `test_mypy_reports_a_misspelt_class_keyword`, `test_mypy_does_not_check_metaclass_class_keywords`, `test_mypy_reports_a_metaclass_conflict`, `test_mypy_refuses_self_in_a_metaclass_new`, `test_mypy_types_a_class_called_from_a_metaclass_registry_as_any`, `test_mypy_ignores_a_metaclass_call_return_type`, `source: https://mypy.readthedocs.io/en/stable/metaclasses.html` |
| 166 | 30 | A `__getattr__` history loads nothing until a field is read, loads all fields once, keeps them in the instance dictionary and loads on iteration; a `cached_property` form passes the same table | `test_every_history_form_reads_the_loaded_fields`, `test_every_history_form_loads_once_for_every_field`, `test_nothing_is_loaded_until_a_field_is_read`, `test_a_loaded_history_reads_its_fields_from_the_instance_dict`, `test_iterating_a_history_loads_it` |
| 167 | 30 | Loaded fields refuse assignment; a misspelt field raises `AttributeError`, where a `.get(name)` form returns `None` | `test_every_history_form_refuses_assignment_to_a_loaded_field`, `test_every_history_form_raises_attribute_error_for_a_misspelt_field`, `test_a_getattr_that_returns_none_hides_a_typo` |
| 168 | 30 | `__getattr__` runs only when normal lookup fails; `__getattribute__` runs on every access | `test_getattr_runs_only_when_normal_lookup_fails`, `test_getattribute_runs_on_every_access`, `source: https://python-patterns.guide/gang-of-four/decorator-pattern/` |
| 169 | 30 | A `__getattr__` that reads a missing attribute recurses, including under `copy`, `deepcopy` and `pickle`; an allow-list, `object.__getattribute__` or `vars()` prevents it; the member's history copies before and after loading | `test_a_getattr_that_reads_a_missing_attribute_recurses`, `test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute`, `test_each_fix_keeps_getattr_out_of_recursion`, `test_copy_keeps_a_history_before_and_after_loading`, `source: https://docs.python.org/3/library/pickle.html`, `source: https://docs.python.org/3/library/copy.html` |
| 170 | 30 | Implicit special-method lookup bypasses both hooks; `__dir__` lists lazy fields without loading and enables the "Did you mean" hint; `hasattr` loads | `test_implicit_special_method_lookup_bypasses_getattr`, `test_dir_lists_the_lazy_fields_before_loading`, `test_a_misspelt_field_suggests_the_declared_name_through_dir`, `test_hasattr_loads_the_history`, `source: https://docs.python.org/3/library/functions.html` |
| 171 | 30 | A module `__getattr__` warns for a deprecated name and returns its replacement, raises for other names, and a module `__dir__` lists the old name | `test_a_deprecated_name_warns_and_returns_the_tracking_history`, `test_an_unknown_module_attribute_raises_attribute_error`, `test_module_dir_lists_the_deprecated_name`, `source: https://peps.python.org/pep-0562/` |
| 172 | 30 | mypy types an unknown attribute by `__getattr__`'s return type, keeps declared field types, accepts assignments `__setattr__` refuses, reports a typo on the `cached_property` form, and accepts names imported through a module `__getattr__` | `test_mypy_types_an_unknown_attribute_by_the_getattr_return_type`, `test_mypy_keeps_the_declared_field_types`, `test_mypy_accepts_an_assignment_that_setattr_refuses`, `test_mypy_reports_a_typo_on_the_cached_property_form`, `test_mypy_accepts_any_name_imported_through_a_module_getattr` |
| 173 | 29-30 | The "Build, run, observe" experiments behave as quoted | `run: Q5` |

Legacy rows at Q2:
- Row 11 gets `test_getattr_runs_only_when_normal_lookup_fails` and `test_getattribute_runs_on_every_access` ("verified (r14)").
- Row 12 gets `test_a_getattr_that_reads_a_missing_attribute_recurses` and `test_each_fix_keeps_getattr_out_of_recursion` ("adjusted (r14)": an allow-list that raises for names outside a fixed set also prevents recursion, evidence L).
- Row 13 gets `test_every_registry_form_books_through_the_registered_carrier`, `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry` and `test_a_second_metaclass_conflicts_with_the_bases_metaclass` ("verified (r14)").

## Corrections after the build
- Step Q6, narrow check (6126b3a, owner's choice after round 2): clean.
- Step Q6, round 2 (5052396): not ready on two small defects, both fixed: the ch29 card still said every test class is refused (two are abstract), and a round 1 replacement left an "It" in ch30 that read as the `cached_property` form. Everything else confirmed, including criteria 11, 18 and 22 and experiment (a) with the new filter.
- Step Q6, round 1 (Opus validation of 506d301): four blocking findings, all fixed: ch29 pointed the metaclass `__call__` mechanics back to the Singleton chapter, which defers them here (now says what that chapter does); ch30 said the proxy chapter measures special-method lookup (it quotes the rule); ch30 gave the wrong cause for mypy accepting `h.status = None` (it matches the declared type; only `h.anything = 1` depends on `__setattr__`); ch30 implied only the `__getattr__` form loads once (both do; the difference is what reads cost afterwards). Should-fix applied: a lost referent ("these four rows"), ch30's filter now adds `E {9}[^ ]` (experiment (a) gains two continuation lines; `E {3,9}` would pull in address lines), both close bullets mapped to their objectives, "conflicts with another metaclass" narrowed to "can conflict" (caption, figure, card), "without a message" (it raises `UnknownCarrierError`), experiment two described as swapping the check, `__prepare__`'s subject, an untested "works on a normal instance", a US spelling in link text, a missing test citation, an exact chapter title, the sidebar's claim about assistants, and cards, READMEs and conftest docstrings that overstated what's tested. Rows 160-173 verified. Nits applied except N5 (the `_SelfHealing` reduced-model excerpt stays as explain-by-example, labelled a reduced model) and N6 (accepted as illustration).
- Step Q5: ch29 2,249 words, ch30 1,913 words. Before quoting, the orchestrator made two ch30 subset assertions deterministic (`sorted(set(dir(history)) & {...}) == [...]`, and the same over `vars`), because a set of strings prints in a per-process hash order. Each experiment was run twice with identical output apart from the duration. ch29: experiment one (forwarded `**kwargs`) fails the unknown-keyword row and the misspelt-keyword static test (`0 == 1` is mypy's exit status); experiment two (`__abstractmethods__` for `isabstract`) fails 7 tests, `HALF` leaking into later registry assertions. ch30 widened the plan's filter to `E {3,7}[^ ]`, because pytest prints `RecursionError` with `E` and three spaces; experiment (a) (no `__dir__`) fails 2 tests, experiment (b) (no allow-list) fails 4, two of them by `RecursionError`. ch30 dropped the plan's unverified "ghost variant" attribution. Fluent Python, GoF and PoEAA are cited at book level (the plan's fallback).
- Step Q3: both figures drawn; figures 00-28 byte-identical; 31 entries in `diagrams.yml`. Captions reworded from the drafts to what tests back (38 and 40 words with the prefix). Figure 29: the metaclass comparison is a muted box with no identifier and "its own registry" (the fixture keeps `_META_CARRIERS`, not the same registry); `type.__new__` is drawn creating the class and then calling `__set_name__` and `__init_subclass__`; the abstract branch reads "is not registered" and the edge to the registry is labelled "if concrete". Figure 30: the plan's "iter(), len(): bypass both" box was false for `TrackingHistory`, which defines `__iter__`; it is now a muted box about a class that relies on forwarding, and "bypass both hooks" is dropped (only the `__getattr__` bypass is tested). The `__prepare__` box and the body-before-`type.__new__` order are data-model behaviour with no test, and no caption claims them.
- Step Q1b: member `dynamic-attributes` (package `dynamic_attributes`, no `[tool.*]` table), 26 test functions, 40 cases (`test_history.py` 7/17, `test_lookup.py` 11/15, `test_module.py` 3/3, `test_static.py` 5/5). mypy prints `Revealed type is "object"` (not `"builtins.object"`), so test 22 asserts that. The `deepcopy` recursion needs a loader that raises `AttributeError` for names other than its field: with a loader that answers every name, `deepcopy` fails first with `TypeError: 'str' object is not callable`; test 11 uses `_load_by_name`, and `copy`, `deepcopy` and `pickle` all give `RecursionError`. Prose must say the loader knows only its field. Test 19 also pins `stacklevel=2` through the warning's filename. Test 9 can't assert a single `consignment_id` hook entry, because the load reads `self.consignment_id` through `__getattribute__`. Deleting `__iter__` fails only test 7. All other evidence P messages matched.
- Step Q2: rows 160-172 resolve to existing tests; legacy rows 11 and 13 verified, row 12 adjusted (an allow-list also prevents recursion); the dated r14 note is in `_plans/spikes.md`.
- Step Q1a: member `carrier-registry` (package `carrier_registry`, no `[tool.*]` table), 24 test functions, 35 cases (`test_registry.py` 14/24, `test_metaclass.py` 3/4, `test_static.py` 7/7); the plan's 23/33 miscounted `test_registry.py`. Deleting the abstract-with-code branch gives `DID NOT RAISE` only (the abstract path returns without registering); `HALF` registers only in experiment (b), where `isabstract` becomes the `__abstractmethods__` check (7 failures, among them `assert ['AIRCO', 'FASTLINE', 'HALF']`). Experiment (a)'s runtime message names the test's class: `'Refused.__init_subclass__() takes no keyword arguments'`. A deletion that stops a refusal lets a test class leak into the registry and fail later tests; green runs never leak. Fixture types and `_MetaCarrierBase` are imported under `TYPE_CHECKING` from conftest; test 17 gets the class from a `meta_carrier_base` fixture. Each static test fails on its own mutation of the credited code.

(None yet. The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.)

Lessons carried from r11-r13, which this plan applies up front:
- **Counts.** Per-file counts are summed from the spec, and the pytest summary line wins (r13 P1a: 43, not 44). ch29's `test_static.py` count and ch30's case total are flagged above for recounting.
- **Members.** The project is named after its package, with no `[tool.*]` table (r13 P1a).
- **Shared tables.** They live in the test module, not in conftest (`from conftest import` fails under importlib mode; r13 P1a).
- **Determinism.**
  - Assertions that can fail compare sorted names, never a set repr of classes (r13 P5).
  - Experiment filters must match pytest continuation lines as `E` plus 9 spaces (r13 P6).
- **mypy.** It narrows after `assert` and flags later lines `[unreachable]`, so values are read through small helpers (r11 M1a, M1b).
- **Static tests.** Every exit-0 static test asserts `_codes(stdout) == set()` and a runtime half (r13 P6).
- **Prose repairs.**
  - A repair can make a dependent sentence false, so the validator re-reads the paragraph and the close (r12 N6).
  - A scope word needs a test that covers the whole scope (r11 owner check: "after both" was false).
- **GoF and Rhodes.** GoF paraphrases from memory are checked at validation (r11 M5, r12 N5). Rhodes's first name is Brandon (r11 M6).
- **Addresses** in quoted output are masked by a stated `sed` (r11 M6).

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs, and once with the test files in reverse order (`tests/test_static.py` first), with the same pass count.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch"` over both members' `tests` prints nothing.
   - `grep -rn "print("` over both members prints nothing.
   - `grep -rnE "metaclass|__prepare__|\*\*kwargs|__subclasses__|\bAny\b|cast\(|TYPE_CHECKING|__getattr__"` over `examples/29-*/src` prints nothing.
   - `grep -rnE "__getattribute__|cached_property|TYPE_CHECKING|\bAny\b|cast\(|metaclass|__init_subclass__|Gateway"` over `examples/30-*/src` prints nothing.
   - No ch29 test outside `_run_isolated` code strings defines a class with `code="FASTLINE"` or `code="AIRCO"` that isn't expected to be refused (checked by reading; `grep -n 'code="' examples/29-*/tests` is reviewed in the Q1a handback).
3. Every test name cited in rows 160-172 and rows 11-13 is defined exactly once across `examples/*/tests`.
4. Every mypy-API test asserts:
   - its exit status;
   - an exact code set, through the anchored `_codes` regex;
   - no line number and no optional note.
   
   Also:
   - `grep -c "_codes("` is at least 6 in ch29's `test_static.py` and at least 5 in ch30's;
   - every `# type: ignore[...]` and `# noqa` names a code;
   - there are no unused ignores.
5. **Every static test can fail on a mutation of the thing its prose credits.** The Q1a/Q1b handback lists each static test with its credited thing, runs the named mutation in a scratch copy and quotes the failing line. Every exit-0 test also asserts the hazard at run time. A test whose mutation doesn't fail it is rewritten, or its prose claim narrowed, before Q5.
6. Deletion tables (Q1a, Q1b): every row, deleted in a fresh scratch copy whose imports come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed", and executor-check rows are resolved or moved to Corrections.
7. Every "silently", "only when imported", "never runs again", "recurses", "loads" or "unchanged" sentence names a test with a deletion-table row (or experiment) whose mutation makes it fail. Scope words ("every", "all", "only", "never", "both") name the test that covers the whole scope, or are cut.
8. ch29-30 are drafted, with:
   - one figure each;
   - captions of 20-45 words including `Figure N.1:`;
   - at most 2,500 prose words each by `validate.py` (an error above; a warning below 1,900 is reported, not padded).
9. Spine and sidebar:
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `grep -c "^## When not to use it"` is 1 and `grep -c "^## How it works"` is 0 in each.
   - `## What you can do now` is the second-to-last H2, directly before `## For deeper coverage`, with as many bullets as the learning objectives.
   - Every backticked token in the close appears earlier in the chapter.
   - Each sidebar:
     - opens with a bold lead and holds a nested `>` prompt;
     - has at most two non-quoted paragraphs;
     - matches no `\bCheck(:| that| three| four| whether)`;
     - is at most 120 words;
     - names only identifiers present in the chapter, its `src` or the standard library.
   - `validate.py` passes the `pattern` spine.
10. Thesis:
    - ch29 says the metaclass registry dissolves (`dissolv` at least 1), names what remains (refusal, imports, test isolation), and gives the one honest metaclass case.
    - ch30 says Proxy is disambiguated (`disambiguat` or "no surrogate" at least 1) without calling `TrackingHistory` a proxy object.
11. Non-overlap and pointers:
    - ch29 points to "The three-way split: dissolve, survive, disambiguate", "Factory Method and Abstract Factory", "Singleton: module, Borg, and metaclass", "Decorators done right", "Descriptors and properties" and "singledispatch: the Visitor the language gives you" by title.
      - `__call__` appears in at most one paragraph.
      - No `_SingletonMeta`, `TARIFF` or `document_kind` appears in `_docs/29-*.md`.
    - ch30 points to "Decorator the pattern vs @decorator the syntax, and Proxy", "Descriptors and properties" and "Singleton: module, Borg, and metaclass" by title.
      - `grep -nE "CarrierGateway|_ForwardingGatewayProxy|Called when the default attribute access fails|may still be bypassed"` over `_docs/30-*.md` prints nothing.
      - No PEP 810 sentence that ch18 quotes is re-quoted.
    - Neither chapter builds a dispatch table or describes any other stub.
12. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, the cards, the specs and the SVGs, with `--stats` reviewed against the house-voice rubric (rules 94-96).
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|memoiz)"` over prose (quotations and code excluded) prints nothing.
    - No paragraph after an excerpt re-narrates its identifiers.
13. No em-dash or en-dash in any file touched in r14, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. A quoted dash is written "[en dash]" in plans and is never quoted in chapters (the enum and data-model sentences stop before theirs).
14. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Smalltalk|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/29-*.md`, `_docs/30-*.md`, the new READMEs and the cards prints nothing.
15. Idiomatic scan: 0 ban-tier in both members.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`. Object addresses are masked by a stated `sed` filter.
17. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Each experiment:
    - runs in a fresh scratch copy, changes one thing, and is deleted afterwards;
    - has its exact filter command stated in the chapter, matching pytest's `E` plus 9 spaces continuation lines where a message is quoted;
    - is quoted as that filter's complete output, followed by `uv run mypy --strict src tests`.
19. Attribution:
    - ch29 credits PEPs 487, 3115 and 520 by author, Rhodes by name and CPython's `inspect` source, and quotes the data model, abc, enum and mypy sentences exactly.
    - ch30 credits PEPs 562 and 810 by author and Rhodes by name, and quotes the data model, built-ins, copy and pickle sentences exactly.
    - GoF and Fowler claims appear only if verified. Every book cited is already in `bibliography.html`.
20. Claims:
    - Every factual sentence in ch29-30 maps to a named test, `run: Q5` or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0, with rows 160-173 resolved and each `source:` URL present in its chapter.
    - No `run: N*` or `run: P*` token appears in rows 160-173.
    - Any prose version mention (3.6, 3.14) is preceded by "since", "before", "until" or "new in", so `check_stale_versions` passes.
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 31 entries, and `diagrams/0*-*`, `diagrams/1*-*` and `diagrams/2[0-8]-*` are unchanged.
22. Reconciliation rows 160-173 are `verified` or `adjusted` with evidence. Rows 11 and 13 are `verified (r14)`, and row 12 is `adjusted (r14)`.
23. Deterministic:
    - No test depends on wall time, the environment, memory addresses, test order or iteration order it didn't create.
    - No test process registers a carrier on `CarrierBase`.
    - Recursion tests assert only the exception type.
    - `filterwarnings = ["error"]` is still in the root config.
24. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.
25. Every self-contained mypy snippet that stands for code is named in the prose as a reduced model: ch29 tests 21-25; ch30 test 25.
26. Test counts in prose and handbacks come from the pytest summary line of a fresh run.
27. Every comparison form said to share a table is a conftest fixture param (`registry_form`, `history_form`), and each chapter shows at most one comparison excerpt.
28. Every figure label that names code exists in that chapter's `src`, conftest or the standard library, checked by grep at Q3. The labels are `CarrierBase`, `__init_subclass__`, `__set_name__`, `__prepare__`, `type.__new__`, `registry`, `DuplicateCarrierError`, `FastlineGateway`, `_CarrierMeta`, `TrackingHistory`, `__getattr__`, `__getattribute__`, `vars`, `load`, `events`, `status`, `last_port`, `__dir__`, `iter`, `len` and `copy`.
29. Repo-relative paths only in this plan and every r14 file: `grep -rnE "/home/|/Users/"` over the files touched in r14 prints nothing.

## Risks

- **Predicted messages and counts.** Every iteration since r05 mispredicted something. Expect differences in these places:
  - whether ch29 experiment (b)'s registered `HALF` changes later tests in collection order;
  - the exact `E {9}` lines of ch29 experiment (a);
  - which tests ch30 experiment (b) fails, and how the `RecursionError` shows in the filter;
  - whether tests 6 and 17 (ch29) need a coded ignore;
  - mypy's output on a module `__getattr__` (ch30 test 26, not run at planning);
  - pickling by reference from a test module under importlib mode (ch30 test 11[pickle]).

  Tests match codes and stable substrings only.
- **Test pollution in ch29.** The isolation rule depends on every in-process refusal raising before insertion. A deletion that removes a refusal registers a test class for the rest of the run. That's acceptable inside a deletion experiment, never in a green run. Criterion 2's review of `code="` lines is the guard.
- **The `isabstract` fallback is an implementation detail of `inspect`.** It's been there since well before 3.14 and is present on the 3.15 branch, but it's a source comment, not a documented guarantee. Prose credits the source and says "on 3.15.2", and test 10 would catch a change.
- **mypy behaviour can move.** These all come from mypy, and the prose says "mypy 2.4.1" for each:
  - unchecked metaclass keywords;
  - the ignored metaclass `__call__` return;
  - `Any` from a metaclass-typed registry;
  - `object`-typed typos through `__getattr__`;
  - accepted assignments through `__setattr__`.
- **The "Did you mean" wording is the interpreter's.** It changed format in recent releases (`'.status' instead of '.stauts'`). Test 17 matches the full suffix as observed on 3.15.2, and the prose says so. If it moves, only that test and one sentence change.
- **Not upstream defects, kept out of prose as defects.** mypy's handling of a metaclass `__call__` return and of a metaclass `__getitem__` are long-standing limitations, consistent with the mypy docs' "does not and cannot understand arbitrary metaclass code". `object.__init_subclass__`'s message naming the subclass is a diagnostic wart. None is filed. If the owner wants one reported, it goes through `lgtm-issue-reporting`, and the chapter states only observed behaviour.
- **Ruff on tests.** B009 may flag `getattr(module, "LazyTrackingHistory")` (ch30 test 19): use `importlib.import_module` and attribute syntax under `pytest.warns`, or a coded `# noqa: B009` with a reason. A class statement inside `pytest.raises` passes (evidence E). E731 forbids assigned lambdas, so loaders are `def`s.
- **mypy narrowing in tests** (r11). After `assert not vars(h).keys() & {...}`, later reads may be flagged `[unreachable]`. Read through small helpers.
- **Word budgets.** Both chapters run close to 2,500.
  - ch29 shrinks first: the `__prepare__` sentence, then the PEP 487 plugin quotation, then the `__call__` sentence to a clause.
  - ch30 shrinks first: the `hasattr` paragraph to one sentence, then the module `__dir__` sentence, then the Rhodes quotation.
  - Their tests stay.
- **Stub pointers.** It's tempting to write "dict dispatch would do this" or "EAFP says catch `AttributeError`". Criterion 11 forbids describing those chapters.
- **New supporting names.** If the owner declines `CarrierRegistrationError`, `gateway_for` or the `LazyTrackingHistory` alias, Q1a or Q1b waits for the replacements. Nothing else moves.
- **Liquid.** The f-strings in excerpts contain single braces only. Any `{{` needs `{% raw %}`.
- **`uv.lock` race.** Q1a and Q1b are sequenced.
