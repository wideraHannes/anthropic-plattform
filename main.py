import anthropic


def main():
    client = anthropic.Anthropic(
        base_url="https://router.eu.requesty.ai",
        api_key="REQUEST_API_KEY",
    )
    response = client.messages.create(
        model="vertex/claude-sonnet-4-6@europe-west1",
        max_tokens=1024,
        messages=[{"role": "user", "content": "What is the capital of France?"}],
    )
    print(f"stop_reason: {response.stop_reason}")
    final_text = next(block for block in response.content if block.type == "text")
    print(final_text.text)


if __name__ == "__main__":
    main()
