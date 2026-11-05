---
title: "Template Method and the function alternative"
order: 13
layout: tutorial
sectionid: docs
part: "selecting-varying-behavior"
description: "Template Method straddles: the hook structure dissolves into a function that takes hooks, and the inheritance form survives where a family of variants shares state and code across steps."
---

## Learning objectives

By the end of this chapter you can:

- Say which part of Template Method dissolves into a function that takes hooks, and which part survives as inheritance.
- Write a skeleton where required hooks have no default, optional hooks have one and the invariant steps sit outside every hook.
- Say why a default body in a `Protocol` doesn't reach a class that only matches structurally.
- Say what `typing.final` enforces at type-check time and what it leaves alone at runtime.
- Choose between hooks and an abstract base class by asking whether the steps share state and code.

## Why this matters

A customs declaration has an order. Refuse a consignment with nothing in it, classify each commodity, total the declared value in one currency, assess duty, then list the documents with the commercial invoice first. Destinations differ in how they classify, how they assess duty and which extra documents they want. They shouldn't differ in the order, or in whether the refusal happens.

The familiar way to write that is a base class with the order in one method and the varying steps as overridable ones. It works until a destination subclass overrides a preparation step, forgets to call the base version, and issues a declaration with no commodity lines. mypy accepts that code. The failure is quiet: a declaration is issued, and it's wrong.

Two other designs have failures of their own. In a bag of hooks where every hook has a default, a destination can omit its classification and still get a declaration, because nothing is missing as far as the type is concerned. A `Protocol` given default method bodies suggests that every class that matches inherits the defaults, and a class that matches structurally doesn't.

{% include excalidraw.html name="13-template-method-and-the-function-alternative" caption="Figure 13.1: One customs skeleton, two ways to vary it. declare_customs fixes the order and the invariant steps and takes hooks for the rest; CustomsDeclarer keeps the same skeleton final and lets a family of destinations share its schedule." %}

Read the figure from the top down, in the order `declare_customs` runs. Two arrows feed the accent box at the top. From the left, `CustomsHooks` supplies functions per destination, with Singapore as the example. From the right, `CustomsDeclarer` supplies bound methods that become hooks, and `NetherlandsDeclarer` and `GermanyDeclarer` point up into it. Below the box, the grey steps are invariant and the blue ones are hooks: refuse no commodities, classify each commodity, total in one currency, assess duty, then the commercial invoice first. A side box, `extra_documents` with the default "none", feeds that last step. The column ends at `CustomsDeclaration`.

## An order variants can't change

*Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994) catalogues Template Method for a procedure whose order a base class fixes while subclasses supply the steps that vary. The force is the one above, a sequence that has to hold across variants that differ in a few steps.

The pattern straddles two buckets. The hook structure dissolves: a function that takes the varying steps as arguments fixes the order as well as a base class does, with nothing to inherit from. The inheritance form survives where a family of variants shares state and code across several steps. Where that line falls is the question [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) left open for this pattern, and the sections below answer it.

Each hook here is a strategy in the sense of [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}), a plain function chosen by the caller. What a hook shares with its neighbours is a fixed order and the invariant steps around it. A skeleton like this has three kinds of step, and the design is mostly deciding which kind each one is. An invariant step sits outside every hook and no variant can touch it. A required hook has no default, so a variant that forgets it fails at construction. An optional hook has a default, so omitting it is a decision the variant made. The mistake to look for is a step in the wrong kind: an invariant left inside an overridable method, or a required hook given a default because it was convenient.

The tariff codes and duty rates in the example are illustrative and make no claim about any destination's rules.

## The function form: fixed steps and hooks

The varying steps are a frozen dataclass. `classify` and `duty` have no default, and `extra_documents` has one:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class CustomsHooks:
    """The steps that vary by destination. Classification and duty are required."""

    country: str
    classify: Classifier
    duty: DutyRule
    extra_documents: DocumentRule = no_extra_documents
