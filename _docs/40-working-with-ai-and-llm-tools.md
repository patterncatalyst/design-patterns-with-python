---
title: "Working with AI and LLM tools"
order: 40
layout: tutorial
sectionid: docs
part: "putting-it-together"
description: "Three hand-written drafts of one pricing function, three gates (types and lint, shape rules, a behaviour oracle) and a model client behind a Protocol, tested with recorded replies."
---

## Learning objectives

By the end of this chapter you can:

- Treat an assistant's reply as a draft, and say which of three gates checks which property.
- Run the static gate and read what `mypy --strict` and ruff can and can't see in a pattern.
- Check a draft's shape against the book's pattern rules with `review_gate.shape`.
- Check a draft's behaviour against an oracle built from the code it replaces.
- Put a model client behind a Protocol and test the review loop with recorded replies and no network.

## Why this matters

A draft of `price` arrives for review, and the reviewer has to decide whether to merge it. The diff shows the code and not the reasons for its shape, so the decision rests on what the reviewer can check. Trust that rests on where a draft came from checks nothing. Trust that rests on gates the team already owns can say what passed and what the gates can't see.

OWASP's [LLM05:2025 entry, Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/), puts the stance in one sentence: "Treat the model as any other user, adopting a zero-trust approach, and apply proper input validation on responses coming from the model to backend functions." That sentence is about a model's output reaching a backend. A pull request is another place output arrives, and the chapter's rule follows from the same stance: trust a reply as far as the checks it has passed.

The book already has three such checks. Types and lint judge a draft's text, the pattern chapters give rules about its shape, and a table of recorded answers judges what it computes. The three drafts below were written by hand for the book. They stand in for replies, so the results describe these drafts and make no claim about what any assistant writes.

{% include excalidraw.html name="40-working-with-ai-and-llm-tools" caption="Figure 40.1: A draft is checked by three gates: types and lint, the pattern shape rules and a behaviour oracle. The three drafts are reported by different gates, and the findings on a rejected reply go back in the next prompt." %}

Read the figure from the top. A wide box, "a draft's text" (`Assistant.reply`, or a file in `tests/drafts`), has three arrows down to three boxes side by side: "static gate: mypy --strict, ruff" ("reports untyped_factory"), "shape review: review_gate.shape" ("reports untyped_factory, typed_hierarchy") and "behaviour oracle: GRID" ("reports untyped_factory, rounded_callable"). The static gate reports one draft and the other two gates report two each, so `untyped_factory` is reported by all three. The gates sit in parallel, because no code orders them. Each has an arrow down to a wide accent box, "accepted" ("no gate reports the draft"). One amber arrow runs from the shape review back up to the first box, labelled "propose: findings go back in the next prompt". It leaves the shape review alone because that is the one gate the tests hand to `propose`.

## Three drafts, three gates

A gate returns findings, and a reply is accepted when no gate has any. The reference is the idiomatic module, `pricing.py`, which uses the shapes the earlier chapters argue for: a callable type for a rule, a read-only table of rules and an unknown name that raises `RatingError`. Its rounding is the line the oracle will care about:

<!-- fmt:off -->
```python
def per_kg(consignment: Consignment, /, *, rate: Decimal) -> Money:
    """Weight times a rate per kilogram, rounded half up to the cent."""
    return Money((consignment.weight.kilograms * rate).quantize(CENT, rounding=ROUND_HALF_UP))
```
<!-- fmt:on -->

The three drafts are text files under `tests/drafts/`, kept as `.py.txt` so that ruff, mypy and pytest don't collect them. Each opens with a comment saying it was written for the book (`test_every_draft_says_it_was_written_for_the_book`). `untyped_factory` is an abstract `RateStrategy` with two subclasses, a getter and setter for the rate, a factory class that stores its instance in `__new__`, and methods without annotations. `typed_hierarchy` is the same hierarchy fully annotated, with the factory as a static method. `rounded_callable` has the idiomatic shape and rounds with `round(..., 2)`.

| Draft | Static gate | Shape review | Behaviour oracle |
| --- | --- | --- | --- |
| `untyped_factory` | fails | fails | fails |
| `typed_hierarchy` | passes | fails | passes |
| `rounded_callable` | passes | passes | fails |
| `pricing.py` | passes | passes | passes |

