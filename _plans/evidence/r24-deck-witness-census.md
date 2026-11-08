---
title: "Evidence: Deck 301 witness census (r24, D1b)"
output: false
render_with_liquid: false
---

# Deck 301 witness census

Recorded 2026-11-07 for r24, step D1b, on Python 3.15.2 and pytest 9.2.0, at commit `4b7ee31` on `release/r24` (after D1c, so every line, anchor, count and figure below is read from the fixed tree; the working tree then held only this file and the reconciliation rows). Paths are repo-relative; `<copy>` stands for the fresh scratch copy of the tree and `<scratch>` for the session scratch directory.

## Method

- Each of the 42 slides of the plan's inventory is recorded with its claim in the deck's standalone wording, the exact front-matter title of the chapter it rests on, and the chapter sentences it rests on. A sentence is a fragment re-found with `grep -nF -- <fragment> <chapter file>`. A fragment is accepted only when it hits exactly one line, and the sentence that contains it is quoted exactly as it stands now. The plan's own line numbers are listed beside the census lines so that D1c's drift is visible.
- A witness test is cited by exact name. Each was searched with `^\s*(async )?def <name>\(` under `examples/*/tests/**/*.py` and has exactly one definition, at column 0 (none inside a class), so a node id is `<file>::<name>`. A test in the "Witness" list is a witness of the slide's claim; a test in the "Notes witness" list backs a sentence the notes may say. Both kinds are run.
- A code slide gives the source path, the 1-based range, the anchor (the exact first line, with its indentation), the line count, the longest line and the chapter fence the range is a contiguous run of. The check compares the range, line for line and byte for byte, with every python fence of the chapter and takes the first fence that contains it as a contiguous run; a match means the excerpt is byte-exact with what the chapter quotes. The builder reads the range from the file and asserts the anchor.
- A figure slide names the figure, its committed PNG and the arrow census re-run against the code now (section "Figure census").
- Every witness test was run by node id in a fresh scratch copy (section "Witness test runs"), and every recorded experiment a note may quote was re-run there (section "Numbers in the notes"). No timing is recorded or quoted anywhere in this file.

## Summary

42 slides. 41 kept as the plan has them, 1 narrowed (slide 7), 0 cut. Every content, code, figure and table slide has at least one witness test or a recorded chapter sentence, and no claim is stretched beyond them. The slide-kind counts are 1 cover, 1 route slide, 8 dividers, 18 code, 2 figures, 5 tables, 7 bullet slides including the closing slide (the route slide is counted with the cover).

| # | Section | Title | Kind | Disposition | Reason |
| --- | --- | --- | --- | --- | --- |
| 1 | Cover | Design Patterns with Python | cover | kept | structural slide |
| 2 | Cover | Seven themes | bullets | kept | structural slide; standalone wording below |
| 3 | Proving it works | divider | divider | kept | structural slide |
| 4 | Proving it works | Tests named as claims | code | kept | claim, witnesses and range confirmed |
| 5 | Proving it works | What each double refuses | table | kept | claim, witnesses and table cells confirmed |
| 6 | Proving it works | Autospec copies signatures | code | kept | claim, witnesses and range confirmed |
| 7 | Proving it works | Clock and environment | code | narrowed | the plan's range tests/test_engine.py:68-80 (the clock test) is not a run of any chapter fence, so the slide shows the environment test (tests/test_environment.py:8-20, a whole fence) and is retitled from 'An injected clock' to 'Clock and environment'; the clock test stays a witness of the claim |
| 8 | Fixtures and test doubles | divider | divider | kept | structural slide |
| 9 | Fixtures and test doubles | Settings that refuse silence | bullets | kept | claim and witnesses confirmed |
| 10 | Fixtures and test doubles | Same-name test files | code | kept | claim, witnesses and range confirmed |
| 11 | Fixtures and test doubles | Calls recorded in order | code | kept | claim, witnesses and range confirmed |
| 12 | Fixtures and test doubles | Two vocabularies | table | kept | claim, witnesses and table cells confirmed |
| 13 | Seams in Python | divider | divider | kept | structural slide |
| 14 | Seams in Python | An engine kept as found | code | kept | claim, witnesses and range confirmed |
| 15 | Seams in Python | Patch where it's looked up | figure | kept | claim and witnesses confirmed; the figure passes the census |
| 16 | Seams in Python | A default captured early | code | kept | claim, witnesses and range confirmed |
| 17 | Seams in Python | What mypy sees of a patch | bullets | kept | claim and witnesses confirmed |
| 18 | Breaking dependencies | divider | divider | kept | structural slide |
| 19 | Breaking dependencies | A characterisation table | code | kept | claim, witnesses and range confirmed |
| 20 | Breaking dependencies | Carriers as parameters | code | kept | claim, witnesses and range confirmed |
| 21 | Breaking dependencies | The engine as a function | code | kept | claim, witnesses and range confirmed |
| 22 | Breaking dependencies | A misspelt override | bullets | kept | claim and witnesses confirmed |
| 23 | Refactor or rewrite | divider | divider | kept | structural slide |
| 24 | Refactor or rewrite | Intent rows and golden quotes | bullets | kept | claim and witnesses confirmed |
| 25 | Refactor or rewrite | A golden comparison | code | kept | claim, witnesses and range confirmed |
| 26 | Refactor or rewrite | The rewrite's quote | code | kept | claim, witnesses and range confirmed |
| 27 | Refactor or rewrite | Parity and accepted differences | bullets | kept | claim and witnesses confirmed |
| 28 | Refactor or rewrite | A router with a shadow | code | kept | claim, witnesses and range confirmed |
| 29 | The final project | divider | divider | kept | structural slide |
| 30 | The final project | An acceptance test first | code | kept | claim, witnesses and range confirmed |
| 31 | The final project | Undo in reverse | code | kept | claim, witnesses and range confirmed |
| 32 | The final project | Publish after the commit | code | kept | claim, witnesses and range confirmed |
| 33 | The final project | One composition root | code | kept | claim, witnesses and range confirmed |
| 34 | Working with AI tools | divider | divider | kept | structural slide |
| 35 | Working with AI tools | Three drafts, three gates | table | kept | claim, witnesses and table cells confirmed |
| 36 | Working with AI tools | Gates in parallel | figure | kept | claim and witnesses confirmed; the figure passes the census |
| 37 | Working with AI tools | A seam for the model | code | kept | claim, witnesses and range confirmed |
| 38 | Working with AI tools | Limits of the gates | bullets | kept | claim and witnesses confirmed |
| 39 | Reference | divider | divider | kept | structural slide |
| 40 | Reference | Sources credited | table | kept | credits table; built from the chapters' own links |
| 41 | Reference | Reading further | table | kept | credits table; built from the chapters and the bibliography |
| 42 | Reference | Site and repository | bullets | kept | URLs return 200; pins re-read from the tree |

## Per-slide census

Every chapter sentence below is a `grep -nF` fragment that hit exactly one line of the named chapter at this commit, and the sentence is quoted as it stands. Every test name was found once under `examples/*/tests`. A slide with a figure or code range names the figure or the source file and lines.

### Slide 1: Design Patterns with Python (Cover)

- Claim: 301: Testing, legacy code and AI.
- Chapter: none; a structural slide.
- Notes cover:
  - Testing, inherited code and AI replies held to gates; the shipping domain; every example is tested code.
- Disposition: **kept**. structural slide.

### Slide 2: Seven themes (Cover)

- Claim: The seven themes and the reference, one bullet each, with no ordinals.
- Chapter: none; a structural slide.
- Notes cover:
  - Each of the seven themes by its subject, with no ordinals, then the reference.
- Disposition: **kept**. structural slide; standalone wording below.

### Slide 3: divider (Proving it works)

- Claim: -
- Notes cover: a claim, its witness and a check seen failing.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 4: Tests named as claims (Proving it works)

- Claim: A test is named for the claim it witnesses, so a failure reads as a broken sentence. A check that was never seen failing is a guess, so it is deleted in a scratch copy to confirm the test fails. The winner's reference is asserted before the calls.
- Chapter: 11, "Proving it works: pytest, pytest-mock, and mypy" (`_docs/11-testing-with-pytest-pytest-mock-and-mypy.md`).
- `11-testing-with-pytest-pytest-mock-and-mypy.md:33`: `grep -nF -- 'A test is named as a claim:' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: A test is named as a claim: `test_book_best_books_only_the_winner` says what the engine does, so a failure reads as a broken sentence.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:33`: `grep -nF -- 'A check that was never seen to fail is a guess' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: A check that was never seen to fail is a guess, so each check is deleted in a scratch copy, and the experiments record which named test failed.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:221`: `grep -nF -- '`test_book_best_books_only_the_winner` also asserts the return value' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: `test_book_best_books_only_the_winner` also asserts the return value, `"AIRCO:CN-00000001"`, before it asserts on the calls.
- Plan lines (tree at 6c27a6f): 11:33, 11:221, 11:223; census lines: 11:33, 11:221.
- Witness tests, each defined once:
  - `test_book_best_books_only_the_winner` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:19`, 1 definition)
  - `test_book_best_books_the_winner_and_returns_its_reference` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py:130`, 1 definition)
- Code: `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py` lines 19 to 34 (16 lines, longest 98 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (13.5 pt).
  - Anchor (line 19, exact, 0 leading spaces): `def test_book_best_books_only_the_winner(`
  - Last line (34): `loser.book.assert_not_called()`
  - Contiguous run of the python fence at `11-testing-with-pytest-pytest-mock-and-mypy.md:91` to `11-testing-with-pytest-pytest-mock-and-mypy.md:108` (block lines 1 to 16 of 16); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: a test named as a claim; the winner's reference is asserted before the calls, because an assertion that a method was called does not say the customer got the right reference.
  - Number: with the engine's booking method changed to book every gateway (E11-1), two tests fail and 32 pass, and mypy still exits 0. The check is deleted in a scratch copy and the test must fail.
  - No timing; the winner's test uses an autospec, the second test a hand-written fake.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 5: What each double refuses (Proving it works)

- Claim: Each kind of double refuses something different: a fake refuses an unknown name and a wrong call, a plain mock refuses nothing, a spec refuses the name only, and an autospec refuses both. In this example the inline plain mock plays the part of the negative case.
- Chapter: 11, "Proving it works: pytest, pytest-mock, and mypy" (`_docs/11-testing-with-pytest-pytest-mock-and-mypy.md`).
- `11-testing-with-pytest-pytest-mock-and-mypy.md:63`: `grep -nF -- 'Each kind of double refuses something different.' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: Each kind of double refuses something different.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:72`: `grep -nF -- 'In this example the plain `Mock` row, built inline, plays the part of the negative fixture' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: In this example the plain `Mock` row, built inline, plays the part of the negative fixture for the engine's claim; it is not an underscore-prefixed object.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:89`: `grep -nF -- '`Mock(spec=CarrierGateway)` closes the first gap and not the second.' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: `Mock(spec=CarrierGateway)` closes the first gap and not the second.
- Plan lines (tree at 6c27a6f): 11:63, 11:65-70, 11:23; census lines: 11:63, 11:72, 11:89.
- Witness tests, each defined once:
  - `test_a_fake_rejects_unknown_names_and_wrong_signatures` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:69`, 1 definition)
  - `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:37`, 1 definition)
  - `test_spec_rejects_unknown_names_but_not_wrong_signatures` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:49`, 1 definition)
  - `test_autospec_rejects_names_and_signatures` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:59`, 1 definition)
- Table: see section "Table cells" (slide 5).
- Notes cover:
  - What the slide shows: four doubles handed a name that does not exist and a call with the wrong shape.
  - The plain mock built inline passes an assertion on a misspelt method and so plays the negative case; autospec refuses both. Fowler's Mocks Aren't Stubs is credited for the vocabulary of doubles.
- Credits: Mocks Aren't Stubs (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and table cells confirmed.

### Slide 6: Autospec copies signatures (Proving it works)

- Claim: Only create_autospec copies the signatures of its target, and mypy accepts every kind of mock where the carrier gateway (the one with quote and book) is expected, so a fake earns a static check and an autospec a runtime check.
- Chapter: 11, "Proving it works: pytest, pytest-mock, and mypy" (`_docs/11-testing-with-pytest-pytest-mock-and-mypy.md`).
- `11-testing-with-pytest-pytest-mock-and-mypy.md:89`: `grep -nF -- 'Only `create_autospec` copies the signatures' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: Only `create_autospec` copies the signatures, so the witness for the engine's claim uses it:
- `11-testing-with-pytest-pytest-mock-and-mypy.md:125`: `grep -nF -- 'mypy accepts every one of the mocks where a `CarrierGateway` is expected.' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: mypy accepts every one of the mocks where a `CarrierGateway` is expected.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:153`: `grep -nF -- 'The practical rule: a fake earns a static check and an autospec earns a runtime check, and a plain mock earns neither.' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: The practical rule: a fake earns a static check and an autospec earns a runtime check, and a plain mock earns neither.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:123`: `grep -nF -- '`side_effect` is how a double drives a branch the happy path never reaches.' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: `side_effect` is how a double drives a branch the happy path never reaches.
- Plan lines (tree at 6c27a6f): 11:89, 11:125, 11:153, 11:127, 11:123; census lines: 11:89, 11:123, 11:125, 11:153.
- Witness tests, each defined once:
  - `test_autospec_rejects_names_and_signatures` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:59`, 1 definition)
  - `test_mypy_accepts_every_mock_where_a_gateway_is_expected` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_static.py:56`, 1 definition)
  - `test_mypy_checks_a_hand_written_fake` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_static.py:119`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_side_effect_drives_the_timeout_branch` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:79`, 1 definition)
- Code: `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py` lines 59 to 66 (8 lines, longest 86 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 59, exact, 0 leading spaces): `def test_autospec_rejects_names_and_signatures(mocker: MockerFixture) -> None:`
  - Last line (66): `gateway.book()`
  - Contiguous run of the python fence at `11-testing-with-pytest-pytest-mock-and-mypy.md:112` to `11-testing-with-pytest-pytest-mock-and-mypy.md:121` (block lines 1 to 8 of 8); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the autospec test with both refusals; mypy accepts every kind of mock where the carrier gateway is expected, because typeshed declares the mock base as a subclass of Any (the comment is quoted and credited to typeshed).
  - A hand-written fake missing a member is a mypy error; the practical rule is the chapter's sentence.
  - side_effect drives the timeout branch that the happy path never reaches (notes witness). The unittest.mock Autospeccing section is credited.
