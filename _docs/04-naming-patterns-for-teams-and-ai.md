---
title: "Naming patterns for teams and AI assistants"
order: 4
layout: tutorial
sectionid: docs
part: "why-python-is-different"
description: "How to name pattern roles and Python mechanisms so reviewers and AI assistants can check a diff against the contract the name promises."
---

## Learning objectives

By the end of this chapter you can:

- Explain why a pattern name is a claim about a contract that a reviewer can check against a diff.
- Place the pattern name in a type alias, a docstring and a pull request description, and follow PEP 8 for the identifiers around it.
- Choose names for the consignment lifecycle that carry a past-tense fact rather than a pattern label.
- Spot names that hide which of the three buckets a design belongs to, and rename them.
- Keep the Decorator pattern and the `@decorator` syntax apart in class names, function names and review comments.
- Write a prompt for an AI assistant and a review of its output that use the same names.
- Recognise when a name has stopped matching its code and apply a rename or retire the label.

## Why this matters

"This should be a Strategy" packs a family of interchangeable algorithms, a caller that picks one, and a promise that the caller doesn't care which. That vocabulary works only when everyone attaches the same contract to the same word, and Python breaks the link twice:

- **The mechanism is lighter.** A Strategy may be a function, so the word no longer implies a class hierarchy.
- **One word means two things.** "Decorator" can be a wrapper object or a line starting with `@`.

A team that doesn't settle these in its names settles them in review threads. A prompt to an AI assistant is one more place the name has to carry the contract: a name that states the role and the mechanism gives the prompt a specific target and the reviewer something specific to look for in the diff.