The first three rows are `test_each_draft_fails_exactly_the_gates_in_the_table`, run once per draft, and the last is `test_the_idiomatic_module_passes_every_gate`. Each gate alone accepts at least one draft that another gate stops: the static gate accepts the second and third, the shape review accepts the third, and the oracle accepts the second. Of these four modules, only the idiomatic one passes all three. The gates answer different questions. Types and lint check that the text is complete and current. The shape review checks that the draft uses the structure the pattern chapters recommend. The oracle checks what the draft computes.

The shape that `typed_hierarchy` keeps is a cost, and [Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) counts it: there mypy and ruff pass the class-per-strategy engine too, so a clean type check says nothing about whether nine classes were needed.

## The static gate

The first gate is what the repository already runs on its own code. It asks a tool to decide from the text, without running anything, whether the annotations are complete and consistent and whether the code uses current idioms. The mypy command-line page describes `--strict` in one sentence: "This flag mode enables a defined subset of optional error-checking flags." It adds that "the --warn-unreachable flag is not automatically enabled by the strict flag." The gate passes `--warn-unreachable` explicitly. Ruff runs with a copy of the repository's rule selection, which includes `UP`.

`untyped_factory` fails both tools. The test collects each finding's line and rule and asserts the sorted list (`test_the_static_gate_reports_the_untyped_draft`). mypy reports `no-untyped-def` for the five methods that have no annotations, at lines 11, 16, 24, 27 and 30 of the draft, and `no-untyped-call` at line 52, the call in `price` to one of them. Ruff reports `UP045` at line 36 and `UP037` at lines 36 and 38, all in the factory class. `UP045` flags `Optional["RateStrategyFactory"]`, and ruff's page for [UP045](https://docs.astral.sh/ruff/rules/non-pep604-annotation-optional/) describes the rule as "Check for typing.Optional annotations that can be rewritten based on PEP 604 syntax." `UP037` flags the quotes in that annotation and in the return annotation of `__new__`.

`typed_hierarchy` passes both. Its base class, its factory and `price` carry the shape:

<!-- fmt:off -->
```python
class RateStrategy(ABC):
    @abstractmethod
    def calculate(self, consignment: Consignment) -> Money: ...


class RateStrategyFactory:
    @staticmethod
    def create(name: str) -> RateStrategy:
        match name:
            case "flat":
                return FlatRate()
            case "per_kg":
                return PerKilogramRate(Decimal("0.45"))
            case _:
                raise RatingError(f"unknown rule {name}")


def price(rule: str, consignment: Consignment, /) -> Money:
    return RateStrategyFactory.create(rule).calculate(consignment)
```
<!-- fmt:on -->

`test_mypy_and_ruff_pass_the_typed_hierarchy` asserts that both tools report nothing on this draft, and that mypy reports `unreachable` for a statement after a `return`, which pins `--warn-unreachable`. The draft is fully annotated and uses `match`, and neither tool asks whether a one-method base or a class of one static method was needed. Run over this draft with every rule and the preview rules switched on, ruff 0.17.4 reports missing docstrings, a missing copyright notice, an unused argument, exception-message style and `no-self-use` for one method, and nothing about the base class or the factory class.

## The shape review

The shape review writes down what a reviewer who has read the pattern chapters looks for, so that the comparison runs on every draft in the same way. `review` parses a draft with `ast`, and each rule is a function from the module to findings. This is one rule and the function that runs them:

<!-- fmt:off -->
```python
def single_method_base(tree: ast.Module) -> Iterator[Finding]:
    """An abstract base with one abstract method is a callable type (Strategy: the callable)."""
    for cls in _classes(tree):
        methods = _methods(cls)
        if (
            _derives_from_abc(cls)
            and len(methods) == 1
            and _decorated_with(methods[0], "abstractmethod")
        ):
            yield Finding(cls.lineno, "single-method-base", "use a callable type alias")


def review(source: str, /, *, rules: Sequence[ShapeRule] = SHAPE_RULES) -> list[Finding]:
    """Findings from every rule, sorted by line: ``ast.walk`` yields nodes in no fixed order."""
    tree = ast.parse(source)
    return sorted(finding for rule in rules for finding in rule(tree))
```
<!-- fmt:on -->

The [`ast` documentation](https://docs.python.org/3/library/ast.html) says `ast.walk` yields nodes "in no specified order", which is why `review` sorts. `test_findings_come_back_in_line_order` feeds it a source whose rule order is the reverse of its line order, and it fails if the sort goes.

`SHAPE_RULES` holds four rules, each from a pattern chapter. `single_method_base` comes from [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}): one abstract method is a callable type. `static_only_class` flags a class whose methods are all static or class methods, which is a module with a class around it, and [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) and [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) show a factory held as a callable in a read-only table. `accessor_pair` flags a `get_x` with a matching `set_x`, which [Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) replaces with an attribute. `instance_in_new` flags a `__new__` that stores on `cls`, the `__new__` form that [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) sets beside the module and the other forms.

On the class drafts the findings are exact lists. `typed_hierarchy` gets `single-method-base` at line 8 and `static-only-class` at line 27 (`test_the_shape_review_names_the_typed_hierarchy_rules`). `untyped_factory` gets `single-method-base` at 9, `accessor-pair` at 24 and `instance-in-new` at 38 (`test_the_shape_review_names_the_untyped_draft_rules`). Each rule also has a minimal case of a few lines that it flags (`test_each_shape_rule_fires_on_its_minimal_case`). The rules stay quiet on a class with `__call__`, on a frozen dataclass with one method (`test_shape_rules_stay_quiet_on_a_callable_class_and_a_frozen_dataclass`) and on a getter with no setter (`test_a_getter_without_a_setter_is_not_an_accessor_pair`).

The rules are a checklist of four shapes. `rounded_callable` passes them and is still wrong, which is the oracle's job to say.

## The behaviour oracle

The first two gates judge text. The oracle runs the draft and compares what it answers. The idea is the golden values of [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}): record the answers of code you trust and hold a replacement to them. Here the recorded answers are the idiomatic module's, written as literals in `EXPECTED_ROWS`, so a change to `pricing.py` can't move its own reference.

