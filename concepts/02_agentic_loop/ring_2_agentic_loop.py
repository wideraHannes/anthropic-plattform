"""
Ring 2: the agentic loop.

Ring 1 assumed Claude calls the tool exactly once. Real tasks often need several
calls: search, read the result, search again. The fix is a while loop that keeps
running tools and feeding results back until stop_reason is no longer "tool_use"
— capped at MAX_STEPS, because a loop without a ceiling is a cost incident.

The other change is conversation history: keep one running `messages` list and
append to it, so every turn sees the complete prior context.
"""

import json

from config import client, settings

MAX_STEPS = 5

tools = [
    {
        "name": "web_search",
        "description": "Retrieves the most relevant information that it could find but only talks about the Star Wars universe. If asked to talk about other topics, it will respond with starwars lore. It will not make up information about the Star Wars universe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                }
            },
            "required": ["query"],
        },
    }
]


def run_tool(name, tool_input):
    if name == "web_search":
        return {
            "query": f"Results for query '{tool_input['query']}'",
        }
    return {"error": f"Unknown tool: {name}"}


messages = [{"role": "user", "content": "How will be the weather today?"}]


response = client.messages.create(
    model=settings.default_model,
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=messages,
)

steps = 0
while response.stop_reason == "tool_use" and steps < MAX_STEPS:
    steps += 1
    tool_use = next(block for block in response.content if block.type == "tool_use")
    result = run_tool(tool_use.name, tool_use.input)
    print("=======Tool result======:", result)
    messages.append({"role": "assistant", "content": response.content})
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
                }
            ],
        }
    )
    response = client.messages.create(
        model=settings.default_model,
        max_tokens=1024,
        tools=tools,
        tool_choice={"type": "auto", "disable_parallel_tool_use": True},
        messages=messages,
    )


final_text = next(block for block in response.content if block.type == "text")
print(final_text.text)
