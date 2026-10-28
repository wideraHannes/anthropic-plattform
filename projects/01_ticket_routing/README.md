# Project 01 — Ticket Routing

Classify incoming support tickets by **intent** and **urgency** and send them to the right queue.

**Pattern:** routing workflow — one structured LLM call, code does the rest. No agent needed.
**Concepts:** [04 Routing](../../concepts/04_workflows_and_multi_agent/) · [06 Evals](../../concepts/06_evals/) · [07 Caching](../../concepts/07_inference_optimization/)

## Files

| File | Role |
|---|---|
| `router.py` | `classify(ticket, prompt)` → `Routing(reasoning, intent, urgency)` via `client.messages.parse(output_format=Routing)`; queue mapping in code. Two prompt versions in `PROMPTS`. |
| `tickets.json` | 28 labelled tickets, each with a `tag`: typical (incl. multi-issue, German, repeat requests, fraud) plus the develop-tests edge cases — irrelevant (spam, `???`), long, hostile, injection, ambiguous. |
| `eval.py` | Exact-match accuracy per label and per tag, failing cases with the model's reasoning, latency, token usage. |

## Run

```bash
cd projects/01_ticket_routing
uv run python router.py "I was charged twice and can't log in"
uv run python eval.py minimal     # before
uv run python eval.py detailed    # after
```

## Design choices to defend

- **Workflow, not agent** — the path is always classify → route. Predictable, cheap, testable.
- **Structured outputs, not a forced tool call** — `messages.parse` with a Pydantic model guarantees the schema and returns a typed object. Forcing `tool_choice` is the older trick (rejected on the newest models) and costs the tool-use overhead on every call.
- **`reasoning` before the labels** in the schema — the model commits to an explanation first; it also makes failures debuggable.
- **An `other` intent → `manual-triage`** — spam and empty tickets have no right answer among five product labels; without it the eval can't even express the correct output.
- **Queue mapping in code**, not in the prompt — business rules change without re-prompting.
- **System prompt cached**, ticket last — stable prefix. (Caching only kicks in above the model's minimum prefix size; check `cache_read_input_tokens`.)

## What the eval showed (Sonnet 4.6, 2026-10-26)

| Prompt | Intent | Urgency | Input tokens |
|---|---|---|---|
| minimal | 22/22 | 21/22 | 17.6k |
| detailed | 22/22 | 22/22 | 23.3k (+33 %) |

Switching from a forced tool call to `messages.parse` (2026-10-27, detailed prompt): still 22/22 · 22/22, input tokens **23.3k → 13.4k**, since there's no tool definition and no tool-use overhead per call.

Lessons: a strong model gets most labels right with almost no prompt — the first 16 tickets scored 100 % with *both* prompts, so the dataset couldn't tell them apart. **An eval is only useful if it's hard enough to discriminate.** The detailed prompt fixes the urgency judgement (T15) at a token cost — a trade-off to state, not hide. The ~1k-token system prompt is just below the cacheable minimum (`cache_read = 0`); grow it with examples and caching starts paying.

**With edge cases (Sonnet 5.5, 2026-10-28, 28 tickets):** both prompts handle the new irrelevant, long, hostile and injection tickets (6/6 incl. `other` for spam/`???`). Remaining failures are judgement calls the per-tag report makes visible — *minimal* rates the ambiguous T28 ("slow … thinking about cancelling") high (churn risk); *detailed* misses T03 (crash on one page → "not blocking") and files T19 (VAT unclear on pricing page) as billing. The labels themselves are debatable: that's what "ambiguous cases where even humans disagree" means — have a second person label them before tuning against them. Caching now hits (16k cache-read tokens): Sonnet 5.5's minimum prefix is lower than 4.6's.

## Try next

1. Add 10 harder tickets to `tickets.json` — does accuracy hold?
2. Point `DEFAULT_MODEL` at Haiku in `.env` and compare accuracy vs tokens vs latency.
3. Add a third label (`language`) or a `confidence` field and route low-confidence tickets to a human.

Guide: <https://platform.claude.com/docs/en/about-claude/use-case-guides/ticket-routing>
