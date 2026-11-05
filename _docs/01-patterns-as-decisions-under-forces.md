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
- List the forces acting on a rate quote and say which party owns the schedule each one changes on.
- Choose between a pricing function over a `Tariff`, separate pricing-rule callables and a `RateCalculator` Protocol by naming the dominant force.
- Explain why a force can outlive the structure that once resolved it, and why that makes "is the force still here?" the question to ask of every pattern.
- Recognise the case where the forces are too weak to justify any pattern.

## Why this matters

A catalogue of patterns is easy to read as a catalogue of shapes: here is a class diagram, here is when to draw it. Read that way, a pattern is something you apply, and the only judgement left is whether you recognise the situation. Someone sees a family of rating rules, remembers a diagram with an abstract base class and three subclasses, and builds it, whether or not anything in the system pulls in that direction.

The catalogue's own framing is different. A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other. The shape is what's left after those forces have been traded off. You stop asking whether the situation looks like the diagram and start asking which forces are present, which one dominates, and what the pattern costs you in return. It also makes the question this book asks of every pattern answerable: when the language moves, did the force move with it, or only the mechanism that resolved it?

One problem runs through the whole chapter: quoting a rate for a consignment. It's small enough to hold in your head and it has real tension in it, because its inputs change on different schedules and its outputs get argued over later. The figure shows the decision.

{% include excalidraw.html name="01-patterns-as-decisions-under-forces" caption="Figure 1.1: The rate-quote decision under four forces. Carrier tariffs, commercial surcharges and destination tax change on separate schedules while every quote must stay reproducible; the chosen shape follows from which force dominates." %}

## What a pattern records

The Gang of Four took the idea from the architect Christopher Alexander, whose patterns describe a problem that recurs in a given environment together with the core of a solution, stated so that you can reuse it without ever building it the same way twice. Alexander's problems are made of forces. In his usage a problem is a set of pressures that can't all be satisfied at once. A solution is a particular compromise among them, valid in a particular context.

The *Design Patterns* catalogue keeps that structure and spells it out in a fixed template. Each entry has a name and classification, an intent, Also Known As, motivation, applicability, structure, participants, collaborations, consequences, implementation notes, sample code, known uses and related patterns. The authors reduce this to four essential elements: the name, the problem, the solution and the consequences. Most readers go straight to Structure, the diagram. It's the least informative part for a decision, because it shows the answer without the question.

The sections that carry the question are Motivation and Applicability, which describe the forces and the context, and Consequences. Consequences is the ledger. It lists what the pattern buys and what it costs: flexibility gained, indirection added, objects multiplied, a change that used to touch one place now touching two. The catalogue itself presents this section as the one that lets you compare design alternatives, and that is the use made of it here. A pattern whose Consequences you can't state has a cost nobody has counted.

Two readings follow. A pattern is valid only where its forces are present, so the first job is to name the forces in your own system, not to scan the catalogue for a resembling diagram. And every pattern has a price, paid whether or not the benefit turns up. A hook for variation that never varies is pure cost.

## The rating problem as forces

Take a rate quote in the shipping domain. A customer asks what it will cost to move a `Consignment` from one zone to another, and the system answers with a `RateQuote` built from `Money` amounts. Four forces act on that answer.

**Carrier tariffs change on the carrier's schedule.** A carrier such as FASTLINE or AIRCO publishes a `Tariff`: a price for each combination of zone and weight band. The carrier reissues it when it chooses, often on a fixed date each year, and sometimes with little warning in between. Nothing in your codebase decides when this happens. The force is that the largest block of numbers feeding every quote is owned by someone outside the team.

**Commercial rules change on the commercial team's schedule.** On top of the carrier price sit `Surcharge` and `Discount` rules: a fuel adjustment this quarter, a volume discount for a key account, a remote-area fee that appears when a contract is signed. These are written by people who answer to sales and finance, who move faster than the carrier and have different reasons. They also come and go independently of each other. A discount can be withdrawn without touching the fuel adjustment.

**Destination tax changes by jurisdiction.** The tax applied to a quote depends on where the consignment is going, and the rules are set by authorities that publish on their own calendar. Tax has its own owner and its own schedule, and it interacts with the others: whether it applies to the discounted price or the list price is a decision somebody has to be able to read off the code.

**Every quote must be reproducible, and every rule testable alone.** A customer disputes an invoice three months after the quote. To settle it, you have to recompute the same `RateQuote` from the same consignment, the tariff that was in force, and the rules that applied at the time, and show how each one contributed. That's a constraint on the whole design: the quote has to be a function of explicit inputs, with no mutable state held in a module or a clock read mid-calculation. It has a second face during development. A rule that can only be exercised by running the entire pipeline is a rule you will test badly. Each one should be checkable on its own with a handful of inputs and an expected `Money`.

These forces point in different directions. Reproducibility pushes towards fewer moving parts and explicit inputs. Independent change pushes towards separation, so that a tax update doesn't mean reopening the discount code. Testability pushes towards rules small enough to call alone. Separation has a cost in indirection, and indirection works against being able to read, in one place, how a price was reached.

## Which force dominates decides the shape

There are three candidate shapes, and each is the right resolution when a different force leads.

**One pricing function over a `Tariff`.** A single function takes the consignment and a `Tariff`, looks up the base price for its zone and weight band, applies the rules in a fixed order and returns a `RateQuote`. The rules sit inline, as ordinary statements. When the carrier's schedule is the force that moves, this is the strongest answer: a reissued tariff is new data, the function doesn't change, and a quote is reproducible because the function and the tariff together are the whole story. Reading the arithmetic is easy because it's all in one place. The cost appears the day a second party starts editing the same function. If adding a surcharge means opening the function that also handles tax, two owners now share one function and its regressions, and a test of one rule drags the others along.

