# Building Agentic Systems with Claude

Clean, correct knowledge + a playground for building **Claude into products**: agents, workflows, multi-agent systems. Preparation for **Anthropic Partner Basecamp**: build an agent end to end, modify an unfamiliar one, measure before/after, defend the design.

## Map

| Folder / file                | What                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------ |
| [`KEYWORDS.md`](KEYWORDS.md) | Anthropic's vocabulary in one page (hub-and-spoke, ACI, context rot, pass^k …) |
| [`concepts/`](concepts/)     | The ideas, one folder each, with small runnable scripts                        |
| [`projects/`](projects/)     | End-to-end examples applying the concepts, each with an `eval.py`              |
| [`exam/`](exam/)             | Cert exam guide                                                                |

## Concepts

| #                                            | Concept                 | One-liner                                                              |
| -------------------------------------------- | ----------------------- | ---------------------------------------------------------------------- |
| [02](concepts/02_agentic_loop/)              | The agentic loop        | `stop_reason == "tool_use"` → run tools → repeat. Pick the build path. |
| [03](concepts/03_tool_design/)               | Tool design             | Tools are the agent's UI: descriptions, schemas, structured errors.    |
| [04](concepts/04_workflows_and_multi_agent/) | Workflows & multi-agent | Chaining, routing, parallel, orchestrator–workers, hub-and-spoke.      |
| [05](concepts/05_guardrails_and_hooks/)      | Guardrails & hooks      | Determinism ladder: prompt → schema → gate → hook → human.             |
| [06](concepts/06_context_engineering/)       | Context engineering     | Smallest high-signal context; compaction, memory, subagents.           |
| [07](concepts/07_evals/)                     | Evals                   | Dataset + grader + number. Outcomes _and_ trajectories.                |
| [08](concepts/08_inference_optimization/)    | Inference optimization  | Caching, batch, effort, model choice, per completed task.              |

## Projects

| #                                       | Project                                                   | Pattern                                                                            | Concepts          |
| --------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------------- |
| [01](projects/01_ticket_routing/)       | Ticket routing                                            | Routing workflow, structured output                                                | 04 · 07 · 08      |
| [02](projects/02_support_agent/)        | Customer support agent (**reusable starter**)             | Single agent + gated tools + handoff                                               | 02 · 03 · 05 · 07 |
| [03](projects/03_research_multi_agent/) | Multi-agent research                                      | Orchestrator–workers, parallel, cited synthesis                                    | 04 · 06 · 07      |
| [4D](projects/4D_framework/)            | Clinic wait time, built along the 4D AI Fluency framework | Delegation → Description → Discernment → Diligence; tests as description, UX audit | –                 |

## Basecamp agenda → where to prepare

| Session                        | Prepare with                                                          |
| ------------------------------ | --------------------------------------------------------------------- |
| Developer Platform             | Concepts 02, 03 · project 01                                          |
| Protocols / Prompt Rescue      | Project 01 `eval.py minimal` vs `detailed`                            |
| Diagnosing AI Problems         | Read the FAIL lines and transcripts of every `eval.py`                |
| Delivering the Claude Demo     | Project 02: chat demo + eval numbers                                  |
| Evals                          | Concept 07 · every project's `eval.py`                                |
| Inference Optimization         | Concept 08 (`prompt_caching.py`) · token/latency output of project 01 |
| Workshop · Context Engineering | Concept 06 · project 03                                               |
| Hackathon · Agent Build        | Project 02 as the starter; patterns from concept 04                   |

## Setup

```bash
uv sync
cp .env.example .env   # add ANTHROPIC_API_KEY; model IDs are configured there
cd projects/02_support_agent && uv run python eval.py
```

All scripts use `config.client` / `config.settings` (see [`config.py`](config.py)).
