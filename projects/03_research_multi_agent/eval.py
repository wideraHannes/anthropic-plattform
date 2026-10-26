"""
Eval for the research system — three code graders, no LLM judge needed.

    uv run python eval.py

1. Faithfulness: every worker quote must appear verbatim in the document it cites.
2. Coverage:     the brief must mention the facts a good answer cannot miss.
3. Citations:    the brief must cite documents by their [name] tag.
"""

import re

from research import CORPUS, DEFAULT_QUESTION, run

# Facts a correct brief for DEFAULT_QUESTION has to surface (regex, case-insensitive).
MUST_MENTION = {
    "cold-climate limit (-15 °C)": r"-\s?15\s?°?\s?C",
    "missing Swedish app language": r"swedish",
    "Norway subsidy needs -25 °C": r"-\s?25|enova",
    "expansion budget EUR 15m": r"15\s?(million|m\b)",
}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def main() -> None:
    result = run(DEFAULT_QUESTION)
    brief = result["brief"]

    findings = [f for r in result["reports"] for f in r.findings]
    unfaithful = [f for f in findings if _norm(f.quote) not in _norm(CORPUS.get(f.doc, ""))]
    missing = [label for label, pattern in MUST_MENTION.items() if not re.search(pattern, brief, re.IGNORECASE)]
    cited = {d for d in CORPUS if f"[{d}]" in brief}

    print("\n" + brief)
    print("\n=== eval ===")
    print(f"faithfulness: {len(findings) - len(unfaithful)}/{len(findings)} quotes found verbatim")
    for f in unfaithful:
        print(f"  NOT FOUND in {f.doc}: {f.quote!r}")
    print(f"coverage    : {len(MUST_MENTION) - len(missing)}/{len(MUST_MENTION)} must-mention facts")
    for label in missing:
        print(f"  MISSING: {label}")
    print(f"citations   : brief cites {len(cited)}/{len(CORPUS)} documents {sorted(cited)}")
    print("usage       :")
    for role, u in result["usage"].items():
        print(f"  {role:12} {u}")


if __name__ == "__main__":
    main()