```

`declare_customs` holds everything that must not vary:

```python
def declare_customs(consignment: Consignment, *, hooks: CustomsHooks) -> CustomsDeclaration:
    """Issue a declaration. The order and the invariant steps are fixed; hooks fill the rest."""
    if not consignment.commodities:
        raise CustomsError(f"consignment {consignment.id} has no commodities to declare")
    lines = tuple(
        DeclarationLine(commodity.description, hooks.classify(commodity), commodity.value)
        for commodity in consignment.commodities
    )
    values = [line.value for line in lines]
    declared_value = sum(values[1:], values[0])
    duty = hooks.duty(lines)
    documents = ("commercial invoice", *hooks.extra_documents(consignment))
    return CustomsDeclaration(consignment.id, hooks.country, lines, declared_value, duty, documents)
```

Two of the lookups raise on a miss rather than guess. `lookup_tariff_code` and `schedule_duty` turn a missing table entry into a `CustomsError` that names the commodity or the tariff code, with the original `KeyError` suppressed, and `test_an_unclassified_commodity_is_refused` and `test_a_tariff_code_without_a_duty_rate_is_refused` check both on both forms. Duty rounds half up to the cent: `test_duty_rounds_half_up_to_cents` uses 28.50 at 5%, where half up gives 1.43 and half even would give 1.42.

A hook can't remove the empty-consignment guard or drop the invoice, because neither is a hook. `test_declare_customs_runs_its_steps_in_order` hands in recording hooks and sees `classify` for each commodity, then `duty`, then `extra_documents`. `test_a_declaration_in_two_currencies_is_refused` shows the total step refusing mixed currencies, because `Money` adds only within one currency, and the invoice-first test checks `documents[0]` on both forms.

Leaving out a hook with no default is a `TypeError` at construction, and `test_a_required_hook_cannot_be_left_out` matches `missing 1 required keyword-only argument: 'classify'`. mypy sees the same mistake before the code runs. The test that runs the snippet through the test module's own helper reports:

```text
<string>:9: error: Missing named argument "classify" for "CustomsHooks"  [call-arg]
```

A hook with the wrong signature fails at the same place, and the message names the slot and both types:

```text
<string>:16: error: Argument "duty" to "CustomsHooks" has incompatible type "Callable[[Money, Decimal], Money]"; expected "Callable[[tuple[DeclarationLine, ...]], Money]"  [arg-type]
```

Leaving out `extra_documents` is fine. `SINGAPORE` doesn't pass one, and `test_a_hook_left_out_takes_its_default` shows it takes `no_extra_documents`, so its document list holds the commercial invoice alone.

## Defaults in a Protocol reach only subclasses

It's tempting to describe the hooks as a `Protocol` and put the default `extra_documents` in its body. [PEP 544](https://peps.python.org/pep-0544/), by Levkivskyi, Lehtosalo and Langa, says where that default goes. In its section "Explicitly declaring implementation" it states: "The default implementations cannot be used if the subtype relationship is implicit and only via structural subtyping". A class that lists the protocol as a base inherits the body. A class that merely has matching methods doesn't.

The test fixtures make the difference concrete:

```python
class _DocumentHooks(Protocol):
    def classify(self, commodity: Commodity, /) -> str: ...

    def extra_documents(self, consignment: Consignment, /) -> tuple[str, ...]:
        return ()


class _ExplicitHooks(_DocumentHooks):
    @override
    def classify(self, commodity: Commodity, /) -> str:
        return "0000.00"


class _StructuralHooks:
    def classify(self, commodity: Commodity, /) -> str:
        return "0000.00"
