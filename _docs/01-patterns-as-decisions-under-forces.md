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

- State what a pattern records: a context, competing forces, a resolution and its Consequences.
- Name the template sections the Gang of Four catalogue uses and say why Consequences is the one that supports a decision.
- List the pressures on a rate quote and the party that owns the schedule each one changes on.
- Choose between a pricing function over a `Tariff`, separate pricing-rule callables and a `RateCalculator` Protocol by naming the change that dominates.
- Explain why a pressure can outlive the structure that once resolved it, and why that makes "is the force still here?" the question to ask of every pattern.
- Recognise the case where the pressures are too weak to justify any pattern.

## Why this matters

It's easy to read a pattern catalogue as a catalogue of shapes: a class diagram, and when to draw it. A pattern then becomes something you apply, and the only judgement left is spotting the situation.

Someone sees a family of rating rules and remembers a diagram with an abstract base class and three subclasses. They build it, whether or not anything in the system pulls in that direction.

The catalogue frames a pattern differently, as the compromise left after competing pressures are traded off. So the questions change. Which pressures are present, which one dominates, and what does the pattern cost in return? The framing also makes this book's question about every pattern answerable: when the language moves, did the force move with it, or only the mechanism that resolved it?

One problem runs through the chapter: quoting a rate for a consignment. It's small enough to hold in your head, and it has real tension. Its inputs change on different schedules, and its outputs get argued over later. The figure shows the decision.

{% include excalidraw.html name="01-patterns-as-decisions-under-forces" caption="Figure 1.1: The rate-quote decision under four forces. Carrier tariffs, commercial surcharges and destination tax change on separate schedules while every quote must stay reproducible; the chosen shape follows from which force dominates." %}

## What a pattern records

A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other.

The Gang of Four took the idea from the architect Christopher Alexander. His patterns describe a problem that recurs in a given environment, together with the core of a solution. You can reuse that core without ever building it the same way twice.

In Alexander's usage a problem is a set of pressures that can't all be satisfied at once. A solution is one compromise among them, valid in one context.

The *Design Patterns* catalogue keeps that structure in a fixed template. Each entry has a name and classification, an intent, Also Known As, motivation, applicability, structure, participants, collaborations, consequences, implementation notes, sample code, known uses and related patterns. The authors reduce it to four essential elements: the name, the problem, the solution and the consequences. Three of the sections matter most when you choose:

| Section | What it tells you |
| --- | --- |
| Structure | The diagram. Most readers go straight to it, and it's the least informative part for a choice: it shows the answer without the question. |
| Motivation and Applicability | The pressures and the context: the question. |
| Consequences | What the pattern buys and what it costs. |

Consequences is the ledger. It lists flexibility gained, indirection added, objects multiplied, a change that used to touch one place now touching two. The catalogue presents this section as the one that lets you compare alternatives, and this book uses it for that. A pattern whose Consequences you can't state has a cost nobody has counted.

Two rules follow. First, a pattern is valid only where its pressures are present, so name them in your own system before you scan the catalogue for a resembling diagram. Second, every pattern has a price, paid whether or not the benefit turns up. A hook for variation that never varies is pure cost.

## Four pressures on a rate quote

A customer asks what it costs to move a `Consignment` from one zone to another. The system answers with a `RateQuote` built from `Money` amounts. Four pressures act on that answer, each with its own owner.

| Pressure | Owner | Schedule |
| --- | --- | --- |
| Carrier tariffs | The carrier | When the carrier chooses |
| `Surcharge` and `Discount` rules | The commercial team | Faster than the carrier; each rule on its own |
| Destination tax | The tax authority of each jurisdiction | The authority's own calendar |
| Reproducible, testable quotes | The disputed invoice | Any time after the quote |

**Carrier tariffs change on the carrier's schedule.** A carrier such as FASTLINE or AIRCO publishes a `Tariff`: a price for each zone and weight band. It reissues the tariff when it chooses, often on a fixed date each year, sometimes at short notice. Your code doesn't decide when. So someone outside the team owns the largest block of numbers in every quote.

