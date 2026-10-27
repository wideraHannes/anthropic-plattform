# Workflow Enforcement and Handoff

Notes on [1.4](https://claudecertificationguide.com/learn/1-agentic-architecture/1-4-workflow-enforcement-handoff).

## Prompt vs. code

- **Prompt** — probabilistic (~90–95%). Fine for style/formatting.
- **Programmatic gate** — deterministic (100%). Use whenever failure means money loss, security breach, or compliance violation.

## Prerequisite gate

Code in the tool handler that blocks execution until a precondition is met. The model cannot argue past it.

```python
@beta_tool
def process_refund(order_id: str, amount: float, reason: str) -> str:
    if session.verified_customer_id is None:
        raise ToolError('{"errorCategory": "permission", "isRetryable": false, ...}')
```

Canonical example: "always verify identity" prompt fails 8% in production; gate drops it to 0%.

**Code:** the gates live in [project 02 `tools.py`](../../../projects/02_support_agent/tools.py) (verify → own order → once → ≤ amount → ≤ €150) and are proven without a model in [`test_tools.py`](../../../projects/02_support_agent/test_tools.py).

## Handoff — 5 mandatory fields

Human agents don't see the transcript. Missing any field forces them to restart.

1. `customer_id`
2. `conversation_summary`
3. `root_cause`
4. `refund_amount` (0 if none)
5. `recommended_action`

**Code:** [`structured_handoff.py`](structured_handoff.py) — `messages.parse(output_format=Handoff)` with `min_length` constraints, plus a coverage check that all three concerns of a multi-concern request survive.

## Multi-concern requests

Decompose → investigate in parallel with shared context → synthesize one resolution. Never pick only the first item or open separate conversations.

## Exam traps

- "Improve the prompt" / "add few-shot" — probabilistic, never sufficient for financial/compliance.
- "Add a routing classifier" — routes between agents; doesn't enforce workflow inside one.
- Handoff missing fields — hard fail.
