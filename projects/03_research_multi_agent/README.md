# Project 03 — Multi-Agent Research

Answer a business question ("Should Acme enter the Nordic heat-pump market?") from a document corpus with a lead agent, parallel researchers and a synthesizer that writes a cited decision brief.

**Pattern:** orchestrator–workers + parallelization (hub-and-spoke). **Concepts:** [04 Multi-agent](../../concepts/04_workflows_and_multi_agent/) · [06 Evals](../../concepts/06_evals/)

```
question ──► planner (sees: corpus INDEX only)
                │  3–5 sub-questions + which docs to read
                ▼
      ┌─────────┼─────────┐   parallel
   worker    worker    worker  (sees: 1 sub-question + its docs only)
      └─────────┼─────────┘   findings = claim + doc + exact quote
                ▼
          synthesizer (sees: compressed findings only) ──► cited brief
```

## Files

| File | Role |
|---|---|
| `corpus/` | 6 short **fictional** documents (market, product, competitors, regulation, pilot feedback, finance). |
| `research.py` | Planner, workers (thread pool), synthesizer; structured outputs via `messages.parse`; token usage per role. |
| `eval.py` | Code graders (verbatim quotes, must-mention coverage, citations) + one LLM judge (brief claims grounded in findings). |

## Run

```bash
cd projects/03_research_multi_agent
uv run python research.py                      # default question
uv run python research.py "Should Acme sell HeatFlow in Finland?"
uv run python eval.py
```

## Design choices to defend

- **Planner sees an index, not the documents** — just-in-time retrieval; its context stays small no matter how big the corpus grows.
- **Workers are isolated** — each gets exactly one sub-question and its docs; no shared history, no cross-talk.
- **Findings carry exact quotes** — makes worker faithfulness checkable by *code*, not by another LLM.
- **LLM judge only where code can't decide** — whether a brief sentence is backed by a finding needs judgement; the judge lists each claim, reasons, then decides (`supported: bool`).
- **Synthesizer gets compressed findings**, not worker transcripts — that's the context budget that matters.
- **Validate model-chosen references** (`sq.docs` filtered against the corpus).
- **Cost:** compare `usage` per role — multi-agent spends more tokens in total but keeps each context small.

## What the eval showed (Sonnet 4.6, 2026-10-26)

24/24 quotes verbatim, 4/4 must-mention facts, 6/6 documents cited. Tokens: planner ~1.1k in, 5 workers ~5.6k in, synthesizer ~2.1k in.

**Re-run with the judge (2026-10-27):** 28/29 quotes verbatim (one quote stitched two sentences with `...`, which the code grader caught), **28/29 brief claims grounded**, 4/4 coverage, 6/6 cited. The judge flagged the brief calling the Norway subsidy "unknown" although the findings say the −28 °C variant meets the −25 °C rule. Whether the judge is right is for you to check (see Try next 0), but no regex could have raised the question.

**Earlier gap (now measured):** the first version's brief said *"Denmark's climate is the mildest of the four Nordic countries"*. That isn't in the corpus; it's the synthesizer's own world knowledge. The old eval only checked **worker** quotes and couldn't see this; the judge now does.

## Try next

0. Calibrate the judge: read 10 of its verdicts yourself. Do you agree? (An uncalibrated judge is a vibe check with extra steps.)
0b. Use the API's [citations](https://platform.claude.com/docs/en/build-with-claude/citations) on worker documents: quotes become verbatim by construction and the faithfulness grader becomes obsolete.
1. Remove the "together cover it fully" line from the planner prompt — does coverage drop?
2. Give every worker *all* documents. Compare tokens and faithfulness.
3. Add an evaluator–optimizer step: a reviewer checks the brief against the open questions and triggers a second worker round.
4. Replace `corpus/` with 20 real documents from a client domain.

Further reading: <https://www.anthropic.com/engineering/multi-agent-research-system>