**Commercial rules change on the commercial team's schedule.** `Surcharge` and `Discount` rules sit on top of the carrier price: a fuel adjustment this quarter, a volume discount for a key account, a remote-area fee that appears when a contract is signed.

People who answer to sales and finance write them, faster than the carrier and for different reasons. The rules also come and go independently. A discount can be withdrawn without touching the fuel adjustment.

**Destination tax changes by jurisdiction.** The tax on a quote depends on where the consignment is going. Authorities set the rules and publish them on their own calendar. Tax also interacts with the other rules: somebody has to be able to read off the code whether it applies to the discounted price or the list price.

**Every quote must be reproducible, and every rule testable alone.** A customer disputes an invoice three months after the quote. To settle it, you recompute the same `RateQuote` from the same consignment, the tariff that applied then and the rules of the time, and show what each contributed.

So the whole quote has to be a function of explicit inputs. No module holds mutable state, and nothing reads a clock mid-calculation.

The same constraint shows up during development. A rule you can exercise only by running the entire pipeline is a rule you'll test badly. Each rule should be checkable alone, with a handful of inputs and an expected `Money`.

The four pull in different directions. Reproducibility pushes towards fewer moving parts and explicit inputs. Independent change pushes towards separation, so a tax update doesn't reopen the discount code. Testability pushes towards rules small enough to call alone.

Separation costs indirection, and indirection makes it harder to read, in one place, how a price was reached.

## The dominant pressure picks the shape

Three shapes fit, each when a different pressure leads:

| Shape | Right when | What it costs |
| --- | --- | --- |
| One pricing function over a `Tariff` | Only the carrier tariff changes | Shared edits once a second party touches the function |
| Pricing-rule callables returning `Money` | Commercial rules and tax change on separate calendars, under separate owners | A composition step and a written order of application |
| A `RateCalculator` Protocol | A participant holds state or offers several operations | A declared interface every implementation honours |

No shape wins in general. Each one wins for a given system.

**One pricing function over a `Tariff`.** A single function takes the consignment and a `Tariff`, looks up the base price for its zone and weight band, applies the rules in a fixed order and returns a `RateQuote`. The rules sit inline, as ordinary statements.

When the carrier's schedule is what moves, this is the strongest answer. A reissued tariff is new data and the function doesn't change.

A quote is reproducible because the function and the tariff together are the whole story. The arithmetic reads in one place. If the carrier tariff is the only thing that ever changes, this shape is correct and the other two are speculation.

The cost appears the day a second party starts editing the same function. If adding a surcharge means opening the function that also handles tax, two owners share one function and its regressions. A test of one rule drags the others along.

When a sales team ships new discounts monthly while finance adjusts tax rules separately, this shape is a source of merge conflicts.

**Separate pricing-rule callables returning `Money`.** Each commercial and tax rule becomes its own small callable. It takes what it needs and returns a `Money` amount, and a short composition step applies the rules to the base price. A new surcharge is then a new callable and a line in the list of rules, not an edit to existing logic.

Each rule is testable alone, with plain inputs and one expected value. This is the shape for commercial rules and tax that change independently, on separate calendars, under separate owners. With monthly discounts and separate tax changes, it pays for its indirection.

You pay with the composition step and the question it raises. In what order do the rules apply, and where is that order written down so that a disputed quote can be explained?

The order is now something you choose, not an accident of line numbers. Reproducibility survives as long as the rules are pure functions of their arguments and the quote records which of them ran.

**A `RateCalculator` Protocol.** Sometimes a participant isn't a plain function. A rule may hold state, such as a loaded table, a cache with an eviction policy or a connection to a carrier's service. Or the pricing may need several operations: quote a rate, explain how it was reached, validate a request before pricing. A bare callable has one operation and no memory.

When either need appears, give the participant a named interface. A `RateCalculator` Protocol states what a calculator can do without making implementations inherit from anything. So a test double or a second carrier's calculator slots in by shape. The price is a declared interface, and every implementation now has to honour it.

If the pricing step acquires state or a second operation, this shape is the accurate description of what you've already built.

