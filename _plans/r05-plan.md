---
title: "r05 plan: Python 3.15, then chapters 9-11 (Part 4, the Python substrate)"
order: 5
output: false
render_with_liquid: false
---

# r05: move to Python 3.15.2, then chapters 9-11

Opus-planned 2026-11-04. Branch `release/r05`. Source of truth for r05 scope, criteria and status. Executors never edit this file; the orchestrator updates the status board. Part A (the interpreter move) is done, gated and checkpoint-committed before any chapter work starts.

## Open user decisions (recommendations included)

1. **Chapter 11 is not a pattern chapter, and it gets one sidebar.** It has no bucket (domain row `n.a.`), stays `kind = "hands-on"`, has no `## When not to use it` heading, and carries exactly one `ai-sidebar` inside `## When a test proves less than it seems`. That matches r04 decision 1 ("one ai-sidebar per chapter"). **Recommend: yes.** The alternative is no sidebar, which breaks parity with chapters 5-8 and drops the most useful review checklist in the book.
2. **Credit Null Object to Woolf, and add two bibliography rows.** Bobby Woolf, "Null Object", in *Pattern Languages of Program Design 3*, eds. Robert C. Martin, Dirk Riehle, Frank Buschmann (Addison-Wesley, 1998; ISBN 9780201310115). Chapter 9 leans on it, and chapters 2 and 3 already use the idea uncredited ("the later pattern literature"). Also add Brian Okken, *Python Testing with pytest*, 2nd ed. (Pragmatic Bookshelf, 2022), which chapter 11 cites. **Recommend: yes.** That means two `bibliography.html` rows, a one-clause credit retrofitted into chapters 2 and 3 (step A5), and new hub `books.yml` entries.
3. **Use the 3.15 idioms in new chapters only.** `frozendict` (PEP 814) and `sentinel` (PEP 661) appear in chapters 9-11. The `MappingProxyType` tables in the chapter 2, 3, 5 and 6 examples and excerpts are not rewritten. A read-only view and a frozen value are different things, the excerpts stay correct, and a rewrite would reopen four verified chapters. **Recommend: going forward only.** Revisit at the r25 QA sweep.

## Planning evidence

All runs were read-only:
- Runtime: `~/.local/bin/python3.15 -I -c ...`, Python 3.15.2 (endoflife.date: 3.15.2 released 2026-10-25; 3.15.0 released 2026-10-09).
- mypy: `uv run --no-project --python 3.15.2 --with mypy==2.4.1 python -I -c "mypy.api.run(['--strict','--warn-unreachable','--cache-dir','/dev/null','--no-error-summary','-c',SNIPPET])"`.
- Run mypy from a directory outside the repo. Inside the repo, the root `[tool.mypy] python_version = "3.14"` applies. Example: `frozendict` reads `[name-defined]` there and passes outside. Step A1 fixes this.

Each item below becomes a test or a reconciliation row; the plan relies on nothing else.

Runtime, unchanged from 3.14.10, so chapters 0-8 keep their wording if fresh runs agree:
- `cannot use 'W' as a set element (unhashable type: 'W')`, `cannot use 'W' as a dict key (unhashable type: 'W')`, `unhashable type: 'W'`.
- A class with `__module__` set outside `__main__` reads `cannot use 'tests.test_aliasing._MutableSlotId' as a dict key (unhashable type: 'M')`. The first name is module-qualified, the second is `__name__`.
- `cannot create weak reference to 'S' object`; `FrozenInstanceError cannot assign to field 'a'`; `mutable default <class 'list'> for field xs is not allowed: use default_factory`.
- `KO.__init__() takes 1 positional argument but 2 were given`. The 3.15 "argument" wording fix (gh-133382) does not touch it.
- `Cannot overwrite attribute __lt__ in class Bad Consider using functools.total_ordering`; `unsupported operand type(s) for *: 'decimal.Decimal' and 'NoR'`.
- `'<=' not supported between instances of 'LtOnly' and 'LtOnly'`; `unsupported format string passed to R.__format__`; `'<' not supported between instances of 'X' and 'X'`; `'R' object is not subscriptable`; `object of type 'L' has no len()`.

Runtime, new on 3.15 or needed by chapters 9-11:
- `frozendict` and `sentinel` are builtins. `frozendict(FASTLINE=1)["AIRCO"] = 2` raises `'frozendict' object does not support item assignment`. It is a `Mapping` and not a `dict`, and equal frozendicts hash equal.
- A sentinel is truthy, `copy.copy(S) is S`, `S < S` raises `'<' not supported between instances of 'sentinel' and 'sentinel'`, and `S | None` is a `typing.Union`.
- `@runtime_checkable` checks names only: a `book(self) -> int` and a `book = 3` attribute both pass `isinstance`. A data protocol under `issubclass` raises `Protocols with non-method members don't support issubclass(). Non-method members: 'code'.`
- New in 3.15 (gh-132604): a Protocol that inherits a runtime-checkable Protocol without its own decorator emits `DeprecationWarning: <class '__main__.Sub'> isn't explicitly decorated with @runtime_checkable but it is used in issubclass() or isinstance(). ... This will raise a TypeError in Python 3.20.` on `isinstance`.
- An undecorated Protocol gives `Instance and class checks can only be used with @runtime_checkable protocols`; `Protocols cannot be instantiated`.
- An ABC subclass missing a method: `Can't instantiate abstract class Half without an implementation for abstract method 'book'`. An explicit subclass of a Protocol instantiates at runtime and inherits the `...` body, which returns `None`.
- A frozen slotted kw_only dataclass can be subclassed with an extra field (`HazmatConsignment(id=..., un_number="UN1203")`). An untyped quoter given a plain `Consignment` raises `'Consignment' object has no attribute 'un_number'`.
- contextlib on 3.15 (gh-125862): a `@contextmanager` used as a decorator on a generator function holds the context across iteration: `['created', 'enter gen', 'row1', 'row2', 'exit gen']`. On 3.14.10 the same code gives `['enter gen', 'exit gen', 'created', 'row1']`.
- `ExitStack` exits in reverse order. A `@contextmanager` without `try/finally` skips cleanup on an exception (`['open']`). An `__exit__` returning `True` swallows the exception.
- `open(p, "w").encoding == "utf-8"` with no `encoding=`, because PEP 686 makes UTF-8 the default in 3.15. This depends on the environment (`PYTHONUTF8=0`), so it is a source claim, not a test.
- unittest.mock: a plain `Mock()` accepts `m.qoute("c")`. `m.assert_called_once_wiht(...)` raises `'assert_called_once_wiht' is not a valid assertion. Use a spec ...`, so the typo example must not use an `assert*` name.
- `Mock(spec=Gateway).qoute` raises `Mock object has no attribute 'qoute'`, but `.quote()` with no arguments is accepted. `create_autospec(Gateway, instance=True)` on a Protocol works: `.quote()` raises `missing a required argument: 'consignment'`, and a positional-only parameter passed by keyword raises `missing a required positional-only argument: 'consignment'`.
- `MagicMock(spec=...)` accepts wrong arity. `seal()` blocks new attributes.
- `module.__package__` does not warn yet, but 3.15 deprecates it for removal. `examples/06-.../tests/test_dip.py:35` uses it.

