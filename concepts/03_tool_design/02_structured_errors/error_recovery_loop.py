"""
Structured error responses (cert 2.2): does the agent pick the right recovery?

A scripted order-lookup tool returns one error category per scenario. The
grader counts how often the model called the tool:
  transient / validation → retry           → 2 calls
  business / permission  → stop, explain   → 1 call
  valid empty result     → no such order   → 1 call (retrying it is the trap)

    uv run python error_recovery_loop.py
"""

import json

from config import client, settings


def error(category: str, retryable: bool, description: str) -> dict:
    return {"isError": True, "errorCategory": category, "isRetryable": retryable, "description": description}


TRANSIENT = error("transient", True, "Upstream order-service timed out.")
VALIDATION = error("validation", True, "`order_id` must match /^A-\\d{4}$/, e.g. 'A-8891'.")
BUSINESS = error("business", False, "Order is archived; status lookups are closed after 2 years.")
PERMISSION = error("permission", False, "Caller lacks scope `orders:read:pii`.")
EMPTY = {"isError": False, "resultCount": 0, "data": []}
SUCCESS = {"isError": False, "resultCount": 1, "data": [{"order_id": "A-8891", "status": "shipped"}]}

TOOL = {
    "name": "lookup_order",
    "description": (
        "Fetch a single order by id.\n"
        "Success: {isError: false, resultCount, data}. resultCount=0 means no such order — do NOT retry.\n"
        "Failure: {isError: true, errorCategory, isRetryable, description}."
    ),
    "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
}

SYSTEM = """You look up orders. Call `lookup_order`, then read the result.
  transient  → retry with the same input.
  validation → retry with corrected input.
  business or permission → do not retry, explain and stop.
  resultCount=0 → the order doesn't exist, stop."""

# (label, user message, scripted tool results, expected number of tool calls)
SCENARIOS = [
    ("transient → retry", "What's the status of order A-8891?", [TRANSIENT, SUCCESS], 2),
    ("validation → fix input", "What's the status of order 8891?", [VALIDATION, SUCCESS], 2),
    ("business → stop", "What's the status of order A-8891?", [BUSINESS], 1),
    ("permission → stop", "What's the status of order A-8891?", [PERMISSION], 1),
    ("empty → don't retry", "What's the status of order A-0000?", [EMPTY], 1),
]


def run_agent(question: str, script: list[dict]) -> int:
    """Hand-rolled loop so the is_error branch is visible. Returns the number of tool calls."""
    messages = [{"role": "user", "content": question}]
    calls = 0
    for _ in range(6):
        response = client.messages.create(
            model=settings.default_model,
            max_tokens=512,
            system=SYSTEM,
            tools=[TOOL],
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            print("  final →", "".join(b.text for b in response.content if b.type == "text").strip())
            return calls

        results = []
        for tool_use in tool_uses:
            result = script[min(calls, len(script) - 1)]  # repeat the last outcome if it keeps calling
            calls += 1
            print(f"  call {calls}: {tool_use.input} → {result.get('errorCategory', 'ok')}")
            results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result),
                "is_error": result["isError"],
            })
        messages.append({"role": "user", "content": results})
    return calls


def main() -> None:
    passed = 0
    for label, question, script, expected_calls in SCENARIOS:
        print(f"\n─── {label} ───")
        calls = run_agent(question, script)
        ok = calls == expected_calls
        passed += ok
        print(f"  {'PASS' if ok else 'FAIL'}: {calls} tool call(s), expected {expected_calls}")
    print(f"\n=== {passed}/{len(SCENARIOS)} recoveries correct ===")


if __name__ == "__main__":
    main()