- Credits: unittest.mock Autospeccing; typeshed unittest/mock.pyi (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 7: Clock and environment (Proving it works)

- Claim: The engine takes its clock as an argument, so a test has nothing to patch and nothing to wait for; ties break on the carrier code. The environment comes in as a mapping, and the one test that touches the real environment restores it inside monkeypatch.context().
- Chapter: 11, "Proving it works: pytest, pytest-mock, and mypy" (`_docs/11-testing-with-pytest-pytest-mock-and-mypy.md`).
- `11-testing-with-pytest-pytest-mock-and-mypy.md:157`: `grep -nF -- 'has nothing to patch and nothing to wait for' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: A test that passes `clock=lambda: fixed_now` and asserts `quote.valid_until == fixed_now + timedelta(minutes=45)` has nothing to patch and nothing to wait for.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:159`: `grep -nF -- 'The engine asks carriers in sorted code order' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: The engine asks carriers in sorted code order and picks the minimum by `(amount, carrier)`, so the winner never depends on how the mapping happens to be ordered.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:179`: `grep -nF -- 'The test captures the value before, whatever the shell left there' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: The test captures the value before, whatever the shell left there, and compares after the `with` block.
- `11-testing-with-pytest-pytest-mock-and-mypy.md:345`: `grep -nF -- 'In this run the code after `yield` ran, and printed its line, for the failed test.' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md`
  - Sentence: In this run the code after `yield` ran, and printed its line, for the failed test.
- Plan lines (tree at 6c27a6f): 11:157, 11:159; census lines: 11:157, 11:159, 11:179, 11:345.
- Witness tests, each defined once:
  - `test_quote_validity_comes_from_the_injected_clock` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py:68`, 1 definition)
  - `test_validity_reads_the_environment_and_the_context_restores_it` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_environment.py:8`, 1 definition)
  - `test_carriers_are_asked_in_code_order` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py:100`, 1 definition)
  - `test_a_tie_is_broken_by_the_carrier_code_in_the_quote` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py:53`, 1 definition)
- Code: `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_environment.py` lines 8 to 20 (13 lines, longest 68 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 8, exact, 0 leading spaces): `def test_validity_reads_the_environment_and_the_context_restores_it(`
  - Last line (20): `assert os.environ.get(VALIDITY_VARIABLE) == before`
  - Contiguous run of the python fence at `11-testing-with-pytest-pytest-mock-and-mypy.md:163` to `11-testing-with-pytest-pytest-mock-and-mypy.md:177` (block lines 1 to 13 of 13); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the one test that touches the real environment, inside monkeypatch.context(), capturing the value first and comparing after.
  - The clock is a constructor argument, ties break on the carrier code, and the environment is a mapping with the real environment as the default; the clock, order and tie tests are the claim's witnesses.
  - Number: in one experiment a failing test that used the yield fixture printed the fixture's teardown line (E11-3). The claim goes no wider than that experiment. pytest's fixtures and monkeypatch how-tos are credited.
- Credits: pytest fixtures how-to; pytest monkeypatch how-to (section "Credits per slide").
- Disposition: **narrowed**. the plan's range tests/test_engine.py:68-80 (the clock test) is not a run of any chapter fence, so the slide shows the environment test (tests/test_environment.py:8-20, a whole fence) and is retitled from 'An injected clock' to 'Clock and environment'; the clock test stays a witness of the claim.

### Slide 8: divider (Fixtures and test doubles)

- Claim: -
- Notes cover: configuration that refuses silence; doubles by what they record; two vocabularies.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 9: Settings that refuse silence (Fixtures and test doubles)

- Claim: Under pytest's defaults an unregistered marker, an xfail test that passes and a deprecation all leave a green run. Four settings refuse what the defaults let through, and one configuration file applies to a run.
- Chapter: 42, "pytest reference" (`_docs/42-appendix-b-pytest.md`).
- `42-appendix-b-pytest.md:23`: `grep -nF -- 'an unregistered marker, an `xfail` test that passes and a deprecation in the end-of-run summary all leave a green run' _docs/42-appendix-b-pytest.md`
  - Sentence: Under pytest's defaults, an unregistered marker, an `xfail` test that passes and a deprecation in the end-of-run summary all leave a green run.
- `42-appendix-b-pytest.md:42`: `grep -nF -- 'Four of its settings refuse what pytest'"'"'s defaults let through.' _docs/42-appendix-b-pytest.md`
  - Sentence: Four of its settings refuse what pytest's defaults let through.
- `42-appendix-b-pytest.md:59`: `grep -nF -- 'One configuration file applies to a run.' _docs/42-appendix-b-pytest.md`
  - Sentence: One configuration file applies to a run.
- Plan lines (tree at 6c27a6f): 42:23, 42:42, 42:59; census lines: 42:23, 42:42, 42:59.
- Witness tests, each defined once:
  - `test_an_unregistered_marker_fails_collection_under_strict_markers` (`examples/42-appendix-b-pytest/tests/test_config.py:61`, 1 definition)
  - `test_a_passing_xfail_fails_the_run_under_strict_xfail` (`examples/42-appendix-b-pytest/tests/test_config.py:77`, 1 definition)
  - `test_an_unknown_option_fails_under_strict_config` (`examples/42-appendix-b-pytest/tests/test_config.py:92`, 1 definition)
  - `test_filterwarnings_error_turns_a_warning_into_a_failure` (`examples/42-appendix-b-pytest/tests/test_config.py:105`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_the_first_config_file_wins_and_is_not_merged` (`examples/42-appendix-b-pytest/tests/test_config.py:157`, 1 definition)
  - `test_a_member_table_replaces_the_root_filter_and_names_its_own_file` (`examples/42-appendix-b-pytest/tests/test_config.py:171`, 1 definition)
- Notes cover:
  - What the slide shows: four settings (strict markers, strict config, strict xfail, filterwarnings error), each tested by an inner session with and without it, asserting exact outcome counts.
  - One configuration file applies: a subdirectory's own table replaces the root's and the options are not merged; a test builds that layout and the header names the subdirectory's file.
  - pytest's reference and configuration pages and its capture-warnings how-to are credited; Okken's book is the book-length treatment.
- Credits: pytest reference page; pytest configuration page; pytest capture-warnings how-to; Python Testing with pytest (section "Credits per slide").
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 10: Same-name test files (Fixtures and test doubles)

- Claim: Under the default import mode two test files with one basename collide: pytest reports an import file mismatch and the run has one collection error. Under importlib each file gets a unique module name, at the cost that test modules cannot import conftest by name.
- Chapter: 42, "pytest reference" (`_docs/42-appendix-b-pytest.md`).
- `42-appendix-b-pytest.md:102`: `grep -nF -- 'Under `prepend` pytest reports an import file mismatch and the run has one collection error.' _docs/42-appendix-b-pytest.md`
  - Sentence: Under `prepend` pytest reports an import file mismatch and the run has one collection error.
- `42-appendix-b-pytest.md:104`: `grep -nF -- 'The cost of `importlib` is on the same page' _docs/42-appendix-b-pytest.md`
  - Sentence: The cost of `importlib` is on the same page: "Test modules can’t import each other." `test_importlib_mode_cannot_import_conftest_by_name` writes a `tests/conftest.py` with a constant and a test that runs `from conftest import LIMIT`.
- `42-appendix-b-pytest.md:106`: `grep -nF -- 'Shared values reach tests through fixtures, which pytest discovers without an import' _docs/42-appendix-b-pytest.md`
  - Sentence: Shared values reach tests through fixtures, which pytest discovers without an import, and a test module imports a type from `conftest.py` under `TYPE_CHECKING`, so nothing is imported at run time.
- Plan lines (tree at 6c27a6f): 42:102, 42:104, 42:106; census lines: 42:102, 42:104, 42:106.
- Witness tests, each defined once:
  - `test_same_basename_test_files_collide_under_prepend` (`examples/42-appendix-b-pytest/tests/test_import_modes.py:22`, 1 definition)
  - `test_importlib_mode_gives_each_test_file_a_unique_name` (`examples/42-appendix-b-pytest/tests/test_import_modes.py:31`, 1 definition)
  - `test_importlib_mode_cannot_import_conftest_by_name` (`examples/42-appendix-b-pytest/tests/test_import_modes.py:39`, 1 definition)
- Code: `examples/42-appendix-b-pytest/tests/test_import_modes.py` lines 15 to 28 (14 lines, longest 91 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 15, exact, 0 leading spaces): `def _two_files_with_one_basename(pytester: pytest.Pytester) -> None:`
  - Last line (28): `result.stdout.fnmatch_lines(["*import file mismatch*"])`
  - Contiguous run of the python fence at `42-appendix-b-pytest.md:85` to `42-appendix-b-pytest.md:100` (block lines 1 to 14 of 14); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the helper that writes two test files with one basename into an inner session; under prepend pytest reports an import file mismatch and one collection error, under importlib each file gets a unique name.
  - The cost: under importlib a test cannot import conftest by name, so shared values go through fixtures and types under TYPE_CHECKING. The import mechanisms page is credited.
- Credits: pytest import mechanisms page (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 11: Calls recorded in order (Fixtures and test doubles)

- Claim: assert_has_calls is stricter than its name suggests and looser than comparing mock_calls: it checks a contiguous, ordered run, and any_order=True drops both conditions.
- Chapter: 43, "Mocking reference: unittest.mock and pytest-mock" (`_docs/43-appendix-c-mocking.md`).
- `43-appendix-c-mocking.md:129`: `grep -nF -- '`assert_has_calls` is stricter than its name suggests, and looser than `mock_calls ==`.' _docs/43-appendix-c-mocking.md`
  - Sentence: `assert_has_calls` is stricter than its name suggests, and looser than `mock_calls ==`.
- `43-appendix-c-mocking.md:23`: `grep -nF -- 'A mock therefore bypasses the static check' _docs/43-appendix-c-mocking.md`
  - Sentence: A mock therefore bypasses the static check, and every check it makes is one you configured.
- `43-appendix-c-mocking.md:230`: `grep -nF -- 'A stub'"'"'s count survives, so a test that reuses one after `resetall()` has to reset it' _docs/43-appendix-c-mocking.md`
  - Sentence: The page adds "By default only the recorded calls are reset." A stub's count survives, so a test that reuses one after `resetall()` has to reset it with `stub.reset_mock()`.
- Plan lines (tree at 6c27a6f): 43:129, 43:103, 43:60, 43:64, 43:23, 43:230; census lines: 43:23, 43:129, 43:230.
- Witness tests, each defined once:
  - `test_assert_has_calls_checks_a_contiguous_ordered_run` (`examples/43-appendix-c-mocking/tests/test_calls.py:81`, 1 definition)
  - `test_mock_calls_records_calls_in_order_with_call_objects` (`examples/43-appendix-c-mocking/tests/test_calls.py:44`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_spec_set_refuses_setting_a_name_the_spec_lacks` (`examples/43-appendix-c-mocking/tests/test_doubles.py:13`, 1 definition)
  - `test_an_assertion_typo_raises_instead_of_passing` (`examples/43-appendix-c-mocking/tests/test_doubles.py:37`, 1 definition)
  - `test_resetall_resets_patches_spies_and_autospecs_but_not_stubs` (`examples/43-appendix-c-mocking/tests/test_spies.py:56`, 1 definition)
- Code: `examples/43-appendix-c-mocking/tests/test_calls.py` lines 81 to 91 (11 lines, longest 89 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 81, exact, 0 leading spaces): `def test_assert_has_calls_checks_a_contiguous_ordered_run(mocker: MockerFixture) -> None:`
  - Last line (91): `gateway.book.assert_has_calls([mock.call("CN-3"), mock.call("CN-1")], any_order=True)`
  - Contiguous run of the python fence at `43-appendix-c-mocking.md:131` to `43-appendix-c-mocking.md:143` (block lines 1 to 11 of 11); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: assert_has_calls checks a contiguous, ordered run; a gap and a reversal both raise; any_order=True accepts both and is the weaker check; to say the calls were exactly these, compare mock_calls with a list.
  - Also: spec_set refuses setting a name the spec lacks, an assertion typo raises instead of passing, a mock bypasses the static check, and a stub keeps its call count after resetall. The unittest.mock and pytest-mock usage pages are credited.
- Credits: unittest.mock page; pytest-mock usage page (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 12: Two vocabularies (Fixtures and test doubles)

- Claim: Two names in the mock libraries collide with Meszaros's: pytest-mock's stub is a recorder for callbacks, where Meszaros's Test Stub feeds indirect inputs, and mocker.spy records a call the test made, where a Test Spy records an indirect output. When a test says stub or spy, ask which vocabulary it is in.
- Chapter: 44, "xUnit test patterns (Meszaros)" (`_docs/44-appendix-d-xunit-test-patterns.md`).
- `44-appendix-d-xunit-test-patterns.md:149`: `grep -nF -- 'When a test says "stub" or "spy", ask which vocabulary it is in.' _docs/44-appendix-d-xunit-test-patterns.md`
  - Sentence: When a test says "stub" or "spy", ask which vocabulary it is in.
- `44-appendix-d-xunit-test-patterns.md:145`: `grep -nF -- 'The stub is a mock object that accepts any arguments and is useful to test callbacks.' _docs/44-appendix-d-xunit-test-patterns.md`
  - Sentence: Two names in the mock libraries collide with Meszaros's. pytest-mock's [usage page](https://pytest-mock.readthedocs.io/en/stable/usage.html) says "The stub is a mock object that accepts any arguments and is useful to test callbacks." That is a callback recorder.
- `44-appendix-d-xunit-test-patterns.md:145`: `grep -nF -- 'Meszaros'"'"'s Test Stub is a double that feeds indirect inputs to the code under test.' _docs/44-appendix-d-xunit-test-patterns.md`
  - Sentence: Meszaros's Test Stub is a double that feeds indirect inputs to the code under test.
- `44-appendix-d-xunit-test-patterns.md:147`: `grep -nF -- 'It records a call the test made, where a Test Spy records an indirect output of a system under test' _docs/44-appendix-d-xunit-test-patterns.md`
  - Sentence: It records a call the test made, where a Test Spy records an indirect output of a system under test, so it isn't a Test Spy in the page's sense.
- `44-appendix-d-xunit-test-patterns.md:110`: `grep -nF -- 'Dummy Object is qualified.' _docs/44-appendix-d-xunit-test-patterns.md`
  - Sentence: Dummy Object is qualified.
- Plan lines (tree at 6c27a6f): 44:147, 44:143-145, 44:162; census lines: 44:110, 44:145, 44:147, 44:149.
- Witness tests, each defined once:
  - `test_stub_records_a_callback` (`examples/43-appendix-c-mocking/tests/test_spies.py:48`, 1 definition)
  - `test_spy_keeps_the_real_behaviour_and_records_returns` (`examples/43-appendix-c-mocking/tests/test_spies.py:23`, 1 definition)
  - `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` (`examples/43-appendix-c-mocking/tests/test_booking.py:19`, 1 definition)
- Table: see section "Table cells" (slide 12).
- Notes cover:
  - What the slide shows: stub and spy in the two vocabularies; when a test says stub or spy, ask which one.
  - Dummy Object is qualified: the engine calls the stub, so Dummy holds only in the sense that the test passes it to fill the parameter and never reads it.
  - State against behaviour verification. Meszaros's book and xunitpatterns.com, the pytest-mock usage page and Fowler are credited.
- Credits: xunitpatterns.com; pytest-mock usage page; xUnit Test Patterns; Mocks Aren't Stubs (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and table cells confirmed.

### Slide 13: divider (Seams in Python)

- Claim: -
- Notes cover: Python looks a name up when the call runs, so every global the code reads is a seam.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 14: An engine kept as found (Seams in Python)

- Claim: Python looks a global name up when the call runs, so every global the inherited engine reads is a seam. The engine holds its own binding of the FASTLINE function, and a test of it reaches the real carrier, whose stand-in raises what a timeout would.
- Chapter: 33, "Seams in Python: monkeypatch, injection, and duck typing" (`_docs/33-seams-in-python.md`).
- `33-seams-in-python.md:22`: `grep -nF -- 'Test code can still change what the calls do, because Python looks a global name up when the call runs.' _docs/33-seams-in-python.md`
  - Sentence: Test code can still change what the calls do, because Python looks a global name up when the call runs.
- `33-seams-in-python.md:63`: `grep -nF -- '`request_quote` is a function imported by name, so `seams.legacy` holds its own binding of it.' _docs/33-seams-in-python.md`
  - Sentence: `request_quote` is a function imported by name, so `seams.legacy` holds its own binding of it.
- `33-seams-in-python.md:24`: `grep -nF -- 'The stand-in SDKs in the example do no I/O' _docs/33-seams-in-python.md`
  - Sentence: The stand-in SDKs in the example do no I/O: where a real one would open a connection, each raises the error a timeout would.
- Plan lines (tree at 6c27a6f): 33:22, 33:63, 33:32; census lines: 33:22, 33:24, 33:63.
- Witness tests, each defined once:
  - `test_the_legacy_engine_calls_the_real_carrier` (`examples/33-seams-in-python/tests/test_patching.py:24`, 1 definition)
- Code: `examples/33-seams-in-python/src/seams/legacy.py` lines 17 to 31 (15 lines, longest 91 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 17, exact, 0 leading spaces): `class RateEngine:`
  - Last line (31): `return RateQuote(consignment.id, code, Money(total))`
  - Contiguous run of the python fence at `33-seams-in-python.md:36` to `33-seams-in-python.md:61` (block lines 10 to 24 of 24); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the inherited engine as found, before any parameter; it holds its own binding of the FASTLINE function and reaches the module for AIRCO.
  - The stand-in SDKs do no I/O and raise what a timeout would. Feathers's seam and enabling point are credited in Working Effectively with Legacy Code, under 'The Seam Model'.
- Credits: Working Effectively with Legacy Code (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 15: Patch where it's looked up (Seams in Python)

- Claim: A patch replaces a name where the engine looks it up. The inherited engine holds its own name for the FASTLINE call, so patching the carrier's module misses it, and the import form decides the target.
- Chapter: 33, "Seams in Python: monkeypatch, injection, and duck typing" (`_docs/33-seams-in-python.md`).
- `33-seams-in-python.md:69`: `grep -nF -- 'The basic principle is that you patch where an object is looked up' _docs/33-seams-in-python.md`
  - Sentence: The `unittest.mock` documentation states the rule: ["patch() works by (temporarily) changing the object that a name points to with another one."](https://docs.python.org/3/library/unittest.mock.html) A few sentences later it gives the principle: "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined."
- `33-seams-in-python.md:88`: `grep -nF -- 'Patching `seams.fastline.request_quote` instead rebinds the name in the module that defines it.' _docs/33-seams-in-python.md`
  - Sentence: Patching `seams.fastline.request_quote` instead rebinds the name in the module that defines it.
- `33-seams-in-python.md:92`: `grep -nF -- 'The import form decides the target.' _docs/33-seams-in-python.md`
  - Sentence: The import form decides the target.
- `33-seams-in-python.md:224`: `grep -nF -- '"Mock the carrier in this test" leaves the target open' _docs/33-seams-in-python.md`
  - Sentence: **Specifying where to patch.** "Mock the carrier in this test" leaves the target open, and a patch on the module that defines a `from`-imported function changes nothing.
- Plan lines (tree at 6c27a6f): 33:69, 33:88, 33:92, 33:224; census lines: 33:69, 33:88, 33:92, 33:224.
- Witness tests, each defined once:
  - `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` (`examples/33-seams-in-python/tests/test_patching.py:29`, 1 definition)
  - `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier` (`examples/33-seams-in-python/tests/test_patching.py:43`, 1 definition)
  - `test_a_module_attribute_is_patched_on_the_module_it_belongs_to` (`examples/33-seams-in-python/tests/test_patching.py:56`, 1 definition)
  - `test_unittest_mock_patch_follows_the_same_lookup_rule` (`examples/33-seams-in-python/tests/test_patching.py:78`, 1 definition)
- Figure: figure 33, `presentation/png/33-seams-in-python.png` (see Figure census).
- Notes cover:
  - What the slide shows: the figure's boxes and arrows from the test, through the namespace the engine reads, to the engine; the two unconnected boxes are notes.
  - Number: with the patch aimed at the defining module (E33-a), one test fails and 20 pass, and mypy exits 0, because the patch is valid and lands where the engine does not look.
  - A request to 'mock the carrier in this test' leaves the target open. unittest.mock's Where to patch is credited.
- Credits: unittest.mock Where to patch (section "Credits per slide").
- Disposition: **kept**. claim and witnesses confirmed; the figure passes the census.

### Slide 16: A default captured early (Seams in Python)

- Claim: A default argument is a value captured at definition, so a patch to the global it was copied from cannot change it. A reload re-runs the module body into the same dictionary and overwrites a live patch.
- Chapter: 33, "Seams in Python: monkeypatch, injection, and duck typing" (`_docs/33-seams-in-python.md`).
- `33-seams-in-python.md:157`: `grep -nF -- 'A default argument is a value captured at definition, so a patch to the global it was copied from can'"'"'t change it.' _docs/33-seams-in-python.md`
  - Sentence: A default argument is a value captured at definition, so a patch to the global it was copied from can't change it.
- `33-seams-in-python.md:159`: `grep -nF -- 'A reload re-runs the module body into that dictionary, which overwrites a live patch.' _docs/33-seams-in-python.md`
  - Sentence: The `importlib` documentation says "When a module is reloaded, its dictionary (containing the module’s global variables) is retained." A reload re-runs the module body into that dictionary, which overwrites a live patch.
- `33-seams-in-python.md:103`: `grep -nF -- 'Both refuse by default, and each has a switch that turns the refusal into a silent miss.' _docs/33-seams-in-python.md`
  - Sentence: Both refuse by default, and each has a switch that turns the refusal into a silent miss.
- Plan lines (tree at 6c27a6f): 33:157, 33:159, 33:103; census lines: 33:103, 33:157, 33:159.
- Witness tests, each defined once:
  - `test_patching_a_module_constant_misses_a_default_captured_at_definition` (`examples/33-seams-in-python/tests/test_seams.py:64`, 1 definition)
  - `test_reload_discards_a_patch_and_keeps_old_bindings` (`examples/33-seams-in-python/tests/test_seams.py:81`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads` (`examples/33-seams-in-python/tests/test_patching.py:105`, 1 definition)
  - `test_patch_refuses_a_name_the_module_does_not_have` (`examples/33-seams-in-python/tests/test_patching.py:119`, 1 definition)
- Code: `examples/33-seams-in-python/tests/test_seams.py` lines 64 to 78 (15 lines, longest 76 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 64, exact, 0 leading spaces): `def test_patching_a_module_constant_misses_a_default_captured_at_definition(`
  - Last line (78): `assert str(passed.total.amount) == "50.00"`
  - Contiguous run of the python fence at `33-seams-in-python.md:138` to `33-seams-in-python.md:154` (block lines 1 to 15 of 15); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: a patch of the constant misses the default captured at definition, so only margin= changes the quote; a reload overwrites a live patch and keeps old bindings.
  - Both monkeypatch and mock.patch refuse a missing name by default, and each has a switch (raising=False, create=True) that turns the refusal into a silent miss. importlib.reload is credited.
- Credits: importlib.reload (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 17: What mypy sees of a patch (Seams in Python)

- Claim: mypy exits 0 on a monkeypatched replacement of the wrong shape and on a misspelt target string; it checks a direct assignment and a fake passed to a Protocol parameter. A parameter is checked by mypy, and a fake of the wrong shape is rejected before the test runs.
- Chapter: 33, "Seams in Python: monkeypatch, injection, and duck typing" (`_docs/33-seams-in-python.md`).
- `33-seams-in-python.md:197`: `grep -nF -- 'mypy exits 0 with no errors.' _docs/33-seams-in-python.md`
  - Sentence: mypy exits 0 with no errors.
- `33-seams-in-python.md:199`: `grep -nF -- 'A direct assignment is checked.' _docs/33-seams-in-python.md`
  - Sentence: A direct assignment is checked.
- `33-seams-in-python.md:219`: `grep -nF -- 'A parameter is checked by mypy, and a fake of the wrong shape is rejected before the test runs.' _docs/33-seams-in-python.md`
  - Sentence: A parameter is checked by mypy, and a fake of the wrong shape is rejected before the test runs.
- `33-seams-in-python.md:214`: `grep -nF -- 'A patch is the way to get the first test around code that can'"'"'t change yet.' _docs/33-seams-in-python.md`
  - Sentence: A patch is the way to get the first test around code that can't change yet.
- Plan lines (tree at 6c27a6f): 33:197, 33:199, 33:219, 33:214, 33:221; census lines: 33:197, 33:199, 33:214, 33:219.
- Witness tests, each defined once:
  - `test_mypy_does_not_check_a_monkeypatched_replacement` (`examples/33-seams-in-python/tests/test_static.py:137`, 1 definition)
  - `test_mypy_checks_a_direct_assignment_to_a_module_name` (`examples/33-seams-in-python/tests/test_static.py:153`, 1 definition)
  - `test_mypy_accepts_a_misspelt_monkeypatch_target_string` (`examples/33-seams-in-python/tests/test_static.py:197`, 1 definition)
  - `test_mypy_checks_a_fake_passed_to_a_protocol_parameter` (`examples/33-seams-in-python/tests/test_static.py:189`, 1 definition)
- Notes cover:
  - What the slide shows: mypy exits 0 for a replacement of the wrong shape and for a misspelt target string; it checks a direct assignment and a fake passed to a Protocol parameter. The two quoted mypy lines are asserted in full by a test, so they may be quoted.
  - A patch is the way to get the first test in; a parameter replaces it.
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 18: divider (Breaking dependencies)

- Claim: -
- Notes cover: change the structure, keep the behaviour, and record the behaviour first.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 19: A characterisation table (Breaking dependencies)

- Claim: A characterisation test records what code does, so that a change can be told apart from a fix. The table pins behaviour a reviewer might call wrong, such as a weight that truncates to zero grams, and a table that cannot fail proves nothing.
- Chapter: 34, "Dependency-breaking techniques for modern Python" (`_docs/34-dependency-breaking-techniques.md`).
- `34-dependency-breaking-techniques.md:32`: `grep -nF -- 'A characterisation test records what code does, so that a change can be told apart from a fix.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: A characterisation test records what code does, so that a change can be told apart from a fix.
- `34-dependency-breaking-techniques.md:59`: `grep -nF -- 'The weight of 0.0006 kg converts to zero grams because `int` truncates' _docs/34-dependency-breaking-techniques.md`
  - Sentence: The weight of 0.0006 kg converts to zero grams because `int` truncates, so AIRCO is asked about a weightless parcel and the quote is a cent.
- `34-dependency-breaking-techniques.md:84`: `grep -nF -- 'A table that can'"'"'t fail proves nothing.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: A table that can't fail proves nothing.
- `34-dependency-breaking-techniques.md:231`: `grep -nF -- 'mypy exits 0: the change is type-correct, and the record of behaviour is what catches it.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: The timeout test for the `parameterised` form fails because the quote no longer raises, and the defaults test fails because its first assertion expects the FASTLINE timeout and gets AIRCO's. mypy exits 0: the change is type-correct, and the record of behaviour is what catches it.
- Plan lines (tree at 6c27a6f): 34:32, 34:59, 34:84, 34:231; census lines: 34:32, 34:59, 34:84, 34:231.
- Witness tests, each defined once:
  - `test_every_step_matches_the_characterisation_table` (`examples/34-dependency-breaking-techniques/tests/test_characterisation.py:92`, 1 definition)
  - `test_the_table_catches_a_step_that_changes_behaviour` (`examples/34-dependency-breaking-techniques/tests/test_characterisation.py:114`, 1 definition)
  - `test_every_step_lets_a_carrier_timeout_fail_the_quote` (`examples/34-dependency-breaking-techniques/tests/test_characterisation.py:98`, 1 definition)
- Code: `examples/34-dependency-breaking-techniques/tests/test_characterisation.py` lines 67 to 76 (10 lines, longest 61 characters, tabs 0, trailing whitespace 0, common indent 4); font by the builder from the longest line (by the builder).
  - Anchor (line 67, exact, 4 leading spaces): `Row(`
  - Last line (76): `),`
  - Contiguous run of the python fence at `34-dependency-breaking-techniques.md:35` to `34-dependency-breaking-techniques.md:56` (block lines 11 to 20 of 20); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the row that pins a weight truncating to zero grams; the table records what the engine returns whether or not anyone would choose it, and runs against five forms of the engine.
  - Number: with a timeout-swallowing 'improvement' added to the engine with carrier parameters (E34-1), two tests fail and 40 pass, the 25 table cases pass, and mypy exits 0, so the record of behaviour is what catches it.
  - Feathers is credited in Working Effectively with Legacy Code, under 'I Need To Make a Change but I Don't Know What Tests To Write'.
- Credits: Working Effectively with Legacy Code (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 20: Carriers as parameters (Breaking dependencies)

- Claim: An engine that takes its carriers as keyword parameters gives a test a seam without a patch, and mypy checks the fake. The price of real defaults is a test that forgets one fake and reaches the real carrier.
- Chapter: 34, "Dependency-breaking techniques for modern Python" (`_docs/34-dependency-breaking-techniques.md`).
- `34-dependency-breaking-techniques.md:88`: `grep -nF -- 'A constructor that takes the carriers as parameters gives the test a seam it can use without one' _docs/34-dependency-breaking-techniques.md`
  - Sentence: A constructor that takes the carriers as parameters gives the test a seam it can use without one, and existing callers don't have to change if each parameter defaults to the real call:
- `34-dependency-breaking-techniques.md:107`: `grep -nF -- 'mypy now checks the fake.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: mypy now checks the fake.
- `34-dependency-breaking-techniques.md:107`: `grep -nF -- 'The price of the defaults is the other direction' _docs/34-dependency-breaking-techniques.md`
  - Sentence: The price of the defaults is the other direction: a test that passes a FASTLINE fake and forgets AIRCO reaches the real SDK and fails with `AIRCO did not answer`.
- Plan lines (tree at 6c27a6f): 34:88, 34:107; census lines: 34:88, 34:107.
- Witness tests, each defined once:
  - `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults` (`examples/34-dependency-breaking-techniques/tests/test_steps.py:19`, 1 definition)
  - `test_mypy_checks_a_fake_passed_as_a_constructor_argument` (`examples/34-dependency-breaking-techniques/tests/test_static.py:75`, 1 definition)
- Code: `examples/34-dependency-breaking-techniques/src/dependency_breaking/parameterised.py` lines 27 to 36 (10 lines, longest 54 characters, tabs 0, trailing whitespace 0, common indent 4); font by the builder from the longest line (by the builder).
  - Anchor (line 27, exact, 4 leading spaces): `def __init__(`
  - Last line (36): `self._margin = margin`
  - Contiguous run of the python fence at `34-dependency-breaking-techniques.md:91` to `34-dependency-breaking-techniques.md:102` (block lines 1 to 10 of 10); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the engine with carrier parameters; AircoPrice is a callback Protocol because the AIRCO SDK takes keyword-only arguments, and mypy checks a fake passed as an argument.
  - The price of the defaults: a test that passes one fake and forgets the other reaches the real SDK and fails loudly here. The typing documentation is credited.
- Credits: typing: annotating callable objects (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 21: The engine as a function (Breaking dependencies)

- Claim: The quote that takes quoters has no defaults, so omitting them is a mypy error and a run-time TypeError. airco_quote keeps the gram truncation, because a step does not fix behaviour.
- Chapter: 34, "Dependency-breaking techniques for modern Python" (`_docs/34-dependency-breaking-techniques.md`).
- `34-dependency-breaking-techniques.md:153`: `grep -nF -- 'the function form drops them.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: The parameterised engine kept defaults so existing callers still work, and the cost was the forgotten fake; the function form drops them.
- `34-dependency-breaking-techniques.md:120`: `grep -nF -- 'The truncation stays, because a step doesn'"'"'t fix behaviour' _docs/34-dependency-breaking-techniques.md`
  - Sentence: The truncation stays, because a step doesn't fix behaviour, and the `grams-truncated` row still passes through `airco_quote`.
- `34-dependency-breaking-techniques.md:153`: `grep -nF -- '`quote_standard` is the one binding the root needs' _docs/34-dependency-breaking-techniques.md`
  - Sentence: `STANDARD_QUOTERS` names both carriers and refuses assignment (`test_standard_quoters_name_both_carriers`), and `quote_standard` is the one binding the root needs: `test_quote_standard_binds_the_standard_quoters` checks it wraps `quote` with `STANDARD_QUOTERS`.
- Plan lines (tree at 6c27a6f): 34:153, 34:120; census lines: 34:120, 34:153.
- Witness tests, each defined once:
  - `test_the_function_form_needs_its_quoters` (`examples/34-dependency-breaking-techniques/tests/test_steps.py:43`, 1 definition)
  - `test_mypy_reports_a_missing_quoters_argument` (`examples/34-dependency-breaking-techniques/tests/test_static.py:83`, 1 definition)
  - `test_quote_standard_binds_the_standard_quoters` (`examples/34-dependency-breaking-techniques/tests/test_steps.py:54`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_airco_quote_converts_kilograms_and_cents` (`examples/34-dependency-breaking-techniques/tests/test_steps.py:32`, 1 definition)
- Code: `examples/34-dependency-breaking-techniques/src/dependency_breaking/rating.py` lines 21 to 34 (14 lines, longest 97 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (14 pt).
  - Anchor (line 21, exact, 0 leading spaces): `def quote(`
  - Last line (34): `return RateQuote(consignment.id, code, Money(total))`
  - Contiguous run of the python fence at `34-dependency-breaking-techniques.md:127` to `34-dependency-breaking-techniques.md:150` (block lines 6 to 19 of 22); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the quote that takes quoters, with no defaults, so omitting them is a mypy error and a run-time TypeError; quote_standard is the one binding the root needs.
  - airco_quote keeps the gram truncation, because a step does not fix behaviour. functools.partial is credited.
- Credits: functools.partial (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 22: A misspelt override (Breaking dependencies)

- Claim: In subclass and override the seam is a method name, and without @override nothing checks the name before the quote runs; @override from typing closes the gap.
- Chapter: 34, "Dependency-breaking techniques for modern Python" (`_docs/34-dependency-breaking-techniques.md`).
- `34-dependency-breaking-techniques.md:183`: `grep -nF -- 'The seam is a method name, and without `@override` nothing checks the name before the quote runs.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: The seam is a method name, and without `@override` nothing checks the name before the quote runs.
- `34-dependency-breaking-techniques.md:183`: `grep -nF -- '`@override` from `typing` closes the gap.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: `@override` from `typing` closes the gap.
- `34-dependency-breaking-techniques.md:187`: `grep -nF -- 'Each move above has a Python form.' _docs/34-dependency-breaking-techniques.md`
  - Sentence: Each move above has a Python form.
- Plan lines (tree at 6c27a6f): 34:183, 34:185-196; census lines: 34:183, 34:187.
- Witness tests, each defined once:
  - `test_a_misspelt_override_falls_through_to_the_real_carrier` (`examples/34-dependency-breaking-techniques/tests/test_steps.py:61`, 1 definition)
  - `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator` (`examples/34-dependency-breaking-techniques/tests/test_static.py:91`, 1 definition)
- Notes cover:
  - What the slide shows: the seam is a method name, and a misspelt override reaches the real SDK unless the method carries @override.
  - Number: with the override renamed (E34-2), five tests fail and 37 pass, and mypy exits 1 with one [misc] error. Each dependency-breaking move has a Python form, and subclass-and-override is the one comparison form. Feathers is credited under 'Dependency Breaking Techniques'.
- Credits: Working Effectively with Legacy Code (section "Credits per slide").
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 23: divider (Refactor or rewrite)

- Claim: -
- Notes cover: tests that record intent, golden values that record behaviour, and a rewrite held to parity.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 24: Intent rows and golden quotes (Refactor or rewrite)

- Claim: Five rows written from the requirement pass a refactor that still changes 18 of 120 recorded quotes. A golden value answers a different question: not is this right but did this change.
- Chapter: 35, "Fowler vs Feathers, contrasted and combined" (`_docs/35-fowler-vs-feathers.md`).
- `35-fowler-vs-feathers.md:24`: `grep -nF -- 'One way of making carrier prices `Money` passes all five and still changes 18 of 120 recorded quotes' _docs/35-fowler-vs-feathers.md`
  - Sentence: One way of making carrier prices `Money` passes all five and still changes 18 of 120 recorded quotes (`test_the_intent_rows_pass_every_engine_and_both_rounding_refactors` and `test_the_golden_quotes_catch_a_refactor_that_changes_rounding`).
- `35-fowler-vs-feathers.md:71`: `grep -nF -- 'not "is this right" but "did this change"' _docs/35-fowler-vs-feathers.md`
  - Sentence: It answers a different question from the intent rows: not "is this right" but "did this change".
- `35-fowler-vs-feathers.md:67`: `grep -nF -- 'The rows pass the refactors that move totals because the carrier prices in them are already whole cents' _docs/35-fowler-vs-feathers.md`
  - Sentence: The rows pass the refactors that move totals because the carrier prices in them are already whole cents and no margined price sits on a half cent, so the two roundings agree.
- Plan lines (tree at 6c27a6f): 35:24, 35:71, 35:67, 35:148, 35:150; census lines: 35:24, 35:67, 35:71.
- Witness tests, each defined once:
  - `test_the_intent_rows_pass_every_engine_and_both_rounding_refactors` (`examples/35-fowler-vs-feathers/tests/test_intent.py:58`, 1 definition)
  - `test_the_golden_quotes_catch_a_refactor_that_changes_rounding` (`examples/35-fowler-vs-feathers/tests/test_golden.py:122`, 1 definition)
  - `test_the_golden_file_records_the_legacy_engine` (`examples/35-fowler-vs-feathers/tests/test_golden.py:91`, 1 definition)
- Notes cover:
  - What the slide shows: five rows written from the requirement pass a refactor that changes 18 of 120 recorded quotes, because the carrier prices in them are whole cents.
  - Number: with each carrier price rounded half up before Money (E35-1), two golden tests fail and 28 pass, the intent cases pass, and mypy exits 0.
  - Fowler's Definition Of Refactoring, Self Testing Code and refactoring.com, and Feathers's 'Changing Software', are credited. Characterise, then refactor in named steps.
- Credits: Definition Of Refactoring; Self Testing Code; refactoring.com; Refactoring; Working Effectively with Legacy Code (section "Credits per slide").
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 25: A golden comparison (Refactor or rewrite)

- Claim: A golden value pins whatever the code did, including behaviour you would call wrong. The comparison returns a list of lines, so a failure reads the same each run, and round(x, 2) on a Decimal rounds half to even in the default context.
- Chapter: 35, "Fowler vs Feathers, contrasted and combined" (`_docs/35-fowler-vs-feathers.md`).
- `35-fowler-vs-feathers.md:106`: `grep -nF -- 'A golden value pins whatever the code did, including behaviour you would call wrong.' _docs/35-fowler-vs-feathers.md`
  - Sentence: A golden value pins whatever the code did, including behaviour you would call wrong.
- `35-fowler-vs-feathers.md:144`: `grep -nF -- 'The default context rounds half to even' _docs/35-fowler-vs-feathers.md`
  - Sentence: The default context rounds half to even, so a total of 32.505 becomes 32.50 where the engine's rule gives 32.51 (`test_round_with_two_digits_rounds_half_to_even_in_the_default_context`).
- `35-fowler-vs-feathers.md:142`: `grep -nF -- 'The first reads `EU-11: golden FASTLINE 14.84, now FASTLINE 14.85`.' _docs/35-fowler-vs-feathers.md`
  - Sentence: The first reads `EU-11: golden FASTLINE 14.84, now FASTLINE 14.85`.
- Plan lines (tree at 6c27a6f): 35:106, 35:144; census lines: 35:106, 35:142, 35:144.
- Witness tests, each defined once:
  - `test_the_refactored_engine_matches_the_golden_quotes` (`examples/35-fowler-vs-feathers/tests/test_golden.py:103`, 1 definition)
  - `test_round_with_two_digits_rounds_half_to_even_in_the_default_context` (`examples/35-fowler-vs-feathers/tests/test_golden.py:137`, 1 definition)
  - `test_the_golden_quotes_catch_a_refactor_that_changes_rounding` (`examples/35-fowler-vs-feathers/tests/test_golden.py:122`, 1 definition)
- Code: `examples/35-fowler-vs-feathers/tests/test_golden.py` lines 66 to 79 (14 lines, longest 89 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 66, exact, 0 leading spaces): `def _mismatches(observed: list[tuple[str, str]], golden: Mapping[str, str]) -> list[str]:`
  - Last line (79): `return lines + missing`
  - Contiguous run of the python fence at `35-fowler-vs-feathers.md:85` to `35-fowler-vs-feathers.md:100` (block lines 1 to 14 of 14); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the comparison returns a list of lines in grid order, so a failure reads the same each run and the first changed row sits at the top; regenerate the file in its own commit.
  - Number: with round(x, 2) in place of the half-up quantise (E35-2), three golden tests fail and 27 pass, the intent cases pass, and mypy exits 0; the first mismatch line is the full text the test asserts. The decimal documentation is credited for half-even rounding.
- Credits: decimal documentation (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 26: The rewrite's quote (Refactor or rewrite)

- Claim: The quote that takes a tariff finds the band by bisection. A first draft that moves each band limit from one band to the other quotes a 5 kg consignment from the next band's price, and both engines put a weight equal to a limit in the lower band.
- Chapter: 36, "Refactor or rewrite" (`_docs/36-refactor-or-rewrite.md`).
- `36-refactor-or-rewrite.md:24`: `grep -nF -- 'A first draft of that rewrite can pass its own tests and still quote a 5 kg consignment from the next band'"'"'s price' _docs/36-refactor-or-rewrite.md`
  - Sentence: A first draft of that rewrite can pass its own tests and still quote a 5 kg consignment from the next band's price, because the difference between `bisect_left` and `bisect_right` moves each band limit from one band to the other (`test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries`).
- `36-refactor-or-rewrite.md:83`: `grep -nF -- 'Both engines put a weight equal to a limit in the lower band' _docs/36-refactor-or-rewrite.md`
  - Sentence: Both engines put a weight equal to a limit in the lower band: 5 kg quotes 13.20 and 5.001 kg quotes 27.50 in each (`test_band_limits_include_the_boundary_weight`).
- `36-refactor-or-rewrite.md:24`: `grep -nF -- 'Replacements seem easy to specify, but often it'"'"'s hard to figure out the details of existing behavior.' _docs/36-refactor-or-rewrite.md`
  - Sentence: Martin Fowler's [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) page names the trap: "Replacements seem easy to specify, but often it's hard to figure out the details of existing behavior." The details here are whether a limit belongs to the band below it, and what happens to a zone nobody listed.
- Plan lines (tree at 6c27a6f): 36:24, 36:83; census lines: 36:24, 36:83.
- Witness tests, each defined once:
  - `test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries` (`examples/36-refactor-or-rewrite/tests/test_parity.py:46`, 1 definition)
  - `test_band_limits_include_the_boundary_weight` (`examples/36-refactor-or-rewrite/tests/test_parity.py:74`, 1 definition)
- Code: `examples/36-refactor-or-rewrite/src/refactor_or_rewrite/rating.py` lines 30 to 42 (13 lines, longest 90 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 30, exact, 0 leading spaces): `def quote(consignment: Consignment, /, *, tariff: Tariff = STANDARD_TARIFF) -> RateQuote:`
  - Last line (42): `return RateQuote(consignment.id, Money(total))`
  - Contiguous run of the python fence at `36-refactor-or-rewrite.md:67` to `36-refactor-or-rewrite.md:81` (block lines 1 to 13 of 13); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the quote that takes a tariff, finding the band by bisect_left so a weight on a limit stays in its band.
  - Number: with bisect_right (E36-1), four tests fail and 15 pass, and mypy exits 0. Fowler's Strangler Fig quote and the bisect documentation are credited.
- Credits: Strangler Fig; bisect (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 27: Parity and accepted differences (Refactor or rewrite)

- Claim: The rewrite differs from the legacy engine only where the accepted list says; the list records a decision, so a reviewer who sees it grow can ask who made that decision. The legacy engine prices an unknown zone as EU, and the rewrite refuses it.
- Chapter: 36, "Refactor or rewrite" (`_docs/36-refactor-or-rewrite.md`).
- `36-refactor-or-rewrite.md:100`: `grep -nF -- 'The list records a decision, so a reviewer who sees it grow can ask who made that decision.' _docs/36-refactor-or-rewrite.md`
  - Sentence: The list records a decision, so a reviewer who sees it grow can ask who made that decision.
- `36-refactor-or-rewrite.md:36`: `grep -nF -- '**Which behaviour should change.**' _docs/36-refactor-or-rewrite.md`
  - Sentence: **Which behaviour should change.** A legacy engine holds behaviour somebody wanted and behaviour nobody chose.
- `36-refactor-or-rewrite.md:83`: `grep -nF -- 'The rewrite refuses AFRICA with a `RatingError` that names the zone' _docs/36-refactor-or-rewrite.md`
  - Sentence: The rewrite refuses AFRICA with a `RatingError` that names the zone (`test_the_rewrite_refuses_an_unknown_zone`).
- Plan lines (tree at 6c27a6f): 36:100, 36:36, 36:98; census lines: 36:36, 36:83, 36:100.
- Witness tests, each defined once:
  - `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted` (`examples/36-refactor-or-rewrite/tests/test_parity.py:42`, 1 definition)
  - `test_the_legacy_engine_prices_an_unknown_zone_as_eu` (`examples/36-refactor-or-rewrite/tests/test_parity.py:60`, 1 definition)
  - `test_the_rewrite_refuses_an_unknown_zone` (`examples/36-refactor-or-rewrite/tests/test_parity.py:66`, 1 definition)
- Notes cover:
  - What the slide shows: the accepted list records a decision, and the parity test fails on a new difference and on a stale entry; the legacy engine prices an unknown zone as EU and the rewrite refuses it.
  - Number: with an empty accepted list (E36-2), one test fails and 18 pass, and mypy exits 0. The mismatches are parity row ids. Feature Parity is credited.
- Credits: Feature Parity (section "Credits per slide").
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 28: A router with a shadow (Refactor or rewrite)

- Claim: A router serves migrated zones from the rewrite and the rest from the legacy engine; with every zone migrated the legacy engine is never called, so router and legacy module can be deleted together. In shadow mode a difference becomes a Mismatch holding both amounts and the caller still gets the legacy quote.
- Chapter: 36, "Refactor or rewrite" (`_docs/36-refactor-or-rewrite.md`).
- `36-refactor-or-rewrite.md:135`: `grep -nF -- 'With EU and ASIA both in `migrated`, a legacy quoter that raises isn'"'"'t reached and both zones still quote' _docs/36-refactor-or-rewrite.md`
  - Sentence: With EU and ASIA both in `migrated`, a legacy quoter that raises isn't reached and both zones still quote (`test_with_every_zone_migrated_the_legacy_engine_is_never_called`), so the router and `legacy.py` can be deleted together.
- `36-refactor-or-rewrite.md:137`: `grep -nF -- 'A difference becomes a `Mismatch` holding both amounts, and the caller still gets the legacy quote' _docs/36-refactor-or-rewrite.md`
  - Sentence: Martin Fowler's [Dark Launching](https://martinfowler.com/bliki/DarkLaunching.html) entry describes calling new behaviour without users seeing it, and names this use: "The old and new code can both be called and their results checked to see if there are changes with the new algorithm, but only one answer returned to the interface." A difference becomes a `Mismatch` holding both amounts, and the caller still gets the legacy quote (`test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote`).
- `36-refactor-or-rewrite.md:139`: `grep -nF -- 'mypy holds the rewrite to the legacy call shape.' _docs/36-refactor-or-rewrite.md`
  - Sentence: mypy holds the rewrite to the legacy call shape.
- Plan lines (tree at 6c27a6f): 36:135, 36:137, 36:149, 36:151, 36:139; census lines: 36:135, 36:137, 36:139.
- Witness tests, each defined once:
  - `test_the_router_serves_migrated_zones_from_the_rewrite` (`examples/36-refactor-or-rewrite/tests/test_strangler.py:16`, 1 definition)
  - `test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote` (`examples/36-refactor-or-rewrite/tests/test_strangler.py:32`, 1 definition)
  - `test_with_every_zone_migrated_the_legacy_engine_is_never_called` (`examples/36-refactor-or-rewrite/tests/test_strangler.py:65`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_mypy_requires_the_rewrite_to_take_a_consignment` (`examples/36-refactor-or-rewrite/tests/test_static.py:63`, 1 definition)
- Code: `examples/36-refactor-or-rewrite/src/refactor_or_rewrite/strangler.py` lines 35 to 46 (12 lines, longest 62 characters, tabs 0, trailing whitespace 0, common indent 4); font by the builder from the longest line (by the builder).
  - Anchor (line 35, exact, 4 leading spaces): `legacy: RateQuoter`
  - Last line (46): `return served`
  - Contiguous run of the python fence at `36-refactor-or-rewrite.md:117` to `36-refactor-or-rewrite.md:130` (block lines 1 to 12 of 12); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the router serves migrated zones from the rewrite and the rest from the legacy engine, and in shadow mode returns the legacy quote while reporting a Mismatch.
  - With every zone migrated the legacy engine is never called, so the router and the legacy module go together; mypy holds the rewrite to the legacy call shape. Transitional Architecture and Dark Launching are credited.
- Credits: Transitional Architecture; Dark Launching (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 29: divider (The final project)

- Claim: -
- Notes cover: one booking through every step, undone on a refusal, published after the commit.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 30: An acceptance test first (The final project)

- Claim: An acceptance test says when the slice is whole and comes first. Because its helper returns a list in a fixed order, a failing run says which stage is absent, not only that something is.
- Chapter: 39, "Final project" (`_docs/39-final-project.md`).
- `39-final-project.md:34`: `grep -nF -- 'An acceptance test says when the slice is whole, and it comes first' _docs/39-final-project.md`
  - Sentence: An acceptance test says when the slice is whole, and it comes first: it fixes one request and the shipment that request has to produce, and the parts are built until it passes.
- `39-final-project.md:68`: `grep -nF -- 'Because the helper returns a list in a fixed order, a failing run says which stage is absent, not only that something is.' _docs/39-final-project.md`
  - Sentence: Because the helper returns a list in a fixed order, a failing run says which stage is absent, not only that something is.
- `39-final-project.md:79`: `grep -nF -- 'When the acceptance test goes red it says which stage; the part'"'"'s own test says why.' _docs/39-final-project.md`
  - Sentence: When the acceptance test goes red it says which stage; the part's own test says why.
- Plan lines (tree at 6c27a6f): 39:34, 39:68, 39:70-75, 39:79; census lines: 39:34, 39:68, 39:79.
- Witness tests, each defined once:
  - `test_a_booking_request_ships_end_to_end` (`examples/39-final-project/tests/test_acceptance.py:98`, 1 definition)
  - `test_the_acceptance_test_fails_when_a_stage_is_left_out` (`examples/39-final-project/tests/test_acceptance.py:110`, 1 definition)
- Code: `examples/39-final-project/tests/test_acceptance.py` lines 35 to 49 (15 lines, longest 88 characters, tabs 0, trailing whitespace 0, common indent 4); font by the builder from the longest line (by the builder).
  - Anchor (line 35, exact, 4 leading spaces): `failures: list[str] = []`
  - Last line (49): `return failures`
  - Contiguous run of the python fence at `39-final-project.md:36` to `39-final-project.md:56` (block lines 5 to 19 of 19); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the helper that collects what is missing instead of stopping at the first miss, so a failing run names the stage.
  - The four left-out stages (rating, carrier, clearance, tracking) are stage removals, each with the helper's list. Percival and Gregory are credited in Architecture Patterns with Python, under 'TDD in High Gear and Low Gear'.
- Credits: Architecture Patterns with Python (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 31: Undo in reverse (The final project)

- Claim: Each step registers its inverse as soon as it succeeds, a refusal runs them newest first, and pop_all() is the commit. A held declaration releases the slot and cancels the carrier booking.
- Chapter: 39, "Final project" (`_docs/39-final-project.md`).
- `39-final-project.md:101`: `grep -nF -- 'a refusal runs them newest first' _docs/39-final-project.md`
  - Sentence: A step that succeeded has to be taken back when a later step refuses, and the desk gets the means from a stack of inverses: each step registers the function that reverses it as soon as it succeeds, and a refusal runs them newest first.
- `39-final-project.md:126`: `grep -nF -- 'In `ship`, `pop_all()` is the commit.' _docs/39-final-project.md`
  - Sentence: In `ship`, `pop_all()` is the commit.
- `39-final-project.md:141`: `grep -nF -- 'The slot was reserved first and the carrier booked second, so the carrier is cancelled first.' _docs/39-final-project.md`
  - Sentence: The slot was reserved first and the carrier booked second, so the carrier is cancelled first.
- Plan lines (tree at 6c27a6f): 39:101, 39:126, 39:141, 39:198; census lines: 39:101, 39:126, 39:141.
- Witness tests, each defined once:
  - `test_the_undo_runs_in_reverse_order_of_the_steps` (`examples/39-final-project/tests/test_rollback.py:41`, 1 definition)
  - `test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking` (`examples/39-final-project/tests/test_rollback.py:30`, 1 definition)
  - `test_a_full_sailing_books_nothing_with_the_carrier` (`examples/39-final-project/tests/test_rollback.py:51`, 1 definition)
- Code: `examples/39-final-project/src/final_project/desk.py` lines 43 to 52 (10 lines, longest 59 characters, tabs 0, trailing whitespace 0, common indent 4); font by the builder from the longest line (by the builder).
  - Anchor (line 43, exact, 4 leading spaces): `def ship(self, request: BookingRequest, /) -> Shipment:`
  - Last line (52): `undo.pop_all()`
  - Contiguous run of the python fence at `39-final-project.md:104` to `39-final-project.md:123` (block lines 1 to 10 of 18); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: each step registers its inverse as it succeeds, a refusal runs them newest first, and pop_all() is the commit.
  - Number: with pop_all() deleted (E39-1), five tests fail and 18 pass, and mypy exits 0, because the booking is made and then undone. The contextlib sentences are credited. Not for a restart, or a step that cannot be undone; Unit of Work in Architecture Patterns with Python is the persistent form.
- Credits: contextlib documentation; Architecture Patterns with Python (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 32: Publish after the commit (The final project)

- Claim: An event cannot be taken back, so effects other parts can see go after pop_all(). An eager publisher reports a booking that was rolled back.
- Chapter: 39, "Final project" (`_docs/39-final-project.md`).
- `39-final-project.md:147`: `grep -nF -- 'An event can'"'"'t be taken back.' _docs/39-final-project.md`
  - Sentence: An event can't be taken back.
- `39-final-project.md:166`: `grep -nF -- 'The rule is that effects other parts can see go after `pop_all()`.' _docs/39-final-project.md`
  - Sentence: The rule is that effects other parts can see go after `pop_all()`.
- `39-final-project.md:309`: `grep -nF -- 'mypy exits 0 again, because publish order isn'"'"'t a type.' _docs/39-final-project.md`
  - Sentence: Everything else passes, including the eager-publisher test, which already expected the early event, and mypy exits 0 again, because publish order isn't a type.
- Plan lines (tree at 6c27a6f): 39:147, 39:166, 39:309; census lines: 39:147, 39:166, 39:309.
- Witness tests, each defined once:
  - `test_a_held_booking_publishes_no_tracking_event` (`examples/39-final-project/tests/test_tracking.py:22`, 1 definition)
  - `test_an_eager_publisher_reports_a_booking_that_was_rolled_back` (`examples/39-final-project/tests/test_tracking.py:37`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_an_invoice_in_two_currencies_has_no_total` (`examples/39-final-project/tests/test_parts.py:120`, 1 definition)
- Code: `examples/39-final-project/src/final_project/desk.py` lines 53 to 60 (8 lines, longest 89 characters, tabs 0, trailing whitespace 0, common indent 8); font by the builder from the longest line (by the builder).
  - Anchor (line 53, exact, 8 leading spaces): `invoice = Invoice(`
  - Last line (60): `return Shipment(rate, slot, reference, declaration, invoice)`
  - Contiguous run of the python fence at `39-final-project.md:104` to `39-final-project.md:123` (block lines 11 to 18 of 18); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the last statements of ship, with the event published after the commit; a held booking leaves no event.
  - Number: with the publish moved into the with block (E39-2), one test fails and 22 pass, and mypy exits 0, because publish order is not a type. Billing refuses to total two currencies.
- Credits: contextlib documentation (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 33: One composition root (The final project)

- Claim: One function chooses the carrier, the subscriber and the pricing rule, and the fewer places that name a concrete carrier, the fewer change when a carrier does. mypy refuses a gateway without cancel.
- Chapter: 39, "Final project" (`_docs/39-final-project.md`).
- `39-final-project.md:170`: `grep -nF -- 'the fewer places that do, the fewer places change when a carrier does.' _docs/39-final-project.md`
  - Sentence: Something has to decide, and the fewer places that do, the fewer places change when a carrier does.
- `39-final-project.md:188`: `grep -nF -- 'mypy guards the other seam.' _docs/39-final-project.md`
  - Sentence: mypy guards the other seam.
- `39-final-project.md:186`: `grep -nF -- '`test_only_the_composition_root_names_a_concrete_carrier` parses each module of the package except `carriers.py` with `ast`' _docs/39-final-project.md`
  - Sentence: `test_only_the_composition_root_names_a_concrete_carrier` parses each module of the package except `carriers.py` with `ast` and lists the ones that import or use `FastlineGateway` or `FastlineClient`.
- Plan lines (tree at 6c27a6f): 39:170, 39:190; census lines: 39:170, 39:186, 39:188.
- Witness tests, each defined once:
  - `test_the_pricing_rule_is_chosen_at_the_composition_root` (`examples/39-final-project/tests/test_parts.py:76`, 1 definition)
  - `test_mypy_refuses_a_gateway_without_cancel` (`examples/39-final-project/tests/test_static.py:65`, 1 definition)
  - `test_only_the_composition_root_names_a_concrete_carrier` (`examples/39-final-project/tests/test_structure.py:17`, 1 definition)
- Code: `examples/39-final-project/src/final_project/app.py` lines 11 to 21 (11 lines, longest 96 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (14 pt).
  - Anchor (line 11, exact, 0 leading spaces): `def build_desk(`
  - Last line (21): `return BookingDesk(rule=rule, plan=plan, gateway=FastlineGateway(client), events=events)`
  - Contiguous run of the python fence at `39-final-project.md:172` to `39-final-project.md:184` (block lines 1 to 11 of 11); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: the one function that chooses the carrier, the subscriber and the pricing rule; a gateway without cancel is refused by mypy and the message names the gateway Protocol.
  - The structure test lists only app.py as naming a concrete carrier. Percival and Gregory's bootstrap is credited.
- Credits: Architecture Patterns with Python (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 34: divider (Working with AI tools)

- Claim: -
- Notes cover: a reply trusted as far as the checks it has passed.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 35: Three drafts, three gates (Working with AI tools)

- Claim: Three drafts, written by hand as stand-ins for replies, are checked by a static gate, a shape review and a behaviour oracle. Each gate alone accepts a draft that another gate stops, and only the idiomatic module passes all three.
- Chapter: 40, "Working with AI and LLM tools" (`_docs/40-working-with-ai-and-llm-tools.md`).
- `40-working-with-ai-and-llm-tools.md:53`: `grep -nF -- 'Each gate alone accepts at least one draft that another gate stops' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: Each gate alone accepts at least one draft that another gate stops: the static gate accepts the second and third, the shape review accepts the third, and the oracle accepts the second.
- `40-working-with-ai-and-llm-tools.md:53`: `grep -nF -- 'Of these four modules, only the idiomatic one passes all three.' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: Of these four modules, only the idiomatic one passes all three.
- `40-working-with-ai-and-llm-tools.md:26`: `grep -nF -- 'They stand in for replies, so the results describe these drafts and make no claim about what any assistant writes.' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: They stand in for replies, so the results describe these drafts and make no claim about what any assistant writes.
- Plan lines (tree at 6c27a6f): 40:53, 40:26, 40:46-51, 40:24; census lines: 40:26, 40:53.
- Witness tests, each defined once:
  - `test_each_draft_fails_exactly_the_gates_in_the_table` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:56`, 1 definition)
  - `test_the_idiomatic_module_passes_every_gate` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:74`, 1 definition)
  - `test_every_draft_says_it_was_written_for_the_book` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:70`, 1 definition)
- Table: see section "Table cells" (slide 35).
- Notes cover:
  - What the slide shows: three drafts written by hand as stand-ins for replies and the gate that stops each; the results describe these drafts and make no claim about what any assistant writes.
  - The class-per-strategy shape, a getter and setter, and a factory that stores its instance are what the shape rules look for. OWASP LLM05:2025 is quoted and credited.
- Credits: OWASP LLM05:2025 (section "Credits per slide").
- Disposition: **kept**. claim, witnesses and table cells confirmed.

### Slide 36: Gates in parallel (Working with AI tools)

- Claim: A draft is checked by three gates that no code orders: the answers differ because the questions do. The typed hierarchy passes mypy and ruff, and the oracle lists the three half-cent rows.
- Chapter: 40, "Working with AI and LLM tools" (`_docs/40-working-with-ai-and-llm-tools.md`).
- `40-working-with-ai-and-llm-tools.md:53`: `grep -nF -- 'The gates answer different questions.' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: The gates answer different questions.
- `40-working-with-ai-and-llm-tools.md:89`: `grep -nF -- '`test_mypy_and_ruff_pass_the_typed_hierarchy` asserts that both tools report nothing on this draft' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: `test_mypy_and_ruff_pass_the_typed_hierarchy` asserts that both tools report nothing on this draft, and that mypy reports `unreachable` for a statement after a `return`, which pins `--warn-unreachable`.
- `40-working-with-ai-and-llm-tools.md:146`: `grep -nF -- 'both give exactly the same three differences' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: `untyped_factory` leaves the rounding argument out and `rounded_callable` uses `round`, and both give exactly the same three differences (`test_the_oracle_lists_the_half_cent_rows`): `CN-5 per_kg: 0.23 != 0.22`, `CN-7 per_kg: 1.13 != 1.12` and `CN-8 per_kg: 5.63 != 5.62`.
- Plan lines (tree at 6c27a6f): 40:53, 40:89; census lines: 40:53, 40:89, 40:146.
- Witness tests, each defined once:
  - `test_mypy_and_ruff_pass_the_typed_hierarchy` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:100`, 1 definition)
  - `test_the_static_gate_reports_the_untyped_draft` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:81`, 1 definition)
  - `test_the_oracle_lists_the_half_cent_rows` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:131`, 1 definition)
- Figure: figure 40, `presentation/png/40-working-with-ai-and-llm-tools.png` (see Figure census).
- Notes cover:
  - What the slide shows: each box and arrow of the figure; the gates are in parallel because no code orders them.
  - Number: with round() in place of quantize in the idiomatic module (E40-1), one test fails and 25 pass, and mypy exits 0. The oracle's three rows are the half-cent products. The mypy and ruff pages are credited.
- Credits: mypy command line; ruff UP045 (section "Credits per slide").
- Disposition: **kept**. claim and witnesses confirmed; the figure passes the census.

### Slide 37: A seam for the model (Working with AI tools)

- Claim: Code that asks an assistant for a reply has a dependency like any other: put it behind a Protocol with a recorded fake. An unrecorded prompt raises, the loop stops at the first accepted reply, and the package imports no network module.
- Chapter: 40, "Working with AI and LLM tools" (`_docs/40-working-with-ai-and-llm-tools.md`).
- `40-working-with-ai-and-llm-tools.md:158`: `grep -nF -- 'Code that asks an assistant for a reply has a dependency like any other' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: Code that asks an assistant for a reply has a dependency like any other, and the book's usual move for a dependency is a Protocol with a fake behind it in tests.
- `40-working-with-ai-and-llm-tools.md:199`: `grep -nF -- 'An unrecorded prompt raises `LookupError`, so a test can'"'"'t pass on a prompt nobody recorded' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: An unrecorded prompt raises `LookupError`, so a test can't pass on a prompt nobody recorded (`test_an_unrecorded_prompt_is_refused`).
- `40-working-with-ai-and-llm-tools.md:201`: `grep -nF -- 'The package imports no network module' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: The package imports no network module: `test_the_package_imports_no_network_module` parses its five files and finds no import of `socket`, `ssl`, `http`, `urllib`, `asyncio` or `subprocess`.
- Plan lines (tree at 6c27a6f): 40:158, 40:199; census lines: 40:158, 40:199, 40:201.
- Witness tests, each defined once:
  - `test_a_rejected_reply_is_sent_back_with_its_findings` (`examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py:23`, 1 definition)
  - `test_the_loop_stops_at_the_first_accepted_reply` (`examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py:33`, 1 definition)
  - `test_the_loop_gives_up_after_its_attempts` (`examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py:43`, 1 definition)
  - `test_an_unrecorded_prompt_is_refused` (`examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py:55`, 1 definition)
  - `test_the_package_imports_no_network_module` (`examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py:62`, 1 definition)
  - `test_mypy_refuses_an_assistant_without_reply` (`examples/40-working-with-ai-and-llm-tools/tests/test_static.py:51`, 1 definition)
- Code: `examples/40-working-with-ai-and-llm-tools/src/review_gate/assistant.py` lines 42 to 56 (15 lines, longest 91 characters, tabs 0, trailing whitespace 0, common indent 0); font by the builder from the longest line (by the builder).
  - Anchor (line 42, exact, 0 leading spaces): `def propose(`
  - Last line (56): `return reviews`
  - Contiguous run of the python fence at `40-working-with-ai-and-llm-tools.md:161` to `40-working-with-ai-and-llm-tools.md:196` (block lines 20 to 34 of 34); identical line for line to the source range, so byte-exact with the chapter.
- Notes cover:
  - What the slide shows: propose asks, gates the reply and, if it is rejected, asks again with the findings appended; a recorded fake holds a reply for exactly that text.
  - Number: with one shape rule removed (E40-2), four tests fail and 22 pass, and mypy exits 0. The package imports no network module; the tests run mypy in-process and ruff as a local process.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 38: Limits of the gates (Working with AI tools)

- Claim: The gates verify what they list: a draft that passes all three has been checked on those rows and in those shapes, and no further. A diff that edits the expected rows moves the answer the oracle holds every draft to.
- Chapter: 40, "Working with AI and LLM tools" (`_docs/40-working-with-ai-and-llm-tools.md`).
- `40-working-with-ai-and-llm-tools.md:205`: `grep -nF -- 'The gates verify what they list.' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: The gates verify what they list.
- `40-working-with-ai-and-llm-tools.md:205`: `grep -nF -- 'A diff that edits `EXPECTED_ROWS` moves the answer the oracle holds every draft to.' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: A diff that edits `EXPECTED_ROWS` moves the answer the oracle holds every draft to.
- `40-working-with-ai-and-llm-tools.md:207`: `grep -nF -- 'Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy.' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: OWASP's [LLM09:2025 entry, Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/), names the failure: "Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy." The gates are a way to verify accuracy at chosen points, and everything between those points is trust.
- `40-working-with-ai-and-llm-tools.md:152`: `grep -nF -- 'The form is reusable because the prompt can state the checks before any reply exists.' _docs/40-working-with-ai-and-llm-tools.md`
  - Sentence: The form is reusable because the prompt can state the checks before any reply exists.
- Plan lines (tree at 6c27a6f): 40:205, 40:207, 40:152; census lines: 40:152, 40:205, 40:207.
- Witness tests, each defined once:
  - `test_the_oracle_lists_the_half_cent_rows` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:131`, 1 definition)
  - `test_mypy_and_ruff_pass_the_typed_hierarchy` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:100`, 1 definition)
- Notes cover:
  - What the slide shows: the gates verify what they list and no further, and a diff that edits the expected rows moves the answer.
  - A prompt that lists the gates says what the reply will be measured against; the review line asks who decided that answer should change. OWASP LLM09:2025 is quoted and credited.
- Credits: OWASP LLM09:2025 (section "Credits per slide").
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 39: divider (Reference)

- Claim: -
- Notes cover: sources, books and the pinned tools.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 40: Sources credited (Reference)

- Claim: The online sources the slides use.
- Chapter: none; a structural slide.
- Table: see section "Table cells" (slide 40).
- Notes cover:
  - Each source is named with its authors and what the slide uses it for.
- Disposition: **kept**. credits table; built from the chapters' own links.

### Slide 41: Reading further (Reference)

- Claim: The books the chapters cite.
- Chapter: none; a structural slide.
- Table: see section "Table cells" (slide 41).
- Notes cover:
  - These books cover the ground the slides compress.
- Disposition: **kept**. credits table; built from the chapters and the bibliography.

### Slide 42: Site and repository (Reference)

- Claim: The site and repository URLs, how to run an example, the pinned versions and the two further decks by theme.
- Chapter: none; a structural slide.
- Table: see section "Table cells" (slide 42).
- Notes cover:
  - The site and repository, how to run an example, the pinned tools by exact version, and the two further decks by theme.
- Disposition: **kept**. URLs return 200; pins re-read from the tree.

## Table cells (slides 5, 12, 35, 40, 41 and 42)

Each cell is a `grep -F` fragment of the chapter at the stated line, and every test is defined once. A row hit exactly one line.

### Slide 5: What each double refuses

Columns: Double, Unknown name, Wrong call, mypy. The chapter's own column heads are "Unknown name, `bok`" and "Call with no consignment"; the slide shortens them.

| Double | Unknown name | Wrong call | mypy | Chapter row (`grep -nF` of the whole row) | Test |
| --- | --- | --- | --- | --- | --- |
| `FakeGateway` | `AttributeError`; mypy `[attr-defined]` | `TypeError`; mypy `[call-arg]` | checked: a missing member is an error | `11:67` hit 1 line | `test_a_fake_rejects_unknown_names_and_wrong_signatures` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:69`) |
| `Mock()` | accepted | accepted | accepted | `11:68` hit 1 line | `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:37`) |
| `Mock(spec=CarrierGateway)` | `AttributeError` | accepted | accepted | `11:69` hit 1 line | `test_spec_rejects_unknown_names_but_not_wrong_signatures` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:49`) |
| `create_autospec(CarrierGateway, instance=True)` | `AttributeError` | `TypeError` | accepted | `11:70` hit 1 line | `test_autospec_rejects_names_and_signatures` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py:59`) |

### Slide 12: Two vocabularies

Columns: Word, pytest-mock meaning, Meszaros meaning. Two rows; the Dummy Object row is qualified in the chapter and is a note, not a row. The cells are worded from the chapter's prose:

| Word | pytest-mock meaning | Meszaros meaning |
| --- | --- | --- |
| Stub | a mock object that accepts any arguments and is useful to test callbacks (`mocker.stub()`) | a double that feeds indirect inputs to the code under test (Test Stub) |
| Spy | a call the test made on a wrapped real object, recorded (`mocker.spy`) | a double that captures the indirect outputs of the code under test for later verification (Test Spy) |

| Cell | Fragment | Chapter line | Hit |
| --- | --- | --- | --- |
| pytest-mock stub | `The stub is a mock object that accepts any arguments and is useful to test callbacks.` | `44:145` | 1 |
| Meszaros stub | `Meszaros's Test Stub is a double that feeds indirect inputs to the code under test.` | `44:145` | 1 |
| pytest-mock spy and Meszaros spy | `It records a call the test made, where a Test Spy records an indirect output of a system under test` | `44:147` | 1 |
| Meszaros spy summary | `Use a Test Double to capture the indirect output calls made to another component by the system under test (SUT) for later verification by the test.` | `44:104` | 1 |
| qualified Dummy paragraph | `Dummy Object is qualified.` | `44:110` | 1 |

Tests: `test_stub_records_a_callback` (`examples/43-appendix-c-mocking/tests/test_spies.py:48`), `test_spy_keeps_the_real_behaviour_and_records_returns` (`test_spies.py:23`), `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` (`examples/43-appendix-c-mocking/tests/test_booking.py:19`), each defined once.

### Slide 35: Three drafts, three gates

Columns: Draft, Static gate, Shape review, Behaviour oracle. Four rows from the chapter's table; `pricing.py` is shown as "the idiomatic module".

| Draft | Static gate | Shape review | Behaviour oracle | Chapter row | Hit |
| --- | --- | --- | --- | --- | --- |
| `untyped_factory` | fails | fails | fails | `40:48` | 1 |
| `typed_hierarchy` | passes | fails | passes | `40:49` | 1 |
| `rounded_callable` | passes | passes | fails | `40:50` | 1 |
| `pricing.py` | passes | passes | passes | `40:51` | 1 |

The first three rows are `test_each_draft_fails_exactly_the_gates_in_the_table` (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:56`), run once per draft (its `TABLE` at `test_gates.py:37-41` holds the same three triples), and the last is `test_the_idiomatic_module_passes_every_gate` (`test_gates.py:73`).

### Slide 40: Sources credited

Columns: Source, Used for. One row per source (a source used by more than one slide is one row). Every URL is a link in the named chapters at the stated lines (a `grep -nF` of the URL in the chapter); a URL cited in the body and in "For deeper coverage" shows every line. Each URL was fetched with `curl -sI`; the status is recorded in "URLs".

| Source | Used for | URL | Slides | Chapter lines |
| --- | --- | --- | --- | --- |
| pytest documentation: fixtures how-to | a yield fixture's teardown follows the test | https://docs.pytest.org/en/stable/how-to/fixtures.html | 7 | 11:37; 11:391 |
| pytest documentation: monkeypatch how-to | monkeypatch changes are undone; context() scopes them | https://docs.pytest.org/en/stable/how-to/monkeypatch.html | 7 | 11:179; 11:391; 33:315 |
| pytest documentation: capture warnings | the default is a summary that is easy to scroll past | https://docs.pytest.org/en/stable/how-to/capture-warnings.html | 9 | 11:213; 11:391 |
| pytest documentation: reference | strict options, their names and the strict alias | https://docs.pytest.org/en/stable/reference/reference.html | 9 | 11:209; 11:391; 42:50; 42:53; 42:65; 42:67; 42:170; 42:231 |
| pytest documentation: configuration | one configuration file applies and files are never merged | https://docs.pytest.org/en/stable/reference/customize.html | 9 | 42:50; 42:57; 42:231 |
| pytest documentation: import mechanisms | the cost of each import mode | https://docs.pytest.org/en/stable/explanation/pythonpath.html | 10 | 42:83; 42:231 |
| Python documentation: unittest.mock | the mock API: assert_has_calls and spec_set | https://docs.python.org/3/library/unittest.mock.html | 11 | 33:69; 43:285 |
| Python documentation: unittest.mock, Autospeccing | what create_autospec copies | https://docs.python.org/3/library/unittest.mock.html#autospeccing | 6 | 11:123; 11:391; 33:315 |
| Python documentation: unittest.mock, Where to patch | patch where an object is looked up | https://docs.python.org/3/library/unittest.mock.html#where-to-patch | 15 | 33:315 |
| typeshed: unittest/mock.pyi | mocks subclass Any, so mypy accepts them everywhere | https://github.com/python/typeshed/blob/main/stdlib/unittest/mock.pyi | 6 | 11:125; 11:391; 43:285 |
| pytest-mock documentation: usage | stub, spy and resetall | https://pytest-mock.readthedocs.io/en/stable/usage.html | 11, 12 | 43:285; 44:145 |
| Python documentation: importlib.reload | a reload overwrites a live patch | https://docs.python.org/3/library/importlib.html#importlib.reload | 16 | 33:315 |
| Python documentation: typing, annotating callable objects | a callback Protocol says keyword-only | https://docs.python.org/3/library/typing.html#annotating-callable-objects | 20 | 34:105 |
| Python documentation: functools | partial binds the standard quoters | https://docs.python.org/3/library/functools.html | 21 | 34:153; 34:268 |
| Martin Fowler, Mocks Aren't Stubs | state against behaviour verification | https://martinfowler.com/articles/mocksArentStubs.html | 5, 12 | 11:393; 43:287; 44:164; 44:202 |
| Martin Fowler, Definition Of Refactoring | the noun refactoring | https://martinfowler.com/bliki/DefinitionOfRefactoring.html | 24 | 35:232 |
| Martin Fowler, Self Testing Code | the condition Fowler's method needs | https://martinfowler.com/bliki/SelfTestingCode.html | 24 | 35:232 |
| refactoring.com | small behaviour-preserving transformations | https://refactoring.com/ | 24 | 35:32; 35:232 |
| Python documentation: decimal | round on a Decimal respects the context's rounding mode | https://docs.python.org/3/library/decimal.html | 25 | 35:144; 35:232 |
| Martin Fowler, Strangler Fig | replacements are hard to specify | https://martinfowler.com/bliki/StranglerFigApplication.html | 26 | 36:24; 36:224 |
| Python documentation: bisect | bisect_left and bisect_right insertion points | https://docs.python.org/3/library/bisect.html | 26 | 36:83; 36:224 |
| Cartwright, Horn and Lewis, Patterns of Legacy Displacement: Feature Parity | parity as the aim of a rewrite | https://martinfowler.com/articles/patterns-legacy-displacement/feature-parity.html | 27 | 36:87; 36:224 |
| Cartwright, Horn and Lewis, Patterns of Legacy Displacement: Transitional Architecture | the router is transitional | https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html | 28 | 36:135; 36:224 |
| Martin Fowler, Dark Launching | calling new behaviour without users seeing it | https://martinfowler.com/bliki/DarkLaunching.html | 28 | 36:137; 36:224 |
| Python documentation: contextlib | ExitStack, callback and pop_all | https://docs.python.org/3/library/contextlib.html | 31, 32 | 39:126; 39:321 |
| OWASP Top 10 for LLM Applications: LLM05:2025 Improper Output Handling | treat model output with zero trust | https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/ | 35 | 40:24; 40:282 |
| OWASP Top 10 for LLM Applications: LLM09:2025 Misinformation | overreliance means failing to verify | https://genai.owasp.org/llmrisk/llm092025-misinformation/ | 38 | 40:207; 40:282 |
| mypy documentation: command line | what --strict enables and --warn-unreachable | https://mypy.readthedocs.io/en/stable/command_line.html | 36 | 40:282 |
| Ruff documentation: UP045 | Optional annotations rewritten as PEP 604 unions | https://docs.astral.sh/ruff/rules/non-pep604-annotation-optional/ | 36 | 40:61; 40:282 |
| Gerard Meszaros, xunitpatterns.com pattern pages | Test Stub, Test Spy and Dummy Object definitions | http://xunitpatterns.com/Test%20Stub.html | 12 | 44:103 |
| Gerard Meszaros, xunitpatterns.com pattern pages | Test Stub, Test Spy and Dummy Object definitions | http://xunitpatterns.com/Test%20Spy.html | 12 | 44:104; 44:139 |
| Gerard Meszaros, xunitpatterns.com pattern pages | Test Stub, Test Spy and Dummy Object definitions | http://xunitpatterns.com/Dummy%20Object.html | 12 | 44:102 |

30 sources in the superset; the slide cannot hold them all legibly in one table, so the builder splits them by theme or drops the rows whose slide notes already carry the credit. A row for a PEP would name its authors; there are none here. Each source is named in the notes of every slide in its Slides column, and nowhere else.

### Slide 41: Reading further

Columns: Book, Authors, Year. Each row is cited by an in-scope chapter and listed in `bibliography.html`.

| Book | Authors | Year | Publisher | Slides | Chapter lines | Bibliography link |
| --- | --- | --- | --- | --- | --- | --- |
| Working Effectively with Legacy Code | Michael Feathers | 2004 | Prentice Hall | 14, 19, 22, 24 | 33:32; 33:315; 34:32; 34:268; 35:34; 35:232; 36:32; 36:224 | https://www.oreilly.com/library/view/working-effectively-with/0131177052/ (listed: True; `grep -cF -- 'Working Effectively with Legacy Code' bibliography.html` = 1) |
| Refactoring: Improving the Design of Existing Code, second edition | Martin Fowler | 2018 | Addison-Wesley | 24 | 35:232; 36:224 | https://martinfowler.com/books/refactoring.html (listed: True; `grep -cF -- 'Refactoring: Improving the Design of Existing Code' bibliography.html` = 1) |
| xUnit Test Patterns: Refactoring Test Code | Gerard Meszaros | 2007 | Addison-Wesley | 12 | 11:61; 11:393; 43:287; 44:23; 44:202 | https://www.informit.com/store/xunit-test-patterns-refactoring-test-code-9780132800051 (listed: True; `grep -cF -- 'xUnit Test Patterns' bibliography.html` = 1) |
| Python Testing with pytest, second edition | Brian Okken | 2022 | Pragmatic Bookshelf | 9 | 11:37; 11:393; 42:231 | https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/ (listed: True; `grep -cF -- 'Python Testing with pytest' bibliography.html` = 1) |
| Architecture Patterns with Python | Harry Percival and Bob Gregory | 2020 | O'Reilly | 30, 31, 33 | 39:79; 39:190; 39:198; 39:321 | https://www.oreilly.com/library/view/-/9781492052197/ (listed: True; `grep -cF -- 'Architecture Patterns with Python' bibliography.html` = 1) |
| Effective Python: 125 Specific Ways to Write Better Python, third edition | Brett Slatkin | 2024 | Addison-Wesley | none (reading list only) | 11:393 | https://www.oreilly.com/library/view/-/9780138172398/ (listed: True; `grep -cF -- 'Effective Python: 125' bibliography.html` = 1) |

Six books. The year, authors and publisher are the bibliography page's. *Effective Python* is cited by one chapter as further reading and no slide's claim rests on it, so its Slides cell is empty; it stays on the reading list. Two bibliography links (Effective Python and Architecture Patterns with Python) answer 301 and redirect to the same book's canonical O'Reilly address; both end at 200.

### Slide 42: Site and repository

| Item | Value | Source |
| --- | --- | --- |
| Site | https://patterncatalyst.github.io/design-patterns-with-python/ | `curl -sI` 200 on 2026-11-07 |
| Repository | https://github.com/patterncatalyst/design-patterns-with-python | `curl -sI` 200 on 2026-11-07 |
| Run an example | `uv sync --locked --all-packages` once from the repository root, then `uv run pytest` and `uv run mypy --strict src tests` in the example's directory | `33:233`, `39:212` |
| CPython 3.15.2 | `.python-version` reads `3.15.2` | `.python-version:1`; `_docs/00-prerequisites.md:33`, `:40` |
| uv 0.13.7 | `uv --version` prints `uv 0.13.7` | `_docs/00-prerequisites.md:34` (the table row), `uv --version` run in the copy |
| pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4, mypy 2.4.1 | exact pins | `pyproject.toml:18-21`; `_docs/00-prerequisites.md:35-38` |
| The other two decks | by theme only (idiomatic Python for 201; patterns and SOLID for 101) | README "Companion decks" |

## Credits per slide

The credits each slide's notes name, from the two tables above (the superset for the reference slides). A slide's notes credit only these.

- Slide 5: Martin Fowler, Mocks Aren't Stubs
- Slide 6: Python documentation: unittest.mock, Autospeccing; typeshed: unittest/mock.pyi
- Slide 7: pytest documentation: fixtures how-to; pytest documentation: monkeypatch how-to
- Slide 9: pytest documentation: reference; pytest documentation: configuration; pytest documentation: capture warnings; Python Testing with pytest, second edition
- Slide 10: pytest documentation: import mechanisms
- Slide 11: Python documentation: unittest.mock; pytest-mock documentation: usage
- Slide 12: Gerard Meszaros, xunitpatterns.com pattern pages; pytest-mock documentation: usage; xUnit Test Patterns: Refactoring Test Code; Martin Fowler, Mocks Aren't Stubs
- Slide 14: Working Effectively with Legacy Code
- Slide 15: Python documentation: unittest.mock, Where to patch
- Slide 16: Python documentation: importlib.reload
- Slide 19: Working Effectively with Legacy Code
- Slide 20: Python documentation: typing, annotating callable objects
- Slide 21: Python documentation: functools
- Slide 22: Working Effectively with Legacy Code
- Slide 24: Martin Fowler, Definition Of Refactoring; Martin Fowler, Self Testing Code; refactoring.com; Refactoring: Improving the Design of Existing Code, second edition; Working Effectively with Legacy Code
- Slide 25: Python documentation: decimal
- Slide 26: Martin Fowler, Strangler Fig; Python documentation: bisect
- Slide 27: Cartwright, Horn and Lewis, Patterns of Legacy Displacement: Feature Parity
- Slide 28: Cartwright, Horn and Lewis, Patterns of Legacy Displacement: Transitional Architecture; Martin Fowler, Dark Launching
- Slide 30: Architecture Patterns with Python
- Slide 31: Python documentation: contextlib; Architecture Patterns with Python
- Slide 32: Python documentation: contextlib
- Slide 33: Architecture Patterns with Python
- Slide 35: OWASP Top 10 for LLM Applications: LLM05:2025 Improper Output Handling
- Slide 36: mypy documentation: command line; Ruff documentation: UP045
- Slide 38: OWASP Top 10 for LLM Applications: LLM09:2025 Misinformation

## Figure census

Re-run now, arrow by arrow, against the specs in `diagrams/specs/` and the code. A figure passes when every arrow is composed by code (a call in `src`, a call the test makes, or interpreter dispatch the test witnesses) and no arrow is conceptual. Legibility is the smallest `font-size` in the SVG scaled into the 12.09 by 4.95 inch box by the contained fit (`min(12.09/w, 4.95/h)`), against the 6.3 pt floor.

| Fig | Slide | viewBox | Smallest label, pt | Edges | Caption words | Registry equals include | PNG (pixels) | Frame, in | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | 15 | 1020x610 | 6.4 | 3 | 41 | yes | `presentation/png/33-seams-in-python.png` (1600x957) | 8.28 by 4.95 | passes |
| 40 | 36 | 960x500 | 7.8 | 7 | 39 | yes | `presentation/png/40-working-with-ai-and-llm-tools.png` (1600x833) | 9.51 by 4.95 | passes |

`presentation/render-png.sh --check` in the fresh copy printed `same` for both PNGs (and for all eighteen figures). The frame the builder uses comes from the PNG's own aspect (1600/957 and 1600/833). The smallest label of figure 33 is the lowest in any deck; the QA drop rule (a viewer cannot read it) is unchanged.

### Figure 33 (slide 15)

Spec: `diagrams/specs/33-seams-in-python.py`, three edges. F1 applied: the two dashed boxes ("patch on seams.fastline.request_quote", "margin=MARGIN in __init__") and the "mypy checks neither" bar are unconnected notes; the spec has no edge into or out of them.

- test to namespace of `seams.legacy`: `monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)` at `examples/33-seams-in-python/tests/test_patching.py:36`, with the result asserted at `:39-40`. Witness: `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`.
- namespace to `RateEngine`, labelled "request_quote: looked up in seams.legacy": the name is bound by the `from` import at `examples/33-seams-in-python/src/seams/legacy.py:12` and read by the call at `:24`. Witness: `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier` (the patch on the defining module misses this lookup).
- namespace to `RateEngine`, labelled "airco.price: looked up on seams.airco": the module is bound at `legacy.py:10` and `airco.price(` is read at `:25-27`. Witness: `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`.
- Unconnected notes: the defining-module patch has no effect on `RateEngine.quote` (`test_patching.py:43-53`), and the margin default is read when the class is defined (`test_patching_a_module_constant_misses_a_default_captured_at_definition`). No edge claims a reach the tests do not show.
- Verdict: every arrow composed.

### Figure 40 (slide 36)

Spec: `diagrams/specs/40-working-with-ai-and-llm-tools.py`, seven edges. F2 applied: each gate box names every draft that gate reports (static gate: `untyped_factory`; shape review: `untyped_factory`, `typed_hierarchy`; behaviour oracle: `untyped_factory`, `rounded_callable`), which is the `TABLE` at `tests/test_gates.py:37-41`.

- draft to static gate, to shape review and to behaviour oracle (three edges): the three calls `static_gate(draft.text)`, `review(draft.text)` and `oracle(load_module(draft.text))` at `examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:62-64`; `StaticGate.__call__` at `tests/conftest.py:98`, `review` at `src/review_gate/shape.py:104`. Witness: `test_each_draft_fails_exactly_the_gates_in_the_table`.
- shape review back up to the draft, labelled "propose: findings go back in the next prompt" (amber): `propose` builds the next prompt from the findings at `src/review_gate/assistant.py:50-55`, with `review` as the gate (`tests/test_assistant.py:28`). Witness: `test_a_rejected_reply_is_sent_back_with_its_findings`.
- each gate to "accepted" (three edges): witnessed by the assert at `tests/test_gates.py:78`, `(static_gate(source), review(source), oracle(pricing)) == ([], [], [])`, which is true only when no gate reports the idiomatic module, as figure 37 of Deck 201 was witnessed. Witness: `test_the_idiomatic_module_passes_every_gate`.
- Verdict: every arrow composed or witnessed by an assert; the three outcome arrows into "accepted" rest on that one assert, on r23's precedent.

## Numbers in the notes

Decision 7 allows a recorded experiment's result in notes as counts and test names, with the edit that produced it, never a duration. Each experiment below was re-run in the fresh scratch copy (after the witness runs) with the command the chapter gives, then the scratch file was restored from the repository (`cmp` shows no difference in the seven example directories). The chapter's own count line is re-found with `grep -n`. Every count equals the chapter's. The durations pytest prints are not recorded here and no note may quote one.

| Id | Slide | Edit (file) | Edit | Failing tests | Result | mypy | Chapter's count line |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E11-1 | 4 | `src/testing_baseline/engine.py`, `RateEngine.book_best` | replace the last line, `return self._gateways[code].book(consignment)`, with a dictionary comprehension that books every gateway, `{c: gateway.book(consignment) for c, gateway in self._gateways.items()}`, and return the entry for the winner's code | `test_book_best_books_only_the_winner`, `test_book_best_books_the_winner_and_returns_its_reference` | 2 failed, 32 passed | Success: no issues found in 10 source files | `11:315` equal |
| E11-3 | 7 | `tests/test_engine.py`, `test_quote_validity_comes_from_the_injected_clock` | add `assert quote.carrier == "airco"` after the `valid_until` assertion; run alone with `-k test_quote_validity_comes_from_the_injected_clock -s` | `test_quote_validity_comes_from_the_injected_clock`; the output shows `quote_log teardown: quotes.log` printed after the `F` | 1 failed, 33 deselected | not run | `11:342` equal |
| E33-a | 15 | `tests/test_patching.py`, `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` | change the FASTLINE target from `"seams.legacy.request_quote"` to `"seams.fastline.request_quote"` | `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` | 1 failed, 20 passed | Success: no issues found in 9 source files | `33:260` equal |
| E34-1 | 19 | `src/dependency_breaking/parameterised.py` | catch `CarrierTimeoutError` around the FASTLINE call, set the price to `None` in the `except` branch and add `"FASTLINE"` to the `prices` mapping only when a price came back (the error is imported from `dependency_breaking.domain`) | `test_every_step_lets_a_carrier_timeout_fail_the_quote[parameterised]`, `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults` | 2 failed, 40 passed (the 25 table cases pass) | Success: no issues found in 12 source files | `34:227` equal |
| E34-2 | 22 | `tests/conftest.py`, `_FakeCarrierRateEngine` | rename `_airco_price` to `_airco_prices`, keeping `@override` | the five `test_every_step_matches_the_characterisation_table[subclass-...]` cases (`fastline-cheaper`, `airco-cheaper`, `tie-goes-to-airco`, `margin-rounds-half-up`, `grams-truncated`) | 5 failed, 37 passed | exit 1, one error: `tests/conftest.py:99: error: Method "_airco_prices" is marked as an override, but no base method was found with this name  [misc]` | `34:251` equal |
| E35-1 | 24 | `src/fowler_feathers/refactored.py`, `_prices` | round each carrier price half up to the cent before `Money(...)`: wrap both in `.quantize(CENT, rounding=ROUND_HALF_UP)` | `test_the_refactored_engine_matches_the_golden_quotes`, `test_the_golden_quotes_catch_a_refactor_that_changes_rounding[round-builtin-expected1]` | 2 failed, 28 passed (the 22 intent cases pass) | Success: no issues found in 9 source files | `35:191` equal |
| E35-2 | 25 | `src/fowler_feathers/refactored.py`, `_with_margin` | replace `(price.amount * self._margin).quantize(CENT, rounding=ROUND_HALF_UP)` with `round(price.amount * self._margin, 2)` | `test_the_refactored_engine_matches_the_golden_quotes`, `test_inline_golden_values_pin_the_rows_a_reviewer_reads[refactored]`, `test_the_golden_quotes_catch_a_refactor_that_changes_rounding[cent-first-expected0]` | 3 failed, 27 passed (the 22 intent cases pass) | Success: no issues found in 9 source files | `35:216` equal |
| E36-1 | 26 | `src/refactor_or_rewrite/rating.py` | replace `bisect_left` with `bisect_right` in the import and in the call | `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted`, `test_band_limits_include_the_boundary_weight[rewrite]`, `test_the_router_serves_migrated_zones_from_the_rewrite`, `test_with_every_zone_migrated_the_legacy_engine_is_never_called` | 4 failed, 15 passed | Success: no issues found in 9 source files | `36:194` equal |
| E36-2 | 27 | `tests/test_parity.py` | replace the `ACCEPTED_DIFFERENCES` line with `ACCEPTED_DIFFERENCES: list[str] = []` | `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted` | 1 failed, 18 passed | Success: no issues found in 9 source files | `36:208` equal |
| E39-1 | 31 | `src/final_project/desk.py`, `BookingDesk.ship` | delete the line `undo.pop_all()` | `test_a_booking_request_ships_end_to_end` and the four `test_the_acceptance_test_fails_when_a_stage_is_left_out` cases (`rating`, `carrier`, `clearance`, `tracking`) | 5 failed, 18 passed | Success: no issues found in 17 source files | `39:291` equal |
| E39-2 | 32 | `src/final_project/desk.py`, `BookingDesk.ship` | move the three-line `self._events.publish(...)` statement to just after `slot = self._plan.reserve(consignment.id)`, inside the `with` block | `test_a_held_booking_publishes_no_tracking_event[after-commit]` | 1 failed, 22 passed | Success: no issues found in 17 source files | `39:305` equal |
| E40-1 | 36 | `src/review_gate/pricing.py`, `per_kg` | replace the `return` line with `return Money(round(consignment.weight.kilograms * rate, 2))` and drop `ROUND_HALF_UP` from the `decimal` import | `test_the_idiomatic_module_passes_every_gate` | 1 failed, 25 passed | Success: no issues found in 10 source files | `40:241` equal |
| E40-2 | 37 | `src/review_gate/shape.py`, `SHAPE_RULES` | remove the `static_only_class,` line | `test_a_rejected_reply_is_sent_back_with_its_findings`, `test_the_loop_gives_up_after_its_attempts`, `test_the_shape_review_names_the_typed_hierarchy_rules`, `test_each_shape_rule_fires_on_its_minimal_case[static-only-class]` | 4 failed, 22 passed | Success: no issues found in 10 source files | `40:266` equal |

Sentences the notes may use, and no more: "with <the edit>, <n> tests fail and <m> pass, and mypy still exits 0" (or "exits 1 with one [misc] error" for E34-2). E11-3 supports only "in one experiment a failing test that uses a yield fixture printed the fixture's teardown line": the chapter's teardown sentence rests on that experiment alone and nothing here widens it. No notes sentence quotes a duration, a pytest banner or a speed comparison.

Suite sizes the notes may state (each re-counted in the copy, `ast`-counted functions and `--collect-only` cases, and equal to the chapter's own sentence):

| Example | Functions | Cases | Chapter sentence |
| --- | --- | --- | --- |
| 11 | 23 | 34 | `11:298` |
| 33 | 19 | 21 | `33:240` |
| 34 | 13 | 42 | `34:210` |
| 35 | 8 | 30 | `35:170` |
| 36 | 15 | 19 | `36:165` |
| 39 | 19 | 23 | `39:212` |
| 40 | 18 | 26 | `40:221` |
| 42 | 39 | 44 | `42:227` |
| 43 | 26 | 32 | `43:281` |

## Boundary check against Deck 101 and Deck 201

Commands (run from the repository root; `<scratch>` holds the extracted text):

```text
python3 presentation/notes.py presentation/design-patterns-with-python-101-patterns-and-solid.pptx > <scratch>/101-notes.txt
python3 presentation/notes.py --slides presentation/design-patterns-with-python-101-patterns-and-solid.pptx > <scratch>/101-slides.txt
python3 presentation/notes.py presentation/design-patterns-with-python-201-idiomatic-python.pptx > <scratch>/201-notes.txt
python3 presentation/notes.py --slides presentation/design-patterns-with-python-201-idiomatic-python.pptx > <scratch>/201-slides.txt
cat <scratch>/10[12]-*.txt presentation/deck-101.js presentation/deck-201.js > <scratch>/all.txt
grep -cF -- <name or phrase> <scratch>/all.txt     # one count per item below
```

- Test names: all 91 names of Deck 301 (witnesses and notes witnesses) were searched, one `grep -cF` each; the total is 0. Both earlier decks name their tests in words or not at all.

- Code ranges: the 18 ranges, each searched by its exact anchor line (when it has 20 or more characters), by its longest line (stripped) and by every consecutive pair of its lines, plus the in-scope example directories searched in the two builders:

| Slide | Range | Anchor hits | Longest-line hits | Shared consecutive line pairs |
| --- | --- | --- | --- | --- |
| 4 | `tests/test_doubles.py:19-34` | 0 | 0 | 0 |
| 6 | `tests/test_doubles.py:59-66` | 0 | 0 | 0 |
| 7 | `tests/test_environment.py:8-20` | 0 | 0 | 0 |
| 10 | `tests/test_import_modes.py:15-28` | 0 | 0 | 0 |
| 11 | `tests/test_calls.py:81-91` | 0 | 0 | 0 |
| 14 | `src/seams/legacy.py:17-31` | 0 | 0 | 0 |
| 16 | `tests/test_seams.py:64-78` | 0 | 0 | 0 |
| 19 | `tests/test_characterisation.py:67-76` | 0 | 0 | 0 |
| 20 | `src/dependency_breaking/parameterised.py:27-36` | 0 | 0 | 0 |
| 21 | `src/dependency_breaking/rating.py:21-34` | 0 | 0 | 0 |
| 25 | `tests/test_golden.py:66-79` | 0 | 0 | 0 |
| 26 | `src/refactor_or_rewrite/rating.py:30-42` | 0 | 0 | 0 |
| 28 | `src/refactor_or_rewrite/strangler.py:35-46` | 0 | 0 | 0 |
| 30 | `tests/test_acceptance.py:35-49` | 0 | 0 | 0 |
| 31 | `src/final_project/desk.py:43-52` | 0 | 0 | 0 |
| 32 | `src/final_project/desk.py:53-60` | 0 | 0 | 0 |
| 33 | `src/final_project/app.py:11-21` | 0 | 0 | 0 |
| 37 | `src/review_gate/assistant.py:42-56` | 0 | 0 | 0 |

- Builders: `grep -c` of `examples/11-`, `33-`, `34-`, `35-`, `36-`, `39-`, `40-`, `42-`, `43-` in `deck-101.js` and `deck-201.js` totals 0. Code ranges total 0. Anchor lines shorter than 20 characters (`Row(` and `def __init__(` are the generic ones) are not searched by anchor; their longest line and every consecutive pair of non-trivial lines are. A pair is two adjacent stripped lines of the range, each longer than eight characters, found adjacent in the earlier decks' text or builders.

- Claim key phrases (case-insensitive `grep -ciF`), one distinctive phrase per content slide, plus the two sources 301 would otherwise share:

| Slide | Phrase | Hits |
| --- | --- | --- |
| 4 | `named as a claim` | 0 |
| 5 | `refuses something different` | 0 |
| 6 | `create_autospec` | 0 |
| 7 | `monkeypatch.context` | 0 |
| 9 | `strict-markers` | 0 |
| 10 | `import file mismatch` | 0 |
| 11 | `assert_has_calls` | 0 |
| 12 | `Test Spy` | 0 |
| 14 | `enabling point` | 0 |
| 15 | `patch where` | 0 |
| 16 | `importlib.reload` | 0 |
| 17 | `monkeypatched replacement` | 0 |
| 19 | `characterisation table` | 0 |
| 20 | `carriers as parameters` | 0 |
| 21 | `quoters` | 0 |
| 22 | `misspelt override` | 0 |
| 24 | `golden quotes` | 0 |
| 25 | `half to even` | 0 |
| 26 | `bisect_left` | 0 |
| 27 | `accepted differences` | 0 |
| 28 | `shadow` | 0 |
| 30 | `acceptance test` | 0 |
| 31 | `pop_all` | 0 |
| 32 | `after the commit` | 0 |
| 33 | `without cancel` | 0 |
| 35 | `behaviour oracle` | 0 |
| 36 | `static gate` | 0 |
| 37 | `RecordedAssistant` | 0 |
| 38 | `OWASP` | 0 |
| 12 | `Meszaros` | 0 |
| 12 | `xunitpatterns` | 0 |

Result: test names 0, code 0, claim phrases 0. Every result is 0.

Terms that do appear in an earlier deck and that 301 also uses, each at a different angle (none is a claim, test or range of 301):

| Term | Where | 301 angle |
| --- | --- | --- |
| composition root | Deck 101 slides "The composition root" and "An unknown carrier fails at the composition root", Seemann credited | slide 33 leads with the pricing rule and the subscriber chosen at the root, and mypy refusing a gateway without `cancel`; Percival and Gregory credited, not Seemann; the structure test is a note |
| Percival and Gregory | Deck 101 reading list and a notes credit | slides 30, 31 and 33 credit three of its chapters by title; the book is credited, no claim is repeated |
| ExitStack | Deck 201 generator-form notes (entered writers unwinding) | slide 31 uses `ExitStack.callback` as a stack of inverses and `pop_all()` as the commit; "entered writers" and the 201 test never appear |
| pytest, pytest-mock, mypy --strict, uv sync | Deck 101 toolchain table and both closing slides | slide 42 repeats the run-an-example sentence, as all three closing slides do; no tool table |
| fixture, "Negative fixture" | Deck 201 null-object code slide docstring | slide 5 says "the negative case" and shows no docstring |

Verdict: no 301 slide reuses a test name, a code range, a title or a headline claim of Deck 101 or Deck 201. No slide is cut or narrowed for the boundary. D5 repeats this check against the built deck's extracted text.

## Sentences no slide may quote

The surveys named phrases that point to the book or use a workspace term. Re-found now across the ten chapters (`grep -nF`, line numbers current):

| Phrase | Hits (chapter:line) |
| --- | --- |
| `this book` | 4: 11:33, 35:48, 40:152, 44:25 |
| `the book` | 34: 11:37, 34:187, 34:268, 35:34, 36:224, 39:22, 39:26, 39:83, 39:143, 39:147, 39:202, 39:295, 39:321, 40:16 (and 20 more) |
| `this chapter` | 10: 11:12, 11:25, 11:61, 11:391, 33:12, 34:12, 35:12, 36:12, 39:12, 40:12 |
| `chapter titled` | 14: 11:37, 11:61, 11:123, 11:179, 42:106, 42:192, 43:23, 43:25, 43:151, 44:27, 44:51, 44:92, 44:139, 44:141 |
| `member` | 9: 11:67, 11:149, 11:153, 11:318, 42:59, 42:65, 42:67, 42:174, 42:227 |
| `survive` | 4: 36:34, 39:198, 43:37, 43:230 |
| `dissolve` | 1: 43:37 |
| `disambiguat` | 1: 43:37 |
| `for the book` | 2: 40:26, 40:44 |
| `Experiment (b)` | 3: 33:92, 33:216, 33:265 |
| `the next chapter` | 1: 35:232 |
| `this appendix` | 6: 42:13, 43:13, 43:46, 43:84, 44:13, 44:202 |
| `By the end of` | 10: 11:12, 33:12, 34:12, 35:12, 36:12, 39:12, 40:12, 42:13, 43:13, 44:13 |

Specific sentences the plan's inventory fragments sit next to, and that must not reach a slide:

- `11-testing-with-pytest-pytest-mock-and-mypy.md:33`: `grep -nF -- 'The examples in this book follow one method.' _docs/11-testing-with-pytest-pytest-mock-and-mypy.md` hit 1 line(s)
- `40-working-with-ai-and-llm-tools.md:26`: `grep -nF -- 'The three drafts below were written by hand for the book.' _docs/40-working-with-ai-and-llm-tools.md` hit 1 line(s)
- `40-working-with-ai-and-llm-tools.md:158`: `grep -nF -- 'the book'"'"'s usual move for a dependency' _docs/40-working-with-ai-and-llm-tools.md` hit 1 line(s)
- `42-appendix-b-pytest.md:59`: `grep -nF -- 'That'"'"'s why the members carry no pytest table.' _docs/42-appendix-b-pytest.md` hit 1 line(s)
- `34-dependency-breaking-techniques.md:187`: `grep -nF -- 'Each move above has a Python form.' _docs/34-dependency-breaking-techniques.md` hit 1 line(s)
- `33-seams-in-python.md:92`: `grep -nF -- 'Experiment (b) below' _docs/33-seams-in-python.md` hit 1 line(s)
- `43-appendix-c-mocking.md:230`: `grep -nF -- 'A stub'"'"'s count survives' _docs/43-appendix-c-mocking.md` hit 1 line(s)
- `35-fowler-vs-feathers.md:48`: `grep -nF -- 'The table is this book'"'"'s own reading of the sources above' _docs/35-fowler-vs-feathers.md` hit 1 line(s)

## Witness test runs

Date 2026-11-07. The 91 distinct test names above (155 cases once parametrised cases expand) were run by node id in a fresh copy built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <copy>`. In the copy: `rm -rf .venv .venv-ft`, then `uv sync --locked --all-packages` (the real repository was never synced). The copy was made before this file existed, so it holds the tree at `4b7ee31`. The reverse run passes the same node ids in reverse order. Each example imports from the copy, not from the repository (`__file__`, scrubbed):

```text
testing_baseline <copy>/examples/11-testing-with-pytest-pytest-mock-and-mypy/src/testing_baseline/__init__.py
seams <copy>/examples/33-seams-in-python/src/seams/__init__.py
dependency_breaking <copy>/examples/34-dependency-breaking-techniques/src/dependency_breaking/__init__.py
fowler_feathers <copy>/examples/35-fowler-vs-feathers/src/fowler_feathers/__init__.py
refactor_or_rewrite <copy>/examples/36-refactor-or-rewrite/src/refactor_or_rewrite/__init__.py
final_project <copy>/examples/39-final-project/src/final_project/__init__.py
review_gate <copy>/examples/40-working-with-ai-and-llm-tools/src/review_gate/__init__.py
pytest_reference <copy>/examples/42-appendix-b-pytest/src/pytest_reference/__init__.py
mocking_reference <copy>/examples/43-appendix-c-mocking/src/mocking_reference/__init__.py
3.15.2
```

```text
$ uv run pytest --version
pytest 9.2.0
$ uv run pytest --collect-only -q <91 node ids>
155 tests collected
```

| Run | Order | Result |
| --- | --- | --- |
| forward 1 | inventory order | `155 passed` |
| forward 2 | inventory order | `155 passed` |
| reverse | reverse of the inventory order | `155 passed` |
| forward 3 | inventory order, after the twelve experiments restored their files | `155 passed` |

Every run used `uv run pytest -q -p no:cacheprovider <node ids>` from the copy's root with the root configuration (`--import-mode=importlib`, strict markers, `filterwarnings = ["error"]`). The 155 cases are the 91 functions with their parametrised cases: 14 of the 91 functions are parametrised and expand to 78 cases between them; the other 77 run once. No failure, no skip, no warning.

Per-example suites, run in full from each example's directory during the experiments baseline (`34 passed`, `21 passed`, `42 passed`, `30 passed`, `19 passed`, `23 passed`, `26 passed`, `44 passed`, `32 passed` for examples 11, 33, 34, 35, 36, 39, 40, 42 and 43) equal the counts in the chapters.

```text
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_book_best_books_only_the_winner
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_book_best_books_the_winner_and_returns_its_reference
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_a_fake_rejects_unknown_names_and_wrong_signatures
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_a_plain_mock_passes_an_assertion_on_a_misspelled_method
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_spec_rejects_unknown_names_but_not_wrong_signatures
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_autospec_rejects_names_and_signatures
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_static.py::test_mypy_accepts_every_mock_where_a_gateway_is_expected
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_static.py::test_mypy_checks_a_hand_written_fake
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_quote_validity_comes_from_the_injected_clock
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_environment.py::test_validity_reads_the_environment_and_the_context_restores_it
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_carriers_are_asked_in_code_order
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_a_tie_is_broken_by_the_carrier_code_in_the_quote
examples/42-appendix-b-pytest/tests/test_config.py::test_an_unregistered_marker_fails_collection_under_strict_markers
examples/42-appendix-b-pytest/tests/test_config.py::test_a_passing_xfail_fails_the_run_under_strict_xfail
examples/42-appendix-b-pytest/tests/test_config.py::test_an_unknown_option_fails_under_strict_config
examples/42-appendix-b-pytest/tests/test_config.py::test_filterwarnings_error_turns_a_warning_into_a_failure
examples/42-appendix-b-pytest/tests/test_import_modes.py::test_same_basename_test_files_collide_under_prepend
examples/42-appendix-b-pytest/tests/test_import_modes.py::test_importlib_mode_gives_each_test_file_a_unique_name
examples/42-appendix-b-pytest/tests/test_import_modes.py::test_importlib_mode_cannot_import_conftest_by_name
examples/43-appendix-c-mocking/tests/test_calls.py::test_assert_has_calls_checks_a_contiguous_ordered_run
examples/43-appendix-c-mocking/tests/test_calls.py::test_mock_calls_records_calls_in_order_with_call_objects
examples/43-appendix-c-mocking/tests/test_spies.py::test_stub_records_a_callback
examples/43-appendix-c-mocking/tests/test_spies.py::test_spy_keeps_the_real_behaviour_and_records_returns
examples/43-appendix-c-mocking/tests/test_booking.py::test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first
examples/33-seams-in-python/tests/test_patching.py::test_the_legacy_engine_calls_the_real_carrier
examples/33-seams-in-python/tests/test_patching.py::test_patching_the_name_where_it_is_looked_up_replaces_the_carrier
examples/33-seams-in-python/tests/test_patching.py::test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier
examples/33-seams-in-python/tests/test_patching.py::test_a_module_attribute_is_patched_on_the_module_it_belongs_to
examples/33-seams-in-python/tests/test_patching.py::test_unittest_mock_patch_follows_the_same_lookup_rule
examples/33-seams-in-python/tests/test_seams.py::test_patching_a_module_constant_misses_a_default_captured_at_definition
examples/33-seams-in-python/tests/test_seams.py::test_reload_discards_a_patch_and_keeps_old_bindings
examples/33-seams-in-python/tests/test_static.py::test_mypy_does_not_check_a_monkeypatched_replacement
examples/33-seams-in-python/tests/test_static.py::test_mypy_checks_a_direct_assignment_to_a_module_name
examples/33-seams-in-python/tests/test_static.py::test_mypy_accepts_a_misspelt_monkeypatch_target_string
examples/33-seams-in-python/tests/test_static.py::test_mypy_checks_a_fake_passed_to_a_protocol_parameter
examples/34-dependency-breaking-techniques/tests/test_characterisation.py::test_every_step_matches_the_characterisation_table
examples/34-dependency-breaking-techniques/tests/test_characterisation.py::test_the_table_catches_a_step_that_changes_behaviour
examples/34-dependency-breaking-techniques/tests/test_characterisation.py::test_every_step_lets_a_carrier_timeout_fail_the_quote
examples/34-dependency-breaking-techniques/tests/test_steps.py::test_a_parameterised_engine_keeps_the_real_carriers_as_defaults
examples/34-dependency-breaking-techniques/tests/test_static.py::test_mypy_checks_a_fake_passed_as_a_constructor_argument
examples/34-dependency-breaking-techniques/tests/test_steps.py::test_the_function_form_needs_its_quoters
examples/34-dependency-breaking-techniques/tests/test_static.py::test_mypy_reports_a_missing_quoters_argument
examples/34-dependency-breaking-techniques/tests/test_steps.py::test_quote_standard_binds_the_standard_quoters
examples/34-dependency-breaking-techniques/tests/test_steps.py::test_a_misspelt_override_falls_through_to_the_real_carrier
examples/34-dependency-breaking-techniques/tests/test_static.py::test_mypy_reports_a_misspelt_override_only_with_the_override_decorator
examples/35-fowler-vs-feathers/tests/test_intent.py::test_the_intent_rows_pass_every_engine_and_both_rounding_refactors
examples/35-fowler-vs-feathers/tests/test_golden.py::test_the_golden_quotes_catch_a_refactor_that_changes_rounding
examples/35-fowler-vs-feathers/tests/test_golden.py::test_the_golden_file_records_the_legacy_engine
examples/35-fowler-vs-feathers/tests/test_golden.py::test_the_refactored_engine_matches_the_golden_quotes
examples/35-fowler-vs-feathers/tests/test_golden.py::test_round_with_two_digits_rounds_half_to_even_in_the_default_context
examples/36-refactor-or-rewrite/tests/test_parity.py::test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries
examples/36-refactor-or-rewrite/tests/test_parity.py::test_band_limits_include_the_boundary_weight
examples/36-refactor-or-rewrite/tests/test_parity.py::test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted
examples/36-refactor-or-rewrite/tests/test_parity.py::test_the_legacy_engine_prices_an_unknown_zone_as_eu
examples/36-refactor-or-rewrite/tests/test_parity.py::test_the_rewrite_refuses_an_unknown_zone
examples/36-refactor-or-rewrite/tests/test_strangler.py::test_the_router_serves_migrated_zones_from_the_rewrite
examples/36-refactor-or-rewrite/tests/test_strangler.py::test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote
examples/36-refactor-or-rewrite/tests/test_strangler.py::test_with_every_zone_migrated_the_legacy_engine_is_never_called
examples/39-final-project/tests/test_acceptance.py::test_a_booking_request_ships_end_to_end
examples/39-final-project/tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out
examples/39-final-project/tests/test_rollback.py::test_the_undo_runs_in_reverse_order_of_the_steps
examples/39-final-project/tests/test_rollback.py::test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking
examples/39-final-project/tests/test_rollback.py::test_a_full_sailing_books_nothing_with_the_carrier
examples/39-final-project/tests/test_tracking.py::test_a_held_booking_publishes_no_tracking_event
examples/39-final-project/tests/test_tracking.py::test_an_eager_publisher_reports_a_booking_that_was_rolled_back
examples/39-final-project/tests/test_parts.py::test_the_pricing_rule_is_chosen_at_the_composition_root
examples/39-final-project/tests/test_static.py::test_mypy_refuses_a_gateway_without_cancel
examples/39-final-project/tests/test_structure.py::test_only_the_composition_root_names_a_concrete_carrier
examples/40-working-with-ai-and-llm-tools/tests/test_gates.py::test_each_draft_fails_exactly_the_gates_in_the_table
examples/40-working-with-ai-and-llm-tools/tests/test_gates.py::test_the_idiomatic_module_passes_every_gate
examples/40-working-with-ai-and-llm-tools/tests/test_gates.py::test_every_draft_says_it_was_written_for_the_book
examples/40-working-with-ai-and-llm-tools/tests/test_gates.py::test_mypy_and_ruff_pass_the_typed_hierarchy
examples/40-working-with-ai-and-llm-tools/tests/test_gates.py::test_the_static_gate_reports_the_untyped_draft
examples/40-working-with-ai-and-llm-tools/tests/test_gates.py::test_the_oracle_lists_the_half_cent_rows
examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py::test_a_rejected_reply_is_sent_back_with_its_findings
examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py::test_the_loop_stops_at_the_first_accepted_reply
examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py::test_the_loop_gives_up_after_its_attempts
examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py::test_an_unrecorded_prompt_is_refused
examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py::test_the_package_imports_no_network_module
examples/40-working-with-ai-and-llm-tools/tests/test_static.py::test_mypy_refuses_an_assistant_without_reply
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_side_effect_drives_the_timeout_branch
examples/42-appendix-b-pytest/tests/test_config.py::test_the_first_config_file_wins_and_is_not_merged
examples/42-appendix-b-pytest/tests/test_config.py::test_a_member_table_replaces_the_root_filter_and_names_its_own_file
examples/43-appendix-c-mocking/tests/test_doubles.py::test_spec_set_refuses_setting_a_name_the_spec_lacks
examples/43-appendix-c-mocking/tests/test_doubles.py::test_an_assertion_typo_raises_instead_of_passing
examples/43-appendix-c-mocking/tests/test_spies.py::test_resetall_resets_patches_spies_and_autospecs_but_not_stubs
examples/33-seams-in-python/tests/test_patching.py::test_monkeypatch_with_raising_false_creates_a_name_nothing_reads
examples/33-seams-in-python/tests/test_patching.py::test_patch_refuses_a_name_the_module_does_not_have
examples/34-dependency-breaking-techniques/tests/test_steps.py::test_airco_quote_converts_kilograms_and_cents
examples/36-refactor-or-rewrite/tests/test_static.py::test_mypy_requires_the_rewrite_to_take_a_consignment
examples/39-final-project/tests/test_parts.py::test_an_invoice_in_two_currencies_has_no_total
```

## Corrections to the plan

1. Line numbers. D1c edited chapters 11, 33, 40, 42 and 44 (and cards and comments elsewhere), so the `NN.md:line` references in the plan's inventory are the tree at 6c27a6f. Every fragment the census uses was re-found and hits exactly one line, and the sentences the plan quotes are unchanged in wording. The plan lines not present among the census's cited lines are, by slide, a sentence the census did not need or one the plan cited for a note: slide 4: 11:223; slide 5: 11:65, 11:23; slide 6: 11:127; slide 11: 43:103, 43:60, 43:64; slide 12: 44:143, 44:162; slide 14: 33:32; slide 17: 33:221; slide 22: 34:185; slide 24: 35:148, 35:150; slide 27: 36:98; slide 28: 36:149, 36:151; slide 30: 39:70; slide 31: 39:198; slide 33: 39:190; slide 35: 40:46, 40:24.
2. Slide 7: the plan's range `tests/test_engine.py:68-80` is the clock test, which no chapter fence quotes; the acceptance criterion needs each range to be a contiguous run of a fence. The only fence in the chapter's time and environment section is the real-environment test, `tests/test_environment.py:8-20` (13 lines, longest 68 characters, a whole 13-line fence at `11.md:163-177`). The census shows that test, retitles the slide 'Clock and environment', and keeps the clock test, the code-order test and the tie-break test as witnesses of the claim. Disposition: narrowed.
3. Tests. The plan's inventory and notes name 90 distinct tests; the census runs 91. It drops `test_quote_log_teardown_runs_when_the_test_fails`, the pytester witness that owner decision O2 removed and that does not exist (`git grep -n` outside `_plans/` prints nothing), and adds two: `test_a_member_table_replaces_the_root_filter_and_names_its_own_file` (slide 9 notes, the layout the pytest reference sentence describes) and `test_resetall_resets_patches_spies_and_autospecs_but_not_stubs` (slide 11 notes, which the plan names only by its chapter sentence). All 91 are defined once, at column 0.
4. Slide 7 notes: after O2 the teardown sentence rests on experiment three alone (E11-3). The census reproduces only that experiment and the notes may say no more than it shows.
5. Slide 12: a two-row table (Stub, Spy). The plan leaves the rows to the census. The Dummy Object is the qualified paragraph (`44.md:110`): the engine does call the stub (`examples/43-appendix-c-mocking/src/mocking_reference/booking.py:35`), so the row is a note, not a table row. `notify=mocker.stub()` is described as passed to fill the parameter and never read by the test.
6. Slide 17: the plan said the mypy lines are quoted only after P11. `test_mypy_checks_a_direct_assignment_to_a_module_name` now asserts both messages in full (`examples/33-seams-in-python/tests/test_static.py:153-166`), so the notes may quote them.
7. Slide 25: P12 landed. `test_golden.py:131` holds the full line `EU-11: golden FASTLINE 14.84, now FASTLINE 14.85`, so the notes may quote it. The golden mismatch lines are the strings `row: golden X, now Y`; chapter 36's mismatches are row ids. The two are named by concept (see Standalone wording).
8. Slide 33: P15 landed. The mypy `[arg-type]` line must contain `CarrierGateway` (`examples/39-final-project/tests/test_static.py:73`), so the notes may say the message names the gateway Protocol.
9. Slide 36: P16 landed. `test_the_static_gate_reports_the_untyped_draft` asserts each (line, rule) pair (`examples/40-working-with-ai-and-llm-tools/tests/test_gates.py:87-97`): `no-untyped-def` at 11, 16, 24, 27 and 30; `UP037` and `UP045` at 36; `UP037` at 38; `no-untyped-call` at 52. The notes may name them.
10. Slide 37: P17 landed. The package-imports test scans five files for `socket`, `ssl`, `http`, `urllib`, `asyncio` and `subprocess`; the tests run mypy in-process and ruff as a local process. The notes must not say that no test calls a network.
11. Slide 35: the witness `test_every_draft_says_it_was_written_for_the_book` carries the phrase in its identifier. The notes name the test only by identifier and say the drafts were written by hand as stand-ins; the phrase 'for the book' appears in no prose, and `check_decks()` (`\b(the|this) book('s)?\b`) does not match inside the identifier.
12. Figure 33: the smallest label is 6.43 pt, so it clears the 6.3 pt floor by 0.13 pt. Figure 40 is 7.84 pt.
13. Bibliography: the links for Effective Python and Architecture Patterns with Python in `bibliography.html` answer 301 with a redirect to the same book's canonical O'Reilly address (both end at 200). Every other URL, 76 of 78 checked, answers 200 with no redirect. Not a chapter defect; recorded for r25's link-drift pass.
14. The slide-kind counts equal the plan's (1 cover, 1 route slide, 8 dividers, 18 code, 2 figures, 5 tables, 7 bullet slides including the closing slide).

## Standalone wording (the deck stands alone)

The rule: no slide text or note points to a chapter, an appendix or "the book's" text, and none points to another slide by number or position. A grep of the inventory's title, claim and notes columns for the QA step 8 terms (`follow`, `next`, `previous`, `earlier`, `later`, `above`, `below`, `the book`, `this book`, `chapter`, `appendix`, `member`, `slide N`) plus the plan's internal codes, and a reading of every cited sentence, found the items below. No title contains a pointer. Where a name collides across chapters it is named by its concept, one chapter's definitions to a slide.

| # | Slide | Chapter wording | Problem | Standalone wording |
| --- | --- | --- | --- | --- |
| 1 | 2 | the seven themes and the reference, two columns | "in order" and ordinals invite a sequence pointer | Eight bullets, one per section, no ordinals: "Proving it works: a claim, its witness and a check seen failing", "Fixtures and test doubles: settings that refuse silence and what each double records", "Seams in Python: a global name is a seam and a patch must land where it is looked up", "Breaking dependencies: change the structure, keep the behaviour, record the behaviour first", "Refactor or rewrite: intent rows, golden quotes and a rewrite held to parity", "The final project: one booking through every step, undone on a refusal", "Working with AI tools: a reply trusted as far as the checks it has passed", "Reference: sources and books". |
| 2 | 4 | `11.md:33` "The examples in this book follow one method." | "this book" | Start from the next sentence: "A test is named as a claim, so a failure reads as a broken sentence." |
| 3 | 4 | `11.md:33` "A negative fixture is a wrong object ... with an underscore prefix and a docstring" | a chapter term that example 11 does not use as defined (P2 fixed the chapter) | Say "the negative case": the inline plain mock that passes a misspelt assertion. Do not name an underscore-prefixed object or its docstring. |
| 4 | 5 | three `CarrierGateway`s: chapter 11 (`quote`, `book`), chapter 39 (`book`, `cancel`), the mocking reference (`quote(consignment_id, weight_kg)`, `book`) | name collision | "the carrier gateway with quote and book" (slides 5 to 7); "the gateway with book and cancel" (slides 31 to 33); the mocking reference's is not named. |
| 5 | 7 | chapter 11's `RateEngine` (a mapping of gateways, a clock, a validity) | one of six `RateEngine`s | "the engine that takes its gateways, a clock and a validity". |
| 6 | 9 | `42.md:59` "That's why the members carry no pytest table." | "members" is the workspace term | "An example's directory has no pytest table of its own, because a table there would replace the root's." Never "member". |
| 7 | 10 | `42.md:106` "The book's habit follows." and the tests of "the chapter titled Final project" | book and chapter pointers | Quote only "Shared values reach tests through fixtures, which pytest discovers without an import." |
| 8 | 11 | `43.md:230` "A stub's count survives" | "survives" is the three-way label | "A stub keeps its call count after resetall." |
| 9 | 12 | `44.md:149` "The sentence in 'Mocking reference...' that defines a stub says ..." | chapter title as a pointer | "When a test says stub or spy, ask which vocabulary it is in." The two vocabularies are named pytest-mock's and Meszaros's. |
| 10 | 12 | `44.md:110` the qualified Dummy paragraph, and the `Mock Object` contrast row | the book's own column headers ("The book's double") | Notes only: "the stub is used by the engine, and the test never reads it, so Dummy holds only in a qualified sense". |
| 11 | 14 | chapter 33 and 34 `legacy.RateEngine` (identical, no carrier parameters) | one of six `RateEngine`s | "the inherited engine, before any parameter". |
| 12 | 17 | `33.md:221` "The next step is the parameter. [Dependency-breaking techniques ...] makes it."; `33.md:214` "Each cost above" | positional word and chapter pointer | "A parameter replaces the patch." and "Each cost can be measured." |
| 13 | 19 | `34.md:22` "The next move is to change the code so the test needs no patch." | positional word | "A dependency-breaking step changes structure and leaves behaviour alone, and the evidence is a record taken before the step." |
| 14 | 20 | chapter 34 `parameterised.RateEngine` | one of six `RateEngine`s | "the engine with carrier parameters". |
| 15 | 21 | chapter 34 `rating.quote(consignment, /, *, quoters, margin)` | one of two `rating.quote`s | "the quote that takes quoters". |
| 16 | 22 | `34.md:185` "Each move above has a Python form."; `34.md:187` "Feathers's chapter 'Dependency Breaking Techniques' is the catalogue; the book is the place to read each technique in full." | "above", "chapter" and "the book" | "Each move has a Python form." and, as a credit only: "in Working Effectively with Legacy Code, under 'Dependency Breaking Techniques'". The word chapter is never used. |
| 17 | 24 | `35.md:30` "Two books, one activity"; `35.md:48` "The table is this book's own reading" | "book" in two senses, and "this book" | "Two methods, one activity". Fowler's and Feathers's books are named as credits. |
| 18 | 24 | chapter 35 legacy `RateEngine` (keyword carriers) and `refactored.RateEngine` | two of six `RateEngine`s | "the engine whose carriers arrive as keyword parameters" and "the refactored engine". |
| 19 | 25 | chapter 35 `_mismatches` returns `row: golden X, now Y` lines; chapter 36's returns row ids | name collision | "golden mismatch lines" (slide 25) and "parity row ids" (slide 27); never both on a slide. |
| 20 | 26 | chapter 36 band if-chain engine and `rating.quote(consignment, /, *, tariff)` | one of six `RateEngine`s and the second `rating.quote` | "the legacy engine's band chain" and "the quote that takes a tariff". |
| 21 | 27 | `36.md:42` "has its own chapter: Fowler vs Feathers" | chapter pointer | Not quoted; the slide states the decision itself. |
| 22 | 30 | `39.md:79` Percival and Gregory's "TDD in High Gear and Low Gear" | chapter title as a pointer | Credit form: "in Architecture Patterns with Python, under 'TDD in High Gear and Low Gear'". |
| 23 | 30 | `39.md:68` the four stand-ins "that do nothing useful" | could read as null objects (Deck 201) | Notes: "stage removals, each replacing one stage with a stand-in that does nothing", never "null object". |
| 24 | 31 | `39.md:101` "[Command, undo, and command queues] ..." | chapter pointer | Not quoted; the slide says "each step registers the function that reverses it". |
| 25 | 33 | `39.md:26` "The patterns in it are the book's own." | "the book's" | Not quoted. |
| 26 | 35 | `40.md:26` "The three drafts below were written by hand for the book." | "for the book" and "below" | "The three drafts were written by hand as stand-ins for replies." |
| 27 | 35 | `40.md:16` "the book's pattern rules"; `40.md:53` "the structure the pattern chapters recommend" | "book" and "chapters" | "the four shape rules" and "the structure the shape rules recommend". |
| 28 | 37 | `40.md:158` "the book's usual move for a dependency is a Protocol with a fake behind it" | "the book's" | "A dependency on a model client goes behind a Protocol with a recorded fake, like any other." |
| 29 | 38 | `40.md:152` "A sidebar in this book has one form ... Every chapter from ... through ..., 34 chapters" | "this book", chapter counts | Only: "a prompt can state the checks before any reply exists, and the review line says what to ask when a diff moves an answer the gate holds." |
| 30 | 38 | `11.md:228` and the pattern-chapter sidebars: "An assistant may ..." | decision 8 (the sidebar form stays as approved; the deck carries none of those sentences) | Not carried; the slide states what a request leaves open ("Write the pricing strategies" leaves the shape and the rounding open). |
| 31 | all | the word "member" in the workspace sense (`_run` docstrings, Appendix B) | workspace term | "an example", "the example's directory". |
| 32 | all | "dissolves", "survives", "disambiguates" and inflections | three-way-split labels | Plain verbs: "is replaced by", "keeps", "has two meanings". |
| 33 | all | internal codes (P1 to P21, F1, F2, K1 to K3, V1, D0 to D6, E-ids) | plan or census labels | Never reach the builder; experiment ids are census keys only. |

No title needs a change. The Boundary table's own "(slides 33, 35 to 38)" style references and every `NN.md:line` stay in the plan and the evidence and never reach the builder's text.

## Cuts and narrowings

Cuts: none. Every claim has a witness test or a recorded chapter sentence that passes, and no chapter now contradicts one.

Narrowings: slide 7 (range, title and one claim, see Corrections item 2). Slide 12 carries two table rows. No claim is stretched: the teardown sentence on slide 7 is the one experiment (E11-3) and no wider; the network sentence on slide 37 is the package-imports test and no wider; the Dummy Object row is qualified.

Facts that bound the notes (all re-checked): no number in any note is a duration; every count is one of the twelve experiments above or a suite size; the only statements about models are the two OWASP quotations on slides 35 and 38 and the hand-written-stand-ins sentence.
