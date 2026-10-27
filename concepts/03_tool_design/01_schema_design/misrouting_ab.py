"""
Tool-schema A/B (cert 2.1): MINIMAL vs PRODUCTION-GRADE descriptions.

Same tool names, same input_schema — only `description` differs. Each query is
routed by both tool sets; the table shows which tool Claude picked.

    uv run python misrouting_ab.py
"""

from config import client, settings

INPUT_SCHEMA = {
    "type": "object",
    "properties": {"query": {"type": "string", "description": "Natural-language user request."}},
    "required": ["query"],
}

MINIMAL = {
    "get_customer": "Retrieves customer information.",
    "lookup_order": "Retrieves order details.",
}

# The five elements: purpose · inputs · example uses · limits · boundary to the sibling tool.
PRODUCTION = {
    "get_customer": (
        "Primary purpose: fetch a CUSTOMER RECORD (identity, contact info, billing address, loyalty tier, account status).\n"
        "Input: a customer identifier — customer_id, email, or phone number. Not an order id.\n"
        "Use for: 'email on file for customer 4421', 'loyalty tier for jane@acme.com'.\n"
        "Does NOT return: order history, shipment status, refunds, line items.\n"
        "Do NOT use for order-specific queries — use `lookup_order`, even when a customer is mentioned."
    ),
    "lookup_order": (
        "Primary purpose: fetch a single ORDER (line items, shipment status, refund status, totals).\n"
        "Input: an order id (e.g. 'A-8891') OR a (customer, relative time) pair like 'customer 4421, yesterday'.\n"
        "Use for: 'shipping status of order A-8891', 'items in the order customer X placed yesterday'.\n"
        "Does NOT return: customer profile fields (email, address, loyalty tier).\n"
        "Do NOT use for customer-profile lookups — use `get_customer`."
    ),
}

SYSTEM = "You are a customer-service backend router. For each request, call exactly one tool. Do not ask questions."

# (query, expected tool) — the last one is the trap: mentions an order, asks for a profile field.
CASES = [
    ("What's the shipping status of order #A-8891 for customer 4421?", "lookup_order"),
    ("Get the loyalty tier for customer 4421.", "get_customer"),
    ("Which items were in the order that customer 4421 placed yesterday?", "lookup_order"),
    ("Show the billing address on file for user 9910.", "get_customer"),
    ("Find the refund status of order 77123.", "lookup_order"),
    ("What email do we have on file for the customer who placed order A-8891?", "get_customer"),
]


def pick_tool(descriptions: dict[str, str], query: str) -> str | None:
    response = client.messages.create(
        model=settings.default_model,
        max_tokens=256,
        system=SYSTEM,
        tools=[{"name": n, "description": d, "input_schema": INPUT_SCHEMA} for n, d in descriptions.items()],
        messages=[{"role": "user", "content": query}],
    )
    return next((b.name for b in response.content if b.type == "tool_use"), None)


def main() -> None:
    hits = {"minimal": 0, "production": 0}
    print(f"{'query':<72} {'expected':<13} {'minimal':<14} production")
    for query, expected in CASES:
        picks = {"minimal": pick_tool(MINIMAL, query), "production": pick_tool(PRODUCTION, query)}
        marks = {}
        for name, pick in picks.items():
            hits[name] += pick == expected
            marks[name] = f"{'✓' if pick == expected else '✗'} {pick}"
        print(f"{query:<72} {expected:<13} {marks['minimal']:<14} {marks['production']}")
    for name, n in hits.items():
        print(f"{name:<11}: {n}/{len(CASES)}")


if __name__ == "__main__":
    main()
