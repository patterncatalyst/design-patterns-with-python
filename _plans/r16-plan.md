---
title: "r16 plan: chapters 33-34 (Seams in Python: monkeypatch, injection, and duck typing; Dependency-breaking techniques for modern Python)"
order: 16
output: false
render_with_liquid: false
---

# r16: chapters 33-34, Seams in Python: monkeypatch, injection, and duck typing; Dependency-breaking techniques for modern Python

Opus-planned 2026-11-06. Branch `release/r16`, cut from main at ad5287d (the r15 merge). This file is the source of truth for r16 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4, uv 0.13.7 and uv_build 0.13.7 match PyPI and python.org (checked 2026-11-06: pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, ruff 0.17.4 of 2026-11-05, mypy 2.4.1 of 2026-10-28, uv and uv-build 0.13.7 of 2026-11-03; python.org lists 3.15.0 to 3.15.2 and nothing later). S0 re-checks before any edit. `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch33: slug `33-seams-in-python`, title "Seams in Python: monkeypatch, injection, and duck typing", part 11 (`changing-inherited-code`), `kind = "hands-on"`, `has_example = true`, `status = "stub"`. The stub carries a `## How it works` heading that the draft drops.
- ch34: slug `34-dependency-breaking-techniques`, title "Dependency-breaking techniques for modern Python", part 11, `kind = "hands-on"`, `has_example = true`, `status = "stub"`. Same stub heading, also dropped.

`validate.py` SPINE for `hands-on`: Learning objectives, Why this matters, Build, run, observe, What you can do now, For deeper coverage. Unlike `pattern`, there's no "When not to use it" and no sidebar count is enforced (the count check runs only for `kind == "pattern"`). One figure is required, and the word ceiling is an error. The hands-on model is "Proving it works: pytest, pytest-mock, and mypy" (ch11), which has the same spine, a chapter-specific "when it proves less" section holding one sidebar, and experiments in Build, run, observe. "ISP, DIP, and dependency injection without a framework" (ch6) is the second model, with its "When the principle costs more than it buys" section.

Work items: PDP-133a-c (ch33 example, figure, prose) and PDP-134a-c (ch34), `todo` in `_plans/iteration-plan.md`.

## User decisions (owner to confirm)

0. **Step ids.** The steps are S0 to S7, as the owner asked. r01's steps table already has S0 to S15, all `done`, and `validate.py --claims` resolves `run: <id>` against the steps tables of every plan. So a token such as `run: S5` would resolve against r01's row and could never fail. Every r16 `run:` token therefore uses an id r01 doesn't have: `S1a`, `S1b`, `S5a` and `S5b`. Plain S0, S2, S3, S4, S6 and S7 appear only in this plan's table and are never cited from the reconciliation plan.

   **Recommend: keep S, with the suffixed tokens.** Alternative: the letter T, which no plan uses (`grep -cE '^\| T[0-9]' _plans/*.md` gives 0).

1. **Kinds and spine.** Both chapters stay `hands-on` with `has_example = true`.
   - ch33's H2s add `## Seams and enabling points`, `## Patch where the name is looked up`, `## monkeypatch or mock.patch`, `## Patches that miss`, `## What mypy checks at each enabling point` and `## When a patch is the wrong seam`, which holds the sidebar.
   - ch34's H2s add `## Pin what the code does today`, `## Parameterise the constructor`, `## Wrap the carrier with a different shape`, `## The class becomes a function`, `## Subclass and override` and `## Techniques Python makes unnecessary`, which holds the sidebar.
   - Each chapter has exactly one sidebar in the 2026-11-05 form: a problem, a nested prompt and at most one review line. A criterion enforces the count, because validate doesn't for hands-on chapters.

   **Recommend: yes.** Alternative: no sidebar, as in chapters 1 to 4. But the hands-on models (5, 6, 9, 11) all carry one, and PRD deck 301 names "easy seams" as part of the AI throughline.

2. **Mocks and monkeypatch are the subject: Option A, a scoped and stated exception.**
   - **The rule being relaxed.** Plans r10 to r15 forbade `mock`, `mocker` and `monkeypatch` in tests. CLAUDE.md doesn't forbid them: it says "Prefer `mocker.create_autospec` and say in the prose that mocks bypass the static check". ch3, ch6 and ch11 already use them.
   - **Where the exception applies, exactly:**
     - every test file of `examples/33-seams-in-python`, because the patch is what's under test;
     - in `examples/34-dependency-breaking-techniques`, only the `legacy` branch of the `step` fixture in `tests/conftest.py`, because the legacy engine takes no parameters, so a namespace patch is its only enabling point.
   - **Where it does not apply:** nowhere else in ch34's tests, and never in any `src`. Criterion 2's greps enforce both limits.
   - **Library order.** pytest-mock's `mocker` is the default, per PRD section 9. One ch33 test uses `unittest.mock.patch` as a context manager, because legacy row 14 names it and because its typing differs (evidence D). Every `mocker.patch` that replaces a function passes `autospec=True`, apart from the tests that show what a plain patch accepts.
   - **Determinism is unchanged.** monkeypatch and mocker undo their changes at teardown, the reload facts run in a fresh interpreter (decision 7), there are no threads, no sleeps and no clock.

   **Recommend: Option A.** Option B, witnessing patching only in reduced models or a separate comparison test, would teach the mechanism without running it on the real legacy modules. Row 14 asks for "an experiment with `unittest.mock.patch` on both targets", and the target-resolution facts (evidence B) depend on real dotted import paths.

3. **The legacy code lives in `src`, as `legacy.py` in each member.** CLAUDE.md separates "the legacy-code part, where inherited code is the subject" from the comparison rule, so the legacy engine isn't a comparison form and isn't held to one excerpt.
   - **What makes it legacy is structure, not sloppiness:**
     - a module-level `from <pkg>.fastline import request_quote`;
     - a module import `from <pkg> import airco`, with the call written `airco.price(...)`;
     - both carrier calls hard-wired inside `RateEngine.quote`;
     - a margin captured as a default argument (`margin: Decimal = MARGIN`).
   - **It still passes every gate.** It is fully typed, so it passes `mypy --strict`, ruff and the idiom scan. In evidence I, the spike's legacy shape passed ruff with "All checks passed!" and mypy found nothing in it.
   - **The stand-in carrier SDKs do no I/O.** `fastline.request_quote` and `airco.price` raise `CarrierTimeoutError` with the carrier's name, in the place where a real SDK would open a connection. The docstrings say so.
   - **Each member has its own copy.** ch34 carries a copy of ch33's legacy engine, identical apart from the package name, so each member stands alone.

   **Recommend: yes.** Alternative: the legacy engine in conftest. That fails, because patch string targets need real dotted import paths, and conftest under `--import-mode=importlib` has no stable one.

4. **ch34 runs one characterisation table across the steps.**
   - **The steps.** Each is a complete `src` module that applies one technique to the module before it: `legacy.py`, then `parameterised.py` (Parameterize Constructor), then `wrapped.py` (the AIRCO SDK wrapped into the shared `CarrierQuoter` shape), then `rating.py` (the class becomes the function `quote`, with `partial` at the root).
   - **The table.** `CHARACTERISATION_ROWS` lives in `tests/test_characterisation.py`. The `step` fixture params are `legacy|parameterised|wrapped|function|subclass`. Each param wires the same SDK-level fakes at that step's enabling point:
     - a namespace patch for `legacy`;
     - constructor keywords for `parameterised`;
     - keywords plus `partial(airco_quote, price=fake)` for `wrapped`;
     - a `quoters` mapping for `function`;
     - overridden methods for `subclass`.
   - **Comparison code.** The subclass form is the one comparison form, a conftest pair `_ExtractedCallsRateEngine` and `_FakeCarrierRateEngine`. Its excerpt is the chapter's one comparison excerpt.
   - **Mutants.** The conftest mutants `_GramsRoundedRateEngine` and `_HalfEvenRateEngine` give test 3, which proves the table can fail.

   **Recommend: yes.** Alternatives:
   - the steps as conftest classes, which would turn the lesson's code into fixtures;
   - one `src` module edited in place, which leaves nothing to run the table against before and after.

5. **The final step has no default carriers.** `quote(consignment, /, *, quoters, margin=MARGIN)` requires `quoters`, `STANDARD_QUOTERS` is a read-only `frozendict`, and `quote_standard = partial(quote, quoters=STANDARD_QUOTERS)` is the root binding.
   - mypy reports a missing `quoters` as `[call-arg]` (test 31). This is the same edge the anti-patterns chapter shows for a missing `tariff`.
   - The `parameterised` step keeps defaults on purpose, because that is how Parameterize Constructor keeps existing callers working. Test 24 shows the cost: a test that forgets a fake reaches the real SDK.

   **Recommend: yes.** Alternative: keep the defaults to the end. That leaves the forgotten-fake hazard in the lesson's final code.

6. **Legacy row 15 closes adjusted.** The seams that need no source change are names looked up at call time in a module namespace: a `from`-imported function, a module attribute reached through a module object, and the module object itself, which any duck-typed object can stand in for. `monkeypatch` or `patch` enables each of them.
   - A value read at definition time can't be reached that way. A default argument is captured when the class is defined (test 10).
   - An injected callable is a seam only once the code takes a parameter. Adding one is a source change, the first technique of ch34 (tests 21 and 24).

   **Recommend: yes.** Alternative: keep "injected callables" in row 15 and add a parameter to ch33's legacy code. Then it wouldn't be the unchanged legacy code the chapter studies.

7. **Reload hazards are witnessed in a fresh interpreter.** A test runs `subprocess.run([sys.executable, "-I", "-c", SCRIPT])`, as the singledispatch chapter's test does. The script reports its facts through `sys.stdout.write`, never `print(`, and the test asserts the exact list it prints. `importlib.reload` never runs in the pytest process, so no test sees a replaced `RateEngine` class.

   **Recommend: yes.** Alternative: reload in-process with careful teardown. That risks class-identity leaks into other tests, which pass or fail by test order.

8. **Feathers credit.** *Working Effectively with Legacy Code* (Prentice Hall, 2004) is in `bibliography.html`. Chapter titles were checked on the InformIT table of contents (evidence K): "The Seam Model", "I Need To Make a Change but I Don't Know What Tests To Write", "My Application Is All API Calls" and "Dependency Breaking Techniques". The seam and enabling-point definitions were checked in the publisher's sample of "The Seam Model".
   - Both are paraphrased only, never quoted, and cited by chapter title. Reader text gives no chapter numbers, for this book or for Feathers's.
   - The individual technique names of "Dependency Breaking Techniques", and the count of 24, were not verified. They stay bracketed: [Parameterize Constructor; Replace Function with Function Pointer; Extract Interface; Subclass and Override Method; Encapsulate Global References; Introduce Static Setter; Link Substitution; Skin and Wrap the API (the "My Application Is All API Calls" chapter)].
   - S5b verifies each name before using it. Any name it can't verify is described, not named. No count appears in reader text.
   - The term "characterisation test" is used in British spelling and attributed to Feathers by idea. His spelling is never quoted.

   **Recommend: yes.**

9. **Scope cuts.** Recorded here and in the S2 spikes note, not in either chapter:
   - `contextvars` as a seam. It was spiked (evidence H), but the outline doesn't name it, and asyncio context belongs to "asyncio and the patterns".
   - `patch.dict`, `patch.multiple`, `mock.seal`, `AsyncMock`, and injection through `sys.modules` or import hooks.
   - Golden files and approval libraries, Fowler's refactoring contrast, and any experiment that changes a rounding rule. "Fowler vs Feathers, contrasted and combined" owns that; domain row 35's failing test is a rounding change.
   - The strangler adapter and parity tests ("Refactor or rewrite").
   - Coverage and mutation-testing tools.
   - Free-threading.

   **Recommend: yes.**

