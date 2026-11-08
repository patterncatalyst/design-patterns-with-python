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

A pattern name is the shortest design review comment there is. "This should be a Strategy" packs a family of interchangeable algorithms, a caller that picks one, and a promise that the caller does not care which. The Gang of Four catalogue exists largely to give teams that vocabulary, so that a design discussion can run at the speed of a sentence instead of a whiteboard session.

The vocabulary only works when everyone attaches the same contract to the same word. Python complicates this in two ways. The mechanism behind a pattern is often lighter than the 1994 structure, so a Strategy may be a function and the word "Strategy" no longer implies a class hierarchy. And two unrelated things share one name, so "decorator" can mean a wrapper object or a line starting with `@`. A team that doesn't settle these questions in its names settles them in review threads.

AI coding assistants add a second reader to the same code. An assistant that is asked for "a factory" or "a strategy" may produce something that matches the name and not the intent, so the reviewer checks the result against the intent. The practical question is what the name lets you verify once the assistant has produced its diff. A name that states the role and the mechanism gives the reviewer something specific to look for in the diff, and it gives the assistant the same specific target in the prompt.

{% include excalidraw.html name="04-naming-patterns-for-teams-and-ai" caption="Figure 4.1: One pattern name, two readers. A reviewer and an AI assistant read the same name for the same contract; naming the Python mechanism as well, a callable type alias rather than a class hierarchy, keeps both readers on the idiomatic shape." %}

## A name is a checkable claim

Robert Martin's treatment of meaningful names in *Clean Code* argues that a name should say why something exists, what it does and how it is used, and that a name needing a comment has failed. Martin Fowler's *Refactoring* lists Mysterious Name as a code smell for the same reason: when a reader cannot tell what an identifier promises, every use of it costs a trip to the definition. Both are arguments about cost. A name that is wrong or vague makes each later reader pay.

Pattern names are compressed claims. Calling something a `RateStrategy` asserts at least three things: there are several interchangeable rate computations, the caller selects one, and the caller depends only on what they share. Each assertion can be checked. Are there several? Does anything select between them? Is the shared surface narrow? A reviewer who reads the name and then finds a single implementation, selected by an `if` inside the class, has found a mismatch between claim and code without reading anything else.

A good name produces a short list of questions the diff can answer. A name like `Helper` produces none, so it never fails review and never helps.

## Where the pattern name lives in Python

In a language where a pattern needs a class, the class name carries the pattern name, and the habit of appending the pattern as a suffix follows. Python gives the pattern name more places to live, and most of them are better than a suffix.

