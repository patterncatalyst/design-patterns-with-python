---
title: "Evidence: r25 QA sweep"
output: false
render_with_liquid: false
---

# r25 QA sweep

## C3a: whole-book quoted-output re-run (2026-11-08)

Method. A fresh copy of the tree (`git ls-files` plus untracked, copied with `cp --parents`), `.venv` and `.venv-ft` removed, `uv sync --locked --all-packages`, and `__file__` of an example package checked to sit inside the copy. Every command ran in the copy with its output passed through `python3 scripts/host_ids.py filter`, the copy path replaced by `<repo>`, and durations normalised. A block matches when its lines equal the scrubbed output, allowing the omissions its prose states (the banner, `note:` lines, a trailing `Found N errors` line, `...` for elided test rows). Experiment blocks were produced by making the edit the prose names in a second fresh copy, running the stated filter, and restoring the file (`diff -r` of the touched member against the repo was clean afterwards). The `<string>:N: error` blocks come from mypy runs inside the member tests: a pytest plugin recorded every `mypy.api.run` output during a full-suite run (1,407 passed), and each block's lines were checked against those outputs.

Result: 185 fenced output blocks in 47 docs, 181 match and 4 were fixed (19:313, 21:256, 30:219, 30:236). The three prose items the r25 evidence left open were also re-run (below).

### Fixes

- `30:219` and `30:236` (chapter 30). The quoted `AssertionError` lines were `tests/test_lookup.py:195` and `:218`. TS2 added a test above them, so they are now `:201` and `:224`. The chapter produced the blocks with two edits in a deliberately altered copy, `__dir__` deleted from `TrackingHistory` (experiment one) and the allow-list check and its `raise` deleted from `__getattr__` (experiment two). Both were repeated in a fresh copy with the stated filter and mypy command. Experiment one now prints `2 failed, 39 passed` and experiment two `4 failed, 37 passed`, because TS2 also raised the suite from 40 to 41 cases (27 test functions). The fences, the sentence "27 test functions and 41 cases" and "All 41 cases pass" were corrected. No card or README repeats these numbers.
- `19:313` (chapter 19, experiment two, adding `cancel` to `CarrierGateway`). TS3 made `test_mypy_reports_an_implementor_missing_a_primitive` assert `note:     insure`. With `cancel` added, mypy lists `cancel, insure` on one note line, so that test fails as well. The fence now shows two failures (`2 failed, 33 passed`, the extra `E` line, `tests/test_static.py:129` and the second `FAILED` line), and the sentence after it says two failures and why.
- `21:256` (chapter 21, session block). The closing mypy line said `9 source files`; the member has 8 (4 sources and 4 test modules), which the experiment blocks below it already say. Corrected to 8.

### TS2 cause removed (chapter 30, line 120)

In a scratch copy, `test_deepcopy_fails_with_a_type_error_when_the_loader_answers_every_name` was given a loader that raises `AttributeError` (the cause, a loader that answers every name, removed). The test then fails with `RecursionError: maximum recursion depth exceeded`, raised from `__getattr__` while `copy._reconstruct` calls `hasattr(y, '__setstate__')` on the bare instance. That is the outcome the sentence before it gives for a loader that knows one field, so the `30.md:120` sentence stands: the `TypeError` comes from the loader answering every name, and with that removed the recursion returns. No narrowing was needed.

### Known items

- Chapter 5's quoted run (the `pytest -v` block at `05:193` and the mypy block at `05:225`) is byte-identical to a fresh run after TS1's explicit ids.
- Chapters 19 and 20: the quoted `tests/test_static.py:96` and the listed `test_static.py` node ids match a fresh run after TS3 and TS4; the only change needed was 19:313 above.
- Planner items left for C3a: 18's "twenty fresh interpreters" (the script in `lazy-import-threads.md` re-run in a fresh copy: 20 of 20 runs loaded the table once, 8 callers, quote 12.00), and 41's `.venv-ft` ruff findings (in a copy without `.git`, with `.venv-ft` removed from `extend-exclude`, `ruff check .` reported 2 findings in `.venv-ft/bin/activate_this.py` and `ruff format --check .` reported 1 file to reformat; with the exclude, both pass).
- Benchmark reports `37:148` and `37:172` equal the recorded `bench/gil_bench.out.txt` and `gil_bench.ft.out.txt` byte for byte; live runs reproduced labels, rows and structure, with timings and ratios differing as the chapter says.
- Chapter 17's block at `17:295` lists mypy errors in an order that depends on mypy's cache state; the doc's order is the warm-cache order.

