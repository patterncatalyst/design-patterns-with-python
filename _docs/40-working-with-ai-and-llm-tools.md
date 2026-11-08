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
- Run the static gate and know what `mypy --strict` and ruff can and can't see in a pattern.
- Check a draft's shape against the pattern rules with `review_gate.shape`.
- Check a draft's behaviour against an oracle built from the code it replaces.
- Put a model client behind a Protocol and test the review loop with recorded replies and no network.

## Why this matters

A draft of `price` arrives for review, and the reviewer has to decide whether to merge it. The diff shows the code, not the reasons for its shape, so the decision rests on what the reviewer can check. Trusting a draft because of where it came from checks nothing. Gates the team already owns can say what passed and what they can't see.

OWASP's [LLM05:2025 entry, Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/), states the stance: "Treat the model as any other user, adopting a zero-trust approach, and apply proper input validation on responses coming from the model to backend functions." A pull request is another place model output arrives. Trust a reply as far as the checks it has passed.

Three checks are already in hand. Types and lint judge a draft's text, the pattern rules judge its shape, and a table of recorded answers judges what it computes. The three drafts below were written by hand to stand in for replies, so the results describe these drafts and make no claim about what any assistant writes.

{% include excalidraw.html name="40-working-with-ai-and-llm-tools" described="true" caption="Figure 40.1: A draft is checked by three gates: types and lint, the pattern shape rules and a behaviour oracle. The three drafts are reported by different gates, and the findings on a rejected reply go back in the next prompt." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-40-working-with-ai-and-llm-tools" markdown="1">
From the top: a wide box, "a draft's text" (`Assistant.reply`, or a file in `tests/drafts`), has three arrows down to three boxes side by side: "static gate: mypy --strict, ruff" ("reports untyped_factory"), "shape review: review_gate.shape" ("reports untyped_factory, typed_hierarchy") and "behaviour oracle: GRID" ("reports untyped_factory, rounded_callable"). The gates sit in parallel, because no code orders them. Each has an arrow down to a wide accent box, "accepted" ("no gate reports the draft"). One amber arrow runs from the row of gates back up to the first box, labelled "propose: every gate's findings go back in the next prompt". It belongs to no one gate, because `propose` collects the findings of every gate it's given.
</div>
</details>

The gates run side by side, and the findings of every gate go back in the next prompt.

## Three drafts, three gates

A gate returns findings, and a reply is accepted when no gate has any. The reference is the idiomatic module, `pricing.py`: a callable type for a rule, a read-only table of rules and an unknown name that raises `RatingError`. Its rounding is the line the oracle cares about:

<!-- fmt:off -->
```python
def per_kg(consignment: Consignment, /, *, rate: Decimal) -> Money:
    """Weight times a rate per kilogram, rounded half up to the cent."""
    return Money((consignment.weight.kilograms * rate).quantize(CENT, rounding=ROUND_HALF_UP))
```
<!-- fmt:on -->

The drafts are text files under `tests/drafts/`, kept as `.py.txt` so ruff, mypy and pytest don't collect them. Each opens with a comment saying it was written by hand.

| Draft | Shape | Static gate | Shape review | Behaviour oracle |
| --- | --- | --- | --- | --- |
| `untyped_factory` | Abstract `RateStrategy`, two subclasses, rate getter and setter, factory storing its instance in `__new__`, no annotations | fails | fails | fails |
| `typed_hierarchy` | The same hierarchy fully annotated, factory as a static method | passes | fails | passes |
| `rounded_callable` | The idiomatic shape, rounding with `round(..., 2)` | passes | passes | fails |
| `pricing.py` | The idiomatic module | passes | passes | passes |

Each gate alone accepts a draft that another gate stops, and only the idiomatic module passes all three. Types and lint check that the text is complete and current. The shape review checks the structure the pattern chapters recommend. The oracle checks what the draft computes.

The shape `typed_hierarchy` keeps is a cost that [Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) counts: mypy and ruff pass a class-per-strategy engine too, so a clean type check says nothing about whether nine classes were needed.

## The static gate

The first gate is what the repository already runs on its own code: decide from the text, without running anything, whether the annotations are complete and the idioms current. The mypy command-line page says `--strict` "enables a defined subset of optional error-checking flags" and that "the --warn-unreachable flag is not automatically enabled by the strict flag", so the gate passes `--warn-unreachable` explicitly. Ruff runs with a copy of the repository's rule selection, which includes `UP`.

| Draft | Tool | Findings |
| --- | --- | --- |
| `untyped_factory` | mypy | `no-untyped-def` on the five unannotated methods; `no-untyped-call` where `price` calls one |
| `untyped_factory` | ruff | `UP045` on `Optional["RateStrategyFactory"]`; `UP037` on the quotes there and in the `__new__` return annotation |
| `typed_hierarchy` | both | nothing |

Ruff's page for [UP045](https://docs.astral.sh/ruff/rules/non-pep604-annotation-optional/) describes the rule as "Check for typing.Optional annotations that can be rewritten based on PEP 604 syntax." `typed_hierarchy` passes both tools:

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

It's fully annotated and uses `match`, and neither tool asks whether a one-method base or a class of one static method was needed. With every rule and the preview rules switched on, ruff 0.17.4 reports missing docstrings, a missing copyright notice, an unused argument, exception-message style and `no-self-use` for one method, and nothing about the base class or the factory class.

## The shape review

The shape review writes down what a reviewer who knows the patterns looks for, so the same comparison runs on every draft. `review` parses a draft with `ast`, and each rule is a function from the module to findings:

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

The [`ast` documentation](https://docs.python.org/3/library/ast.html) says `ast.walk` yields nodes "in no specified order", which is why `review` sorts. `SHAPE_RULES` holds four rules, each from a pattern:

| Rule | Flags | Replacement | Source |
| --- | --- | --- | --- |
| `single_method_base` | An abstract base with one abstract method | A callable type | [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) |
| `static_only_class` | A class whose methods are all static or class methods | A factory held as a callable in a read-only table | [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}), [Shortcut patterns]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) |
| `accessor_pair` | A `get_x` with a matching `set_x` | An attribute | [Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) |
| `instance_in_new` | A `__new__` that stores on `cls` | A module, or another Singleton form | [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) |

