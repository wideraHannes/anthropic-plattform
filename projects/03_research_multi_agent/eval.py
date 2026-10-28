"""
Eval for the research system — three code graders + one LLM judge.

    uv run python eval.py

1. Faithfulness (workers, code):   every worker quote appears verbatim in its document.
2. Groundedness (brief, LLM judge): every factual claim in the brief is backed by a finding.
3. Coverage (code):                the brief mentions the facts a good answer cannot miss.
4. Citations (code):               the brief cites documents by their [name] tag.

Code where the check is mechanical, a judge only where it needs judgement.
"""

import re

from pydantic import BaseModel, Field

from config import client, settings
from research import CORPUS, DEFAULT_QUESTION, run

# Facts a correct brief for DEFAULT_QUESTION has to surface (regex, case-insensitive).
MUST_MENTION = {
    "cold-climate limit (-15 °C)": r"-\s?15\s?°?\s?C",
    "missing Swedish app language": r"swedish",
    "Norway subsidy needs -25 °C": r"-\s?25|enova",
    "expansion budget EUR 15m": r"15\s?(million|m\b)",
}

JUDGE_SYSTEM = """You check a decision brief against the research findings it was written from.
Split the brief into its individual factual claims (numbers, facts about markets,
products, competitors, rules, customers). Skip the recommendation itself and
opinions. A claim is supported only if the findings state it; general world
knowledge does not count. Explain briefly, then decide."""


class Claim(BaseModel):
    claim: str
    reason: str = Field(description="Which finding supports it, or why none does.")
    supported: bool


class Judgement(BaseModel):
    claims: list[Claim]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def judge_brief(brief: str, findings: list) -> list[Claim]:
    evidence = "\n".join(f'- {f.claim} [{f.doc}] "{f.quote}"' for f in findings)
    response = client.messages.parse(
        model=settings.default_model,
        max_tokens=4096,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": f"<findings>\n{evidence}\n</findings>\n\n<brief>\n{brief}\n</brief>"}],
        output_format=Judgement,
    )
    return response.parsed_output.claims


def main() -> None:
    result = run(DEFAULT_QUESTION)
    brief = result["brief"]
    findings = [f for r in result["reports"] for f in r.findings]

    unfaithful = [f for f in findings if normalize(f.quote) not in normalize(CORPUS.get(f.doc, ""))]
    claims = judge_brief(brief, findings)
    ungrounded = [c for c in claims if not c.supported]
    missing = [label for label, pattern in MUST_MENTION.items() if not re.search(pattern, brief, re.IGNORECASE)]
    cited = {d for d in CORPUS if f"[{d}]" in brief}

    print("\n" + brief)
    print("\n=== eval ===")
    print(f"faithfulness: {len(findings) - len(unfaithful)}/{len(findings)} worker quotes found verbatim")
    for f in unfaithful:
        print(f"  NOT FOUND in {f.doc}: {f.quote!r}")
    print(f"groundedness: {len(claims) - len(ungrounded)}/{len(claims)} brief claims backed by findings")
    for c in ungrounded:
        print(f"  UNSUPPORTED: {c.claim}\n    why: {c.reason}")
    print(f"coverage    : {len(MUST_MENTION) - len(missing)}/{len(MUST_MENTION)} must-mention facts")
    for label in missing:
        print(f"  MISSING: {label}")
    print(f"citations   : brief cites {len(cited)}/{len(CORPUS)} documents {sorted(cited)}")
    print("usage       :")
    for role, u in result["usage"].items():
        print(f"  {role:12} {u}")


if __name__ == "__main__":
    main()