### QO1 record (from C2d)

41 appendix A, line 43, re-run in a fresh copy on 2026-11-08: `uv sync --locked --all-packages` leaves 55 distributions; `uv sync --locked` leaves 13 and removes all 42 workspace members; `uv run --no-sync pytest -q examples/00-prerequisites` fails collection with `ModuleNotFoundError: No module named 'consignments'`. The stale-lock block (`41:50`) and the duplicate-`conftest` line (`41:202`) match too.

### Decision 9, branches kept

- `examples/43-appendix-c-mocking/tests/test_patching.py:32`: the `if before is None` branch sits in the arrange phase of a parametrised test and chooses between `delenv` and `setenv` to put the environment in the starting state the parameter names. There is one assertion and one path through the verification, so the branch adds no conditional logic to what the test checks. Kept.
- `examples/35-fowler-vs-feathers/tests/test_golden.py:97`: the `--update-golden` branch writes the golden file and skips. It is the golden-master workflow that chapter 35 teaches, so removing it would remove the lesson. Kept.
- "Test seam" wording: kept, listed under "Checked, not a defect" in the plan.

### Per-block table

| doc:line | command | result |
|---|---|---|
| 00:168 | check-prereqs, pytest -v, mypy in example 00 | match |
| 00:186 | check-prereqs, pytest -v, mypy in example 00 | match |
| 00:208 | check-prereqs, pytest -v, mypy in example 00 | match |
| 02:171 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 03:180 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 03:212 | `uv run mypy --strict src tests` in the member | match |
| 05:132 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 05:193 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 05:225 | `uv run mypy --strict src tests` in the member | match |
| 06:66 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 06:180 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 06:210 | `uv run mypy --strict src tests` in the member | match |
| 06:220 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 07:74 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 07:194 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 07:232 | `uv run mypy --strict src tests` in the member | match |
| 07:240 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 07:251 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 07:260 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 08:188 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 08:233 | `uv run mypy --strict src tests` in the member | match |
| 08:241 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 08:253 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 08:263 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 09:50 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 09:138 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 09:153 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 09:226 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 09:279 | `uv run mypy --strict src tests` in the member | match |
| 09:287 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 09:294 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 09:304 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 09:313 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 10:91 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 10:205 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 10:243 | `uv run mypy --strict src tests` in the member | match |
| 10:251 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 10:261 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:141 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 11:147 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 11:187 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:193 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 11:199 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:247 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 11:294 | `uv run mypy --strict src tests` in the member | match |
| 11:304 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:322 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:333 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:349 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:360 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 11:370 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 12:125 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 12:131 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 12:137 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 12:144 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 12:152 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 12:207 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 12:251 | `uv run mypy --strict src tests` in the member | match |
| 12:259 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 12:266 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 12:280 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 13:81 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 13:87 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 13:120 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 13:206 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 13:242 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 13:288 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 13:304 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 14:69 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 14:122 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 14:128 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 14:134 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 14:170 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 14:224 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 14:282 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 14:296 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 15:103 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 15:246 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 15:293 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 15:305 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 16:102 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 16:108 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 16:124 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 16:173 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 16:211 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 16:257 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 16:273 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 17:67 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 17:111 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 17:178 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 17:221 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 17:281 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 17:295 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 18:76 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 18:181 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 18:215 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 18:262 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 18:274 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 19:46 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 19:114 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 19:211 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 19:243 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 19:296 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 19:313 | scratch-copy edit named in the prose, then the filter and mypy command given there | fixed |
| 20:155 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 20:187 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 20:222 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 20:290 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 20:308 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 21:256 | `uv run pytest -v` then `mypy --strict src tests` in the member | fixed |
| 21:322 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 21:335 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 22:49 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 22:239 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 22:288 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 22:303 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 23:87 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 23:95 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 23:117 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 23:170 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 23:204 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 23:266 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 23:278 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 24:173 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 24:233 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 24:251 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 25:61 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 25:88 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 25:146 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 25:198 | `explain(STANDARD_TARIFF)` | match |
| 25:204 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 25:210 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 25:240 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 25:306 | `explain(STANDARD_TARIFF)` | match |
| 25:318 | `explain(STANDARD_TARIFF)` | match |
| 26:237 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 26:300 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 26:324 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 27:164 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 27:223 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 27:289 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 27:306 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 28:171 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 28:227 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 28:245 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 29:196 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 29:255 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 29:272 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 30:219 | scratch-copy edit named in the prose, then the filter and mypy command given there | fixed |
| 30:236 | scratch-copy edit named in the prose, then the filter and mypy command given there | fixed |
| 31:182 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 31:194 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 32:163 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 32:198 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 33:201 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 33:242 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 33:256 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 33:271 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 33:294 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 34:219 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 34:235 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 35:179 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 35:199 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 36:141 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 36:172 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 36:202 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 37:148 | benchmark report | match |
| 37:172 | benchmark report | match |
| 37:221 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 37:268 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 37:287 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 38:35 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 38:102 | mypy.api.run output captured from the member tests (`uv run pytest -p capmypy`) | match |
| 38:214 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 38:226 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 39:214 | `uv run pytest -v` then `mypy --strict src tests` in the member | match |
| 39:250 | `uv run mypy --strict src tests` in the member | match |
| 39:263 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 39:299 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 40:228 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 40:235 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 40:249 | scratch-copy edit named in the prose, then the filter and mypy command given there | match |
| 41:50 | uv sync / mypy from the root, edit named in prose | match |
| 41:202 | uv sync / mypy from the root, edit named in prose | match |
| 46:199 | `uv run pytest -q` and mypy in the member | match |

