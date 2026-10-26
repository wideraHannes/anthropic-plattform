# 04 — Workflows & Multi-Agent Systems

> Start with the simplest thing that works. Add steps only when they measurably help: single call → workflow (code decides the path) → agent (model decides the path) → multi-agent.

Basecamp: *Hackathon · Agent Build*, *Defend the design choices*.

## The patterns (from "Building effective agents")

| Pattern | Code controls | Use when |
|---|---|---|
| **Prompt chaining** | fixed sequence of calls, gates between | Task splits cleanly into steps (draft → check → translate). |
| **Routing** | classify, then dispatch to a specialised prompt/model | Distinct input categories (→ [project 01](../../projects/01_ticket_routing/)). |
| **Parallelization** | fan-out, then merge / vote | Independent subtasks, or several opinions for confidence. |
| **Orchestrator–workers** | LLM plans subtasks at runtime, workers execute | Subtasks can't be known upfront (→ [project 03](../../projects/03_research_multi_agent/)). |
| **Evaluator–optimizer** | generate → critique → revise loop | Clear quality criteria and iteration pays off. |
| **Agent** | model loops with tools until done | Open-ended, many steps, recoverable errors (→ [project 02](../../projects/02_support_agent/)). |

## Core rules for multi-agent

1. **Hub-and-spoke**: one coordinator; subagents never talk peer-to-peer.
2. **Subagents start with an empty context.** Pass every fact they need — explicitly.
3. **Decompose broadly, with non-overlapping scopes.** Narrow decomposition silently drops coverage.
4. **Return condensed, structured results** (with sources) — the coordinator's context is the bottleneck.
5. **Parallelize independent work**; serialise only real dependencies.
6. **Multi-agent costs ~several× the tokens** of one agent. Worth it for breadth-heavy, parallelizable work; not for tightly coupled tasks.

## Anti-patterns

- Agent where a 3-step workflow would do.
- Framework-heavy abstractions that hide the prompts and the loop.
- Many items in one context (attention dilution) — use per-item passes + one integration pass.

## Code here

| Folder | Shows | Cert |
|---|---|---|
| [`01_hub_and_spoke/`](01_hub_and_spoke/) | Messages-API coordinator, schema-enforced breadth, gap review loop. | 1.2 |
| [`02_subagents_sdk/`](02_subagents_sdk/) | Same idea with the Agent SDK `Agent` tool, parallel spawn, citation metadata. | 1.3 |
| [`03_task_decomposition/`](03_task_decomposition/) | Fixed pipeline vs dynamic decomposition, attention dilution. | 1.6 |

## Sources

- Building effective agents — <https://www.anthropic.com/engineering/building-effective-agents>
- How we built our multi-agent research system — <https://www.anthropic.com/engineering/multi-agent-research-system>