mypy 2.4.1 on 3.15.2:
- Variance is inferred for `class Quoter[T: Consignment](Protocol)`. `price_all(HazmatQuoter())` against `Quoter[Consignment]` is `[arg-type]` with `Following member(s) of "HazmatQuoter" have conflicts`. `GeneralQuoter` is accepted as `Quoter[HazmatConsignment]`.
- A callback Protocol with `/` accepts a function whose parameter name differs. Without `/` the result is `[assignment]` with the note `"KwRule.__call__" has type "def __call__(self, consignment: Consignment) -> int"`.
- An unguarded `find_gateway(code).book(...)` is `[union-attr]`. Walrus, `match`/`case None`, early return, `assert g is not None` and the conditional expression all narrow (exit 0).
- `Half()` on an ABC: `[abstract]` `Cannot instantiate abstract class "Half" with abstract attribute "book"`. `Gateway()`: `[misc]` `Cannot instantiate protocol class`. An explicit Protocol subclass with no body: `[abstract]` (runtime disagrees). `@override` on a misspelled method: `[misc]` `Method "boook" is marked as an override, but no base method was found with this name`.
- A sentinel narrows with `is`. Forgetting its branch is `[union-attr]` twice: `Item "None" of "str | ACCOUNT_DEFAULT | None"` and `Item "sentinel" of ...`. mypy does not report a sentinel whose name differs from its variable, although PEP 661 says checkers should, so the prose claims nothing about it.
- `frozendict` is typed: `F["AIRCO"] = 2` is `[index]` `Unsupported target for indexed assignment`. `lazy import json` type-checks, and attribute errors on the module are still reported.
- `Mock()`, `Mock(spec=Tracker)`, `MagicMock(spec=Tracker)`, `create_autospec(...)` and `mocker.create_autospec(...)` are all accepted where an unrelated Protocol is expected (exit 0).
- `reveal_type(mocker.create_autospec(...))` is `unittest.mock.MagicMock | unittest.mock.AsyncMock | unittest.mock.NonCallableMagicMock`, not `Any`. The reason is typeshed's `class NonCallableMock(Base, Any)`, whose comment reads exactly: `# We subclass with "Any" because mocks are explicitly designed to stand in for other types,` / `# something that can't be expressed with our static type system.` So the book's wording becomes "assignable to every type", not "is `Any`".
- `assert_type(x, int)` on a `str` is `[assert-type]` `Expression is of type "str", not "int"`.
- `__exit__` typed `-> None`: code after a `with` whose body raises is `[unreachable]` under `--warn-unreachable`. Typed `-> bool`: no error.
- `@contextmanager` targets type as the yielded type; `ExitStack.enter_context` returns it.
- A fake missing `book` in a `Mapping[str, Gateway]` argument is `[dict-item]` with no member note. In an annotated assignment it is `[assignment]` with `"QuoteOnly" is missing following "Gateway" protocol member:` / `book`.
- ruff 0.17.3: `sentinel` is `F821` under `py314` and clean under `py315`. `lazy import` passes check and format under `py315`.

Repo facts:
- Chapters 9-11 are `kind = "hands-on"`, `has_example = true`, `status = "stub"`, part 4. Their stubs have a placeholder `## How it works`.
- The chapter 9 stub `description` is backwards ("the Null Object that replaces a None carrier").
- Reconciliation rows run 1-46; r05 adds 47-64. `_data/diagrams.yml` has nine entries.
- The mypy-API helpers in members write their own `mypy.ini` (`mypy_path` only). Snippets are checked against the running interpreter's version, and the helper does not pass `--warn-unreachable`.
- `pytest_plugins` in a member conftest is not top-level, so `pytester` is not used.
- Already taught and not to be repeated:
  - The bare `find_gateway` `[union-attr]` demonstration ("What 1994 assumed, and what Python dissolves", "The three-way split").
  - The names-only `runtime_checkable` caution and the Protocol-vs-ABC one-paragraph witness (the same two chapters).
  - ISP-sized Protocols and `create_autospec` of the wrong Protocol passing mypy ("ISP, DIP, and dependency injection without a framework").
  - Negative fixtures, typed ignores and `mypy.api` witnesses are used throughout chapters 5-8 but never explained.
- Hub:
  - `_data/sites.yml` synopsis says "idiomatic Python 3.14", so **a hub PR is needed**.
  - `books.yml` lacks `design-patterns-with-python` in `referenced_by` for Meszaros and *The Pragmatic Programmer*, and has no entry for Meyer's *Object-Oriented Software Construction*, although all three are in `bibliography.html` (pre-existing gaps that the PR closes).

## Python 3.15 changes against chapters 0-8

| Change | Touches | Action |
| --- | --- | --- |
| Error messages: unhashable, weakref, frozen, kw_only, operand, ordering, format (unchanged) | ch7, ch8 tests and quoted output | Re-run and re-quote (A4); expect no wording change |
| "Did you mean" suggestions across members, foreign method names (gh-146406) | No AttributeError output is quoted in ch0-8 | A4 confirms by grep; none expected |
| gh-133382 "argument" wording | ch8 kw_only (`positional argument`) | Verified unchanged |
| PEP 649 deferred annotations (since 3.14) | ch0 line 128, spike 012 comment | Reword as history: "Since Python 3.14, ..." (the one allowed hit) |
| dataclasses: generated `__init__` annotations drop internal names (gh-137530) | No test inspects them | None (A4 grep `__init__.__annotations__` = 0) |
| `runtime_checkable` inheritance deprecation (gh-132604) | ch3 uses decorated Protocols only; ch6 composite never `isinstance`d | None; taught in ch9 |
| PEP 686 UTF-8 default | No ch0-8 code opens files | None; ch10 keeps explicit `encoding="utf-8"` |
| `__package__`/`__loader__` deprecated for removal | `examples/06-.../tests/test_dip.py:35` | `module.__spec__.parent` (A1); not quoted in prose |
| PEP 814 `frozendict` | `MappingProxyType` tables in ch2/3/5/6 | Decision 3: unchanged |
| PEP 661 `sentinel` | ch2 "Absence in the type" | None; ch9 teaches it |
| PEP 810 `lazy import` | ch2 "Modules" says the module is built "when first imported" | Still true for eager imports; note for the Singleton chapter (r08), not now |
| `singledispatchmethod` changes | Future singledispatch chapter (reconciliation row 9) | Row 9 wording "on the pinned interpreter"; spike 012 re-run in A1 |
| Removals (`typing.ByteString`, `no_type_check_decorator`, NamedTuple kwargs) | Unused (grep) | None |

3.15 features chapters 9-11 use: `sentinel` and `frozendict` (ch9), the runtime_checkable inheritance deprecation (ch9), the `@contextmanager`-as-decorator change over generators (ch10), and `filterwarnings = ["error"]`, explained in ch11 as the way a 3.15 deprecation fails the build. Rejected for now: `TypeForm` (PEP 747), `disjoint_base` (PEP 800), closed `TypedDict` (PEP 728), `lazy import` (it belongs with module singletons), comprehension unpacking (PEP 798).

## Plans and history

- **Living, edited with a dated note "2026-11-04 (r05): Python 3.15.2":**
  - `CLAUDE.md`.
  - `_plans/r01-build-plan.md` "Verified toolchain" table only: CPython row `3.15.2 (released 2026-10-25)`, mypy row `2.4.1 (supports 3.15)`, date checked 2026-11-04. The table is validator-checked (`PLAN_REL`). One dated note line goes under the table; the r01 steps and criteria stay as written.
  - `_plans/shipping-domain-model.md` (lines 13 and 137; rows 9-11 at step 0).
  - `_plans/reconciliation-plan.md` (row 9 wording; rows 47-64; a dated re-run note under the table, and on row 44 "(unchanged on 3.15.2)" only if A4 confirms it).
  - `_plans/iteration-plan.md` (PDP-109..111 active; dated note).
  - `_plans/spikes.md` (dated note: spike tests re-run green on 3.15.2; the recorded GIL bench and S4a outputs remain 3.14.10 evidence; the GIL chapter re-measures).
- **Untouched history:** `_plans/r02-plan.md`, `r03-plan.md`, `r04-plan.md`, `spikes/S4a-findings.md`, `spikes/feature-spikes/bench/gil_bench.out.txt`, and the r01 steps and criteria rows.
- **Notion PRD** "Target Python 3.14" is updated to 3.15 by the orchestrator.

## Approach

- **Chapter 9 dissolves Null Object and disambiguates Protocol vs ABC.**
  - Null Object force: a caller asking for a collaborator that may not exist must not proceed as if it did. It used to be resolved by a do-nothing stand-in. In Python, `X | None` resolves it without the pattern's structure, and the thesis wording is used once: "a feature resolves the force without the pattern's structure".
  - Chapter 9 builds on the bare demonstration in "What 1994 assumed, and what Python dissolves" (pointer by title, no re-quote) and goes further:
    - the narrowing forms;
    - the stand-in that loses a booking, which mypy accepts;
    - where a null object stays right (`no_discount`);
    - a 3.15 `sentinel` when `None` is itself a meaningful value.
  - Disambiguation: "interface" means a Protocol (structural, checked where used) or an ABC (nominal, checked at construction, shares code). The two aren't rivals: `AircoGateway` inherits `CarrierBase` and still satisfies `CarrierGateway` by shape.
  - Non-overlap: ISP-sized Protocols and consumer ownership are pointed to "ISP, DIP, and dependency injection without a framework" in one sentence. The mock-as-`Any` caveat is not restated (it lives there and in chapter 11). `CarrierBase` shows no hook methods; Template Method gets one pointer.
- **Chapter 10 survives: Resource Acquisition.**
  - Force: a resource must be released on every exit path, and what "release" means is a decision.
  - `with` and PEP 343 give the call sites (`__exit__` runs on every path), so the boilerplate dissolves. The pattern survives because the author still decides:
    - what release means (close, commit or discard);
    - whether an exception propagates or is swallowed;
    - the order across several resources.
  - `ManifestWriter` writes to a `.partial` file and commits by `Path.replace` only on success.
  - The book uses "resource acquisition" as a descriptive label and does not attribute the name to POSA3. No cross-language comparison.
  - Non-overlap: `async with` gets one pointer to "asyncio and the patterns". Generators stay trivial (generators belong to "Iterator: generators and the iterator protocol"). The decorator form gets one pointer to "Decorator the pattern vs @decorator the syntax, and Proxy" and says plainly that this is the syntax.