## C3b integration (2026-11-08)

### Gates (real repo, branch release/r25 at b365523)

| Gate | Result |
| --- | --- |
| `bash scripts/verify.sh` | `1407 passed in 164.46s`, `verify: all steps passed` (ruff check, ruff format, mypy per member and on scripts all clean) |
| `uv run ruff format --check .` | `667 files already formatted` |
| `uv run ruff check .` | `All checks passed!` |
| `uv run python scripts/validate.py` | `validate: 0 error(s), 6 warning(s)` (the six owner-accepted appendix word-floor warnings) |
| `validate.py --claims` | every row resolved (legacy, yes); 0 unresolved |
| `validate.py --self-test` | `self-test: ok` |
| `python3 scripts/host_ids.py check` | `887 text file(s), 0 hit(s)` |
| ban scan (`--exclude .venv-ft`) | `total: 0 matching lines (0 ban-tier)` |
| idiom scan over `examples spikes scripts` | 69 ban-tier hits, all `print()` in CLI and benchmark scripts whose output is their purpose (host_ids.py 19, the three `bench/` scripts of examples 21 and 37 and the spike 29, validate.py 8, render and generate scripts 3); 2 watch hits kept |
| `bash scripts/site-build.sh` | `site-build: ok (Gemfile.lock unchanged)` (md5 identical before and after, also after the CSS change) |
| `presentation/render-png.sh --check --deck 101, 201, 301` | `same` for all 13 figures (6, 5 and 2) |
| Legibility | `check_figure_legibility` runs inside `validate.py`; 0 errors, so all 41 figures pass the 8 px floor at 982 px |

### Link sweep

- 208 URL tokens in the reader files (`_docs`, `_examples`, `_parts`, `bibliography.html`, `index.html`, `examples.html`, `README.md`, `examples/*/README.md`) reduce to 199 distinct pages; 13 carry a fragment.
- 198 end at 200 with no redirect. The one extracted non-URL is the Liquid text `https://github.com/{{`, not a link.
- 2 redirect, both expected and not links: `https://astral.sh/uv/install.sh` (the uv installer command URL, one hop to `releases.astral.sh`) and the clone URL `https://github.com/patterncatalyst/design-patterns-with-python`, which the README writes with `.git` (one hop to the repository page; 200).
- 0 non-200. All 13 fragments resolve (`id=` or `name=` found on the fetched page).
- No link edited.

### Figure breakout and overflow, measured

Method: the built `_site` served from a local port; headless Firefox (no webdriver installed) loaded a harness page that opened each of the 47 docs in an iframe 390 and 1280 px wide and posted `documentElement.scrollWidth`, `clientWidth` and `innerWidth` back. The iframe has a classic 12 px scrollbar, so the viewport for layout is 378 and 1268 px; a page scrolls sideways when `scrollWidth` exceeds `clientWidth`.

| Chapter | 390 px: scrollWidth / clientWidth | 1280 px: scrollWidth / clientWidth |
| --- | --- | --- |
| 19 | 378 / 378 | 1268 / 1268 |
| 21 | 378 / 378 | 1268 / 1268 |
| 25 | 378 / 378 | 1268 / 1268 |
| 31 | 378 / 378 | 1268 / 1268 |
| 34 | 378 / 378 | 1268 / 1268 |
| 37 | 378 / 378 | 1268 / 1268 |