10. **No cross-language wording.** The outline's "fewer of Feathers' techniques than in C++/Java" is reframed in time: Feathers's catalogue assumes a call site whose target is fixed before the program runs, and Python looks a global name up when the call runs.
    - Feathers's other seam kinds are named only as "other kinds Feathers describes", with no explanation of build tools.
    - Criterion 14's grep bans the language names, "classpath", "preprocessor" and "linker".

    **Recommend: yes.**

11. **Domain names** come from `_plans/shipping-domain-model.md` rows 33-34, the Carrier and Rating areas and the series supporting names. There's no new domain area and no new carrier code.
    - **Both members:**
      - `ConsignmentId`;
      - frozen slotted `Consignment(id, zone, weight_kg: Decimal)`;
      - `Money(amount: Decimal, currency: str = "EUR")`;
      - `RateQuote(consignment_id, carrier: str, total: Money)`;
      - `CarrierTimeoutError`;
      - `RateEngine`;
      - `MARGIN = Decimal("1.10")`;
      - stand-in SDKs `fastline.request_quote(zone: str, weight_kg: Decimal) -> Decimal` and `airco.price(*, destination: str, grams: int) -> int` (cents).
    - **New supporting names:** `CarrierQuoter` (a `type` alias, `Callable[[str, Decimal], Decimal]`), `AircoPrice` (a callback Protocol, keyword-only), `airco_quote`, `STANDARD_QUOTERS`, `quote`, `quote_standard`.
    - **Test-only:** `_FakeAirco`, `_WrongAirco`, `_ExtractedCallsRateEngine`, `_FakeCarrierRateEngine`, `_GramsRoundedRateEngine`, `_HalfEvenRateEngine`, `CarrierAnswers`.
    - `Weight` isn't reused, because a `Decimal` kilogram field keeps the gram conversion visible. Zones `EU` and `ASIA`, prices and cents are illustrative.

    **Recommend: yes.**

Also proposed for the owner (no decision needed unless declined):
- **No new books.** Feathers, Fowler's *Refactoring* 2nd ed., Meszaros and Martin are already in `bibliography.html`. Fowler isn't cited in either chapter, because the contrast belongs to "Fowler vs Feathers, contrasted and combined".
- **Web sources fetched 2026-11-06** (evidence K): the `unittest.mock` page ("Where to patch", autospeccing, `spec_set`), the pytest monkeypatch how-to, the `importlib` reload entry and the `functools.partial` entry.
- **At S2, a dated r16 note in `_plans/spikes.md`** records evidence B to J and the scope cuts of decision 9.

## Planning evidence

The planning run was read-only, so no scratch directory was created and nothing was left to delete. Every probe ran as inline code, with the session scratchpad (`<scratchpad>`) as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `<repo>/.venv/bin/python -I -c CODE` (one probe fed the code on stdin with `-I -`), version `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- mypy: `<repo>/.venv/bin/python -I -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET`, version `mypy 2.4.1 (compiled: yes)`.
- ruff: `<repo>/.venv/bin/ruff check --isolated --no-cache --line-length 100 --select E,F,W,I,UP,B,SIM,RUF,PT,N --target-version py315 --output-format concise --stdin-filename probe.py -`, ruff 0.17.4.
- pytest 9.2.0. `pytest.MonkeyPatch.context()` was used directly in the probes.

Multi-module probes built modules in memory: `types.ModuleType` entries in `sys.modules` and, for reload, a small `MetaPathFinder` and `Loader` serving source from a dict. They're reduced models. Module names in messages (`engine`, `carriers`) become the member's dotted names, and on a real package, `<module ...>` reprs include a file path (Risks). Line numbers will differ and are never asserted. Every output is a prediction for the member until the build quotes it as observed.

**A. Pins.** `pytest 9.2.0 2026-10-27`, `pytest-mock 3.17.0 2026-10-17`, `ruff 0.17.4 2026-11-05`, `mypy 2.4.1 2026-10-28`, `uv 0.13.7 2026-11-03`, `uv-build 0.13.7 2026-11-03`. python.org: 3.15.0, 3.15.1, 3.15.2. No bump.

**B. Where a patch lands (row 14).** `carriers.fastline_quote` raises `ConnectionError("FASTLINE called for real")`. `engine_from` does `from carriers import fastline_quote`, and `engine_mod` does `import carriers` and calls `carriers.fastline_quote`. Each line is `mock.patch(target, fake)`, where the fake returns `Decimal("25.00")`:
```
from-import, patch carriers.X          ConnectionError: FASTLINE called for real
from-import, patch engine_from.X       Decimal('25.00')
module import, patch carriers.X        Decimal('25.00')
module import, patch engine_mod.carriers.X Decimal('25.00')
module import, patch engine_mod.X -> AttributeError <module 'engine_mod'> does not have the attribute 'fastline_quote'
create=True -> ConnectionError FASTLINE called for real
restored: True
```
- A `from`-import makes a second name in the using module, so the patch must target that module.
- A module import looks the name up on the defining module at call time, so the patch targets the defining module.
- `create=True` makes a name nothing reads.

**C. monkeypatch targets, guards and autospec.** `carriers.fastline_quote(zone: str, weight_kg: Decimal) -> Decimal` raises; `engine` from-imports it:
```
monkeypatch string engine.fastline_quote     25.00
monkeypatch object (engine, name)            25.00
monkeypatch object (carriers, name)          ConnectionError: FASTLINE called for real
monkeypatch typo name, object form           AttributeError: <module 'engine'> has no attribute 'fastline_qoute'
monkeypatch typo name, string form           AttributeError: 'module' object at engine has no attribute 'fastline_qoute'
monkeypatch raising=False typo               None
monkeypatch bad module string                ModuleNotFoundError: No module named 'enginex'
restored after context                       True
autospec right call                          25.00
autospec wrong arity                         TypeError: missing a required argument: 'weight_kg'
autospec wrong keyword                       TypeError: missing a required argument: 'weight_kg'
plain patch wrong arity                      25.00
plain patch typo assert                      AttributeError: 'assert_caled_once' is not a valid assertion. Use a spec for the mock if 'assert_caled_once' is meant to be an attribute
autospec typo assert                         AttributeError: 'function' object has no attribute 'assert_caled_once'
autospec unknown attr                        AttributeError: 'function' object has no attribute 'nonsense'
spec_set set unknown attr                    AttributeError: Mock object has no attribute 'nonsense'
spec_set wrong arity call                    <MagicMock name='fastline_quote()' id='140704237881056'>
patch typo target                            AttributeError: <module 'engine'> does not have the attribute 'fastline_qoute'
```
- The string and object forms of `monkeypatch.setattr` both refuse a missing name by default, and the two messages differ.
- `raising=False` creates the misspelt name silently.
- Only autospec checks the call signature. `spec_set=True` refuses unknown attributes but accepts a wrong-arity call.
- The member never asserts a mock `id`.

**D. mypy on `unittest.mock.patch`, `monkeypatch` and direct assignment.** Exit 1:
```
<string>:8: note: Revealed type is "unittest.mock.MagicMock | unittest.mock.AsyncMock"
<string>:10: note: Revealed type is "unittest.mock.MagicMock | unittest.mock.AsyncMock"
<string>:12: note: Revealed type is "unittest.mock.MagicMock | unittest.mock.AsyncMock"
<string>:14: note: Revealed type is "def () -> str"
<string>:19: note: Revealed type is "str"
<string>:22: error: Function is missing a type annotation for one or more parameters  [no-untyped-def]
<string>:31: error: Incompatible types in assignment (expression has type "Callable[[], int]", variable has type "Callable[[], str]")  [assignment]
<string>:31: error: Incompatible return value type (got "int", expected "str")  [return-value]
```
- **The patch, by form.**
  - Lines 8-12: `patch("os.getcwd")`, with `autospec=True`, and `patch.object(os, "getcwd", autospec=True)` as context managers all reveal the `MagicMock | AsyncMock` union.
  - Line 14: with `new=lambda: "/x"`, the revealed type is the replacement's.
  - Line 19: inside an `@patch`-decorated test, `os.getcwd()` is still `str`. mypy doesn't model the patch.
  - Line 22: an unannotated decorator-injected mock parameter is `[no-untyped-def]` under `--strict`. Annotated as `MagicMock`, it passes.
- **Silent.** `monkeypatch.setattr(os, "getcwd", lambda: 42)`, `monkeypatch.setattr("os.getcwd", 42)` and `monkeypatch.setattr(os, "getcwdd", ...)` give nothing.
- **Checked.** A direct `os.getcwd = lambda: 42` is checked (line 31). With a `lambda: "/x"` it passes.

**E. mypy on `mocker.patch` and on fakes at a typed parameter.** Exit 1:
```
<string>:11: note: Revealed type is "unittest.mock.MagicMock | unittest.mock.AsyncMock | unittest.mock.NonCallableMagicMock"
<string>:13: note: Revealed type is "unittest.mock.MagicMock | unittest.mock.AsyncMock | unittest.mock.NonCallableMagicMock"
<string>:27: error: Argument 1 to "engine" has incompatible type "Callable[[str], Decimal]"; expected "FastlineQuote"  [arg-type]
<string>:27: note: "FastlineQuote.__call__" has type "Callable[[str, Decimal], Decimal]"
<string>:29: error: Argument 1 to "engine" has incompatible type "Callable[[Any], Decimal]"; expected "FastlineQuote"  [arg-type]
<string>:29: note: "FastlineQuote.__call__" has type "Callable[[str, Decimal], Decimal]"
<string>:34: error: Argument 1 to "engine2" has incompatible type "Callable[[str], Decimal]"; expected "Callable[[str, Decimal], Decimal]"  [arg-type]
```
- `mocker.patch` adds `NonCallableMagicMock` to the union.
- `mocker.patch("os.getcwdd", return_value=1)` (line 14) gives nothing: a misspelt target string isn't checked.
- A one-parameter fake passed where a callback Protocol or a `Callable` alias is expected is `[arg-type]` (lines 27, 29, 34). A matching function or a two-parameter lambda passes.
- The same fake passed to `monkeypatch.setattr` (line 37) gives nothing.

**F. `importlib.reload` (decision 7).** Served by an in-memory loader:
```
1 carriers patched then reloaded; carriers.fastline_quote is fake: False
2 after reload under patch: ConnectionError FASTLINE called for real
3 old instance isinstance new class: False old_cls is new: False
4 attribute set before reload survives: True
5 engine.fastline_quote is carriers.fastline_quote after reloading carriers: False | engine.carriers is carriers: True
```
- A reload re-executes the module, overwriting a live patch (lines 1-2).
- An instance made before the reload isn't an instance of the reloaded class (line 3).
- The module dictionary is kept (line 4).
- Reloading the defining module doesn't rebind a `from`-import elsewhere, though a module reference still points at the same module object (line 5).

**G. monkeypatch teardown after a reload.**
```
teardown restored the pre-reload function: True | not the reloaded one: True
module state list replaced by reload: True
```
Undoing a patch after a reload puts back the object from before the reload. Module-level state such as a list is replaced by the reload.

**H. Default arguments, `partial` and `contextvars`.**
```
module constant read at call time, patched           20
module constant captured as default, patched         11.00
default-argument carrier after patching the name     TimeoutError FASTLINE did not answer
default-argument carrier passed a fake               25.00
partial binds the fake                               26.00
partial keyword still overridable                    27.00
__defaults__ / __kwdefaults__: (Decimal('1.10'),) True
contextvar set                                       30.00
contextvar reset                                     TimeoutError FASTLINE did not answer
contextvar in copied context only                    (Decimal('31'), 'outside:')
outside                                              TimeoutError FASTLINE did not answer
```
- A default is evaluated once, when the function or class is defined, so patching the module name afterwards reaches neither a captured constant nor a captured carrier function. Passing the argument does.
- A `partial`'s bound keyword can be overridden at the call.
- `contextvars` works as a seam, but it's a scope cut (decision 9).

**I. One characterisation table across five forms (decision 4).** A reduced model of the legacy engine, the three steps and the subclass form. The rows are zone, weight in kilograms, the FASTLINE price and the AIRCO answer in cents:
- `EU 12.5 25.00 2800`
- `ASIA 12.5 60.00 5450`
- `EU 1 20.00 2000`
- `EU 1 10.15 2000`
- `EU 0.0004 30.00 1`

Every form printed the same list; the legacy line was:
```
legacy [('FASTLINE', '27.50', [('AIRCO', 'EU', 12500), ('FASTLINE', 'EU', '12.5')]), ('AIRCO', '59.95', [('AIRCO', 'ASIA', 12500), ('FASTLINE', 'ASIA', '12.5')]), ('AIRCO', '22.00', [('AIRCO', 'EU', 1000), ('FASTLINE', 'EU', '1')]), ('FASTLINE', '11.17', [('AIRCO', 'EU', 1000), ('FASTLINE', 'EU', '1')]), ('AIRCO', '0.01', [('AIRCO', 'EU', 0), ('FASTLINE', 'EU', '0.0004')])]
all equal: True
```
- **Behaviour the table pins:**
  - a tie goes to AIRCO, because the key is `(price, code)`;
  - the margin is rounded half up (10.15 x 1.10 = 11.165 becomes 11.17, where half-even gives 11.16);
  - grams are truncated by `int`.
- **Grams row.** The member uses 0.0006 kg instead of 0.0004, because `int` and `round` disagree on 0.6 grams (0 against 1), so the grams mutant in test 18 fails it.
- **Calls.** They're compared as a sorted list of tuples.

**J. Subclass and override.** mypy exit 1:
```
<string>:28: error: Method "_fastline_qoute" is marked as an override, but no base method was found with this name  [misc]
<string>:39: error: Signature of "_fastline_quote" incompatible with supertype "RateEngine"  [override]
```
- With `@override`, a misspelt method name is `[misc]`. Without it, mypy reports nothing for the same typo (line 33). A wrong signature is `[override]` either way.
- ruff on the whole legacy-shaped model gave `All checks passed!`.
- At run time the typo falls through to the base method: `CarrierTimeoutError FASTLINE did not answer for EU`.

**K. Sources fetched 2026-11-06.** curl with `-L`, tags stripped, whitespace collapsed. Prose agents re-fetch, the page text wins, and a quotation stops where the page's sentence stops.
- **`unittest.mock`** (https://docs.python.org/3/library/unittest.mock.html, banner "Python 3.15.2 documentation"), section "Where to patch":
  - "patch() works by (temporarily) changing the object that a name points to with another one."
  - "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined."
  - "spec_set: A stricter variant of spec."
  - "A more powerful form of spec is autospec."
- **pytest monkeypatch how-to** (https://docs.pytest.org/en/stable/how-to/monkeypatch.html):
  - "The monkeypatch fixture helps you to safely set/delete an attribute, dictionary item or environment variable, or to modify sys."
  - "All modifications will be undone after the requesting test function or fixture has finished."
- **importlib** (https://docs.python.org/3/library/importlib.html), `reload`:
  - "When a module is reloaded, its dictionary (containing the module’s global variables) is retained."
  - "If a module imports objects from another module using from … import …, calling reload() for the other module does not redefine the objects imported from it". The page's sentence continues after an em dash, so the quotation stops at "from it".
  - "If a module instantiates instances of a class, reloading the module that defines the class does not affect the method definitions of the instances". This sentence also continues after an em dash; quote at most up to "instances".
- **functools** (https://docs.python.org/3/library/functools.html), `partial`: "Return a new partial object which when called will behave like func called with the positional arguments args and keyword arguments keywords." The ISP and DIP chapter already teaches `partial` injection, so ch34 points there and quotes this only if it needs the definition.
- **Feathers, *Working Effectively with Legacy Code*** (Prentice Hall, 2004).
  - InformIT table of contents (https://www.informit.com/store/working-effectively-with-legacy-code-9780131177055) lists Part I "The Mechanics of Change" with "4. The Seam Model". Part II includes "13. I Need To Make a Change but I Don't Know What Tests To Write" and "15. My Application Is All API Calls". Part III is "25. Dependency Breaking Techniques".
  - The publisher's sample of "The Seam Model" defines a seam as a place where behaviour can be altered without editing in that place, and says every seam has an enabling point, where the choice of behaviour is made. It names object seams, among other kinds.
  - Paraphrase only. Reader text cites chapter titles, never numbers.
  - The O'Reilly search confirms the book (Pearson, 2004-09-22, 464 pages). The O'Reilly page itself returned 403. Technique names are unverified (decision 8).
- **Typeshed's `unittest/mock.pyi` comment** is already quoted by "Proving it works: pytest, pytest-mock, and mypy". ch33 points there and doesn't re-quote it.

**L. Repo facts.**
- **Reconciliation.**
  - Rows run 1-187, so r16 adds 188-198.
  - Legacy rows 14, 15 and 16 (ch33, ch33, ch34) are `open` and belong to r16. `CLAIMS_FIRST_ENFORCED = 47`, so they're legacy rows.
  - No other open row names ch33 or ch34. Rows 5, 17-27 belong elsewhere and aren't touched.
- **Figures.** `_data/diagrams.yml` has 33 entries; r16 makes 35.
- **Test names.** 783 unique `def test_` names across `examples` and `spikes`, with the three known duplicates unchanged. All 41 names in the Example spec were checked, and none clashes.
- **Members.** No member uses project `seams` or `dependency-breaking`, or package `seams` or `dependency_breaking`.
- **Promises made to these chapters, which they must honour:**
  - "Proving it works: pytest, pytest-mock, and mypy": "When the fix is to patch a module's name rather than the environment, that's a seam, and [ch33] compares the options." ch33 must compare a patch with a parameter, in `## When a patch is the wrong seam`.
  - "Singleton: module, Borg, and metaclass": "[ch33] covers the alternative, patching module state, and what it costs." ch33 must state the costs, each with a test.
  - The part blurb: "Seams in Python, dependency-breaking techniques, Fowler and Feathers contrasted and combined, and the decision between refactoring and rewriting."
  - `bibliography.html` Feathers note: "Seams, characterization tests, and the dependency-breaking techniques the changing-inherited-code chapters adapt to Python, where monkeypatching and duck typing change which seams are cheap." Its "Citation discipline" says Feathers is cited "for the full dependency-breaking technique", as a pointer and not a displacing summary.
  - **Circularity rule.** "Proving it works" and "Singleton" defer patching module state here, so ch33 owns it and never points back to either for patching. ch33 may point to "Proving it works" for the double table and `monkeypatch.context()`, which that chapter owns and doesn't defer.