`typed_hierarchy` gets `single-method-base` at line 8 and `static-only-class` at line 27. `untyped_factory` gets `single-method-base` at 9, `accessor-pair` at 24 and `instance-in-new` at 38. The rules stay quiet on a class with `__call__`, on a frozen dataclass with one method and on a getter with no setter.

The rules are a checklist of four shapes. `rounded_callable` passes them and is still wrong.

## The behaviour oracle

The first two gates judge text. The oracle runs the draft and compares its answers with recorded ones, the golden values of [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}). The recorded answers are the idiomatic module's, written as literals in `EXPECTED_ROWS`, so a change to `pricing.py` can't move its own reference.

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

The grid is ten consignments, two rules over five weights. At 0.45 a kilogram, 0.5 kg, 2.5 kg and 12.5 kg price at 0.225, 1.125 and 5.625 before rounding, and rounding half up gives 0.23, 1.13 and 5.63. `untyped_factory` leaves the rounding argument out and `rounded_callable` uses `round`, which rounds half to even, so both give the same three differences: `CN-5 per_kg: 0.23 != 0.22`, `CN-7 per_kg: 1.13 != 1.12` and `CN-8 per_kg: 5.63 != 5.62`. `typed_hierarchy` rounds half up and passes.

The oracle loads the draft as a module from a temporary directory, so it runs code the reviewer didn't write. Run it after the static and shape gates, and only where a mistake costs nothing. The loader isn't a sandbox.

## Prompts as reusable patterns

Every pattern sidebar has one form: what the request leaves open, one prompt to paste, and one line of review. The prompt names the pattern's rule and its identifiers, so it states the checks before any reply exists. The review line says what to ask when a diff moves an answer the gates hold. Choosing the names a prompt uses, and reviewing a name against its contract, belong to [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}). The sidebar under "When the gates aren't enough" adds the gates to the request for `price`.

## A seam for the model client

Code that asks an assistant for a reply has a dependency like any other, so it goes behind a Protocol with a fake in tests. `Assistant` has one method. `RecordedAssistant` replays recorded replies in order for each prompt, and `propose` runs the loop:

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

The loop's behaviour:

- **A rejected reply goes back with its findings.** The second prompt is the first plus `Fix these findings:` and one line per finding.
- **The loop stops at the first accepted reply**, so a later recorded reply is never requested.
- **It gives up after `attempts`** and returns every review, all rejected.
- **An unrecorded prompt raises `LookupError`**, so nothing passes on a prompt nobody recorded.

The package imports none of `socket`, `ssl`, `http`, `urllib`, `asyncio` or `subprocess`. mypy runs in-process and ruff as a local process. A client for a real service goes behind the same Protocol as an adapter; see [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}), [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) and, for why `assistant` is a parameter and nothing is patched, [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}). mypy holds the seam: a class with `answer` where the Protocol asks for `reply` is refused with `[arg-type]` and a message naming `Assistant`.

## When the gates aren't enough

The gates verify what they list. The oracle says nothing about a weight outside its ten rows, and the shape review looks for four shapes. A draft that passes all three has been checked on those rows and in those shapes, and no further. A diff that edits `EXPECTED_ROWS` moves the answer every draft is held to.

OWASP's [LLM09:2025 entry, Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/), names the failure: "Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy." The gates verify accuracy at chosen points, and everything between those points is trust.

<blockquote class="ai-sidebar" markdown="1">

**Asking for code you will gate.** "Write the pricing strategies" leaves the shape and the rounding open. Paste a prompt that names the gates the reply must pass:

> Write `price(rule, consignment, /)` over `type PricingRule = Callable[[Consignment], Money]`, with the rules in a read-only `frozendict` and an unknown name raising `RatingError`. Round with `quantize(CENT, rounding=ROUND_HALF_UP)`. No base classes, no static-only classes, no getters or setters. The reply must pass `mypy --strict`, ruff, `review_gate.shape.review` and the grid in `tests/test_gates.py`.

If the diff touches `GRID` or `EXPECTED_ROWS`, ask who decided that answer should change.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then, in `examples/40-working-with-ai-and-llm-tools`:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'
uv run mypy --strict src tests
```

All 26 cases pass and mypy is clean. Run each experiment in a scratch copy of the repository: delete the copy's `.venv`, run `uv sync --locked --all-packages` from its root and check that `review_gate.__file__` points into the copy.

- **Round with `round`.** In `src/review_gate/pricing.py`, make `per_kg` return `Money(round(consignment.weight.kilograms * rate, 2))` and drop `ROUND_HALF_UP` from the import. One test fails: the idiomatic module now gets the same three half-cent rows wrong as the rounding drafts. mypy stays green, because the change moves a value, not a type.
- **Drop a shape rule.** Remove `static_only_class,` from `SHAPE_RULES` in `src/review_gate/shape.py`. Four tests fail: `typed_hierarchy` loses its second finding, the rule's minimal case finds nothing, and the two loop tests hit `LookupError` because the fix-up prompt no longer matches the recorded one. The table still holds, since `single-method-base` still stops `typed_hierarchy`.

## What you can do now

- Treat a reply as a draft and say which gate checks what, using the table of three drafts against three gates.
- Run the static gate and read its `no-untyped-def`, `no-untyped-call`, `UP045` and `UP037` findings, knowing it passes a needless class hierarchy.
- Check shape with `review` and `SHAPE_RULES`, which name the line and rule of each finding.
- Check behaviour with `GRID` and the recorded `EXPECTED_ROWS`, which catch the three half-cent rows.
- Run the review loop with `Assistant`, `RecordedAssistant` and `propose`, with recorded replies and no network module.

## For deeper coverage

The [mypy command-line page](https://mypy.readthedocs.io/en/stable/command_line.html) defines `--strict` and `--warn-unreachable`, and the [ruff rules index](https://docs.astral.sh/ruff/rules/) lists every rule the gate's selection draws from, including [UP045](https://docs.astral.sh/ruff/rules/non-pep604-annotation-optional/). The [`ast` documentation](https://docs.python.org/3/library/ast.html) covers the tree the shape review reads. OWASP's [LLM05:2025 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) and [LLM09:2025 Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/) entries are the sources of the two quotations. [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}) covers recorded answers as a check, and [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}) covers names in prompts and reviews. The [bibliography]({{ '/bibliography/' | relative_url }}) lists the books.
