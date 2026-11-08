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

A customs declaration has an order, and destinations vary only some of its steps. The familiar base class lets one destination override a preparation step, skip the base version and issue a declaration with no commodity lines, and mypy accepts it. A function that takes the varying steps fixes the order with nothing to override.

{% include excalidraw.html name="13-template-method-and-the-function-alternative" described="true" caption="Figure 13.1: One customs skeleton, two ways to vary it. declare_customs fixes the order and the invariant steps and takes hooks for the rest; CustomsDeclarer keeps the same skeleton final and lets a family of destinations share its schedule." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-13-template-method-and-the-function-alternative" markdown="1">
Read from the top down, in the order `declare_customs` runs. Two arrows feed the accent box at the top. From the left, `CustomsHooks` supplies functions per destination, with Singapore shown. From the right, `CustomsDeclarer` supplies bound methods that become hooks, and `NetherlandsDeclarer` and `GermanyDeclarer` point up into it. Below the box, the grey steps are invariant and the blue ones are hooks: refuse an empty consignment, classify each commodity, total in one currency, assess duty, then the commercial invoice first. A side box, `extra_documents` with the default "none", feeds that last step. The column ends at `CustomsDeclaration`.
</div>
</details>

The figure shows one skeleton fed either by hooks or by a class's bound methods.

## Pattern: Template Method

### The problem

A declaration refuses a consignment with nothing in it, classifies each commodity, totals the declared value in one currency, assesses duty, then lists the documents with the commercial invoice first. Destinations differ in how they classify, how they assess duty and which extra documents they want. They shouldn't differ in the order, or in whether the refusal happens. The force is a sequence that has to hold across variants that differ in a few steps.

Three designs fail quietly:

- **A base class with overridable steps.** A destination subclass overrides a preparation step, forgets to call the base version, and issues a declaration with no commodity lines. mypy accepts it.
- **A bag of hooks that all have defaults.** A destination omits its classification and still gets a declaration, because nothing is missing as far as the type is concerned.
- **A `Protocol` with default method bodies.** It suggests every matching class inherits the defaults, and a class that matches structurally doesn't.

### The solution

A **Template Method** fixes the order of a procedure in one place and lets variants supply only the steps that differ.

**Bucket: dissolves.** A function that takes the varying steps as arguments fixes the order as well as a base class does; the inheritance form survives where a family of variants shares state and code across several steps.

*Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994) builds it with a base class. [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) left open where the line falls for this pattern; the sections below draw it.

A skeleton has three kinds of step:

| Kind | Default | A variant that leaves it out |
| --- | --- | --- |
| Invariant | not a hook | can't touch it |
| Required hook | none | fails at construction |
| Optional hook | yes | made a decision |

The mistake to look for is a step of the wrong kind: an invariant inside an overridable method, or a required hook given a default because it was convenient. Each hook is a strategy in the sense of [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}). The tariff codes and duty rates are illustrative and make no claim about any destination's rules.

### How Python models it

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

A hook can't remove the empty-consignment guard or drop the invoice, because neither is a hook. The hooks run in order: `classify` for each commodity, then `duty`, then `extra_documents`. Mixed currencies are refused at the total, because `Money` adds only within one currency. `lookup_tariff_code` and `schedule_duty` turn a missing table entry into a `CustomsError` naming the commodity or the tariff code, with the original `KeyError` suppressed. Duty rounds half up to the cent: 28.50 at 5% gives 1.43, where half even would give 1.42.

Leaving out a required hook is a `TypeError` at construction (`missing 1 required keyword-only argument: 'classify'`), and mypy sees it first:

```text
<string>:9: error: Missing named argument "classify" for "CustomsHooks"  [call-arg]
```

A hook with the wrong signature fails at the same place, and the message names the slot and both types:

```text
<string>:16: error: Argument "duty" to "CustomsHooks" has incompatible type "Callable[[Money, Decimal], Money]"; expected "Callable[[tuple[DeclarationLine, ...]], Money]"  [arg-type]
```

Leaving out `extra_documents` is fine. `SINGAPORE` doesn't pass one, takes `no_extra_documents`, and lists the commercial invoice alone.

### Defaults in a Protocol reach only subclasses

It's tempting to describe the hooks as a `Protocol` and put the default `extra_documents` in its body. [PEP 544](https://peps.python.org/pep-0544/), by Levkivskyi, Lehtosalo and Langa, says where that default goes. Its section "Explicitly declaring implementation" states: "The default implementations cannot be used if the subtype relationship is implicit and only via structural subtyping". A class that lists the protocol as a base inherits the body. A class that merely has matching methods doesn't:

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

`extra_documents` on the explicit subclass returns `()`. On the structural one it raises `AttributeError`. mypy agrees that the structural class doesn't match:

```text
<string>:19: error: Incompatible types in assignment (expression has type "Structural", variable has type "DestinationRules")  [assignment]
<string>:19: note: "Structural" is missing following "DestinationRules" protocol member:
<string>:19: note:     extra_documents
```