<!-- fmt:off -->
```python
GRID = tuple(product(("flat", "per_kg"), ("0.5", "1", "2.5", "12.5", "40")))
```

```python
def oracle(module: ModuleType) -> list[str]:
    """Run the draft's ``price`` over the grid and list each row that differs from the record."""
    failures: list[str] = []
    for index, ((rule, kilograms), expected) in enumerate(zip(GRID, EXPECTED_ROWS, strict=True)):
        consignment = Consignment(ConsignmentId(f"CN-{index}"), "EU", Weight(Decimal(kilograms)))
        actual = module.price(rule, consignment).amount
        if actual != Decimal(expected):
            failures.append(f"CN-{index} {rule}: {expected} != {actual}")
    return failures
```
<!-- fmt:on -->

The grid is ten consignments, two rules over five weights. At 0.45 a kilogram, 0.5 kg, 2.5 kg and 12.5 kg price at 0.225, 1.125 and 5.625 before rounding, so the recorded answers are 0.23, 1.13 and 5.63, where rounding half up takes each to the next cent. `untyped_factory` leaves the rounding argument out and `rounded_callable` uses `round`, and both give exactly the same three differences (`test_the_oracle_lists_the_half_cent_rows`): `CN-5 per_kg: 0.23 != 0.22`, `CN-7 per_kg: 1.13 != 1.12` and `CN-8 per_kg: 5.63 != 5.62`. Seven other rows agree. `typed_hierarchy` passes the oracle because it rounds half up.

The oracle loads the draft as a module from a file in a temporary directory, so it runs code the reviewer didn't write. Run it after the static and shape gates, and where a mistake costs nothing. The loader isn't a sandbox.

## Prompts as reusable patterns

A sidebar in this book has one form: a problem in a sentence or two, one prompt to paste, and one line of review. The prompt names the chapter's rule and its identifiers. Every chapter from [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}) through [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}), 34 chapters, carries exactly one sidebar, and each of the 34 has one nested prompt and one review line. The form is reusable because the prompt can state the checks before any reply exists. A prompt that lists the gates says what the reply will be measured against, and the review line says what to ask when a diff moves an answer the gates hold.

The sidebar below follows the form for `price`. The names a prompt should use, and the review of a name against its contract, belong to [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}). The prompt below adds the gates to the request.

## A seam for the model client

Code that asks an assistant for a reply has a dependency like any other, and the book's usual move for a dependency is a Protocol with a fake behind it in tests. `Assistant` has one method. `RecordedAssistant` replays recorded replies in order for each prompt, and `propose` runs the loop: ask, gate the reply, and if it's rejected, ask again with the findings appended.