{% include excalidraw.html name="04-naming-patterns-for-teams-and-ai" described="true" caption="Figure 4.1: One pattern name, two readers. A reviewer and an AI assistant read the same name for the same contract; naming the Python mechanism as well, a callable type alias rather than a class hierarchy, keeps both readers on the idiomatic shape." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-04-naming-patterns-for-teams-and-ai" markdown="1">
At the top, a request names a pattern: add a pricing rule to the rate quote. It splits two ways. On the left, "Names only the pattern" (the label says nothing about the mechanism) leads to `RateStrategy`, a class suffix that suggests a subclass per rule, and then to "Read as a class hierarchy": the reviewer expects the 1994 structure. On the right, "Names the role and the mechanism" (the label points at the idiom) leads to `PricingRule`, a callable type alias, and `per_kg`, a function that fits it, both feeding "Read as a callable": the reviewer checks signature and types. Both paths end at the bottom box, "Reviewer and assistant check the same contract: one name, one claim to verify", the left path with a dashed arrow.
</div>
</details>

## A name is a checkable claim

Robert Martin's *Clean Code* argues that a name should say why something exists, what it does and how it's used. Martin Fowler's *Refactoring* lists Mysterious Name as a smell: when a reader can't tell what an identifier promises, every use costs a trip to the definition.

A pattern name is a compressed claim, and each part can be checked against the diff. `RateStrategy` asserts:

| Claim | Check |
| --- | --- |
| Several interchangeable rate computations exist | Count the implementations |
| The caller selects one | Find the place that chooses |
| The caller depends only on what they share | Read the shared surface |

One implementation, chosen by an `if` inside the class, fails the name without anything else being read. A name like `Helper` raises no questions, so it never fails review and never helps.

## Where the pattern name lives in Python

Where a pattern needs a class, the class name carries the pattern, and a suffix follows. Python offers better places:

| Place | What it carries | From the [three-way split example]({{ '/examples/03-three-way-split/' | relative_url }}) |
| --- | --- | --- |
| Type alias | The role in the name, the mechanism on the right | `type PricingRule = Callable[[Consignment], Money]` |
| Docstring | The pattern, once, where it's the reason the code exists | Calculators that wrap one another form a Decorator |
| Pull request description | The decision: which pattern, which bucket, why | "Pricing is now a `PricingRule` callable; the class hierarchy was removed" |

With the alias in place, `flat_rate` and `per_kg` are ordinary functions named for what they compute. See the [`type` statement](https://docs.python.org/3/reference/simple_stmts.html#type) for the syntax. "Refactored pricing" in a pull request can't be checked against anything.

[PEP 8](https://peps.python.org/pep-0008/#naming-conventions) carries information too: `CapWords` for classes, `lower_case_with_underscores` for functions and variables, `UPPER_CASE` for constants. A reader who sees `per_kg` expects a function, and one who sees `CarrierGateway` expects a class or protocol. `GATEWAYS`, keyed by the carrier codes `FASTLINE` and `AIRCO`, reads at a glance as a fixed module-level table.

## Names across the consignment lifecycle

The lifecycle events are `Booked`, `Loaded`, `Departed`, `Cleared` and `Delivered`: frozen dataclasses that make up the `HandlingEvent` union a `TrackingHistory` holds. An event records something that already happened, so its name is a past-tense fact. `BookingHandler` or `LoadState` would name a mechanism or a mode. Anyone who knows shipping can check the event names against the business without reading the code.

`describe` dispatches on the event type with one registered case per class, so a new event shows up in the diff as a new name and a new case. Single dispatch won't report a missing case; `mypy --strict` reports an uncovered union member only in a `match` ending in `assert_never`. With `singledispatch`, the list of names is the list of cases, and the reviewer is the check.

"Add a `Delayed` event alongside `Departed` and `Cleared`" names an existing family, and the reply can be checked for the same frozen, slotted shape. "Add a status field" names nothing.

## Names that hide the bucket

A good name tells the reader whether a design dissolved, survives or needs disambiguating. Pattern suffixes often hide it:

| Name | Problem | Better |
| --- | --- | --- |
| `RateStrategy` | Could be an ABC with subclasses, a protocol or a callable | `PricingRule` as a callable alias, with `per_kg` as an implementation |
| `ConsignmentFactory` | Promises a creation seam a function already is | `make_consignment`, which can grow keyword arguments without becoming a class |
| `ConsignmentManager`, `...Helper` | Names no role or contract, so it can't be wrong and collects responsibilities | The job it does: `CarrierGateway`, `PricingRule`, `TrackingHistory` |

If creation later needs state, `ConsignmentFactory` can be earned then, and the diff that introduces it records why. For a Manager in a diff, ask which job the class does; the answer is usually its name.

Fowler gives the remedies names: Rename Variable, Rename Field, and Change Function Declaration. A rename is small and safe, so make it as soon as the better name is clear.

## Keeping Decorator and `@decorator` apart in names

| | Decorator pattern | `@decorator` syntax |
| --- | --- | --- |
| What it is | A wrapper object with the wrapped object's interface, composed at run time | A function rebinding at definition time |
| In code | `Surcharge`: an inner `RateCalculator` plus a fee | `@audited(audit_trail.append)` on `quote_carrier` |
| How it's named | The domain concept, a surcharge on a rate | A participle for the property the function now has |

Neither name contains "decorator", because the word would be wrong for one of them. The docstring can name the pattern; the class name stays in the domain.

In review, use "Decorator" only for the pattern, and say "decorator syntax" or "the `@` form" for the other. "This decorator should be composable at run time" is ambiguous, since only the pattern can be reassembled per consignment. "This should be a Decorator, not an `@`-applied function" can be checked against the diff.

## Steering an AI assistant with names

"Use the Strategy pattern" leaves the mechanism open, and the reviewer decides afterwards whether a class hierarchy is acceptable. "Define `PricingRule` as a callable type alias and write `per_kg` as a plain function that fits it" names the role and the mechanism, so the result can be compared with the instruction line by line.

- **State the bucket.** "This is a dissolved pattern: no base class" turns a preference into a testable constraint.
- **Name the existing vocabulary.** Point at `HandlingEvent`, `CarrierGateway` or `Consignment` and ask for code that follows them.
- **Disambiguate up front.** "A Decorator pattern object, not an `@` function" costs one phrase.

## Reviewing a name an assistant attached to its output

Treat a pattern name in a class or a summary as a claim, as for a colleague's code:

1. **Contract.** For `RateStrategy`, find the several implementations and the place one is chosen. With one implementation, the better name is the plain function it contains.
2. **Mechanism.** If the intended shape was a callable alias and the diff adds an ABC with one method, the name may be right and the shape wrong. Say which, and point at the alias.
3. **Disambiguation.** "Added a decorator": a `Surcharge`-style wrapper and an `@audited`-style function have different tests and different failure modes.
4. **Domain vocabulary.** `ShipmentTracker` for what is a `TrackingHistory` adds a second word for one concept. That's cheap to reject now and costly to find a year later.

## When a name stops matching the code

`per_kg` gains a minimum charge, a `Surcharge` gains a second fee, a `PricingRule` ends up holding state. Each change is reasonable, and the name slowly stops being true. Rename it: editors rename across a codebase, and `mypy --strict` reports a reference left under the old name. Do it in its own commit, so the diff is a rename and nothing else.

Sometimes the right move is no label. A former Strategy that has shrunk to one function called from one place documents something that no longer exists: drop the name from the docstring, delete the alias if nothing else uses it, and let the function be a function. The reverse holds too. A callable that grows state, validation and a second method has become a class; name it for its role in the domain, and name the pattern in the docstring if that helps.

## What you can do now

- Treat a name as a checkable claim: `RateStrategy` and its three questions.
- Place the name: `type PricingRule = Callable[[Consignment], Money]`, the docstring, the PR description, and `GATEWAYS` under PEP 8.
- Name lifecycle events as facts: `Booked` through `Delivered` in `HandlingEvent`.
- Rename names that hide the bucket: `PricingRule`, `make_consignment`, and the Manager and Helper suffixes.
- Keep the two decorators apart: `Surcharge` against `audited(sink)`.
- Write a prompt that names `PricingRule` and `per_kg`, and review the reply with the four checks.
- Rename in its own commit, or retire the label.

## For deeper coverage

For the vocabulary itself, the Gang of Four catalogue, *Design Patterns: Elements of Reusable Object-Oriented Software*, is the source of the pattern names used throughout, and its Introduction, on what a pattern name adds to a design vocabulary, is the reference for treating them as a shared language. Robert C. Martin's *Clean Code: A Handbook of Agile Software Craftsmanship* covers meaningful names in depth, including the cost of vague names and noise words. Martin Fowler's *Refactoring: Improving the Design of Existing Code*, Second Edition, covers the Mysterious Name smell and the Rename refactorings. The full citations are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
