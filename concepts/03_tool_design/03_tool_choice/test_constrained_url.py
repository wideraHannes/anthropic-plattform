"""The constraint lives in code, so a test proves it — no model, no tokens."""

import json

import pytest
from anthropic.lib.tools import ToolError

from constrained_url import fetch_url, load_document

DOCUMENT = "https://arxiv.org/paper/2401.12345.pdf"
ADMIN_ENDPOINT = "https://api.malicious.example/admin/keys"
NON_DOCUMENT = "https://docs.python.org/3/api/run"


def test_generic_tool_fetches_anything():
    assert json.loads(fetch_url.call({"url": ADMIN_ENDPOINT}))["url"] == ADMIN_ENDPOINT


def test_constrained_tool_loads_documents():
    assert json.loads(load_document.call({"url": DOCUMENT}))["url"] == DOCUMENT


@pytest.mark.parametrize(("url", "category"), [(ADMIN_ENDPOINT, "permission"), (NON_DOCUMENT, "validation")])
def test_constrained_tool_rejects(url, category):
    with pytest.raises(ToolError) as exc:
        load_document.call({"url": url})
    assert json.loads(exc.value.content)["errorCategory"] == category