Put a default that should apply to every caller where every caller reaches it: on a dataclass field, as `CustomsHooks` does, or in the template function. For explicit `Protocol` subclasses being nominal, see [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}).

### When steps share state: the ABC form

Singapore's hooks share no state. The Netherlands and Germany both classify with the same EU table and assess duty from the same EU schedule, and differ in country and documents. Written as hooks, that's the same schedule bound into each destination's hook. The repetition says the family is one thing, and a class says so:

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

The class holds the classification table and the duty schedule, which the function form would thread through hooks. `extra_documents` is abstract, so a subclass without it raises `TypeError` at construction; the [`abc` documentation](https://docs.python.org/3/library/abc.html) describes the mechanism. `declare` is final and hands the declarer's bound methods to `declare_customs`, so the order exists once.

The two destinations give equal lines and duty, different documents, and share one classification object. For the Netherlands the class form and the function form produce equal declarations, and every invariant check runs against both.

| Shape | Form |
| --- | --- |
| One destination, or steps that share nothing | hooks |
| A family whose steps read the same state and share code | a class with a final template |

### Keeping the skeleton fixed

The failure to guard against is an invariant in an overridable step:

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

With an empty consignment, `_OpenDeclarer` raises `no commodities to declare`, and `_ForgetfulDeclarer` returns a declaration whose `lines` is `()`. The override didn't call the base version, so the guard is gone, and nothing in the signature said it had to be called. mypy accepts the shape with no output.

`typing.final` on `declare` closes that gap for the checker. The [`typing` documentation](https://docs.python.org/3/library/typing.html) says `@final` on a method "indicates to a type checker that the method cannot be overridden in a subclass", and adds: "There is no runtime checking of these properties." [PEP 591](https://peps.python.org/pep-0591/) specifies the feature. mypy rejects an override:

```text
<string>:7: error: Cannot override final attribute "declare" (previously declared in base class "CustomsDeclarer")  [misc]
```

The runtime doesn't. `CustomsDeclarer.declare.__final__` is `True`, and a subclass that overrides `declare` still runs its override. The check happens only where the checker runs. A skeleton that's a plain function has no such gap, because there's nothing to override.

## When not to use it

- **Template Method.** Write a function when there is one variant. If every hook is optional, nothing is fixed: that's a pipeline of strategies, and a list of callables says it more directly. If the order itself changes by destination, model a list of stages; [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) covers clearance stages that can stop a consignment. A class is the wrong tool when the steps share nothing: binding unrelated functions into a class adds inheritance and buys no shared state.

> **🤖 Explore with your agent**
>
> "Write `declare_customs` as a function that fixes the order and the invariant steps (refuse an empty consignment, total in one currency, invoice first) and takes `CustomsHooks`, a frozen keyword-only dataclass with `classify` and `duty` undefaulted and `extra_documents` defaulted. Use an ABC only when destinations share a table and a schedule, and mark its `declare` with `typing.final`. No default bodies in a `Protocol`."
>
> If an invariant sits inside a hook, ask for a test where a variant skips it.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/13-template-method-and-the-function-alternative
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 28 cases pass, the shared invariants against both forms, and mypy reports `Success: no issues found in 9 source files`. Two experiments, each in a scratch copy:

- **Remove `@final` from `declare`.** Two tests fail: `__final__` is no longer set, and mypy now accepts the override snippet. mypy on the member reports an `Unused "type: ignore" comment` on the overriding fixture, because the ignore has no error left to cover.
- **Remove the no-commodities guard.** Three tests fail with `IndexError: list index out of range` from the totalling step, a later line, instead of a refusal that names the consignment. mypy stays green, because no type says a consignment must have a commodity.

## What you can do now

- Say what dissolves and what survives: `declare_customs` takes `CustomsHooks`, and the ABC form survives where steps share state.
- Write a skeleton with required hooks undefaulted, optional hooks defaulted, and the guard and the invoice outside every hook.
- Put a default where every caller reaches it, on a dataclass field, not in a `Protocol` body.
- Read `typing.final`: a type-check error on an override, and a runtime `__final__` attribute that stops nothing.
- Choose between hooks and the ABC form: `CustomsDeclarer` fits because its destinations share a schedule and state.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Template Method. [PEP 544](https://peps.python.org/pep-0544/) covers protocols and explicit subclassing, [PEP 591](https://peps.python.org/pep-0591/) and the [`typing.final` documentation](https://docs.python.org/3/library/typing.html) cover final methods, and the [`abc`](https://docs.python.org/3/library/abc.html) and [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) documentation cover abstract methods, `kw_only` and field defaults.

Luciano Ramalho's *Fluent Python*, second edition, has a chapter titled "Inheritance: For Better or For Worse" on when subclassing pays for itself. Brett Slatkin's *Effective Python*, third edition, has short rules on classes and typing in the same spirit. Both are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
