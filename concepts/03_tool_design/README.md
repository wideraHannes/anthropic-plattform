# 03 — Tool Design (the Agent–Computer Interface)

> Tools are the agent's UI. Spend as much care on tool names, descriptions and errors as you would on a human-facing API — Claude only sees `name + description + input_schema`.

Basecamp: *Read and modify an unfamiliar agent's tool definitions*.

## Core rules

1. **Description = routing signal.** Purpose, inputs, 1–3 example uses, limits, and explicit boundaries to sibling tools ("use `lookup_order` for order IDs, not this").
2. **Few, focused tools per role** (≈ 4–5). Prefer one `schedule_event` over `list_users` + `list_events` + `create_event`.
3. **Constrain inputs in the schema** (enums, formats, `strict: true`), not in prose.
4. **Structured errors**: `errorCategory` (transient · validation · business · permission), `isRetryable`, a human-readable `description`. An empty result is *not* an error.
5. **Return what the model needs, not everything you have.** Trim payloads; meaningful IDs/names over UUID dumps.
6. **`tool_choice`** — `auto` for chat, force a specific tool for a mandatory step / structured output (on models that support forcing; on newest models use `auto` + `strict` or structured outputs).

## MCP in a product

MCP is how you *ship* tools to many agents. In your own app: Messages API **MCP connector** (`mcp_servers` + `mcp_toolset`) or the Agent SDK's `mcp_servers` option. Configuring MCP for *your coding assistant* (`.mcp.json`) is Claude Code territory, not covered in this repo.

## Anti-patterns

- Overlapping descriptions → misrouting that no system prompt fixes.
- One 18-tool super-agent.
- Generic `fetch_url(url)` when the agent only ever needs `get_docs_page(slug)`.
- Raising exceptions instead of returning a structured error result.

## Code here

| Folder | Shows | Cert |
|---|---|---|
| [`01_schema_design/`](01_schema_design/) | Minimal vs production descriptions, measured misrouting A/B. | 2.1 |
| [`02_structured_errors/`](02_structured_errors/) | Error categories driving retry vs escalate. | 2.2 |
| [`03_tool_choice/`](03_tool_choice/) | Overloaded vs scoped toolsets, constrained tools, `tool_choice` modes. | 2.3 |

## Sources

- Writing tools for agents — <https://www.anthropic.com/engineering/writing-tools-for-agents>
- Tool use overview — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview>
- MCP connector — <https://platform.claude.com/docs/en/agents-and-tools/mcp-connector>