**Separate pricing-rule callables returning `Money`.** Each commercial and tax rule becomes its own small callable that takes what it needs and returns a `Money` amount, and a short composition step applies them to the base price. Now a new surcharge is a new callable and a line in the list of rules, not an edit to existing logic, and each rule is testable alone with plain inputs and one expected value. This is the shape for the case where commercial rules and tax change independently, on separate calendars, under separate owners. What you pay is the composition step and the question it forces: in what order do the rules apply, and where is that order written down so that a disputed quote can be explained? The ordering is now a piece of design, not an accident of line numbers. Reproducibility survives as long as the rules are pure functions of their arguments and the quote records which of them ran.

**A `RateCalculator` Protocol.** Sometimes a participant isn't a plain function. A rule may hold state, such as a loaded table, a cache with an eviction policy or a connection to a carrier's service. Or the thing doing the pricing may need to offer several operations: quote a rate, explain how it was reached, validate a request before pricing. A bare callable has one operation and no memory. When either need appears, give the participant a named interface. A `RateCalculator` Protocol states what a calculator can do without forcing implementations to inherit from anything, so a test double or a second carrier's calculator slots in by shape. The price is a declared interface, and every implementation now has to honour it.

The forces don't rank the shapes absolutely. They rank them for a given system. If the carrier tariff is the only thing that ever changes, the first shape is correct and the other two are speculation. If a sales team ships new discounts monthly while finance adjusts tax rules separately, the first shape is a source of merge conflicts and the second pays for its indirection. If the pricing step acquires state or a second operation, the third becomes the accurate description of what you've already built.

Start from the shape that resolves the forces you have today, and keep the others in view as the ones you'd move to if a force grew. Robert Martin's treatment of the open-closed principle describes exactly that discipline: you don't know in advance which change will arrive, so you wait for the first one and then arrange the code so the next change of that kind needs no edits to existing logic.

## Forces outlive the structures that resolved them

Consider how the second shape was usually drawn thirty years ago. A rating rule became a class, an abstract base class declared the one method every rule had to implement, and the calculator held a list of objects that satisfied it. That structure is a perfectly good resolution of the forces above, and the catalogue gives it a name. It's also the structure of an era in which a piece of behaviour could reach a call site only by being wrapped in an object of a declared class.

The structure and the forces are separable. Because Python lets you pass a function wherever that object was passed, the abstract base class and the subclasses are no longer needed to carry behaviour. Nothing about the commercial team's calendar has changed, though. The surcharge still has to be addable without editing the tax rule, the order of application still has to be explainable in a dispute, and each rule still has to be testable alone. A callable resolves the same forces with less machinery.

That question is the book's recurring test, and it runs both ways. Sometimes a language feature resolves the force without the pattern's structure, and the structure should go. Sometimes the force is as strong as ever and the pattern remains the right resolution, even though the syntax around it has changed. The following chapter, [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}), takes the assumptions the catalogue was written under and checks each against what the language now provides.

## What a pattern name buys and costs

A name is a compression device. Saying "this is a Strategy" lets a reviewer reconstruct the intent, the participants and the Consequences without reading the code, and it lets two engineers argue about whether the force is present instead of about vocabulary. That shared handle is most of what the catalogue gave the field, The cost is that the name drags a picture along with it. Say "Strategy" to a team and some of them will see a base class and a registry before they see the function you meant, and a review conversation will drift towards the structure rather than the force. When the name and the mechanism have diverged, the precise move is to name the force first and the pattern second, and to use the pattern's name only for what it still describes.

## When the forces argue for no pattern

Suppose a team quotes for one carrier. The tariff is reissued once a year, the only commercial rule is a flat fuel adjustment that the same people maintain, and tax is applied by a single line the finance team has signed off. Every force that justifies separation is absent. One function over a `Tariff` with the adjustment written inline is shorter, easier to read top to bottom and easier to reproduce for a dispute than any arrangement of rule callables. The patterns would add files and indirection against a change that isn't coming.

Pick the change that actually happens in your system, such as a new surcharge, and count what has to be edited to make it. If the answer is one function, in one file, owned by one team, the structure is already doing its job. If it's the same function that two other teams are editing this sprint, the forces are present and a pattern is justified. Martin's warning about needless complexity points the same way: the cost of a premature abstraction is real, and it lands on every reader of the code from the day it's written.

## What you can do now

- State what a pattern records: Alexander's forces, the context they act in, the resolution and its Consequences.
- Name the template sections and use Consequences as the ledger: it lists what a pattern buys and what it costs, so it supports the decision.
- List the four forces on the rate quote and their owners: the carrier, the commercial team, the tax authority and the disputed invoice.
- Choose by the dominant force: a function over `Tariff`, rule callables returning `Money`, or a `RateCalculator` Protocol.
- Ask whether the force is still here, as in the move from a class per rule to a callable.
- Recognise the one-carrier case, and apply the count-the-edits test.

## For deeper coverage

*Design Patterns: Elements of Reusable Object-Oriented Software* by Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides (Addison-Wesley, 1994) is the source of the template and the four essential elements. Read its Introduction for the definition and its treatment of Consequences. *Agile Software Development: Principles, Patterns, and Practices* by Robert C. Martin (Prentice Hall, 2002) covers the open-closed principle and the argument for letting a real change, not a predicted one, drive the structure. Both are listed with publisher and year in the [bibliography]({{ '/bibliography/' | relative_url }}).
