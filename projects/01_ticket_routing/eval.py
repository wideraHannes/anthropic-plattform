"""
Eval for the ticket router: accuracy, latency and tokens on tickets.json.

    uv run python eval.py minimal     # baseline prompt
    uv run python eval.py detailed    # rescued prompt

Grader: code (exact match on intent and urgency). Read the FAIL lines —
the reasoning field tells you why the model chose what it chose.
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from router import PROMPTS, classify

TICKETS = json.loads((Path(__file__).parent / "tickets.json").read_text())
USAGE_KEYS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def run_one(ticket: dict, prompt: str) -> tuple[dict, object, float]:
    start = time.perf_counter()
    response = classify(ticket["text"], prompt)
    return ticket, response, time.perf_counter() - start


def main(prompt: str) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda t: run_one(t, prompt), TICKETS))

    intent_ok = urgency_ok = 0
    for ticket, response, _ in results:
        got = response.parsed_output
        intent_ok += got.intent == ticket["intent"]
        urgency_ok += got.urgency == ticket["urgency"]
        if (got.intent, got.urgency) != (ticket["intent"], ticket["urgency"]):
            print(f"FAIL {ticket['id']}: expected {ticket['intent']}/{ticket['urgency']}, "
                  f"got {got.intent}/{got.urgency}\n     {ticket['text']}\n     why: {got.reasoning}")

    n = len(results)
    tokens = {k: sum(getattr(r.usage, k) or 0 for _, r, _ in results) for k in USAGE_KEYS}
    latencies = sorted(s for _, _, s in results)
    print(f"\n=== prompt: {prompt} ===")
    print(f"intent accuracy : {intent_ok}/{n}  ({intent_ok / n:.0%})")
    print(f"urgency accuracy: {urgency_ok}/{n}  ({urgency_ok / n:.0%})")
    print(f"latency p50/max : {latencies[n // 2]:.2f}s / {latencies[-1]:.2f}s")
    print(f"tokens          : {tokens}")


if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "detailed"
    if choice not in PROMPTS:
        sys.exit(f"unknown prompt {choice!r}, choose from {list(PROMPTS)}")
    main(choice)
