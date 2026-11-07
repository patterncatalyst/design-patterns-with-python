---
title: "r19 plan: chapters 39-40 (Final project; Working with AI and LLM tools)"
order: 19
output: false
render_with_liquid: false
---

# r19: chapters 39-40, Final project; Working with AI and LLM tools

Opus-planned 2026-11-06. Branch `release/r19`, cut from main at 3722ab8 (the r18 merge). This file is the source of truth for r19 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No pin changes this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4, uv 0.13.7 and uv_build 0.13.7 match PyPI and python.org (checked 2026-11-06 from PyPI JSON: pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, ruff 0.17.4 of 2026-11-05, mypy 2.4.1 of 2026-10-28, uv and uv-build 0.13.7 of 2026-11-03; `python.org/ftp/python/` lists 3.15.0, 3.15.1, 3.15.2 and 3.16.0, `3.15.3/` is a 404, and `3.16.0/` holds only `Python-3.16.0a1.tgz`, a pre-release; local `uv --version` prints `uv 0.13.7`). V0 re-checks before any edit. `uv.lock` changes only because two members are added. `ci.yml` doesn't change (decision 7).

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch39: slug `39-final-project`, title "Final project", part 13 (`putting-it-together`), `kind = "hands-on"`, `has_example = true`, `status = "stub"`. The stub carries a `## How it works` heading that the draft drops.
- ch40: slug `40-working-with-ai-and-llm-tools`, title "Working with AI and LLM tools", part 13, `kind = "argument"`, `has_example = false` (V0 sets `true`, decision 3), `status = "stub"`. The stub carries a `## The argument` heading that the draft drops.
- Part 13's blurb: "A final project that combines the patterns, and working with AI and LLM tools on pattern-heavy code."

`validate.py` SPINE: `hands-on` is Learning objectives, Why this matters, Build, run, observe, What you can do now, For deeper coverage; `argument` is Learning objectives, Why this matters, What you can do now, For deeper coverage. No sidebar count is enforced for either kind (the count check runs only for `kind == "pattern"`). One figure is required for both, the word ceiling (2,500) is an error and the floor (1,900) a warning. `has_example` is metadata only. Captions are 20-45 words. `check_stale_versions` applies as in r18 (evidence M). The hands-on model is "asyncio and the patterns"; the argument-with-example model is "Refactor or rewrite".

Work items: PDP-139a-c (ch39 example, figure, prose) and PDP-140a-c (ch40), `todo` in `_plans/iteration-plan.md`. The iteration plan quotes no PRD intent for these chapters beyond the roadmap line and the part blurb; the binding intent is domain rows 39 and 40 and reconciliation rows 24 and 25 (evidence N).

## User decisions (owner to confirm)

0. **Step ids.** The steps are V0 to V7. At planning time `grep -nE '^\| V[0-9]' _plans/*.md` and `grep -n 'run: V' _plans/*.md` print nothing (the caller confirmed V is unused). Following r16 to r18, only suffixed ids are cited as `run:` tokens: `V1a`, `V1b`, `V5a` and `V5b`. Plain V0, V2, V3, V4, V6 and V7 appear only in this plan's table. One `run:` token cites a recorded file: `run: _plans/evidence/r19-sidebar-census.md` (written at V2).

   **Recommend: yes.**

1. **ch39 kind: `hands-on`, `has_example = true` (unchanged), with one AI sidebar** in the 2026-11-05 form, held in `## When the composition is the wrong shape`. It isn't a `pattern` chapter: it has no single pattern to set against its forces and no bucket (domain row 39: `n.a.`).

   **Recommend: yes.** Alternative: no sidebar. Every chapter from the SOLID part on carries one, and the final project is where a reader most plausibly asks an assistant to "add a stage".

