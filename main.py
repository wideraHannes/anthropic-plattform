from config import client, settings


def main():
    response = client.messages.create(
        model=settings.default_model,
        max_tokens=1024,
        messages=[{"role": "user", "content": "What is the capital of France?"}],
    )
    print(f"stop_reason: {response.stop_reason}")
    final_text = next(block for block in response.content if block.type == "text")
    print(final_text.text)


if __name__ == "__main__":
    main()
