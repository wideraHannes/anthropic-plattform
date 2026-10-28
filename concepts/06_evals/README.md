# 06 — Evals

> If you can't measure it, you can't improve it — and you can't defend it to a customer. An eval is a fixed set of inputs + a grader + a number you compare before and after a change.

## Core rules

1. **Define success criteria first** — specific, measurable, tied to the use case (accuracy ≥ 90 %, never refund unverified, p95 latency < 3 s, cost per ticket < $0.01).
2. **Build the dataset from reality** — real transcripts/tickets, plus deliberate edge cases and adversarial inputs. Volume of automated cases beats a few hand-graded ones.
3. **Pick the cheapest grader that is reliable**
   | Grader | Use for |
   |---|---|
   | **Code** (exact match, regex, schema, state check) | Labels, extracted fields, "did the agent call X before Y". |
   | **Unit test** (pytest, no model) | Anything deterministic: gates, validators, tool logic. Free, runs in CI. |
   | **LLM-as-judge** with a rubric | Tone, faithfulness, completeness. Ask for reasoning, then a verdict. |
   | **Human** | Calibrating the LLM judge; rare, expensive. |
4. **For agents, grade outcomes *and* trajectories** — final state (refund issued?), plus process checks (verified first? within N turns?).
5. **Track quality, latency and cost together.** A better prompt that doubles cost is a trade-off, not a win.
6. **Read failing transcripts.** The number tells you *that* it failed; the transcript tells you *why*.
7. **One change at a time**, same dataset, compare runs.

## Tests vs evals

- **Test** (pytest): pass/fail on code that must *always* hold — a refund gate, a URL validator. No model, no tokens. If it fails, no prompt can save you.
- **Eval** (`eval.py`): a *number* for behaviour that varies — accuracy, scenario pass rate, groundedness. Compare before/after a change.

Use both: [project 02](../../projects/02_support_agent/) has `test_tools.py` (gates) and `eval.py` (agent behaviour). Eval frameworks (DeepEval, promptfoo …) earn their place once you have many graders and want dashboards; for a handful of code graders and one judge they hide more than they save.

## Anti-patterns

- Vibe-checking on three examples.
- Tuning the prompt on the same cases you report (keep a held-out set once the set grows).
- An LLM judge with no rubric ("is this good? yes/no").

## Code here

| File | Shows |
|---|---|
| [`graders.py`](graders.py) | Code grader vs LLM-judge (`messages.parse` → `Verdict`) on the same outputs. |

Every project in [`../../projects/`](../../projects/) has its own `eval.py` — that's where evals become real.

## Sources

- Define success criteria — <https://platform.claude.com/docs/en/test-and-evaluate/define-success>
- Develop tests — <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests>
- Demystifying evals for AI agents — <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