- **Already taught, so not repeated.** Each gets a pointer by title and at most one sentence:
  - "ISP, DIP, and dependency injection without a framework": constructor injection as a dataclass field, `partial` and closures, the composition root, Fowler's injection article, mypy's `partial` assignment gap, and an autospec bypassing mypy.
  - "Protocol, duck typing, and structural typing with mypy": structural conformance and callback Protocols with `/`.
  - "Proving it works": the double matrix (fake, `Mock`, `Mock(spec=)`, autospec), the typeshed comment and `monkeypatch.context()`.
  - "Strategy: the callable": a callable as the varying part.
  - "SRP, OCP, and LSP in Python": `@override` and override signatures.
  - "Anti-patterns and pattern misuse": the service locator moves a missing dependency from mypy to the first call. ch34 may echo this for `quoters` in one clause.
- **Stubs whose ground must not be taken or described:**
  - "Fowler vs Feathers, contrasted and combined": the contrast and golden values; domain row 35's rounding failure.
  - "Refactor or rewrite": the strangler adapter and parity.
  - "asyncio and the patterns".
  - "Working with AI and LLM tools".
  - "Mocking reference: unittest.mock and pytest-mock" (Appendix C): ch33 may point to it for the rest of the API, as "Proving it works" does.
- **Status board hygiene.** r15 is merged (ad5287d), but `iteration-plan.md` marks r15 "(active)" and PDP-131a to 132c `active`, and r15's R7 reads `todo`. The orchestrator closes them at S0.

## What is new in each chapter

**ch33 (seams that need no source change, and what each costs).** "Proving it works" uses `monkeypatch.context()` once for the environment, and the ISP and DIP chapter injects through parameters. This chapter adds:
- **Feathers's seam and enabling point, in Python.** Every global name a function looks up when it runs is a seam, and the enabling point is a rebinding of that name in the namespace where it's looked up.
- **Where to patch.** It's decided by the import form: a `from`-import needs the using module, and a module import needs the module that defines the name.
- **The guards.**
  - monkeypatch refuses a missing name unless told otherwise.
  - `patch` refuses a missing name unless told to create it.
  - autospec, and only autospec, refuses a wrong call.
  - Both undo their changes.
- **Patches that miss.** A default captured at definition, a reload, and a duck-typed object standing in for a whole module, which is checked only when called.
- **What mypy checks at each enabling point.** Nothing for a patch, the assignment for a direct rebinding, and the shape for a parameter.
- **The comparison the earlier chapters promised.** A patch gets the first test around code that can't be changed yet. A parameter is the seam to keep.

