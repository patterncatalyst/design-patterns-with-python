---
title: "r06 plan: chapters 12-13 (Part 5, Strategy and Template Method)"
order: 6
output: false
render_with_liquid: false
---

# r06: chapters 12-13, Strategy and Template Method

Opus-planned 2026-11-04. Branch `release/r06`. This file is the source of truth for r06 scope, criteria and status. Executors never edit it; the orchestrator updates the status board. There's no toolchain work this iteration: Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged, and `uv.lock` changes only because two members are added.

## User decisions (2026-11-04, confirmed by the owner)

Owner ruling on decision 1 (2026-11-04): there was never a ban on comparison code; CLAUDE.md now
says comparison code is allowed when it teaches, as the exception, tested against the same
behaviour table, with the idiomatic code as the lesson. So the class-per-strategy design stays a
test fixture that runs the shared table, and chapter 12 MAY show one short excerpt of it beside the
`RATE_RULES` dict (at most one comparison excerpt, inside the six-excerpt limit), with the dict of
functions taught as the answer. Decisions 2 and 3 proceed as recommended.

Original wording (recommendations as written by the planner):

1. **Keep the class-per-strategy design as a test-only negative fixture in chapter 12.** Domain row 12 requires it ("A class-per-strategy design needs three classes and a registry to pass the same table of cases a dict of functions passes"), and reconciliation row 1 (r02) moved "type and line counts" into this chapter. CLAUDE.md bans classic "before" code written for contrast. The way through is the r05 `_NullGateway` precedent:
   - `_PricingStrategy(ABC)` plus three subclasses and a `_STRATEGIES` dict live only in `tests/test_behaviour_table.py`.
   - The fixture runs the same behaviour table as `RATE_RULES`, and an `ast` count reports four strategy classes against one.
   - Prose reports the test results and never excerpts the fixture.
   - There are no line counts, because line counts depend on formatting.
   
   **Recommend: yes.** If you say no, drop tests 15-16, mark row 1 `adjusted` ("counts dropped as contrast code"), and change domain row 12's failing-test column.
2. **Put the chapter 13 ABC form in `src/`, delegating to the function form.** Both forms are needed to show the straddle (domain row 13: "dissolve (hooks); survive (ABC where steps share state)"):
   - `declare_customs(consignment, *, hooks)` is the function form.
   - `CustomsDeclarer(ABC)` holds shared state (`classification`, `schedule`), shared default steps (`classify`, `duty`) and one abstract primitive (`extra_documents`). Its `@final declare` hands its own bound methods to `declare_customs` as hooks.
   - The skeleton exists once, every invariant check is seen by both forms, and `NetherlandsDeclarer` and `GermanyDeclarer` are a family that shares code and state.
   
   **Recommend: yes.** The alternative is an ABC in a test fixture only. That leaves "survives" without reader-facing code and weakens the bucket claim the three-way split chapter already promised ("the Template Method chapter says where that line falls").
3. **No new books: GoF and *Fluent Python* 2nd ed. are the books both chapters lean on.**
   - Both are already in `bibliography.html` and in hub `books.yml` with `design-patterns-with-python` in `referenced_by`, so **no hub PR this iteration**.
   - Norvig's "Design Patterns in Dynamic Languages" is rejected because its claim is a comparison between languages, which the thesis rules out.
   - Kerievsky's *Refactoring to Patterns* (Form Template Method) isn't in the bibliography and would need a verification, a bibliography row and a hub entry for one sentence.
   
   **Recommend: yes.** If you want Kerievsky, add step G0b: verify the edition, add the `bibliography.html` row and the hub `books.yml` entry, and open the hub PR at G7.

## Planning evidence

All runs were read-only, from `/tmp` (outside the repo):
- Runtime: `~/.local/bin/python3.15 -I -c ...` (3.15.2).
- mypy: `uv run --no-project --python 3.15.2 --with mypy==2.4.1 python -I -c "mypy.api.run(['--strict','--cache-dir','/dev/null','--no-error-summary','-c',SNIPPET])"`.

Each item below becomes a test or a reconciliation row. The plan relies on nothing else. Anything not listed here, including every experiment output, is a prediction to be quoted as observed.

Runtime (3.15.2):
- `partial(per_kg, rate=2).__name__` raises `AttributeError: 'functools.partial' object has no attribute '__name__'`.
- A frozen dataclass rule instance: `'ZoneRate' object has no attribute '__name__'`.
- A lambda's `__name__` is `<lambda>`. A closure's is `rule`, with qualname `mk.<locals>.rule`.
- `partial(f, rate=2) == partial(f, rate=2)` is `False`, while `.func` and `.keywords` compare equal. `repr(partial)` contains a memory address, so it is never quoted or asserted.
- Two equal closures compare `False`.
- A frozen slotted dataclass with `__call__` and a `frozendict` field compares equal and hashes equal. Its repr is stable: `Tariff(per_kg_by_zone=frozendict({'EU': Decimal('0.80')}))`.
- An unbound partial fails only when called: `per_kg() missing 1 required keyword-only argument: 'rate'` (the positional form reads `missing 1 required positional argument: 'tariff'`).
- `frozendict(...)["zone"] = 2` raises `'frozendict' object does not support item assignment`. A missing key raises `KeyError('nope')`.
- `Decimal("28.85") * Decimal("0.50")` is `14.4250`: `ROUND_HALF_UP` gives `14.43` and `ROUND_HALF_EVEN` gives `14.42`. That's the rounding case where the two modes differ.
- `typing.final` on a method: a subclass override runs at runtime and `Base.declare.__final__ is True`.
- A frozen slotted kw_only dataclass with a function default works (`default is no_docs`). A missing required field raises `CustomsHooks.__init__() missing 1 required keyword-only argument: 'classify'`.
- Protocol default bodies: an explicit subclass inherits `extra_documents` (returns `()`). A structural class doesn't: `'Structural' object has no attribute 'extra_documents'`.

mypy 2.4.1:
- A registry `Mapping[str, PricingRule] = frozendict({...})` checks each entry as `[dict-item]`, with `expected "str": "Callable[[Consignment], Money]"`:
  - wrong return: `"Callable[[Consignment], Decimal]"`;
  - extra keyword-only parameter: `"def per_kg(consignment: Consignment, *, rate: Decimal) -> Money"`;
  - lambda body: `[dict-item]` plus `Incompatible return value type (got "Decimal", expected "Money")  [return-value]`;
  - class instead of instance: `"type[ZoneRate]"`.
