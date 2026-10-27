"""
Generic vs constrained tool (cert 2.3): same capability, different blast radius.

  fetch_url(url)      — accepts anything; a footgun for subagents.
  load_document(url)  — allow-listed hosts + document extensions only; anything
                        else is a structured error (2.2 shape) via ToolError.

The description of a tool is a suggestion; the code is the enforcement. That
needs no model to prove — see test_constrained_url.py:

    uv run pytest
"""

import json
from urllib.parse import urlparse

from anthropic import beta_tool
from anthropic.lib.tools import ToolError

ALLOWED_HOSTS = {"arxiv.org", "docs.python.org", "example.com"}
DOCUMENT_EXTS = (".pdf", ".md", ".txt", ".html", ".htm")


def _error(category: str, description: str) -> ToolError:
    return ToolError(json.dumps({"errorCategory": category, "isRetryable": False, "description": description}))


@beta_tool
def fetch_url(url: str) -> str:
    """Fetch the raw body at a URL and return it as text.

    Args:
        url: Any URL.
    """
    return json.dumps({"url": url, "text": "<raw body>"})


@beta_tool
def load_document(url: str) -> str:
    """Load a document (PDF, Markdown, plain text, HTML) from an allow-listed
    host. Returns a structured error for any URL that is not a document.

    Args:
        url: URL of the document, e.g. 'https://arxiv.org/abs/2401.12345.pdf'.
    """
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise _error("permission", f"Host {parsed.hostname!r} is not in the allow-list {sorted(ALLOWED_HOSTS)}.")
    if not parsed.path.lower().endswith(DOCUMENT_EXTS):
        raise _error("validation", f"Path {parsed.path!r} has no document extension {DOCUMENT_EXTS}.")
    return json.dumps({"url": url, "text": "<document body>"})