- **Chapter 11 is the testing baseline, bucket n.a. (decision 1).** It teaches what chapters 0-8 use but never explain, so later chapters can point to it:
  - the book's evidence method (claim, witness test, negative fixture, deletion table, scratch-copy experiment);
  - fixtures as dependencies by name, factory fixtures, `yield` teardown, and `pytest.param` ids;
  - the double matrix (fake, `Mock`, `Mock(spec=)`, `create_autospec`) against unknown names, wrong signatures and mypy, with the vacuous-assertion failure;
  - deterministic time (injected clock, tie-break);
  - process state with `monkeypatch.context` for the environment only;
  - mypy as a test (member runs over `tests/`, `assert_type`, typed ignores under `warn_unused_ignores`, the API helper);
  - root configuration that refuses silence.
  
  It doesn't repeat chapter 6's first autospec demonstration (pointer by title), the full pytest or mock reference (pointers to "pytest reference" and "Mocking reference: unittest.mock and pytest-mock"), the Meszaros taxonomy beyond the four double names (pointer to "xUnit test patterns (Meszaros)"), or monkeypatch as a seam (pointer to "Seams in Python: monkeypatch, injection, and duck typing").
- **One uv member per chapter:**
  - `examples/09-protocol-and-structural-typing` (project `structural-typing`, package `structural_typing`);
  - `examples/10-context-managers` (project `context-managers`, package `context_managers`);
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy` (project `testing-baseline`, package `testing_baseline`).
  
  Each is standalone, re-declares its own small domain module and imports no other member.
- **mypy witnesses** copy the r04 helper (own `mypy.ini`, `--strict`, `--cache-dir os.devnull`, `--no-error-summary`). Chapter 10 adds `--warn-unreachable` for its reachability snippet. Each witness asserts exit status, an exact `_codes()` set and one or two substrings. Typed ignores in tests are static witnesses.
- **Negative witness rule.** Every check in model code has a test that fails when the check is deleted, proven by the deletion tables in steps 1a-1c.
- **Global state.** No `mock.patch`/`mocker.patch` anywhere. `monkeypatch` only in chapter 11's `test_environment.py`, and only `setenv`/`delenv` inside `monkeypatch.context()`. No module-level mutable tables.

Rejected:
- `pytester` for teardown and xfail witnesses (plugin registration across the workspace). Those claims are cited from the pytest docs and reproduced as experiments instead.
- `NullGateway` in `src/`; it is a negative fixture.
- `@runtime_checkable` on the src Protocol, because nothing in src calls `isinstance`. The checked copy is a test fixture.
- `ABC.register`, which adds no witness the chapter needs.
- Teaching `mocker.patch`.
- A claim that a sentinel name mismatch is reported (mypy doesn't).
- An encoding test that depends on `PYTHONUTF8`.
- `lazy import` in chapters 9-11.
- Rewriting the earlier `MappingProxyType` tables (decision 3).

## Part A: the move to 3.15.2 (steps A1-A6, before any chapter work)

A1, interpreter and pins (one executor):
- `.python-version` becomes `3.15.2`.
- Root `pyproject.toml`: `requires-python = ">=3.15"`, ruff `target-version = "py315"`, mypy `python_version = "3.15"`.
- `requires-python = ">=3.15"` in `examples/00-prerequisites`, `03-three-way-split`, `05-srp-ocp-lsp`, `06-isp-dip-and-di-without-a-framework`, `07-the-data-model`, `08-dataclasses-and-value-semantics` and `spikes/feature-spikes`.
- `uv lock`, then `uv sync --locked --all-packages`. Pins are unchanged: pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3, mypy 2.4.1, uv 0.13.7. CI is unchanged (`uv python install` reads `.python-version`).
- `test_dip.py`: `module.__package__` becomes `module.__spec__.parent` (with a `None` guard if mypy needs it).
- Try `filterwarnings = ["error"]` in `[tool.pytest.ini_options]`. If any warning fires, record it in the handback and stop for an orchestrator call: no blanket ignore, and a targeted ignore needs a reconciliation row.
- `bash scripts/verify.sh` green three consecutive times; the handback has the pytest header line.

A2, scripts (one executor):
- `check-prereqs.sh`: the header comment says "CPython at the `.python-version` pin". The not-found row reads `no Python ${py_pin%.*} found (uv python install $py_pin)`, so no version is hard-coded.
- `validate.py`:
  - Self-test fixtures move from `3.14.x` to `3.15.x`.
  - New `check_stale_versions`: in reader-facing files, flag `Python 3.N`, `python3.N` and `3.N.M` where N isn't the pinned minor, unless the match is preceded within 16 characters by `since `, `before `, `until ` or `new in `. Self-tests cover a hit, a "Since Python 3.14" pass, and `3.12` after "new in".
  - New claims audit: `validate.py --claims` prints a Markdown table (row, chapter, status, evidence, resolved) from `_plans/reconciliation-plan.md`. Evidence tokens are backticked `test_*` names (resolved against `def test_...` in `examples/*/tests/**/*.py`, ids stripped), `source: <url>` (the URL must appear in that chapter's `_docs` file) and `run: <step id>`.
  - In the default run, rows 47 and later with an unresolved token are errors; earlier rows print as `legacy` info. Self-tests cover resolved, unresolved and legacy rows.
  - `--self-test` passes.

A3, text sweep, no quoted output (one executor):
- Site and repo text: `CLAUDE.md` (thesis, toolchain, language floor; add the planning-evidence findings to "Spike findings": inherited runtime_checkable deprecation, mock classes subclassing `Any`, explicit Protocol subclass `[abstract]` vs runtime, the contextlib 3.15 change, and API snippets targeting the running interpreter); `_config.yml`, `index.html` (both lines), `README.md` (lines 3 and 21), `examples.html` (lines 17 and 55), `examples/README.md`, `examples/00-prerequisites/README.md`, `_examples/00-prerequisites.md` (lines 5 and 12), `_parts/00-orientation.md` blurb.
- Chapter 0 text: description; line 14; the version table CPython row `3.15.2`; "Verified 2026-11-04"; `.python-version` holds `3.15.2`; `uv python install 3.15.2`; `~/.local/bin/python3.15`; "a 3.15 interpreter"; line 128 reworded "Since Python 3.14, annotations are evaluated lazily (PEP 649), so ..."; `uv python uninstall 3.15.2`; line 227 "as they work in 3.15".
- Other chapters: ch2 lines 7, 36 and 66 ("the idiom for naming a type in 3.15"); ch6 line 24; ch8 lines 24 and 73 (only after A4 confirms the message); the ch9 stub `description`.
- Plan notes per "Plans and history"; `spikes/feature-spikes/tests/test_dispatch.py` docstring and comment.

A4, quoted-output sweep (three parallel executors: ch0-3, ch5-6, ch7-8; each owns only its chapter files):
- Re-run every quoted block from a fresh run of the exact command or snippet on 3.15.2, filtered with `python3 scripts/host_ids.py filter`:
  - ch0: prereqs 168, pytest 186, mypy 208.
  - ch2: 171.
  - ch3: 180, 212.
  - ch5: 134, 191, 223.
  - ch6: 66, 178, 208, 218.
  - ch7: 74, 192, 230, 238, 249, 258.
  - ch8: 186, 231, 239, 251, 261.
- Re-perform each "Build, run, observe" experiment in a scratch copy.
- Check every inline backticked error or message string in prose against a fresh run.
- The handback has a table per chapter (block line, command, old/new identical or the diff) plus raw output. Any change is re-quoted and the matching test substring re-checked.

A5, attribution (decision 2): one clause crediting Woolf (PLoPD3, 1998) where chapters 2 and 3 introduce Null Object; the two `bibliography.html` rows (markup matching the existing rows).

A6, Part A gate: verify, validate (with `--self-test` and `--claims`), host_ids, the version greps (criteria A-1 to A-4), `scripts/site-build.sh` clean. Then the checkpoint commit `chore(r05): move the book to Python 3.15.2`.

Deliberate history statements allowed after the sweep (the complete list): `_docs/00-prerequisites.md`, the PEP 649 sentence "Since Python 3.14, ...". Internal files keep dated measurements ("600 runs on 3.14" in `CLAUDE.md`, re-labelled "measured on 3.14.10").

## Per-chapter spec

### Chapter 9: Protocol, duck typing, and structural typing with mypy (hands-on, has_example = true)

Thesis: an interface in Python is a shape the checker compares where a value is used, and absence is a member of that shape's type. Null Object dissolves into `X | None`. "Interface" needs disambiguating: a Protocol is structural and checked at the point of use, while an ABC is nominal, checked at construction, and carries shared code.

Sections (about 2,300 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): a missing carrier that crashes as `AttributeError` deep in booking; a do-nothing gateway that returns an empty reference and loses the booking silently; a hazmat-only quoter passed where any consignment arrives.
3. Figure plus one paragraph (~60).
4. `## Shape at the point of use` (~150). One sentence points to "ISP, DIP, and dependency injection without a framework" for consumer-owned Protocols. What mypy compares: parameter kinds and types and the return type. The missing-member note appears on assignment and not on a dict entry (test 21). `GATEWAYS` is a 3.15 `frozendict` (test 6).
5. `## Absence in the type: Null Object dissolves` (~380):
   - Woolf (PLoPD3, 1998) credited for the pattern. The force and structure. Bucket: dissolves, with the thesis wording. One pointer to "What 1994 assumed, and what Python dissolves" for the unguarded `[union-attr]`.
   - New material: the narrowing forms (walrus, `match`, early return). `assert` narrows for mypy but is removed when Python runs with `-O` (source: the `assert` statement reference). The `_NullGateway` fixture loses a booking while mypy accepts it (tests 3 and 22). A null object stays right where doing nothing is the correct answer (`no_discount`, test 4).
   - When `None` is itself data, use a 3.15 `sentinel`: `carriers_to_ask` with `ACCOUNT_DEFAULT`. Sentinels are truthy, so test with `is` (tests 5 and 18).
