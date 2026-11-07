---
title: "r21 plan: appendices D-F (test patterns, pattern-to-force reference, principles)"
order: 21
output: false
render_with_liquid: false
---

# r21: appendices D-F, xUnit test patterns, the pattern-to-force reference and programming principles

Opus-planned 2026-11-07. Branch `release/r21`, cut from main at 97207d4 (the r20 merge, tagged `r20.x`). This file is the source of truth for r21 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No pin changes this iteration. Python 3.15.2, uv 0.13.7, uv_build 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1 and ruff 0.17.4 are still the latest stable releases (checked 2026-11-07 from PyPI JSON `info.version` and the upload date of that release: pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, mypy 2.4.1 of 2026-10-28, ruff 0.17.4 of 2026-11-05, uv and uv-build 0.13.7 of 2026-11-03; `python.org/ftp/python/` lists `3.15.0/`, `3.15.1/`, `3.15.2/` and `3.16.0/`, `3.15.3/` is a 404 and `3.16.0/` holds only `Python-3.16.0a1.tgz`, a pre-release; local `uv --version` prints `uv 0.13.7`; in the scratch environment `pytest --version` prints `pytest 9.2.0`, `ruff --version` `ruff 0.17.4`, `mypy --version` `mypy 2.4.1 (compiled: yes)`, `importlib.metadata.version("pytest-mock")` `3.17.0`, and `sys.version` `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`). X0 re-checks before any edit.

Owner decisions recorded 2026-11-07 (section "Owner decisions, 2026-11-07" below): Appendix F gets a member, `examples/46-appendix-f-programming-principles`, that witnesses the Law of Demeter, and every other recommendation stands. The owner also changed CLAUDE.md's spike finding from a `between=` hook to `gap=` (the GIL chapter's `StowagePlan` parameter); that edit is committed with this amendment.

Exact identities, from `scripts/chapters.toml` and the `_docs` front matter (the front matter wins where wording differs):
- Appendix D: slug `44-appendix-d-xunit-test-patterns`, title "xUnit test patterns (Meszaros)", part 14 (`appendices`), `appendix: "D"`, `kind = "appendix"`, `has_example = false`, `status = "stub"`. PDP-144. The registry row says "Test patterns (Meszaros)"; reader text uses the front-matter title.
- Appendix E: slug `45-appendix-e-pattern-to-force-reference`, title "Pattern-to-force quick reference", part 14, `appendix: "E"`, `kind = "appendix"`, `has_example = false`, `status = "stub"`. PDP-145.
- Appendix F: slug `46-appendix-f-programming-principles`, title "Programming principles reviewed in code", part 14, `appendix: "F"`, `kind = "appendix"`, `has_example = false` (X0 sets `true`, owner decision O1), `status = "stub"`. PDP-146.
- Each stub carries `## Learning objectives`, `## Why this matters`, `## Reference` and `## For deeper coverage`, each "Draft pending.", and a `description` "Draft pending: <title>." The draft replaces `## Reference` with the sections below.
- Part 14's blurb: "Reference material: build and toolchain, pytest, mocking, xUnit test patterns, a pattern-to-force quick reference, and programming principles reviewed in code."

`validate.py` for `kind = "appendix"` (unchanged since r20): SPINE is Learning objectives, Why this matters, For deeper coverage; no figure is required and none is planned; above 2,500 prose words is an error, below 1,900 a warning; `word_count` skips table rows, headings, fenced code, inline code and URLs; the sidebar count runs only for `kind == "pattern"`; `has_example` is metadata only. A reconciliation row's `source:` URL must appear in `_docs/<NN>-*.md` for the number in its Ch cell. A `run: <id>` token resolves when some `_plans/r*-plan.md` has a row `| <id> | ... | done |`, and `run: <path>` when the file exists under `_plans/evidence/`. `check_stale_versions`, `check_banned` (em dash, capstone, PDP ids, iteration ids, the word "spike"), `check_xrefs` and `check_templates` apply to the appendices, the bibliography and any edited chapter.

Work items: PDP-144, PDP-145 and PDP-146, `todo` in `_plans/iteration-plan.md`. The iteration plan quotes no PRD intent for D to F beyond the roadmap line ("r21 | Appendices D-F") and the registry rows; `r01-build-plan.md` names only the slugs. The binding intent is the domain-model rows D, E and F, the promises in chapters and in `bibliography.html` (evidence S), and the house rules. Where a promise asks for something that has no witness in the repo, the promise is corrected in this iteration (fix-now rule), not honoured with an unwitnessed claim (decisions 6 and 12).

## Owner decisions, 2026-11-07

The owner reviewed the decisions below on 2026-11-07. Where an owner decision and a numbered decision differ, the owner decision wins and the numbered decision is amended in place (marked "amended 2026-11-07").

