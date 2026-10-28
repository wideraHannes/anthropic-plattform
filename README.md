# Building Agentic Systems with Claude

A knowledge base for the Claude Developer Platform: one concept per folder, small runnable scripts, end-to-end projects with evals.

## Setup

```bash
uv sync
cp .env.example .env
```

- **Claude API:** set `ANTHROPIC_API_KEY`. That's it.
- **Gateway / external provider:** also uncomment `ANTHROPIC_BASE_URL` and the `MODEL_*` IDs in `.env`.

All code uses `config.client` / `config.settings` ([`config.py`](config.py)). Default model: Claude Sonnet 5.5.

## Start here: [`api_surfaces.ipynb`](concepts/01_api_surfaces/api_surfaces.ipynb)

| #   | Surface           | Call                                              | Use when                           |
| --- | ----------------- | ------------------------------------------------- | ---------------------------------- |
| 1   | Plain call        | `client.messages.create`                          | One request, one answer            |
| 2   | Streaming         | `client.messages.stream`                          | Long output, live UI               |
| 3   | Structured output | `client.messages.parse(output_format=Model)`      | Code consumes the answer           |
| 4   | Manual tool loop  | `stop_reason == "tool_use"` → `tool_result`       | Understanding what the runner does |
| 5   | Tool Runner       | `client.beta.messages.tool_runner` + `@beta_tool` | Custom tools (default)             |

```bash
cd concepts/01_api_surfaces && uv run --with jupyter jupyter lab api_surfaces.ipynb
```

## Concepts

| #                                            | Concept                 | One-liner                                                              |
| -------------------------------------------- | ----------------------- | ---------------------------------------------------------------------- |
| [01](concepts/01_api_surfaces/)              | API surfaces            | `create` → `stream` → `parse` → manual loop → Tool Runner.             |
| [02](concepts/02_agentic_loop/)              | The agentic loop        | `stop_reason == "tool_use"` → run tools → repeat. Pick the build path. |
| [03](concepts/03_tool_design/)               | Tool design             | Tools are the agent's UI: descriptions, schemas, structured errors.    |
| [04](concepts/04_workflows_and_multi_agent/) | Workflows & multi-agent | Chaining, routing, parallel, orchestrator–workers, hub-and-spoke.      |
| [05](concepts/05_guardrails_and_hooks/)      | Guardrails & hooks      | Determinism ladder: prompt → schema → gate → hook → human.             |
| [06](concepts/06_evals/)                     | Evals                   | Edge cases, code before LLM grader, six eval types (notebook).         |
| [07](concepts/07_inference_optimization/)    | Inference optimization  | Caching, batch, effort, model choice, per completed task.              |

## Projects

Each project has a `README.md` (design choices, eval results, what to try next) and an `eval.py`.

| #                                       | Project                                       | Pattern                                                     | Concepts          |
| --------------------------------------- | --------------------------------------------- | ----------------------------------------------------------- | ----------------- |
| [01](projects/01_ticket_routing/)       | Ticket routing                                | Routing workflow, structured output                         | 04 · 06 · 07      |
| [02](projects/02_support_agent/)        | Customer support agent (**reusable starter**) | Single agent + gated tools + handoff                        | 02 · 03 · 05 · 06 |
| [03](projects/03_research_multi_agent/) | Multi-agent research                          | Orchestrator–workers, parallel, gap review, cited synthesis | 04 · 06           |
| [4D](projects/4D_framework/)            | Clinic wait time, along the 4D AI Fluency framework | Delegation → Description → Discernment → Diligence    | –                 |

```bash
cd projects/02_support_agent && uv run pytest && uv run python eval.py
```

## Reference

- [`KEYWORDS.md`](KEYWORDS.md) — Anthropic's vocabulary on one page (ACI, context rot, hub-and-spoke, pass^k …)
- [`exam/`](exam/ccaf_exam_guide.pdf) — Claude Certified Architect exam guide (PDF)
