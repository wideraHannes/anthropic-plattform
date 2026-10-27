# Agent SDK — the loop as a library

> Build production AI agents with Claude Code as a library. Same tools, agent loop, and context management that power Claude Code — programmable.
> — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)

## Client SDK vs. Agent SDK

**Client SDK** (`anthropic`) = direct API access; you write the loop (rings 1–4) or let the Tool Runner run it over *your* tools (ring 5).
**Agent SDK** (`claude-agent-sdk`) = Claude Code's harness: the loop **plus** built-in tools (`Read`/`Edit`/`Bash`/`WebSearch`/`Agent`…), subagents, hooks, sessions. You still host it.

```python
async for message in query(prompt="Fix the bug in auth.py", options=ClaudeAgentOptions(...)):
    print(message)
```

## Three primitives

- **`ClaudeAgentOptions`** — declarative spec: `system_prompt`, `model`, `allowed_tools`, `agents`, `permission_mode`, `hooks`, `mcp_servers`, `output_format`.
- **`query(prompt, options)`** — async generator that runs the loop and streams `SystemMessage` → `AssistantMessage` → `UserMessage` → terminal `ResultMessage`.
- **`AgentDefinition`** — one subagent slot in `options.agents`: `description` (routing hint), `prompt` (its system prompt), `tools` (its allow-list), optional `model`. Attribute streamed events via `AssistantMessage.parent_tool_use_id`.

## Structured output

`ClaudeAgentOptions(output_format=...)` gives the **final result** a JSON schema. Subagents (`AgentDefinition`) have no schema option: their return value is the final text of their inner loop, read by the coordinator (another Claude turn, not Python). So between subagents: state the shape in the prompt and keep metadata explicit ([04/01](../../04_workflows_and_multi_agent/01_subagents_sdk/)).

## Code here

[`simple_claude_code.py`](simple_claude_code.py) — `query()` with `allowed_tools`, `permission_mode="acceptEdits"` and a system prompt; the agent edits [`utils.py`](utils.py) in this folder test-driven. `git checkout utils.py` resets it.

## Repo gotcha: auth & model IDs

Transport is a subprocess to the local `claude` CLI, so it uses **CLI auth** (Claude Code login or `ANTHROPIC_API_KEY`) — **not** this repo's Requesty router in `config.py`. Model IDs are the short aliases `"sonnet"` / `"opus"` / `"haiku"`.