2. **The final project's scope and patterns** (evidence B to E). One booking slice, end to end, through all seven domain areas, network-free and deterministic: a `BookingRequest` is rated, a slot is reserved on a sailing, the carrier booking is placed, customs clears the declaration, an invoice is raised and a tracking event is published; a held declaration undoes the slot and the carrier booking. Patterns composed, each with its own test (evidence C):
   - **Strategy** (Rating): `type PricingRule = Callable[[Consignment], Money]`, chosen once at the composition root (test 12).
   - **Adapter** (Carrier): `FastlineGateway` turns a `Consignment` into the stand-in SDK's grams and receipt number behind the `CarrierGateway` Protocol (test 10).
   - **Chain of Responsibility** (Documentation): `ClearanceStage` callables, the first that returns `Held` stops the chain (test 11).
   - **Command with undo, on an `ExitStack`** (Routing and Carrier): each step registers its inverse with `ExitStack.callback`; a hold unwinds them in reverse; `pop_all()` commits (tests 4 to 7). This is the chapter's one new mechanism: "Context managers: deterministic cleanup" taught `ExitStack` for resources and never `callback` or `pop_all` (evidence M).
   - **Observer** (Tracking): `Signal[HandlingEvent]` delivers `BOOKED` to `TrackingHistory`, published only after the commit (tests 8, 9; the chapter's one comparison form, an eager publisher).
   - **Facade**: `BookingDesk.ship` is the one call a caller makes.
   - **Composition root** (dependency injection without a framework): `build_desk` is the only module that names a concrete carrier class (test 15).
   - Billing gets `LineItem`, `Invoice` and `Settlement` for the first time in the book (domain table: "Billing ... final project"; evidence M).

   Cut: State and `assert_never` over `ConsignmentStatus`, Builder, Memento, Visitor, Interpreter, Iterator, Decorator, Proxy, async, threads, persistence, retries, any second carrier. Each cut pattern is still named in one table row with its chapter title, so the reader sees where it would attach without code for it.

   **Not re-teaching.** Each composed pattern gets at most one sentence of mechanism and a pointer by exact title (evidence M lists them). The prose teaches only what appears where patterns meet: the order of side effects (undo before publish), the single composition root, and an acceptance test that fails while any stage is missing (test 2).

   **Recommend: yes.** Alternative: add State (`ConsignmentStatus` through `match`) as an eighth composition. It costs about 250 words and adds nothing that meets another pattern at a seam.

3. **ch40 kind: `argument`, `has_example = true`, with a runnable example and one sidebar.** The r17 precedent (ch35, ch36): argument kind with `## Build, run, observe` added. The chapter argues where trust in an assistant's reply comes from, and the example measures it. The example (evidence F to J):
   - three **hand-written drafts**, stored as text under `tests/drafts/`, standing in for an assistant's replies. The chapter says they were written for the book; it never says a model produced them (decision 5);
   - **three gates the reader already owns**: the static gate (`mypy --strict` and ruff with the repo's selection), a **shape review** (`review_gate.shape`, four rules from the book's pattern chapters, standard library `ast`), and a **behaviour oracle** (a generated grid of consignments that the draft must price as the idiomatic module does, the golden-values idea from "Fowler vs Feathers, contrasted and combined");
   - the measured result: each draft fails exactly the gates in a three-by-three table. The typed class hierarchy passes mypy and ruff and fails only the shape review; the callable draft that rounds with `round()` passes mypy, ruff and the shape review and fails only the oracle; the untyped factory fails all three (test 1);
   - a **Protocol seam for the model client**: `Assistant` (`reply(prompt, /) -> str`), a `RecordedAssistant` fake that replays recorded replies and refuses an unrecorded prompt, and `propose`, which gates each reply and sends the findings back in the next prompt. No mock is used; the fake is a plain class (tests 10 to 13).

   **Recommend: yes.** Alternatives: (a) `hands-on` kind, same content; (b) no example, argued in prose like "Naming patterns for teams and AI assistants". (b) leaves every claim about the drafts untested and domain row 40's review-checklist test unbuilt.

4. **Library additions: none.** Standard library only in both members (`ast`, `contextlib`, `importlib.util`, `subprocess` to run ruff from tests as "Shortcut patterns: dict dispatch, function tables, and EAFP" already does). No hypothesis (the oracle is a fixed grid from `itertools.product`, as r17's golden grid was), no syrupy or approval library, no vendor SDK, no HTTP client. mypy is reached through `mypy.api` from tests only (precedent: every `test_static.py`).

   **Recommend: yes.** Alternative: hypothesis for the oracle. It adds a pin to the dev group for one chapter and replaces a fixed, quotable list of failing rows with a shrunk example.

5. **Vendor neutrality and the house rule on model behaviour.**
   - No vendor cloud SDK, service, model name or product name in either member or chapter. The `Assistant` Protocol is the book's own; the chapter says an adapter over whatever client the reader uses fits behind it (the Adapter pattern, pointer to "Adapter, Facade, and Bridge") and names none.
   - No test calls a model or the network. A test asserts that `review_gate` imports no network module (test 14).
   - **No sentence claims how language models behave**, what they "typically", "often" or "tend to" produce, how a prompt changes a reply, or that the loop converges with a real model. The drafts are labelled hand-written. The only statements about models are quotations of fetched OWASP pages (evidence K), attributed as OWASP's.
   - Claims that can't be made deterministic and are therefore **not made** (decision 5 list, enforced by criterion 20): typical assistant output for a pattern request (legacy row 25); whether naming the rule in a prompt improves a reply; how often a reply fails a gate; run-to-run variation of a model; whether a fix-up prompt is followed; productivity, defect or adoption figures of any kind.

   **Recommend: yes.**

6. **ch40's sidebar and the prompt-pattern section.** ch40 gets exactly one sidebar, in the same form as every other: its prompt asks for `price` over `PricingRule` and states the three gates the reply must pass. A section "Prompts as reusable patterns" describes the book's sidebar form (problem, a prompt that names the chapter's rule and identifiers, one review line) and backs its counts with `_plans/evidence/r19-sidebar-census.md` (V2 greps: sidebars per chapter, each with a nested `>` prompt). It points to "Naming patterns for teams and AI assistants" for names in prompts and doesn't re-teach its practices.

   **Recommend: yes.** Alternative: no sidebar in ch40, since the chapter is about prompts. Then criterion 9 changes for ch40 only.

7. **Free-threaded CI job: neither member joins.** The r18 job is scoped to the chapters whose subject is the build (r18 decision 2, option B "bounded"). Neither member has build-dependent behaviour: no threads, no GIL reads. Evidence D: both reduced models passed on `3.15.2t` (18 passed). `ci.yml` is unchanged.

   **Recommend: yes.** Alternative: add both paths to the job's pytest line (one-line change; about 4 s more).

8. **No mocks, `mocker` or `monkeypatch`.** Seams are parameters: `BookingDesk`'s collaborators, `build_desk`'s `rule`, `propose`'s `assistant` and `gates`. Recording collaborators in ch39 are conftest wrappers around the real classes (composition, not subclassing). The r16 exception isn't extended.

   **Recommend: yes.**

9. **Comparison code.** One comparison form per chapter, a conftest fixture param, at most one comparison excerpt:
   - ch39: `publish_form` `after-commit|eager`; `_EagerBookingDesk` publishes `BOOKED` before clearance, so a held booking leaves a tracking event (test 9).
   - ch40: the drafts are the subject being reviewed, as the legacy engine was in Part 11, and they are test data, not conftest classes. They reach tests through a `draft` fixture param (`untyped_factory|typed_hierarchy|rounded_callable`). The chapter excerpts one draft (`typed_hierarchy`, the one the static gate passes) and describes the other two by their findings.

   **Recommend: yes.**

10. **Executing a draft in a test.** The behaviour oracle imports draft text as a module (`importlib.util.spec_from_file_location` on a file written to `tmp_path`), so a test runs code the reviewer didn't write. Prose says so in one sentence: run the oracle where a mistake costs nothing, after the static and shape gates. The drafts in the member are the book's own text. No sandbox is built.

    **Recommend: yes.** Alternative: run the oracle in a subprocess with `-I`. Safer in principle, but it adds a second process per draft and its isolation is not a sandbox either.

11. **Reversals and rewordings of binding lines** (each gets a dated note at V0):
    - **Domain row 40** says "a Java-in-Python generated `RateStrategyFactory`". Reader text can't name another language (criterion 14) or call a hand-written draft generated (decision 5). Reworded: "a hand-written draft in the class-per-strategy shape (`RateStrategyFactory`), then the idiomatic `PricingRule` version"; the failing test becomes the three-gate table.
    - **Reconciliation legacy row 25** ("Typical LLM output for patterns is Java-in-Python and fails strict mypy or the idiom scan"; "Collect sample outputs") can't be made deterministic and would need a model call. Expected close: **adjusted (r19)**, the claim about typical output dropped; the drafts' gate results are witnessed by rows 239 to 244.
    - **The "idiom scan"** in row 25 and domain row 40 is the `lgtm-idiomatic-review` skill script, which lives outside the repo, so a reader can't run it. The reader-facing equivalent is the member's `review_gate.shape`; the skill scan still runs over both members as a gate (criterion 15).
    - **Domain row 39** names `RateEngine` among the wired names. The book replaced the class with `PricingRule` and `quote` in "Strategy: the callable"; the row is updated to the example-spec names. Its order "booking -> rating -> stowage -> clearance -> invoice" gains the carrier booking between stowage and clearance.
    - **`chapters.toml`**: ch40 `has_example` `false` to `true`.
    - **CLAUDE.md**'s "Prefer `mocker.create_autospec`" isn't followed here (decision 8); no CLAUDE.md edit.

    **Recommend: yes.**

12. **Citations** (evidence K). Python docs (`contextlib` `ExitStack`, `ast`), the mypy command-line page (`--strict`), ruff's UP045 rule page, OWASP Top 10 for LLM Applications 2025 entries LLM05 and LLM09 (fetched pages, quotations attributed to OWASP). *Architecture Patterns with Python* (already in `bibliography.html`) by verified chapter titles in ch39. Mark Seemann's "Composition Root" post as already cited by "ISP, DIP, and dependency injection without a framework", by pointer through that chapter only. No new book.

    **Recommend: yes.** Alternative: add *Growing Object-Oriented Software, Guided by Tests* (walking skeleton, acceptance test first) to the bibliography and hub. Its edition and chapter titles weren't verified at planning; V5a would have to.

13. **Domain names** come from `_plans/shipping-domain-model.md` only: Consignment (`Consignment`, `Commodity`, `Weight`, `ConsignmentId`), Carrier (`CarrierGateway`, `FastlineGateway`, stand-in SDK, `FASTLINE`), Rating (`PricingRule`, `RateQuote`, `Money`, `RatingError`), Routing (`Sailing`, `StowagePlan`, `SlotId`), Tracking (`HandlingEvent`, `HandlingKind`, `TrackingHistory`), Documentation (`CustomsDeclaration`, `ClearanceStage`), Billing (`Invoice`, `LineItem`, `Settlement`), supporting `BookingRequest`. Port codes `NLRTM` and `SGSIN`; HS codes `0901.21` and `6109.10` (the dispatch chapter's illustrative codes) plus `9999.99` as the unknown code. No new domain area, no new carrier code. Rows 39 and 40 are updated in this commit.

    **Recommend: yes.**

14. **No cross-language wording, no project-outcome statistics, no chapter numbers** in reader text; "final project", never the banned synonym. ch40 says "class-per-strategy shape", never the language the shape comes from.

    **Recommend: yes.**

Also proposed for the owner (no decision needed unless declined):
- **No new books** (decision 12).
- **A dated r19 note** in `_plans/spikes.md` at V2: evidence B to J.
- **Status hygiene at V0**: r18 is merged (3722ab8) but `iteration-plan.md` marks r18 "(active)" and PDP-137a to 138c `active`, and r18's U7 reads `todo`. The orchestrator closes them.

## Planning evidence

Probes ran in a scratch copy at `<scratchpad>/plan19`, built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <dir>`, then `rm -rf .venv .venv-ft` and `uv sync --locked --all-packages`. Two reduced probe members were added there (`examples/39-probe`, package `final_project`; `examples/40-probe`, package `review_gate`) with `uv lock`. Sources were fetched into `<scratchpad>/fetch19`. Both directories were deleted afterwards; the repo was unchanged (`git status` clean). No host change was made.
- Runtime: `Python 3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`; free-threaded `Python 3.15.2 free-threading build (main, Oct 26 2026, 14:06:54) [Clang 23.1.3 ]` (already in uv's store from r18).
- mypy 2.4.1 `--strict --warn-unreachable --cache-dir /dev/null` through `mypy.api` with `mypy_path` set to the member's `src`; ruff 0.17.4 `--isolated --no-cache --target-version py315 --line-length 100 --select E,F,W,I,UP,B,SIM,RUF,PT,N`; pytest 9.2.0 with the repo's `addopts` and `filterwarnings = ["error"]`.
- Baseline: `1263 tests collected` from the root; 878 `def test_` lines across `examples` and `spikes` (three known duplicates); `_data/diagrams.yml` has 39 entries.

The models are reduced models: the names follow the domain model, but line numbers, messages and counts are predictions until the build quotes them as observed.

**A. Pins.** See the header. No bump.

**B. ch39 reduced model.** Nine `src` modules (`domain`, `rating`, `carriers`, `stowage`, `clearance`, `tracking`, `billing`, `desk`, `app`): `mypy --strict src` gives `Success: no issues found in 10 source files`. One test module of 9 tests: `9 passed` three times (0.02 to 0.03 s).
- Request: `CN-1`, zone `EU`, destination `SGSIN`, 12.5 kg, one `Commodity("0901.21", "green coffee", Money(400.00))`. Freight `5.63` (12.5 x 0.45 = 5.625, half up), duty `30.00` (400.00 x 0.075), invoice total `35.63`, slot `SlotId(1, 1, 1)`, carrier `open == {1001: 12500}` (grams), history one `BOOKED` event.
- `settle(invoice, Money(35.00))` raises `SettlementError` matching `35.00 does not settle 35.63`.

**C. Each composition is witnessed.**
- Held declaration (`9999.99`): `ClearanceHeldError` matching `unknown HS code 9999.99`; afterwards `(dict(plan.reservations), client.open, history.events) == ({}, {}, ())`, and the next request takes `SlotId(1, 1, 1)` again.
- An empty declaration with recording collaborators: the undo log is `["cancel", "release"]` (reverse order of registration).
- Stage left out (the acceptance helper returns an ordered list of failures):
  - rating replaced by a zero rule: `['freight 0.00', 'invoice 30.00']`;
  - carrier replaced by an inert gateway: `['carrier {}']`;
  - clearance replaced by a zero-duty pass-through: `['duty 0.00', 'invoice 5.63']`;
  - tracking not subscribed: `['tracking']`.
- `ast` over `src`: only `app.py` imports `FastlineGateway` or `FastlineClient` (outside `carriers.py`).

**D. Mutations in the ch39 model** (each restored before the next):
- `undo.callback(self._gateway.cancel, reference)` removed: the held test and the reverse-order test fail (2 failed, 7 passed).
- `undo.pop_all()` removed: the end-to-end test fails (the commit unwinds); 1 failed, 8 passed.
- The publish moved inside the `with` block before clearance (the eager form): the held test fails, history holds one event (1 failed, 8 passed).
- `ExitStack` replaced by `try/except` that releases then cancels: only the reverse-order test fails.
- Free-threaded: both probe members on `.venv-ft` (`3.15.2t`, `sys._is_gil_enabled()` `False`): `18 passed in 4.38s` (decision 7).

**E. ch39 seams for the stage-left-out test.** `BookingDesk` takes `rule`, `plan`, `gateway`, `clear` and `events` as keyword parameters; the test composes a desk with one collaborator replaced. The acceptance helper must return exact lists (the probe's first version asserted `!= []`, which passes on anything; criterion 7).

**F. ch40 drafts under the static gate** (text files `tests/drafts/*.py.txt`, importing `review_gate.domain`):
- `untyped_factory`: an ABC `RateStrategy` with one abstract `calculate`, two subclasses, `get_rate`/`set_rate`, a `RateStrategyFactory` caching `_instance` in `__new__`, an `Optional["RateStrategyFactory"]` annotation, an if/elif factory, `quantize(Decimal("0.01"))` with the context's default rounding. mypy exit 1, codes `['no-untyped-call', 'no-untyped-def']` (five `no-untyped-def`, two `no-untyped-call`); ruff exit 1, `['UP037', 'UP045']` (`Use X | None for type annotations`, `Remove quotes from type annotation`).
- `typed_hierarchy`: the same hierarchy fully annotated, a `match` factory with `@staticmethod create`, `ROUND_HALF_UP`, `RatingError`. **mypy exit 0, ruff exit 0** ("All checks passed!").
- `rounded_callable`: the idiomatic shape (`PricingRule`, `frozendict` of rules, `price` with EAFP) with `round(amount, 2)` in place of `quantize(..., ROUND_HALF_UP)`. mypy exit 0, ruff exit 0.
- The idiomatic `src/review_gate/pricing.py`: mypy 0, ruff 0.
- ruff `--select ALL --preview` over `typed_hierarchy` reports docstring, copyright, argument and exception-message rules and `no-self-use` (PLR6301, preview); no rule about a one-method base or a static-only class. `ruff rule too-few-public-methods` and `ruff rule PLR0903` are both "invalid value" on 0.17.4. Prose may say "ruff 0.17.4 has no rule for either shape" only in that scope.

**G. Shape review** (`ast`, four rules, findings sorted by line):
- `untyped_factory`: `[(8, 'single-method-base'), (23, 'accessor-pair'), (37, 'instance-in-new')]` (`static-only-class` doesn't fire because the class also has `__new__`).
- `typed_hierarchy`: `[(7, 'single-method-base'), (26, 'static-only-class')]`.
- `rounded_callable` and `pricing.py`: `[]`.
- The `ast` docs say `ast.walk` yields nodes "in no specified order", so `review` sorts its findings (a determinism rule for criterion 23).

**H. Behaviour oracle.** Grid `product(("flat", "per_kg"), ("0.5", "1", "2.5", "12.5", "40"))`, ids `CN-0` to `CN-9`, EU, per-kg rate 0.45. `rounded_callable` and `untyped_factory` both give exactly `["CN-5 per_kg: 0.23 != 0.22", "CN-7 per_kg: 1.13 != 1.12", "CN-8 per_kg: 5.63 != 5.62"]` (0.225, 1.125 and 5.625 are the half-cent products; half up against half even). `typed_hierarchy` and `pricing.py` give `[]`.

**I. The table.** `(static fails, shape fails, oracle fails)`: `untyped_factory` `(True, True, True)`, `typed_hierarchy` `(False, True, False)`, `rounded_callable` `(False, False, True)`; the idiomatic module `([], [], [])`. Nine probe tests passed three times from the root (3.14 to 3.17 s; the time is mypy) and from the member directory; `mypy --strict src` exit 0.

**J. The assistant seam.** `RecordedAssistant({prompt: [typed_hierarchy], second: [idiomatic]})` driven by `propose(prompt, assistant=..., gates=[static, review])`: reviews accepted `[False, True]`; prompts sent `[prompt, second]`, where `second` is the prompt plus `"\n\nFix these findings:\n"` and one line per finding (`line 7: single-method-base, use a callable type alias`). An unrecorded prompt raises `LookupError` matching `no recorded reply`. The reduced model loaded drafts with `exec` into a `ModuleType`; the member uses `importlib.util` on a `tmp_path` file (decision 10). Under `--import-mode=importlib` a test module can't import helpers from `conftest` by name (the probe's first collection failed); gates reach tests through fixtures.

**K. Sources, fetched 2026-11-06.** Quotable, exactly as on the page:
- `contextlib` (https://docs.python.org/3/library/contextlib.html, banner "Python 3.15.2 documentation"): "Each instance maintains a stack of registered callbacks that are called in reverse order when the instance is closed (either explicitly or implicitly at the end of a with statement)."; `callback`: "Accepts an arbitrary callback function and arguments and adds it to the callback stack."; `pop_all`: "Transfers the callback stack to a fresh ExitStack instance and returns it." and "No callbacks are invoked by this operation".
- `ast` (https://docs.python.org/3/library/ast.html): "The ast module helps Python applications to process trees of the Python abstract syntax grammar."; `ast.walk`: "Recursively yield all descendant nodes in the tree starting at node (including node itself), in no specified order."
- mypy command line (https://mypy.readthedocs.io/en/stable/command_line.html): `--strict` "This flag mode enables a defined subset of optional error-checking flags."; "Note: the --warn-unreachable flag is not automatically enabled by the strict flag."
- ruff UP045 (https://docs.astral.sh/ruff/rules/non-pep604-annotation-optional/): "Check for typing.Optional annotations that can be rewritten based on PEP 604 syntax."
- OWASP LLM05:2025 Improper Output Handling (https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/): "Treat the model as any other user, adopting a zero-trust approach, and apply proper input validation on responses coming from the model to backend functions."
- OWASP LLM09:2025 Misinformation (https://genai.owasp.org/llmrisk/llm092025-misinformation/): "Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy."; the risk example heading "Unsafe Code Generation". Quoted as OWASP's, never restated as the book's own claim about models.
- *Architecture Patterns with Python* (cosmicpython.com, the book's free online edition), chapter titles verified from the page titles: "TDD in High Gear and Low Gear" (`chapter_05_high_gear_low_gear.html`), "Unit of Work Pattern" (`chapter_06_uow.html`), "Dependency Injection (and Bootstrapping)" (`chapter_13_dependency_injection.html`, which says its `bootstrap.py` "is called a composition root in OO languages"). By title and topic only.
- Not used: martinfowler.com's "Exploring Generative AI" memo index (fetched; it calls its own memos "incomplete and tentative"); NIST AI 600-1 (not fetched).
- For V5a and V5b to re-fetch: every sentence above, plus any sentence an executor adds.

**L. Not claimable** (decision 5): see the list there. Also not claimed: that an `ExitStack` rollback is a transaction or a saga (nothing persists; the chapter says "undo" and "compensating step" at most once, without a source); that the shape rules are complete; that a draft passing all three gates is correct beyond the grid.

**M. Repo facts.**
- **Reconciliation.** Rows run 1 to 231, so r19 adds 232 to 248. Legacy rows 24 (ch39) and 25 (ch40) are carried and noted "r19" at V0. `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** 39 entries; r19 makes 41.
- **Test names.** None of the 31 names in the Example spec appears among the 878 existing `def test_` lines (checked by grep at planning; V1a and V1b re-check). The existing `test_money_addition_needs_one_currency` is why ch39's currency test has a different name.
- **Members.** No member uses project `final-project` or `review-gate`, or package `final_project` or `review_gate`.
- **Promises these chapters must honour:**
  - "Anti-patterns and pattern misuse" (sidebar review line): "For reviewing generated code in general, see Working with AI and LLM tools." ch40 is that general treatment.
  - The domain table's Billing area: "Invoice, LineItem, Settlement ... final project"; r12's note "keeps `Invoice` and `LineItem` for the final project". No member defines them yet (grep of `examples/*/src`).
  - "Mediator and Chain of Responsibility" uses `Settlement` as a clearance message (a duty settlement). ch39's `Settlement` is Billing's, closing an invoice; ch39 doesn't reuse or mention the other.
  - Part 13 blurb (header).
  - No other `_docs` page mentions either chapter.
- **Exact titles for pointers** (front matter): "Strategy: the callable"; "Adapter, Facade, and Bridge"; "Mediator and Chain of Responsibility"; "Command, undo, and command queues"; "Context managers: deterministic cleanup"; "Observer"; "ISP, DIP, and dependency injection without a framework"; "Protocol, duck typing, and structural typing with mypy"; "Dataclasses and value semantics"; "Shortcut patterns: dict dispatch, function tables, and EAFP"; "Singleton: module, Borg, and metaclass"; "Factory Method and Abstract Factory"; "Anti-patterns and pattern misuse"; "Fowler vs Feathers, contrasted and combined"; "Naming patterns for teams and AI assistants" (chapters.toml says "Naming patterns for teams and AI"; the front matter wins); "Seams in Python: monkeypatch, injection, and duck typing"; "State and finite state machines".
- **Overlap.** "Context managers: deterministic cleanup" teaches `ExitStack` over manifest writers (`write_manifests`) and never `callback` or `pop_all` (grep). ch04 teaches naming the bucket, the vocabulary and the disambiguation in prompts, and four review checks of a name; ch40 points there and doesn't repeat them.
- **Sidebars.** 34 docs have exactly one `<blockquote class="ai-sidebar"`; 0 to 4, 39, 40 and the appendices have none (grep at planning; V2 records the census).
- **CI.** The `free-threaded` job runs `examples/37-*` and `examples/38-*` only.
- **Status hygiene.** See "Also proposed".

**N. Binding lines read.** Domain row 39: "One slice end to end: booking -> rating -> stowage -> clearance -> invoice"; "all seven areas wired through a composition root: `BookingRequest`, `RateEngine`, `StowagePlan`, `ClearanceStage`, `Invoice`, `LineItem`, `Settlement`"; "The end-to-end acceptance test fails until every stage is integrated". Domain row 40: "Reviewing LLM-generated pattern code in this domain"; "a Java-in-Python generated `RateStrategyFactory`, then the idiomatic `PricingRule` version"; "A review-checklist test: generated code fails mypy strict or the idiom scan; the corrected version passes". Reconciliation row 24: "The final project integrates all seven domain areas without a framework" (end-to-end acceptance test; idiom scan). Row 25: decision 11.

## What is new in each chapter

**ch39 (patterns meet at seams).**
- One request through seven areas, with the patterns already in the book and none re-taught.
- `ExitStack.callback` and `pop_all` as undo and commit for a multi-step booking.
- Side effects that can't be undone (a published event) happen after the commit.
- One composition root, checked by a structure test; one acceptance test that fails while any stage is missing.

**ch40 (trust comes from gates, not from the author).**
- A reply is a draft; the reviewer's gates are types and lint, the book's shape rules, and a behaviour oracle.
- No single gate is enough: each draft fails a different set.
- The book's sidebar form as a reusable prompt pattern.
- The model client as a dependency behind a Protocol, tested with a recorded fake and no network.

## Approach

- **Thesis wording.**
  - ch39: the patterns in this book compose without a framework, and the new design questions sit where they meet: which step can be undone and in what order, which effect must wait for the commit, and which single function chooses the concrete parts. An acceptance test written first says when the slice is whole.
  - ch40: an assistant's reply is a draft whose reasoning isn't in the diff. Trust it as far as the gates you already own: `mypy --strict` and ruff for types and idioms, shape rules for the patterns, and a behaviour oracle for what it computes. Each catches a draft the others pass. Code that calls a model puts the client behind a Protocol and tests with recorded replies.
- **One uv member per chapter**, standalone, named after its package, no `[tool.*]` table:
  - `examples/39-final-project` (project `final-project`, package `final_project`);
  - `examples/40-working-with-ai-and-llm-tools` (project `review-gate`, package `review_gate`).
- **mypy and ruff witnesses.** Copy `_run`/`_codes` from `examples/38-asyncio-and-the-patterns/tests/test_static.py` and `_ruff_codes` from `examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_static.py`. Each static test asserts the exit status, the exact sorted code list and one stable substring, never line numbers (except the shape review's own `Finding.line`, which is part of the API under test), and names its credited thing and a mutation that fails it.
- **Negative witness rule.** Every pinned behaviour in `src` has a test that fails when it's changed (deletion tables).
- **Comparison and seam code** in conftest, through fixtures; conftest types imported under `TYPE_CHECKING` only; shared tables in the test module that uses them.
- **Determinism.** No clock, `random`, sleep or network. Lists and tuples only in failing assertions. `review` sorts findings (evidence G). No assertion names an address or an absolute path.
- **Counts** come from the code; the pytest summary line wins.
- **Repair rule (r12).** After every repair the validator re-reads the paragraph and the close bullets that depend on it.
- **Excerpt rule.** At most six excerpts per chapter, one of them a comparison excerpt.

Rejected in either `src`: `monkeypatch`, `mock`, `patch`, `Any`, `cast`, `Optional`, `random`, `global`, `sys.modules`, `time.`, `datetime`, `print(`, `exec(`, `eval(`, `subprocess`, `socket`, `urllib`, `http`. In ch40 `tests`, `subprocess` appears only in the ruff gate and `importlib.util` only in the oracle's loader.

## Per-chapter spec

### ch39: Final project (hands-on)

Thesis: as above. Sections (about 2,300 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~100), five bullets, one per close bullet:
   - write the acceptance test for a slice before the slice exists, and make it name each stage it needs;
   - wire seven domain areas through one composition root that is the only place naming a concrete part;
   - undo completed steps in reverse when a later step refuses, with `ExitStack.callback` and `pop_all`;
   - order effects so that nothing a step can't take back happens before the commit;
   - say which earlier pattern each part is, and where a pattern left out would attach.
2. `## Why this matters` (~180). Intent first: a booking that customs holds has already taken a slot on the sailing and a carrier booking. Without an undo, the slot stays reserved and the carrier holds a booking nobody pays for (deletion row 1); with an eager publisher, tracking reports a booking that never happened (test 9).
3. Figure plus one paragraph (~50).
4. `## The slice and its acceptance test` (~350). The request, the expected shipment (freight 5.63, duty 30.00, invoice 35.63, `SlotId(1, 1, 1)`, one `BOOKED` event). Excerpt the acceptance helper's head and test 1. Test 2: with any stage left out the helper lists what's missing (evidence C). One sentence: *Architecture Patterns with Python* argues for the balance of end-to-end and unit tests in "TDD in High Gear and Low Gear" (title and topic only).
5. `## The parts, each from an earlier chapter` (~350). A table: part, pattern, module, test, chapter title. Rows: `PricingRule` (Strategy; test 12; "Strategy: the callable"), `FastlineGateway` (Adapter; test 10; "Adapter, Facade, and Bridge"), `ClearanceStage` chain (Chain of Responsibility; test 11; "Mediator and Chain of Responsibility"), `Signal` and `TrackingHistory` (Observer; test 8; "Observer"), `BookingDesk.ship` (Facade; test 1), frozen value types (`Money`, `Weight`, `Invoice`; test 14; "Dataclasses and value semantics"). Plus three rows for patterns left out and where they would attach: `ConsignmentStatus` transitions ("State and finite state machines"), a caching gateway proxy ("Decorator the pattern vs @decorator the syntax, and Proxy"), amendments with undo ("Command, undo, and command queues"). No mechanism re-taught.
6. `## Undo in reverse with ExitStack` (~400). Excerpt `BookingDesk.ship`. Quote the docs' "called in reverse order" sentence and `pop_all`'s "Transfers the callback stack" sentence. A held declaration releases the slot and cancels the carrier booking (test 4) in reverse order (test 5); a full sailing books nothing with the carrier (test 6); the next request takes the freed slot (test 7). Each `callback` is the inverse of the step before it, which is the Command chapter's undo rule without a command class (pointer to "Command, undo, and command queues"; the `ExitStack` itself was introduced in "Context managers: deterministic cleanup").
7. `## Publish after the commit` (~300). An event can't be unpublished. The after-commit form records nothing for a held booking (test 8); the comparison excerpt `_EagerBookingDesk.ship` (or its two changed lines) records a `BOOKED` event for it (test 9). Rule: effects other parts can see go after `pop_all()`.
8. `## One composition root` (~250). Excerpt `build_desk`. Only `app.py` names `FastlineGateway` or `FastlineClient` (test 15); the pricing rule is chosen there (test 12); mypy refuses a gateway without `cancel` where `CarrierGateway` is expected (test 16). Pointer to "ISP, DIP, and dependency injection without a framework"; one sentence citing *Architecture Patterns with Python*'s "Dependency Injection (and Bootstrapping)", which calls its bootstrap module a composition root.
9. `## Billing closes the slice` (~150). `Invoice` from two `LineItem`s; `settle` refuses a short payment (test 13) and an invoice in two currencies has no total (test 14).
10. `## When the composition is the wrong shape` (~180). When one step is all there is (no undo needed), when steps cross a process or a network (an `ExitStack` holds callbacks in one process only; nothing here persists, evidence L), when undo isn't possible (a carrier that can't cancel needs a different design, not a callback). Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Adding a stage to the booking.** "Add an insurance step" names no place for the undo or for the event. Paste a prompt that keeps the slice's rules:

    > Add the step inside the `ExitStack` in `BookingDesk.ship`, after the carrier booking and before clearance, and register its inverse with `undo.callback`. Publish nothing before `undo.pop_all()`. Take the new collaborator as a keyword parameter of `BookingDesk` and choose it only in `build_desk`. Extend `acceptance_failures` with the step's expected result, and add a held-declaration test that shows the step undone.

    If the diff imports a concrete class outside `app.py`, ask why the composition root didn't choose it.</blockquote>

    At most 120 words; every backticked name exists in `src`, the tests or the standard library.
11. `## Build, run, observe` (~200 plus output). From the repository root once `uv sync --locked --all-packages`, then `cd examples/39-final-project`, `uv run pytest -v`, `uv run mypy --strict src tests`. Experiments run in fresh scratch copies (delete `.venv`, `uv sync --locked --all-packages`, confirm `final_project.__file__` points into the copy). The stated filter is r18's: `uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'`, then `uv run mypy --strict src tests`. No repo script and no `host_ids.py` in any reader command.
    - (a) In `src/final_project/desk.py`, delete the line `undo.pop_all()`.
      - Expected: test 1 fails (the commit unwinds: the slot and carrier booking are gone); mypy exits 0 (executor check on the exact `E` lines and which other tests fail).
    - (b) Restore, then move the `self._events.publish(...)` line to just after `slot = self._plan.reserve(...)`, inside the `with` block.
      - Expected: test 8 fails with one `BOOKED` event in the history; mypy exits 0.
12. `## What you can do now` (~130): five bullets in objective order, naming `acceptance_failures` and test 2; `build_desk` and test 15; `ExitStack`, `undo.callback`, `pop_all` and test 5; test 8 against `_EagerBookingDesk`; the parts table. Every backticked token appears earlier.
13. `## For deeper coverage` (~100): `contextlib`; *Architecture Patterns with Python* ("TDD in High Gear and Low Gear", "Dependency Injection (and Bootstrapping)", "Unit of Work Pattern" for the persistent form of commit and rollback); one title pointer to "Working with AI and LLM tools" describing nothing; the bibliography link.

Figure `39-final-project` (vertical pipeline):
- **Top:** "BookingRequest" then "BookingDesk.ship (Facade)".
- **Steps, top to bottom:** "quote: PricingRule"; "StowagePlan.reserve, undo: release"; "CarrierGateway.book, undo: cancel"; "clear: ClearanceStage chain"; "undo.pop_all(): commit"; "Invoice from LineItems"; "Signal.publish(BOOKED) to TrackingHistory".
- **Side box beside reserve and book** (accent): "ExitStack holds the undo callbacks".
- **Muted dashed branch from clear:** "Held: cancel, then release; nothing published".
- **Bottom bar:** "build_desk: the one place that names FastlineGateway".
- No digits in the SVG.

Caption draft (about 40 words with the prefix): "Figure 39.1: One booking through every domain area. Each completed step registers its undo on an exit stack; a held declaration unwinds them in reverse, and the tracking event is published only after the commit." V3 counts and adjusts.

### ch40: Working with AI and LLM tools (argument, with an example)

Thesis: as above. Sections (about 2,350 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~110), five bullets:
   - treat an assistant's reply as a draft and say which gate checks which property;
   - run the static gate and read what `mypy --strict` and ruff can and can't see in a pattern;
   - check a draft's shape against the book's pattern rules with `review_gate.shape`;
   - check a draft's behaviour against an oracle built from the code it replaces;
   - put a model client behind a Protocol and test the loop with recorded replies, no network.
2. `## Why this matters` (~180). Intent first: a draft of `price` arrives that type-checks and passes lint (evidence F), and the reviewer has to decide whether to merge it. Quote OWASP LLM05's zero-trust sentence, attributed. Say the three drafts in this chapter were written for the book.
3. Figure plus one paragraph (~50).
4. `## Three drafts, three gates` (~300). The table (test 1) and its reading: no gate alone accepts only the idiomatic module. One pointer to "Anti-patterns and pattern misuse" for why the class-per-strategy shape is a cost, not a style. Test 2.
5. `## The static gate` (~350). The untyped draft's codes (test 3): `no-untyped-def`, `no-untyped-call`, `UP045` and `UP037`; quote mypy's `--strict` sentence and its `--warn-unreachable` note, and the UP045 rule sentence. Excerpt `typed_hierarchy` (the comparison excerpt, decision 9): it passes both (test 4). ruff 0.17.4 has no rule for a one-method base or a static-only class (evidence F; scoped to that version, one sentence).
6. `## The shape review` (~400). Excerpt `single_method_base` and `review`. The four rules, each with the chapter title it comes from: `single-method-base` ("Strategy: the callable"), `static-only-class` ("Factory Method and Abstract Factory" and "Shortcut patterns: dict dispatch, function tables, and EAFP"), `accessor-pair` ("Anti-patterns and pattern misuse"), `instance-in-new` ("Singleton: module, Borg, and metaclass"). Findings on the two class drafts (tests 5, 6), each rule on its minimal case (test 8), and silence on a callable class and a one-method frozen dataclass (test 9). Quote the `ast` docs' "in no specified order" clause for why `review` sorts. Say the rules are a checklist, not a proof (evidence L).
7. `## The behaviour oracle` (~300). Excerpt `GRID` and the oracle helper. The two rounding drafts fail exactly at 0.225, 1.125 and 5.625 kg-prices (test 7). The oracle is the idiomatic module's answers on a generated grid, the golden-values idea from "Fowler vs Feathers, contrasted and combined" (pointer, not re-taught). The oracle runs the draft, so it comes after the other gates (decision 10).
8. `## Prompts as reusable patterns` (~250). The sidebar form: a problem, a prompt that names the chapter's rule and identifiers, one review line; counts from the census (`run: _plans/evidence/r19-sidebar-census.md`). A prompt that names the gate states what the reply will be checked against. Pointer to "Naming patterns for teams and AI assistants" for names in prompts, not repeated. No claim that a prompt changes a reply (decision 5).
9. `## A seam for the model client` (~300). Excerpt `Assistant`, `RecordedAssistant.reply` and `propose`. A rejected reply goes back with its findings (test 10), the loop stops at the first accepted reply (test 11) and gives up after its attempts (test 12); an unrecorded prompt is an error, so a test can't pass on a prompt nobody recorded (test 13). The package imports no network module (test 14); mypy refuses an assistant without `reply` (test 15). The adapter over a real client goes behind the same Protocol and isn't in the book (pointers to "Protocol, duck typing, and structural typing with mypy" and "Seams in Python: monkeypatch, injection, and duck typing").
10. `## When the gates aren't enough` (~150). The grid covers what it lists; the shape rules cover four shapes; a reply that changes a test changes the oracle. Quote OWASP LLM09's overreliance sentence, attributed. Then the sidebar:

    <blockquote class="ai-sidebar" markdown="1"> **Asking for code you will gate.** "Write the pricing strategies" leaves the shape and the rounding open. Paste a prompt that names the gates the reply must pass:

    > Write `price(rule, consignment, /)` over `type PricingRule = Callable[[Consignment], Money]`, with the rules in a read-only `frozendict` and an unknown name raising `RatingError`. Round with `quantize(CENT, rounding=ROUND_HALF_UP)`. No base classes, no static-only classes, no getters or setters. The reply must pass `mypy --strict`, ruff, `review_gate.shape.review` and the grid in `tests/test_gates.py`.

    If the diff changes `GRID` or a draft's expected findings, ask who decided the answer should change.</blockquote>
11. `## Build, run, observe` (~200 plus output). As ch39 (confirm `review_gate.__file__`).
    - (a) In `src/review_gate/pricing.py`, replace `amount.quantize(CENT, rounding=ROUND_HALF_UP)` with `round(amount, 2)`.
      - Expected: tests 1 and 2 fail on the idiomatic module, because the oracle's reference is the idiomatic module itself; executor check: the reference must be a recorded expectation table, not the module under change, or the experiment changes nothing (see the Example spec's `EXPECTED_ROWS`). mypy exits 0.
    - (b) Restore, then delete `static_only_class` from `SHAPE_RULES`.
      - Expected: test 5 fails with only `single-method-base` listed, test 8[static-only-class] fails, test 1 still passes (the typed hierarchy is still caught by the other rule). mypy exits 0. Executor check.
12. `## What you can do now` (~130): five bullets mapped to the objectives, naming test 1's table; tests 3 and 4; `review` and `SHAPE_RULES`; `GRID` and test 7; `Assistant`, `RecordedAssistant` and `propose`.
13. `## For deeper coverage` (~120): the mypy command-line page, ruff's rules index, the `ast` docs, the two OWASP entries, "Fowler vs Feathers, contrasted and combined" and "Naming patterns for teams and AI assistants" by title, the bibliography link.

Figure `40-working-with-ai-and-llm-tools` (vertical):
- **Top:** "Assistant.reply (RecordedAssistant in tests)".
- **Three gates, top to bottom:** "static gate: mypy --strict, ruff"; "shape review: review_gate.shape"; "behaviour oracle: GRID".
- **Bottom:** "accepted" (accent).
- **A return arrow from each gate to the top:** "propose: findings go back in the next prompt".
- **Three muted labels at the gate each draft fails first:** "untyped_factory" at the static gate, "typed_hierarchy" at the shape review, "rounded_callable" at the oracle.
- No digits in the SVG.

Caption draft (about 38 words): "Figure 40.1: An assistant's reply passes three gates in turn: types and lint, the pattern shape rules, then a behaviour oracle. Each of the three drafts stops at a different gate, and findings return in the next prompt." V3 counts and adjusts.

Citations, both chapters: verify each before writing; quote no sentence unless checked on a fetched page; stop each quotation where the page's sentence stops; keep curly apostrophes or stop before them; attribute every OWASP sentence to OWASP; no outcome claim; no comparison between languages.

## Example spec

### `examples/39-final-project` (project `final-project`, package `final_project`)

`pyproject.toml` in the r18 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`).

- **`domain.py`**: `ConsignmentId` (`NewType`); frozen slotted `Money(amount: Decimal, currency: str = "EUR")` with `__add__` refusing a different currency (`ValueError`); `Weight(kilograms)` refusing a non-positive weight; `Commodity(hs_code, description, value: Money)`; `Consignment(id, zone, destination, weight, commodities: tuple[Commodity, ...])`; `BookingRequest(consignment, carrier)`; `Sailing(code, origin, destination)` with UN/LOCODEs `NLRTM` and `SGSIN`; `HandlingKind` (`BOOKED`, `LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED`); `HandlingEvent(consignment_id, kind, location)`.
- **`rating.py`**: `type PricingRule = Callable[[Consignment], Money]`; `CENT`; `RateQuote(consignment_id, total)`; `per_kg` over a read-only `frozendict` of zone rates (`EU` 0.45, `ASIA` 1.20, illustrative), half up to the cent; `RatingError` for an unknown zone; `quote(consignment, /, *, rule) -> RateQuote`.
- **`carriers.py`**: `CarrierGateway` Protocol (`book(consignment, /) -> str`, `cancel(reference, /) -> None`); `FastlineClient` stand-in SDK (`submit(*, grams, destination) -> int` receipt from 1001, `void(receipt)`, read-only `open` view of receipts to grams; no I/O); `FastlineGateway(client)` adapter, references `FL-<receipt>`.
- **`stowage.py`**: frozen slotted ordered `SlotId(bay, row, tier)`; `StowagePlan(sailing, *, tiers)` with `reserve(consignment_id, /) -> SlotId` (lowest free tier), `release(slot, /)`, read-only `reservations`; `StowageFullError`.
- **`clearance.py`**: `CustomsDeclaration(consignment, duty)`; `Held(reason)`; `ClearanceHeldError` carrying `held`; `type ClearanceStage = Callable[[CustomsDeclaration], Held | None]`; `declare(consignment, /)` (duty over a read-only `frozendict` of HS rates `0901.21` 0.075 and `6109.10` 0.12, illustrative); stages `has_commodities`, `known_codes`; `STAGES`; `clear(declaration, /, *, stages=STAGES)`.
- **`tracking.py`**: `type Subscriber[E] = Callable[[E], None]`; `Signal[E]` with `subscribe` and `publish` (single-threaded; no weak references, which stay in "Observer"); `TrackingHistory` with `record` and `events`.
- **`billing.py`**: `LineItem(description, amount)`; `Invoice(consignment_id, lines)` with `total` (sums through `Money.__add__`); `Settlement(invoice, paid)`; `SettlementError(ValueError)`; `settle(invoice, payment, /)`.
- **`desk.py`**: `Shipment(quote, slot, carrier_reference, declaration, invoice)`; `BookingDesk(*, rule, plan, gateway, clear=clear, events)` with `ship(request, /) -> Shipment`: quote; inside `with ExitStack() as undo:` reserve and `undo.callback(plan.release, slot)`, book and `undo.callback(gateway.cancel, reference)`, clear, `undo.pop_all()`; then invoice; then publish `BOOKED` at the sailing's origin.
- **`app.py`**: `build_desk(*, client, plan, history, rule=per_kg) -> BookingDesk` (subscribes `history.record`, wraps `client` in `FastlineGateway`).
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- `_RecordingPlan` and `_RecordingGateway` wrap a real `StowagePlan` and `FastlineGateway` and append `"release"` and `"cancel"` to a shared log (composition, satisfying the Protocol and the plan's methods);
- `_EagerBookingDesk` (the comparison form): same collaborators, publishes `BOOKED` before clearance;
- fixture `publish_form` (`after-commit|eager`) returning a desk factory; fixture `world` returning a fresh `(client, plan, history)` triple.

`test_acceptance.py` (holds `REQUEST`, `COFFEE`, `UNKNOWN`, and `acceptance_failures(shipment, history, client, plan) -> list[str]`):
1. `test_a_booking_request_ships_end_to_end`: `acceptance_failures(...) == []`.
2. `test_the_acceptance_test_fails_when_a_stage_is_left_out` x (`rating`, `carrier`, `clearance`, `tracking`) with the exact lists of evidence C = 4.
3. `test_the_shipment_settles_for_the_invoice_total`.

`test_rollback.py`:
4. `test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking`.
5. `test_the_undo_runs_in_reverse_order_of_the_steps`: `["cancel", "release"]`.
6. `test_a_full_sailing_books_nothing_with_the_carrier`: `StowageFullError`; `client.open` empty.
7. `test_the_next_request_takes_the_slot_a_rollback_freed`: `SlotId(1, 1, 1)`.

`test_tracking.py`:
8. `test_a_held_booking_publishes_no_tracking_event` (after-commit form): `()`.
9. `test_an_eager_publisher_reports_a_booking_that_was_rolled_back` (eager form): one `BOOKED` event for `CN-2`.

`test_parts.py`:
10. `test_the_adapter_sends_fastline_grams_and_returns_its_reference`: `"FL-1001"`, `{1001: 12500}`.
11. `test_clearance_stops_at_the_first_stage_that_holds` x (empty: `nothing declared`; unknown: `unknown HS code 9999.99`) = 2.
12. `test_the_pricing_rule_is_chosen_at_the_composition_root`: `build_desk(..., rule=...)` with a flat rule gives a different freight and invoice.
13. `test_a_short_payment_does_not_settle`: `35.00 does not settle 35.63`.
14. `test_an_invoice_in_two_currencies_has_no_total`: `ValueError`.

`test_structure.py`:
15. `test_only_the_composition_root_names_a_concrete_carrier`: `["app.py"]` (the `ast` form of evidence C).

`test_static.py`:
16. `test_mypy_refuses_a_gateway_without_cancel`: a snippet passing a class with only `book` as `gateway=` gives `["arg-type"]` (executor check against `call-arg`), substring `"CarrierGateway"`. Credits the Protocol annotation on `BookingDesk`. Mutation: annotating `gateway` as `object` and the call as `gateway.book` makes it `["attr-defined"]` on `src` (executor designs; quotes the line).

Planned: 16 test functions, 20 cases (`test_acceptance.py` 3/6, `test_rollback.py` 4/4, `test_tracking.py` 2/2, `test_parts.py` 5/6, `test_structure.py` 1/1, `test_static.py` 1/1). The pytest summary line wins.

Also `README.md` and the card `_examples/39-final-project.md`: `order: 39`, eyebrow "Putting it together · Final project", a concept title with no count.

Deletion table (V1a; each in a fresh scratch copy):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| `undo.callback(gateway.cancel, ...)` | removed | 4, 5 | the carrier keeps the booking |
| `undo.callback(plan.release, ...)` | removed | 4, 5, 7 | the slot stays reserved |
| `undo.pop_all()` | removed (experiment a) | 1 | the commit unwinds |
| publish after the `with` | moved inside, before clearance (experiment b) | 8 | the held booking is reported |
| `ExitStack` | `try/except` releasing then cancelling | 5 | order is `release, cancel` |
| `reserve` before `book` | swapped | 6 | a full sailing has already booked the carrier |
| `has_commodities` first in `STAGES` | removed | 11[empty] | the unknown-code stage answers instead (executor check) |
| `Money.__add__` currency check | removed | 14 | a mixed total is computed |
| `settle` equality | `>=` | 13 | executor check: a short payment still fails; an over-payment test is added if needed |
| `history.record` subscription in `build_desk` | removed | 1 | the helper lists `tracking` |
| `FastlineGateway` named in `desk.py` | imported there | 15 | two modules name it |

### `examples/40-working-with-ai-and-llm-tools` (project `review-gate`, package `review_gate`)

- **`domain.py`**: `ConsignmentId`; `RatingError`; frozen slotted `Weight(kilograms)`, `Money(amount, currency="EUR")`, `Consignment(id, zone, weight)`.
- **`pricing.py`**: `type PricingRule = Callable[[Consignment], Money]`; `CENT`; `flat`; `per_kg(consignment, /, *, rate)` half up; `RULES` (read-only `frozendict`: `flat`, `per_kg` at 0.45 through `partial`); `price(rule, consignment, /) -> Money` (EAFP, `RatingError` for an unknown name).
- **`shape.py`**: frozen slotted ordered `Finding(line, rule, advice)`; `type ShapeRule = Callable[[ast.Module], Iterator[Finding]]`; `single_method_base`, `static_only_class`, `accessor_pair`, `instance_in_new`; `SHAPE_RULES` (tuple); `review(source, /, *, rules=SHAPE_RULES) -> list[Finding]` (sorted). Each rule's docstring names the chapter title it comes from.
- **`assistant.py`**: `Assistant` Protocol (`reply(self, prompt: str, /) -> str`); `RecordedAssistant(replies: Mapping[str, Sequence[str]])` (replays in order per prompt, records `prompts`, raises `LookupError("no recorded reply for prompt ...")`); `type Gate = Callable[[str], list[Finding]]`; frozen `Review(source, findings)` with `accepted`; `propose(prompt, /, *, assistant, gates, attempts=2) -> list[Review]` (the fix-up prompt format of evidence J).
- `py.typed`, and an `__init__.py` that imports nothing.
- **`tests/drafts/`**: `untyped_factory.py.txt`, `typed_hierarchy.py.txt`, `rounded_callable.py.txt` (evidence F). Not `.py`, so neither ruff, mypy nor pytest collects them. Each opens with a comment: "Written for the book as a draft to review."

`tests/conftest.py`:
- fixtures `static_gate` (mypy through `mypy.api` with `mypy_path` at `src`, plus ruff through `subprocess` with the repo's selection, both returning `Finding`s with the tool code as `rule`), `draft` (param `untyped_factory|typed_hierarchy|rounded_callable`, returns the text), `load_module` (writes text to `tmp_path` and imports it with `importlib.util`).

`test_gates.py` (holds `GRID` and `EXPECTED_ROWS`, the recorded idiomatic answers as literal `Decimal` strings, so the oracle doesn't use the module under test as its reference; see experiment (a)):
1. `test_each_draft_fails_exactly_the_gates_in_the_table` x `draft` = 3 (evidence I).
2. `test_the_idiomatic_module_passes_every_gate`.
3. `test_the_static_gate_reports_the_untyped_draft`: `["UP037", "UP045", "no-untyped-call", "no-untyped-def"]`.
4. `test_mypy_and_ruff_pass_the_typed_hierarchy`: `([], [])`.
5. `test_the_shape_review_names_the_typed_hierarchy_rules`: `[(7, "single-method-base"), (26, "static-only-class")]` (line numbers move by the header comment: executor check).
6. `test_the_shape_review_names_the_untyped_draft_rules`.
7. `test_the_oracle_lists_the_half_cent_rows` x (`untyped_factory`, `rounded_callable`) = 2.

`test_shape.py`:
8. `test_each_shape_rule_fires_on_its_minimal_case` x 4 rules = 4.
9. `test_shape_rules_stay_quiet_on_a_callable_class_and_a_frozen_dataclass`.

`test_assistant.py`:
10. `test_a_rejected_reply_is_sent_back_with_its_findings`.
11. `test_the_loop_stops_at_the_first_accepted_reply`.
12. `test_the_loop_gives_up_after_its_attempts`.
13. `test_an_unrecorded_prompt_is_refused`.
14. `test_the_package_imports_no_network_module`: `ast` over `src/review_gate/*.py`; no import of `socket`, `ssl`, `http`, `urllib`, `asyncio` or `subprocess`.

`test_static.py`:
15. `test_mypy_refuses_an_assistant_without_reply`: a class with `answer` passed as `assistant=` gives `["arg-type"]`, substring `"Assistant"`. Credits the Protocol annotation on `propose`. Mutation: annotating `assistant: object` makes `src` report `attr-defined`.

Planned: 15 test functions, 21 cases (`test_gates.py` 7/10, `test_shape.py` 2/5, `test_assistant.py` 5/5, `test_static.py` 1/1). The pytest summary line wins.

Also `README.md` and the card `_examples/40-working-with-ai-and-llm-tools.md`: `order: 40`, eyebrow "Putting it together · Working with AI and LLM tools". Card and README say the drafts were written for the book.

Deletion table (V1b):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| `ROUND_HALF_UP` in `pricing.py` | `round(amount, 2)` (experiment a) | 2 | the oracle lists three rows |
| `static_only_class` in `SHAPE_RULES` | removed (experiment b) | 5, 8 | the rule's finding is gone |
| `single_method_base` | removed | 5, 6, 8[single-method-base] | the rule's finding is gone; test 1 still passes because `static_only_class` still flags the typed hierarchy |
| `sorted` in `review` | removed | executor check: `ast.walk` order may already be line order for these drafts; add a test whose rules yield out of order if nothing fails | |
| `accessor_pair` requires both halves | `get_` alone | 9 | a getter-only class is flagged (executor adds the case) |
| `RecordedAssistant` refusal | returns `""` | 13 | no `LookupError` |
| `propose` fix-up prompt | resends the original prompt | 10 | second prompt differs |
| `propose` break on acceptance | removed | 11 | a second reply is requested (`LookupError`) |
| `attempts` | ignored (`while True`) | 12 | executor designs a prompt-exhaustion failure (`LookupError`) |
| ruff selection in `static_gate` | `UP` dropped | 3 | `UP037`, `UP045` gone |

Rows marked "executor check" are resolved at V1b or moved to Corrections.

## Steps and status

Step ids are `V*` (decision 0). Only `V1a`, `V1b`, `V5a` and `V5b` are cited as `run:` tokens.

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| V0 | Bookkeeping with dated notes, re-checking the pins and recording the decisions. In `iteration-plan.md`: PDP-139a-c and 140a-c `active`, r19 active, r18 closed, PDP-137a to 138c closed. In r18's plan: U7 closed. In the reconciliation plan: rows 232-248 `open`; rows 24 and 25 noted "r19". In `chapters.toml`: ch40 `has_example = true`. Domain rows 39-40 as drafted in this commit. The ch39-40 stub `description` lines are written | - | todo |
| V1a | ch39 member, card and README; one `uv lock`; three green runs and one reverse-order run; the deletion table and the static mutation run, each in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`), deleted after use | V0 | todo |
| V1b | ch40 member, drafts, card and README; one `uv lock` after V1a; three green runs plus one reverse-order run; the deletion table; the static mutation run | V1a | todo |
| V2 | Witness results into rows 232-247. `_plans/evidence/r19-sidebar-census.md` (dated: the grep commands, sidebars per doc, each with a nested `>` prompt, the docs with none). The dated r19 note in `_plans/spikes.md` (evidence B to J). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | V1b | todo |
| V3 | Two figures, specs `diagrams/specs/39-*.py` and `40-*.py`, and `_data/diagrams.yml` (single owner; 41 entries). Figures 00-38 unchanged. Every name drawn exists in `src`, conftest, the tests or the standard library | V2 | todo |
| V4 | ch39-40 `status = "drafted"` (kinds unchanged) | V3 | todo |
| V5a | ch39 prose agent: re-fetch every source and quote exactly; run both experiments twice in fresh scratch copies with the stated filter; scrub before quoting; hand back the sources checked and a per-paragraph claims table that marks each sentence as test, source or run | V3, V4 | todo |
| V5b | ch40 prose agent, in parallel with V5a, with the same duties, plus a per-sentence check against decision 5's list: every sentence that mentions a model, an assistant or a reply is either about the book's own code and drafts or an attributed OWASP quotation | V3, V4 | todo |
| V6 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also: close-to-objective mapping, the excerpt check, the not-re-teaching check (criterion 11), decision 5's grep (criterion 20), the cross-language and outcome greps | V5a, V5b | todo |
| V7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r19.x` on main; notes-only release | V6 | todo |

Reconciliation rows (step V0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 232 | 39 | One booking request ships end to end through all seven domain areas, and the shipment settles for the invoice total | `test_a_booking_request_ships_end_to_end`, `test_the_shipment_settles_for_the_invoice_total` |
| 233 | 39 | The acceptance test fails, naming what is missing, when any stage is left out | `test_the_acceptance_test_fails_when_a_stage_is_left_out` |
| 234 | 39 | A held declaration releases the slot and cancels the carrier booking, in reverse order; a full sailing books nothing with the carrier; the freed slot is taken by the next request | `test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking`, `test_the_undo_runs_in_reverse_order_of_the_steps`, `test_a_full_sailing_books_nothing_with_the_carrier`, `test_the_next_request_takes_the_slot_a_rollback_freed`, `source: https://docs.python.org/3/library/contextlib.html` |
| 235 | 39 | Publishing after the commit records nothing for a held booking; an eager publisher reports a booking that was rolled back | `test_a_held_booking_publishes_no_tracking_event`, `test_an_eager_publisher_reports_a_booking_that_was_rolled_back` |
| 236 | 39 | The adapter sends the SDK grams and returns its reference; clearance stops at the first stage that holds; the pricing rule is chosen at the composition root | `test_the_adapter_sends_fastline_grams_and_returns_its_reference`, `test_clearance_stops_at_the_first_stage_that_holds`, `test_the_pricing_rule_is_chosen_at_the_composition_root` |
| 237 | 39 | A short payment doesn't settle, and an invoice in two currencies has no total | `test_a_short_payment_does_not_settle`, `test_an_invoice_in_two_currencies_has_no_total` |
| 238 | 39 | Only the composition root names a concrete carrier, and mypy refuses a gateway without `cancel` | `test_only_the_composition_root_names_a_concrete_carrier`, `test_mypy_refuses_a_gateway_without_cancel` |
| 239 | 40 | Each of the three drafts fails exactly the gates in the table, and the idiomatic module passes every gate | `test_each_draft_fails_exactly_the_gates_in_the_table`, `test_the_idiomatic_module_passes_every_gate` |
| 240 | 40 | The static gate reports the untyped draft's codes and passes the typed class hierarchy | `test_the_static_gate_reports_the_untyped_draft`, `test_mypy_and_ruff_pass_the_typed_hierarchy`, `source: https://mypy.readthedocs.io/en/stable/command_line.html`, `source: https://docs.astral.sh/ruff/rules/non-pep604-annotation-optional/` |
| 241 | 40 | The shape review names each class draft's rules, each rule fires on its minimal case, and the rules stay quiet on a callable class and a frozen dataclass | `test_the_shape_review_names_the_typed_hierarchy_rules`, `test_the_shape_review_names_the_untyped_draft_rules`, `test_each_shape_rule_fires_on_its_minimal_case`, `test_shape_rules_stay_quiet_on_a_callable_class_and_a_frozen_dataclass`, `source: https://docs.python.org/3/library/ast.html` |
| 242 | 40 | The behaviour oracle lists exactly the half-cent rows for both rounding drafts | `test_the_oracle_lists_the_half_cent_rows` |
| 243 | 40 | A rejected reply goes back with its findings, the loop stops at the first accepted reply and gives up after its attempts, and an unrecorded prompt is refused | `test_a_rejected_reply_is_sent_back_with_its_findings`, `test_the_loop_stops_at_the_first_accepted_reply`, `test_the_loop_gives_up_after_its_attempts`, `test_an_unrecorded_prompt_is_refused` |
| 244 | 40 | The package imports no network module, and mypy refuses an assistant without `reply` | `test_the_package_imports_no_network_module`, `test_mypy_refuses_an_assistant_without_reply` |
| 245 | 40 | OWASP advises a zero-trust approach to model output and defines overreliance as trust without verification | `source: https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/`, `source: https://genai.owasp.org/llmrisk/llm092025-misinformation/` |
| 246 | 40 | Every chapter's AI sidebar has the same form (a problem, a nested prompt, one review line), with the counts given | `run: _plans/evidence/r19-sidebar-census.md` |
| 247 | 39-40 | mypy `--strict`, ruff and the idiom scan pass both members | `run: V1a`, `run: V1b` |
| 248 | 39-40 | The "Build, run, observe" experiments behave as quoted | `run: V5a`, `run: V5b` |

Legacy rows carried (V0 notes them "r19"; V2 sets the status):
- Row 24 (the final project integrates all seven areas without a framework): expected **verified (r19)** by rows 232, 233 and 238 plus criterion 15's idiom scan.
- Row 25 (typical LLM output is Java-in-Python and fails strict mypy or the idiom scan): expected **adjusted (r19)**: the claim about typical output is dropped, because it can't be made deterministic without calling a model (decision 5); the gate results for hand-written drafts are rows 239 to 244.

## Corrections after the build

The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.

Lessons carried from r11-r18, which this plan applies up front:
- **Counts.** Per-file counts are summed from the spec, and the pytest summary line wins (r13 to r18; r16 to r18 builds all added tests the deletion runs needed).
- **Members.** Named after the package, with no `[tool.*]` table (r13).
- **Shared tables** in the test module; conftest types under `TYPE_CHECKING`; classes and helpers through fixtures, because a test module can't import `conftest` by name under `--import-mode=importlib` (r13, r14, evidence J).
- **Determinism.** Lists or tuples only in failing assertions, never a set or dict repr (r13 to r17); sort anything from `ast.walk` (evidence G).
- **Witness strength.** An assertion of `!= []` or `pytest.raises` on an exception the harness can also raise is no witness (r18 U1b: `except*`, guard `TimeoutError`; evidence E here). Assert exact lists.
- **Self-referential oracle.** A reference computed by the module under test can't see that module change (experiment a); record the expected rows as literals.
- **Experiment filters.** `E` plus 3, 7, 9 and 11 spaces as separate alternatives, `(tests|src)/.*Error$` and `skipped` (r13 to r18). An experiment that needs more than a one-line change says so (r18 U1b).
- **Reader commands.** No repo script, and never `host_ids.py` (r15).
- **Pointers.** None that describes a stub's content, none circular (r14, r16). ch39 points to ch40 by title only, describing nothing.
- **Claim scrutiny.** Cards, READMEs, conftest, draft headers and `src` docstrings get the same review as chapters (r14, r16, r17, r18).
- **Unverified names.** No unverified chapter title (r16, r17).
- **Quotations** stop where the page's sentence stops (r18 U6 round 1); a title that trips the ban tier is cited through another heading (r18 U5).
- **Voice.** "earns its place" is banned (r15).
- **Close.** Every artifact named in "What you can do now" appears earlier in the chapter (r16).
- **Paths.** Repo-relative only in plans (r09).

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs and once in reverse file order, with the same pass count.
   - `grep -rnE "time\.|perf_counter|datetime|random|sleep|print\(|socket|urllib|requests|httpx"` over both members' `tests` prints nothing.
   - `grep -rnE "monkeypatch|mocker|unittest\.mock|\bpatch\b|\bAny\b|cast\(|print\(|Optional|random|\bglobal\b|sys\.modules|time\.|datetime|exec\(|eval\(|subprocess|socket|urllib|http"` over both members' `src` prints nothing.
   - `subprocess` appears in ch40's `tests/conftest.py` only; no test opens a network connection.
3. Every test name cited in rows 232-244 is defined exactly once across `examples/*/tests`.
4. Static tests assert their exit status, an exact sorted code list and no line number. Every `# type: ignore[...]` and `# noqa` names a code, and there are no unused ignores.
5. Every static test fails on its named mutation (V1a, V1b quote the line).
6. Deletion tables: every row, changed in a fresh scratch copy, makes the named test fail for the stated reason; the handback quotes the failing line. Executor-check rows are resolved or moved to Corrections.
7. Every "undoes", "releases", "cancels", "publishes", "refuses", "catches", "fails", "passes" or "names" sentence names a test with a deletion row, experiment or mutation that makes it fail. Test 2's assertions are exact lists, never `!= []`. Scope words name the test that covers the whole scope, or are cut.
8. ch39-40 are drafted, with one figure each, captions of 20-45 words including `Figure N.1:`, and at most 2,500 prose words each by `validate.py` (a warning below 1,900 is reported, not padded).
9. Spine and sidebar:
   - ch39 passes the `hands-on` spine and ch40 the `argument` spine plus `## Build, run, observe`; `grep -cE "^## (How it works|The argument)$"` is 0 in both.
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `## What you can do now` is the second-to-last H2 with as many bullets as the objectives; every backticked token in it appears earlier.
   - Each sidebar opens with a bold lead and holds a nested `>` prompt; has at most two non-quoted paragraphs; matches no `\bCheck(:| that| three| four| whether)`; is at most 120 words; names only identifiers in the chapter, its `src`, tests or the standard library; and claims nothing about what assistants or models produce.
10. Thesis:
    - ch39 shows undo in reverse, publish after commit and the single composition root, each with its test, and the acceptance test failing per missing stage.
    - ch40 shows the three-gate table and says which gate checks which property; says the drafts were written for the book.
11. Pointers, promises and overlap:
    - ch39 names each composed pattern's chapter by its exact front-matter title (evidence M) and gives no pattern more than one sentence of mechanism; it teaches `ExitStack.callback` and `pop_all`, not `ExitStack` for resources; it points to "Working with AI and LLM tools" by title, describing nothing.
    - ch40 honours "Anti-patterns and pattern misuse"'s promise (general review of generated code), points to "Naming patterns for teams and AI assistants" and "Fowler vs Feathers, contrasted and combined" by title, and doesn't repeat ch04's prompt practices or review checks.
12. Voice:
    - `$S --tier ban --fail --exclude .venv-ft` exits 0 over both chapters, the READMEs, cards, drafts, specs and SVGs, with `--stats` reviewed. "earns its place" appears nowhere.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|optimiz|synchroniz|parallelizat|utiliz)"` over prose (quotations, code and API names excluded) prints nothing.
13. No em or en dash in any file touched in r19, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. Quotations stop before any dash on the source page.
14. `grep -nE "Java|JavaScript|C#|C\+\+|\.NET|\bGo\b|Rust|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]"` over `_docs/39-*.md`, `_docs/40-*.md`, the new READMEs, the cards and the drafts prints nothing.
15. Idiom scan (`lgtm-idiomatic-review`): 0 ban-tier in both members' `src` and `tests`. The drafts are text files and are out of its scope; their findings are the chapter's subject.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs scrubbed before quoting.
17. Every excerpt matches its source byte for byte. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Each experiment runs in a fresh scratch copy, changes one thing and is deleted afterwards. Its filter is stated in the chapter; its output is quoted as the filter's complete output followed by mypy's; and it is run twice with identical output apart from duration.
19. Attribution: every docs and OWASP quotation is exact, attributed and stops where the page's sentence stops; *Architecture Patterns with Python* by verified chapter titles only; every book cited is already in `bibliography.html`. Nothing is copied beyond the quoted sentences.
20. Claims:
    - Every factual sentence maps to a named test, a `run:` token, the census file or a fetched source URL linked in the chapter, in the prose agent's claims table.
    - Decision 5: `grep -niE "\b(models?|LLMs?|assistants?)\b[^.]*\b(often|usually|typically|tend|tends|likely|always|never|produce|produces|generate|generates|hallucinat)"` over ch40 lists only attributed quotations and sentences about the book's own drafts and code; V6 reads each hit. No vendor or model product name appears in either chapter, member, card or README.
    - No outcome statistic: `grep -niE "percent|%|most (teams|projects|developers)|productiv|in production"` over both chapters prints nothing outside code.
    - `validate.py`, `--self-test` and `--claims` exit 0 with rows 232-248 resolved.
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 41 entries, and figures 00-38 are unchanged.
22. Reconciliation rows 232-248 are `verified` or `adjusted` with evidence; legacy rows 24 and 25 carry their r19 status.
23. Deterministic: no test depends on wall time, absolute paths, hash order, test order, `ast.walk` order or the network. `filterwarnings = ["error"]` stays in the root config.
24. CI `ci-ok` is green on the PR; `ci.yml` is unchanged (decision 7). Merge happens only after the owner's explicit approval.
25. Test counts in prose and handbacks come from a fresh pytest summary line.
26. Repo-relative paths only: `grep -rnE "/home/|/Users/"` over the files touched in r19 prints nothing.

## Risks

- **Predicted messages, codes and line numbers.** Expect differences in mypy's code for a missing Protocol member (`[arg-type]` against `[call-arg]` or `[misc]`), the shape findings' line numbers once each draft gains its header comment, and the exact `no-untyped-def` count. Tests match codes and stable substrings; the shape tests' line numbers are re-derived at V1b.
- **mypy cost in tests.** Each static-gate call is a full `mypy.api` run (about 0.3 s each in the probe; the ch40 member ran in about 3.2 s). Acceptable; the cache stays at `/dev/null` for determinism.
- **ruff from a test.** The ruff gate runs the venv's ruff binary through `sys.executable -I -m ruff`, as "Shortcut patterns" does. A ruff upgrade can add codes to the untyped draft (test 3); that is the pin's job, re-checked each release.
- **Executing drafts.** The oracle runs draft code (decision 10). The drafts are the book's text; a reader adapting the oracle to real replies should run it after the other gates and somewhere disposable, and the chapter says so once.
- **House rule on model behaviour.** The likeliest defect is a sentence that slips from "this draft" to "assistants". Criterion 20's grep and V5b's per-sentence check exist for it.
- **Word budgets.** ch39 shrinks first: the left-out-patterns rows of the parts table, then the Billing section to two sentences; tests stay. ch40 shrinks first: the prompt-pattern section to one paragraph, then the minimal-case discussion of the shape rules.
- **Overlap.** ch39 must not re-teach Strategy, Adapter, Chain of Responsibility, Observer or `ExitStack` for resources; ch40 must not re-teach ch04's naming practices or ch35's golden files.
- **Domain collision.** `Settlement` means a duty settlement in "Mediator and Chain of Responsibility" and an invoice settlement here; the ch39 member and prose use only the Billing meaning.
- **`uv.lock` races.** V1a and V1b are sequenced.
- **Nothing upstream.** No finding in r19 goes to a project without the owner, through `lgtm-issue-reporting`.