<!-- fmt:off -->
```python
class Assistant(Protocol):
    def reply(self, prompt: str, /) -> str: ...


class RecordedAssistant:
    """Replays recorded replies in order for each prompt and refuses a prompt without one."""

    def __init__(self, replies: Mapping[str, Sequence[str]]) -> None:
        self._replies = {prompt: list(texts) for prompt, texts in replies.items()}
        self.prompts: list[str] = []

    def reply(self, prompt: str, /) -> str:
        self.prompts.append(prompt)
        remaining = self._replies.get(prompt)
        if not remaining:
            raise LookupError(f"no recorded reply for prompt {prompt!r}")
        return remaining.pop(0)


def propose(
    prompt: str, /, *, assistant: Assistant, gates: Sequence[Gate], attempts: int = 2
) -> list[Review]:
    """Ask, gate the reply and, if it is rejected, ask again with the findings appended."""
    reviews: list[Review] = []
    current = prompt
    for _ in range(attempts):
        source = assistant.reply(current)
        findings = tuple(finding for gate in gates for finding in gate(source))
        reviews.append(Review(source, findings))
        if not findings:
            break
        lines = "\n".join(f"line {f.line}: {f.rule}, {f.advice}" for f in findings)
        current = f"{prompt}\n\nFix these findings:\n{lines}"
    return reviews
```
<!-- fmt:on -->

The tests drive the loop with the drafts as recorded replies and the shape review as the gate. A rejected reply goes back with its findings: the second prompt is the first plus `Fix these findings:` and one line per finding, and the fake holds a reply under exactly that text (`test_a_rejected_reply_is_sent_back_with_its_findings`). The loop stops at the first accepted reply, so a second recorded reply is never requested (`test_the_loop_stops_at_the_first_accepted_reply`), and it gives up after its attempts with both replies rejected (`test_the_loop_gives_up_after_its_attempts`). An unrecorded prompt raises `LookupError`, so a test can't pass on a prompt nobody recorded (`test_an_unrecorded_prompt_is_refused`).

The package imports no network module: `test_the_package_imports_no_network_module` parses its five files and finds no import of `socket`, `ssl`, `http`, `urllib`, `asyncio` or `subprocess`. The tests run mypy in-process and ruff as a local process. A client for a real service goes behind the same Protocol as an adapter, and the book contains none. [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) covers the pattern, [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) the Protocol, and [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) why `assistant` is a parameter and nothing is patched. mypy holds the seam: a class with `answer` where the Protocol asks for `reply` is refused with `[arg-type]` and a message that names `Assistant`, and renaming the method clears it (`test_mypy_refuses_an_assistant_without_reply`).

## When the gates aren't enough

The gates verify what they list. The grid is ten rows, so the oracle says nothing about a weight it doesn't list, and the shape review looks for four shapes. `rounded_callable` shows the gap between the first two gates and the third, and a draft that passes all three has been checked on those rows and in those shapes, and no further. A diff that edits `EXPECTED_ROWS` moves the answer the oracle holds every draft to.

OWASP's [LLM09:2025 entry, Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/), names the failure: "Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy." The gates are a way to verify accuracy at chosen points, and everything between those points is trust.

<blockquote class="ai-sidebar" markdown="1">

**Asking for code you will gate.** "Write the pricing strategies" leaves the shape and the rounding open. Paste a prompt that names the gates the reply must pass:

> Write `price(rule, consignment, /)` over `type PricingRule = Callable[[Consignment], Money]`, with the rules in a read-only `frozendict` and an unknown name raising `RatingError`. Round with `quantize(CENT, rounding=ROUND_HALF_UP)`. No base classes, no static-only classes, no getters or setters. The reply must pass `mypy --strict`, ruff, `review_gate.shape.review` and the grid in `tests/test_gates.py`.