Start from the shape that fits the pressures you have today. Keep the others in view as the ones you'd move to if a pressure grew.

Robert Martin's treatment of the open-closed principle describes that discipline. You don't know in advance which change will arrive, so you wait for the first one, then arrange the code so the next change of that kind needs no edits to existing logic.

## Forces outlive the structures that resolved them

Thirty years ago the second shape was usually drawn with classes. A rating rule became a class, an abstract base class declared the one method every rule had to implement, and the calculator held a list of objects that satisfied it. That structure suits the rate quote perfectly well, and the catalogue gives it a name. It's also the structure of an era in which behaviour reached a call site only inside an object of a declared class.

The structure and the forces are separable. Python lets you pass a function wherever that object was passed, so the abstract base class and the subclasses no longer have to carry behaviour.

The commercial team's calendar hasn't changed, though. A surcharge still has to be addable without editing the tax rule, the order of application still has to be explainable in a dispute, and each rule still has to be testable alone.

A callable meets the same needs with less machinery.

Is the force still here? The book asks it of every pattern, and the answer runs both ways. Sometimes a language feature resolves the pressure without the pattern's structure, and the structure should go. Sometimes the pressure is as strong as ever, and the pattern stays the right resolution, even though the syntax around it has changed.

[What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) takes the assumptions the catalogue was written under and checks each against what the language now provides.

## What a pattern name buys and costs

A name is a compression device. Saying "this is a Strategy" lets a reviewer reconstruct the intent, the participants and the Consequences without reading the code. It also lets two engineers argue about whether the pressure behind it exists, not about vocabulary. That shared handle is most of what the catalogue gave the field.

The cost is the picture the name drags along. Say "Strategy" to a team and some of them will see a base class and a registry before they see the function you meant.

A review then drifts towards the structure and away from the pressure. When the name and the mechanism have diverged, name the pressure first and the pattern second, and use the pattern's name only for what it still describes.

## When nothing argues for a pattern

Suppose a team quotes for one carrier. The tariff is reissued once a year, and the only commercial rule is a flat fuel adjustment that the same people maintain. A single line applies tax, and the finance team has signed it off. Nothing that justifies separation is present.

One function over a `Tariff`, with the adjustment written inline, is shorter and reads top to bottom. It's also easier to reproduce for a dispute than any arrangement of rule callables. The patterns would add files and indirection against a change that isn't coming.

Pick a change that actually happens in your system, such as a new surcharge, and count what it has to edit:

| The change edits | Verdict |
| --- | --- |
| One function, in one file, owned by one team | The structure is already doing its job |
| The same function two other teams are editing this sprint | The pressures are present, and a pattern is justified |

Martin's warning about needless complexity points the same way. A premature abstraction has a real cost, and it lands on every reader of the code from the day it's written.

## What you can do now

- State what a pattern records: Alexander's forces, the context they act in, the resolution and its Consequences.
- Name the template sections and use Consequences as the ledger: it lists what a pattern buys and what it costs, so it supports the choice.
- List the four pressures on the rate quote and their owners: the carrier, the commercial team, the tax authority and the disputed invoice.
- Choose by the dominant pressure: a function over `Tariff`, rule callables returning `Money`, or a `RateCalculator` Protocol.
- Ask whether the force is still here, as in the move from a class per rule to a callable.
- Recognise the one-carrier case, and apply the count-the-edits test.

## For deeper coverage

*Design Patterns: Elements of Reusable Object-Oriented Software* by Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides (Addison-Wesley, 1994) is the source of the template and the four essential elements. Read its Introduction for the definition and its treatment of Consequences. *Agile Software Development: Principles, Patterns, and Practices* by Robert C. Martin (Prentice Hall, 2002) covers the open-closed principle and the argument for letting a real change, not a predicted one, drive the structure. *A Pattern Language* by Christopher Alexander, Sara Ishikawa and Murray Silverstein (Oxford University Press, 1977) is the architecture book in which Alexander set out patterns. All three are listed with publisher and year in the [bibliography]({{ '/bibliography/' | relative_url }}).
