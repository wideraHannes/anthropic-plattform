"""
Ticket router: classify a support ticket into intent + urgency, then map it to a queue.

Pattern: single LLM call with structured output (`messages.parse`). No agent —
the path is fixed, so a workflow is cheaper and easier to test.

Two prompt versions live in PROMPTS so eval.py can measure before/after:
    uv run python router.py "My card was charged twice"
"""

import sys
from typing import Literal

from pydantic import BaseModel, Field

from config import client, settings

Intent = Literal["billing", "technical_issue", "account_access", "shipping", "feedback"]
Urgency = Literal["low", "high"]

QUEUES = {
    ("billing", "high"): "finance-priority",
    ("billing", "low"): "finance",
    ("technical_issue", "high"): "on-call-engineering",
    ("technical_issue", "low"): "product-support",
    ("account_access", "high"): "security",
    ("account_access", "low"): "product-support",
    ("shipping", "high"): "logistics-priority",
    ("shipping", "low"): "logistics",
    ("feedback", "high"): "product-support",
    ("feedback", "low"): "product-feedback",
}


class Routing(BaseModel):
    reasoning: str = Field(description="One or two sentences: why this intent and urgency.")
    intent: Intent
    urgency: Urgency


PROMPTS = {
    # Baseline: names the labels, decides nothing.
    "minimal": "Classify the customer support ticket by intent and urgency.",
    # Rescued: definitions, tie-break rules, the reason urgency matters.
    "detailed": """You route customer support tickets for a SaaS company with a web shop.
Your label decides which team sees the ticket first; a wrong "low" on an urgent
ticket means a customer waits a day, so judge urgency carefully.

<intents>
- billing: charges, invoices, prices, refunds, cancellations with money involved.
- technical_issue: bugs, errors, crashes, outages, performance problems.
- account_access: login, password, email change, suspicious account activity.
- shipping: delivery status, lost packages, shipping destinations and times.
- feedback: praise, feature requests, opinions without a concrete problem.
</intents>

<urgency>
- high: customer is blocked, losing money, security is at risk, many users are
  affected, or the customer is repeating an unresolved request.
- low: question, request, or minor annoyance with a workaround.
</urgency>

<rules>
- If a ticket mentions several issues, choose the one the customer needs solved
  first (usually the money or the security issue).
- A refund request is billing, even if an order number is mentioned.
- Tickets may be in any language.
</rules>""",
}


def classify(ticket: str, prompt: str = "detailed"):
    """Return the API response; `.parsed_output` is a validated `Routing`."""
    return client.messages.parse(
        model=settings.default_model,
        max_tokens=512,
        # Stable prefix (system) first, cached; the ticket comes last.
        system=[{"type": "text", "text": PROMPTS[prompt], "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": f"<ticket>\n{ticket}\n</ticket>"}],
        output_format=Routing,
    )


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or "I was charged twice and can't log in to check."
    routing = classify(text).parsed_output
    print(routing.model_dump_json(indent=2))
    print("queue:", QUEUES[(routing.intent, routing.urgency)])
