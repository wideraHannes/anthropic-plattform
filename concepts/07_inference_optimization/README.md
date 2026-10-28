# 07 — Inference Optimization (cost · latency · quality)

> Optimise cost per *completed task*, not per request. Free wins first (caching, trimming, batching), trade-offs second (effort, model choice).

## The levers, in order

| # | Lever | Effect | Notes |
|---|---|---|---|
| 1 | **Prompt caching** | cache reads ≈ 10 % of input price, lower latency | Prefix match: `tools → system → messages`. Stable content first, volatile last. Verify via `usage.cache_read_input_tokens`. Minimum prefix size is model-dependent. |
| 2 | **Input hygiene** | fewer tokens every turn | Trim tool results, drop stale history. |
| 3 | **Batch API** | −50 % | Async, results within 24 h; not for interactive traffic. First-party API / Claude Platform on AWS only. |
| 4 | **Effort** (`output_config.effort`) | fewer thinking/output tokens | `low` for classification/chat, `high`/`xhigh` for agentic coding. Measure per route. |
| 5 | **Model choice** | price × capability | Opus for hard reasoning, Sonnet for most production, Haiku for high-volume simple tasks / subagents. Try the strong model at lower effort before building a cascade. |
| 6 | **Streaming** | perceived latency (TTFT) | Required for large `max_tokens`. |
| 7 | **Token counting** | predict cost before sending | `messages.count_tokens`. |

## Core rules

1. **Measure first** — log `usage` (input, output, cache read/write) per request.
2. **Never put timestamps, UUIDs or unsorted JSON in the cached prefix** — silent cache misses.
3. **Caches are model-scoped** — a multi-model cascade forfeits cache reuse.
4. **Re-run your eval after every optimisation** (→ [06](../06_evals/)) — cheaper but wrong is not cheaper.

## Code here

| File | Shows |
|---|---|
| [`prompt_caching.py`](prompt_caching.py) | Same large system prompt twice → cache write, then cache read; prints `usage`. |

## Sources

- Prompt caching — <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>
- Batch processing — <https://platform.claude.com/docs/en/build-with-claude/batch-processing>
- Effort — <https://platform.claude.com/docs/en/build-with-claude/effort>
- Reduce latency — <https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency>
- Choosing a model — <https://platform.claude.com/docs/en/about-claude/models/choosing-a-model>