```

`test_protocol_defaults_reach_only_explicit_subclasses` calls `extra_documents` on both. The explicit subclass returns `()`. The structural one raises `AttributeError` with `has no attribute 'extra_documents'`. The type checker agrees that the structural class doesn't match: `test_mypy_requires_every_protocol_member_for_a_structural_match` assigns one to a `DestinationRules` variable and reports:

```text
<string>:19: error: Incompatible types in assignment (expression has type "Structural", variable has type "DestinationRules")  [assignment]
<string>:19: note: "Structural" is missing following "DestinationRules" protocol member:
<string>:19: note:     extra_documents
```

A default that should apply to every caller belongs where every caller reaches it: on a dataclass field, as `CustomsHooks` does, or in the template function. For explicit subclasses of a `Protocol` being nominal and what that does to the checker, see [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}).

## When steps share state: the ABC form

Singapore's hooks are separate functions that share no state. The Netherlands and Germany are a different shape. Both classify with the same EU table and assess duty from the same EU schedule, and they differ in country and documents. Written as hooks, that's the same schedule bound into a hook for each destination. The repetition is the sign that the family has become one thing, and a class says so:

<!-- fmt:off -->
```python
class CustomsDeclarer(ABC):
    """Destinations that share a classification and a schedule. The template is final."""

    country: ClassVar[str]

    def __init__(
        self, *, classification: Mapping[str, str], schedule: Mapping[str, Decimal]
    ) -> None:
        self.classification = classification
        self.schedule = schedule

    def classify(self, commodity: Commodity) -> str:
        return lookup_tariff_code(self.classification, commodity, self.country)

    def duty(self, lines: tuple[DeclarationLine, ...]) -> Money:
        return schedule_duty(lines, schedule=self.schedule)

    @abstractmethod
    def extra_documents(self, consignment: Consignment) -> tuple[str, ...]: ...

    @final
    def declare(self, consignment: Consignment) -> CustomsDeclaration:
        hooks = CustomsHooks(
            country=self.country,
            classify=self.classify,
            duty=self.duty,
            extra_documents=self.extra_documents,
        )
        return declare_customs(consignment, hooks=hooks)
```
<!-- fmt:on -->

The class holds two pieces of state that the function form has to thread through hooks: the classification table and the duty schedule. `extra_documents` is abstract, so a subclass without it can't be built: `test_a_declarer_without_its_documents_cannot_be_built` expects a `TypeError` naming the abstract method, and the `abc` module's [documentation](https://docs.python.org/3/library/abc.html) describes the mechanism. `declare` is final and hands the declarer's own bound methods to `declare_customs`, so the skeleton exists once and the class adds no second copy of the order.

`test_two_destinations_share_the_schedule_and_differ_in_documents` gives equal lines and equal duty and different documents, with the two instances sharing one classification object. `test_the_template_and_the_hooks_give_the_same_declaration` shows the class form and the function form produce an equal declaration for the Netherlands. The shared invariant tests run on both forms through a fixture with two parameters, `hooks` and `template`, so each of those checks runs against both.

The line between the two forms follows from the shared state. One destination, or steps that share nothing, means hooks. A family whose steps read the same state and share code means a class.

## Keeping the skeleton fixed

The failure to guard against is an invariant that lives in an overridable step. The test fixtures show it in a template with a `check` method:

<!-- fmt:off -->
```python
class _OpenDeclarer:
    """A template whose invariant lives in an overridable step."""

    def check(self, consignment: Consignment) -> None:
        if not consignment.commodities:
            raise CustomsError("no commodities to declare")

    def declare(self, consignment: Consignment) -> CustomsDeclaration:
        self.check(consignment)
        lines = tuple(
            DeclarationLine(commodity.description, "0000.00", commodity.value)
            for commodity in consignment.commodities
        )
        zero = Money(Decimal("0.00"), "EUR")
        return CustomsDeclaration(consignment.id, "NL", lines, zero, zero, ("commercial invoice",))


class _ForgetfulDeclarer(_OpenDeclarer):
    @override
    def check(self, consignment: Consignment) -> None:
        return None
