# 05 — Guardrails, Gates & Hooks

> Prompts are probabilistic, code is deterministic. When a mistake costs money, security or compliance, move the rule out of the prompt and into code.

Basecamp: *Defend the design choices to a technical buyer*.

## The determinism ladder

| Rung | Mechanism | Reliability | Use for |
|---|---|---|---|
| 1 | System prompt guidance | ~90–95 % | Tone, style, soft preferences. |
| 2 | Structured output (schema, `strict`) | shape guaranteed | Output that code consumes. |
| 3 | **Gate in the tool handler** | 100 % | Preconditions ("verify identity before refund"). |
| 4 | **Hook** (Agent SDK `PreToolUse` / Tool Runner per-turn hooks) | 100 % | Policy across many tools (amount limits, PII redaction, audit log). |
| 5 | Human in the loop | — | Irreversible or high-value actions. |

## Core rules

1. **State lives server-side**, not in the model's context (`session.verified_customer_id`).
2. **Gates block mismatches too**, not only "missing".
3. **Policy before the action** (`PreToolUse`), **data shaping after** (`PostToolUse`).
4. **Human handoff is a structured object** (customer, summary, root cause, amount, recommended action) — the human doesn't read the transcript.
5. **Test the gate without the model** — call the tool function directly.

## Anti-patterns

- "Add a stronger instruction / few-shot" as the fix for a financial failure.
- Blocking in `PostToolUse` — the action already happened.
- Handoff objects with placeholder text ("n/a").

## Code here

| Folder | Shows | Cert |
|---|---|---|
| [`01_prerequisite_gates_and_handoff/`](01_prerequisite_gates_and_handoff/) | Gate notes + structured human handoff via `messages.parse`; gate code and tests in project 02. | 1.4 |
| [`02_sdk_hooks/`](02_sdk_hooks/) | `PreToolUse` / `PostToolUse` hooks in the Agent SDK. | 1.5 |

Applied end-to-end in [project 02 — support agent](../../projects/02_support_agent/), gates tested with pytest. Agent SDK basics: [02 / Agent SDK](../02_agentic_loop/agent_sdk/).

## Sources

- Agent SDK hooks — <https://code.claude.com/docs/en/agent-sdk/hooks>
- Tool Runner — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner>
