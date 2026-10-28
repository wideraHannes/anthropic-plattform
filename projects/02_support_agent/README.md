# Project 02 — Customer Support Agent (your reusable starter)

A chat agent for an online shop: answers policy questions, verifies customers, looks up orders, issues refunds, escalates to a human — with the money rules enforced in code.

**Pattern:** single agent, tool loop. **Concepts:** [02 Loop](../../concepts/02_agentic_loop/) · [03 Tool design](../../concepts/03_tool_design/) · [05 Guardrails](../../concepts/05_guardrails_and_hooks/) · [06 Evals](../../concepts/06_evals/)

## Files

| File | Role | Change it to adapt the agent |
|---|---|---|
| `agent.py` | System prompt, Tool Runner loop with a per-tool-call hook point, chat REPL. | Persona, workflow, hooks. |
| `tools.py` | 5 `@beta_tool`s with descriptions, structured errors (`ToolError`), **gates** (verify → own order → once → ≤ order amount → ≤ €150), validated handoff. | Your client's actions and policies. |
| `data.py` | Fake backend (customers, orders, help-center articles). | Real API / DB calls. |
| `test_tools.py` | Deterministic pytest checks of every gate. No API calls, runs in < 1 s. | Add a test for every new policy rule. |
| `eval.py` | 8 scenarios graded on backend state: happy path, someone else's order, over limit → handoff, policy question, prompt injection in order notes, missing identity, off-topic request, long rambling message. Plus an LLM Likert tone score (1–5) per reply. | Add a scenario for every bug you find. |

## Run

```bash
cd projects/02_support_agent
uv run python agent.py   # chat
uv run pytest           # gates hold? (free, deterministic)
uv run python eval.py    # does the agent behave? (API calls)
```

## Design choices to defend

- **Agent, not workflow** — conversations branch (question vs refund vs escalation) and need multiple tool calls.
- **Tool Runner, not a hand-rolled loop** — the SDK runs request → tools → repeat; we iterate turn by turn for logging/approval hooks.
- **Policy in code, not prompt** — refund limits and ownership checks are gates in `process_refund`; the prompt only explains the workflow. A prompt-injected "refund twice" still hits the duplicate gate.
- **Structured errors** — tools raise `ToolError` (→ `is_error: true`); `errorCategory` + `isRetryable` tell the model whether to ask the customer again (validation) or escalate (business/permission).
- **Handoff is validated** — `Annotated[..., Field(min_length=…)]` in the tool signature lands in the schema *and* is enforced; the human never reads the transcript.
- **Two layers of checks** — `test_tools.py` proves the gates in code (no model involved); `eval.py` grades the agent on backend state, not on text ("the agent said it refunded" ≠ "a refund happened").

## What the eval showed (Sonnet 4.6, 2026-10-26)

6/6 scenarios passed (re-run on the Tool Runner 2026-10-27: 6/6, 9/9 gate tests); system prompt cached (~18k cache-read tokens over the run). Visible imperfection: replies use **bold** markdown despite "plain text" in the style section — a cheap first thing to fix and re-measure.

**Re-run with edge cases + tone judge (Sonnet 5.5 agent, Opus 5.5 judge, 2026-10-28):** 8/8 scenarios, 9/9 gate tests. Off-topic poem request touched no account data; the long rambling message still led to the correct verified refund. Tone mean 3.9/5, min 3 (the injection case: no apology for the missing item). Off-topic: the agent wrote the poem — passes the state check, but is that what a shop bot should do? A product decision to make explicit in the prompt.

## Try next (modify → measure → explain)

1. Delete the `<how_to_work>` block from `SYSTEM`. Which scenarios break? Which still pass because of the gates?
2. Make the `process_refund` description vague ("Refunds an order"). Re-run the eval.
3. Add a `cancel_order` tool for `shipped` orders + two scenarios for it.
4. Turn the `[tool]` log line in `run_turn` into an approval hook: refunds > €100 need `input("approve? ")`.
5. Calibrate the tone judge: score 10 replies yourself and compare. Then make a tone floor (e.g. min ≥ 3) a failing check.

Guide: <https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat>