```
<!-- fmt:on -->

`test_a_subclass_that_skips_the_base_check_declares_nothing` runs an empty consignment through both. `_OpenDeclarer` raises `no commodities to declare`. `_ForgetfulDeclarer` returns a declaration whose `lines` is `()`. The override didn't call the base version, so the guard is gone, and nothing in the signature said it had to be called. `test_mypy_accepts_an_override_that_skips_the_base_step` runs the same shape through mypy, and the run exits 0 with empty output.

`typing.final` on `declare` is the way to close that gap: the invariant lives in a method the checker refuses to let a subclass override. The [`typing` documentation](https://docs.python.org/3/library/typing.html) says that decorating a method with `@final` "indicates to a type checker that the method cannot be overridden in a subclass", and adds: "There is no runtime checking of these properties." [PEP 591](https://peps.python.org/pep-0591/) specifies the feature. Both halves are in the example. mypy rejects an override:

```text
<string>:7: error: Cannot override final attribute "declare" (previously declared in base class "CustomsDeclarer")  [misc]
```

The runtime doesn't. `test_final_marks_the_template_without_enforcing_it` shows `CustomsDeclarer.declare.__final__` is `True`, and that a subclass overriding `declare` runs its override and returns its own declaration. The decorator marks the method for the checker, and the check happens only where the checker runs. A skeleton that's a plain function has no such gap, because there's nothing to override.

## When not to use it

Write a function when there is one variant.

If every hook is optional, nothing is fixed. That's a pipeline of strategies, and a list of callables says it more directly than a skeleton. If the order itself changes by destination, the thing to model is a list of stages; [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) is the place for clearance stages that can stop a consignment.

A class is the wrong tool when the steps share nothing. Binding unrelated functions into a class to get an overridable method adds inheritance and buys no shared state.

<blockquote class="ai-sidebar" markdown="1">

**Reviewing assistant-written templates.** Asked for "a template method", an assistant may write an abstract base class whose subclasses must remember to call the parent, put an invariant inside an overridable step, or give a `Protocol` default bodies and expect matching classes to inherit them. Paste a prompt that states the form:

> Write `declare_customs` as a function that fixes the order and the invariant steps (refuse an empty consignment, total in one currency, invoice first) and takes `CustomsHooks`, a frozen keyword-only dataclass with `classify` and `duty` undefaulted and `extra_documents` defaulted. Use an ABC only when destinations share a table and a schedule, and mark its `declare` with `typing.final`. No default bodies in a `Protocol`.

If an invariant sits inside a hook, ask for the test where a variant skips it.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/13-template-method-and-the-function-alternative
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 28 items

tests/test_hooks.py::test_declare_customs_runs_its_steps_in_order PASSED [  3%]
tests/test_hooks.py::test_a_hook_left_out_takes_its_default PASSED       [  7%]
tests/test_hooks.py::test_a_declaration_needs_at_least_one_commodity[hooks] PASSED [ 10%]
tests/test_hooks.py::test_a_declaration_needs_at_least_one_commodity[template] PASSED [ 14%]
tests/test_hooks.py::test_a_declaration_in_two_currencies_is_refused[hooks] PASSED [ 17%]
tests/test_hooks.py::test_a_declaration_in_two_currencies_is_refused[template] PASSED [ 21%]
tests/test_hooks.py::test_the_commercial_invoice_is_always_first[hooks] PASSED [ 25%]
tests/test_hooks.py::test_the_commercial_invoice_is_always_first[template] PASSED [ 28%]
tests/test_hooks.py::test_a_required_hook_cannot_be_left_out PASSED      [ 32%]
tests/test_hooks.py::test_an_unclassified_commodity_is_refused[hooks] PASSED [ 35%]
tests/test_hooks.py::test_an_unclassified_commodity_is_refused[template] PASSED [ 39%]
tests/test_hooks.py::test_duty_rounds_half_up_to_cents PASSED            [ 42%]
tests/test_hooks.py::test_a_tariff_code_without_a_duty_rate_is_refused[hooks] PASSED [ 46%]
tests/test_hooks.py::test_a_tariff_code_without_a_duty_rate_is_refused[template] PASSED [ 50%]
tests/test_hooks.py::test_a_declaration_lists_a_line_per_commodity_and_totals_them[hooks] PASSED [ 53%]
tests/test_hooks.py::test_a_declaration_lists_a_line_per_commodity_and_totals_them[template] PASSED [ 57%]
tests/test_hooks.py::test_every_value_in_the_model_is_frozen PASSED      [ 60%]
tests/test_protocol_defaults.py::test_protocol_defaults_reach_only_explicit_subclasses PASSED [ 64%]
tests/test_static.py::test_mypy_rejects_overriding_the_final_template PASSED [ 67%]
tests/test_static.py::test_mypy_accepts_an_override_that_skips_the_base_step PASSED [ 71%]
tests/test_static.py::test_mypy_checks_hooks_at_construction[missing-required] PASSED [ 75%]
tests/test_static.py::test_mypy_checks_hooks_at_construction[wrong-signature] PASSED [ 78%]
tests/test_static.py::test_mypy_requires_every_protocol_member_for_a_structural_match PASSED [ 82%]
tests/test_template.py::test_the_template_and_the_hooks_give_the_same_declaration PASSED [ 85%]
tests/test_template.py::test_a_declarer_without_its_documents_cannot_be_built PASSED [ 89%]
tests/test_template.py::test_final_marks_the_template_without_enforcing_it PASSED [ 92%]
tests/test_template.py::test_a_subclass_that_skips_the_base_check_declares_nothing PASSED [ 96%]
tests/test_template.py::test_two_destinations_share_the_schedule_and_differ_in_documents PASSED [100%]

============================== 28 passed in 2.30s ==============================
Success: no issues found in 9 source files
```

