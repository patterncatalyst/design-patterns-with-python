---
title: "Patterns as decisions under forces"
order: 1
layout: tutorial
sectionid: docs
part: "why-not-gof"
description: "A design pattern records a decision made under competing forces, and its Consequences are the ledger. The rate quote shows how the dominant force picks the shape."
---

## Learning objectives

By the end of this chapter you can:

- State what a pattern records: a context, competing pressures, a resolution and its Consequences.
- Name the template sections the Gang of Four catalogue uses and say why Consequences is the one that supports a decision.
- List the pressures on a rate quote and the party that owns the schedule each one changes on.
- Choose between a pricing function over a `Tariff`, separate pricing-rule callables and a `RateCalculator` Protocol by naming the dominant pressure.
- Explain why a pressure can outlive the structure that once resolved it, and ask "is the force still here?" of every pattern.
- Recognise the case where the pressures are too weak to justify any pattern.

## Why this matters

Read as a catalogue of shapes, a pattern is a class diagram you apply when the situation looks familiar. Someone sees a family of rating rules, remembers an abstract base class with three subclasses, and builds it whether or not the rules ever vary.

The catalogue itself frames a pattern as the compromise left after competing pressures are traded off. The useful questions are which pressures are present, which one dominates, and what the pattern costs. They also make a second question answerable: when the language changes, does the pressure go away, or only the mechanism that resolved it?

The running problem is quoting a rate for a consignment. Its inputs change on different schedules, and its outputs get argued over later. The figure shows the four pressures and the choice they bear on.