**ch34 (Feathers's techniques in Python, each step under one characterisation table).** This chapter adds:
- **A characterisation table** pinning what the legacy engine does today, including a tie-break, half-up rounding, gram truncation and a timeout that fails the whole quote.
- **One technique per step, each a real module:**
  - parameterise the constructor, with production defaults;
  - wrap the AIRCO SDK into one `CarrierQuoter` shape;
  - the class becomes a function whose carriers are a required mapping, bound with `partial` at the root.
- **The same table at every step,** and a test that the table fails when a step changes behaviour.
- **Subclass and override** as the comparison: it passes the table, and a misspelt override reaches the real carrier, which mypy reports only with `@override`.
- **Which techniques Python makes unnecessary.**

## Approach

- **Thesis wording.**
  - ch33 says Python looks a global name up when the call runs, so the legacy engine already has seams. Patching is their enabling point, and it works when the patch lands where the name is looked up. mypy checks none of it, so a patch is how you get the first test, and a parameter is the seam you keep.
  - ch34 says a dependency-breaking step changes structure, not behaviour, and the evidence is one characterisation table run at every step. Python turns several of Feathers's techniques into a keyword parameter, a function value or a patch.
- **Credit.**
  - Feathers by title and topic, paraphrase only (decision 8).
  - The `unittest.mock`, pytest monkeypatch, `importlib` and `functools` pages, with exact quotations from fetched pages.
  - No GoF and no Fowler in either chapter.
- **One uv member per chapter.** Each is standalone and named after its package (the r13 correction), so no member needs a `[tool.*]` table:
  - `examples/33-seams-in-python` (project `seams`, package `seams`);
  - `examples/34-dependency-breaking-techniques` (project `dependency-breaking`, package `dependency_breaking`).
- **mypy witnesses** copy the `_run` helper from `examples/32-anti-patterns-and-pattern-misuse/tests/test_static.py`: `mypy_path` set to the member's `src`, `--strict --warn-unreachable`, `--cache-dir os.devnull`. `_codes(stdout)` returns a sorted list.
  - Each test asserts the exit status, an exact `_codes()` list and one or two stable substrings. It never asserts line numbers or optional notes.
  - Exception: tests that are about a revealed type assert the `Revealed type is "..."` substring, as r14's test 22 did.
  - Executor check: a snippet that imports `pytest` or `pytest_mock` resolves through the running interpreter's site-packages under `_run`.
- **Static-test mutation rule (r12-r15).** Every static test names, in the Example spec, the thing its prose credits and a plausible mutation that makes the test fail.
  - **An exit-0 test also exercises the hazard at run time,** in the same test, and asserts `_codes(stdout) == []`.
  - A reduced-model test credits mypy only, and the prose names it as a reduced model.
- **Repair rule (r12).** After every repair, the validator re-reads the paragraph and the close bullets that depend on it. Scope words ("every", "only", "never", "all", "both", "nothing", "any") each name the test that witnesses the whole scope, or are cut. "Any object with the right method" is witnessed by two objects only, so prose says "an object with the right method", not "any".
- **Excerpt rule.** No excerpt can break an owner decision:
  - no `monkeypatch`, `mock` or `patch` in a `src` excerpt;
  - no second comparison excerpt in ch34 (the subclass form is the one);
  - no ch34 excerpt that fixes behaviour inside a dependency-breaking step;
  - no reader-facing text naming another language.

  S6 checks each excerpt against decisions 2-5 and 10.
- **Comparison code** (the owner's 2026-11-04 rule).
  - The ch34 subclass form is real, runs on the shared table as a `step` fixture param, and has one excerpt.
  - The legacy engine is the subject, not a comparison (decision 3).
  - Shared tables live in the test module that uses them, and conftest holds only fixtures and forms (the r13 importlib correction).
  - Test modules import conftest types only under `TYPE_CHECKING` and get classes through fixtures (the r14 Q1a precedent).
- **Negative witness rule.** Every check or pinned behaviour in `src` has a test that fails when it's deleted or changed. The deletion tables (S1a, S1b) name the test and say why it sees the change. A row whose witness was predicted but not run is marked "executor check".
- **A measurement test must be able to fail.** "The table pins behaviour" is witnessed by test 18, which runs the table against two mutants and asserts the exact failing row ids. "Every step preserves behaviour" is witnessed by test 16 together with the ch34 deletion table, in which every step module appears.
- **Determinism.**
  - No `sleep`, `time.time`, `perf_counter`, `datetime.now`, threads or `print(` in tests. The reload script writes through `sys.stdout.write`.
  - `monkeypatch` and `mocker` appear only where decision 2 allows.
  - `importlib.reload` runs only in the fresh-interpreter script (decision 7).
  - Failing assertions compare lists or tuples of strings, never a set repr.
  - No assertion names a mock `id` or a module file path.
  - `filterwarnings = ["error"]` stays active.
- **Counts** of test functions and cases come from the code, and the pytest summary line wins.

Rejected:
- In either `src`: `monkeypatch`, `mock`, `patch`, `Any`, `cast`, `print(`, `Optional`, `importlib`, `contextvars`, `global`, `sys.modules`.
- In ch34's `src`: `ABC`, `abstractmethod`, a subclass-and-override hook.
- In both: a rounding-rule experiment (decision 9), claims about model output, and timing anywhere.

## Per-chapter spec

### ch33: Seams in Python: monkeypatch, injection, and duck typing (hands-on, has_example = true)

Thesis: Python looks a global name up when the call runs. So code that was never written for tests still has seams: a `from`-imported function, a module attribute, and a module object, for which an object of the right shape can stand in. The enabling point is a patch in the namespace where the name is looked up. mypy checks none of it, and a value read at definition time is out of reach. Use the patch to get the first test, and make a parameter the seam you keep.

Sections (about 2,350 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~110), five bullets, one per close bullet:
   - name a seam and its enabling point, and find the seams the legacy `RateEngine` already has;
   - patch a name where it's looked up, and predict from the import form when a patch has no effect;
   - choose between `monkeypatch` and `mock.patch`, and use the guards that turn a silent miss into an error;
   - recognise patches that can't reach their target: a default captured at definition, and a reload;
   - say what mypy checks at each enabling point, and when to replace a patch with a parameter.
2. `## Why this matters` (~180). Intent first: a rating engine written before anyone tested it asks FASTLINE and AIRCO for prices and adds a margin. Three failures:
   - a test of it reaches the carrier (test 1);
   - a patch on the module that defines the carrier call changes nothing (test 3);
   - a patched margin is ignored (test 10).
3. Figure plus one paragraph (~50).
4. `## Seams and enabling points` (~300).
   - Paraphrase Feathers's seam and enabling point, citing "The Seam Model" in *Working Effectively with Legacy Code* by title.
   - In Python, a global name a function looks up when it runs is a seam, and rebinding it in that namespace is the enabling point. Say "other kinds Feathers describes" without explaining them (decision 10).
   - Excerpt `legacy.py`: the imports, `MARGIN` and `RateEngine`.
   - The object seam, a parameter a caller fills, is the ISP and DIP chapter's subject (one pointer by title), and "Protocol, duck typing, and structural typing with mypy" covers checking its shape (one clause).
5. `## Patch where the name is looked up` (~400).
   - Quote the mock docs' "works by (temporarily) changing" sentence and its "basic principle" sentence.
   - Patching `seams.legacy.request_quote` replaces FASTLINE (test 2). Excerpt test 2.
   - Patching `seams.fastline.request_quote` leaves the engine calling the real carrier (test 3).
   - AIRCO is reached through the `airco` module object, so its patch goes on `seams.airco` (test 4).
   - `unittest.mock.patch` follows the same rule (test 5).
   - The import form decides the target, so changing an import moves the test's patch (experiment b).
6. `## monkeypatch or mock.patch` (~350).
   - Quote the monkeypatch how-to's "safely set/delete" and "undone" sentences.
   - The string and object forms (test 2).
   - The default refuses a misspelt name (test 6), and `raising=False` creates a name nothing reads (test 7).
   - The changes are undone when the context ends (test 14).
   - `patch` refuses a name the module doesn't have, and `create=True` makes one nothing reads (test 8).
   - `autospec=True` refuses a call with the wrong signature where a plain patch accepts it (test 9). Quote "A more powerful form of spec is autospec." and the `spec_set` sentence.
   - pytest-mock's `mocker.patch` resolves targets the same way. One pointer to "Proving it works: pytest, pytest-mock, and mypy" for the double table, and one to "Mocking reference: unittest.mock and pytest-mock".
7. `## Patches that miss` (~300).
   - A margin captured as a default argument isn't reached by patching `MARGIN`, and passing `margin=` is (test 10).
   - A reload overwrites a live patch, doesn't rebind a `from`-import, and leaves an old instance on the old class (test 11). Quote the `importlib` "dictionary ... is retained" sentence and the `from … import …` sentence, stopping at "from it".
   - Duck typing at a module seam: an object with a `price` method stands in for the `airco` module, and an object without one fails only when called (test 15).
8. `## What mypy checks at each enabling point` (~300). These are reduced models where marked.
   - `monkeypatch.setattr` with a wrong-shape replacement passes mypy (test 16), as does a misspelt target string (test 21).
   - A direct `legacy.request_quote = wrong` is reported (test 17).
   - `patch` is typed as a `MagicMock` union, or as its replacement when given `new` (test 18).
   - A decorator-injected mock needs an annotation under `--strict` (test 19).
   - A fake passed to a Protocol-typed parameter is checked (test 20, reduced model).
   - One pointer to "Proving it works" for why a mock is assignable to every type. Don't re-quote typeshed.
9. `## When a patch is the wrong seam` (~200). This is the comparison promised by "Proving it works" and "Singleton", stated as costs, each with a test:
   - the target is a string tied to the import form (tests 3, 5, experiment b);
   - mypy checks neither the target nor the replacement (tests 16, 21);
   - a default or a reload defeats it (tests 10, 11);
   - a parameter is checked by mypy (test 20).

   A patch is the way to get the first test around code that can't change yet. The next step is a parameter: one pointer by title to "Dependency-breaking techniques for modern Python", describing nothing beyond "makes the parameter".

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Specifying where to patch.** "Mock the carrier in this test" leaves the target open, and a patch on the module that defines a `from`-imported function changes nothing. Paste a prompt that states the target:

   > Patch `request_quote` where `seams.legacy` looks it up, with `monkeypatch.setattr("seams.legacy.request_quote", fake)`, not on `seams.fastline`. Keep `raising` at its default. With `mocker.patch`, pass `autospec=True`. Pass `margin=` instead of patching `MARGIN`, and don't call `importlib.reload` in a test. Then name the constructor parameter that would let this test drop the patch.

   Run the test once with the fake returning another price; if the quote doesn't move, the patch missed.</blockquote>

   The sidebar body is at most 120 words by `validate.word_count`. Every backticked name exists in `src`, the tests or the standard library, and the opening sentence describes a request, not what assistants do.
10. `## Build, run, observe` (~200 plus output).
    - From the repository root, once, `uv sync --locked --all-packages`. Then `cd examples/33-seams-in-python`, `uv run pytest -v` and `uv run mypy --strict src tests`.
    - Each experiment runs in a fresh scratch copy: delete the copy's `.venv`, run `uv sync --locked --all-packages`, and confirm `seams.__file__` points into the copy. Each changes one thing.
    - The chapter states the filter `uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|errors?))'`, then `uv run mypy --strict src tests`.
    - The command names no repo script. `host_ids.py` never appears in a reader-facing command. Scrubbing happens before quoting, outside the chapter.

    Experiments:
    - (a) In `tests/test_patching.py`, change test 2's FASTLINE target from `"seams.legacy.request_quote"` to `"seams.fastline.request_quote"`.
      - Expected: test 2 fails with `seams.domain.CarrierTimeoutError: FASTLINE did not answer for 'EU'`, and mypy exits 0.
      - Executor check: the module-qualified `E` line, and the closing `src/.../fastline.py:NN: CarrierTimeoutError` line.
    - (b) In `src/seams/legacy.py`, replace `from seams.fastline import request_quote` with `from seams import fastline`, and the call with `fastline.request_quote(...)`.
      - Expected:
        - test 2 fails at setup, with monkeypatch's `has no attribute 'request_quote'`;
        - test 3 fails with `DID NOT RAISE`, because the defining-module patch now works;
        - test 5's `defining-module` row changes;
        - test 17's snippet may change (executor check);
        - mypy exits 0.
      - Executor check: the exact failing set.
11. `## What you can do now` (~130): five bullets, one per objective, in the same order. They name:
    - `legacy.py` and the three seams;
    - tests 2 and 3;
    - tests 6 and 9;
    - tests 10 and 11;
    - tests 16 and 20.

    Every backticked token in the close appears earlier in the chapter.
12. `## For deeper coverage` (~100):
    - the `unittest.mock` "Where to patch" and autospeccing sections;
    - the pytest monkeypatch how-to;
    - the `importlib.reload` entry;
    - Feathers, *Working Effectively with Legacy Code*, "The Seam Model";
    - the pytest-mock documentation;
    - the bibliography link.

Figure `33-seams-in-python` (vertical, one main lane, two side boxes):
- **Top:** "test" with `monkeypatch.setattr("seams.legacy.request_quote", fake)`.
- **Accent box:** "namespace of seams.legacy" listing `request_quote`, `airco`, `MARGIN`, `RateEngine`.
- **Arrow down to `RateEngine.quote`,** with two labelled reads: "request_quote: looked up in seams.legacy" and "airco.price: looked up on seams.airco".
- **Muted dashed side box:** "patch on seams.fastline.request_quote: no effect; seams.legacy holds its own name".
- **Muted side box:** "margin=MARGIN: read when the class was defined; a later patch misses it".
- **Bottom bar:** "mypy checks neither the target nor the replacement".
- No digits in the SVG.

Caption draft (about 40 words with the prefix): "Figure 33.1: A patch replaces a name in the namespace where the engine looks it up. The legacy module holds its own name for the FASTLINE call, so patching the carrier's module misses it, and a default read at definition time is out of reach." S3 counts and adjusts.

### ch34: Dependency-breaking techniques for modern Python (hands-on, has_example = true)

Thesis: a dependency-breaking step changes structure, not behaviour, and the evidence is one characterisation table run against every step. In Python, three of Feathers's techniques become a keyword parameter with a default, a wrapper function and a function that takes its carriers as values. Subclass and override still works, but it's checked only by method name.

Sections (about 2,350 prose words, max 2,500; at most six excerpts, exactly one from the comparison fixture):

1. `## Learning objectives` (~110), five bullets:
   - pin what the legacy engine does today in a characterisation table, including behaviour you'd call a bug;
   - parameterise a constructor so a test passes fakes without a patch;
   - wrap a carrier SDK with a different shape so every carrier fits one callable type, and turn the class into a function bound at the root;
   - run one table across every step, and show that the table can fail;
   - say which of Feathers's techniques Python makes unnecessary, and what subclass and override costs.
2. `## Why this matters` (~180). Intent first: the patch from "Seams in Python: monkeypatch, injection, and duck typing" (one pointer) gets a first test, and the next move is to change the code so the test needs no patch. Changing untested code can change what it quotes. Three failures:
   - a forgotten fake at a defaulted parameter reaches the real carrier (test 24);
   - a step that also "improves" timeout handling changes behaviour (experiment a);
   - a misspelt override reaches the real carrier (test 29).
3. Figure plus one paragraph (~50).
4. `## Pin what the code does today` (~350).
   - Paraphrase Feathers's characterisation test, which records what the code actually does, citing "I Need To Make a Change but I Don't Know What Tests To Write" by title.
   - Excerpt `CHARACTERISATION_ROWS`. The rows pin the tie-break, half-up rounding and gram truncation (test 16), and a timeout that fails the whole quote (test 17).
   - The `step` fixture wires the same SDK-level fakes at each step's enabling point.
   - Test 18 runs the table against two altered engines and gets exactly the rows they break, so the table can fail.
5. `## Parameterise the constructor` (~300).
   - Excerpt `parameterised.RateEngine.__init__`. The defaults are the real SDK calls, so existing callers don't change, and the legacy patch is no longer needed (tests 16[parameterised-*], 22).
   - mypy checks a fake passed as an argument (test 30), which `monkeypatch.setattr` never did. Point back to "Seams in Python" for that, without re-teaching it.
   - The cost of defaults: a test that forgets a fake reaches the real SDK (test 24).
   - `AircoPrice` is a callback Protocol because the SDK takes keyword-only arguments. One pointer to "Protocol, duck typing, and structural typing with mypy".
6. `## Wrap the carrier with a different shape` (~300).
   - Excerpt `airco_quote`. It converts kilograms to grams with `int`, as the legacy code did, and cents to a `Decimal` (test 25). The gram truncation stays: a step doesn't fix behaviour.
   - Both carriers now fit `CarrierQuoter`, so the engine holds a mapping of them (tests 16[wrapped-*]).
   - Paraphrase the "skin and wrap" idea from Feathers's "My Application Is All API Calls" only if S5b verifies it (decision 8).
7. `## The class becomes a function` (~300).
   - Excerpt `quote`, `STANDARD_QUOTERS` and `quote_standard`. The class held only its carriers, so it dissolves into a function. One pointer to "Strategy: the callable".
   - `quoters` is required: mypy reports a missing one (test 31), and at run time the error is a `TypeError` (test 26).
   - `STANDARD_QUOTERS` is read-only and names both carriers (test 27), and `quote_standard` binds them (test 28). One pointer to the ISP and DIP chapter for `partial` at the root, and nothing about its mypy gap.
8. `## Subclass and override` (~250).
   - The comparison excerpt is `_FakeCarrierRateEngine`. The legacy calls are first extracted into methods (`_ExtractedCallsRateEngine`), then overridden. It passes the same table (tests 16[subclass-*]).
   - A misspelt override falls through to the real carrier (test 29). mypy reports the typo only when the method carries `@override` (test 32, reduced model). One pointer to "SRP, OCP, and LSP in Python".
   - The callable parameter makes the same substitution visible at the call, where mypy checks it (test 30).
9. `## Techniques Python makes unnecessary` (~250). A table with three columns: technique (bracketed names, decision 8), its Python form, and the test or pointer that backs it.
   - Parameterize Constructor: a keyword parameter with a default (tests 22, 24).
   - Replace Function with Function Pointer: nothing to do, because a function is a value (test 16[function-*]).
   - Extract Interface: a `Callable` alias or a Protocol the carrier needn't import (test 30; "Protocol, duck typing, and structural typing with mypy").
   - Subclass and Override Method: still works, but a callable parameter is checked (tests 29, 32).
   - Encapsulate Global References, Introduce Static Setter and Link Substitution: a patch where the name is looked up ("Seams in Python").
   - Skin and Wrap the API: `airco_quote` (test 25).

   No count of techniques. Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Breaking a dependency without changing behaviour.** "Make `RateEngine` testable" invites a rewrite, and a rewrite can quietly change the tie-break or the timeout. Paste a prompt that fixes the order of work:

   > Before changing `RateEngine`, write a characterisation table: for each row, the zone, weight and each carrier's answer, and the `(carrier, total, calls)` the code produces today, including the tie-break and the gram truncation. Make one change per step and run the table after each: carriers as keyword parameters defaulting to the real calls; then `airco_quote` wrapping the AIRCO SDK into `CarrierQuoter`; then a `quote` function taking `quoters`, bound with `functools.partial`. Don't fix behaviour in the same step.

   If an expected value in the table changed in the diff, ask which step meant to change behaviour.</blockquote>
10. `## Build, run, observe` (~200 plus output). The scratch-copy and stated-filter rules are the same as ch33's (confirm `dependency_breaking.__file__`).
    - (a) In `parameterised.py`, wrap the FASTLINE call in `try`/`except CarrierTimeoutError` and quote AIRCO alone when FASTLINE times out, an "improvement" made during the step.
      - Expected: test 17[parameterised] fails with `DID NOT RAISE`, every table row passes, and mypy exits 0.
      - Executor check: the exact `E` lines.
    - (b) In `tests/conftest.py`, rename `_FakeCarrierRateEngine._airco_price` to `_airco_prices`.
      - Expected: the `subclass` table rows fail with `CarrierTimeoutError: AIRCO did not answer for ...`, and test 17[subclass] still passes, because FASTLINE raises first.
      - mypy reports `[misc]`: the method is marked `@override` and no base method has that name.
      - Executor check: the exact failing set.
11. `## What you can do now` (~130): five bullets mapped one to one to the objectives. They name:
    - `CHARACTERISATION_ROWS` with test 16;
    - `parameterised.RateEngine` with test 30;
    - `airco_quote` and `quote_standard`;
    - test 18;
    - the techniques table with test 32.
12. `## For deeper coverage` (~100):
    - Feathers, *Working Effectively with Legacy Code*: "Dependency Breaking Techniques" and the characterisation-test chapter, by title;
    - the `functools.partial` entry;
    - one title pointer each to "Fowler vs Feathers, contrasted and combined" and "Refactor or rewrite", describing nothing;
    - the bibliography link.

Figure `34-dependency-breaking-techniques` (vertical staircase, four steps, one bar):
- **Step boxes, top to bottom:**
  - `legacy`, labelled "enabling point: a patch on seams' names";
  - `parameterised`, labelled "keyword parameters; defaults are the real calls";
  - `wrapped`, labelled "airco_quote fits CarrierQuoter";
  - `rating.quote`, accent, labelled "quoters required; quote_standard binds them".
- **Arrow labels between steps:** "one technique".
- **Right-hand bar along all four:** "same characterisation table".
- **Muted dashed side box:** "subclass and override: overridden method names; mypy checks a typo only with @override".
- No digits in the SVG.

Caption draft (about 38 words with the prefix): "Figure 34.1: Each step moves the enabling point from a patched name toward a parameter mypy checks, and the same characterisation table runs at every step. Subclass and override passes the table too, but a misspelt method reaches the real carrier." S3 counts and adjusts.

Citations, both chapters: verify each before writing and apply the bracketed fallbacks. Quote no sentence unless it was checked on a fetched page, stop each quotation where the page's sentence stops or before an em dash, and make no comparison between languages.

## Example spec

### `examples/33-seams-in-python` (project `seams`, package `seams`)

`pyproject.toml` in the r15 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`).

- **`domain.py`:**
  - `ConsignmentId` (`NewType`);
  - frozen slotted `Consignment(id, zone, weight_kg: Decimal)`;
  - frozen slotted `Money(amount: Decimal, currency: str = "EUR")`;
  - frozen slotted `RateQuote(consignment_id, carrier: str, total: Money)`;
  - `CarrierTimeoutError(Exception)`.
- **`fastline.py`:** `request_quote(zone: str, weight_kg: Decimal) -> Decimal`, raising `CarrierTimeoutError(f"FASTLINE did not answer for {zone!r}")`. The docstring says it stands in for an SDK call that opens a connection.
- **`airco.py`:** `price(*, destination: str, grams: int) -> int`, in cents, raising `CarrierTimeoutError(f"AIRCO did not answer for {destination!r}")`.
- **`legacy.py`** (decision 3):
  - `from seams import airco` and `from seams.fastline import request_quote` at module level;
  - `MARGIN = Decimal("1.10")`;
  - `class RateEngine` with `__init__(self, *, margin: Decimal = MARGIN)`;
  - `quote(self, consignment) -> RateQuote`:
    - calls `request_quote(zone, weight_kg)` and `airco.price(destination=zone, grams=int(weight_kg * 1000))`;
    - converts cents with `Decimal(cents) / 100`;
    - picks `min` over `(code, price)` with key `(price, code)`;
    - multiplies by the margin and quantises half up to the cent.
  - The docstrings describe the code as inherited and untested. Comments don't call it bad.
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- `consignment` (`CN-1`, `EU`, `Decimal("12.5")`).
- `fastline_fake` returning `Decimal("25.00")`.
- `airco_fake(*, destination, grams)` returning `2800` and recording grams in a list fixture.

`test_patching.py`:
1. `test_the_legacy_engine_calls_the_real_carrier`: `RateEngine().quote(consignment)` raises `CarrierTimeoutError`, matching `FASTLINE did not answer for 'EU'`. Domain row 33's failing test.
2. `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`: `monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)` (string form) and `monkeypatch.setattr(airco, "price", airco_fake)` (object form) give `("FASTLINE", "27.50")`.
3. `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`: target `"seams.fastline.request_quote"` raises `CarrierTimeoutError`, matching `FASTLINE did not answer`.
4. `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`: `legacy.airco is airco`, and patching `seams.airco.price` reaches the engine (AIRCO answers 2000 and wins at 22.00).
5. `test_unittest_mock_patch_follows_the_same_lookup_rule` x (`using-module`, `defining-module`): `unittest.mock.patch(target, fastline_fake)` as a context manager. Outcomes are `"FASTLINE 27.50"` and `"CarrierTimeoutError"` respectively, each recorded as a string.
6. `test_monkeypatch_refuses_a_misspelt_name`: `AttributeError` matching `has no attribute 'request_qoute'`. The message contains the module repr, so only the substring is matched.
7. `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`: `raising=False` on `request_qoute`; the quote still raises `CarrierTimeoutError`.
8. `test_patch_refuses_a_name_the_module_does_not_have`: `mocker.patch("seams.legacy.price")` raises `AttributeError` matching `does not have the attribute 'price'`. With `create=True`, the quote still raises `CarrierTimeoutError`.
9. `test_autospec_refuses_a_call_with_the_wrong_signature` x (`autospec`, `plain`): `mocker.patch("seams.legacy.request_quote", autospec=...)`, then `legacy.request_quote("EU")` gives `"TypeError: missing a required argument: 'weight_kg'"` against `"accepted"`.
10. `test_monkeypatch_undoes_its_changes_when_the_context_ends`: inside `monkeypatch.context()`, set both names, then assert `legacy.request_quote is fastline.request_quote` after the block.

`test_seams.py`:

11. `test_patching_a_module_constant_misses_a_default_captured_at_definition`: patching `seams.legacy.MARGIN` to `Decimal("2")` (with fakes in place) leaves `"27.50"`, and `RateEngine(margin=Decimal("2"))` gives `"50.00"`.
12. `test_reload_discards_a_patch_and_keeps_old_bindings`: a fresh interpreter (decision 7) writes four lines, and the test asserts the exact list:
    - the patch is overwritten by the reload;
    - teardown restores the pre-reload object;
    - a `from`-import isn't rebound after reloading `seams.fastline`;
    - an old instance is not an instance of the reloaded `RateEngine`.

    The exact strings are fixed by S1a, for example `["patch overwritten: True", "teardown restored pre-reload object: True", "from-import rebound: False", "old instance is new class: False"]`.
13. `test_an_object_with_the_right_method_can_stand_in_for_a_module`: `monkeypatch.setattr(legacy, "airco", _FakeAirco())` quotes. `_WrongAirco()` (it has `quote`, not `price`) raises `AttributeError` matching `'_WrongAirco' object has no attribute 'price'`, and only at the call.

`test_static.py` (each row: credited thing; mutation that fails it):

14. `test_mypy_does_not_check_a_monkeypatched_replacement`: imports `src`. `monkeypatch.setattr(legacy, "request_quote", wrong)`, where `wrong` takes one parameter, exits 0 with `[]`. Runtime half: the same patch makes `quote` raise `TypeError` matching `positional argument` (executor check on the exact text). Credits mypy's silence. Mutation: `legacy.request_quote = wrong` gives `["assignment"]`.
15. `test_mypy_checks_a_direct_assignment_to_a_module_name`: imports `src`; `legacy.request_quote = wrong` gives `["assignment"]`. Mutation: a correctly typed replacement gives `[]`.
16. `test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement`: `patch("seams.legacy.request_quote")` reveals `MagicMock | unittest.mock.AsyncMock`, and with `new=` it reveals the replacement's type. The test asserts the two `Revealed type is` substrings and exit 0. Mutation: `new=` removed from the second gives the union twice.
17. `test_mypy_requires_an_annotation_on_a_decorator_injected_mock`: `@patch("seams.legacy.request_quote")` on `def test(m) -> None` gives `["no-untyped-def"]`. Mutation: `m: MagicMock` gives `[]`.
18. `test_mypy_checks_a_fake_passed_to_a_protocol_parameter`: reduced model; a one-parameter fake passed to a callback-Protocol parameter gives `["arg-type"]`. Mutation: a two-parameter fake gives `[]`.
19. `test_mypy_accepts_a_misspelt_monkeypatch_target_string`: imports `src`; `monkeypatch.setattr("seams.legacy.request_qoute", fake)` exits 0 with `[]`. Runtime half: the same call raises `AttributeError`. Mutation: the object form with an attribute access `legacy.request_qoute` gives `["attr-defined"]`.

Numbers are spec ids, and the reconciliation and prose cite names, not numbers. The prose section map above uses the earlier draft numbering; S5a maps by name. Planned: 19 test functions and 21 cases:
- `test_patching.py`: 10 functions, 12 cases;
- `test_seams.py`: 3 functions, 3 cases;
- `test_static.py`: 6 functions, 6 cases.

The executor counts from the pytest summary line, and S1a records any difference.

Prose-to-test map for ch33 (by name, so the section spec's numbers resolve):
- "test 1": `test_the_legacy_engine_calls_the_real_carrier`
- "test 2": `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`
- "test 3": `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`
- "test 4": `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`
- "test 5": `test_unittest_mock_patch_follows_the_same_lookup_rule`
- "test 6": `test_monkeypatch_refuses_a_misspelt_name`
- "test 7": `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`
- "test 8": `test_patch_refuses_a_name_the_module_does_not_have`
- "test 9": `test_autospec_refuses_a_call_with_the_wrong_signature`
- "test 10": `test_patching_a_module_constant_misses_a_default_captured_at_definition`
- "test 11": `test_reload_discards_a_patch_and_keeps_old_bindings`
- "test 14": `test_monkeypatch_undoes_its_changes_when_the_context_ends`
- "test 15": `test_an_object_with_the_right_method_can_stand_in_for_a_module`
- "test 16": `test_mypy_does_not_check_a_monkeypatched_replacement`
- "test 17": `test_mypy_checks_a_direct_assignment_to_a_module_name`
- "test 18": `test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement`
- "test 19": `test_mypy_requires_an_annotation_on_a_decorator_injected_mock`
- "test 20": `test_mypy_checks_a_fake_passed_to_a_protocol_parameter`
- "test 21": `test_mypy_accepts_a_misspelt_monkeypatch_target_string`

Also `README.md` and the card `_examples/33-seams-in-python.md`: `order: 33`, eyebrow "Changing inherited code · Seams", and a concept title with no count. None of the following appears in `src/`: `monkeypatch`, `mock`, `patch`, `importlib`, `contextvars`, `Any`, `cast`, `print(`, `Optional`, `global`, `sys.modules`.

Deletion table (S1a; for the subject code, "deleted" means changed in a scratch copy):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| `from seams.fastline import request_quote` | `from seams import fastline` with a qualified call (experiment b) | 2 (setup), 3, 5[defining-module] | the using-module name disappears and the defining-module patch starts working (executor check) |
| `from seams import airco` with `airco.price` | `from seams.airco import price` | 2, 4 | the object-form patch on `seams.airco` no longer reaches the engine |
| `margin: Decimal = MARGIN` | `MARGIN` read inside `quote` | 10 (prose numbering) | the patched margin now applies: `"50.00"`, not `"27.50"` |
| FASTLINE stand-in raises | returns a price | 1 | `DID NOT RAISE` |
| key `(price, code)` | `price` only, with FASTLINE first in the tuple | executor check (no table row ties in ch33; ch34 owns the tie row) | none expected; S1a records it |
| test 2 target | the defining module (experiment a) | 2 | `CarrierTimeoutError` |
| `raising` default in test 6 | `raising=False` | 6 | `DID NOT RAISE` |
| `autospec=True` in test 9 | removed | 9[autospec] | `"accepted"` |

### `examples/34-dependency-breaking-techniques` (project `dependency-breaking`, package `dependency_breaking`)

- **`domain.py`, `fastline.py`, `airco.py`, `legacy.py`:** as ch33, with package `dependency_breaking` (decision 3).
- **`parameterised.py`** (Parameterize Constructor):
  - `type FastlineQuote = Callable[[str, Decimal], Decimal]`;
  - `class AircoPrice(Protocol)` with `def __call__(self, *, destination: str, grams: int) -> int: ...`;
  - `RateEngine.__init__(self, *, fastline_quote: FastlineQuote = request_quote, airco_price: AircoPrice = airco.price, margin: Decimal = MARGIN)`;
  - `quote` is otherwise as in `legacy.py`.
- **`wrapped.py`** (the AIRCO SDK wrapped):
  - `type CarrierQuoter = Callable[[str, Decimal], Decimal]`;
  - `airco_quote(zone: str, weight_kg: Decimal, /, *, price: AircoPrice = airco.price) -> Decimal`, which converts with `int(weight_kg * 1000)` and `Decimal(cents) / 100`;
  - `RateEngine.__init__(self, *, fastline: CarrierQuoter = request_quote, airco: CarrierQuoter = airco_quote, margin: Decimal = MARGIN)`, holding the quoters as `{"AIRCO": ..., "FASTLINE": ...}`;
  - `quote` takes `min` over `(code, quoter(zone, weight_kg))` with the same key.
- **`rating.py`** (the class becomes a function):
  - imports `CarrierQuoter` and `airco_quote` from `wrapped`;
  - `STANDARD_QUOTERS: Mapping[str, CarrierQuoter] = frozendict({"AIRCO": airco_quote, "FASTLINE": request_quote})`;
  - `quote(consignment: Consignment, /, *, quoters: Mapping[str, CarrierQuoter], margin: Decimal = MARGIN) -> RateQuote`;
  - `quote_standard = partial(quote, quoters=STANDARD_QUOTERS)`.
- Every step module is complete and self-contained apart from the domain and SDK imports, so its diff from the module before it is the technique. The README lists each diff.
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- `CarrierAnswers`: a frozen dataclass of the FASTLINE price, the AIRCO cents and an optional `fastline_error`. It has a `calls: list[tuple[str, str, str]]` recorder via a factory that returns `(fastline_fake, airco_fake, calls)`.
- `step` fixture params `legacy|parameterised|wrapped|function|subclass`. Each returns `(answers) -> (quote_for, calls)`, where `quote_for: Callable[[Consignment], RateQuote]`.
  - `legacy`: `monkeypatch.setattr("dependency_breaking.legacy.request_quote", ...)` and `monkeypatch.setattr(legacy.airco, "price", ...)`. This is the only use of `monkeypatch` in the ch34 tests (decision 2).
  - `parameterised`: constructor keywords.
  - `wrapped`: `fastline=` and `airco=partial(airco_quote, price=airco_fake)`.
  - `function`: `partial(quote, quoters={...})`.
  - `subclass`: `_FakeCarrierRateEngine(fastline_fake, airco_fake)`.
- `_ExtractedCallsRateEngine`: the legacy body with the two SDK calls moved into `_fastline_quote(zone, weight_kg)` and `_airco_price(zone, grams)`.
- `_FakeCarrierRateEngine(_ExtractedCallsRateEngine)`: both methods marked `@override`, forwarding to the fakes.
- Mutants for test 18: `_GramsRoundedRateEngine` (`round` instead of `int`) and `_HalfEvenRateEngine` (`ROUND_HALF_EVEN`). Both are built on `parameterised.RateEngine`'s constructor shape.

`test_characterisation.py` (holds `CHARACTERISATION_ROWS`, ids `fastline-cheaper`, `airco-cheaper`, `tie-goes-to-airco`, `margin-rounds-half-up`, `grams-truncated`; evidence I with 0.0006 kg in the last row):

16. `test_every_step_matches_the_characterisation_table` x `step` (5) x rows (5) = 25. Each asserts `(quote.carrier, str(quote.total.amount), sorted(calls))` exactly. Expected:
    - `("FASTLINE", "27.50", ...)`;
    - `("AIRCO", "59.95", ...)`;
    - `("AIRCO", "22.00", ...)`;
    - `("FASTLINE", "11.17", ...)`;
    - `("AIRCO", "0.01", [("AIRCO", "EU", "0"), ("FASTLINE", "EU", "0.0006")])`, with calls recorded as strings.
17. `test_every_step_lets_a_carrier_timeout_fail_the_quote` x `step` (5): a FASTLINE fake raising `CarrierTimeoutError("FASTLINE did not answer for 'EU'")` makes the quote raise it.
18. `test_the_table_catches_a_step_that_changes_behaviour` x (`grams-rounded`, `half-even`): runs every row against the mutant and asserts the list of failing row ids, `["grams-truncated"]` and `["margin-rounds-half-up"]`. This is the measurement that can fail.

`test_steps.py`:

19. `test_the_legacy_engine_needs_a_patch_to_reach_a_fake`: without the fixture, `legacy.RateEngine().quote(c)` raises `CarrierTimeoutError` matching `FASTLINE did not answer`.
20. `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`: `parameterised.RateEngine().quote(c)` raises the same error, and `RateEngine(fastline_quote=fake)`, with AIRCO forgotten, raises `AIRCO did not answer`.
21. `test_airco_quote_converts_kilograms_and_cents`: `airco_quote("EU", Decimal("12.5"), price=fake) == Decimal("28.00")`, and the fake saw `grams=12500`.
22. `test_the_function_form_needs_its_quoters`: `quote(c)`, with a coded `# type: ignore[call-arg]`, raises `TypeError` matching `missing 1 required keyword-only argument: 'quoters'`.
23. `test_standard_quoters_name_both_carriers`: `sorted(STANDARD_QUOTERS) == ["AIRCO", "FASTLINE"]`, and assignment raises `TypeError` matching `does not support item assignment`.
24. `test_quote_standard_binds_the_standard_quoters`: `quote_standard.func is quote`, `quote_standard.keywords == {"quoters": STANDARD_QUOTERS}`, and `quote_standard(c)` raises `CarrierTimeoutError`.
25. `test_a_misspelt_override_falls_through_to_the_real_carrier`: a test-local subclass of the `extracted_calls_engine` fixture's class defines `_airco_prices` without `@override`. The quote raises `CarrierTimeoutError` matching `AIRCO did not answer`.

`test_static.py`:

26. `test_mypy_checks_a_fake_passed_as_a_constructor_argument`: imports `src`; `parameterised.RateEngine(airco_price=wrong)`, where `wrong` takes `(zone, grams)` positionally, gives `["arg-type"]`. Credits the `AircoPrice` parameter. Mutation: annotating the parameter `object` empties the list.
27. `test_mypy_reports_a_missing_quoters_argument`: imports `src`; `quote(c)` gives `["call-arg"]`, matching `Missing named argument "quoters"` (executor check on the wording). Mutation: a default `quoters=STANDARD_QUOTERS` empties it.
28. `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator`: reduced model; two snippets give `[["misc"], []]`. Mutation: `@override` added to the second gives `[["misc"], ["misc"]]`.

Prose-to-test map for ch34 (the section spec's numbers):
- "test 16": `test_every_step_matches_the_characterisation_table`
- "test 17": `test_every_step_lets_a_carrier_timeout_fail_the_quote`
- "test 18": `test_the_table_catches_a_step_that_changes_behaviour`
- "test 22" (the legacy patch is no longer needed): `test_the_legacy_engine_needs_a_patch_to_reach_a_fake`
- "test 24": `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`
- "test 25": `test_airco_quote_converts_kilograms_and_cents`
- "test 26": `test_the_function_form_needs_its_quoters`
- "test 27": `test_standard_quoters_name_both_carriers`
- "test 28": `test_quote_standard_binds_the_standard_quoters`
- "test 29": `test_a_misspelt_override_falls_through_to_the_real_carrier`
- "test 30": `test_mypy_checks_a_fake_passed_as_a_constructor_argument`
- "test 31": `test_mypy_reports_a_missing_quoters_argument`
- "test 32": `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator`

Planned: 13 test functions and 44 cases:
- `test_characterisation.py`: 3 functions, 32 cases;
- `test_steps.py`: 7 functions, 7 cases;
- `test_static.py`: 3 functions, 3 cases.

The pytest summary line wins.

Also `README.md` and the card `_examples/34-dependency-breaking-techniques.md`: `order: 34`, eyebrow "Changing inherited code · Dependency breaking", and a concept title with no count. None of the following appears in `src/`: `monkeypatch`, `mock`, `patch`, `importlib`, `Any`, `cast`, `print(`, `Optional`, `ABC`, `abstractmethod`, `global`.

Deletion table (S1b):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| `ROUND_HALF_UP` in `parameterised.py` | removed (`ROUND_HALF_EVEN` default) | 16[parameterised-margin-rounds-half-up] | `"11.16"` |
| `int(` in `airco_quote` | `round(` | 16[wrapped-grams-truncated], 16[function-grams-truncated], 21 | grams `"1"` against `"0"` |
| `/ 100` in `airco_quote` | removed | 16[wrapped-*], 16[function-*], 21 | AIRCO price a hundred times larger |
| `code` in the `min` key, `wrapped.py` | removed, with FASTLINE first in the mapping | 16[wrapped-tie-goes-to-airco] | `"FASTLINE"` (executor check) |
| `code` in the `min` key, `rating.py` | removed, with FASTLINE first in `quoters` | 16[function-tie-goes-to-airco] | as above (executor check) |
| timeout propagation in `parameterised.py` | caught (experiment a) | 17[parameterised] | `DID NOT RAISE` |
| defaults in `parameterised.py` | removed | 20 | `TypeError`, not `CarrierTimeoutError` |
| `quoters` required | defaulted | 22, 27 | no `TypeError`; empty code list |
| `frozendict` | plain dict | 23 | `DID NOT RAISE` |
| `quote_standard` binding | `partial(quote)` | 24 | keywords differ |
| `@override` on `_FakeCarrierRateEngine` | removed | none at run time; mypy is then silent on a typo (test 28's subject) | recorded, not a failure row |

## Steps and status

Step ids are `S*` (decision 0). Only `S1a`, `S1b`, `S5a` and `S5b` are cited as `run:` tokens.

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| S0 | Bookkeeping, all with dated notes, plus re-checking the upstream pins and recording the decisions. In `iteration-plan.md`: PDP-133a-c and 134a-c `active`, r16 active, r15 closed, PDP-131a to 132c closed. In r15's plan: R7 closed. In the reconciliation plan: rows 188-198 `open`, rows 14-16 noted "r16". In the domain model: rows 33-34 get the names and decisions 2-11. ch33-34 stub `description` lines are written | - | todo |
| S1a | ch33 member, card and README; one `uv lock`; three green runs plus one reverse-file-order run; the deletion table, each row in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`), deleted after use; each static mutation run | S0 | todo |
| S1b | ch34 member, card and README; one `uv lock` after S1a (sequenced for `uv.lock`); three green runs plus one reverse-order run; the deletion table; each static mutation run | S1a | todo |
| S2 | Witness results into rows 188-197 and legacy rows 14-16 (14 and 16 verified, 15 adjusted). The dated r16 note in `_plans/spikes.md` (evidence B-J, decision 9). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | S1b | todo |
| S3 | Two figures, specs `diagrams/specs/33-*.py` and `34-*.py`, and `_data/diagrams.yml` (single owner; 35 entries). Figures 00-32 unchanged. Every name drawn exists in `src`, conftest or the standard library | S2 | todo |
| S4 | ch33-34 `status = "drafted"` (`kind` stays `hands-on`) | S3 | todo |
| S5a | ch33 prose agent: re-fetch sources and quote exactly; run both experiments in fresh scratch copies with the stated filter; scrub output before quoting; hand back the sources checked and a per-paragraph claims table that names, for each static-test citation, its mutation | S3, S4 | todo |
| S5b | ch34 prose agent, in parallel with S5a, with the same duties, plus verifying each bracketed Feathers technique name (decision 8) | S3, S4 | todo |
| S6 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also: close-to-objective mapping, the excerpt check against decisions 2-5 and 10, pointer circularity (criterion 11), the cross-language grep (criterion 14), and the scope of the mock exception (criterion 2) | S5a, S5b | todo |
| S7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r16.x` on main; notes-only release | S6 | todo |

Reconciliation rows (step S0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 188 | 33 | The legacy engine calls the real carrier; a patch where the name is looked up replaces it; a patch on the module that defines a `from`-imported name leaves the engine calling the real carrier; a module attribute is patched on its own module; `unittest.mock.patch` follows the same rule | `test_the_legacy_engine_calls_the_real_carrier`, `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`, `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`, `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`, `test_unittest_mock_patch_follows_the_same_lookup_rule`, `source: https://docs.python.org/3/library/unittest.mock.html` |
| 189 | 33 | monkeypatch refuses a misspelt name and with `raising=False` creates a name nothing reads; `patch` refuses a missing name; autospec refuses a wrong-signature call that a plain patch accepts; monkeypatch undoes its changes | `test_monkeypatch_refuses_a_misspelt_name`, `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`, `test_patch_refuses_a_name_the_module_does_not_have`, `test_autospec_refuses_a_call_with_the_wrong_signature`, `test_monkeypatch_undoes_its_changes_when_the_context_ends`, `source: https://docs.pytest.org/en/stable/how-to/monkeypatch.html` |
| 190 | 33 | A patched constant misses a default captured at definition; a reload overwrites a patch, teardown restores the pre-reload object, a `from`-import isn't rebound and an old instance keeps the old class | `test_patching_a_module_constant_misses_a_default_captured_at_definition`, `test_reload_discards_a_patch_and_keeps_old_bindings`, `source: https://docs.python.org/3/library/importlib.html` |
| 191 | 33 | An object with the right method stands in for a module at a namespace seam, and one without it fails only when called | `test_an_object_with_the_right_method_can_stand_in_for_a_module` |
| 192 | 33 | mypy checks neither a monkeypatched replacement nor a target string, checks a direct assignment, types a patch as a `MagicMock` union or as its replacement, requires an annotation on a decorator-injected mock, and checks a fake at a Protocol parameter | `test_mypy_does_not_check_a_monkeypatched_replacement`, `test_mypy_accepts_a_misspelt_monkeypatch_target_string`, `test_mypy_checks_a_direct_assignment_to_a_module_name`, `test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement`, `test_mypy_requires_an_annotation_on_a_decorator_injected_mock`, `test_mypy_checks_a_fake_passed_to_a_protocol_parameter` |
| 193 | 34 | The legacy engine, each dependency-breaking step and the subclass form match one characterisation table, and a carrier timeout fails the quote at every step | `test_every_step_matches_the_characterisation_table`, `test_every_step_lets_a_carrier_timeout_fail_the_quote` |
| 194 | 34 | The characterisation table fails exactly the rows an altered engine breaks | `test_the_table_catches_a_step_that_changes_behaviour` |
| 195 | 34 | The legacy engine needs a patch; a parameterised engine keeps the real carriers as defaults; `airco_quote` converts kilograms and cents; the function form requires its quoters; `STANDARD_QUOTERS` is read-only; `quote_standard` binds them | `test_the_legacy_engine_needs_a_patch_to_reach_a_fake`, `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`, `test_airco_quote_converts_kilograms_and_cents`, `test_the_function_form_needs_its_quoters`, `test_standard_quoters_name_both_carriers`, `test_quote_standard_binds_the_standard_quoters`, `source: https://docs.python.org/3/library/functools.html` |
| 196 | 34 | A misspelt override reaches the real carrier, and mypy reports it only with `@override`; mypy checks a fake passed as a constructor argument and reports a missing `quoters` | `test_a_misspelt_override_falls_through_to_the_real_carrier`, `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator`, `test_mypy_checks_a_fake_passed_as_a_constructor_argument`, `test_mypy_reports_a_missing_quoters_argument` |
| 197 | 33-34 | mypy `--strict`, ruff and the idiom scan pass the legacy modules and every step | `run: S1a`, `run: S1b` |
| 198 | 33-34 | The "Build, run, observe" experiments behave as quoted | `run: S5a`, `run: S5b` |

Legacy rows at S2:
- **Row 14** gets `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`, `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`, `test_unittest_mock_patch_follows_the_same_lookup_rule` and `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`. Marked "verified (r16)".
- **Row 15** gets `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`, `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`, `test_an_object_with_the_right_method_can_stand_in_for_a_module`, `test_patching_a_module_constant_misses_a_default_captured_at_definition` and `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`. Marked "adjusted (r16)" (decision 6).
- **Row 16** gets `test_every_step_matches_the_characterisation_table`, `test_every_step_lets_a_carrier_timeout_fail_the_quote` and `test_the_table_catches_a_step_that_changes_behaviour`. Marked "verified (r16)".

## Corrections after the build

(None yet. The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.)

Lessons carried from r11-r15, which this plan applies up front:
- **Counts.** Per-file counts are summed from the spec, and the pytest summary line wins (r13 P1a, r14 Q1a, r15 R1b's sum error).
- **Members.** The project is named after its package, with no `[tool.*]` table (r13 P1a).
- **Shared tables.** They live in the test module, not in conftest (r13 P1a). Conftest types are imported under `TYPE_CHECKING`, and classes come through fixtures (r14 Q1a).
- **Determinism.**
  - Assertions that can fail compare lists or tuples, never a set repr, not even of strings (r13 P5, r14 Q5).
  - No assertion names a mock `id` or a module path.
- **Experiment filters.** They match pytest's `E` plus 3, 7, 9 and 11 spaces as separate alternatives, and `(tests|src)/.*Error$` (r13 P6, r14 Q6, r15 R1a).
- **Reader commands.** No reader-facing command pipes through a repo script. `host_ids.py` never appears in a chapter (r15 R6 round 1).
- **Pointers.** No pointer sends the reader back to a chapter that defers the topic here (r14 Q6), and no pointer describes a stub's content. ch33 doesn't point back to "Proving it works" or "Singleton" for patching module state.
- **Scope words.** Every scope word is checked against the code (r11, r15 R6). "Any object" becomes "an object" unless a test covers the whole scope.
- **Voice.** The ban tier flags "earns its place" (r15 R5); neither chapter uses it, in a heading or in prose.
- **Measurement.** A test that claims something is measured must be able to fail (r15). Test 18 exists for that.
- **Static tests.** Every exit-0 static test asserts `_codes(stdout) == []` and a runtime half (r13 P6).
- **Paths.** Repo-relative paths only in plans (r09 process incident).

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs, and once with the test files in reverse order, with the same pass count.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|threading|print\("` over both members' `tests` prints nothing.
   - `grep -rnE "monkeypatch|mocker|unittest\.mock|\bpatch\b|importlib|\bAny\b|cast\(|print\(|Optional|contextvars|\bglobal\b|sys\.modules"` over both members' `src` prints nothing.
   - `grep -rlE "monkeypatch|mocker|unittest\.mock"` over `examples/34-*/tests` prints only `examples/34-dependency-breaking-techniques/tests/conftest.py`. In that file, `monkeypatch` appears only inside the `legacy` branch of the `step` fixture (S6 reads it).
   - `importlib.reload` appears in ch33's tests only inside the fresh-interpreter script string.
   - `grep -rnE "\bABC\b|abstractmethod"` over `examples/34-*/src` prints nothing.
3. Every test name cited in rows 188-196 and rows 14-16 is defined exactly once across `examples/*/tests`.
4. Every mypy-API test asserts its exit status, an exact sorted code list through the anchored `_codes` regex, and no line number. Revealed-type tests assert only the `Revealed type is` substring.
   - `grep -c "_codes("` is at least 6 in ch33's `test_static.py` and at least 3 in ch34's.
   - Every `# type: ignore[...]` and `# noqa` names a code, and there are no unused ignores.
5. **Every static test can fail on a mutation of the thing its prose credits.** The S1a and S1b handbacks list each static test with its credited thing, run the named mutation in a scratch copy and quote the failing line. Every exit-0 test also asserts the hazard at run time.
6. Deletion tables (S1a, S1b): every row, changed in a fresh scratch copy whose imports come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. Executor-check rows are resolved or moved to Corrections.
7. Every "has no effect", "misses", "refuses", "accepts", "reaches the real carrier", "falls through" or "preserves" sentence names a test with a deletion-table row, experiment or mutation that makes it fail. Scope words ("every", "all", "only", "never", "any", "nothing") name the test that covers the whole scope, or are cut.
8. ch33-34 are drafted, with:
   - one figure each;
   - captions of 20-45 words including `Figure N.1:`;
   - at most 2,500 prose words each by `validate.py` (an error above; a warning below 1,900 is reported, not padded).
9. Spine and sidebar:
   - Both chapters pass the `hands-on` spine.
   - `grep -c "^## How it works"` is 0 in both.
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `## What you can do now` is the second-to-last H2, directly before `## For deeper coverage`, with as many bullets as the learning objectives. Every backticked token in the close appears earlier in the chapter.
   - Each sidebar:
     - opens with a bold lead and holds a nested `>` prompt;
     - has at most two non-quoted paragraphs;
     - matches no `\bCheck(:| that| three| four| whether)`;
     - is at most 120 words;
     - names only identifiers present in the chapter, its `src`, its tests or the standard library;
     - makes no claim about what assistants or models produce.
10. Thesis:
    - ch33 says a global name looked up at call time is a seam, the patch is its enabling point, and a parameter is the seam to keep. It compares patch and parameter with a cost per test, honouring the "Proving it works" and "Singleton" promises.
    - ch34 says each step changes structure and not behaviour, and shows one table run at every step plus the test that the table can fail.
11. Non-overlap and pointers:
    - ch33 points to "ISP, DIP, and dependency injection without a framework", "Protocol, duck typing, and structural typing with mypy", "Proving it works: pytest, pytest-mock, and mypy" (double table only), "Mocking reference: unittest.mock and pytest-mock" and "Dependency-breaking techniques for modern Python" by title, one clause each.
    - ch33 doesn't point to "Singleton: module, Borg, and metaclass", and doesn't point to "Proving it works" for patching module state.
    - ch34 points to "Seams in Python: monkeypatch, injection, and duck typing", "Strategy: the callable", "Protocol, duck typing, and structural typing with mypy", "SRP, OCP, and LSP in Python", "ISP, DIP, and dependency injection without a framework", "Fowler vs Feathers, contrasted and combined" and "Refactor or rewrite" by title. It describes nothing of the last two.
    - Neither chapter describes golden files, a rounding-rule change, a strangler adapter, asyncio, `contextvars` or LLM output.
    - Neither re-quotes the typeshed comment.
12. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, the cards, the specs and the SVGs, with `--stats` reviewed against the house-voice rubric. "earns its place" appears nowhere.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|memoiz|characteriz|parameteriz)"` over prose (quotations and code excluded) prints nothing. Feathers's technique names, if verified, are proper names and exempt inside the techniques table only.
    - No paragraph after an excerpt re-narrates its identifiers.
13. No em-dash or en-dash in any file touched in r16, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. Quotations stop before the docs' em dashes (evidence K).
14. `grep -nE "Java|C#|C\+\+|\.NET|Smalltalk|classpath|preprocessor|linker|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/33-*.md`, `_docs/34-*.md`, the new READMEs and the cards prints nothing.
15. Idiomatic scan: 0 ban-tier in both members, including `legacy.py` and the step modules.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs scrubbed before quoting. Module reprs that carry a file path are scrubbed or not quoted.
17. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Each experiment:
    - runs in a fresh scratch copy, changes one thing, and is deleted afterwards;
    - has its exact filter command stated in the chapter, matching `E` plus 3, 7, 9 and 11 spaces and `(tests|src)/.*Error$`;
    - is quoted as that filter's complete output, followed by `uv run mypy --strict src tests`;
    - is run twice with identical output apart from the duration.
19. Attribution:
    - Feathers is cited by title and chapter title, paraphrased only, with technique names only if verified.
    - The `unittest.mock`, monkeypatch how-to, `importlib` and `functools` sentences are quoted exactly. Every book cited is already in `bibliography.html`.
20. Claims:
    - Every factual sentence in ch33-34 maps to a named test, `run: S1a`, `run: S1b`, `run: S5a`, `run: S5b`, or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0, with rows 188-198 resolved and each `source:` URL present in its chapter.
    - No r16 `run:` token matches an r01 step id (decision 0).
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 35 entries, and `diagrams/0*-*`, `diagrams/1*-*`, `diagrams/2*-*`, `diagrams/30-*`, `diagrams/31-*` and `diagrams/32-*` are unchanged.
22. Reconciliation rows 188-198 are `verified` or `adjusted` with evidence. Rows 14 and 16 are `verified (r16)`, and row 15 is `adjusted (r16)`.
23. Deterministic: no test depends on wall time, the environment, memory addresses, file paths, test order or iteration order it didn't create. `filterwarnings = ["error"]` is still in the root config.
24. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.
25. Every self-contained mypy snippet that stands for code is named in the prose as a reduced model: ch33's `test_mypy_checks_a_fake_passed_to_a_protocol_parameter` and ch34's `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator`.
26. Test counts in prose and handbacks come from the pytest summary line of a fresh run.
27. The subclass form is a `step` fixture param on the shared table, and ch34 shows exactly one excerpt from it. The legacy module isn't counted as a comparison form.
28. Every figure label that names code exists in that chapter's `src`, conftest or the standard library, checked by grep at S3.
29. Repo-relative paths only in this plan and every r16 file: `grep -rnE "/home/|/Users/"` over the files touched in r16 prints nothing.

## Risks

- **Predicted messages and counts.** Every iteration since r05 mispredicted something. Expect differences in these places:
  - the exact `TypeError` text when a one-parameter replacement is called with two arguments;
  - mypy's wording for a missing keyword-only argument (`Missing named argument "quoters"`);
  - the codes for a direct assignment to a `from`-imported module name (`[assignment]`, perhaps with others);
  - which tests ch33 experiment (b) fails, and whether some show as setup `ERROR`;
  - whether the tie-break deletions fail as predicted, given mapping order.

  Tests match codes and stable substrings only.
- **Module reprs carry paths.** On a real package, `monkeypatch` and `patch` errors print `<module 'seams.legacy' from '<path>'>`. Tests match only the trailing substring, and quoted output is scrubbed or trimmed. Criterion 16 guards this.
- **Mocks leaking.** monkeypatch and mocker undo at teardown, and a failing test still tears down. The reload runs out of process. If any test reloads in-process, class identity can leak; criterion 2 forbids it.
- **mypy finding pytest in `_run`.** Snippets that import `pytest` or `pytest_mock` rely on mypy resolving installed packages from the running interpreter. If they don't resolve, the snippet takes a local stub Protocol for the setattr signature, and the prose says so.
- **The mock exception spreading.** Later plans must not cite r16 as permission. The exception is scoped to ch33's tests and ch34's legacy step, and it's recorded in decision 2 and the S2 spikes note.
- **Overlap with "Fowler vs Feathers, contrasted and combined".** That chapter owns golden values and a rounding-rule failure. ch34's table pins half-up rounding and test 18 uses a half-even mutant, but neither experiment changes a rounding rule, and the prose doesn't describe the Fowler contrast. The r17 planner is told this in the S2 note.
- **Unverified Feathers technique names.** If S5b can't verify them, the techniques table describes each technique without a name, and the section shrinks.
- **mypy and pytest behaviour can move.** The prose says "mypy 2.4.1" for the patch typing and the unchecked monkeypatch results, and "pytest 9.2.0" once for monkeypatch's messages.
- **Not upstream defects, kept out of prose as defects.**
  - The two monkeypatch error wordings differ by form.
  - `spec_set` doesn't check call signatures, as documented: only autospec copies signatures.
  - The docs' em dashes only constrain where a quotation stops.

  Nothing is filed. If the owner wants one reported, it goes through `lgtm-issue-reporting`.
- **Word budgets.** Both chapters carry many witnesses.
  - ch33 shrinks first: the `spec_set` quotation, then the duck-typed module paragraph to one sentence, then the decorator-annotation test's paragraph.
  - ch34 shrinks first: the techniques table to four rows, then the `AircoPrice` callback-Protocol sentence.
  - Their tests stay.
- **Legacy-shape drift.** A reviewer may "fix" `legacy.py` (move imports, drop the default). The deletion tables make that visible: the patch tests fail. Comments in `legacy.py` say the shape is the subject.
- **`uv.lock` race.** S1a and S1b are sequenced.
- **Liquid.** The f-strings in excerpts contain single braces only. Any `{{` needs `{% raw %}`.