- The keyword form `frozendict(w=weight_of)` gives `[arg-type]` instead, so src uses the dict-literal form.
- A valid registry (function, `partial(per_kg, rate=...)`, `ZoneRate(...)` instance) exits 0.
- `partial(per_kg)`, which binds nothing, is **accepted** in the registry (exit 0). `partial(per_kg, rat=...)` is `[call-arg]` `Unexpected keyword argument "rat" for "per_kg"; did you mean "rate"?`. This is the same gap the ISP/DIP chapter documents.
- `Hooks()` without a required field: `Missing named argument "classify" for "CustomsHooks"  [call-arg]`. A two-parameter duty function: `Argument "duty" to "CustomsHooks" has incompatible type "Callable[[Money, Decimal], Money]"; expected "Callable[[Money], Money]"  [arg-type]`. The chapter 13 duty signature takes lines, so the executor re-verifies the exact text against the real signature.
- A defaulted dataclass field typed `Callable[...]` is called as a plain callable (`reveal_type` gives `tuple[str, ...]`).
- A structural class missing a Protocol member that has a default body: `[assignment]` with `"Structural" is missing following "DestinationRules" protocol member:` / `extra_documents`. The note appears because the Protocol has two members and one is missing (r05 correction to claim 53). An explicit subclass is accepted.
- Overriding a `@final` method: `Cannot override final attribute "declare" (previously declared in base class "Declarer")  [misc]`.
- An override that skips the base step (no `super()` call) exits 0 with empty output.
- `frozendict[str, Decimal]` as a frozen dataclass field type-checks, and `hash(t)` is accepted.