- **O1. Appendix F gets a runnable member** (replaces decision 1's recommendation for F). `examples/46-appendix-f-programming-principles` (project `principles-reviewed`, package `principles_reviewed`, Billing area) holds an `Invoice` before/after for the Law of Demeter, in the layout of `examples/43-appendix-c-mocking`: the reader the package ships asks the shipment for the amount due, and the comparison reader, a conftest fixture param, reaches through the shipment to its invoice. The Law of Demeter is back in F's set, witnessed by the member and sourced from the Demeter project's general-formulation and object-formulation pages at Northeastern University (evidence V; credited, quoted exactly, nothing copied). F names the final project's two chains as counter-examples with the code evidence (decision 16). Member spec: "Example spec" below; build step X1d; rows 307 to 312. `chapters.toml` 46 `has_example = true` at X0. Domain rows D to F as amended in decision 12. D and E keep no member.
- **O2. Everything else as recommended**: D's 26 patterns with summary-only quotes and the qualifier in C (decisions 3, 4); E's four verbatim tables (decisions 8, 9); F's other principles and cuts (decision 5, amended for Demeter only); lengths, no figure, no sidebar (decisions 2, 10); citations (decision 11, amended); the bibliography fixes with Code Complete removed (decision 6); the clause in "Decorators done right" (decision 7); rows 199 to 211 closed at X0 after a re-run (decision 14); the Conditional Test Logic instances recorded for r25 (decision 13).
- **O3. CLAUDE.md.** The owner changed CLAUDE.md line 165 from "with a `between=` hook plus `Barrier`" to "with a `gap=` hook plus `Barrier`". The edit is the owner's and is committed with this amendment; executors still don't edit CLAUDE.md.

## User decisions (owner reviewed 2026-11-07)

0. **Step ids.** The steps are X0 to X6. At planning `grep -nE '^\| X[0-9]' _plans/*.md` and `grep -n 'run: X' _plans/*.md` print nothing (the caller confirmed X is unused). Following r16 to r20, only suffixed ids are cited as `run:` tokens: `X1a`, `X1b`, `X1c`, `X1d` (added 2026-11-07, O1), `X4a`, `X4b` and `X4c`. Plain X0, X2, X3, X5 and X6 appear only in this plan's table. Four `run:` tokens cite recorded files written at X1: `_plans/evidence/r21-test-pattern-map.md` (X1a), `_plans/evidence/r21-pattern-force-census.md` (X1b), `_plans/evidence/r21-principle-witnesses.md` (X1c) and `_plans/evidence/r21-demeter-member.md` (X1d).

   **Recommend: yes.**

1. **No runnable member for D or E; one member for F** (amended 2026-11-07, owner decision O1; the original recommendation was no member for any of the three). D and E are maps onto code that already exists and is already tested; a new member would add tests that witness nothing the existing ones don't.
   - **D.** 25 of the Meszaros patterns that have a fetched page also have at least one existing test that is an instance of the page's definition (evidence D, 37 test names, each defined once). The patterns with a page but no clean instance (Delta Assertion, Data-Driven Test, Test Hook, Dependency Lookup, Humble Object, Back Door Manipulation, Minimal Fixture, Testcase Class per Fixture, Chained Tests, In-line Teardown and the smells) are cut, not built: building a test only so that the appendix can name a pattern would turn the reference into a catalogue tour.
   - **E.** Every row's witness is the developing chapter's sentence plus that chapter's member tests (evidence E). There is nothing to run that the chapters don't already run.
   - **F.** Every kept principle except the Law of Demeter has existing tests in the chapter that teaches it, and three existing before/after pairs tested on one shared table (ch19, ch31, ch32) supply snippets (evidence F). The Law of Demeter has no witness in the repo, so the owner chose the member (O1): `examples/46-appendix-f-programming-principles`, specified under "Example spec" (9 test functions, 15 cases in the planning spike, evidence V).

   The witness for "this test is an instance of that pattern or principle" is a recorded file per appendix (X1a to X1c): each cited test run by node id in a fresh scratch copy three times and once in reverse order, with its one-line reason against the fetched definition.

   **Owner: D and E no member; F member (O1).** The rejected alternative was a D member that builds the cut patterns (Humble Object, Delta Assertion).

2. **Depth and length.** Each appendix is a reference: tables carry the items, prose carries the rule, the trap and the pointer. Prose targets by `validate.py`: D about 1,600 to 2,100 words, E about 700 to 1,100 (almost all of E is tables, which don't count), F about 1,600 to 2,200. The 2,500 ceiling is an error; a warning below 1,900 is reported and never padded (owner decision 2026-11-05; r20 accepted 1,590, 1,661 and 1,890). An item with no witness is cut, not written. At most five excerpts in D, none in E, at most five in F, each byte-exact from an existing test or `src` file. No figure, no experiment, no new code. Each appendix opens with what it isn't: D doesn't repeat the four-doubles table of "Proving it works: pytest, pytest-mock, and mypy" or the API of "Mocking reference: unittest.mock and pytest-mock"; E doesn't repeat the map of "The three-way split: dissolve, survive, disambiguate"; F doesn't re-teach the SOLID chapters.

   **Recommend: yes.** Alternative: E as one table with no prose beyond the spine. The table needs about 300 words of prose to say how to read a row (what "force" means in the book, which bucket the developing chapter gives, why some patterns have two rows).

3. **D's pattern set and its source** (evidence D).
   - **Source.** Gerard Meszaros's site, xunitpatterns.com, which carries the pattern pages of the book in a pre-publication form. Every pattern page says so: "The book has now been published and the content of this chapter has likely changed substanstially." (the site's spelling), and each points to a page number of the printed book. Its footer: "Copyright © 2003-2008 Gerard Meszaros all rights reserved". So D quotes only the one-sentence summary of a page, attributed to the page by URL, never the book by page number, and says once that the site is the pre-publication text and the book (already in `bibliography.html`) is the reference. Nothing beyond the summary sentence is copied; the reasons in D's tables are the book's own words about its own tests. Pages are served over `http://` only (`https://xunitpatterns.com/` timed out at planning).
   - **Set** (each with a page and at least one existing test; evidence D lists the names):
     - Test structure: Four-Phase Test.
     - Fixtures: Fresh Fixture, Shared Fixture, Standard Fixture, Implicit Setup, Inline Setup, Delegated Setup, Creation Method, Implicit Teardown, Automated Teardown.
     - Doubles: Test Double, Dummy Object, Test Stub, Test Spy, Fake Object, Configurable Test Double, Hard-Coded Test Double, Test-Specific Subclass; Mock Object named as the contrast only (decision 4).
     - Verification and test code: State Verification, Behavior Verification, Guard Assertion, Custom Assertion, Test Utility Method, Parameterized Test.
     - Dependency Injection, as Meszaros names it for tests, pointing to "ISP, DIP, and dependency injection without a framework" for the design.
   - **Cut:** SuiteFixture Setup (folded into the Shared Fixture row's test, not named), Assertion Message (the one instance is inside a conftest helper of the GIL chapter), the patterns of decision 1 with no instance, Persistent Fresh Fixture and Mystery Guest (404 at planning), and the smells section (decision 13).

   **Recommend: yes.** Alternatives: (a) cite only the book and quote nothing: the appendix would then rest on no fetched text, against the every-claim rule; (b) the doubles only (five names, as ch11): it leaves the bibliography's "four-phase test" and the fixture vocabulary that B's rows already instantiate unconnected.

4. **D keeps two vocabularies apart, and C gets one qualifier now.** pytest-mock's and `unittest.mock`'s names collide with Meszaros's (evidence D, clashes):
   - `mocker.stub()` is "a mock object that accepts any arguments and is useful to test callbacks" (pytest-mock usage page). The repo uses it as a Test Spy (`test_stub_records_a_callback` asserts its calls) and as a Dummy Object (`test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` never checks it), never as a Meszaros Test Stub, which feeds indirect inputs.
   - `mocker.spy` wraps a real method; the test in C calls the spied method itself, so it isn't capturing a system under test's indirect outputs.
   - `Mock` checks calls after the exercise step, which is the Test Spy's style: the Test Spy page says a spy "does not fail the test at the first deviation from the expected behavior like a Mock Object" (X4a quotes the full sentence or stops before its comma). ch11's "A mock, in his sense, is an object that checks the calls it receives." stays true.
   - The book's `FakeGateway` (configured `amount` and `times_out`, records `booked`) is in Meszaros's terms a Configurable Test Double used as stub and spy, not a Fake Object; the Fake Object page says a fake doesn't act as "a control point to inject indirect inputs". ch11's "A fake is a working, simplified implementation." stays true of the word; D says which Meszaros name each book double fits.
   - "Mocking reference: unittest.mock and pytest-mock" says: "A stub is a callable that records how it was called, for a callback the code under test is given." That is pytest-mock's sense, unqualified. X4a adds "in pytest-mock's sense" (or equivalent, at most five words) to that sentence; nothing else in C changes. Row 306 witnesses it.

   **Recommend: yes.** Alternative: leave C as is and flag the clash only in D. A reader of C alone would carry the wrong Meszaros meaning.

5. **F's principle set** (evidence F). Kept, each with prose in the book, existing tests and a fetched or bibliography source:
   - **SRP, OCP, LSP** ("SRP, OCP, and LSP in Python"), with Design by Contract folded into LSP (the chapter's own pointer to Meyer).
   - **ISP, DIP** ("ISP, DIP, and dependency injection without a framework"), plus the final project's composition-root test.
   - **Composition over inheritance** ("Adapter, Facade, and Bridge", Brandon Rhodes's page, already cited there).
   - **DRY, YAGNI and simple design**, reviewed on the overbuilt rating engine of "Anti-patterns and pattern misuse": its tests count where the fuel surcharge lives, the classes and lines, and the calls, on one shared table (the before/after pair domain row F asks for). Sources: the Pragmatic Programmer's tips page (DRY), Fowler's bliki "Yagni", Fowler's bliki "BeckDesignRules" for simple design. **KISS is not named**: no fetched source defines the acronym, and the chapter's words are Martin's "needless complexity" and Beck's rules.
   - **Orthogonality** (Pragmatic Programmer, promised by the bibliography): the Bridge tests and the SRP change-isolation test.
   - **Fail fast** ("ISP, DIP, and dependency injection without a framework": "An unknown code fails at start-up, where the mistake is cheap to find."; the service-locator test of "Anti-patterns and pattern misuse" as the contrast), source Jim Shore's "Fail Fast" column on martinfowler.com.
   - **EAFP** ("Shortcut patterns: dict dispatch, function tables, and EAFP"), source the Python glossary.

   - **Law of Demeter** (amended 2026-11-07, owner decision O1): witnessed by the F member's tests and sourced from the Demeter project's pages (evidence V); the final project's chains are named as counter-examples (decision 16).

   Cut, each with its reason recorded in X1c: **KISS** as a name, **Tell, Don't Ask** (no prose, no test framed by it), the **Zen of Python** (no chapter quotes it), **Rule of Three**, **Hollywood principle**, **separation of concerns** (folded into SRP by the chapter's own sentence), **do one thing** and the **Boy Scout Rule** (no prose, no test), **Brooks's Law** and **tracer bullets** (project and process claims; no code can witness them, and Brooks's Law is an outcome claim).

   **Recommend: yes.** Alternatives: (a) keep the promised book principles as "source-only" rows marked "not reviewed in code"; this contradicts the appendix's title and the every-claim rule for Brooks's Law; (b) build the Demeter member (decision 1 (a)).

6. **Align the bibliography with what D and F actually use (fix-now).** `bibliography.html` promises more than the appendices can witness (evidence S):
   - Pragmatic Programmer: "The source for DRY, orthogonality, and tracer bullets reviewed in the programming-principles appendix." becomes DRY and orthogonality only.
   - Clean Code: "The source for the Boy-Scout Rule and the do-one-thing discipline behind the programming-principles appendix." becomes the meaningful-names use that "Naming patterns for teams and AI assistants" makes of it (that chapter cites it twice, evidence S).
   - The Mythical Man-Month and Code Complete rows are removed: no chapter or appendix cites either once F drops Brooks's Law and names simplicity through Beck's rules.
   - Meszaros: "...the testing chapter and the test-double reference appendix." becomes "...the testing chapter and the xUnit test patterns appendix." (the appendix's real title).
   - The hub's `_data/books.yml` lists this book under `referenced_by` for all four books; removing it from The Mythical Man-Month and Code Complete is a hub PR of its own, which the orchestrator opens only with the owner's approval after r21 merges (the hub's review notes also name the Java and C++ books, so the entries themselves stay).

   **Recommend: yes.** Alternative: keep Code Complete and verify a chapter of it on simplicity through the O'Reilly connector at X4c; it would be cited by title and topic only, as Okken is in B.

7. **Fix one clause in "Decorators done right" (fix-now).** ch26 says "What stays design is the discipline around it, so the bucket is survives, as [The three-way split: dissolve, survive, disambiguate] sorts it." ch03's map sorts the pair "Decorator pattern vs `@decorator` syntax" as "Needs disambiguating" and links ch26 from that row; ch03 nowhere sorts the discipline as "survives". X4b rewrites the clause so that ch26 keeps its own verdict without attributing it to ch03 (for example "so the bucket is survives; the map in [The three-way split...] files the shared name under needs disambiguating"). Nothing else in ch26 changes. E gives each chapter's own verdict and says that the pair row and the discipline row answer different questions (the shared name, and the discipline around the syntax).

   **Recommend: yes.** Alternative: change ch03's row instead. That would move a map every chapter links to.

8. **E's table format.** Four tables, by catalogue family as the book's parts group them: creational, structural, behavioural, and beyond the catalogue. Columns: Pattern | Bucket | Force | When not to use it | Chapter. Every cell except Pattern and Chapter is a verbatim clause of the developing chapter (decision 9); the Chapter cell is a link whose text is the exact front-matter title. The Bucket cell uses the developing chapter's word (dissolves, survives, needs disambiguating, straddles), and where ch03's map differs (Template Method: ch03 "Dissolves", ch13 "straddles two buckets"; the `@decorator` discipline, decision 7) the row follows the developing chapter and a one-line note says so. Patterns treated in two or three chapters (Proxy in three, Visitor in two, Decorator in two) get one row per chapter, each with that chapter's angle. A short closing list names the techniques that later chapters give a catalogue name to but no bucket (Seam, Monitor Object, Active Object, Strangler Fig) and the three anti-patterns, by chapter title, with no force column. E doesn't repeat ch03's "What Python gives you" column.

   **Recommend: yes.** Alternatives: (a) one table of all rows, sorted by name: easier lookup, but 36 rows wide on a phone and no grouping; (b) a definition list per pattern: more prose, same content.

9. **E quotes the book, and only the book.** A force or when-not cell is a clause copied from the developing chapter, trimmed only at a clause boundary, with links reduced to their text and no ellipsis inside a cell; it is never reworded. The source of each cell (file and line at commit 97207d4) is recorded in X1b's census and re-checked by `grep -F` at X4b and X5. E makes no claim of its own beyond how to read the tables.

   **Recommend: yes.** Alternative: paraphrased one-liners. They would be new claims, each needing its own witness.

10. **No AI sidebar in any appendix.** The r19 census records none in appendices 41 to 46, the validator requires one only for pattern chapters, and r20 placed none in A to C. A reference appendix has no decision rule of its own for a prompt to bake in.

    **Recommend: yes.** Alternative: one sidebar in E with a prompt that asks an assistant to name the force before it proposes a pattern. ch04 and ch40 already carry that advice.

11. **Citation set** (evidence R). Primary sources, quoted exactly and only where fetched; nothing copied beyond the quoted sentences:
    - D: the xunitpatterns.com pages of the kept patterns (decision 3), pytest-mock's usage page (already cited by C) for the `stub` sentence, Fowler's "Mocks Aren't Stubs" (already cited by C and ch11) by title and topic; the book *xUnit Test Patterns: Refactoring Test Code* (bibliography).
    - E: none new. Its sources are the chapters. The "For deeper coverage" section points to the GoF book and Alexander only as ch01 already does (bibliography).
    - F: Brandon Rhodes's "The Composition Over Inheritance Principle" (already cited by ch19), https://pragprog.com/tips/ (DRY and orthogonality tips), https://martinfowler.com/bliki/Yagni.html, https://martinfowler.com/bliki/BeckDesignRules.html, https://martinfowler.com/ieeeSoftware/failFast.pdf (Jim Shore), the Python glossary entry for EAFP (already cited by ch31), and for the Law of Demeter (amended 2026-11-07) https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html and https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html (evidence V); books already in the bibliography: Martin's *Agile Software Development*, Meyer's *Object-Oriented Software Construction*, *The Pragmatic Programmer*, the GoF book.

    **Recommend: yes** (owner: as recommended, with the two Demeter pages added, O1).

12. **Domain rows D to F are corrected at X0.** Row D: "Test doubles named in the shipping tests" becomes "xUnit test patterns mapped onto existing shipping tests; no member". Row E: "One line per pattern and its force" becomes "One row per pattern per developing chapter: bucket, force and when-not quoted from that chapter; no member". Row F (amended 2026-11-07, O1): "DRY, YAGNI, KISS, Law of Demeter on `RateEngine` and `Invoice` code" and "small before/after snippets" become "SOLID, composition over inheritance, DRY, YAGNI and simple design, orthogonality, fail fast, EAFP and the Law of Demeter, reviewed on existing tested code (the before/after pairs of ch19, ch31 and ch32) and on member `examples/46-appendix-f-programming-principles` (`principles_reviewed`, Billing area: `ConsignmentId`, `Money`, `LineItem`, `Invoice`, `Shipment` with `credits` and `amount_due`, `SettlementError`, `settle`, `remittance_line`; test-only `_chained_remittance`, the one comparison form, as fixture param `reader_form` `delegating|chained`)", with key names `Shipment.amount_due`, `reader_form`. No new domain area: a credit is a `LineItem`, and `Shipment` is the final project's name for a booked consignment's record.

    **Owner: yes, as amended (O1).**

13. **No smells section, and no test edits.** The smell pages exist (Fragile Test, Obscure Test, Erratic Test, Assertion Roulette, Test Logic in Production, Conditional Test Logic), and the D survey found instances of Conditional Test Logic in three existing tests (`if before is None` in C's `test_patch_dict_restores_the_mapping_after_the_test`, the `--update-golden` branch of `test_the_golden_file_records_the_legacy_engine`, a branch in `test_each_change_moves_only_the_fields_it_feeds`) and "test seam" wording in `StowagePlan`'s docstring. Whether each is a smell is a judgement the pages don't settle for pytest, and a smells section would need either that judgement or test edits in chapters already validated. D names no smell. X1a records the three instances for the r25 QA sweep.

    **Recommend: yes.** Alternative: a short smells table that names the three instances and fixes them now (fix-now rule): three test edits in ch05, ch35 and C, each re-run and re-validated in r21.

14. **Close the stale r17 rows 199 to 211 at X0** (evidence T). r17 merged (f60cca0, tagged) after its T6 validation, its acceptance criterion 22 required the rows `verified` or `adjusted`, and its T2 note says they resolve, but nobody changed the Status cells. At planning, in a fresh scratch copy: every one of the 21 test names in rows 199 to 209 is defined exactly once; `-k` over those names gave `44 passed, 5 deselected`; both members gave `49 passed` three times, mypy `--strict` `Success: no issues found in 9 source files` for each, `ruff check` `All checks passed!`, `ruff format --check` `20 files already formatted`, the idiom scan 0 ban-tier; the tokens `run: T1a`, `run: T1b`, `run: T5a` and `run: T5b` resolve (r17's steps table marks all four `done`); `validate.py --claims` marks all 13 rows resolved; each of the eleven `source:` URLs returns HTTP 200 and appears in the chapter of its Ch cell (ch35: decimal, json, DefinitionOfRefactoring, refactoring.com, SelfTestingCode, LegacySeam; ch36: bisect, StranglerFigApplication, DarkLaunching, feature-parity, transitional-architecture). X0 sets rows 199 to 211 to `verified (r17; closed at r21 X0 after a re-run, 2026-11-07)` with a dated note in the log. X0 re-runs the three member runs in its own fresh copy before the edit.

    **Recommend: yes.** Alternative: leave them for the r25 sweep. They would stay the only open enforced rows (legacy rows 26 and 27 are also open, below the enforcement line; they belong to r25 and this plan doesn't touch them).

15. **No cross-language wording, no project-outcome statistics, no chapter numbers** in reader text; pointers by exact front-matter title (evidence S). Counts in reader text are counts of the repo (rows, tests) with a witness, never claims about other projects.

    **Recommend: yes.**

16. **F names the final project's chains as counter-examples** (added 2026-11-07, O1; evidence V). Under the object form of the Law of Demeter a method may send messages only to its parameters (including `self`), the immediate parts of the enclosing object and objects it creates. Two places in the final project send past that:
    - `examples/39-final-project/tests/test_acceptance.py` line 40, in the helper `acceptance_failures(shipment, ...)`: `shipment.invoice.total` (and `shipment.invoice.total.amount` on line 41), a message to the shipment's part's part; `tests/test_parts.py` line 98 does the same.
    - `examples/39-final-project/src/final_project/desk.py` line 58: `self._plan.sailing.origin`, a message to an object returned by an immediate part.
    F says what each couples, from the code only: `Shipment` and `Invoice` are frozen dataclasses and the reads change no state; the final project has no credit, so its amount due is the invoice total and a chained read and a delegating one give the same answer there, which is what the member's no-credit rows show; the member's credit test shows the cost appears when the amount due stops being the invoice total. F doesn't call the chains acceptable or wrong beyond that, and the final project's code doesn't change in r21 (its tests stay the acceptance test's own concern). X1d records the four lines with `grep -n` at the branch head.

    **Recommend: yes.** Alternative: change the final project to call a delegating method. It would edit a validated chapter's code and quoted lines in r21.

Also proposed for the owner (no decision needed unless declined):
- **Status hygiene at X0.** r20 is merged (97207d4) and tagged `r20.x`, but `iteration-plan.md` marks r20 "(active)" and PDP-141 to 143 `active`. X0 closes them and marks PDP-144 to 146 and r21 active.
- **A dated r21 note** in `_plans/spikes.md` at X2: evidence D to F and T.
- **CLAUDE.md drift.** CLAUDE.md's spike finding named a `between=` hook for the forced `+=` race; the GIL chapter's member uses `gap=` on `StowagePlan` (evidence D). The owner fixed it on 2026-11-07 (O3).

## Planning evidence

Probes ran in a scratch copy at `<scratchpad>/plan21`, built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <dir>`, then `rm -rf .venv .venv-ft` and `uv sync --locked --all-packages`; `fowler_feathers.__file__` and `refactor_or_rewrite.__file__` pointed into the copy. Sources were fetched into `<scratchpad>/fetch21d` (D) and `<scratchpad>/f21` (F); three read-only survey agents reported D, E and F, and their test names and quotes were re-checked by grep (below). All scratch directories were deleted afterwards; the repo was unchanged apart from this plan (`git status` clean before the commit). No sync ran in the real repo, and no host change was made.

**A. Pins.** See the header.

**B. Baseline.** From the scratch root: `1387 passed in 181.98s (0:03:01)`; 1004 `def test_` lines across `examples` and `spikes`; 41 example members; `_data/diagrams.yml` has 41 entries. The appendix stubs 44 to 46 are 8 prose words each.

**B2. Every test this plan names.** The 124 distinct `test_` names in this file are each defined exactly once across `examples/*/tests` (grep at planning). Run by node id in the scratch copy: `214 passed` three times forward (10.80s, 10.83s, 10.93s) and `214 passed` once in reverse node order. X1a to X1c repeat this for the names they keep, in their own fresh copies.

**C. Reconciliation.** Rows run 1 to 278, so r21 adds 279 onwards. Open rows: legacy 26 and 27 (ch14, ch9; below `CLAIMS_FIRST_ENFORCED = 47`) and r17's 199 to 211 (evidence T). No row names chapter 44, 45 or 46.

**D. Meszaros pages** (fetched 2026-11-07 from `http://xunitpatterns.com/`; 55 candidate pages, 53 returned 200, `Persistent Fresh Fixture.html` and `Mystery Guest.html` returned 404). The raw HTML wraps sentences with tabs, so a quote is exact after collapsing whitespace; ten summaries were re-checked that way at planning. Kept patterns, summary sentence (exact), and the existing tests that are instances (each name defined exactly once across `examples/*/tests`):

| Pattern (page) | Summary sentence | Instances | Why |
| --- | --- | --- | --- |
| Four-Phase Test (`Four%20Phase%20Test.html`) | "Structure each test with four distinct parts executed in sequence." | `test_quote_validity_comes_from_the_injected_clock` (ch11) | fixtures set up, the engine is exercised, the asserts verify, `quote_log` tears down after `yield` |
| Test Double | "We replace a component on which the SUT depends with a "test-specific equivalent."" | the rows below | umbrella |
| Dummy Object | "We pass an object that has no implementation as an argument of a method called on the SUT." | `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` (C) | `notify=mocker.stub()` is passed and never checked |
| Test Stub | "We replace a real object with a test-specific object that feeds the desired indirect inputs into the system under test." | `test_side_effect_drives_the_timeout_branch` (ch11), `test_a_carrier_that_times_out_is_skipped` (C) | an exception fed as an indirect input |
| Test Spy | "Use a Test Double to capture the indirect output calls made to another component by the system under test (SUT) for later verification by the test." | `test_book_best_books_the_winner_and_returns_its_reference` (ch11), `test_stub_records_a_callback` (C), `test_a_rejected_reply_is_sent_back_with_its_findings` (ch40) | the code under test's calls recorded, asserted after the exercise step |
| Mock Object (contrast) | "Replace an object the system under test (SUT) depends on with a test-specific object that verifies it is being used correctly by the SUT." | none as an instance; `test_book_best_books_only_the_winner` (ch11) asserts after the call | the page compares each call with expectations as it arrives |
| Fake Object | "Replace a component that the system under test (SUT) depends on with a much lighter-weight implementation." | `test_the_feed_yields_events_in_order_and_closes_at_the_end` (ch38) | `InMemoryFeed` in place of a carrier feed; X1a confirms or cuts (weak: it is also configured) |
| Configurable Test Double | "Configure a reusable Test Double with the values to be returned or verified during the fixture setup phase of a test." | `test_best_quote_picks_the_cheapest_carrier`, `test_book_best_books_only_the_winner` (ch11) | `FakeGateway` configured in setup; `create_autospec` plus `return_value` is the page's generated variation |
| Hard-Coded Test Double | "Build the Test Double by hard-coding the return values and/or expected calls." | `test_airco_quote_converts_kilograms_and_cents` (ch34), `test_the_acceptance_test_fails_when_a_stage_is_left_out` (ch39) | a closure that always returns one price; an inert gateway |
| Test-Specific Subclass | "Add methods that expose the state or behavior needed by the test to a subclass of the SUT." | `test_every_step_matches_the_characterisation_table` (ch34, the `subclass` step), `test_a_misspelt_override_falls_through_to_the_real_carrier` (ch34) | `_FakeCarrierRateEngine` overrides the extracted carrier calls |
| Fresh Fixture | "Each test constructs its own brand-new test fixture for its own private use." | `test_tmp_path_is_a_fresh_directory_per_test`, `test_a_factory_fixture_builds_a_fresh_object_per_call` (B) | a new directory or object per test |
| Shared Fixture | "We reuse the same instance of the test fixture across many tests." | `test_a_module_scoped_fixture_is_set_up_once_for_the_module`, `test_yield_fixtures_tear_down_in_reverse_order_of_setup` (B) | one setup line for two inner tests |
| Standard Fixture | "The same design of test fixture is used in several tests." | `test_book_best_books_only_the_winner`, `test_side_effect_drives_the_timeout_branch` (ch11) | both take the conftest `consignment` fixture |
| Implicit Setup | "Build the test fixture common to several tests in the setUp method." | `test_an_autouse_fixture_runs_without_being_named` (B) | the framework runs the fixture unasked; `setUp` is in a code span on the page |
| Inline Setup | "Each Test Method creates it's own Fresh Fixture by calling the appropriate constructor methods to build exactly the test fixture it requires." | `test_an_unrecorded_prompt_is_refused` (ch40) | the test calls constructors itself; "it's" is the page's spelling, so X4a quotes up to "Fresh Fixture" or paraphrases |
| Delegated Setup | "Each test creates its own Fresh Fixture by calling Creation Methods from within the Test Methods." | `test_a_quote_rounds_half_up_to_the_cent`, `test_a_clean_batch_returns_its_quotes_in_order` (B) | each calls `make_consignment` |
| Creation Method | "Set up the test fixture by calling methods that hide the mechanics of building ready-to-use objects behind Intent Revealing Names." | `test_a_factory_fixture_builds_a_fresh_object_per_call` (B) | `make_consignment` with defaults (the page's parameterized variation) |
| Implicit Teardown | "The Test Automation Framework calls our clean up logic in the tearDown method after every Test Method." | `test_quote_validity_comes_from_the_injected_clock` (ch11, with `_plans/evidence/yield-fixture-teardown-on-failure.md`), `test_yield_fixtures_tear_down_in_reverse_order_of_setup` (B) | the code after `yield` runs after the test |
| Automated Teardown | "We keep track of all resources that are created in a test and automatically destroy/free them during teardown." | `test_monkeypatch_undoes_its_changes_when_the_context_ends` (ch33), `test_validity_reads_the_environment_and_the_context_restores_it` (ch11) | `monkeypatch` records each change and undoes all of them |
| State Verification | "We inspect the state of the system under test (SUT) after it has been exercised and compare it to the expected state." | `test_a_clean_batch_returns_its_quotes_in_order` (B), `test_best_quote_picks_the_cheapest_carrier` (ch11) | asserts on returned values only |
| Behavior Verification | "We capture the indirect outputs of the SUT as they occur and compare them to the expected behavior." | `test_book_best_books_only_the_winner` (ch11) | `assert_called_once_with`, `assert_not_called` |
| Guard Assertion | "Replace an if statement in a test with an assertion that fails the test if not satisfied." | `test_null_object_is_an_optional_checked_by_mypy` (ch03) | `assert gateway is not None` before the call |
| Custom Assertion | "Create a purpose-built Assertion Method that compares only those attributes of the object that define test-specific equality." | `test_a_booking_request_ships_end_to_end`, `test_the_acceptance_test_fails_when_a_stage_is_left_out` (ch39) | `acceptance_failures` compares only the slice's attributes; it returns a list that `assert ... == []` checks, which D says |
| Test Utility Method | "We encapsulate the test logic we want to reuse behind a suitably named utility method." | `test_the_refactored_engine_matches_the_golden_quotes` (ch35) | `_observed` and `_mismatches` |
| Parameterized Test | "We pass the information needed to do fixture setup and result verification to a utility method that implements the entire test lifecycle." | `test_every_step_matches_the_characterisation_table` (ch34) | each row goes to a helper that builds, exercises and returns; `pytest.mark.parametrize` generates the test functions instead, which D says |
| Dependency Injection | "The client provides the depended-on object to the SUT." | `test_booking_service_runs_against_an_injected_fake` (ch06), `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults` (ch34), `test_two_threads_parked_between_read_and_write_take_the_same_slot` (ch37, `gap=`) | the page's constructor-injection variation, defaults included |

Cut at planning (no clean instance or no page): Persistent Fresh Fixture, Mystery Guest (404), Delta Assertion, Data-Driven Test, Test Hook (the GIL chapter's `gap=` is a parameter taking a callable, which is Dependency Injection, not a testing flag), Dependency Lookup, Humble Object, Back Door Manipulation, Minimal Fixture, Testcase Class per Fixture (no test classes anywhere), Test Helper, Chained Tests, Inline Teardown, Garbage-Collected Teardown, Lazy Setup, Setup Decorator, SuiteFixture Setup and Assertion Message (decision 3), and the smells (decision 13).

Clashes (decision 4): pytest-mock usage page, "The stub is a mock object that accepts any arguments and is useful to test callbacks."; Test Spy page, "Because a Test Spy does not fail the test at the first deviation from the expected behavior like a Mock Object, ..."; Fake Object page, "while a Test Stub acts as a control point to inject indirect inputs into the SUT the Fake Object does not" (a fragment; X4a quotes a whole sentence or paraphrases). Two odd aliases on the site (Dummy Object lists "Stub", Fake Object lists "Dummy") are not repeated.

Book prose D stays consistent with (exact): ch11 line 61 "Gerard Meszaros's *xUnit Test Patterns* (Addison-Wesley, 2007) supplies the vocabulary this chapter uses: *test double* for any stand-in for a collaborator, and the names dummy, fake, stub, spy and mock for the kinds. A fake is a working, simplified implementation. A mock, in his sense, is an object that checks the calls it receives. The chapter titled [xUnit test patterns (Meszaros)](...) covers the taxonomy. This chapter needs only the names."; ch11 line 63 "Python's `unittest.mock` blurs the lines, because one `Mock` object stands in for all of them."; C line 186 (decision 4); C line 287 and ch11 line 391 (Meszaros as the source of the names).

**E. Pattern chapters** (survey of `_docs/`, quotes re-checked). The force is defined in "Patterns as decisions under forces", line 25: "A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other." ch03 line 23 glosses it as "its force, the pressure that made the pattern worth having". Every GoF pattern of the 23 has a developing chapter; none is missing. Bucket sentences at commit 97207d4 (line numbers grep-verified):

| Pattern | Developing chapter (exact title) | Bucket sentence (file:line) |
| --- | --- | --- |
| Factory Method | Factory Method and Abstract Factory | 16:34 heading "Factory Method dissolves" |
| Abstract Factory | same | 16:130 "The bucket is survives." |
| Builder | Builder, dataclasses, and Prototype | 17:36 "...so the bucket is dissolves" |
| Prototype | same | 17:130 "That dissolves too." |
| Singleton | Singleton: module, Borg, and metaclass | 18:41 "The bucket is needs disambiguating..." |
| Adapter, Facade, Bridge | Adapter, Facade, and Bridge | 19:36 "All three patterns in this chapter survive." |
| Decorator pattern vs `@decorator` syntax | Decorator the pattern vs @decorator the syntax, and Proxy | 20:41 "...so they need disambiguating." |
| Proxy (surrogate) | same | none stated in ch20; ch03 line 72 and ch30 line 22 |
| Composite, Flyweight | Composite and Flyweight | 21:23 "Both patterns survive in Python..." |
| Strategy | Strategy: the callable | 12:34 "This pattern dissolves, because a feature resolves the force without the pattern's structure." |
| Template Method | Template Method and the function alternative | 13:36 "The pattern straddles two buckets." (ch03 table: Dissolves; ch03 line 157 section "Patterns that straddle two buckets") |
| State | State and finite state machines | 14:34 "The pattern survives, and the transition table is the design." |
| Command | Command, undo, and command queues | 15:42 "So the bucket is survives, with the deferred call dissolving." |
| Observer | Observer | 22:58 "The bucket is survives..." |
| Mediator, Chain of Responsibility | Mediator and Chain of Responsibility | 23:30 "...both patterns survive because Python's syntax doesn't make those decisions for you." |
| Iterator | Iterator: generators and the iterator protocol | 24:47 "The bucket is dissolves..." |
| Visitor (closed set) | Visitor, Memento, and Interpreter | 25:36 "Python dissolves that machinery..." |
| Memento | same | 25:105 "The bucket is survives, because two decisions stay with you: what to capture, and what must not roll back." |
| Interpreter | same | 25:153 "The bucket is survives, because the grammar and its readings are still design." |
| `@decorator` discipline | Decorators done right | 26:22 "...so the bucket is survives, as [ch03] sorts it." (decision 7) |
| `cached_property` as Proxy | Descriptors and properties | 27:22 "...`cached_property` is where the Proxy name needs disambiguating." |
| Visitor (open set) | singledispatch: the Visitor the language gives you | 28:22 "For an open set of kinds like this one it dissolves into a single generic function..." |
| Metaclass registry | Metaclasses, __init_subclass__, and registries | 29:22 "...so the pattern dissolves..." (preceded by "Since Python 3.6", exempt from the stale-version check by "since"; E quotes from "the pattern dissolves") |
| Proxy (interception) | Dynamic attributes: __getattr__ and Proxy as a feature | 30:22 "That's interception with no surrogate, which is where Proxy is disambiguated..." |
| If-chain dispatch | Shortcut patterns: dict dispatch, function tables, and EAFP | 31:36 "What dissolves is the structure built around it..." |
| Value Object | Dataclasses and value semantics | 08:38 "This pattern dissolves." |
| Null Object | Protocol, duck typing, and structural typing with mypy | 09:62 "This pattern dissolves." |
| "Interface" | same | 09:162 ""Interface" needs disambiguating: the word covers two mechanisms, and they check at different times." |
| Resource acquisition | Context managers: deterministic cleanup | 10:36 "This pattern survives." (10:32 says the label is "descriptive, not a catalogue name") |

Force and when-not sentences: the survey returned one to three exact sentences per row with file:line (for example State, 14:34 "The force is that the legal transitions are a business rule that has to be written in one place and checked." and 14:200 "A two-state flag is a `bool`."; Command, 15:36 "The force is that a change needs an identity of its own." and 15:220 "Call the function when a change is never undone or queued."; Abstract Factory, 16:130 "The force is that products must come from the same family, and a language that stores callables doesn't choose the family."). X1b records every cell's sentence and line in the census and re-checks it with `grep -F`. No `_docs` file contains an em or en dash. The quoted lines use straight apostrophes; curly ones occur only on lines not quoted (14:192, 18:70, 18:177, 24:145, 27:131, 27:158, 27:188, 29:155, 30:147).

Witness tests per row: the survey named 97 tests, each defined exactly once; 43 of them, two or three per family, were re-checked by grep at planning. The spec below names the ones E cites.

Named without a bucket (closing list): Seam and enabling point ("Seams in Python: monkeypatch, injection, and duck typing", 33:32); characterisation test ("Dependency-breaking techniques for modern Python", 34:32); Strangler Fig, cited ("Refactor or rewrite", the heading "A strangler-style router"); Monitor Object and Scoped Locking ("The GIL and performance", 37:78); Active Object ("asyncio and the patterns", 38:170). Anti-patterns ("Anti-patterns and pattern misuse", 32:22 definition): the overbuilt rating engine, getters and setters, service locator. "asyncio and the patterns" also has a bucket table of its own (38:48 to 55); E points to it in one sentence and doesn't copy it.

**F. Principles** (survey, test names re-checked: every one of the 33 names below is defined exactly once).

| Principle | Prose (file:line) | Tests | Source |
| --- | --- | --- | --- |
| SRP | 05:36 "Robert C. Martin states it as "a class should have only one reason to change"..." | `test_each_change_moves_only_the_fields_it_feeds`, `test_pricing_and_tax_run_alone` | Martin, *Agile Software Development* (bibliography) |
| OCP | 05:85 "...take a change you have already seen, a new destination in this case, without reopening code that is tested and in service." | `test_a_new_tax_rule_is_added_without_editing_quote` | Meyer, Martin (bibliography) |
| LSP, Design by Contract | 05:117 "In practice, a subtype may accept more than its supertype and promise more, and it may not accept less or promise less."; 05:245 (Meyer) | `test_calculator_honours_the_rate_contract`, `test_contract_catches_a_strengthened_precondition`, `test_contract_catches_a_weakened_postcondition`, `test_mypy_rejects_an_incompatible_override`, `test_mypy_cannot_see_a_behavioural_violation` | Liskov and Wing, as ch05 cites them; Meyer (bibliography) |
| ISP | 06:24 "Robert C. Martin's interface segregation principle says a client should not be forced to depend on methods it does not use." | `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`, `test_adapters_satisfy_every_role_without_naming_one` | Martin (bibliography) |
| DIP | 06:76 "High-level modules should not depend on low-level modules, and both should depend on abstractions..." | `test_policy_modules_do_not_import_the_adapters`, `test_adapters_import_neither_policy_nor_protocols`, `test_swapping_the_carrier_changes_no_consumer`, `test_only_the_composition_root_names_a_concrete_carrier` (ch39) | Martin; Fowler's injection article (ch06 cites it) |
| Composition over inheritance | 19:166 (Rhodes quotes the GoF principle) | `test_a_class_adapter_still_exposes_the_clients_own_methods`, `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`, `test_every_booking_kind_works_with_every_carrier` | https://python-patterns.guide/gang-of-four/composition-over-inheritance/: "Favor object composition over class inheritance." |
| DRY | 32:68 "Changing how the surcharge is applied means reading five places to find the one that decides." (the word DRY isn't used in the book) | `test_the_fuel_surcharge_lives_in_one_definition_of_the_function` | https://pragprog.com/tips/: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." (the tip title holds an em dash and an entity; not quoted) |
| YAGNI | 32:139 "Add a class or a Protocol only when it holds state, offers several operations or has a second implementation today, and name the change it makes cheaper."; 06:155 | `test_the_engine_needs_more_classes_functions_and_lines_than_the_function`, `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time` | https://martinfowler.com/bliki/Yagni.html (the defining sentence has curly quotes and line breaks in the raw; X4c quotes up to "should not be built now" or paraphrases with the link) |
| Simple design | 01:85 "Martin's warning about needless complexity points the same way..." | `test_one_engine_quote_makes_more_python_calls_than_the_function`, `test_every_rating_form_quotes_the_same_table` | https://martinfowler.com/bliki/BeckDesignRules.html (the four rules, e.g. "Fewest elements") |
| Orthogonality | 19:166 "...so each can change without disturbing the other." | `test_a_new_booking_kind_needs_no_gateway_change`, `test_each_change_moves_only_the_fields_it_feeds` | https://pragprog.com/tips/: "Design components that are self-contained, independent, and have a single, well-defined purpose." |
| Fail fast | 06:143 "An unknown code fails at start-up, where the mistake is cheap to find." | `test_unknown_carrier_fails_at_the_composition_root`; contrast `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered` (ch32) | https://martinfowler.com/ieeeSoftware/failFast.pdf: "A system that fails fast does exactly the opposite: when a problem occurs, it fails immediately and visibly." |
| EAFP | 31:75 (the glossary quote) | `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`, `test_an_eafp_read_reloads_when_another_thread_evicts_first`, `test_two_eafp_readers_that_both_miss_both_load`, `test_every_cache_form_reads_loads_and_evicts_the_same_way` | https://docs.python.org/3/glossary.html (the raw has two spaces after "permission."; ch31 already quotes it) |

Before/after pairs already tested on one shared table: ch32's test-only `_RateEngine` (factory, strategy and visitor in `tests/conftest.py`) against `quote(consignment, tariff)`; ch19's class adapter against the object adapter (the `gateway_form` fixture) and class-per-pair against the bridge; ch31's look-first against EAFP cache forms. `Invoice` exists only in `examples/39-final-project/src/final_project/billing.py`, and no test frames a principle on it; `shipment.invoice.total` appears in the final project's acceptance test (decision 5).

Not discussed anywhere in `_docs/`: Law of Demeter (19:132 is the nearest sentence, about reaching through the adapter's `client` field), Tell, Don't Ask, the Zen of Python (no hit for "PEP 20", "explicit is better", "obvious way"), Rule of Three, Hollywood principle, do one thing, Boy Scout Rule, Brooks's Law, tracer bullets. No `_docs` sentence points to Appendix F.

**R. Sources.** Fetched 2026-11-07: the 55 xunitpatterns.com pages (D), pytest-mock's usage page (D), python-patterns.guide's composition page, pragprog.com/tips, Fowler's Yagni, BeckDesignRules and TellDontAsk pages, the Law of Demeter general-formulation page, PEP 20, the Python glossary, the Fail Fast PDF (F). Every quote above was read from the raw HTML or the PDF's text; X4a to X4c re-fetch each page before quoting.

**S. Repo facts and promises.**
- **Promises the appendices must honour** (grep of `_docs/`, `_parts/`, `_examples/`, `README.md`, `index.html`, `bibliography.html`, the domain model and the example READMEs for the three titles, the three slugs and "Appendix D/E/F"):
  1. "Proving it works: pytest, pytest-mock, and mypy" line 61: "The chapter titled [xUnit test patterns (Meszaros)] covers the taxonomy." D must cover the test-double taxonomy (dummy, fake, stub, spy, mock) with sources, and say where the book's doubles sit in it.
  2. `bibliography.html`, Meszaros row: "The four-phase test and test-double taxonomy behind the testing chapter and the test-double reference appendix." D covers Four-Phase Test; the row's appendix name is corrected (decision 6).
  3. `bibliography.html`, Pragmatic Programmer row: "The source for DRY, orthogonality, and tracer bullets reviewed in the programming-principles appendix." F covers DRY and orthogonality; tracer bullets are cut and the row corrected (decisions 5, 6).
  4. `bibliography.html`, Clean Code row: "The source for the Boy-Scout Rule and the do-one-thing discipline behind the programming-principles appendix." Cut and corrected; "Naming patterns for teams and AI assistants" cites the book at lines 34 and 128 for meaningful names.
  5. `bibliography.html`, Mythical Man-Month row: "The source for Brooks's Law in the programming-principles appendix." Cut; the row is removed (decision 6).
  6. `bibliography.html`, Code Complete row: "Second edition; the construction-practice reference behind the simplicity and maintainability principles reviewed in the programming-principles appendix." Removed unless the owner takes decision 6's alternative.
  7. Domain rows D, E and F (decision 12).
  8. Part 14's blurb (header): satisfied by the three titles.
  9. No chapter links to E or F; ch11 is the only chapter that links D.
- **Exact titles for pointers**: the 47 front-matter titles, listed in evidence E and F; for D also "Proving it works: pytest, pytest-mock, and mypy", "pytest reference", "Mocking reference: unittest.mock and pytest-mock", "ISP, DIP, and dependency injection without a framework".
- **Overlap.** ch03 owns the bucket map, its "What Python gives you" column and the straddlers; E points there and adds the force and the when-not rule. ch11 owns the four-doubles table, its experiments and the claim-witness method; C owns the mock API; B owns the fixture forms; D names the patterns and points to the test that instantiates each. ch05 and ch06 own the SOLID teaching; F states each principle in one or two sentences, quotes the chapter's statement and lists the tests.
- **Hub.** `_data/books.yml` in the hub lists this book under `referenced_by` for The Pragmatic Programmer, Clean Code, The Mythical Man-Month and Code Complete (decision 6).

**T. Stale r17 rows.** Decision 14 holds the run results. r17's steps table marks T1a, T1b, T5a and T5b `done`; r18's U0 closed r17's T6 and T7 on the board but didn't touch the rows.

**U. Not claimable.** That a pattern or principle is "best practice" beyond a quoted sentence; that any test is or was written "to follow" Meszaros (D says a test is an instance of a pattern's definition, not that it was designed from it); the content of the printed book beyond its title and the site's own note; that the repo's tests are free of smells; any statement about the Law of Demeter, KISS, Brooks's Law or tracer bullets; outcomes of applying any principle; anything a pattern chapter doesn't say (E).

**V. The F member and the Law of Demeter** (added 2026-11-07 for owner decision O1).
- **Sources**, fetched 2026-11-07 (raw HTML, whitespace collapsed; no dash in either quote):
  - https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html: ""Only talk to your immediate friends" is the motto."; "Each unit should have only limited knowledge about other units: only units "closely" related to the current unit."; "The style rule was discovered at Northeastern University in the fall of 1987 by Ian Holland."
  - https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html: "Within a method, messages can only be sent to the following objects:" followed by a numbered list (a parameter of the method, including the enclosing object; a global object, "For pragmatic reasons"; an immediate part object, computed or stored; an object created within the method). F paraphrases the list with the link and quotes only the lead sentence.
  - `.../LawOfDemeter/LawOfDemeter.html` returned 404. Neither page is versioned or dated; credit is to the Demeter project at Northeastern by page title.
- **Spike**, in a fresh scratch copy at `<scratchpad>/plan21b` (built the usual way; `uv init --lib --vcs none --no-readme --no-description --author-from none --name principles-reviewed examples/46-appendix-f-programming-principles` printed "Project `principles-reviewed` is already a member of workspace" and created `pyproject.toml`, `src/principles_reviewed/__init__.py` and `py.typed`, with `requires-python = ">=3.15.2"` and `uv_build>=0.13.7,<0.14.0`, edited to the repo's `>=3.15` and `<0.14`; `uv lock` printed `Added principles-reviewed v0.1.0`; `principles_reviewed.__file__` pointed into the copy). A probe of the spec below gave `15 passed` three times from the member, once in reverse file order and once from the root; `mypy --strict src tests` `Success: no issues found in 6 source files`; `ruff check` clean after two raw-string fixes (`RUF043` on `match=` patterns) and `ruff format`; the idiom scan 0 ban-tier. The copy was deleted.
- **Mutations in the spike** (failing tests, exact): `amount_due` ignoring the credits: 6 failed (the amount-due test, the other-currency credit test, `settle` accepts and both refusals, the delegating credit case); `remittance_line` reading `shipment.invoice.total`: 2 failed (the delegating credit case and the delegating attribute case); the `__add__` currency check removed: 1 (the two-currency test); the `__sub__` check removed: 1 (the other-currency credit test); `__str__` without the currency: 8; `payment != due` to `payment.amount < due.amount`: 1 (the `25.01` refusal); `payment < due`: mypy exit 1 (`Money` has no ordering), so that form isn't a row; `total` returning the first line: 10; the comparison reader asking the shipment: 2 (the chained credit case and the chained attribute case); the `credited` fixture without its credit: 5. mypy exit 0 for every row but the one noted. Pytest ids of the indirect cases held spaces (`delegating-CN-3 25.00 EUR`), so the spec gives them explicit ids.
- **Final project chains** (decision 16): `test_acceptance.py:40-41` and `test_parts.py:98` read `shipment.invoice.total`; `desk.py:58` reads `self._plan.sailing.origin`; `billing.py:39` formats `invoice.total.amount` from its parameter. No final-project `Shipment` has credits.
- **Names.** None of the nine planned test names exists in `examples/*/tests` (grep at planning). No member uses project `principles-reviewed` or package `principles_reviewed`. The final project's `test_an_invoice_in_two_currencies_has_no_total` and `test_a_short_payment_does_not_settle` exist, so the member's names differ.

## What is new in each appendix

**D.** The Meszaros vocabulary mapped onto the book's own tests: test structure, fixtures, doubles, verification and dependency injection; and the two places where Python's mock libraries reuse a Meszaros name for something else.

**E.** One lookup table per family with each pattern's bucket, force and when-not rule in the words of the chapter that develops it.

**F.** The principles the book's code already applies, each with the chapter that states it and the tests that show it, and the before/after pairs that compare a principle against its absence on one table; a new member for the Law of Demeter, and the final project's chains named as its counter-examples.

## Approach

- **Thesis wording.**
  - D: the book's tests already use most of Meszaros's patterns under pytest's names; knowing the names makes a suite's intent readable, and two of the mock libraries' names mean something different from his.
  - E: a pattern is chosen for a force, so the quick reference is a table of forces, in the words of the chapters that weighed them.
  - F: the book states a principle where a test can show it; these are the ones its code shows, and each row names its test.
- **Per-row witnesses.** Every pattern, principle and table cell an appendix states appears in its witness table below with: test names (existing), a line of the X1 evidence file, a chapter sentence (file and line, E) or a fetched source URL linked in the appendix. X4a to X4c hand back the table filled with the observed witness per row and add rows for anything their prose names that the table lacks; an item without a witness is cut.
- **Instance rule (D, F).** A test is cited for a pattern or principle only if X1a or X1c can state in one line, against the fetched definition or the chapter sentence, why it is an instance. "Uses a fixture" isn't enough for Shared Fixture; the scope must be shared.
- **Excerpts.** Byte-exact from the named file at the branch head; whole functions or whole fixtures, wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->` where indented, and in `{% raw %}` if they contain `{{`.
- **Counts** come from the repo and a fresh pytest summary line wins (lesson "Recount").
- **Repair rule (r12).** After every repair the validator re-reads the paragraph and the rows that depend on it, and greps the same claim everywhere it can recur (lesson "Grep everywhere").

## Per-appendix spec

Common to all three: front matter keeps `layout`, `order`, `part`, `appendix`; `description` is rewritten from "Draft pending" (X0 writes a one-sentence draft, X4 finalises). Spine headings exactly `## Learning objectives`, `## Why this matters`, `## For deeper coverage`; `## Reference` is removed. No `## What you can do now`; the objectives map to sections by their order. No figure, no sidebar, no experiment. Links to other book pages use `{{ '/docs/<slug>/' | relative_url }}`.

### Appendix D: xUnit test patterns (Meszaros)

Sections (about 1,900 prose words, max 2,500; at most five excerpts):

1. `## Learning objectives` (~70), four bullets: name the four phases of a test and find them in a pytest test; pick the Meszaros name for a fixture's lifetime and setup; name the double a test uses, including when pytest-mock's name says otherwise; say whether a test verifies state or behaviour.
2. `## Why this matters` (~200). Intent first: the names let a reviewer say what a test is for in one word. One sentence that the doubles' refusals are in "Proving it works: pytest, pytest-mock, and mypy" and the API in "Mocking reference: unittest.mock and pytest-mock", not repeated. The source note: the pages quoted are the pre-publication text on Meszaros's site, the book is the reference (decision 3), and every row names an existing test.
3. `## Four-phase test` (~200). The summary sentence; the four phases in `test_quote_validity_comes_from_the_injected_clock` and its `quote_log` fixture, with the teardown-on-failure evidence that ch11 already reports (pointer, not repeated). Excerpt: that test.
4. `## Fixtures: lifetime, setup and teardown` (~450 plus a table). Table: pattern | summary | test | what pytest calls it. Rows: Fresh Fixture, Shared Fixture, Standard Fixture, Implicit Setup, Inline Setup, Delegated Setup, Creation Method, Implicit Teardown, Automated Teardown. Prose: function scope is a Fresh Fixture by default; a wider `scope=` is a Shared Fixture and the order of teardown is B's (pointer to "pytest reference"); `autouse` is Implicit Setup; `monkeypatch` is Automated Teardown. Excerpt: the factory fixture `make_consignment` from B's conftest.
5. `## Test doubles` (~550 plus a table). Table: pattern | summary | the book's double | test. Rows: Test Double, Dummy Object, Test Stub, Test Spy, Fake Object (if X1a keeps it), Configurable Test Double, Hard-Coded Test Double, Test-Specific Subclass; Mock Object as the last row, marked as the contrast. Prose: `FakeGateway` in his terms; why a `Mock` asserted afterwards is spy style (quote the Test Spy sentence); the Test-Specific Subclass of "Dependency-breaking techniques for modern Python".
6. `## Two vocabularies` (~250). pytest-mock's `stub` (quote its usage sentence) used as a spy and as a dummy; `mocker.spy` beside Test Spy; one sentence that "Mocking reference: unittest.mock and pytest-mock" uses pytest-mock's sense (decision 4).
7. `## Verifying results` (~300 plus a table). State Verification, Behavior Verification, Guard Assertion, Custom Assertion (with the "returns a list" caveat), Test Utility Method, Parameterized Test (with the pytest difference). Pointer to Fowler's "Mocks Aren't Stubs" for the state-or-behaviour choice, as C cites it. Excerpt: `acceptance_failures` from the final project's test module.
8. `## Dependency injection in tests` (~150). The summary sentence; the three tests; pointer to "ISP, DIP, and dependency injection without a framework" for the design.
9. `## For deeper coverage` (~100): *xUnit Test Patterns: Refactoring Test Code* (bibliography), the site's pattern pages, "Mocks Aren't Stubs", "pytest reference" and "Mocking reference: unittest.mock and pytest-mock" by title, the bibliography link.

**Witness table D.** "src" means a page URL linked in D (`http://xunitpatterns.com/<Name>.html`, spaces as `%20`).

| Item | What D says | Witness |
| --- | --- | --- |
| Four-Phase Test | four parts in sequence; the ch11 test shows them | `test_quote_validity_comes_from_the_injected_clock`; src |
| Fresh, Shared, Standard Fixture | per test; across tests; one design reused | `test_tmp_path_is_a_fresh_directory_per_test`, `test_a_factory_fixture_builds_a_fresh_object_per_call`, `test_a_module_scoped_fixture_is_set_up_once_for_the_module`, `test_book_best_books_only_the_winner`; src |
| Implicit, Inline, Delegated Setup; Creation Method | framework-run; in the test; through a creation method | `test_an_autouse_fixture_runs_without_being_named`, `test_an_unrecorded_prompt_is_refused`, `test_a_quote_rounds_half_up_to_the_cent`; src |
| Implicit, Automated Teardown | code after `yield`; `monkeypatch` undoes every change | `test_yield_fixtures_tear_down_in_reverse_order_of_setup`, `test_monkeypatch_undoes_its_changes_when_the_context_ends`; `run: _plans/evidence/yield-fixture-teardown-on-failure.md`; src |
| Dummy Object, Test Stub, Test Spy | passed and unchecked; feeds an input; records outputs | `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`, `test_side_effect_drives_the_timeout_branch`, `test_a_carrier_that_times_out_is_skipped`, `test_book_best_books_the_winner_and_returns_its_reference`, `test_stub_records_a_callback`, `test_a_rejected_reply_is_sent_back_with_its_findings`; src |
| Fake Object | lighter-weight implementation | `test_the_feed_yields_events_in_order_and_closes_at_the_end` (X1a keeps or cuts); src |
| Configurable, Hard-Coded Test Double; Test-Specific Subclass | configured in setup; fixed answers; a subclass that overrides | `test_best_quote_picks_the_cheapest_carrier`, `test_airco_quote_converts_kilograms_and_cents`, `test_the_acceptance_test_fails_when_a_stage_is_left_out`, `test_every_step_matches_the_characterisation_table`, `test_a_misspelt_override_falls_through_to_the_real_carrier`; src |
| Mock Object contrast; `Mock` is checked afterwards | the page's definition; the book asserts after the call | `test_book_best_books_only_the_winner`; src Mock Object, Test Spy |
| pytest-mock `stub` and `spy` names | a callback recorder used as spy or dummy; a wrapper the test calls itself | `test_stub_records_a_callback`, `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`, `test_spy_keeps_the_real_behaviour_and_records_returns`; src https://pytest-mock.readthedocs.io/en/stable/usage.html |
| State, Behavior Verification; Guard, Custom Assertion; Test Utility Method; Parameterized Test | as in the section | `test_a_clean_batch_returns_its_quotes_in_order`, `test_book_best_books_only_the_winner`, `test_null_object_is_an_optional_checked_by_mypy`, `test_a_booking_request_ships_end_to_end`, `test_the_refactored_engine_matches_the_golden_quotes`, `test_every_step_matches_the_characterisation_table`; src |
| Dependency Injection | the client provides the dependency, defaults allowed | `test_booking_service_runs_against_an_injected_fake`, `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`, `test_two_threads_parked_between_read_and_write_take_the_same_slot`; src |
| the site is the pre-publication text | the site's own note | src (any pattern page) |

### Appendix E: Pattern-to-force quick reference

Sections (about 900 prose words; no excerpt):

1. `## Learning objectives` (~50), three bullets: find a pattern's force and when-not rule in one place; tell from the bucket whether Python removes the structure; jump to the chapter that weighs it.
2. `## Why this matters` (~250). Intent first: the book chooses a pattern by its force, and the force is the part that stays when the structure dissolves. Quote ch01 line 25 (the definition) and ch03's gloss. How to read a row: every Bucket, Force and When-not cell is the developing chapter's own words (decision 9); a pattern treated in two chapters has two rows; where the map in "The three-way split: dissolve, survive, disambiguate" differs, the row follows the developing chapter and says so. One sentence that the map lists what Python gives for each pattern and isn't repeated here; one sentence pointing to the bucket table of "asyncio and the patterns".
3. `## Creational patterns` (~60 plus a table): Factory Method, Abstract Factory, Builder, Prototype, Singleton.
4. `## Structural patterns` (~80 plus a table): Adapter, Facade, Bridge, Decorator (the pattern, ch20), Proxy (surrogate, ch20), Proxy (`cached_property`, ch27), Proxy (interception, ch30), Composite, Flyweight.
5. `## Behavioural patterns` (~80 plus a table): Strategy, Template Method (straddles; note), State, Command, Observer, Chain of Responsibility, Mediator, Iterator, Visitor (closed set, ch25), Visitor (open set, ch28), Memento, Interpreter.
6. `## Beyond the catalogue` (~80 plus a table): Value Object, Null Object, "Interface", resource acquisition, the `@decorator` discipline (ch26; note, decision 7), metaclass registry, if-chain dispatch.
7. `## Named elsewhere, without a bucket` (~120): Seam, characterisation test, Strangler Fig, Monitor Object, Active Object, and the three anti-patterns, one line each with the chapter title and the chapter's defining clause (evidence E). No force column.
8. `## For deeper coverage` (~80): "Patterns as decisions under forces" and "The three-way split: dissolve, survive, disambiguate" by title; the GoF book and Alexander as ch01 cites them (bibliography); the bibliography link.

**Witness table E.** Per row: the chapter sentences (file:line at the branch head, recorded in `run: _plans/evidence/r21-pattern-force-census.md`) and the tests.

| Row | Tests |
| --- | --- |
| Factory Method | `test_the_creator_design_declares_three_classes_where_the_registry_declares_none`, `test_a_classmethod_constructor_returns_the_subclass_it_is_called_on` |
| Abstract Factory | `test_mypy_rejects_a_kit_that_mixes_reference_types`, `test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate` |
| Builder | `test_a_builder_with_a_step_left_out_fails_only_at_build`, `test_mypy_accepts_a_builder_with_a_step_left_out` |
| Prototype | `test_a_template_and_replace_give_a_new_request`, `test_replace_reruns_the_cross_field_checks` |
| Singleton | `test_every_importer_gets_the_one_tariff_table`, `test_functools_cache_runs_a_loader_twice_when_two_threads_arrive_together` |
| Adapter | `test_a_client_whose_shape_matches_needs_no_adapter`, `test_the_fastline_adapter_translates_the_booking_call` |
| Facade | `test_ship_books_each_carrier_through_one_call`, `test_the_desk_names_no_sdk_type_in_its_public_surface` |
| Bridge | `test_every_booking_kind_works_with_every_carrier`, `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier` |
| Decorator pattern vs syntax | `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs`, `test_the_at_sign_rebinds_the_name_once_at_definition_time` |
| Proxy (surrogate) | `test_the_proxy_asks_the_gateway_once_per_consignment`, `test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price` |
| Proxy (`cached_property`) | `test_chargeable_weight_is_computed_on_first_access_and_stored` |
| Proxy (interception) | `test_nothing_is_loaded_until_a_field_is_read`, `test_a_getattr_that_returns_none_hides_a_typo` |
| Composite | `test_the_total_weight_includes_nested_consolidations`, `test_a_consignment_may_appear_only_once_in_a_consolidation` |
| Flyweight | `test_the_pool_returns_one_commodity_per_code`, `test_a_shared_mutable_commodity_changes_every_consignment` |
| Strategy | `test_a_class_per_strategy_passes_the_same_table`, `test_a_quote_records_the_rule_that_priced_it` |
| Template Method | `test_the_template_and_the_hooks_give_the_same_declaration`, `test_a_required_hook_cannot_be_left_out` |
| State | `test_an_illegal_event_is_a_transition_error`, `test_mypy_reports_a_state_missing_from_the_match` |
| Command | `test_amendments_compare_by_value_and_partials_do_not`, `test_a_failing_batch_leaves_the_booking_unchanged` |
| Observer | `test_one_failing_subscriber_does_not_stop_the_rest`, `test_a_bound_method_subscriber_is_dropped_when_its_owner_goes` |
| Chain of Responsibility | `test_the_first_stage_that_decides_wins`, `test_a_stage_added_after_release_clears_a_restricted_commodity` |
| Mediator | `test_the_mediator_releases_in_either_order`, `test_a_choreography_loses_a_settlement_that_arrives_before_inspection` |
| Iterator | `test_the_first_page_reads_only_one_page`, `test_a_self_iterating_history_is_empty_on_the_second_pass` |
| Visitor (closed) | `test_mypy_reports_an_event_left_out_of_a_match` |
| Visitor (open) | `test_another_module_extends_the_set_when_it_is_imported`, `test_a_raising_fallback_names_an_unregistered_kind` |
| Memento | `test_rollback_restores_the_attached_documents`, `test_rollback_keeps_the_audit_trail` |
| Interpreter | `test_every_rule_form_prices_the_same_consignments`, `test_explain_writes_the_tariff_as_text` |
| Value Object | `test_equal_values_are_interchangeable`, `test_a_mutable_dataclass_is_not_a_dict_key` |
| Null Object | `test_mypy_requires_a_branch_for_absence`, `test_a_null_gateway_hides_a_lost_booking` |
| "Interface" | `test_mypy_checks_protocols_at_use_and_abcs_at_construction` |
| Resource acquisition | `test_writer_closes_and_discards_on_an_exception`, `test_exit_stack_unwinds_entered_writers_in_reverse_order` |
| `@decorator` discipline | `test_wraps_keeps_the_name_qualname_doc_and_module`, `test_stacking_order_decides_whether_a_cache_hit_is_timed` |
| Metaclass registry | `test_the_registry_maps_each_code_to_its_gateway_class`, `test_a_duplicate_code_keeps_the_first_class` |
| If-chain dispatch | `test_every_document_kind_has_an_issuer`, `test_an_if_chain_whose_else_raises_misses_a_new_kind` |
| Named without a bucket; anti-patterns | chapter sentences only (evidence E); `test_the_engine_needs_more_classes_functions_and_lines_than_the_function`, `test_a_setter_lets_a_quoted_consignment_change_its_quote`, `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered` for the anti-patterns |

### Appendix F: Programming principles reviewed in code

Sections (about 2,100 prose words, max 2,500; at most six excerpts, one of them the member's comparison form):

1. `## Learning objectives` (~70), four bullets: state each principle in one sentence and name the test that shows it in this book; read a before/after pair as a measured comparison; say which principle a design change serves; say why a principle with no witness isn't listed.
2. `## Why this matters` (~200). Intent first: a principle is a reason for a shape, and a test is where the reason shows. One sentence that the SOLID chapters teach five of these and aren't repeated; one sentence on the selection rule (a principle is listed where the book's code shows it, decision 5).
3. `## SOLID, by its tests` (~450 plus a table). Table: principle | the chapter's statement (quoted) | tests | chapter title. Rows SRP, OCP, LSP (with Design by Contract), ISP, DIP. Prose: what each test pins, one sentence each; the LSP pair (a contract suite and mypy, each blind to the other's half).
4. `## Composition over inheritance` (~250). Rhodes's quotation of the GoF principle (as ch19 quotes it); the class adapter that still exposes the client's own methods; the class-per-pair count against the bridge. Excerpt: the class adapter comparison form from ch19's conftest or `src`, as it stands.
5. `## Duplication, speculation and size` (~450). DRY (the tips sentence), YAGNI (Fowler's page), simple design (Beck's rules), all on the overbuilt rating engine: where the fuel surcharge lives, classes and lines, calls, a new charge kind, and the shared table both forms pass. Excerpts: the function `quote` and the engine's `_FuelSurcharge` (or the smallest whole class that shows the duplication) from ch32, byte-exact.
6. `## Orthogonality` (~150). The tips sentence; a new booking kind needs no gateway change; one change moves only the fields it feeds.
7. `## Fail fast` (~200). Shore's sentence; an unknown carrier fails at the composition root; the located engine fails at the first quote (the contrast).
8. `## EAFP` (~200). The glossary sentence as ch31 quotes it; the three race tests and the shared cache-form table. Pointer to "Shortcut patterns: dict dispatch, function tables, and EAFP" for the race mechanics.
9. `## The Law of Demeter` (~350). The motto and the general-formulation sentence (quoted), the object form's lead sentence (quoted) and its list (paraphrased, linked). The member: a shipment answers `amount_due()`; the shipped reader names `amount_due` and `consignment_id`, the comparison names `consignment_id`, `invoice` and `total`; both give the same line until a credit is granted, and then only the shipped reader sees it. Excerpt: the comparison reader `_chained_remittance` from the member's conftest (the one comparison excerpt), beside `Shipment.amount_due` and `remittance_line` from `src` (one excerpt). Counter-examples (decision 16): the final project's acceptance helper reads `shipment.invoice.total`, and its desk reads `self._plan.sailing.origin`; what each couples, from the code; that the final project has no credits, so its two readings agree there. One "Running the member" line: from the root once `uv sync --locked --all-packages`; then `cd examples/46-appendix-f-programming-principles`, `uv run pytest -q`, `uv run mypy --strict src tests`; the summary line quoted from a fresh scrubbed run.
10. `## For deeper coverage` (~120): Martin, Meyer, *The Pragmatic Programmer*, the GoF book (bibliography); the fetched pages; the six chapter titles; the bibliography link.

**Witness table F.**

| Item | What F says | Witness |
| --- | --- | --- |
| SRP | one reason to change; a change moves only what it feeds | `test_each_change_moves_only_the_fields_it_feeds`, `test_pricing_and_tax_run_alone` |
| OCP | a new rule arrives as data, `quote` unedited | `test_a_new_tax_rule_is_added_without_editing_quote` |
| LSP, Design by Contract | contract suite plus mypy, each blind to half | `test_calculator_honours_the_rate_contract`, `test_contract_catches_a_strengthened_precondition`, `test_contract_catches_a_weakened_postcondition`, `test_mypy_rejects_an_incompatible_override`, `test_mypy_cannot_see_a_behavioural_violation` |
| ISP | a narrow Protocol spares a fake | `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`, `test_adapters_satisfy_every_role_without_naming_one` |
| DIP | import direction; one composition root | `test_policy_modules_do_not_import_the_adapters`, `test_adapters_import_neither_policy_nor_protocols`, `test_swapping_the_carrier_changes_no_consumer`, `test_only_the_composition_root_names_a_concrete_carrier` |
| composition over inheritance | inherited methods leak; N times M against N plus M | `test_a_class_adapter_still_exposes_the_clients_own_methods`, `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`, `test_every_booking_kind_works_with_every_carrier`; src python-patterns.guide |
| DRY | one definition against five | `test_the_fuel_surcharge_lives_in_one_definition_of_the_function`; src pragprog tips |
| YAGNI, simple design | counts and a new charge kind; one table | `test_the_engine_needs_more_classes_functions_and_lines_than_the_function`, `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`, `test_one_engine_quote_makes_more_python_calls_than_the_function`, `test_every_rating_form_quotes_the_same_table`; src Yagni, BeckDesignRules |
| orthogonality | independent axes | `test_a_new_booking_kind_needs_no_gateway_change`, `test_each_change_moves_only_the_fields_it_feeds`; src pragprog tips |
| fail fast | at the root, not at first use | `test_unknown_carrier_fails_at_the_composition_root`, `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`; src failFast.pdf |
| EAFP | the glossary; the race tests | `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`, `test_an_eafp_read_reloads_when_another_thread_evicts_first`, `test_two_eafp_readers_that_both_miss_both_load`, `test_every_cache_form_reads_loads_and_evicts_the_same_way`; src glossary |
| Law of Demeter, motto and general form | limited knowledge; immediate friends | src general-formulation |
| Law of Demeter, object form | messages to parameters, `self`, immediate parts, created objects | src object-formulation |
| the shipped reader and the comparison agree without credits | same remittance line, both forms | `test_both_readers_give_the_same_line_without_credits` |
| a credit reaches only the reader that asks the shipment | `CN-3 25.00 EUR` against `CN-3 35.63 EUR` | `test_a_credit_reaches_only_the_reader_that_asks_the_shipment` |
| what each reader names | `amount_due`, `consignment_id` against `consignment_id`, `invoice`, `total` | `test_each_reader_names_the_attributes_it_depends_on` |
| amount due, settlement, money | credits subtract; one currency; exact payment only | `test_the_amount_due_subtracts_the_credits`, `test_a_credit_in_another_currency_is_refused`, `test_settle_accepts_the_amount_due`, `test_settle_refuses_any_other_payment`, `test_an_invoice_totals_its_lines`, `test_lines_in_two_currencies_have_no_total` |
| the final project's chains | four lines, what they couple, no credits there | `run: _plans/evidence/r21-demeter-member.md` (the X1d `grep -n` record) |
| the cut list | not stated in reader text | `run: _plans/evidence/r21-principle-witnesses.md` |

Citations, all three: re-fetch before writing; quote no sentence unless checked on a fetched page; stop each quotation where the page's sentence stops, and before any dash; keep curly apostrophes or stop before them; normalise the xunitpatterns.com whitespace only; no outcome claim; no comparison between languages.

## Example spec

### `examples/46-appendix-f-programming-principles` (project `principles-reviewed`, package `principles_reviewed`)

Added 2026-11-07 (owner decision O1). Layout as `examples/43-appendix-c-mocking`: `pyproject.toml` (`requires-python = ">=3.15"`, `dependencies = []`, `uv_build>=0.13.7,<0.14`, no `[tool.*]` table), `README.md`, `src/principles_reviewed/`, `tests/`. Created with `uv init --lib --vcs none --no-readme --no-description --author-from none --name principles-reviewed examples/46-appendix-f-programming-principles`, then edited to those two lines (evidence V). One `uv lock` (`Added principles-reviewed v0.1.0`). The root configuration applies: `mypy --strict`, ruff, `filterwarnings = ["error"]`, `--import-mode=importlib`.

- **`domain.py`**: `ConsignmentId` (`NewType` over `str`); frozen slotted `Money(amount: Decimal, currency: str = "EUR")` with `__add__` (`ValueError` "cannot add <other> to <self>" across currencies), `__sub__` (`ValueError` "cannot subtract <other> from <self>") and `__str__` (`"<amount> <currency>"`, for example `25.00 EUR`). No ordering methods.
- **`billing.py`**: frozen slotted `LineItem(description: str, amount: Money)`; frozen slotted `Invoice(consignment_id, lines: tuple[LineItem, ...])` with a `total` property (needs one line at least, one currency); frozen slotted `Shipment(consignment_id, invoice, credits: tuple[LineItem, ...] = ())` with `amount_due() -> Money` (the invoice total less each credit); `SettlementError(ValueError)`; `settle(shipment, payment, /) -> Money` (refuses any payment but the amount due, message "<payment> does not settle <due>"); `remittance_line(shipment, /) -> str` returning `f"{shipment.consignment_id} {shipment.amount_due()}"`. A credit is a `LineItem` (no new entity). Amounts are illustrative.
- `py.typed`, and an `__init__.py` that imports nothing.

Rejected in `src`: `Any`, `cast`, `Optional`, `print(`, `random`, `global`, `time.`, `datetime`, `sys.modules`, `subprocess`, `socket`, `urllib`, `http`, `mock`, `monkeypatch`, and any attribute chain from a parameter or `self` past an immediate part (the member mustn't break the rule it witnesses; X1d greps it).

`tests/conftest.py`: the comparison form and its fixtures; no `pytest_plugins`.
- `type Reader = Callable[[Shipment], str]`.
- `_chained_remittance(shipment, /) -> str` returning `f"{shipment.consignment_id} {shipment.invoice.total}"`, with a one-line comment that it is the comparison form.
- `READERS: dict[str, Reader] = {"delegating": remittance_line, "chained": _chained_remittance}` (or a read-only `frozendict`, as the repo's other tables, executor's choice; the docstring says which).
- Fixture `reader_form`, `params=["delegating", "chained"]`, returning `READERS[request.param]`.
- Fixture `credited`: `CN-3`, lines freight 30.00 and duty 5.63 EUR, one credit "damaged pallet" 10.63 EUR (amount due 25.00).

`tests/test_billing.py` (functions 1 to 6, 7 cases):
1. `test_an_invoice_totals_its_lines` (35.63).
2. `test_lines_in_two_currencies_have_no_total` (`match=r"^cannot add USD to EUR$"`).
3. `test_the_amount_due_subtracts_the_credits` (`credited`: 25.00).
4. `test_a_credit_in_another_currency_is_refused` (`match=r"^cannot subtract USD from EUR$"`).
5. `test_settle_accepts_the_amount_due` (returns `Money(Decimal("25.00"))`).
6. `test_settle_refuses_any_other_payment` x (`24.99`, `25.01`) = 2 (`match=rf"^{re.escape(paid)} EUR does not settle 25\.00 EUR$"`).

`tests/test_demeter.py` (functions 7 to 9, 8 cases):
7. `test_both_readers_give_the_same_line_without_credits`: rows `one-line` (`CN-1`, 30.00, `"CN-1 30.00 EUR"`) and `two-lines` (`CN-2`, 30.00 and 5.63, `"CN-2 35.63 EUR"`) x `reader_form` (`delegating`, `chained`) = 4.
8. `test_a_credit_reaches_only_the_reader_that_asks_the_shipment`: `reader_form` indirect, `pytest.param("delegating", "CN-3 25.00 EUR", id="delegating")` and `pytest.param("chained", "CN-3 35.63 EUR", id="chained")` = 2. The chained case pins the comparison's wrong answer as a literal.
9. `test_each_reader_names_the_attributes_it_depends_on`: indirect, ids `delegating` and `chained`; the sorted set of `ast.Attribute.attr` names in `inspect.getsource(reader)` (dedented) equals `["amount_due", "consignment_id"]` and `["consignment_id", "invoice", "total"]` = 2. The docstring says what it measures (the attribute names a reader's own source uses) and what it doesn't (calls made inside those attributes).

Planned: 9 test functions and 15 cases (`test_billing.py` 6/7, `test_demeter.py` 3/8); the spike gave `15 passed`. The pytest summary line wins. No `test_static.py`: no claim in F rests on what mypy reports for the member, so no static test is planned (if X4c needs one, X1d adds it and Corrections records it).

Also `README.md` and the card `_examples/46-appendix-f-programming-principles.md`: `order: 46`, eyebrow "Appendices · Programming principles", a concept title with no count; README and card say the comparison reader lives only in `tests/conftest.py`.

Deletion table (X1d; each in a fresh scratch copy, failing tests from the spike, evidence V):

| Check or pinned behaviour | Changed as | Failing tests | Why it sees the change |
| --- | --- | --- | --- |
| `amount_due` subtracts the credits | loop body removed | 3, 4, 5, 6 (both), 8[delegating] (6 failed) | the due stays at the invoice total |
| `remittance_line` asks the shipment | reads `shipment.invoice.total` | 8[delegating], 9[delegating] (2) | the credit is missed; `invoice` and `total` appear |
| `_chained_remittance` reaches through | calls `shipment.amount_due()` | 8[chained], 9[chained] (2) | the comparison stops being one |
| `Money.__add__` currency check | removed | 2 (1) | no `ValueError` |
| `Money.__sub__` currency check | removed | 4 (1) | no `ValueError` |
| `Money.__str__` | currency dropped | 6 (both), 7 (four), 8 (both) (8) | lines and messages change |
| `settle` exact match | `payment.amount < due.amount` | 6[25.01] (1) | an overpayment settles |
| `Invoice.total` sums every line | returns the first line | 1, 2, 3, 5, 6 (both), 7[two-lines] (both forms), 8 (both) (10) | the total changes |
| `credited` fixture | credit removed | 3, 5, 6 (both), 8[delegating] (5) | no credit to see |

Rows are re-run at X1d, each in a fresh copy, and the handback quotes the failing line; a difference goes to Corrections. `payment < due` is not a row: mypy refuses it (evidence V).

## Evidence files (X1)

Each is dated, written in a fresh scratch copy (no `.git`, no `.venv`, `uv sync --locked --all-packages`, a member's `__file__` confirmed inside the copy), scrubbed with `python3 scripts/host_ids.py filter`, and the copy is deleted afterwards. Each lists the commit it ran at.

- **`_plans/evidence/r21-test-pattern-map.md` (X1a).** Per kept D pattern: the page URL, the summary sentence as fetched (whitespace normalised), each cited test's node id, its one-line reason, and the result of running exactly those node ids three times forward and once in reverse order (`-p no:randomly` isn't installed; reverse order by listing node ids reversed). Fake Object kept or cut with its reason. The cut list with reasons. The three Conditional Test Logic instances (decision 13) for r25.
- **`_plans/evidence/r21-pattern-force-census.md` (X1b).** Per E row: each Bucket, Force and When-not cell as it will appear, its file and line, and the result of `grep -cF` on the cell's text in that file (1 each, after link text substitution, which the file records); the tests run as in X1a.
- **`_plans/evidence/r21-demeter-member.md` (X1d).** The member's build record: `uv init` and `uv lock` lines, three forward runs and one reverse-order run from the member and from the root, mypy, ruff, the idiom scan, the deletion table, the `src` grep of the rejected list, and the `grep -n` of the final project's four chain lines (decision 16).
- **`_plans/evidence/r21-principle-witnesses.md` (X1c).** Per kept F principle: the chapter sentence and line, the source sentence as fetched, the tests run as in X1a, and the one-line reason; the cut list with one reason each (decision 5).

## Steps and status

Step ids are `X*` (decision 0). Only `X1a`, `X1b`, `X1c`, `X1d`, `X4a`, `X4b` and `X4c` are cited as `run:` tokens (X1d added 2026-11-07, O1).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| X0 | Bookkeeping with dated notes; re-check the pins; record the decisions. `iteration-plan.md`: r20 closed, PDP-141 to 143 `done`, PDP-144 to 146 `active`, r21 active. Reconciliation plan: rows 199 to 211 closed after a fresh-copy re-run (decision 14); rows 279 to 312 `open` with a dated note. Domain rows D to F (decision 12, amended). `chapters.toml`: 46 `has_example = true` (O1; 44 and 45 stay `false`). `bibliography.html` rows (decision 6). The three stub `description` lines. `verify.sh` and `validate.py` green after the edits | - | done |
| X1a | `_plans/evidence/r21-test-pattern-map.md` | X0 | done |
| X1b | `_plans/evidence/r21-pattern-force-census.md` (parallel with X1a) | X0 | done |
| X1c | `_plans/evidence/r21-principle-witnesses.md` (parallel with X1a) | X0 | done |
| X1d | F member, card and README (Example spec); one `uv lock`; three green runs and one reverse-order run, from the member and from the root; the deletion table, each row in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, `principles_reviewed.__file__` confirmed inside the copy), deleted after use; `_plans/evidence/r21-demeter-member.md`. The only `uv.lock` change is the new member. Runs in parallel with X1a to X1c (it alone touches `uv.lock`) | X0 | done |
| X2 | Witness results into rows 279 to 312 (rows naming a `source` keep the URL as "source (open until prose links it)", as r20's W2 did). The dated r21 note in `_plans/spikes.md`. Every quote, count or reason that differs from Planning evidence goes in "Corrections after the build". A failed witness cuts the row before prose | X1a, X1b, X1c, X1d | todo |
| X3 | `chapters.toml`: 44 to 46 `status = "drafted"` (kinds and `has_example` unchanged); `_data/diagrams.yml` unchanged at 41 entries | X2 | todo |
| X4a | D prose agent, plus decision 4's qualifier in C (one sentence): re-fetch every page and quote exactly; hand back witness table D filled and a per-paragraph claims table | X3 | todo |
| X4b | E prose agent, in parallel, plus decision 7's clause in ch26: every cell re-checked with `grep -F` against the census; witness table E filled | X3 | todo |
| X4c | F prose agent, in parallel, with the same duties for witness table F; excerpts byte-exact; the member's summary line quoted from a fresh scrubbed run | X3 | todo |
| X5 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also: every witness row checked (at least one in three re-run or re-fetched by the validator; every E cell re-grepped), the excerpt check, the overlap check (criterion 11), the cross-language, outcome and stale-version greps, and the "grep everywhere" sweep (criterion 27) | X4a, X4b, X4c | todo |
| X6 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r21.x` on main; notes-only release; after merge and with the owner's approval, the hub PR of decision 6 | X5 | todo |

Reconciliation rows (step X0). The "How to verify" column uses resolvable tokens. Ch `44` is D, `45` E, `46` F.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 279 | 44 | A pytest test with a fixture, a call, an assertion and a `yield` teardown has Meszaros's four phases | `test_quote_validity_comes_from_the_injected_clock`, `run: _plans/evidence/r21-test-pattern-map.md`, `source: http://xunitpatterns.com/Four%20Phase%20Test.html` |
| 280 | 44 | Function-scoped fixtures are Fresh Fixtures, a module-scoped one is a Shared Fixture, and conftest fixtures reused across tests are a Standard Fixture | `test_tmp_path_is_a_fresh_directory_per_test`, `test_a_factory_fixture_builds_a_fresh_object_per_call`, `test_a_module_scoped_fixture_is_set_up_once_for_the_module`, `test_book_best_books_only_the_winner`, `source: http://xunitpatterns.com/Fresh%20Fixture.html`, `source: http://xunitpatterns.com/Shared%20Fixture.html` |
| 281 | 44 | An autouse fixture is Implicit Setup, a test that calls constructors is Inline Setup, and a factory fixture is a Creation Method used by Delegated Setup | `test_an_autouse_fixture_runs_without_being_named`, `test_an_unrecorded_prompt_is_refused`, `test_a_quote_rounds_half_up_to_the_cent`, `source: http://xunitpatterns.com/Creation%20Method.html` |
| 282 | 44 | Code after a fixture's `yield` is Implicit Teardown and `monkeypatch` is Automated Teardown | `test_yield_fixtures_tear_down_in_reverse_order_of_setup`, `test_monkeypatch_undoes_its_changes_when_the_context_ends`, `run: _plans/evidence/yield-fixture-teardown-on-failure.md`, `source: http://xunitpatterns.com/Automated%20Teardown.html` |
| 283 | 44 | The book's doubles are, in Meszaros's terms, dummies, stubs, spies, configurable and hard-coded doubles and test-specific subclasses, each in the named test | `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`, `test_side_effect_drives_the_timeout_branch`, `test_book_best_books_the_winner_and_returns_its_reference`, `test_best_quote_picks_the_cheapest_carrier`, `test_airco_quote_converts_kilograms_and_cents`, `test_every_step_matches_the_characterisation_table`, `source: http://xunitpatterns.com/Test%20Double.html` |
| 284 | 44 | A `Mock` checked after the exercise step works in the Test Spy's style, not as a Mock Object that checks each call as it arrives | `test_book_best_books_only_the_winner`, `source: http://xunitpatterns.com/Test%20Spy.html`, `source: http://xunitpatterns.com/Mock%20Object.html` |
| 285 | 44 | pytest-mock's `stub` is a callback recorder that the book uses as a spy and as a dummy, never as a Meszaros Test Stub; `mocker.spy` wraps a method the test calls itself | `test_stub_records_a_callback`, `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`, `test_spy_keeps_the_real_behaviour_and_records_returns`, `source: https://pytest-mock.readthedocs.io/en/stable/usage.html` |
| 286 | 44 | The named tests verify state, verify behaviour, guard with an assertion, use a custom assertion and a test utility method, and run one helper per table row | `test_a_clean_batch_returns_its_quotes_in_order`, `test_null_object_is_an_optional_checked_by_mypy`, `test_a_booking_request_ships_end_to_end`, `test_the_refactored_engine_matches_the_golden_quotes`, `test_every_step_matches_the_characterisation_table`, `source: http://xunitpatterns.com/Custom%20Assertion.html` |
| 287 | 44 | Passing a collaborator in, with or without a production default, is Meszaros's Dependency Injection | `test_booking_service_runs_against_an_injected_fake`, `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`, `test_two_threads_parked_between_read_and_write_take_the_same_slot`, `source: http://xunitpatterns.com/Dependency%20Injection.html` |
| 288 | 44 | The pages quoted are the pre-publication text on the author's site, which says the book's content has changed | `run: _plans/evidence/r21-test-pattern-map.md`, `source: http://xunitpatterns.com/Test%20Stub.html` |
| 289 | 45 | Every Bucket, Force and When-not cell is a verbatim clause of the chapter the row names | `run: _plans/evidence/r21-pattern-force-census.md`, `run: X4b` |
| 290 | 45 | The creational rows' claims are witnessed by their chapters' tests | `test_the_creator_design_declares_three_classes_where_the_registry_declares_none`, `test_mypy_rejects_a_kit_that_mixes_reference_types`, `test_a_builder_with_a_step_left_out_fails_only_at_build`, `test_replace_reruns_the_cross_field_checks`, `test_every_importer_gets_the_one_tariff_table` |
| 291 | 45 | The structural rows' claims are witnessed by their chapters' tests | `test_a_client_whose_shape_matches_needs_no_adapter`, `test_ship_books_each_carrier_through_one_call`, `test_every_booking_kind_works_with_every_carrier`, `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs`, `test_the_proxy_asks_the_gateway_once_per_consignment`, `test_chargeable_weight_is_computed_on_first_access_and_stored`, `test_nothing_is_loaded_until_a_field_is_read`, `test_the_total_weight_includes_nested_consolidations`, `test_the_pool_returns_one_commodity_per_code` |
| 292 | 45 | The behavioural rows' claims are witnessed by their chapters' tests | `test_a_class_per_strategy_passes_the_same_table`, `test_the_template_and_the_hooks_give_the_same_declaration`, `test_an_illegal_event_is_a_transition_error`, `test_amendments_compare_by_value_and_partials_do_not`, `test_one_failing_subscriber_does_not_stop_the_rest`, `test_the_first_stage_that_decides_wins`, `test_the_mediator_releases_in_either_order`, `test_the_first_page_reads_only_one_page`, `test_mypy_reports_an_event_left_out_of_a_match`, `test_another_module_extends_the_set_when_it_is_imported`, `test_rollback_restores_the_attached_documents`, `test_every_rule_form_prices_the_same_consignments` |
| 293 | 45 | The beyond-the-catalogue rows' claims are witnessed by their chapters' tests | `test_equal_values_are_interchangeable`, `test_mypy_requires_a_branch_for_absence`, `test_mypy_checks_protocols_at_use_and_abcs_at_construction`, `test_writer_closes_and_discards_on_an_exception`, `test_wraps_keeps_the_name_qualname_doc_and_module`, `test_the_registry_maps_each_code_to_its_gateway_class`, `test_every_document_kind_has_an_issuer` |
| 294 | 45 | Each of the 23 catalogue patterns has at least one row, and no row names a pattern without a developing chapter | `run: _plans/evidence/r21-pattern-force-census.md` |
| 295 | 26 | "Decorators done right" states its own bucket for the `@decorator` discipline without attributing it to the three-way split's map | `run: X4b` |
| 296 | 46 | One collaborator change moves only the outputs it feeds, and a new rule arrives without editing `quote` | `test_each_change_moves_only_the_fields_it_feeds`, `test_pricing_and_tax_run_alone`, `test_a_new_tax_rule_is_added_without_editing_quote` |
| 297 | 46 | A contract suite catches a strengthened precondition and a weakened postcondition that mypy can't see, and mypy catches an incompatible override | `test_contract_catches_a_strengthened_precondition`, `test_contract_catches_a_weakened_postcondition`, `test_mypy_rejects_an_incompatible_override`, `test_mypy_cannot_see_a_behavioural_violation` |
| 298 | 46 | A narrow Protocol spares a fake the unused methods, and policy and adapter modules import in one direction with one composition root | `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`, `test_policy_modules_do_not_import_the_adapters`, `test_adapters_import_neither_policy_nor_protocols`, `test_only_the_composition_root_names_a_concrete_carrier` |
| 299 | 46 | A class adapter still exposes the client's own methods, and the class-per-pair design needs a class for every pair where the bridge needs one per axis | `test_a_class_adapter_still_exposes_the_clients_own_methods`, `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`, `source: https://python-patterns.guide/gang-of-four/composition-over-inheritance/` |
| 300 | 46 | The function keeps the fuel surcharge in one definition and the engine in five, and the engine needs more classes, lines and calls for the same table | `test_the_fuel_surcharge_lives_in_one_definition_of_the_function`, `test_the_engine_needs_more_classes_functions_and_lines_than_the_function`, `test_one_engine_quote_makes_more_python_calls_than_the_function`, `test_every_rating_form_quotes_the_same_table`, `source: https://pragprog.com/tips/`, `source: https://martinfowler.com/bliki/Yagni.html`, `source: https://martinfowler.com/bliki/BeckDesignRules.html` |
| 301 | 46 | A new booking kind needs no gateway change | `test_a_new_booking_kind_needs_no_gateway_change`, `test_every_booking_kind_works_with_every_carrier` |
| 302 | 46 | An unknown carrier fails at the composition root, while a located engine fails only at its first quote | `test_unknown_carrier_fails_at_the_composition_root`, `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`, `source: https://martinfowler.com/ieeeSoftware/failFast.pdf` |
| 303 | 46 | An EAFP read survives an eviction between check and read where a look-first read raises, and every cache form passes one table | `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`, `test_an_eafp_read_reloads_when_another_thread_evicts_first`, `test_every_cache_form_reads_loads_and_evicts_the_same_way`, `source: https://docs.python.org/3/glossary.html` |
| 304 | 44-46 | Every test cited in rows 279 to 303 and 307 to 311 is defined once and passes three runs forward and one in reverse order in a fresh copy | `run: X1a`, `run: X1b`, `run: X1c`, `run: X1d` |
| 305 | 44-46 | Every item stated in the three appendices has its witness in the filled witness tables | `run: X4a`, `run: X4b`, `run: X4c` |
| 306 | 43 | "Mocking reference: unittest.mock and pytest-mock" says that its stub is pytest-mock's sense of the word | `run: X4a` |
| 307 | 46 | The reader that asks the shipment for the amount due and the reader that reaches through to the invoice give the same remittance line while there is no credit | `test_both_readers_give_the_same_line_without_credits`, `source: https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html` |
| 308 | 46 | Once a credit is granted, only the reader that asks the shipment reports the amount due; the chained reader reports the invoice total | `test_a_credit_reaches_only_the_reader_that_asks_the_shipment`, `test_the_amount_due_subtracts_the_credits` |
| 309 | 46 | The shipped reader's source names `amount_due` and `consignment_id`; the chained reader's names `consignment_id`, `invoice` and `total` | `test_each_reader_names_the_attributes_it_depends_on`, `source: https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html` |
| 310 | 46 | Money refuses to add or subtract another currency, an invoice totals its lines, and a shipment settles only for the amount due | `test_an_invoice_totals_its_lines`, `test_lines_in_two_currencies_have_no_total`, `test_a_credit_in_another_currency_is_refused`, `test_settle_accepts_the_amount_due`, `test_settle_refuses_any_other_payment` |
| 311 | 46 | mypy `--strict`, ruff and the idiom scan pass the member, three runs and one reverse-order run with the same count, and every deletion row fails its named tests | `run: X1d` |
| 312 | 46 | The final project reads `shipment.invoice.total` in its acceptance helper and `self._plan.sailing.origin` in its desk, and grants no credits | `run: _plans/evidence/r21-demeter-member.md` |

No legacy rows are carried. Rows 199 to 211 change status only (decision 14). Rows 307 to 312 were added 2026-11-07 (O1).

## Corrections after the build
- Step X1a: `r21-test-pattern-map.md` was recorded on 2026-11-07. Of the 26 patterns, 24 have an instance, Mock Object is a contrast only, and Fake Object is **cut**. The planned example, `InMemoryFeed`, is handed the indirect inputs the test wants read, and no double in the repo keeps its own state across calls. Test Spy gains `test_book_best_books_only_the_winner`. Automated Teardown (undone by `monkeypatch.context()` at the end of the `with` block), Custom Assertion (returns a list) and Parameterized Test are qualified. Standard, Inline and Implicit Setup are weak and go to the X5 re-read. All 31 tests (60 cases) passed in three forward runs and one reverse run.
- Step X1b: `r21-pattern-force-census.md` has 33 rows (5, 9, 12, 7) and a closing list of 9. The list adds the characterisation test and the anti-pattern definition to decision 8's seven. Proxy (surrogate) in ch20 has no bucket clause, so its cell is a dash with a note. Conflicts found: ch03's table puts Template Method under Dissolves, but ch03's prose (lines 18, 157 and 163) and ch13:36 say it straddles two buckets. ch03:18 also names Command and Visitor as straddling, while the table files each in one bucket. ch26:22's "survives" contradicts ch03:70 and ch20:41 (decision 7). X4b fixes ch26:22 and the ch03 table so they agree with the chapters' prose.
- Step X1c: `r21-principle-witnesses.md` has 29 tests (52 cases), three forward runs and one reverse run, and every source returned 200. DRY is weak: the fuel rule is spread across five definitions, not copied, so F says "where the rule lives". Simple design covers only "passes the tests" and "fewest elements", so F doesn't claim all four rules. SRP, OCP, LSP, ISP and DIP have no fetched source and rest on the chapters' own sentences. The final project also chains `shipment.quote.total`, `shipment.declaration.duty` (test_acceptance.py:36-39), `self._plan.sailing.origin` again (conftest.py:118) and `invoice.total.amount` (billing.py:39). F lists every one. Its Demeter paraphrase must keep item 2.1 of the object formulation.

The orchestrator records here every handback that differs from this plan: quotes, counts, which tests a row cites, word counts, declined findings, witness rows added or cut.

Lessons carried from r11-r20, which this plan applies up front:
- **Grep everywhere** (r20 W5 rounds 1 and 2). A claim recurs in the appendix, its front-matter `description`, the part's and the examples' `card_blurb`, the README, the bibliography and the chapters that point here; every fix is grepped across all of them in the same round. Both r20 round-2 blockers were round-1 defects left in text the fixes didn't touch.
- **The run wins** (r20 W4b). A doc quote that contradicts a pinned run isn't quoted as fact; here, a page that describes a pattern differently from the repo's test leads to the row being cut, not to a reworded quote.
- **Recount** (r20 W1b, W1c). Counts in prose and handbacks come from fresh runs and greps, never from this plan's numbers (r20's plan miscounted both members).
- **Dated addendum** (r20 W4a). When an evidence file's counts go stale before the prose quotes them, the file gets a dated addendum with the fresh figures, and the prose quotes the addendum.
- **Done tokens** (r20 W2). A step cited by `run:` is marked plain `done` in the table, never `done (date)`.
- **Sources before prose** (r20 W2). Rows that name a `source` hold it as "source (open until prose links it)" until X4 links the URL.
- **Pointers.** Exact front-matter titles only; none that describes a stub's content; none circular (r14, r16, r19, r20 round 1).
- **Claim scrutiny.** The bibliography, cards, READMEs and front matter get the same review as the appendices (r14 to r20).
- **Quotations** stop where the page's sentence stops, and before a dash; a source's own misspelling is quoted as is or not quoted (r18 U6, r20).
- **Voice.** "earns its place" is banned (r15); the voice scan needs `--exclude .venv-ft`; "spike" never appears in reader files, code blocks included (r20 W4b).
- **Paths.** Repo-relative only in plans (r09); `<scratchpad>` in place of the scratch path.
- **Step X0:** (2026-11-07) Pins re-checked and unchanged: PyPI `info.version` pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4, uv and uv-build 0.13.7; `python.org/ftp/python/` lists 3.15.0, 3.15.1, 3.15.2 and 3.16.0 (pre-release). Rows 199 to 211 re-run in a fresh copy as decision 14 says: the 21 names defined once, `-k` gave `44 passed, 5 deselected`, both members `49 passed` three times, mypy `Success: no issues found in 9 source files` for each, ruff clean, `20 files already formatted`; closed. Deviation 1: `validate.py` reads any unresolved `source:` or `run:` token, or a missing test name, as an error for rows from 47, so X0 added only rows 279 to 287, 290 to 293 and 296 to 303 (every test they name exists), with each `source:` written "source (open until prose links it)" and each future `run:` written "run (open until ... )". Rows 288, 289, 294, 295 and 304 to 306 (no evidence that exists yet) are added at X2; rows 307 to 312 at X1d. Deviation 2: the three stub `description` lines and part 14's blurb already read as the plan states, so they are unchanged. Deviation 3: the Clean Code row now points to "Naming patterns for teams and AI assistants" by its exact title. `bash scripts/verify.sh` printed `1387 passed` and `verify: all steps passed`; `validate.py` printed `0 error(s), 3 warning(s)` (the three r20 appendix word counts).
- **Step X1d:** (2026-11-07) The member has 12 test functions and 18 cases, not 9 and 15 (`18 passed`, three runs from the member and from the root, one reverse-file-order run from each, `1405 tests collected` over the whole repository, `verify.sh` `1405 passed`). Three tests were added because the source pins behaviour that none of the planned nine sees: `test_an_invoice_needs_a_line` (the `Invoice.__post_init__` guard; row 10 of the evidence file), `test_settle_refuses_the_right_amount_in_another_currency` (payment equality includes the currency; row 11) and `test_the_comparison_reader_is_not_part_of_the_package` (the README and card say the comparison reader lives only in `tests/conftest.py`; row 12). Because of the second, deletion rows 1, 6, 7, 8 and 9 each fail one more test than the plan's table (7, 9, 2, 11 and 6 failures against 6, 8, 1, 10 and 5); rows 2 to 5 match the plan; the failing lines are in `_plans/evidence/r21-demeter-member.md`. `Invoice.total` is a `functools.reduce` over `Money.__add__` and the table of readers is a `MappingProxyType`;. `test_each_reader_names_the_attributes_it_depends_on` and the other tests in `tests/test_demeter.py` use `type Reader` locally because a test module cannot import the conftest. The final project has a fifth chain line, `billing.py:39` (`invoice.total.amount`, from a parameter), recorded in the evidence file; decision 16's four lines are unchanged. Rows 307 to 312 were added to the reconciliation plan at X1d; row 311's `run: X1d` resolves from this `done`. `src` grep of the rejected list and of chains past an immediate part prints nothing; `uv.lock` gained only the member (6 insertions).

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`; `uv lock --check` passes and the only `uv.lock` change is the new member; the only `examples/` change is the new member, and no `spikes/` file changes (amended 2026-11-07, O1).
1a. The F member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs and once in reverse file order, with the same pass count, from the member directory and from the root; a whole-repo `uv run pytest --co -q` collects with no error. Its `src` grep (Example spec, rejected list) prints nothing; its tests use no `time.`, `random`, `sleep`, `datetime`, `socket` or `urllib`; every assertion compares an exact value, list or message; `_chained_remittance` appears only in `tests/conftest.py`; every deletion row fails its named tests (X1d quotes the line). The idiom scan is 0 ban-tier over `src` and `tests`.
2. Every test name cited in rows 279 to 303 and 307 to 311 and in the three witness tables is defined exactly once across `examples/*/tests`, and every one passes in X1's fresh-copy runs (three forward, one reverse) with the same count.
3. Every D row's test is an instance of the fetched page's definition, with its one-line reason in X1a; Fake Object is kept or cut by X1a.
4. Every E cell other than Pattern and Chapter is found by `grep -F` in the chapter its row names (after link-text substitution), as X1b records and X5 re-checks; no cell is reworded.
5. Every F row names its chapter sentence, its tests and its source; no principle of decision 5's cut list appears in reader text.
6. Every excerpt matches its source byte for byte at the branch head; indented multi-line excerpts are wrapped in fmt guards; excerpts containing `{{` are wrapped in `{% raw %}`.
7. Every "is", "fits", "verifies", "fails", "moves", "spares" or "keeps" sentence about a test names that test, and scope words ("every", "all", "most") name the witness that covers the whole scope, or are cut.
8. Appendices 44 to 46 are drafted, with no figure include, the appendix spine, no `## Reference` heading, and at most 2,500 prose words each by `validate.py` (a warning below 1,900 is reported, not padded).
9. No sidebar: `grep -c '<blockquote class="ai-sidebar"'` is 0 in 44 to 46, and `{: .ai-sidebar}` appears nowhere.
10. Thesis: D maps the taxonomy ch11 promises and keeps the two vocabularies apart; E gives every catalogue pattern a row in its developing chapter's words; F lists only principles with a code witness.
11. Pointers, promises and overlap (evidence S):
    - D covers the taxonomy and Four-Phase Test (promises 1 and 2); the bibliography rows say what D and F use (decision 6).
    - Pointers use exact front-matter titles.
    - D doesn't repeat ch11's four-doubles table or experiments, B's fixture rows or C's API; E doesn't repeat ch03's "What Python gives you" column; F doesn't re-teach ch05 or ch06.
    - ch26 differs from main by the one clause of decision 7, and C by the qualifier of decision 4.
12. Voice:
    - `$S --tier ban --fail --exclude .venv-ft` exits 0 over the three appendices, `bibliography.html`, ch26 and C, with `--stats` reviewed. "earns its place" appears nowhere.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per appendix outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|optimiz|synchroniz|parallelizat|utiliz)"` over prose prints nothing outside quotations, code and pattern names (Meszaros's "Behavior Verification" and Rhodes's "Favor" are names or quotations and stay as spelt).
13. No em or en dash in any file touched in r21, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. Quotations stop before any dash on the source page.
14. `grep -nE "Java|JavaScript|C#|C\+\+|\.NET|\bGo\b|Rust|capstone|PDP-|\br[0-9]{2}\b|spike|[Cc]hapter [0-9]"` over `_docs/44-*.md`, `_docs/45-*.md`, `_docs/46-*.md` and the changed lines of ch26, C and `bibliography.html` prints nothing.
15. `python3 scripts/host_ids.py check` exits 0. No scratch or home path appears in any tracked file.
16. Attribution: every quotation is exact, attributed and stops where the page's sentence stops; books by title only and only books already in `bibliography.html`; the xunitpatterns.com pages are credited as the author's pre-publication text; nothing is copied beyond the quoted sentences.
17. Claims:
    - F's Law of Demeter section names the final project's lines only as decision 16 states, with no claim beyond the code.
    - Every factual sentence maps to a named test, a `run:` token, an evidence file line, a chapter sentence or a fetched source URL linked in the appendix, in the prose agent's claims table.
    - No outcome statistic: `grep -niE "percent|%|most (teams|projects|developers)|productiv|in production"` over the three appendices prints nothing outside code.
    - `validate.py`, `--self-test` and `--claims` exit 0 with rows 279 to 312 resolved; `check_stale_versions` reports nothing for the three appendices.
18. `chapters.toml` 46 has `has_example = true`, 44 and 45 `false`; the card `_examples/46-appendix-f-programming-principles.md` renders. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 41 entries, unchanged.
19. Reconciliation rows 279 to 312 are `verified` or `adjusted` with evidence; rows 199 to 211 are `verified (r17 ...)` per decision 14; no other row changes.
20. CI `ci-ok` is green on the PR; `ci.yml` is unchanged. Merge happens only after the owner's explicit approval; the hub PR only after a second approval.
21. Test counts in prose and handbacks come from a fresh pytest summary line.
22. `bibliography.html` keeps its structure; the removed rows leave no dangling reference (`grep -n "Mythical\|Code Complete"` over `_docs/` and `bibliography.html` prints nothing unless decision 6's alternative is taken).
23. The domain-model rows D to F match decision 12.
24. Each appendix's `description` and any card or index text that mentions it says only what the appendix does (lesson "Grep everywhere").
25. Reverse-order and repeat runs (criterion 2) show no order dependence among the cited tests.
26. The three Conditional Test Logic instances are recorded in X1a for r25 and no test is edited (decision 13), unless the owner takes decision 13's alternative.
27. Before handback of X5: every claim fixed in a repair round is grepped across the appendix, its `description`, `bibliography.html`, the chapters that point here (ch11, ch26, C) and `README.md`, and the grep is recorded in Corrections.

## Risks

- **Pre-publication text.** The site says the book's chapters changed after the pages were written, so a summary sentence may differ from the book's. D quotes only the site and says so; it attributes nothing to a printed page.
- **Instance judgements.** "This test is a Test Spy" is an interpretation against a definition. The instance rule (one-line reason per test, X1a) and the cut-when-unsure rule bound it; X5 re-reads one in three.
- **Vocabulary drift into other pages.** D's careful names could contradict ch11's or C's looser use; decision 4 fixes C's one sentence, and criterion 27's sweep greps "stub", "spy", "fake" and "mock" in ch11, C and D after every repair.
- **E line drift.** Line numbers in the census move if ch26 or another chapter is edited; the census records file and text, and the grep is on the text, not the line.
- **E quoting links.** Chapter sentences contain Liquid links; a cell copies the link text, never the `{{ ... }}`, so `check_templates` sees nothing unwrapped.
- **Stale versions.** "Since Python 3.6" in the metaclass chapter must not be copied into E without "since" (exempt) or at all; E's cell starts after it.
- **Word budgets.** E will sit far below 1,900 (warning, reported). D and F may too; never pad.
- **Bibliography and hub.** Removing two books changes a page the hub links; the hub PR is separate and owner-approved. If the owner keeps them, criterion 22 changes.
- **Overlap.** The likeliest defect is D re-teaching ch11's doubles table or C's API, or F re-teaching ch05; criterion 11 and X5 check it.
- **The member breaking its own rule.** A `src` line in the member that chains past an immediate part would contradict F; X1d greps for it, and X5 re-reads `billing.py`.
- **Attribute-name witness scope.** Test 9 measures the names a reader's own source uses, not the calls made inside them; F says that, and doesn't claim the test detects every violation of the object form.
- **`uv.lock` races.** X1d is the only step that changes `uv.lock`.
- **Nothing upstream.** No finding in r21 goes to a project without the owner, through `lgtm-issue-reporting`.
