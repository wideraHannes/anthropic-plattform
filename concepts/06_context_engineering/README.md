# 06 — Context Engineering

> Context is a finite resource with diminishing returns. The job is to find the *smallest set of high-signal tokens* that makes the desired behaviour likely — at every turn, not just in the first prompt.

Basecamp: *Workshop · Context Engineering*.

## What goes into the context window

System prompt · tool definitions · examples · message history · tool results · retrieved documents · thinking. Every one of these competes for the model's attention.

## Core rules

1. **System prompt at the right altitude** — specific enough to guide, general enough to not be a brittle if/else list. Organise with sections / XML tags.
2. **Minimal, non-overlapping toolset** — if a human can't tell which tool to use, neither can the model (→ [03](../03_tool_design/)).
3. **Just-in-time retrieval** — keep lightweight references (IDs, paths, URLs) and let the agent load details via tools, instead of stuffing everything upfront.
4. **Long-horizon techniques**
   - **Compaction** — summarise history near the limit (server-side: `compact_20260112`).
   - **Context editing** — clear stale tool results / thinking (`clear_tool_uses_20250919`).
   - **Structured note-taking / memory** — agent writes progress to a file or the memory tool, reloads it later.
   - **Subagents** — explore in a fresh context, return a condensed summary (→ [04](../04_workflows_and_multi_agent/)).
5. **Stale state is poison.** Old tool results outlive the files they describe; after changes, start fresh with a curated summary.
6. **Stable prefix first** — keeps prompt caching working (→ [08](../08_inference_optimization/)).

## Anti-patterns

- Dumping the whole knowledge base into the system prompt "just in case".
- Forwarding full subagent transcripts to the coordinator instead of compact findings.
- Resuming a session after the underlying data changed.

## Code here

| Folder | Shows | Cert |
|---|---|---|
| [`01_session_state/`](01_session_state/) | Resume vs fork vs fresh start + summary. | 1.7 |

Applied in [project 03](../../projects/03_research_multi_agent/): workers get only their slice of sources and return compressed, cited findings.

## Sources

- Effective context engineering for AI agents — <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Context windows — <https://platform.claude.com/docs/en/build-with-claude/context-windows>
- Context editing — <https://platform.claude.com/docs/en/build-with-claude/context-editing>
- Memory tool — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool>