Sources fetched 2026-11-04. The prose agents re-fetch them and quote exactly. The fetch tool paraphrases punctuation, so the page text wins.
- functools docs, partial Objects (https://docs.python.org/3/library/functools.html): "partial objects are like function objects in that they are callable, weak referenceable, and can have attributes. There are some important differences. For instance, the `__name__` and `__doc__` attributes are not created automatically." `Placeholder` is "Added in version 3.14" (rejected below).
- typing docs, `@typing.final` (https://docs.python.org/3/library/typing.html#typing.final): "Decorator to indicate final methods and final classes." and "There is no runtime checking of these properties." Changed in 3.11: sets `__final__` to `True`.
- PEP 544, "Explicitly declaring implementation" (https://peps.python.org/pep-0544/): "In this case a class could use default implementations of protocol members." and "The default implementations cannot be used if the subtype relationship is implicit and only via structural subtyping". The final punctuation is to be confirmed on the page.
- *Fluent Python* 2nd ed. chapter titles, verified from the book's official code repository README (https://github.com/fluentpython/example-code-2e): "Design Patterns with First-Class Functions" and "Inheritance: For Better or For Worse". O'Reilly pages return 403. The O'Reilly MCP confirms the edition (2022, ISBN 9781492056348) but can't show the table of contents.
- GoF: the O'Reilly MCP confirms the book (Addison-Wesley, 1994, ISBN 0201633612) but can't open the text. **No GoF sentence is quoted.** The credit goes by pattern name and the catalogue's standard sections (Intent, Applicability, Consequences, Implementation), which the forces chapter already introduces. The terms "hook operations", "primitive operations" and "Hollywood principle" are bracketed: use a term only if a prose agent verifies it in the book; otherwise describe it in the book's own words without the label.

Repo facts:
- Chapters 12-13 are `kind = "pattern"`, `has_example = true`, `status = "stub"`, part 5 (`_parts/05-selecting-and-varying-behaviour.md`, slug `selecting-varying-behavior`, left as is). They are the **first pattern-kind chapters to be drafted**: `validate.py` enforces `SPINE["pattern"]` (Learning objectives, Why this matters, Build, run, observe, When not to use it, For deeper coverage) and exactly one `ai-sidebar`.
- The stubs have `## How it works` placeholders and "Draft pending" descriptions.
- Reconciliation rows run 1-64, so r06 adds 65-74. Row 1 (ch2) defers Strategy's counts to this chapter. `CLAIMS_FIRST_ENFORCED = 47`.
- `_data/diagrams.yml` has twelve entries; r06 makes fourteen.
- **Run-token collision.** `validate.py --claims` resolves `run: <id>` against every `r*-plan.md` steps table. Ids `0`-`7`, `1a`-`1c`, `A0`-`A6` and `S*` are already `done` in earlier plans, so an r06 step reusing one would resolve without proof. r06 step ids are `G0`-`G7` (with `G1a`, `G1b`), which appear in no other plan.
- **Test-name collision.** Claim tokens resolve against `def test_*` across all members. Several names already repeat across members (`test_weight_must_be_positive_and_finite`, `test_money_addition_needs_one_currency`). Every test name cited in rows 65-74 must be new across `examples/*/tests` (criterion 3).
- The mypy-API helper (r04/r05 shape) writes its own `mypy.ini` (`mypy_path` only) and doesn't pass `--warn-unreachable`. Neither chapter needs it.
- Already taught, so not repeated (each gets a pointer by title, at most one sentence):
  - The PricingRule alias excerpt and the def/lambda/partial slot witness: "What 1994 assumed, and what Python dissolves" and "The three-way split: dissolve, survive, disambiguate".
  - The `RateStrategy` vs `PricingRule` naming argument: "Naming patterns for teams and AI assistants".
  - The three shapes for rating (function over a tariff, rule callables, a `RateCalculator` Protocol): "Patterns as decisions under forces".
  - A new rule arriving as data in a mapping, and the limit when a rule's signature must change: "SRP, OCP, and LSP in Python".
  - `partial` injection and mypy not checking a partial's assignment: "ISP, DIP, and dependency injection without a framework".
  - Callback Protocols with `/`, Protocol vs ABC, `[abstract]` at construction, explicit Protocol subclasses returning `None`, `typing.override`: "Protocol, duck typing, and structural typing with mypy". Its last paragraph already points to "Template Method and the function alternative" for the shared skeleton.
  - The evidence method, negative fixtures, deletion tables and the mypy-API helper: "Proving it works: pytest, pytest-mock, and mypy".
  - The `declare_customs`/`CustomsHooks` order witness: "The three-way split".
- Later chapters whose ground must not be taken:
  - "Shortcut patterns: dict dispatch, function tables, and EAFP" (dispatch tables in general);
  - "Mediator and Chain of Responsibility" (customs **clearance** stages, restricted commodities);
  - "Decorator the pattern vs @decorator the syntax, and Proxy" and "Decorators done right" (registration decorators);
  - "Command, undo, and command queues".

## What is new in each chapter

**Chapter 12 (dissolves).** The earlier chapters show that a `PricingRule` slot takes a function. This chapter covers what changes once there are several rules and a caller picks one:
- **Selection by name.** A read-only `frozendict` registry. An unknown name is a `RatingError`, and the quote records the key.
- **Configured rules.** A `partial`, a closure and a frozen dataclass with `__call__` all fill the slot. They differ in what an audit can recover: `__name__`, value equality, hashing and a stable repr. That links back to the reproducible-quote force.
- **What mypy checks per registry entry.** It checks the return type, extra parameters, a lambda's body and a class registered where an instance belongs. It doesn't check a partial that binds nothing.
- **Where a strategy has to be an object.** Hidden state breaks reproducibility, and several operations call for a Protocol (pointer).
- **The class-per-strategy fixture** passes the same table (decision 1).

**Chapter 13 (straddles).** The three-way split chapter shows only the hooks shape. This chapter adds:
- required hooks against hooks with defaults (dataclass fields), with mypy and runtime both enforcing the required ones;
- invariant steps the hooks can't remove;
- Protocol defaults reaching only explicit subclasses (PEP 544);
- the ABC form for a family that shares state and code, delegating to the same skeleton (decision 2);
- the forgotten `super()` call, which mypy accepts;
- `typing.final`, which mypy enforces and the runtime only marks.

## Approach

- **Thesis wording.** Chapter 12 uses "a feature resolves the force without the pattern's structure" once and names Strategy as dissolving. Chapter 13 says Template Method straddles: the hook structure dissolves, and the inheritance form survives where a family of variants shares state and code across steps.
- **Credit.**
  - Both chapters credit GoF where the pattern is introduced.
  - Chapter 12 credits Ramalho's *Fluent Python* chapter "Design Patterns with First-Class Functions" for the treatment of strategies as functions. Nothing from his example is used: his domain is order discounts, and the book's is rating.
  - Chapter 13 cites the inheritance chapter by title for further reading only.
- **Domain names** come from `_plans/shipping-domain-model.md`.
  - Chapter 12 (Rating): `PricingRule`, `RateQuote`, `Tariff`, `RatingError`, `Money`, `Weight`, `Consignment`, `ConsignmentId`.
  - Chapter 13 (Documentation): `CustomsDeclaration`, `Commodity`, `ConsignmentId`, `Money`, and the existing supporting name `CustomsHooks`.
  - New supporting names, recorded in domain rows 12-13 at G0: `RATE_RULES`, `ZoneRate`, `per_kg`, `flat_rate`; `declare_customs`, `DeclarationLine`, `CustomsError`, `CustomsDeclarer`, `NetherlandsDeclarer`, `GermanyDeclarer`, `lookup_tariff_code`, `schedule_duty`, `no_extra_documents`, `SINGAPORE`, `NETHERLANDS`, `EU_CLASSIFICATION`, `EU_SCHEDULE`. No new domain area. Carrier codes don't appear. Tariff codes, duty rates and zone rates are illustrative, and the prose says so once, as the SRP/OCP chapter does.
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/12-strategy-the-callable` (project `strategy-callable`, package `strategy_callable`);
  - `examples/13-template-method-and-the-function-alternative` (project `template-method`, package `template_method`).
- **mypy witnesses** copy the r05 helper (own `mypy.ini`, `--strict`, `--cache-dir os.devnull`, `--no-error-summary`). Each asserts exit status, an exact `_codes()` set and one or two substrings, never line numbers. Typed ignores in tests are static witnesses (`warn_unused_ignores` under strict).
- **Negative witness rule.** Every check in src has a test that fails when the check is deleted, and the deletion tables (G1a, G1b) name the test **and say why it sees the deletion**. That fixes the r05 tie-break lesson.
- **Global state.** No `mock`, `mocker`, `monkeypatch`, `print(` or wall clock. No module-level mutable tables (every registry and table is a `frozendict`). `filterwarnings = ["error"]` stays active.

Rejected:
- `functools.Placeholder` (new in 3.14): mypy 2.4.1 support wasn't verified, and keyword binding covers every case here.
- Norvig's dynamic-languages talk (a comparison between languages).
- A "best of all strategies" selector (too close to *Fluent Python*'s example).
- Strategy registration by `@decorator` (belongs to the decorator chapters).
- An if-chain "before" version (pointer to the dict-dispatch chapter instead).
- Line counts (formatting-dependent).
- A Protocol-with-defaults in src (a test fixture is enough; nothing in src needs it).
- Restating the `[abstract]` mypy message (the Protocol chapter owns it; the runtime refusal is re-witnessed only because it guards this member's `@abstractmethod`).
- Customs clearance stages (Chain of Responsibility chapter).

## Per-chapter spec

### Chapter 12: Strategy: the callable (pattern, has_example = true, bucket: dissolves)

Thesis: Strategy's force, a caller choosing an algorithm at run time without knowing which one it holds, is intact. Its structure (strategy interface, concrete strategy classes, context) dissolves into a callable type alias, a read-only mapping and a call. What's left to design is selection, configuration and what a quote records about the rule that priced it.

Sections (about 2,300 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - a quote that records `rule.__name__` and crashes on the first configured rule;
   - a registry holding the class `ZoneRate` where an instance belongs, which prices a consignment as a `ZoneRate` object;
   - a pull request adding an abstract `PricingStrategy`, three subclasses and a factory to do what a mapping of three callables does.
3. Figure plus one paragraph (~60).
4. `## The force that remains` (~330):
   - GoF credited for Strategy, by Intent and Consequences, in the book's own words. Nothing quoted.
   - Bucket: dissolves, using the thesis wording once.
   - One sentence pointing to "What 1994 assumed, and what Python dissolves" for the alias and the def/lambda/partial slot. No re-excerpt.
   - New material: the class-per-strategy negative fixture passes the same behaviour table (test 15), and the `ast` count gives four strategy classes against one (test 16). The one class that remains, `ZoneRate`, earns its place in the next section.
   - Ramalho's chapter "Design Patterns with First-Class Functions" credited for the same treatment.
5. `## Choosing a rule by name` (~280). Excerpt `RATE_RULES` and `quote`:
   - The registry is a 3.15 `frozendict` (test 8).
   - An unknown name is a `RatingError`, not a bare `KeyError` (test 7).
   - The quote records the key it was given (test 6), so a disputed invoice names its rule.
   - One pointer to "Shortcut patterns: dict dispatch, function tables, and EAFP" for dispatch tables in general. One sentence pointing to "SRP, OCP, and LSP in Python" for adding a rule as data without editing the registry.
6. `## Configured rules: a partial, a closure, or a rule object` (~380):
   - `per_kg` needs a rate, so it's bound with `partial`. `ZoneRate` needs a tariff, so it's a frozen dataclass with `__call__`.
   - A table (rows not counted) with columns Form | Fills a `PricingRule` | `__name__` | Equal when configured the same | Hashable | Stable repr. Rows: function, lambda, closure, `partial`, frozen dataclass with `__call__`. Built from tests 10-12 and the planning evidence.
   - The functools docs quoted exactly on `__name__` and `__doc__`.
   - Consequence: record the registry key, and use a rule object when two quotes must be compared by the rule that priced them.
   - One sentence pointing to "ISP, DIP, and dependency injection without a framework" for `partial` injection.
7. `## What mypy checks in a strategy slot` (~300). Fresh output from test 17, covering four entry errors plus the valid control, and test 18:
   - each registry entry is checked against `PricingRule`, including a lambda's body and a class registered where an instance belongs;
   - a `partial` that binds nothing passes and fails at call time (test 14), and a misspelt keyword is caught;
   - one sentence pointing to "Protocol, duck typing, and structural typing with mypy" for the callback Protocol form with `/`, used when keyword parameters, overloads or attributes matter.
8. `## When a strategy has to be an object` (~220):
   - Hidden state: `_make_loyalty_discount` prices the same consignment differently on the second call (test 13), which breaks the reproducible-quote force. State goes in as an argument or not at all.
   - A rule that must also explain or validate has several operations, which is the `RateCalculator` case. One pointer to "Patterns as decisions under forces".
   - Here the class is still optional, but the Protocol becomes the contract.
9. `## When not to use it` (~170): a single rule called from one place (a function, no registry); a registry consulted with a literal key everywhere; rules that need different inputs, which is a signature problem and not a selection problem; a rule object written where a function would do. Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written strategies.** An assistant asked for "the Strategy pattern" may write an abstract `PricingStrategy` with a subclass per rule and a factory, record `rule.__name__` in a quote, register a class where an instance belongs, or keep a running counter inside a rule. Check: does each rule fill a `PricingRule` slot as a callable; is the registry read-only, with an unknown key raised as a domain error; does the quote record the key rather than an introspected name; does every partial bind what its rule needs; does a rule's result depend only on its argument.</blockquote>

   Each check maps to tests 15, 7-8, 6 and 10, 17 (class case), 14 and 18, and 13. No claim about how often assistants do this.
10. `## Build, run, observe` (~220 plus output). Commands as in the Protocol chapter. Experiments, each in a scratch copy, one change, reverted:
    - (a) In `RATE_RULES`, replace `ZoneRate(TARIFF)` with `ZoneRate`. Expected: the member mypy run reports `[dict-item]` naming `"type[ZoneRate]"`, and `test_each_registered_rule_prices_the_behaviour_table[zone]` fails. Quote both as observed.
    - (b) Replace `partial(per_kg, rate=Decimal("1.20"))` with `partial(per_kg)`. Expected: mypy reports success, and the `[per-kg]` case fails with `TypeError` naming `'rate'`. Quote as observed.
11. `## For deeper coverage` (~130): GoF (Strategy); Ramalho, *Fluent Python* 2nd ed., "Design Patterns with First-Class Functions"; the functools docs (partial Objects); PEP 695 (`type` statement); PEP 814 (`frozendict`); the dataclasses docs (frozen, hash); Slatkin, *Effective Python* 3rd ed. by topic (closures, `partial`); the bibliography link.

Figure `12-strategy-the-callable` (vertical):
- Top accent box: `quote(consignment, "zone")`.
- Then `RATE_RULES` ("read-only, selected by name"), fanning to three light boxes: `flat_rate` "function", `partial(per_kg, rate=...)` "bound configuration", `ZoneRate(TARIFF)` "rule object: equal, hashable".
- They join at `RateQuote` "records rule name and price".
- Side box: "unknown name: RatingError".
- No numbers in the SVG.

Caption draft (40 words with prefix): "Figure 12.1: One quote, three rules in a slot. The caller names a rule, the read-only registry returns a callable, and quote records the name with the price, whether the rule is a function, a partial or a frozen dataclass."

### Chapter 13: Template Method and the function alternative (pattern, has_example = true, bucket: straddles)

Thesis: Template Method fixes an order of steps and lets variants supply some of them. The hook structure dissolves into a function that takes hooks: required hooks have no default, optional hooks have one, and invariant steps sit outside every hook. The inheritance form survives where a family of variants shares state and code across several steps. There, the template is `@final` and delegates to the same skeleton, and a forgotten `super()` call is the failure that mypy can't see.

Sections (about 2,300 prose words, max 2,500; at most six excerpts):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): a destination subclass overrides a preparation step, forgets `super()`, and issues a declaration with no commodity lines that mypy accepts (tests 11 and 18); a hook bag where every hook defaults, so a missing classification passes silently; a Protocol given default bodies on the assumption that matching classes inherit them.
3. Figure plus one paragraph (~60).
4. `## An order variants can't change` (~300):
   - GoF credited for Template Method [primitive/hook operation terms and the Hollywood principle only if verified, else described without labels].
   - Bucket: straddles. Hooks dissolve; the inheritance form survives where state is shared.
   - One sentence pointing to "The three-way split: dissolve, survive, disambiguate" for the hooks shape. One sentence noting that each hook is a strategy in the sense of "Strategy: the callable", so this chapter doesn't re-teach callables.
5. `## The function form: fixed steps and hooks` (~330). Excerpt `declare_customs` and `CustomsHooks`:
   - Fixed steps: refuse a consignment without commodities; classify each commodity; total the declared value in one currency; assess duty; put the commercial invoice first, then the extra documents.
   - Tests 1-6. `classify` and `duty` have no default, so a missing hook is a `TypeError` at construction and `[call-arg]` under mypy. `extra_documents` defaults to `no_extra_documents`. A wrong hook signature is `[arg-type]` (test 19).
   - Fresh output for the two static cases.
6. `## Defaults in a Protocol reach only subclasses` (~220):
   - PEP 544 quoted exactly ("Explicitly declaring implementation").
   - Fixture `_DocumentHooks(Protocol)` with a default `extra_documents`: an explicit subclass gets `()`, and a structural match raises `AttributeError` at runtime and is `[assignment]` with the missing-member note under mypy (tests 12 and 20).
   - Conclusion: defaults that should apply to every caller belong on dataclass fields or in the template function, not in a Protocol body.
   - One pointer to "Protocol, duck typing, and structural typing with mypy" for explicit Protocol subclasses being nominal.
7. `## When steps share state: the ABC form` (~380). Excerpt `CustomsDeclarer` (`<!-- fmt:off -->` wrapped):
   - `__init__` takes `classification` and `schedule`; `classify` and `duty` are concrete defaults reading them; `extra_documents` is abstract; `@final declare` passes the bound methods to `declare_customs`.
   - `NetherlandsDeclarer` and `GermanyDeclarer` differ only in country and documents.
   - The template and the hooks give the same declaration (test 8). Every invariant test runs on both forms (`[hooks|template]`), so the skeleton exists once.
   - The line: one destination, or steps that share nothing, means hooks. A family whose steps read the same state and share code means a class. Binding the same schedule into three hooks for each destination is the sign the family has become one.
8. `## Keeping the skeleton fixed` (~280):
   - The classic failure: `_OpenDeclarer`, whose invariant lives in an overridable `check`, and `_ForgetfulDeclarer`, whose override skips `super()`, issues a declaration with no lines (test 11). mypy exits 0 (test 18).
   - `typing.final` on `declare`: mypy reports `[misc]` on an override (test 17), and the runtime runs the override and only sets `__final__` (test 10). The typing docs are quoted exactly ("There is no runtime checking of these properties.") with a PEP 591 link.
   - `@final` is a marker for the checker, applied with decorator syntax. No pointer to the Decorator chapters is needed.
9. `## When not to use it` (~170): one variant (write the function); hooks that are all optional (nothing is fixed, so it's a pipeline of strategies); steps whose order varies by destination (a list of stages, not a template); one pointer to "Mediator and Chain of Responsibility" for clearance stages. Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written templates.** An assistant may write an abstract base class whose subclasses must remember to call `super()`, put an invariant inside an overridable step, give a Protocol default bodies and expect matching classes to inherit them, or leave the template method open to override. Check: is the skeleton a function or a `@final` method; does every invariant sit outside the hooks; does each required hook lack a default, so construction fails without it; is a Protocol default reached only through an explicit subclass; does a test fail when a variant skips a step.</blockquote>

   Each check maps to tests 10 and 17, 3-5, 2 and 19, 12 and 20, and 11.
10. `## Build, run, observe` (~220 plus output). Experiments:
    - (a) Delete `@final` from `CustomsDeclarer.declare`. Expected: the member mypy run reports an unused `type: ignore` on the `_OverridingDeclarer` fixture, and `test_final_marks_the_template_without_enforcing_it` and `test_mypy_rejects_overriding_the_final_template` fail. Quote as observed.
    - (b) Delete the no-commodities guard in `declare_customs`. Expected: both cases of `test_a_declaration_needs_at_least_one_commodity` fail. Quote the observed error.
11. `## For deeper coverage` (~130): GoF (Template Method); PEP 544; PEP 591 and the `typing.final` docs; the `abc` docs; the dataclasses docs (`kw_only`, defaults); Ramalho, *Fluent Python* 2nd ed., "Inheritance: For Better or For Worse"; Slatkin, *Effective Python* 3rd ed. by topic; the bibliography link.

Figure `13-template-method-and-the-function-alternative` (vertical):
- Top accent box: `declare_customs(consignment, hooks=...)`.
- Five step boxes in order. Invariant steps (darker light fill) are "refuse no commodities", "total in one currency" and "commercial invoice first". Hook steps are "classify each commodity" and "assess duty", with a side box "extra_documents (default: none)".
- Left feed: `CustomsHooks` "functions per destination" (SINGAPORE).
- Right feed: `CustomsDeclarer` "@final declare, shared schedule" with `NetherlandsDeclarer` and `GermanyDeclarer` below, feeding bound methods into the same top box.
- Ends at `CustomsDeclaration`.

Caption draft (39 words with prefix): "Figure 13.1: One customs skeleton, two ways to vary it. declare_customs fixes the order and the invariant steps and takes hooks for the rest; CustomsDeclarer keeps the same skeleton final and lets a family of destinations share its schedule."

Citations, both chapters: verify each before writing; apply the bracketed fallbacks; quote no sentence unless it was checked on a fetched page; no comparison between languages.

## Example spec

### `examples/12-strategy-the-callable` (project `strategy-callable`, package `strategy_callable`)

`pyproject.toml` in the r05 shape (`requires-python = ">=3.15"`, no `[tool.*]`).

- `domain.py`:
  - `ConsignmentId = NewType`.
  - `Weight(kilograms: Decimal)`, frozen slotted, finite and positive, `ValueError` otherwise.
  - `Money(amount: Decimal, currency: str)`.
  - `Consignment(id, weight, zone: str, destination: str)`, frozen slotted kw_only.
  - `RateQuote(consignment_id, rule: str, price: Money)` and `RatingError`.
- `rules.py`:
  - `type PricingRule = Callable[[Consignment], Money]`.
  - `flat_rate(consignment) -> Money` returns 25.00 EUR.
  - `per_kg(consignment, *, rate: Decimal) -> Money`, quantised to cents with `ROUND_HALF_UP`.
  - `Tariff(per_kg_by_zone: frozendict[str, Decimal], currency: str = "EUR")`, frozen slotted.
  - `ZoneRate(tariff: Tariff)`, frozen slotted, `__call__(self, consignment, /) -> Money`: it raises `RatingError(f"no tariff for zone {zone!r}")` for an unknown zone and quantises `ROUND_HALF_UP`.
  - `TARIFF = Tariff(frozendict({"EU": Decimal("0.50"), "ASIA": Decimal("1.50")}))`.
  - `RATE_RULES: Mapping[str, PricingRule] = frozendict({"flat": flat_rate, "per-kg": partial(per_kg, rate=Decimal("1.20")), "zone": ZoneRate(TARIFF)})`, in dict-literal form so mypy reports `[dict-item]` per entry.
  - `quote(consignment, rule_name: str, *, rules: Mapping[str, PricingRule] = RATE_RULES) -> RateQuote`: `try`/`except KeyError` raises `RatingError(f"no pricing rule named {rule_name!r}") from None` and records `rule_name`.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: `consignment` (EU zone, `"NLRTM"`), `asia_consignment` (`"SGSIN"`).

`test_behaviour_table.py` (fixtures `_PricingStrategy(ABC)` with abstract `price`, `_FlatRateStrategy`, `_PerKgStrategy`, `_ZoneRateStrategy`, `_STRATEGIES: dict[str, _PricingStrategy]`; module-level `_BEHAVIOUR_TABLE` of `pytest.param(key, kg, zone, expected, id=key)`):
1. `test_each_registered_rule_prices_the_behaviour_table[flat|per-kg|zone]`
15. `test_a_class_per_strategy_passes_the_same_table[flat|per-kg|zone]`
16. `test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one`: parses `inspect.getsource(rules)` and this module with `ast` and counts `ClassDef`s that define `__call__` or `price`. Expected: 1 (`ZoneRate`) and 4.

`test_rules.py`:
2. `test_rules_round_half_up_to_cents[per-kg|zone]`: the zone case is 28.85 kg at 0.50 giving `14.43` (`HALF_EVEN` would give `14.42`); the per-kg case is chosen by the executor so that `HALF_EVEN` differs as well.
3. `test_zone_rate_refuses_a_zone_without_a_tariff`
4. `test_a_rated_weight_must_be_positive_and_finite`

`test_selection.py`:
6. `test_a_quote_records_the_rule_that_priced_it`
7. `test_an_unknown_rule_name_is_a_rating_error`: `pytest.raises(RatingError, match="no pricing rule named 'express'")`.
8. `test_the_rule_registry_is_read_only`: `# type: ignore[index]`; `TypeError` matching `does not support item assignment`; `not isinstance(RATE_RULES, dict)`.

`test_configured.py` (fixtures `_quote_by_function_name`, `_make_loyalty_discount` closure with `nonlocal` counter):
10. `test_partials_and_rule_objects_have_no_name`: `AttributeError` for the `per-kg` and `zone` entries through `_quote_by_function_name`; `flat_rate.__name__ == "flat_rate"`; a lambda gives `"<lambda>"`.
11. `test_a_partial_has_no_value_equality`: `!=`, but `.func` and `.keywords` are equal.
12. `test_a_rule_object_compares_and_hashes_by_value`: `==`, equal `hash`, `repr(...)` starts with `"ZoneRate(tariff=Tariff("`.
13. `test_a_rule_with_hidden_state_is_not_reproducible`
14. `test_an_unbound_partial_fails_only_when_called`: `TypeError` matching `missing 1 required keyword-only argument: 'rate'`.

`test_static.py`:
17. `test_mypy_checks_each_registry_entry[valid|wrong-return|extra-parameter|lambda-body|class-not-instance]`:
    - exit 0 with empty output for `valid`;
    - then `{"dict-item"}`, `{"dict-item"}`, `{"dict-item", "return-value"}`, `{"dict-item"}`;
    - every error case contains `expected "str": "Callable[[Consignment], Money]"`, and the last also contains `"type[ZoneRate]"`.
18. `test_mypy_checks_partial_keywords_but_not_a_missing_binding[missing|misspelt]`: exit 0 with empty output, then `{"call-arg"}` with `did you mean "rate"`.

Also `README.md` and the card `_examples/12-strategy-the-callable.md` (`order: 12`, eyebrow "Selecting behaviour · Strategy"). No `mock`, `monkeypatch`, `print(`, `Optional`, `TypeVar(` or `isinstance` in `src/`.

Deletion table (G1a). Each row: the check, how it's deleted, the failing test, and why that test sees it.

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `Weight` finite/positive | `__post_init__` removed | 4 | constructs `Weight(Decimal(0))` and `Weight(Decimal("NaN"))` and expects `ValueError` |
| `per_kg` quantise | return the raw product | 2[per-kg] | expected amount has two places; the raw product has more |
| `ROUND_HALF_UP` (both rules) | default rounding | 2[per-kg], 2[zone] | each case is chosen where `HALF_EVEN` gives a different cent |
| `ZoneRate` unknown zone | plain index | 3 | expects `RatingError`; gets `KeyError` |
| `quote` unknown name | plain index | 7 | expects `RatingError`; gets `KeyError` |
| `quote` records the key | records `""` | 6 | asserts `quote(...).rule == "zone"` |
| `frozendict` registry | `dict` | 8 | assignment no longer raises; `isinstance(..., dict)` |
| `frozen=True` on `ZoneRate` | `frozen` dropped | 12 | `__hash__` becomes `None`, so `hash()` raises |
| `rate=` binding | `partial(per_kg)` | 1[per-kg] | calling the rule raises `TypeError` |
| `ZoneRate(TARIFF)` instance | the class | 1[zone], member mypy | price is a `ZoneRate`, not `Money`; `[dict-item]` |

### `examples/13-template-method-and-the-function-alternative` (project `template-method`, package `template_method`)

- `domain.py`:
  - `ConsignmentId`.
  - `Money(amount, currency)` with a same-currency `__add__` that raises `CustomsError("mixed currencies: EUR and SGD")`.
  - `Commodity(description: str, value: Money)`.
  - `Consignment(id, destination: str, commodities: tuple[Commodity, ...])`, kw_only.
  - `DeclarationLine(description, tariff_code, value)`.
  - `CustomsDeclaration(consignment_id, country, lines, declared_value, duty, documents)`, frozen slotted.
  - `CustomsError`.
- `hooks.py`:
  - `type Classifier = Callable[[Commodity], str]`, `type DutyRule = Callable[[tuple[DeclarationLine, ...]], Money]`, `type DocumentRule = Callable[[Consignment], tuple[str, ...]]`.
  - `no_extra_documents(consignment, /) -> tuple[str, ...]`.
  - `CustomsHooks(*, country: str, classify: Classifier, duty: DutyRule, extra_documents: DocumentRule = no_extra_documents)`, frozen slotted kw_only.
  - `lookup_tariff_code(table, commodity, country) -> str` raises `CustomsError(f"no tariff code for {description!r} in {country}")`.
  - `schedule_duty(lines, *, schedule: Mapping[str, Decimal]) -> Money` sums per-line percentage duty, quantised `ROUND_HALF_UP`, and raises `CustomsError(f"no duty rate for {code}")`.
  - `declare_customs(consignment, *, hooks) -> CustomsDeclaration` runs the fixed steps in the order of the chapter spec.
  - `EU_CLASSIFICATION`, `EU_SCHEDULE`, `SG_CLASSIFICATION` (all `frozendict`, illustrative).
  - `SINGAPORE` (no `extra_documents`, so it takes the default) and `NETHERLANDS` (`partial(schedule_duty, schedule=EU_SCHEDULE)`, extra documents).
- `declarer.py`: `CustomsDeclarer(ABC)`:
  - `country: ClassVar[str]`;
  - `__init__(self, *, classification, schedule)`;
  - `classify` uses `lookup_tariff_code`; `duty` uses `schedule_duty`;
  - `@abstractmethod extra_documents`;
  - `@final declare(self, consignment)` returns `declare_customs(consignment, hooks=CustomsHooks(country=self.country, classify=self.classify, duty=self.duty, extra_documents=self.extra_documents))`.
  
  Subclasses `NetherlandsDeclarer` (`"NL"`, same documents as `NETHERLANDS`) and `GermanyDeclarer` (`"DE"`), each with `@override extra_documents`.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: `consignment` (`"NLRTM"`, laptops and cotton t-shirts in EUR); a `declare` fixture parametrized `hooks` (`partial(declare_customs, hooks=NETHERLANDS)`) and `template` (`NetherlandsDeclarer(classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE).declare`).

`test_hooks.py`:
1. `test_declare_customs_runs_its_steps_in_order`: recording hooks give `["classify:laptops", "classify:cotton t-shirts", "duty", "extra_documents"]`.
2. `test_a_hook_left_out_takes_its_default`: SINGAPORE documents are `("commercial invoice",)`.
3. `test_a_declaration_needs_at_least_one_commodity[hooks|template]`
4. `test_a_declaration_in_two_currencies_is_refused[hooks|template]`
5. `test_the_commercial_invoice_is_always_first[hooks|template]`
6. `test_a_required_hook_cannot_be_left_out`: `# type: ignore[call-arg]`; `TypeError` matching `missing 1 required keyword-only argument: 'classify'`.
7. `test_an_unclassified_commodity_is_refused[hooks|template]`
21. `test_duty_rounds_half_up_to_cents`
22. `test_a_tariff_code_without_a_duty_rate_is_refused[hooks|template]`

`test_template.py` (fixtures `_OpenDeclarer` and `_ForgetfulDeclarer(_OpenDeclarer)`, self-contained with an overridable `check`; `_OverridingDeclarer(NetherlandsDeclarer)` overriding `declare` with `# type: ignore[misc]`; `_NoDocumentsDeclarer(CustomsDeclarer)` without `extra_documents`):
8. `test_the_template_and_the_hooks_give_the_same_declaration`
9. `test_a_declarer_without_its_documents_cannot_be_built`: `# type: ignore[abstract]`; matching `abstract method 'extra_documents'`.
10. `test_final_marks_the_template_without_enforcing_it`: `CustomsDeclarer.declare.__final__ is True` and the override's result is returned.
11. `test_a_subclass_that_skips_the_base_check_declares_nothing`: an empty consignment gives a declaration with `lines == ()`, and `_OpenDeclarer` itself raises.
23. `test_two_destinations_share_the_schedule_and_differ_in_documents`: NL and DE give equal `duty` and `lines` and different `documents`.

`test_protocol_defaults.py` (fixtures `_DocumentHooks(Protocol)`, `_ExplicitHooks(_DocumentHooks)`, `_StructuralHooks`):
12. `test_protocol_defaults_reach_only_explicit_subclasses`

`test_static.py`:
17. `test_mypy_rejects_overriding_the_final_template`: `{"misc"}`, `Cannot override final attribute "declare"`.
18. `test_mypy_accepts_an_override_that_skips_the_base_step`: exit 0, empty.
19. `test_mypy_checks_hooks_at_construction[missing-required|wrong-signature]`: `{"call-arg"}` with `Missing named argument "classify" for "CustomsHooks"`; `{"arg-type"}` with `Argument "duty" to "CustomsHooks" has incompatible type`.
20. `test_mypy_requires_every_protocol_member_for_a_structural_match`: `{"assignment"}`, `is missing following` and `extra_documents`.

Test numbering follows the prose references; the gaps (13-16) are intentional.

Also `README.md` and the card (`order: 13`, eyebrow "Selecting behaviour · Template Method"). No `mock`, `monkeypatch`, `print(`, `super()` in `src/`, or `isinstance` in `src/`.

Deletion table (G1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| no-commodities guard | removed | 3[hooks], 3[template] | the template delegates to `declare_customs`, so both cases run the same guard |
| `Money.__add__` currency | plain add | 4[both] | expects `CustomsError` naming both currencies |
| invoice first | invoice dropped or appended last | 5[both] | asserts `documents[0] == "commercial invoice"` |
| step order | `extra_documents` called first | 1 | recorded order differs |
| `lookup_tariff_code` missing | `table[...]` | 7[both] | `KeyError`, not `CustomsError`; one function serves both forms |
| `schedule_duty` missing rate | `schedule[...]` | 22[both] | as above |
| `ROUND_HALF_UP` in duty | default rounding | 21 | case chosen where `HALF_EVEN` differs |
| `extra_documents` default | default removed | 2, member mypy | SINGAPORE construction raises `TypeError`; `[call-arg]` |
| `classify` without default | default added | 6 | `pytest.raises(TypeError)` sees nothing raised; mypy reports the unused ignore |
| `@final` | removed | 10, 17, member mypy | `__final__` missing; snippet exits 0; unused `[misc]` ignore |
| `@abstractmethod` | removed | 9 | the incomplete declarer builds; mypy reports the unused `[abstract]` ignore |
| bound-method delegation | `duty=lambda lines: Money(0, ...)` | 8 | declarations differ in `duty` |

## Steps and status

Step ids are `G*` because `--claims` resolves `run:` tokens against every plan's steps table.

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| G0 | This plan file. PDP-112a-c and 113a-c `active` in `iteration-plan.md` (dated note). Reconciliation rows 65-74 `open`, and a row 1 note "counts witnessed by row 65 (r06)". Domain-model rows 12-13 updated with the example-spec names (row 12: `Mapping[str, PricingRule]` over a 3.15 `frozendict`, `ZoneRate`, and the failing test as decision 1 settles it; row 13: `CustomsHooks`, `declare_customs`, `CustomsDeclarer` with `@final declare`, Protocol defaults as a test fixture). ch12/13 stub `description` lines written. Decisions recorded | - | done |
| G1a | ch12 member, card, README; three green runs; the deletion table above, each row run in a scratch copy | G0 | done |
| G1b | ch13 member, card, README; one `uv lock` after both members (sequenced); three green runs; deletion table | G1a | todo |
| G2 | Witness results into rows 65-74 (claims audit resolves). A failed witness changes the thesis before prose. Any message differing from Planning evidence goes in "Corrections after the build" | G1b | todo |
| G3 | Two figures, specs `diagrams/specs/12-*.py` and `13-*.py`, `_data/diagrams.yml` (single owner; `section: "Ch. 12"`/`"Ch. 13"`); figures 00-11 unchanged | G2 | todo |
| G4 | ch12-13 `status = "drafted"` (`kind` stays `pattern`) | G3 | todo |
| G5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly, runs the experiments in scratch copies, quotes fresh output filtered by `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table (claim, then test, run or source URL) | G3, G4 | todo |
| G6 | Opus validation; up to two repair rounds | G5 | todo |
| G7 | PR, `ci-ok` green, ask the user before merge; tag r06.x; notes-only release. No hub PR (decision 3) | G6 | todo |

Reconciliation rows (step G0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 65 | 12 | A class-per-strategy design passes the same behaviour table as the read-only registry of callables, declaring four strategy classes where the callable design declares one | `test_each_registered_rule_prices_the_behaviour_table`, `test_a_class_per_strategy_passes_the_same_table`, `test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one` |
| 66 | 12 | Rules are selected by name from a read-only `frozendict`; an unknown name is a `RatingError`; the quote records the key | `test_a_quote_records_the_rule_that_priced_it`, `test_an_unknown_rule_name_is_a_rating_error`, `test_the_rule_registry_is_read_only` |
| 67 | 12 | A partial and a rule object have no `__name__`; a partial has no value equality; a frozen dataclass rule compares, hashes and prints by value; rounding is half up | `test_partials_and_rule_objects_have_no_name`, `test_a_partial_has_no_value_equality`, `test_a_rule_object_compares_and_hashes_by_value`, `test_rules_round_half_up_to_cents`, `source: https://docs.python.org/3/library/functools.html` |
| 68 | 12 | mypy checks each registry entry (return, extra parameter, lambda body, class for instance) and a partial's keywords, but accepts a partial that binds nothing, which fails only when called | `test_mypy_checks_each_registry_entry`, `test_mypy_checks_partial_keywords_but_not_a_missing_binding`, `test_an_unbound_partial_fails_only_when_called` |
| 69 | 12 | A rule with hidden state prices the same consignment differently on a second call | `test_a_rule_with_hidden_state_is_not_reproducible` |
| 70 | 13 | `declare_customs` runs fixed steps in order that no hook can remove; required hooks have no default (runtime `TypeError`, mypy `[call-arg]`), an omitted optional hook takes its default, hook signatures are `[arg-type]`-checked | `test_declare_customs_runs_its_steps_in_order`, `test_a_hook_left_out_takes_its_default`, `test_a_required_hook_cannot_be_left_out`, `test_the_commercial_invoice_is_always_first`, `test_a_declaration_needs_at_least_one_commodity`, `test_mypy_checks_hooks_at_construction` |
| 71 | 13 | Protocol default bodies reach only explicit subclasses; a structural match must define every member | `test_protocol_defaults_reach_only_explicit_subclasses`, `test_mypy_requires_every_protocol_member_for_a_structural_match`, `source: https://peps.python.org/pep-0544/` |
| 72 | 13 | An override that skips a base step issues a bad declaration and mypy accepts it; `@final` makes overriding the template a mypy error and the runtime only marks it | `test_a_subclass_that_skips_the_base_check_declares_nothing`, `test_mypy_accepts_an_override_that_skips_the_base_step`, `test_mypy_rejects_overriding_the_final_template`, `test_final_marks_the_template_without_enforcing_it`, `source: https://docs.python.org/3/library/typing.html` |
| 73 | 13 | The ABC form delegates to the same skeleton and gives the same declaration; a family of destinations shares schedule and code and differs in documents; an ABC missing its abstract step can't be built | `test_the_template_and_the_hooks_give_the_same_declaration`, `test_two_destinations_share_the_schedule_and_differ_in_documents`, `test_a_declarer_without_its_documents_cannot_be_built` |
| 74 | 12-13 | The "Build, run, observe" experiments behave as quoted | `run: G5` |

## Corrections after the build

- Row 68 (step G1a, confirmed by the orchestrator with a mypy 2.4.1 run): a partial that binds nothing is accepted only where it is assigned to the typed `PricingRule` slot, as a registry entry is; calling it directly, `partial(per_kg)(c)`, is `Missing named argument "rate" for "per_kg"  [call-arg]`. The claim and prose say "accepted in a typed slot".
- Step G1a added deletion rows for the `ZoneRate` quantise, both `from None` clauses and `frozen=True` on `Tariff`; the per-kg half-up case is 0.1875 kg at 1.20 (0.225 rounds to 0.23 half up, 0.22 half even).

(Left empty for the orchestrator.)

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member: `uv run pytest` and `uv run mypy --strict src tests` exit 0 on three consecutive runs. `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch|random|print\("` over both members prints nothing. `grep -n "super()" examples/13-*/src` prints nothing.
3. Every test name cited in rows 65-74 is defined exactly once across `examples/*/tests` (`grep -rhoE "def test_\w+" examples/*/tests | sort | uniq -d` lists none of them).
4. Every mypy-API test asserts exit status and an exact code set (`grep -c "_codes("` at least 3 in each `test_static.py`), and no test asserts a line number. Every `# type: ignore[...]` names a code.
5. Deletion tables (G1a, G1b): every row, when deleted in a scratch copy, makes the named test fail for the stated reason. The handback quotes the failing line, and no row reads "nothing failed".
6. ch12-13 drafted, one figure each, captions 20-45 words including `Figure N.1:`, 1,900-2,500 prose words each (validate.py).
7. `grep -c '<blockquote class="ai-sidebar"'` is 1 in each; `{: .ai-sidebar}` appears nowhere. `grep -c "^## When not to use it"` is 1 in each and `grep -c "^## How it works"` is 0. `validate.py` passes the `pattern` spine.
8. Thesis:
   - ch12 contains "a feature resolves the force without the pattern's structure" (or adapted) and names Strategy as dissolving.
   - ch13 says Template Method straddles, the hooks dissolve and the ABC form survives where state is shared (`grep -ciE "straddl"` at least 1; `dissolv` and `surviv` each at least 1).
9. Non-overlap:
   - ch12 has no excerpt of the `type PricingRule` / `flat_rate` / `per_kg` / `quote` block from "What 1994 assumed", and no re-explanation of `RateStrategy` naming or of the partial assignment gap (one sentence each, with pointers by title to "What 1994 assumed, and what Python dissolves", "Naming patterns for teams and AI assistants", "ISP, DIP, and dependency injection without a framework", "Protocol, duck typing, and structural typing with mypy", "SRP, OCP, and LSP in Python", "Patterns as decisions under forces" and "Shortcut patterns: dict dispatch, function tables, and EAFP").
   - ch13 has no restated `[abstract]` mypy message and no `override` teaching. It points to "The three-way split: dissolve, survive, disambiguate", "Strategy: the callable", "Protocol, duck typing, and structural typing with mypy" and "Mediator and Chain of Responsibility" by title.
   - `grep -niE "clearance|restricted"` over `examples/13-*/src` prints nothing.
   - Neither chapter re-teaches the evidence method, which is pointed to "Proving it works: pytest, pytest-mock, and mypy".
10. Voice:
    - `scan.sh --tier ban --fail` exits 0 over both chapters, READMEs, cards and SVGs, with `--stats` reviewed.
    - Contractions are used: uncontracted `does not|do not|is not|are not|did not|cannot` at most 3 per chapter outside code and output.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz)"` over prose (front matter `part:` slug excluded) prints nothing.
11. `grep -c $'\u2014'` is 0 over every file touched in r06, including this plan.
12. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Lisp|Dylan|Smalltalk|capstone|PDP-|\br0[0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/1[23]-*.md`, the new READMEs and cards prints nothing.
13. Idiomatic scan: 0 ban-tier in both members.
14. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`, never hand-edited.
15. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run (API output prints `<string>:N` matching the snippet), apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean.
16. Each experiment is performed in a scratch copy and changes one thing. The prose quotes the observed result, and the handback includes the raw filtered output.
17. Attribution (standing rule: credit every source a chapter leans on, by author and work, where the idea is used; nothing copied; quotations exact from fetched pages; a missing credit is blocking):
    - ch12 credits GoF and Ramalho ("Design Patterns with First-Class Functions") and quotes the functools partial paragraph exactly.
    - ch13 credits GoF and quotes PEP 544 and the `typing.final` docs exactly.
    - GoF terms appear only if verified, with the bracketed fallbacks applied. Each prose agent lists the sources it checked.
    - Every book cited is already in `bibliography.html` and in hub `books.yml` `referenced_by` (decision 3).
18. Claims:
    - Every factual sentence in ch12-13 maps to a named test, a recorded run (`run: G5` or a file under `_plans/evidence/`) or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0. The claims table lists rows 1-74, with 65-74 resolved, and each `source:` URL appears in its chapter.
19. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has fourteen entries, and `diagrams/0*-*` and `diagrams/1[01]-*` are unchanged.
20. Reconciliation rows 65-74 are `verified` or `adjusted` with evidence. Row 1 carries the r06 note.
21. Deterministic: no test depends on wall time, the environment, memory addresses (`repr` of a partial is never asserted) or iteration order it didn't create. `filterwarnings = ["error"]` is still in the root config.
22. CI `ci-ok` is green on the PR. Merge happens only after the user's explicit approval.

## Risks

- **Predicted messages.** r05 mispredicted four. Everything in Planning evidence was run. The chapter 13 `[arg-type]` text must be re-verified against the real `DutyRule` signature (lines, not `Money`), and every experiment output is a prediction. Tests match stable substrings, and differences go in "Corrections after the build".
- **Run-token and test-name collisions** make claims resolve without proof. G-prefixed step ids and criterion 3 guard against both.
- **Contrast code** (decision 1). The class-per-strategy fixture must not appear in prose excerpts. The `ast` count must count strategy classes (defining `__call__` or `price`), not every class, or `Tariff` inflates it.
- **The ABC justification** (decision 2) can read as a rationalisation, because bound methods fill hooks without inheritance. The prose states the line plainly: a family that shares state and code across steps. Test 23 is its witness.
- **Protocol fixture interplay.** `_ExplicitHooks` is an explicit Protocol subclass, which the Protocol chapter calls nominal. Don't re-teach the `None`-body hazard; give a pointer.
- **`@final` override fixture** needs `# type: ignore[misc]`, so experiment (a) changes the member mypy output. That's expected and quoted.
- **ruff.** B027 (empty non-abstract method in an ABC) must not fire: hook defaults return values. N818 holds (`CustomsError`, `RatingError`).
- **Overlap** with the three-way split (order witness), the Protocol chapter (`[abstract]`, `override`), the SRP/OCP chapter (rules as data), the ISP/DIP chapter (partial gap), dict dispatch, Chain of Responsibility (clearance) and the decorator chapters. Criterion 9 greps for it, and pointers go by title only.
- **Liquid.** f-strings with `{{` in excerpts need `{% raw %}`; validate.py checks.
- **Word budgets.** ch12 sections 6-7 and ch13 sections 5 and 7 are dense. Tables don't count toward the floor, and each chapter has at most six excerpts.
- **Attribution.** GoF can't be quoted (no fetched text). The *Fluent Python* titles were verified through the book's code repository, not the publisher page. The PEP 544 sentence's final punctuation is to be confirmed on the page.
- **`uv.lock` race.** G1a and G1b are sequenced, and project names normalise to the package names.

