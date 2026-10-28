# 01 — API surfaces

> Everything in the client SDK is one endpoint, `POST /v1/messages`. `create`, `stream`, `parse` and `tool_runner` are helpers on top of it.

## Core rules

1. **Start with the lowest surface that solves the problem.** Single call → structured output → tools → agent harness.
2. **Need data, not prose?** `client.messages.parse(output_format=PydanticModel)` → `response.parsed_output`. Don't force a tool call to get JSON; newer models reject a forced `tool_choice` with a 400.
3. **Custom tools?** `client.beta.messages.tool_runner` + `@beta_tool`. Write the manual loop only to learn it, or when the runner's per-turn hooks don't fit.
4. **Tools + typed result** → `tool_runner(..., output_format=Model)`.
5. **There is no `messages.complete`.** `client.completions.create` is the legacy Text Completions API. Don't use it.

## Pick the surface

| Surface | Call | You own | Use when |
|---|---|---|---|
| Plain call | `messages.create` | everything | One request, one answer |
| Streaming | `messages.stream` | everything | Long output, live UI |
| Structured output | `messages.parse` | schema | Code consumes the answer |
| Manual loop | `create` + `while stop_reason == "tool_use"` | loop + tools | Full control per turn |
| Tool Runner | `beta.messages.tool_runner` | tools | **Default** for custom-tool agents |

## Code here

| File | What |
|---|---|
| [`api_surfaces.ipynb`](api_surfaces.ipynb) | One order-shop task walked through all five surfaces, each step adding one capability. |
| [`orders.json`](orders.json) | The shared data the custom tool reads in steps 4–5. |

Run: `uv run --with jupyter jupyter lab` from this folder, or pick the repo `.venv` as the kernel in VS Code (this needs `ipykernel`).

Next: [02 — the agentic loop](../02_agentic_loop/) goes deeper on steps 4–5; the step after that (built-in tools, subagents, hooks) is the [Agent SDK](../02_agentic_loop/agent_sdk/).

## Sources

- Intro — <https://platform.claude.com/docs/en/intro>
- Tool Runner — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner>
- Structured outputs — <https://platform.claude.com/docs/en/build-with-claude/structured-outputs>
