"""
Prompt caching in two calls.

Call 1 writes the large, stable system prompt to the cache
(cache_creation_input_tokens > 0). Call 2 sends the identical prefix with a
different question and reads it back (cache_read_input_tokens > 0) — billed at
a fraction of the normal input price.

If both calls show 0 for cache tokens: the prefix is below the model's
minimum cacheable size, or something in the prefix changed between calls.
"""

from config import client, settings

# ~3k tokens of stable "knowledge base" — comfortably above every model's minimum.
POLICY = "\n".join(
    f"Policy §{i}: Orders in category {i % 7} may be returned within {14 + i % 3 * 7} days; "
    f"refunds over €{100 + i * 5} require manager approval and a verified customer ID."
    for i in range(1, 121)
)

SYSTEM = [
    {
        "type": "text",
        "text": f"You answer questions about the shop's return policy.\n\n<policy>\n{POLICY}\n</policy>",
        "cache_control": {"type": "ephemeral"},
    }
]


def ask(question: str) -> None:
    response = client.messages.create(
        model=settings.default_model,
        max_tokens=256,
        system=SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    u = response.usage
    print(f"\nQ: {question}")
    print(
        f"  input={u.input_tokens}  cache_write={u.cache_creation_input_tokens}  "
        f"cache_read={u.cache_read_input_tokens}  output={u.output_tokens}"
    )


if __name__ == "__main__":
    ask("How long can I return an item from category 3?")
    ask("Which refunds need manager approval?")
