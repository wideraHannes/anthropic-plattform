"""
Minimal Agent SDK run: built-in tools, auto-approved edits, streamed events.

    uv run python simple_claude_code.py

Other prompts to try:
    "Add docstrings to all functions in utils.py"
    "Add type hints to all functions in utils.py"
"""

import asyncio

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, ToolUseBlock, query

PROMPT = "Add a fibonacci function to utils.py test-driven with pytest: write the tests first, run them, fix any failures."


async def main() -> None:
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Write", "Glob", "Bash"],  # auto-approved tools
        permission_mode="acceptEdits",  # auto-approve file edits
        system_prompt="You are a senior Python developer. Follow PEP 8.",
    )
    async for message in query(prompt=PROMPT, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"Tool: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
