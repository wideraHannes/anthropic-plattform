"""
Two graders on the same outputs: a code grader and an LLM judge.

The code grader is cheap, deterministic and blind to meaning — it checks a
regex. The LLM judge reads a rubric, reasons, and gives a verdict. Watch where
they disagree: that's exactly where you need the judge (or a human).

The judge follows the develop-tests tips: a detailed rubric, an empirical
verdict (pass/fail, not prose), reasoning before the verdict (thinking on), and
a different model than the one that wrote the replies (`settings.judge_model`).
"""

import re

from pydantic import BaseModel, Field

from config import client, settings

QUESTION = "My refund for order O-77 hasn't arrived. When will I get my money?"

RUBRIC = """A good reply:
1. States that refunds take 5-7 business days after approval.
2. Does not promise a specific date or an amount beyond the order value.
3. Is polite and acknowledges the customer's frustration."""

CANDIDATES = {
    "good": "Sorry for the wait! Your refund for O-77 was approved yesterday; refunds "
    "take 5-7 business days to reach your account.",
    "keyword_but_wrong": "Refunds take 5-7 business days, but I've added a $20 bonus and "
    "guarantee it arrives tomorrow.",
    "right_but_no_keyword": "I'm sorry about this. Once approved, refunds usually show up "
    "within one to one and a half working weeks.",
}


class Verdict(BaseModel):
    reasoning: str = Field(description="Check each rubric point in one sentence.")
    passed: bool


def code_grader(reply: str) -> bool:
    return bool(re.search(r"5\s*[-–]\s*7 business days", reply))


def llm_judge(reply: str) -> Verdict:
    response = client.messages.parse(
        model=settings.judge_model,
        max_tokens=16000,
        thinking={"type": "adaptive"},  # reason before scoring
        output_format=Verdict,
        messages=[
            {
                "role": "user",
                "content": f"<rubric>\n{RUBRIC}\n</rubric>\n\n<question>{QUESTION}</question>\n\n"
                f"<reply>{reply}</reply>\n\nGrade the reply against every rubric point.",
            }
        ],
    )
    return response.parsed_output


if __name__ == "__main__":
    for name, reply in CANDIDATES.items():
        verdict = llm_judge(reply)
        print(f"\n[{name}]  code={code_grader(reply)}  judge={verdict.passed}")
        print(f"  judge reasoning: {verdict.reasoning}")