6. `## Generic protocols and inferred variance` (~250): `Quoter[T: Consignment]` in PEP 695 syntax with no `contravariant=True`. mypy infers that a quoter of the general type serves the narrower one and rejects the reverse (fresh `<string>:N` output). The runtime `AttributeError` shows why.
7. `## Callback protocols` (~170): `PricingRule.__call__(self, consignment, /)`. With `/`, `flat_rate` and `per_kg` qualify whatever their parameter names; without it, the name must match (`[assignment]`). When a callback Protocol beats a `Callable` alias: keyword parameters, overloads, attributes.
8. `## Protocol or ABC: two mechanisms, one word` (~330), disambiguate, stated as the bucket:
   - The ABC refuses an incomplete subclass at construction (runtime and `[abstract]`) and shares `reference()`.
   - The Protocol is checked where the value is passed.
   - `AircoGateway(CarrierBase)` satisfies `CarrierGateway` too.
   - Explicitly subclassing a Protocol makes the class nominal: mypy says `[abstract]`, the runtime instantiates it, and the inherited `...` body returns `None` (test 13).
   - `typing.override` catches a misspelled override.
   - Choose by who owns the need and whether code is shared. One pointer to "Template Method and the function alternative".
9. `## What runtime_checkable checks` (~180): names only (wrong signature and non-callable attribute pass); data protocols refuse `issubclass`; on 3.15 an undecorated sub-protocol warns and will raise in 3.20 (source: What's New in 3.15). The example's Protocols aren't runtime-checkable.
10. `## When not to use it` (~170): a Protocol with one implementation and no substitute; an ABC hierarchy for code that shares nothing; `X | None` threaded through ten signatures where one guard at the boundary would do; a sentinel where `None` already means "absent". Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written interfaces.** An assistant may add a `NullGateway` that returns empty values, inherit from a Protocol to "implement" it, use `isinstance` against a runtime-checkable Protocol as a signature check, or leave a callback Protocol without `/`. Check: is absence a `| None` that every caller narrows; does a null object exist only where doing nothing is the correct result; is a Protocol satisfied by shape rather than inheritance; is a runtime check backed by `mypy --strict`; does each callback Protocol mark its parameters positional-only.</blockquote>

    Each check maps to tests 3, 4, 13, 14, 17 and 20. No claim about assistant frequency.
11. `## Build, run, observe` (~220 plus output). Commands as in chapter 5. Experiments, each in a scratch copy, one change, reverted:
    (a) Delete the `if gateway is None:` guard in `book_with`. Expected: the member mypy run reports `[union-attr]` on that line and `test_book_with_turns_absence_into_a_booking_error` fails with `AttributeError`; quote the 3.15 message as observed.
    (b) Delete the `/` from `PricingRule.__call__`. Expected: mypy reports `[assignment]` (or `[arg-type]`) where `per_kg` is typed as a `PricingRule`, and pytest stays green.
12. `## For deeper coverage` (~130):
    - PEP 544 (Levkivskyi, Lehtosalo, Langa); the typing spec chapter "Protocols"; the mypy docs "Protocols and structural subtyping"; PEP 695 (variance inference); PEP 698 (`override`); PEP 3119 (ABCs); PEP 661 (Einat, Zijlstra); PEP 814 (Stinner, Na).
    - What's New in Python 3.15 (runtime_checkable deprecation).
    - Woolf, PLoPD3.
    - Fluent Python 2nd ed. ["Interfaces, Protocols, and ABCs" and "More About Type Hints" only if verified against the O'Reilly table of contents, else by topic]; Effective Python 3rd ed. by topic; bibliography link.

Figure `09-protocol-and-structural-typing` (vertical):
- Top accent box: `book_with(code, consignment)`.
- Three lanes below, each a light box with the check and where it happens:
  - "absence": `find_gateway(code) -> CarrierGateway | None`, "narrowed before use";
  - "shape": `CarrierGateway`, "compared where passed" (`FastlineGateway`, no base class);
  - "declaration": `CarrierBase`, "checked at construction" (`AircoGateway`).
- Side box: `_NullGateway` "absence hidden: accepted, books nothing".

No numbers in the SVG. Caption draft (39 words with prefix): "Figure 9.1: Three checks behind one booking call. The optional return makes absence a branch the caller must write, the Protocol compares shape where the gateway is passed, and the ABC refuses an incomplete subclass when it is built."

Citations: verify each before writing; bracketed fallbacks; no sentence quoted unless checked; no cross-language comparison.

### Chapter 10: Context managers: deterministic cleanup (hands-on, has_example = true)

Thesis: Resource Acquisition survives. `with` guarantees that `__exit__` runs on every path, which removes the boilerplate. What release means stays with the author: close, commit or discard, propagate or swallow, and the order across several resources.

Sections (about 2,300 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): an exception halfway through a manifest leaves a handle open and a half-written manifest that a downstream reader takes for complete.
3. Figure plus one paragraph (~60).
4. `## Resource Acquisition: the force and why it survives` (~250): PEP 343 (van Rossum, Coghlan) and the data model's "With Statement Context Managers". Bucket: survives, and why. POSA3 (Kircher, Jain, 2004) credited for resource acquisition and release as a design topic [pattern names only if verified].
5. `## A class with __enter__ and __exit__` (~380): excerpt of `ManifestWriter`. Write to `.partial`, close always, `replace` on success, `unlink` on failure, return `None` so the exception propagates, single-use guard. mypy reads `__exit__`'s return type: `-> None` makes code after a raising `with` unreachable, `-> bool` doesn't (fresh output). Explicit `encoding="utf-8"` even though 3.15 defaults to UTF-8 (source: PEP 686).
6. `## The generator form` (~280): excerpt of `manifest_file`. Code before `yield` is enter and code after is exit, but only `try` makes the exit run on an exception (`_leaky_manifest_file` fixture; mypy can't see it, test 13). The exception re-raises at the `yield`. Annotate as `Iterator[TextIO]`.
7. `## Several resources: ExitStack` (~250): excerpt of `write_manifests`. When opening the third manifest fails, the two entered writers exit in reverse order and discard their partials.
8. `## Swallowing an exception` (~170): a truthy `__exit__` swallows. Use `contextlib.suppress` for one named exception only, and where the suppressed case is expected.
9. `## A context manager as a decorator` (~170): `@manifest_scope`-style use is the decorator syntax applied to a cleanup (one pointer to "Decorator the pattern vs @decorator the syntax, and Proxy"). From 3.15 a context manager decorating a generator function stays entered across iteration; before Python 3.15 it exited as soon as the generator was created (source: What's New in 3.15; test 9).
10. `## When not to use it` (~170): a resource with no release step; a context manager wrapping a single call that already closes; swallowing to "keep going"; one pointer to "asyncio and the patterns" for `async with`. Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written cleanup.** An assistant may open a file without `with`, write a `@contextmanager` with no `try`, return `True` from `__exit__`, or write directly to the final path. Check: is every acquisition inside a `with`; does the generator form use `try`; does `__exit__` return `None` unless swallowing is the documented intent; is a failed write discarded rather than left for a reader; does a test raise mid-write and assert the handle is closed.</blockquote>
11. `## Build, run, observe` (~230). Experiments:
    (a) Delete `self._handle.close()` from the failure branch of `ManifestWriter.__exit__`. Expected: `test_writer_closes_and_discards_on_an_exception[class]` fails on `handle.closed`.
    (b) Remove the `try` from `manifest_file`. Expected: `test_writer_closes_and_discards_on_an_exception[generator]` fails, and mypy reports success.
12. `## For deeper coverage` (~130): PEP 343; data model "With Statement Context Managers"; `contextlib` docs (`contextmanager`, `ExitStack`, `suppress`, `ContextDecorator`); PEP 686; What's New 3.15 (contextlib); POSA3 by topic; Fluent Python 2nd ed. ["with, match, and else Blocks" if verified, else by topic]; Effective Python 3rd ed. by topic; bibliography link.

Figure `10-context-managers` (vertical):
- Top accent box: `with ManifestWriter(path) as out:`.
- Then `__enter__`: "opens path.partial", then "body writes lines".
- The flow branches:
  - "body returns": `__exit__(None, None, None)`, "close, replace partial with path", ending at "manifest committed";
  - "body raises": `__exit__(type, exc, tb)`, "close, unlink partial, return None", ending at "exception propagates".

Caption draft (37 words): "Figure 10.1: Both ways out of a manifest write. The with statement calls __exit__ on success and on failure; ManifestWriter decides what each means, committing the partial file on success and discarding it before the exception continues."

### Chapter 11: Proving it works: pytest, pytest-mock, and mypy (hands-on, has_example = true, no bucket)

Thesis: a test is evidence for one named claim, and it counts only if it has been seen to fail. Fixtures supply dependencies by name. Fakes are checked by mypy and mocks are not. `create_autospec` is the only mock that checks call shapes, and mypy checks the tests themselves.

Sections (about 2,300 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): an assertion on a misspelled method that passes against a plain `Mock`; a quote test that depends on the wall clock; a suite that's green after the check it guards is deleted.
3. Figure plus one paragraph (~60).
4. `## A claim, a witness, and a test you've seen fail` (~300):
   - The method the book's examples follow, stated once: name tests as claims; keep negative fixtures `_`-prefixed in `tests/` with a "Negative fixture:" docstring; a deletion table removes each check in a scratch copy and records the failing test; experiments change one thing.
   - [Name "mutation testing" and credit DeMillo, Lipton and Sayward, *IEEE Computer* 11(4), 1978, only if verified; else describe the practice unnamed.]
5. `## Fixtures and parametrize` (~250): dependencies by parameter name and `conftest.py` discovery; the `make_fake` factory fixture; `yield` teardown runs whether the test passes or fails (source: pytest docs "How to use fixtures"; experiment c); `pytest.param(..., id=...)`. Pointer to "pytest reference".
6. `## Fakes and mocks: what each one checks` (~360):
   - Meszaros (2007) credited for "test double" and the names fake, stub, mock and spy, plus one pointer to "xUnit test patterns (Meszaros)".
   - A table (rows not counted) with columns Double | Unknown name | Wrong signature | mypy, rows `FakeGateway`, `Mock()`, `Mock(spec=...)`, `create_autospec(..., instance=True)`, built from tests 6-8 and 13-14.
   - The vacuous assertion. `side_effect` drives the timeout branch.
   - The typeshed comment quoted exactly, with attribution to typeshed's `unittest/mock.pyi`, as the reason every mock is assignable to every type. One pointer to "ISP, DIP, and dependency injection without a framework" for the first demonstration, and one to "Mocking reference: unittest.mock and pytest-mock".
7. `## Time, environment, and other process state` (~220): inject `clock: Callable[[], datetime]` rather than patching; break ties by carrier code so the winner is deterministic; `monkeypatch.context()` for `os.environ`, restored on exit (test 11). One pointer to "Seams in Python: monkeypatch, injection, and duck typing".
8. `## mypy as a test` (~260): `uv run mypy --strict src tests` checks the tests too; `assert_type` fails the mypy run and is a no-op at runtime; a typed `# type: ignore[code]` under `warn_unused_ignores` fails when mypy stops reporting; the API helper asserts exit status and an exact code set; snippets are checked against the running interpreter.
9. `## Configuration that refuses silence` (~150): `--strict-markers`, `--strict-config`, `xfail_strict`, and `filterwarnings = ["error"]` if A1 adopted it, so the 3.15 runtime_checkable deprecation fails a run rather than scrolling past. Source: pytest docs "Configuration" and "How to capture warnings". `--import-mode=importlib` gets only a pointer to "Prerequisites and the toolchain".
10. `## When a test proves less than it seems` (~180): asserting that a mock was called instead of the outcome; a mock where a fake would be checked; a test never seen failing; one parametrize case per line of the implementation. Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written tests.** An assistant may use a plain `Mock` for a typed collaborator, assert only that a method was called, patch a module global instead of injecting it, or read the clock inside the code under test. Check: is each mock built with `create_autospec`; does the test assert an outcome a reader cares about; is the dependency passed in; is time injected; has the test been seen to fail with its check deleted.</blockquote>
11. `## Build, run, observe` (~230). Experiments:
    (a) Make `RateEngine.book_best` book every carrier. Expected: `test_book_best_books_only_the_winner` fails on `assert_not_called`.
    (b) In `test_autospec_rejects_names_and_signatures`, replace `mocker.create_autospec(CarrierGateway, instance=True)` with `mocker.Mock(spec=CarrierGateway)`. Expected: `Failed: DID NOT RAISE <class 'TypeError'>`.
    (c) Add a failing assert to `test_quote_validity_comes_from_the_injected_clock` and run with `-s`. Expected: the `quote_log` fixture's teardown line prints after the failure.
12. `## For deeper coverage` (~130): pytest docs (fixtures, parametrize, monkeypatch, configuration, warnings); pytest-mock docs; `unittest.mock` "Autospeccing"; typeshed; Meszaros 2007; Fowler, "Mocks Aren't Stubs" [only if the martinfowler.com URL verifies, else omit]; Okken 2nd ed. by topic (decision 2); Effective Python 3rd ed. by topic; bibliography link.

Figure `11-testing-with-pytest-pytest-mock-and-mypy` (vertical): accent box "claim: the engine books only the winner", then "witness test: test_book_best_books_only_the_winner", then "seen failing: deletion in a scratch copy", then "quoted output: fresh, scrubbed run". A side box "negative fixture: shows the failure the claim rules out" connects to the witness. Caption draft (35 words): "Figure 11.1: How a claim becomes evidence. Each claim gets a witness test named after it, the test is seen to fail when its check is deleted, and only a fresh, scrubbed run is quoted."

## Example spec

### `examples/09-protocol-and-structural-typing` (project `structural-typing`, package `structural_typing`)

`pyproject.toml` in the r04 shape (`requires-python = ">=3.15"`, no `[tool.*]`).

- `domain.py`: `ConsignmentId = NewType`. `Weight` (frozen slotted, finite positive). `Money` (frozen slotted, `Decimal`, currency, same-currency `__add__`). `Consignment(id, weight, destination)` (frozen slotted kw_only). `HazmatConsignment(Consignment)` adds `un_number: str`, and `__post_init__` checks `UN\d{4}` with a `ValueError`. `BookingError`.
- `carriers.py`:
  - `class CarrierGateway(Protocol)`: `book(self, consignment: Consignment, /) -> str`.
  - `FastlineGateway` (plain class).
  - `class CarrierBase(ABC)`: `code: ClassVar[str]`, concrete `reference(self, consignment) -> str` giving `f"{self.code}:{consignment.id}"`, `@abstractmethod book`.
  - `AircoGateway(CarrierBase)` with `@override book`.
  - `GATEWAYS: Mapping[str, Callable[[], CarrierGateway]] = frozendict(FASTLINE=FastlineGateway, AIRCO=AircoGateway)`.
  - `find_gateway(code) -> CarrierGateway | None`.
  - `book_with(code, consignment) -> str`, which raises `BookingError(f"unknown carrier {code!r}")` when the lookup returns `None`.
  - `ACCOUNT_DEFAULT = sentinel("ACCOUNT_DEFAULT")`.
  - `carriers_to_ask(preferred: str | None | ACCOUNT_DEFAULT = ACCOUNT_DEFAULT, *, account_carrier: str = "FASTLINE") -> tuple[str, ...]`: the sentinel gives `(account_carrier,)`, `None` gives `tuple(sorted(GATEWAYS))`, a known code gives `(code,)`, and an unknown code raises `BookingError`.
- `pricing.py`:
  - `class PricingRule(Protocol)`: `__call__(self, consignment: Consignment, /) -> Money`.
  - `flat_rate(consignment)` and `per_kg(shipment)` (different parameter names on purpose; docstring says why).
  - `no_discount(consignment, /) -> Money` returns zero in EUR.
  - `quote(consignment, rule: PricingRule, discount: PricingRule = no_discount) -> Money`.
  - `class Quoter[T: Consignment](Protocol)`: `quote(self, consignment: T, /) -> Money`.
  - `GeneralQuoter`, `HazmatQuoter` (adds a surcharge using `un_number`), `price_all(quoter: Quoter[Consignment], consignments)`, `price_hazmat(quoter: Quoter[HazmatConsignment], consignments)`.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: an EUR `consignment` to `"SGSIN"`, a `hazmat` consignment.

`test_absence.py` (fixture `_NullGateway`, which returns `""`):
1. `test_find_gateway_returns_none_for_an_unknown_code`
2. `test_book_with_turns_absence_into_a_booking_error`: `"FASTLINE:CN-..."` for a known code; `BookingError` matching `unknown carrier 'UNKNOWN'`.
3. `test_a_null_gateway_hides_a_lost_booking`: the reference is `""` and nothing raises.
4. `test_no_discount_is_a_null_object_that_loses_nothing`
5. `test_a_sentinel_separates_not_given_from_none`: the three branches; an unknown code raises; `copy.copy(ACCOUNT_DEFAULT) is ACCOUNT_DEFAULT`; `bool(ACCOUNT_DEFAULT) is True`.
6. `test_the_registry_is_a_frozendict`: item assignment (`# type: ignore[index]`) raises `TypeError` matching `does not support item assignment`; it is a `Mapping`, not a `dict`.

`test_generics.py`:
7. `test_a_general_quoter_serves_hazmat_consignments`
8. `test_a_hazmat_quoter_fails_on_a_general_consignment_at_runtime`: `# type: ignore[arg-type]`; `AttributeError` matching `un_number`.
9. `test_hazmat_consignment_validates_its_un_number`
10. `test_callback_protocol_accepts_any_parameter_name`

`test_disambiguate.py` (fixtures `_HalfCarrier(CarrierBase)` and `_DeclaredGateway(CarrierGateway)`):
11. `test_abc_refuses_an_incomplete_subclass_at_construction`: `# type: ignore[abstract]`; matching `without an implementation for abstract method 'book'`.
12. `test_both_carriers_satisfy_the_protocol_one_by_inheritance`
13. `test_explicit_protocol_subclass_is_nominal_and_still_instantiable`: `_DeclaredGateway().book(c) is None`.

`test_runtime_checkable.py` (fixtures `_CheckedGateway`, `_WrongSignature`, `_BookAttribute`, `_HasCode`, `_UndecoratedTracking(_CheckedGateway, Protocol)`):
14. `test_runtime_checkable_checks_names_only`
15. `test_a_data_protocol_refuses_issubclass`
16. `test_an_undecorated_subprotocol_warns_on_isinstance`: `pytest.warns(DeprecationWarning, match="isn't explicitly decorated")`.

`test_static.py`:
17. `test_mypy_requires_a_branch_for_absence[unguarded|walrus|match|early-return|assert]`: the first is exit 1 with `{"union-attr"}` (control); the others are exit 0.
18. `test_mypy_requires_a_branch_for_the_sentinel`: exit 1, `{"union-attr"}`, `Item "sentinel" of`.
19. `test_mypy_infers_quoter_variance`: exit 1 with `{"arg-type"}` and `have conflicts`; the reverse is exit 0.
20. `test_mypy_matches_callback_parameter_names_without_slash`: `{"assignment"}`.
21. `test_mypy_checks_protocols_at_use_and_abcs_at_construction[protocol-use|abc-construction|declared-protocol|override-typo]`:
    - codes, in order: `{"assignment"}`, `{"abstract"}`, `{"abstract"}`, `{"misc"}`;
    - substrings, in order: `missing following "CarrierGateway" protocol member`, `Cannot instantiate abstract class`, the same, `marked as an override, but no base method was found`.
22. `test_mypy_accepts_a_null_gateway`: exit 0, empty.

Also `README.md` and the card `_examples/09-protocol-and-structural-typing.md` (`order: 9`, eyebrow "Python substrate · Protocol, Null Object"). No `mock`, `monkeypatch`, `print(`, `Optional` or `TypeVar(` in the member. No `isinstance` in `src/`.

### `examples/10-context-managers` (project `context-managers`, package `context_managers`)

- `manifest.py`:
  - `ConsignmentId`; `Manifest(sailing: str, port: str, consignments: tuple[ConsignmentId, ...])` (frozen slotted; `port` is a UN/LOCODE checked in `__post_init__`).
  - `type Opener = Callable[[Path], TextIO]`; `open_utf8(path) -> TextIO` returns `path.open("w", encoding="utf-8")`.
  - `render_line(consignment_id) -> str`.
  - `ManifestWriter(path, *, opener=open_utf8)`:
    - `__enter__ -> TextIO` opens `<name>.partial`, and raises `RuntimeError("ManifestWriter is single-use")` if entered twice;
    - `__exit__(...) -> None` always closes, then `replace`s on success or `unlink(missing_ok=True)`s on failure.
  - `@contextmanager manifest_file(path, *, opener=open_utf8) -> Iterator[TextIO]` with the same semantics through `try`/`except BaseException`/`else`.
  - `write_manifests(manifests, directory, *, opener=open_utf8) -> list[Path]` over `ExitStack`.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: a `RecordingOpener` (records `opened`/`closed` events in order, can fail on the Nth open with `OSError`); three manifests (`"NLRTM"`, `"SGSIN"`, `"DEHAM"`).

`test_writer.py` (fixtures `_write_without_with` and `_leaky_manifest_file`; every leaked handle is closed in the test's `finally`):
1. `test_without_with_an_exception_leaves_the_handle_open`
2. `test_writer_closes_and_discards_on_an_exception[class|generator]`
3. `test_writer_commits_only_on_success[class|generator]`: the final file is absent inside the block and present after.
4. `test_writer_is_single_use`
5. `test_the_generator_form_needs_try`

`test_stack.py`:
6. `test_exit_stack_unwinds_entered_writers_in_reverse_order`: the third open fails; closes are `second writer, then first writer` in reverse; no final or partial files remain.
7. `test_exit_stack_commits_every_manifest_on_success`

`test_semantics.py` (fixture `_Swallowing`):
8. `test_a_truthy_exit_swallows_the_exception`
9. `test_a_context_manager_decorating_a_generator_spans_iteration`: the log is empty before iteration, then `["enter", "row NLRTM", "row SGSIN", "exit"]`.
10. `test_manifest_rejects_a_port_that_is_not_a_locode`

`test_static.py`:
11. `test_mypy_reads_exit_return_type_for_reachability[none-exit|bool-exit]`: with `--warn-unreachable`, exit 1 with `{"unreachable"}`, then exit 0.
12. `test_mypy_types_the_with_target[class|generator|exit-stack]`: `assert_type(out, TextIO)`, exit 0.
13. `test_mypy_cannot_see_a_missing_try`: exit 0.

Also `README.md` and the card (`order: 10`, eyebrow "Python substrate · Context managers, Resource Acquisition"). No `async`, `yield` outside `manifest_file` and the test-local generator, no `print(`, no `mock`, no `monkeypatch`, no `time.`.

Test 6's expected close order is exactly "second writer, then first writer". The executor asserts the recorded event list from a real run.

### `examples/11-testing-with-pytest-pytest-mock-and-mypy` (project `testing-baseline`, package `testing_baseline`)

- `domain.py`: `ConsignmentId`, `Weight`, `Money` (`__lt__` for selection), `Consignment`, `RatingError`.
- `carriers.py`: `CarrierQuote(carrier: str, amount: Money)`; `CarrierTimeoutError`; `class CarrierGateway(Protocol)` with `quote(self, consignment, /) -> CarrierQuote` and `book(self, consignment, /) -> str`.
- `engine.py`:
  - `RateQuote(consignment_id, carrier, total: Money, valid_until: datetime, skipped: tuple[str, ...])`.
  - `RateEngine(gateways: Mapping[str, CarrierGateway], *, clock: Callable[[], datetime], validity: timedelta)`:
    - `best_quote(consignment) -> RateQuote` asks carriers in sorted code order, skips `CarrierTimeoutError`, picks the minimum by `(amount, carrier)`, sets `valid_until = clock() + validity`, and raises `RatingError("no carrier answered")` when all time out;
    - `book_best(consignment) -> str` books the winner only.
  - `validity_from_env(environ: Mapping[str, str] = os.environ) -> timedelta` reads `RATE_QUOTE_VALIDITY_MINUTES` (default 30) and raises `ValueError` unless it is a positive int.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: `consignment`; `fixed_now` (2026-11-04 09:00 UTC); `make_fake` factory fixture returning `FakeGateway(carrier, amount, *, times_out=False)`, which records `booked`; a `quote_log` `yield` fixture over `tmp_path` that writes a teardown line.

`test_engine.py`:
1. `test_best_quote_picks_the_cheapest_carrier[fastline-cheaper|airco-cheaper|tie-goes-to-airco]`, using `pytest.param(..., id=...)`.
2. `test_quote_validity_comes_from_the_injected_clock`: also `assert_type(quote.total, Money)`.
3. `test_a_timed_out_carrier_is_skipped`
4. `test_every_carrier_timing_out_is_a_rating_error`

`test_doubles.py` (all through `mocker`):
5. `test_book_best_books_only_the_winner`: autospec, `assert_called_once_with(consignment)`, `assert_not_called()`.
6. `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`: `loser.bok.assert_not_called()` passes.
7. `test_spec_rejects_unknown_names_but_not_wrong_signatures`
8. `test_autospec_rejects_names_and_signatures`: `AttributeError` matching `has no attribute 'bok'`; `TypeError` matching `missing a required positional-only argument: 'consignment'`.
9. `test_side_effect_drives_the_timeout_branch`

`test_environment.py`:
10. `test_validity_reads_the_environment_and_the_context_restores_it`: captures `os.environ.get(...)` before, uses `monkeypatch.context()`, asserts it is equal after.
11. `test_validity_rejects_a_value_that_is_not_a_positive_int[zero|negative|text]`, plus the default when unset (via the `environ` parameter, no patching).

`test_static.py`:
12. `test_mypy_accepts_every_mock_where_a_gateway_is_expected[Mock|Mock-spec|MagicMock-spec|autospec]`: exit 0, empty.
13. `test_mypy_checks_a_hand_written_fake[dict-entry|assignment]`: `{"dict-item"}`; `{"assignment"}` with `missing following "CarrierGateway" protocol member`.
14. `test_assert_type_is_static_only`: snippet exit 1 with `{"assert-type"}`; at runtime `assert_type(1, str) == 1` (with `# type: ignore[assert-type]`).

Also `README.md` and the card (`order: 11`, eyebrow "Python substrate · Testing baseline"). No `mock.patch`, `mocker.patch`, `time.sleep`, `datetime.now` or `print(`. `monkeypatch` only in `test_environment.py`.

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| A0 | This plan file; dated notes per "Plans and history"; PDP-109a..c, 110a..c, 111a..c `active`; reconciliation rows 47-64 `open`; decisions recorded | - | todo |
| A1 | Interpreter and pins to 3.15.2, `uv lock`, members' `requires-python`, `__spec__.parent`, `filterwarnings` trial; verify.sh x3 | A0 | todo |
| A2 | `check-prereqs.sh`; `validate.py` stale-version check, claims audit, self-test fixtures | A1 | todo |
| A3 | Text sweep (no quoted output); CLAUDE.md findings | A1 | todo |
| A4 | Quoted-output sweep ch0-8 (three parallel executors), experiments re-performed, re-quotes | A1, A3 | todo |
| A5 | Woolf credit in ch2/ch3; Woolf and Okken bibliography rows (decision 2) | A3 | todo |
| A6 | Part A gate (criteria A-1 to A-7); checkpoint commit | A2, A4, A5 | todo |
| 0 | Domain-model rows 9-11 updated: names as in the example spec; row 9 caveat now "stated in the ISP/DIP chapter; chapter 9 doesn't repeat it; chapter 11 gives the matrix"; row 11 failing text uses the 3.15 message `missing a required positional-only argument: 'consignment'` and "mock classes subclass `Any` in typeshed"; ch9 stub description fixed | A6 | todo |
| 1a | ch9 member, card, README; three green runs; **deletion table**: the `find_gateway` `None` return (replaced by `KeyError`), the `book_with` guard, each `carriers_to_ask` branch, the `un_number` check, `no_discount` default (replaced by `None`), `frozendict` (replaced by `dict`), `CarrierBase.reference`, `@abstractmethod`, `/` on `PricingRule`, `@override` | 0 | todo |
| 1b | ch10 member; deletion table: both closes in `__exit__`, `replace`, `unlink`, the single-use guard, the generator's except-branch close and unlink, the else-branch replace, the `ExitStack` (replaced by a plain loop), the LOCODE check | 1a | todo |
| 1c | ch11 member; one `uv lock` after all three (sequenced); deletion table: minimum selection, the code tie-break, clock use, validity add, the timeout skip, the all-timed-out error, book winner only, the env positive-int check, the env default | 1b | todo |
| 2 | Witness results into rows 47-64 with test names (claims audit resolves); a failed witness changes the thesis before prose | 1c | todo |
| 3 | Three figures, specs `diagrams/specs/09-*.py`, `10-*.py`, `11-*.py`, `_data/diagrams.yml` (single owner; `section: "Ch. 9"`/`"Ch. 10"`/`"Ch. 11"`); figures 00-08 unchanged | 2 | todo |
| 4 | ch9-11 `status = "drafted"` (kind stays `hands-on`) | 3 | todo |
| 5 | Three prose agents in parallel; verify attributions; run the experiments in scratch copies; quote fresh filtered output; each hands back the sources it checked and a per-paragraph claims table (claim, then test, run or source) | 3, 4 | todo |
| 6 | Opus validation; up to two repair rounds | 5 | todo |
| 7 | PR, `ci-ok` green, ask the user before merge; tag r05.x; notes-only release; hub PR: `sites.yml` synopsis "idiomatic Python 3.15"; `books.yml` `referenced_by` for Meszaros and *The Pragmatic Programmer*; new entries for Meyer's *Object-Oriented Software Construction* (1997), Woolf/PLoPD3 and Okken 2nd ed., with `book_categories.yml` placement | 6 | todo |

Reconciliation rows (step A0). The "Verified by" column uses resolvable tokens.

| # | Ch | Claim | Verified by |
| --- | --- | --- | --- |
| 47 | 0-8 | Every quoted output and inline message in chapters 0-8 reproduces on 3.15.2 and mypy 2.4.1, or is re-quoted from a fresh run | `run: A4` |
| 48 | 9 | `X \| None` makes absence a branch: unguarded access is `[union-attr]`; walrus, match and early return narrow; `assert` narrows but is removed under `-O` | `test_mypy_requires_a_branch_for_absence`, `test_book_with_turns_absence_into_a_booking_error`, `source: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement` |
| 49 | 9 | A null gateway hides a lost booking and mypy accepts it; a null object is right where doing nothing is the answer | `test_a_null_gateway_hides_a_lost_booking`, `test_mypy_accepts_a_null_gateway`, `test_no_discount_is_a_null_object_that_loses_nothing` |
| 50 | 9 | A 3.15 `sentinel` separates not-given from `None`, is truthy, keeps identity under copy, and mypy narrows it with `is` | `test_a_sentinel_separates_not_given_from_none`, `test_mypy_requires_a_branch_for_the_sentinel`, `source: https://peps.python.org/pep-0661/` |
| 51 | 9 | PEP 695 Protocol variance is inferred: a general quoter serves the narrow type, the narrow quoter is rejected, and it fails at runtime | `test_mypy_infers_quoter_variance`, `test_a_general_quoter_serves_hazmat_consignments`, `test_a_hazmat_quoter_fails_on_a_general_consignment_at_runtime` |
| 52 | 9 | A callback Protocol with `/` ignores parameter names; without it, names must match | `test_callback_protocol_accepts_any_parameter_name`, `test_mypy_matches_callback_parameter_names_without_slash` |
| 53 | 9 | Protocol is checked at use, ABC at construction; an explicit Protocol subclass is abstract to mypy but instantiable; `override` catches a misspelling; an ABC subclass also satisfies the Protocol | `test_mypy_checks_protocols_at_use_and_abcs_at_construction`, `test_abc_refuses_an_incomplete_subclass_at_construction`, `test_explicit_protocol_subclass_is_nominal_and_still_instantiable`, `test_both_carriers_satisfy_the_protocol_one_by_inheritance` |
| 54 | 9 | `runtime_checkable` checks names only; data protocols refuse `issubclass`; 3.15 warns on an undecorated sub-protocol | `test_runtime_checkable_checks_names_only`, `test_a_data_protocol_refuses_issubclass`, `test_an_undecorated_subprotocol_warns_on_isinstance` |
| 55 | 10 | Without `with`, an exception leaves the handle open; `ManifestWriter` and `manifest_file` close on every path and commit only on success | `test_without_with_an_exception_leaves_the_handle_open`, `test_writer_closes_and_discards_on_an_exception`, `test_writer_commits_only_on_success`, `test_writer_is_single_use` |
| 56 | 10 | The generator form needs `try`, and mypy can't see it missing | `test_the_generator_form_needs_try`, `test_mypy_cannot_see_a_missing_try` |
| 57 | 10 | `ExitStack` unwinds entered resources in reverse order when a later one fails | `test_exit_stack_unwinds_entered_writers_in_reverse_order`, `test_exit_stack_commits_every_manifest_on_success` |
| 58 | 10 | A truthy `__exit__` swallows; mypy's reachability follows `__exit__`'s return type | `test_a_truthy_exit_swallows_the_exception`, `test_mypy_reads_exit_return_type_for_reachability` |
| 59 | 10 | On 3.15 a context manager decorating a generator function spans iteration (before 3.15 it exited at creation) | `test_a_context_manager_decorating_a_generator_spans_iteration`, `source: https://docs.python.org/3.15/whatsnew/3.15.html` |
| 60 | 11 | A plain Mock passes an assertion on a misspelled method; spec rejects names only; autospec rejects names and signatures | `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`, `test_spec_rejects_unknown_names_but_not_wrong_signatures`, `test_autospec_rejects_names_and_signatures`, `test_book_best_books_only_the_winner` |
| 61 | 11 | Every mock is assignable to every type for mypy because typeshed subclasses mocks from `Any`; a hand-written fake is checked | `test_mypy_accepts_every_mock_where_a_gateway_is_expected`, `test_mypy_checks_a_hand_written_fake`, `source: https://github.com/python/typeshed/blob/main/stdlib/unittest/mock.pyi` |
| 62 | 11 | An injected clock and a code tie-break make quote tests deterministic; `monkeypatch.context` restores the environment | `test_quote_validity_comes_from_the_injected_clock`, `test_best_quote_picks_the_cheapest_carrier`, `test_validity_reads_the_environment_and_the_context_restores_it` |
| 63 | 11 | `assert_type` is a static assertion and a runtime no-op; a typed ignore is a static regression test | `test_assert_type_is_static_only`, `run: 1c` |
| 64 | 11 | `yield` fixture teardown runs on failure; strict markers, config and xfail refuse silence; `filterwarnings = error` fails on a deprecation | `run: 5`, `source: https://docs.pytest.org/en/stable/how-to/fixtures.html`, `source: https://docs.pytest.org/en/stable/reference/reference.html` |

## Acceptance criteria

Part A:
- A-1. `.python-version` is `3.15.2`. `grep -rnE '>=3\.14|py314|"3\.14"' pyproject.toml examples/*/pyproject.toml spikes/*/pyproject.toml` prints nothing. `uv lock --check` passes.
- A-2. `grep -rnE "Python 3\.14|python3\.14|3\.14\.[0-9]" _docs _parts _examples examples/README.md examples/*/README.md README.md index.html examples.html chapters.html bibliography.html diagrams.html _config.yml _data diagrams/*.svg` prints exactly one line: the chapter 0 PEP 649 history sentence. `validate.py`'s stale-version check agrees.
- A-3. The chapter 0 version table, the r01 "Verified toolchain" table, `.python-version`, `uv.lock` and `ci.yml` agree (`check_pins` clean). The chapter 0 prereqs and pytest outputs show `Python 3.15.2`.
- A-4. The A4 handback table covers all 24 quoted blocks and every inline message, each from a fresh run; changed quotes are re-quoted; no block is edited without a run.
- A-5. `bash scripts/check-prereqs.sh` prints `python   OK     Python 3.15.2 (...)` and contains no hard-coded minor version.
- A-6. `validate.py`, `--self-test` and `--claims` exit 0. The claims table lists rows 1-64, with 47-64 resolved.
- A-7. `filterwarnings = ["error"]` is adopted with verify green, or its rejection is recorded with the warning text.

Chapters:
1. `bash scripts/verify.sh` prints `verify: all steps passed`.
2. Each new member: `uv run pytest` and `uv run mypy --strict src tests` exit 0 on three consecutive runs. `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock\.patch|mocker\.patch|random"` over the three members prints nothing. `grep -rln monkeypatch examples/1[01]-* examples/09-*` lists only `examples/11-.../tests/test_environment.py`.
3. Every mypy-API test asserts exit status and an exact code set (`grep -c "_codes("` at least 4 per `test_static.py`). Every `# type: ignore[...]` names a code.
4. Deletion tables (1a-1c): every listed check, when deleted, makes at least one named test fail; no row reads "nothing failed".
5. ch9-11 drafted, one figure each, captions 20-45 words including `Figure N.1:`, 1,900-2,500 prose words each.
6. `grep -c '<blockquote class="ai-sidebar"'` is 1 in each of ch9, ch10 and ch11; `{: .ai-sidebar}` appears nowhere. `grep -c "^## When not to use it"` is 1 in ch9 and ch10 and 0 in ch11. `grep -c "^## When a test proves less than it seems"` is 1 in ch11. `grep -c "^## How it works"` is 0 in all three.
7. Thesis: ch9 contains "a feature resolves the force without the pattern's structure" (or adapted), names Null Object as dissolving and "interface" as needing disambiguation. ch10 names Resource Acquisition as surviving. `grep -ciE "dissolv|surviv|disambiguat"` over ch11 prints 0.
8. Non-overlap:
   - ch9 repeats neither the `<string>:7` `find_gateway` output from "What 1994 assumed" nor the mock-as-`Any` caveat. It has one pointer each to the ISP/DIP chapter and to "Template Method and the function alternative".
   - `grep -nE "async |yield from|__aenter__|aclosing"` over `examples/10-context-managers/src` prints nothing. ch10 prose mentions `async with` in one sentence only.
   - ch11 points to "ISP, DIP, and dependency injection without a framework", "pytest reference", "Mocking reference: unittest.mock and pytest-mock", "xUnit test patterns (Meszaros)" and "Seams in Python: monkeypatch, injection, and duck typing" by title, without re-explaining them.
9. Voice: `scan.sh --tier ban --fail` exits 0 over the three chapters, READMEs, cards and SVGs; `--stats` reviewed; contractions used (uncontracted `does not|do not|is not|are not|did not` at most 3 per chapter outside code and output).
10. `grep -c $'\u2014'` is 0 over every file touched in r05, including this plan.
11. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|RAII|capstone|PDP-|\br0[0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/09-*.md _docs/1[01]-*.md`, the new READMEs and cards prints nothing.
12. Idiomatic scan: 0 ban-tier in the three members.
13. `python3 scripts/host_ids.py check` exits 0; quoted output shows `<repo>`.
14. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run (API output prints `<string>:N` matching the snippet), apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->` so ruff's markdown formatting leaves them unchanged (`ruff format --check .` clean).
15. Each experiment is performed in a scratch copy and changes one thing; the prose quotes the observed result; the handback includes raw filtered output.
16. Attribution (standing rule: credit every source a chapter leans on, by author and work, where the idea is used; every book in `bibliography.html` and in hub `books.yml` `referenced_by`; nothing copied; quotations exact and attributed; a missing credit is blocking):
    - ch9 credits Woolf; ch11 credits Meszaros, and quotes the typeshed comment exactly with attribution; ch10 credits PEP 343's authors and POSA3 by topic.
    - Fluent Python chapter titles appear only if verified; bracketed fallbacks applied; each prose agent lists the sources it checked.
17. Claims: every factual sentence in ch9-11 maps to a named test, a recorded run or a fetched source in the prose agent's claims table. `validate.py --claims` resolves rows 47-64.
18. `scripts/site-build.sh` succeeds and `git status` is clean afterwards; `_data/diagrams.yml` has twelve entries; `diagrams/0[0-8]-*` unchanged.
19. Reconciliation rows 47-64 are `verified` or `adjusted`, with evidence.
20. Deterministic: no test depends on wall time, environment defaults, ordering of dict iteration it didn't create, or `PYTHONUTF8`.
21. CI `ci-ok` green on the PR; merge only after the user's explicit approval; the hub PR is opened after merge.

## Risks

- **3.15 drift in quoted output.** Planning runs show the wording unchanged, but typeshed is version-gated, so a mypy message in chapters 5-8 could shift under `python_version = "3.15"`. A4 re-runs everything; tests keep matching stable substrings.
- **mypy-API snippets target the running interpreter, member runs target the root config.** Both are 3.15 only after A1. Running a witness from the repo before A1 gives false `[name-defined]` errors on `frozendict` and `sentinel`.
- **`filterwarnings = error` surprises.** It can turn a pytest, mypy or plugin warning into a failure. Leaked file handles in ch10 negative tests raise `ResourceWarning` through pytest's unraisable hook, so every leaking test closes its handle in `finally`.
- **Mocks are not literally `Any`.** `reveal_type` shows the MagicMock union. Prose says "assignable to every type" and gives typeshed's reason; the domain row and CLAUDE.md wording are corrected at step 0 and A3.
- **The autospec message depends on parameter kind** (`missing a required argument` vs `missing a required positional-only argument`). The test matches the positional-only form because the Protocol uses `/`.
- **Typo examples on `assert_*` names are guarded by unittest.mock.** The vacuous example must use an attribute such as `loser.bok`, not `assert_called_once_wiht`.
- **The explicit Protocol subclass disagreement** (mypy `[abstract]`, runtime instantiates and returns `None`) could read as a bug report. State it as observed behaviour, witnessed both ways.
- **Sentinel name rules.** PEP 661 asks checkers to flag a mismatched name and mypy 2.4.1 doesn't; the prose makes no claim. The variable and string names must match.
- **The contextlib 3.15 change is new behaviour.** Cite What's New and test only 3.15 behaviour; the "before 3.15" sentence rests on the source plus the recorded 3.14.10 planning run.
- **Overlap** with chapters 2, 3 and 6 (Null Object, runtime_checkable, autospec), the Iterator chapter (generators), the asyncio chapter, the Decorator chapters, the Seams chapter and appendices B-D. Criterion 8 greps, and pointers go by title only.
- **Word budgets.** Ch9 and ch11 have dense sections; at most six excerpts each, and tables don't count toward the floor.
- **The `uv.lock` race.** 1a, 1b and 1c are sequenced, and the project names normalise to the package names.
- **Hub scope creep.** The PR also fixes pre-existing `referenced_by` gaps (Meszaros, *The Pragmatic Programmer*, Meyer). Keep it to data files.
- **Liquid.** f-strings with `{{` in prose code need `{% raw %}`; validate.py checks.
- **Attribution.** Woolf's year (1998 is the chapter year; one retailer lists 1997), the PEP author lists, the Fluent Python titles and the DeMillo citation all need fallbacks per criterion 16.
