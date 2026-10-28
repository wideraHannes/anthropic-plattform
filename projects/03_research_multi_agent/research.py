"""
Multi-agent research: orchestrator → parallel workers → gap review → synthesizer.

    uv run python research.py "Should Acme launch HeatFlow in Norway in 2027?"

Context engineering is the point of this project — each role sees only what it needs:
- planner:     the question + a one-line INDEX of the corpus (not the documents)
- workers:     one sub-question + only the documents assigned to it
- reviewer:    the lead again, with the workers' open questions + the INDEX → follow-ups
- synthesizer: the question + the workers' compressed, quoted findings
"""

import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel, Field

from config import client, settings

CORPUS_DIR = Path(__file__).parent / "corpus"
CORPUS = {p.stem: p.read_text() for p in sorted(CORPUS_DIR.glob("*.md"))}
# One line per document: what the planner and reviewer see instead of the full text.
CORPUS_INDEX = "\n".join(
    f"- {name}: {next((l for l in text.splitlines() if l.startswith('Summary:')), '').removeprefix('Summary:').strip()}"
    for name, text in CORPUS.items()
)

DEFAULT_QUESTION = "Should Acme enter the Nordic heat pump market in 2027, and if so, which country first?"


class SubQuestion(BaseModel):
    question: str
    docs: list[str] = Field(min_length=1, description="Document names from the index to read.")


class Plan(BaseModel):
    sub_questions: list[SubQuestion] = Field(min_length=3, max_length=5)


class Review(BaseModel):
    follow_ups: list[SubQuestion] = Field(
        default_factory=list,
        max_length=3,
        description="Follow-up sub-questions for open questions the corpus can still answer. Empty if none.",
    )


class Finding(BaseModel):
    claim: str
    doc: str = Field(description="Name of the document the quote is from.")
    quote: str = Field(description="Exact sentence copied verbatim from that document.")


class WorkerReport(BaseModel):
    findings: list[Finding] = Field(min_length=1)
    open_questions: list[str] = Field(default_factory=list, description="What the documents could not answer.")


USAGE: defaultdict[str, Counter] = defaultdict(Counter)  # role -> calls, input_tokens, output_tokens


def call_structured[T: BaseModel](role: str, system: str, prompt: str, schema: type[T]) -> T:
    response = client.messages.parse(
        model=settings.default_model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_format=schema,
    )
    USAGE[role].update(calls=1, input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)
    return response.parsed_output


def plan(question: str) -> Plan:
    system = """You are the lead researcher. You split a business question into 3-5
independent sub-questions that together cover it fully (market, product fit,
competition, regulation, customers, money — whatever applies), and assign each
the documents a researcher should read. You do not answer the question yourself."""
    prompt = f"<question>{question}</question>\n\n<corpus_index>\n{CORPUS_INDEX}\n</corpus_index>"
    result = call_structured("planner", system, prompt, Plan)
    result.sub_questions = drop_unknown_docs(result.sub_questions)
    return result


def drop_unknown_docs(sub_questions: list[SubQuestion]) -> list[SubQuestion]:
    """Never trust model-chosen references blindly: keep only docs that exist."""
    for sq in sub_questions:
        sq.docs = [d for d in sq.docs if d in CORPUS]
    return [sq for sq in sub_questions if sq.docs]


def review(question: str, reports: list[WorkerReport]) -> list[SubQuestion]:
    open_questions = "\n".join(f"- {q}" for r in reports for q in r.open_questions) or "- none"
    system = """You are the lead researcher reviewing your researchers' gaps. For open
questions that another document in the index could answer, write a follow-up
sub-question and assign those documents. Ignore gaps the corpus cannot close."""
    prompt = (
        f"<question>{question}</question>\n\n<open_questions>\n{open_questions}\n</open_questions>\n\n"
        f"<corpus_index>\n{CORPUS_INDEX}\n</corpus_index>"
    )
    return drop_unknown_docs(call_structured("reviewer", system, prompt, Review).follow_ups)


def research(sub: SubQuestion) -> WorkerReport:
    system = """You are a researcher. Answer ONE sub-question using ONLY the documents
provided. Every finding must carry an exact quote copied from its document.
If the documents do not answer something, list it under open_questions."""
    docs = "\n\n".join(f'<document name="{d}">\n{CORPUS[d]}\n</document>' for d in sub.docs)
    prompt = f"{docs}\n\n<sub_question>{sub.question}</sub_question>"
    return call_structured("worker", system, prompt, WorkerReport)


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
    USAGE["synthesizer"].update(calls=1, input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)
    return "".join(b.text for b in response.content if b.type == "text")


def run(question: str) -> dict:
    USAGE.clear()
    the_plan = plan(question)
    for sq in the_plan.sub_questions:
        print(f"[planner] {sq.question}  ->  {sq.docs}")
    subs = the_plan.sub_questions
    with ThreadPoolExecutor() as pool:  # independent work runs in parallel
        reports = list(pool.map(research, subs))
        # One gap-review round: follow-ups only where the corpus can still help.
        follow_ups = review(question, reports)
        for sq in follow_ups:
            print(f"[reviewer] {sq.question}  ->  {sq.docs}")
        reports += list(pool.map(research, follow_ups))
    subs = subs + follow_ups
    brief = synthesize(question, list(zip(subs, reports)))
    return {"plan": the_plan, "follow_ups": follow_ups, "reports": reports, "brief": brief, "usage": {role: dict(c) for role, c in USAGE.items()}}


if __name__ == "__main__":
    result = run(" ".join(sys.argv[1:]) or DEFAULT_QUESTION)
    print("\n" + result["brief"])
    print("\n[usage per role]")
    for role, u in result["usage"].items():
        print(f"  {role:12} {u}")