The suite has 21 test functions and 28 cases. Seventeen of those cases are in the hooks module's tests, and the rest cover the class form, the `Protocol` fixture and the static witnesses.

**Experiment one: remove `@final`.** In a scratch copy, delete the `@final` line above `declare` in `CustomsDeclarer`. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then the member's mypy run gives:

```text
E       assert 0 == 1
tests/test_static.py:47: AssertionError
E       AssertionError: assert False is True
tests/test_template.py:74: AssertionError
FAILED tests/test_static.py::test_mypy_rejects_overriding_the_final_template
FAILED tests/test_template.py::test_final_marks_the_template_without_enforcing_it
2 failed, 26 passed in 2.34s
tests/test_template.py:41: error: Unused "type: ignore" comment  [unused-ignore]
Found 1 error in 1 file (checked 9 source files)
```

The runtime test fails because `__final__` is no longer set. The static test fails because the override snippet is now accepted. The member's own mypy run reports the unused `type: ignore` on the `_OverridingDeclarer` fixture, the subclass that overrides `declare` in the runtime test, because the ignore no longer has an error to cover.

**Experiment two: remove the no-commodities guard.** In a fresh scratch copy, delete the two-line `if not consignment.commodities:` block in `declare_customs`. The same filtered run, then the member's mypy run, gives:

```text
E       IndexError: list index out of range
E       IndexError: list index out of range
E       IndexError: list index out of range
FAILED tests/test_hooks.py::test_a_declaration_needs_at_least_one_commodity[hooks]
FAILED tests/test_hooks.py::test_a_declaration_needs_at_least_one_commodity[template]
FAILED tests/test_template.py::test_a_subclass_that_skips_the_base_check_declares_nothing
3 failed, 25 passed in 2.18s
Success: no issues found in 9 source files
```

Both cases of `test_a_declaration_needs_at_least_one_commodity` fail, and so does the Netherlands check at the end of `test_a_subclass_that_skips_the_base_check_declares_nothing`. The next step in the function, taking the first of the values, hits an empty list. Without the guard the failure is an `IndexError` from a later line and not a refusal that names the consignment. mypy stays green, because nothing in a type says a consignment must have a commodity.

## What you can do now

- Say what dissolves and what survives: `declare_customs` takes `CustomsHooks`, and the ABC form survives where steps share state.
- Write the skeleton: `test_a_required_hook_cannot_be_left_out` and `test_a_hook_left_out_takes_its_default`, with the guard and the invoice outside every hook.
- Place a default where it is reached: `test_protocol_defaults_reach_only_explicit_subclasses` against a dataclass default.
- Read `typing.final`: a type-check error on an override, and a runtime `__final__` attribute that stops nothing.
- Choose between hooks and the ABC form: `CustomsDeclarer` and `test_two_destinations_share_the_schedule_and_differ_in_documents` share a schedule and state, so the ABC form fits.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Template Method. [PEP 544](https://peps.python.org/pep-0544/) covers protocols and explicit subclassing, [PEP 591](https://peps.python.org/pep-0591/) and the [`typing.final` documentation](https://docs.python.org/3/library/typing.html) cover final methods, and the [`abc`](https://docs.python.org/3/library/abc.html) and [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) documentation cover abstract methods, `kw_only` and field defaults.

Luciano Ramalho's *Fluent Python*, second edition, has a chapter titled "Inheritance: For Better or For Worse" on when subclassing pays for itself. Brett Slatkin's *Effective Python*, third edition, has short rules on classes and typing in the same spirit. Both are in the hub's list and on the [bibliography page]({{ '/bibliography/' | relative_url }}).
