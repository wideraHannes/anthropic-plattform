# Project 03 — Multi-Agent Research

Answer a business question ("Should Acme enter the Nordic heat-pump market?") from a document corpus with a lead agent, parallel researchers and a synthesizer that writes a cited decision brief.

**Pattern:** orchestrator–workers + parallelization (hub-and-spoke). **Concepts:** [04 Multi-agent](../../concepts/04_workflows_and_multi_agent/) · [06 Context engineering](../../concepts/06_context_engineering/) · [07 Evals](../../concepts/07_evals/)

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
| `research.py` | Planner, workers (thread pool), synthesizer; token usage per role. |
| `eval.py` | Code graders: verbatim-quote faithfulness, must-mention coverage, citations. |

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
- **Findings carry exact quotes** — makes faithfulness checkable by *code*, not by another LLM.
- **Synthesizer gets compressed findings**, not worker transcripts — that's the context budget that matters.
- **Validate model-chosen references** (`sq.docs` filtered against the corpus).
- **Cost:** compare `usage` per role — multi-agent spends more tokens in total but keeps each context small.

## What the eval showed (Sonnet 4.6, 2026-10-26)

24/24 quotes verbatim, 4/4 must-mention facts, 6/6 documents cited. Tokens: planner ~1.1k in, 5 workers ~5.6k in, synthesizer ~2.1k in.

**Known gap:** the brief still said *"Denmark's climate is the mildest of the four Nordic countries"*. That isn't in the corpus; it's the synthesizer's own world knowledge. The eval only checks **worker** quotes, so it can't see this. A real limit of the eval, and a good first fix.

## Try next

0. Close the gap: make the synthesizer put each fact as `claim [doc]` on its own line, then check every claim against its doc's findings (code or an LLM judge).
1. Remove the "together cover it fully" line from the planner prompt — does coverage drop?
2. Give every worker *all* documents. Compare tokens and faithfulness.
3. Add an evaluator–optimizer step: a reviewer checks the brief against the open questions and triggers a second worker round.
4. Replace `corpus/` with 20 real documents from a client domain.

Further reading: <https://www.anthropic.com/engineering/multi-agent-research-system>