The first is the type alias. In the [three-way split example]({{ '/examples/03-three-way-split/' | relative_url }}), the pricing contract is a single declaration, `type PricingRule = Callable[[Consignment], Money]`. The alias states the role in the name and the mechanism in the right-hand side. A reader who sees `PricingRule` knows what the parameter is for, and a reader who follows it to the definition sees that a plain callable satisfies it. The functions `flat_rate` and `per_kg` are then ordinary functions named for what they compute, not for the role they play. See the [`type` statement](https://docs.python.org/3/reference/simple_stmts.html#type) for the alias syntax.

The second is the docstring. A one-line docstring can name the pattern when the pattern is the reason the code exists: the stack of calculators that wrap one another is a Decorator, and saying so once, where the class is defined, tells reviewers which contract to check.

The third is the pull request description. It records the decision: which pattern, which bucket, and why. A description that says "pricing is now a `PricingRule` callable; the class hierarchy was removed" lets a reviewer verify the diff against a stated intent. A description that says "refactored pricing" cannot be checked against anything.

Around all three sit the conventions in [PEP 8](https://peps.python.org/pep-0008/#naming-conventions). Classes use `CapWords`, functions and variables use `lower_case_with_underscores`, and constants use `UPPER_CASE`. These conventions carry information. A reader who sees `per_kg` expects a function and one who sees `CarrierGateway` expects a class or protocol, so a name that breaks the convention sends a false signal. In the example, the registry of carrier factories is `GATEWAYS`, a module-level constant keyed by the carrier codes `FASTLINE` and `AIRCO`, and the convention tells the reader at a glance that it is a fixed table and not a class.

## Names across the consignment lifecycle

Pattern labels are not the only names that need care. The consignment lifecycle in the example is a sequence of facts: `Booked`, `Loaded`, `Departed`, `Cleared` and `Delivered`. Each is a frozen dataclass, and together they make up the `HandlingEvent` union that a `TrackingHistory` holds.

The past participle is the convention for events. An event records something that already happened and can't be undone, so the name is a statement of fact. Compare `BookingHandler` or `LoadState`, which name a mechanism or a mode. The event names describe the domain, the domain is what the whole team shares, and a reviewer who knows shipping can check each name against the business without knowing anything about the code.

The `describe` function dispatches on the event type, with one registered case per class, so a new event type shows up in the diff as a new name and a new case. Single dispatch won't report a missing case, where `mypy --strict` reports an uncovered union member in a `match` that ends in `assert_never`. The list of names is the list of cases to cover, so the reviewer is the check here, and a missing case is visible to anyone who reads the names.

A prompt that says "add a `Delayed` event alongside `Departed` and `Cleared`" names an existing family, and a reviewer can check whether the new class follows the same frozen, slotted shape. A prompt that says "add a status field" names nothing, and whatever comes back must be judged from scratch.

## Names that hide the bucket

The three-way split sorts every pattern into dissolved, survives or needs disambiguating, and a good name tells the reader which. Names built from a pattern suffix often hide it.

`RateStrategy` is the clearest case. The suffix says Strategy, but it doesn't say whether the design is an abstract base class with subclasses, a protocol, or a callable. All three are plausible, and only one is idiomatic for a single-method contract. `PricingRule` names the role, and defining it as a callable alias names the mechanism. The bucket, dissolved, is then visible in the code and not only in the author's head. A function such as `per_kg` is then a legitimate implementation, and a reviewer doesn't need to ask where the base class went.

`ConsignmentFactory` has the same problem. The word Factory promises a creation seam, but in Python a function already is one. A function named `make_consignment` says what it produces and what kind of thing it is, and it leaves room for the function to grow keyword arguments without becoming a class. If a class is later needed because creation has state, the name `ConsignmentFactory` can be earned then, and the diff that introduces it is the record of why.

The suffixes `Manager` and `Helper` hide more. They name no role or contract. A `ConsignmentManager` might hold state, wrap a gateway or validate input, and a reviewer can't tell which from the name. Because the name can't be wrong, it can't be checked, and the class collects responsibilities until someone splits it. When a name like this appears in a diff, the useful review question is which job the class does, since the answer is usually the name it should have had: a `CarrierGateway` for the boundary to a carrier, a `PricingRule` for a computation, a `TrackingHistory` for an ordered record.

Fowler's *Refactoring* gives the remedy names of its own: Rename Variable and Rename Field, and Change Function Declaration for functions. A rename is a small, safe change, and it's worth making as soon as a better name is clear.

## Keeping Decorator and `@decorator` apart in names

The headline disambiguation in this book is the Decorator pattern against the `@decorator` syntax. They are different things.

The Decorator pattern is a wrapper object that adds behaviour while keeping the wrapped object's interface, composed at runtime so that stacks are data. In the example it is `Surcharge`, which holds an inner `RateCalculator` and a fee and adds the fee to whatever the inner calculator prices. The name is the domain concept: a surcharge on a rate. It doesn't end in `Decorator`, and it doesn't need to. The docstring can name the pattern, and the class name stays in the domain.

The `@decorator` syntax is a function rebinding at definition time. In the example it is `audited(sink)`, applied to `quote_carrier` with `@audited(audit_trail.append)`. The name is a past participle describing the property the function now has: it is audited. Neither name contains the word decorator, because the word would be wrong for one of the two.

The rule for review follows from this. Use "Decorator" only for the pattern, and say "decorator syntax" or "the `@` form" for the other. A comment that reads "this decorator should be composable at runtime" is ambiguous, because only the pattern can be reassembled per consignment and the syntax cannot. A comment that says "this should be a Decorator, not an `@`-applied function" states the intended mechanism and can be checked against the diff.

## Steering an AI assistant with names

A prompt is a place where names do work. Telling an assistant to "use the Strategy pattern" leaves the mechanism open, and the reviewer will have to decide afterwards whether a class hierarchy is acceptable. Telling it to "define `PricingRule` as a callable type alias and write `per_kg` as a plain function that fits it" names the role and the mechanism, and the result can be compared with the instruction line by line.

Three practices keep prompts and reviews aligned.

State the bucket. "This is a dissolved pattern: no base class" is one sentence, and it turns a vague preference into a testable constraint.

Name the existing vocabulary. Point at `HandlingEvent`, `CarrierGateway` or `Consignment` by name and ask for code that follows them. The names anchor the request in code that already exists and has already been reviewed.

Give the disambiguation up front. "A Decorator pattern object, not an `@` function" costs one phrase and removes the commonest source of mismatch.

## Reviewing a name an assistant attached to its output

Code may come back with a pattern name attached, in a class name or a summary. Treat the name as a claim and run the same checks as for a colleague's code.

Start with the contract. If the name is `RateStrategy`, find the several interchangeable implementations and the place where one is chosen. If there is one implementation, the name is premature, and the better name is the plain function it contains.

Then check the mechanism. If the intended shape was a callable alias and the diff adds an abstract base class with a single method, the name may be right and the shape wrong. Say which in the review comment and point at the alias that should replace the hierarchy.

Then check for the disambiguation. If the summary says "added a decorator", find out which one. A new `Surcharge`-style wrapper class and a new `@audited`-style function have different tests and different failure modes.

Finally, check the vocabulary against the domain. A name such as `ShipmentTracker` for something that is really a `TrackingHistory` introduces a second word for an existing concept. Mismatched domain words are cheap to reject in review and costly to find a year later.

## When a name stops matching the code

Names drift. A function called `per_kg` gains a minimum charge, a `Surcharge` gains a second fee, a `PricingRule` ends up holding state. Each change is small and reasonable, and the name slowly stops being true.

The drift is a smell in Fowler's terms, and the fix is a rename. Editors rename across a codebase, and in annotated code `mypy --strict` reports a reference left under the old name. Do it in its own commit, so that the diff shows a rename and nothing else and a reviewer can approve it in seconds.

Sometimes the right move is not a better label but no label. When a design that was once a Strategy has shrunk to a single function called from one place, the pattern name is documentation of something that no longer exists. Remove the name from the docstring, delete the alias if nothing else uses it, and let the function be a function. The inverse also holds: when a plain callable grows state, validation and a second method, it has become a class, and the right name for the class describes its role in the domain, with the pattern named in the docstring if it helps.

## What you can do now

- Treat a name as a checkable claim: `RateStrategy` and its three questions.
- Place the name: `type PricingRule = Callable[[Consignment], Money]`, the docstring, the PR description, and `GATEWAYS` under PEP 8.
- Name lifecycle events as facts: `Booked` through `Delivered` in `HandlingEvent`.
- Rename names that hide the bucket: `PricingRule`, `make_consignment`, and the Manager and Helper suffixes.
- Keep the two decorators apart: `Surcharge` against `audited(sink)`.
- Write a prompt that names `PricingRule` and `per_kg`, and review the reply with the four checks.
- Rename in its own commit, or retire the label.

## For deeper coverage

For the vocabulary itself, the Gang of Four catalogue, *Design Patterns: Elements of Reusable Object-Oriented Software*, is the source of the pattern names used throughout this book, and its Introduction, on what a pattern name adds to a design vocabulary, is the reference for treating them as a shared language. Robert C. Martin's *Clean Code: A Handbook of Agile Software Craftsmanship* covers meaningful names in depth, including the cost of vague names and noise words. Martin Fowler's *Refactoring: Improving the Design of Existing Code*, Second Edition, covers the Mysterious Name smell and the Rename refactorings. The full citations are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
