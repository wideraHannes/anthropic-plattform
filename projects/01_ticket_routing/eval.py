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


def run_one(ticket: dict, prompt: str) -> dict:
    start = time.perf_counter()
    routing, usage = classify(ticket["text"], prompt)
    return {
        "ticket": ticket,
        "routing": routing,
        "usage": usage,
        "seconds": time.perf_counter() - start,
    }


def main(prompt: str) -> None:
    # First call alone writes the cache; the rest run in parallel and can read it.
    results = [run_one(TICKETS[0], prompt)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results += list(pool.map(lambda t: run_one(t, prompt), TICKETS[1:]))

    intent_ok = urgency_ok = 0
    for r in results:
        t, got = r["ticket"], r["routing"]
        i_ok, u_ok = got.intent == t["intent"], got.urgency == t["urgency"]
        intent_ok += i_ok
        urgency_ok += u_ok
        if not (i_ok and u_ok):
            print(f"FAIL {t['id']}: expected {t['intent']}/{t['urgency']}, "
                  f"got {got.intent}/{got.urgency}\n     {t['text']}\n     why: {got.reasoning}")

    n = len(results)
    tokens = {
        k: sum(getattr(r["usage"], k) or 0 for r in results)
        for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    }
    latencies = sorted(r["seconds"] for r in results)
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