Before the fixes below, 10 of 47 docs overflowed at 390 px (none at 1280 px, and none of the figure chapters above): 03, 35, 45, 46, 42 (wide tables, up to 617 px), 29 (the long title `__init_subclass__`), 11, 39, 44 (tables and the title) and 07.

- `assets/css/site.css`: at 640 px and below a table in the chapter body becomes `display: block; max-width: 100%; overflow-x: auto`, so it scrolls inside its own box; headings in the body and the chapter `h1` break long identifiers (`overflow-wrap: anywhere`, `min-width: 0`).
- Chapter 07 was not CSS. Line 169 had a code span with leading spaces (`` `   EUR 12.50` ``) that kramdown did not close, so the paragraph rendered with stray backticks and the later code spans inverted into prose. The sentence now reads "right-aligning `EUR 12.50` in twelve columns", which `test_repr_str_and_format_serve_different_readers` asserts (`f"{price:>12}" == "   EUR 12.50"`). No other built page has a stray backtick in a paragraph.
- After the fixes: 0 of 47 docs overflow at 390 px or at 1280 px (94 measurements).

### Chapter 17, block 17:295

- The block is the output of experiment two, whose command is `uv run mypy --strict src tests | grep -v "^ "` in a scratch copy.
- In a fresh copy (new `uv sync`, no cache) the six errors come out in the doc's order, with or without `pytest -q` first (two runs each, plus three cold runs). If the reader has already run the chapter's own `mypy` on the clean code (the Build, run, observe step), the cache is warm and the list comes out with `tests/conftest.py:202` before `tests/test_prototype.py`. The doc's order is the cold one, and C3a's note that it was the warm one is the other way round.
- Decision: the fence stays as it is and the command now carries `--no-incremental`, which gives the doc's order from any cache state (checked in the warm state too). The sentence says why. The count of six errors and the prose after the fence are unchanged.

## C4a reconciliation (2026-11-08)

### Legacy rows, re-witnessed (decision 6)

The 32 rows (1 to 5, 17 to 27, 31 to 46) each name the tests, `run:` file or `source:` URL that witness the chapter's sentence today; the old free-text "how to verify" cell and the old status note moved into the row's history. The 190 distinct test cases named by rows 1 to 5, 17 to 46 and 437 onward were run from the repo root with `--import-mode=importlib`, three times forward and once with the node ids reversed: `190 passed` each time. Rows 5 and 26 were `open` and are `verified (r25)`. Row 27 was `open` and is `adjusted (r25)`: it said "in most cases" and "unnecessary", which chapter 9 doesn't claim, so it now reads that `Optional` plus mypy dissolves Null Object where absence must be handled and that a null object stays where doing nothing is the correct answer. No chapter sentence needed narrowing: each of the 32 claims is stated in its chapter at or below what its tests assert (checked by reading the sentence beside each test).

Row 4 says Singleton has two meanings; chapter 3's own example witnesses the module form (`test_module_is_one_instance_for_every_importer`), and the class forms are witnessed by chapter 18's `test_every_form_gives_each_caller_the_same_rates` and `test_borg_instances_share_state_but_are_distinct_and_unequal`.

Row 23 (no timed sleep in the async tests): a grep for `sleep(`, `time.`, `perf_counter` and `random` over the tests of examples 37 and 38 finds one use, the `asyncio.sleep(0)` yield at `examples/38-*/tests/test_stowage.py:51`, which its docstring names as a yield to the loop and `conftest.py` names as the only one. No timed sleep, clock or random appears in either member's tests.

### Rows 437 onward

- 452: all six Python fences of chapter 2 were compared line by line with the sources and tests of example 3: 0 lines missing.
- 456: `pytest --collect-only` in example 30 reports 41 tests from 27 test functions; the full suite run now gives `41 passed`.
- 457: in a scratch copy of `test_loop.py` with `await asyncio.sleep(0)` inserted before `quote(consignment)`, the test fails: `At index 1 diff: 'tracking polled' != 'rating finished'`.
- 458, 461, 463 and 460 are the C3a, C2d and C3b records above.

### VA5 mutation proof

`CLAIMS_FIRST_ENFORCED` is 1 and the legacy branch is gone. In a scratch copy of `validate.py`: (a) with the skip condition made `r.row < 10**9`, `--self-test` exits 1 with "claim errors include row 46 with no token and every unresolved row" and "claim row 1 without a token is an error"; (b) with the constant set back to 47, it exits 1 with "claims are enforced from row 1" and the same two. The real file passes.
