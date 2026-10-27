# 4D Framework — AI Fluency

Four competencies for working *with* AI: **Delegation, Description, Discernment, Diligence** (Dakan & Feller). Applied here to one build:

> A community health clinic needs a way for patients to check wait times before coming in.

```
outer loop:  Delegation ─────────────────────► Diligence
             (should AI do it?)               (can we vouch for it?)
inner loop:  Description ◄──────────────────► Discernment
             (tell AI what you want)          (judge what came back)
```

**Modes:** *Automation* (AI does it, you check) · *Augmentation* (you build together) · *Agency* (AI acts within your boundaries).

## The four Ds

| D | Core question | In this project |
|---|---|---|
| [1 · Delegation](1_delegation/) | Should AI do this, and in which mode? | [Problem brief + delegation plan](1_delegation/handsons.md) |
| [2 · Description](2_description/) | How do I tell AI what I want? | [Requirement → spec → tests](2_description/handson.md) |
| [3 · Discernment](3_discernment/) | Is the result actually *good*? | [Design spec](3_discernment/design.md) → [UX audit](3_discernment/ux_feedback.md) |
| [4 · Diligence](4_diligence/) | Can I stand behind it? | Tests, documented limits, no personal data |

## Takeaways

- **Delegation:** delegate implementation, keep judgement.
- **Description:** tests are the most precise description.
- **Discernment:** all 25 tests passed, yet the UX audit still found unclear labels, missing feedback and raw JSON errors.
- **Diligence:** verify, disclose AI use, understand what you ship.

## Run

```bash
cd code && uv run pytest -q   # 31 tests
```

## Sources

- [Framework for AI Fluency (Ringling College)](https://ringling.libguides.com/ai/framework)
- [AI Fluency: Framework and foundations (Anthropic Academy)](https://academy.claude.com/courses/ai-fluency-framework-foundations)
