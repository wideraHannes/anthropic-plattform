# Delegation — Basics

> **Delegation** means decomposing a problem into parts and deciding which role AI plays in each of them.
>
> - Delegating **implementation** to AI is usually fine.
> - Delegating **judgement** is usually not advised.

## Scenario

A customer comes to you with a problem.

1. How do you decompose it?
2. What role does AI play at each stage of that work?

## Mental model: you lead, AI is your team

You are the lead of a project, and AI is your team. A great team lead:

- **Frames the problem** so it's clear what needs solving.
- **Sets goals** to measure what good looks like.
- **Decides what to tackle first.**
- **Knows which decisions to make themselves.**

## The builder's toolkit

Every builder has a toolkit of six areas. AI can help in all of them — more in some, less in others.

| Area | Core question | Role of AI | Delegation |
| --- | --- | --- | --- |
| **Empathy** | What does the person actually need? | Talk to users and observe what frustrates them. AI can help organise learnings, but can't make the observations. | Low |
| **Design** | What should we build and why? | Weighing trade-offs, making bets, deciding what matters — all judgement calls. AI can generate options, not make the calls. | Low |
| **Architecture** | How should it be structured? | AI knows patterns, but not your circumstances. Ideal for human–AI collaboration. | Medium |
| **Implementation** | Writing the actual code. | AI is strongest here. Define clear tests and success checkpoints. | High — most aggressive delegation |
| **Judgement** | Does it work? Is the product good? | AI can tell you whether code runs, not whether it feels right. Requires your expertise, standards and perspective. | Low |
| **Shipping** | Getting the product to real users and learning from them. | Communication, measurement, iteration. AI can draft release notes, but doesn't understand the user experience. | Low |

**AI is strongest in the middle and weakest at the edges — the edges are where human work lives.**

![Toolkit](/assets/toolkit.png)

## What good delegation looks like

- Spend real time on the **beginning** of the project.
- Get clear on **who you're building for**.
- **Define what success means.**
- **Inspect the results sceptically.**
- Keep **judgement calls** in your own hands.