If the diff touches `GRID` or `EXPECTED_ROWS`, ask who decided that answer should change.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then, in `examples/40-working-with-ai-and-llm-tools`, `uv run pytest` runs 18 test functions as 26 cases, and `uv run mypy --strict src tests` checks the example:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'
uv run mypy --strict src tests
```

```text
26 passed in 3.81s
Success: no issues found in 10 source files
```

Each experiment below runs in a scratch copy of the repository: delete the copy's `.venv`, run `uv sync --locked --all-packages` from its root and check that `review_gate.__file__` points into the copy. The first changes the rounding in `src/review_gate/pricing.py`. Replace the `return` line of `per_kg` with `return Money(round(consignment.weight.kilograms * rate, 2))`, and drop `ROUND_HALF_UP` from the `decimal` import. Left in, the unused import adds a ruff finding to the failure. The same two commands print:

```text
E       AssertionError: assert ([], [], ['CN....63 != 5.62']) == ([], [], [])
E         At index 2 diff: ['CN-5 per_kg: 0.23 != 0.22', 'CN-7 per_kg: 1.13 != 1.12', 'CN-8 per_kg: 5.63 != 5.62'] != []
E         Use -v to get more diff
tests/test_gates.py:78: AssertionError
FAILED tests/test_gates.py::test_the_idiomatic_module_passes_every_gate - Ass...
1 failed, 25 passed in 3.79s
Success: no issues found in 10 source files
```

One test fails, and the third item of its tuple is the oracle's list: the idiomatic module now gives the same three rows as the two rounding drafts. The table test still passes, because it runs the drafts and never `pricing.py`. mypy exits 0, since the change moves a value and not a type.

The second experiment restores `pricing.py` and, in `src/review_gate/shape.py`, removes the `static_only_class,` line from `SHAPE_RULES`. The same two commands print:

```text
E           LookupError: no recorded reply for prompt 'Write price() over PricingRule.\n\nFix these findings:\nline 8: single-method-base, use a callable type alias'
src/review_gate/assistant.py:25: LookupError
E           LookupError: no recorded reply for prompt 'Write price() over PricingRule.\n\nFix these findings:\nline 8: single-method-base, use a callable type alias'
src/review_gate/assistant.py:25: LookupError
E       AssertionError: assert [(8, 'single-method-base')] == [(8, 'single-...-only-class')]
E         Right contains one more item: (27, 'static-only-class')
E         Use -v to get more diff
tests/test_gates.py:114: AssertionError
E       AssertionError: assert [] == [(1, 'static-only-class')]
E         Right contains one more item: (1, 'static-only-class')
E         Use -v to get more diff
tests/test_shape.py:82: AssertionError
FAILED tests/test_assistant.py::test_a_rejected_reply_is_sent_back_with_its_findings
FAILED tests/test_assistant.py::test_the_loop_gives_up_after_its_attempts - L...
FAILED tests/test_gates.py::test_the_shape_review_names_the_typed_hierarchy_rules
FAILED tests/test_shape.py::test_each_shape_rule_fires_on_its_minimal_case[static-only-class]
4 failed, 22 passed in 3.81s
Success: no issues found in 10 source files
```

Four tests fail. The typed hierarchy's shape test finds `single-method-base` and not the second rule, and the minimal case for `static-only-class` finds nothing. The two loop tests fail because the findings sent back have changed: with one finding in place of two, the fix-up prompt is no longer the text the fake holds a reply for, and the fake refuses it. The table test still passes, since `single-method-base` still stops `typed_hierarchy`. mypy exits 0 again.

## What you can do now

- Treat a reply as a draft and say which gate checks what: `test_each_draft_fails_exactly_the_gates_in_the_table` gives each draft its row, and `test_the_idiomatic_module_passes_every_gate` shows the one module that clears all three.
- Run the static gate: `test_the_static_gate_reports_the_untyped_draft` lists `UP037`, `UP045`, `no-untyped-call` and `no-untyped-def`, and `test_mypy_and_ruff_pass_the_typed_hierarchy` shows a draft they both accept.
- Check shape: `review` runs `SHAPE_RULES` over a draft and returns sorted findings, and the two shape tests on the class drafts name the line and rule of each.
- Check behaviour: `GRID` and the recorded `EXPECTED_ROWS` give the oracle, and `test_the_oracle_lists_the_half_cent_rows` lists the three rows both rounding drafts get wrong.
- Put the client behind a Protocol: `Assistant`, `RecordedAssistant` and `propose` run the review loop with recorded replies, and the import test shows no network module in the package.

## For deeper coverage

The [mypy command-line page](https://mypy.readthedocs.io/en/stable/command_line.html) defines `--strict` and `--warn-unreachable`, and the [ruff rules index](https://docs.astral.sh/ruff/rules/) lists every rule the gate's selection draws from, including [UP045](https://docs.astral.sh/ruff/rules/non-pep604-annotation-optional/). The [`ast` documentation](https://docs.python.org/3/library/ast.html) covers the tree the shape review reads. OWASP's [LLM05:2025 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) and [LLM09:2025 Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/) entries are the sources of the two quotations. [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}) covers recorded answers as a check, and [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}) covers names in prompts and reviews. The books the book draws on are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