{% include excalidraw.html name="01-patterns-as-decisions-under-forces" described="true" caption="Figure 1.1: The rate-quote decision under four forces. Carrier tariffs, commercial surcharges and destination tax change on separate schedules while every quote must stay reproducible; the chosen shape follows from which force dominates." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-01-patterns-as-decisions-under-forces" markdown="1">
The figure reads from the top down. The top box, "Problem: quote a consignment", asks for one rate per carrier, zone and weight. Below it, a band headed "Forces pulling on the design" holds four boxes: carrier tariffs, in zone and weight bands; surcharges and discounts, commercial and set per contract; destination tax, which varies by country; and reproducible quotes, because billing disputes replay them. All four point at the accent box, which picks where the rating rules live: the shape that best resolves the pressures. It leads to "Consequences", what the choice buys and what it costs. The last box says the shape follows the dominant pressure: one function, separate callables, or a Protocol.
</div>
</details>

## What a pattern records

A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other.

The Gang of Four took the idea from the architect Christopher Alexander: a pattern describes a problem that recurs in a context, and the core of a solution you can reuse without building it the same way twice. The forces are pressures that can't all be satisfied at once, and the solution is one compromise among them.

The *Design Patterns* catalogue fixes this in a template: name and classification, intent, Also Known As, motivation, applicability, structure, participants, collaborations, consequences, implementation, sample code, known uses and related patterns. The authors reduce it to four essential elements: the name, the problem, the solution and the consequences. Three sections bear on a choice:

| Section | What it tells you |
| --- | --- |
| Structure | The diagram: the answer without the question. Most readers go straight to it. |
| Motivation and Applicability | The pressures and the context: the question. |
| Consequences | What the pattern buys and what it costs. |

Consequences is the ledger: flexibility gained, indirection added, objects multiplied, a change that used to touch one place now touching two. The catalogue presents it as the section that lets you compare alternatives. If you can't state a pattern's Consequences, nobody has counted its cost.

Two rules follow:

- **A pattern is valid only where its pressures are present.** Name them in your own system; don't scan the catalogue for a diagram that resembles your code.
- **Every pattern has a price, paid whether or not the benefit arrives.** A hook for variation that never varies is pure cost.

## Four pressures on a rate quote

A customer asks what it costs to move a `Consignment` between two zones. The system answers with a `RateQuote` built from `Money` amounts. Four pressures act on it:

| Pressure | Owner | Changes |
| --- | --- | --- |
| Carrier tariffs | The carrier | When the carrier chooses |
| `Surcharge` and `Discount` rules | The commercial team | Faster than the carrier; each rule on its own |
| Destination tax | The tax authority of each jurisdiction | On the authority's calendar |
| Reproducible, testable quotes | The disputed invoice | Any time after the quote |

- **Carrier tariffs.** A carrier such as FASTLINE or AIRCO publishes a `Tariff`, a price for each zone and weight band, and reissues it when it chooses: often on a fixed date each year, sometimes at short notice. Someone outside the team owns the largest block of numbers in every quote.
- **Commercial rules.** A fuel adjustment this quarter, a volume discount for a key account, a remote-area fee from a new contract. Sales and finance write them, and a discount can be withdrawn without touching the fuel adjustment.
- **Destination tax.** Each authority publishes its own rules, and somebody has to be able to read off the code whether tax applies to the discounted price or the list price.
- **Reproducibility.** A customer disputes an invoice three months later. You recompute the same `RateQuote` from the same consignment, the tariff and rules of the time, and show what each contributed. The quote has to be a function of explicit inputs: no mutable module state, no clock read mid-calculation. Each rule should also be checkable alone, with a few inputs and an expected `Money`.

They pull apart. Reproducibility wants few moving parts and explicit inputs. Independent change wants separation, so a tax update doesn't reopen the discount code. Testability wants rules small enough to call alone. Separation costs indirection, and indirection makes it harder to read in one place how a price was reached.

## The dominant pressure picks the shape

| Shape | Right when | What it costs |
| --- | --- | --- |
| One pricing function over a `Tariff` | Only the carrier tariff changes | Shared edits once a second party touches the function |
| Pricing-rule callables returning `Money` | Commercial rules and tax change on separate calendars, under separate owners | A composition step and a written order of application |
| A `RateCalculator` Protocol | A participant holds state or offers several operations | A declared interface every implementation honours |

**One pricing function over a `Tariff`.** The function looks up the base price for the zone and weight band, applies the rules inline in a fixed order and returns a `RateQuote`. A reissued tariff is new data, and the function doesn't change. The function and the tariff are the whole story, so a quote is easy to reproduce. If nothing but the tariff ever changes, this is the correct shape and the other two are speculation. It breaks down when a second owner edits it: adding a surcharge opens the function that also handles tax, and a test of one rule drags the others along. A sales team shipping monthly discounts while finance adjusts tax turns it into a source of merge conflicts.

**Pricing-rule callables returning `Money`.** Each rule is a small callable that takes what it needs and returns an amount, and a short composition step applies them to the base price. A new surcharge is a new callable and a line in the list of rules, and each rule is testable alone. The cost is the composition step and its question: in what order do the rules apply, and where is that order written down so a disputed quote can be explained? Reproducibility holds as long as the rules are pure functions of their arguments and the quote records which ran.

**A `RateCalculator` Protocol.** Some participants aren't plain functions. A rule may hold a loaded table, a cache or a connection to a carrier's service, or the pricing may need several operations: quote, explain, validate. A callable has one operation and no memory. A `RateCalculator` Protocol names what a calculator can do without making implementations inherit from anything, so a test double or a second carrier's calculator fits by shape. Once the pricing step has state or a second operation, this shape describes what you've already built.

Start from the shape that fits today's pressures, and know which one you'd move to if a pressure grew. Robert Martin's treatment of the open-closed principle describes the discipline: you can't predict which change arrives, so wait for the first one, then arrange the code so the next change of that kind needs no edits to existing logic.

## From a class per rule to a callable

In 1994 the second shape was drawn with classes: a rule per class, an abstract base class declaring the one method, and a calculator holding a list of rule objects. It resolves the pressures well, and the catalogue names it Strategy. It also dates from a time when behaviour reached a call site only inside an object of a declared class.

The class structure and the pressures are separable. Python passes a function wherever that object went, so the base class and subclasses no longer carry anything. The commercial team's calendar hasn't changed: a surcharge must still be addable without editing the tax rule, the order must still be explainable, and each rule must still be testable alone. A callable meets the same needs with less machinery.

Ask "is the force still here?" of every pattern. The answer goes either way:

- A language feature resolves the pressure without the pattern's structure, and the structure goes.
- The pressure is as strong as ever, and the pattern stays, with different syntax around it.

[What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) checks the catalogue's assumptions against what the language now provides.

## What a pattern name buys and costs

"This is a Strategy" lets a reviewer reconstruct the intent, the participants and the Consequences without reading the code, and lets two engineers argue about whether the pressure exists instead of about vocabulary. That shared handle is most of what the catalogue gave the field.

The cost is the picture the name drags along. Say "Strategy" and some of the team see a base class and a registry before the function you meant, and the review argues about the base class instead of asking whether the rules change independently. When the code no longer has the catalogue's structure, name the pressure first and the pattern second, and use the name only for what the code still does.

## When nothing argues for a pattern

A team quotes for one carrier. The tariff is reissued once a year, the only commercial rule is a flat fuel adjustment the same people maintain, and one line applies tax that finance has signed off. One function over a `Tariff`, with the adjustment inline, is shorter, reads top to bottom, and is easier to reproduce for a dispute than any arrangement of rule callables.

Pick a change that happens in your system, such as a new surcharge, and count what it edits:

| The change edits | Verdict |
| --- | --- |
| One function, in one file, owned by one team | The structure is already doing its job |
| The same function two other teams are editing this sprint | The pressures are present, and a pattern is justified |

Martin's warning about needless complexity points the same way: a premature abstraction costs every reader from the day it's written.

## What you can do now

- State what a pattern records: Alexander's forces, the context they act in, the resolution and its Consequences.
- Name the template sections and use Consequences as the ledger: it lists what a pattern buys and what it costs, so it supports the choice.
- List the four pressures on the rate quote and their owners: the carrier, the commercial team, the tax authority and the disputed invoice.
- Choose by the dominant pressure: a function over `Tariff`, rule callables returning `Money`, or a `RateCalculator` Protocol.
- Ask whether the force is still here, as in the move from a class per rule to a callable.
- Recognise the one-carrier case, and apply the count-the-edits test.

## For deeper coverage

*Design Patterns: Elements of Reusable Object-Oriented Software* by Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides (Addison-Wesley, 1994) is the source of the template and the four essential elements. Read its Introduction for the definition and its treatment of Consequences. *Agile Software Development: Principles, Patterns, and Practices* by Robert C. Martin (Prentice Hall, 2002) covers the open-closed principle and the argument for letting a real change, not a predicted one, drive the structure. *A Pattern Language* by Christopher Alexander, Sara Ishikawa and Murray Silverstein (Oxford University Press, 1977) is the architecture book in which Alexander set out patterns. All three are listed with publisher and year in the [bibliography]({{ '/bibliography/' | relative_url }}).
