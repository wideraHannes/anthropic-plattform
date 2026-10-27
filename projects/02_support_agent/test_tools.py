"""
Deterministic tests for the policy gates in tools.py — no API calls, no tokens.

    uv run pytest

The eval measures the agent; these tests prove the guardrails hold no matter
what the model says. If a gate test fails, no prompt can save you.
"""

import json

import pytest
from anthropic.lib.tools import ToolError

from tools import escalate_to_human, lookup_order, process_refund, reset_session, session, verify_customer


@pytest.fixture(autouse=True)
def fresh_session():
    reset_session()


def error_category(exc: pytest.ExceptionInfo[ToolError]) -> str:
    return json.loads(exc.value.content)["errorCategory"]


def verify(email="alice@example.com", zip_code="10115"):
    verify_customer.call({"email": email, "zip_code": zip_code})


def refund(order_id="O-77", amount=49.99):
    return process_refund.call({"order_id": order_id, "amount": amount, "reason": "damaged"})


def test_refund_happy_path():
    verify()
    assert json.loads(refund())["status"] == "refunded"
    assert session.refunds == {"O-77": 49.99}


@pytest.mark.parametrize(
    ("setup", "order_id", "amount", "category"),
    [
        (lambda: None, "O-77", 49.99, "permission"),  # unverified
        (lambda: verify("bob@example.com", "20095"), "O-77", 49.99, "permission"),  # not the owner
        (verify, "O-77", 60.00, "validation"),  # more than the order amount
        (verify, "O-78", 649.00, "business"),  # above the auto-refund limit
    ],
    ids=["unverified", "not_owner", "over_order_amount", "over_auto_limit"],
)
def test_refund_gates_block(setup, order_id, amount, category):
    setup()
    with pytest.raises(ToolError) as exc:
        refund(order_id, amount)
    assert error_category(exc) == category
    assert session.refunds == {}


def test_refund_only_once():
    verify()
    refund()
    with pytest.raises(ToolError) as exc:
        refund()
    assert error_category(exc) == "business"


def test_wrong_zip_does_not_verify():
    with pytest.raises(ToolError):
        verify(zip_code="99999")
    assert session.verified_customer_id is None


def test_lookup_foreign_order_is_denied():
    verify()
    with pytest.raises(ToolError) as exc:
        lookup_order.call({"order_id": "O-79"})
    assert error_category(exc) == "permission"


def test_incomplete_handoff_is_rejected():
    args = {"customer_id": "C-1001", "conversation_summary": "too short", "root_cause": "TV cracked",
            "refund_amount": 649.0, "recommended_action": "refund"}
    with pytest.raises(ValueError):  # summary below min_length — the runner returns it as is_error
        escalate_to_human.call(args)
    assert session.handoffs == []
