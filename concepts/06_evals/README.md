# 06 — Evals

> If you can't measure it, you can't improve it — and you can't defend it to a customer. An eval is a fixed set of inputs + a grader + a number you compare before and after a change.

## Core rules

1. **Define success criteria first** — specific, measurable, tied to the use case (accuracy ≥ 90 %, never refund unverified, p95 latency < 3 s, cost per ticket < $0.01).
2. **Be task-specific** — mirror the real task distribution, then add the edge cases the guide names: irrelevant or missing input, overly long input, hostile or harmful input, and ambiguous cases where even humans would disagree. Tag them and report per tag, so an average can't hide them.
3. **Automate** — structure every case so a grader returns a bool or a number (label, string match, score). No reading needed to get the score.
4. **Volume over quality** — many cases with a slightly noisier automated grader beat a few hand-graded ones. Grow the list, not the grader.
5. **Pick the fastest reliable grader** — in this order:
   | Grader | Use for |
   |---|---|
   | **Code** (exact/string match, regex, schema, state check, embeddings, ROUGE) | Labels, extracted fields, "did the agent call X before Y". Fastest, deterministic, no nuance. |
   | **LLM-based** with a rubric | Tone, faithfulness, privacy, context use. Test its reliability first, then scale. |
   | **Human** | Calibrating the LLM grader. Slow and expensive — avoid where possible. |
6. **LLM grader tips** — detailed rubric that anchors every level; empirical output (yes/no or 1–5, enforced by a schema); reasoning before the score (thinking on); a **different model** than the one that generated (`settings.judge_model`).
7. **For agents, grade outcomes *and* trajectories** — final state (refund issued?), plus process checks (verified first? within N turns?).
8. **Track quality, latency and cost together.** A better prompt that doubles cost is a trade-off, not a win.
9. **Read failing transcripts**, change one thing at a time, compare runs on the same dataset.

## Eval types (from the guide)

| Criterion | Method | Grader | Here |
|---|---|---|---|
| Task fidelity | Exact match | code | [P01](../../projects/01_ticket_routing/) |
| Consistency | Cosine similarity of embeddings | code | notebook §2 |
| Relevance & coherence | ROUGE-L vs. reference | code | notebook §3 |
| Tone & style | LLM Likert scale 1–5 | LLM | [P02](../../projects/02_support_agent/) |
| Privacy / groundedness | LLM binary yes/no | LLM | [P03](../../projects/03_research_multi_agent/) |
| Context use | LLM ordinal scale 1–5 | LLM | notebook §6 |

## Tests vs evals

- **Test** (pytest): pass/fail on code that must *always* hold — a refund gate, a URL validator. No model, no tokens. If it fails, no prompt can save you.
- **Eval** (`eval.py`): a *number* for behaviour that varies — accuracy, scenario pass rate, groundedness. Compare before/after a change.

Use both: [project 02](../../projects/02_support_agent/) has `test_tools.py` (gates) and `eval.py` (agent behaviour). Eval frameworks (DeepEval, promptfoo …) earn their place once you have many graders and want dashboards; for a handful of code graders and one judge they hide more than they save.

## Anti-patterns

- Vibe-checking on three examples; only "happy path" cases.
- Tuning the prompt on the same cases you report (keep a held-out set once the set grows).
- An LLM judge with no rubric ("is this good? yes/no"), free-text scores parsed with `int()`, or the generator grading itself.

## Code here

| File | Shows |
|---|---|
| [`eval_types.ipynb`](eval_types.ipynb) | All six eval types from the guide on tiny datasets with tagged edge cases. Run: `uv run --with jupyter jupyter lab` from this folder. |
| [`graders.py`](graders.py) | Code grader vs LLM judge (`messages.parse` → `Verdict`) on the same outputs — where they disagree is where you need the judge. |

Every project in [`../../projects/`](../../projects/) has its own `eval.py` — that's where evals become real.

## Sources

- Define success criteria — <https://platform.claude.com/docs/en/test-and-evaluate/define-success>
- Develop tests (design principles, example evals, grading) — <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests>
- Demystifying evals for AI agents — <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
