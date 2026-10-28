# 02 — The Agentic Loop

> An agent is just an LLM using tools in a loop: `while stop_reason == "tool_use": run tools → append results → call again`.

## Core rules

1. **The API is stateless.** All state lives in the `messages` list you resend each turn.
2. **Append the full assistant `content`**, then one user message with *all* matching `tool_result` blocks (bound by `tool_use_id`). Claude calls tools in parallel — answer every call in the same message.
3. **Errors are results, not crashes.** Return `is_error: true` with a useful message so the model can correct itself (Tool Runner: `raise ToolError(...)`).
4. **Check `stop_reason` every turn**: `tool_use` (continue), `end_turn` (done), `max_tokens`, `pause_turn`, `refusal`.
5. **Cap iterations and tokens.** A loop without a ceiling is a cost incident waiting to happen.
6. **Use the Tool Runner** (`client.beta.messages.tool_runner` + `@beta_tool`) once you understand the hand-rolled loop.

## Pick the build path

| Path | You own | Use when |
|---|---|---|
| **Messages API, manual loop** | loop + tools + hosting | You need full control over every turn. |
| **Messages API, Tool Runner** | tools + hosting | Most custom agents. Same API, loop is handled. |
| **Claude Agent SDK** | config + hosting | You want Claude Code's harness (files, bash, subagents, hooks) as a library. |
| **Claude Managed Agents** | config only | Anthropic hosts loop + sandbox; long-running, scheduled, versioned agents. |

Before any of these: **do you need an agent at all?** A single call or a fixed workflow is cheaper, faster and easier to test (→ [04](../04_workflows_and_multi_agent/)).

## Code here — the five rings

| Ring | File | Adds |
|---|---|---|
| 1 | [`ring_1_single_tool.py`](ring_1_single_tool.py) | One tool, one round trip. No loop. |
| 2 | [`ring_2_agentic_loop.py`](ring_2_agentic_loop.py) | `while stop_reason == "tool_use"`. |
| 3 | [`ring_3_multiple_tools.py`](ring_3_multiple_tools.py) | Several tools, parallel `tool_use` blocks in one turn. |
| 4 | [`ring_4_error_handling.py`](ring_4_error_handling.py) | `is_error: true` so the model can retry. |
| 5 | [`ring_5_tool_runner.py`](ring_5_tool_runner.py) | Same thing with the Tool Runner — production shape; `ToolError` for error results. |

Next step up the build-path table: [`agent_sdk/`](agent_sdk/) — the Claude Agent SDK, Claude Code's harness as a library.

## Sources

- Build a tool-using agent — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent>
- Building effective agents — <https://www.anthropic.com/engineering/building-effective-agents>
- Cert: [1.1 Agentic Loops](https://claudecertificationguide.com/learn/1-agentic-architecture/1-1-agentic-loops)
