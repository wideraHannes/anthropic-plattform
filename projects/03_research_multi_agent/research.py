"""
Multi-agent research: orchestrator → parallel workers → synthesizer.

    uv run python research.py "Should Acme launch HeatFlow in Norway in 2027?"

Context engineering is the point of this project — each role sees only what it needs:
- planner:     the question + a one-line INDEX of the corpus (not the documents)
- workers:     one sub-question + only the documents assigned to it
- synthesizer: the question + the workers' compressed, quoted findings
"""

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel, Field

from config import client, settings

CORPUS_DIR = Path(__file__).parent / "corpus"
CORPUS = {p.stem: p.read_text() for p in sorted(CORPUS_DIR.glob("*.md"))}

DEFAULT_QUESTION = "Should Acme enter the Nordic heat pump market in 2027, and if so, which country first?"


class SubQuestion(BaseModel):
    question: str
    docs: list[str] = Field(min_length=1, description="Document names from the index to read.")


class Plan(BaseModel):
    sub_questions: list[SubQuestion] = Field(min_length=3, max_length=5)


class Finding(BaseModel):
    claim: str
    doc: str = Field(description="Name of the document the quote is from.")
    quote: str = Field(description="Exact sentence copied verbatim from that document.")


class WorkerReport(BaseModel):
    findings: list[Finding] = Field(min_length=1)
    open_questions: list[str] = Field(default_factory=list, description="What the documents could not answer.")


USAGE: dict[str, dict[str, int]] = {}


def _structured(role: str, system: str, prompt: str, schema: type[BaseModel]) -> BaseModel:
    tool = {"name": "submit", "description": f"Submit the {role} result.", "input_schema": schema.model_json_schema()}
    response = client.messages.create(
        model=settings.default_model,
        max_tokens=4096,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": "submit"},
        messages=[{"role": "user", "content": prompt}],
    )
    _track(role, response.usage)
    return schema.model_validate(next(b for b in response.content if b.type == "tool_use").input)


def _track(role: str, usage) -> None:
    u = USAGE.setdefault(role, {"calls": 0, "input_tokens": 0, "output_tokens": 0})
    u["calls"] += 1
    u["input_tokens"] += usage.input_tokens
    u["output_tokens"] += usage.output_tokens


def corpus_index() -> str:
    lines = []
    for name, text in CORPUS.items():
        summary = next((l for l in text.splitlines() if l.startswith("Summary:")), "")
        lines.append(f"- {name}: {summary.removeprefix('Summary:').strip()}")
    return "\n".join(lines)


def plan(question: str) -> Plan:
    system = """You are the lead researcher. You split a business question into 3-5
independent sub-questions that together cover it fully (market, product fit,
competition, regulation, customers, money — whatever applies), and assign each
the documents a researcher should read. You do not answer the question yourself."""
    prompt = f"<question>{question}</question>\n\n<corpus_index>\n{corpus_index()}\n</corpus_index>"
    result = _structured("planner", system, prompt, Plan)
    for sq in result.sub_questions:  # never trust model-chosen references blindly
        sq.docs = [d for d in sq.docs if d in CORPUS]
    result.sub_questions = [sq for sq in result.sub_questions if sq.docs]
    return result


def research(sub: SubQuestion) -> WorkerReport:
    system = """You are a researcher. Answer ONE sub-question using ONLY the documents
provided. Every finding must carry an exact quote copied from its document.
If the documents do not answer something, list it under open_questions."""
    docs = "\n\n".join(f'<document name="{d}">\n{CORPUS[d]}\n</document>' for d in sub.docs)
    prompt = f"{docs}\n\n<sub_question>{sub.question}</sub_question>"
    return _structured("worker", system, prompt, WorkerReport)


def synthesize(question: str, reports: list[tuple[SubQuestion, WorkerReport]]) -> str:
    blocks = []
    for sub, rep in reports:
        findings = "\n".join(f"- {f.claim} [{f.doc}]" for f in rep.findings)
        gaps = "\n".join(f"- {q}" for q in rep.open_questions) or "- none"
        blocks.append(f"<sub_question q=\"{sub.question}\">\n{findings}\nOpen:\n{gaps}\n</sub_question>")
    response = client.messages.create(
        model=settings.default_model,
        max_tokens=2048,
        system="""You write decision briefs for executives: a one-line recommendation,
then the key reasons and the main risks. Use only the findings given and cite
each fact with its [document] tag. Name what is still unknown.""",
        messages=[{"role": "user", "content": f"<question>{question}</question>\n\n" + "\n\n".join(blocks)}],
    )
    _track("synthesizer", response.usage)
    return "".join(b.text for b in response.content if b.type == "text")


def run(question: str) -> dict:
    USAGE.clear()
    the_plan = plan(question)
    for sq in the_plan.sub_questions:
        print(f"[planner] {sq.question}  ->  {sq.docs}")
    with ThreadPoolExecutor() as pool:  # independent work runs in parallel
        reports = list(pool.map(research, the_plan.sub_questions))
    brief = synthesize(question, list(zip(the_plan.sub_questions, reports)))
    return {"plan": the_plan, "reports": reports, "brief": brief, "usage": dict(USAGE)}


if __name__ == "__main__":
    result = run(" ".join(sys.argv[1:]) or DEFAULT_QUESTION)
    print("\n" + result["brief"])
    print("\n[usage per role]")
    for role, u in result["usage"].items():
        print(f"  {role:12} {u}")
