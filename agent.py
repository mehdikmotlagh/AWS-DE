"""A minimal model-and-tools agent you can run from the command line."""

import os

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from tools import execute_tool

MAX_TURNS = 5
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Search the built-in data engineering notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic or keywords to find.",
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_date",
            "description": "Get today's date in the computer's local timezone.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a basic arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Numbers and arithmetic such as (12 + 3) * 4.",
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]


def run_agent(client: OpenAI, question: str) -> str:
    """Ask the model a question and run its requested tools until it answers."""
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "Answer clearly and concisely. Use the available tools when they "
                "can help. Base claims about the built-in notes on search results; "
                "say when those notes do not contain an answer."
            ),
        },
        {"role": "user", "content": question},
    ]

    for _ in range(MAX_TURNS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        assistant_message = response.choices[0].message
        if not assistant_message.tool_calls:
            if assistant_message.content is None:
                raise RuntimeError("The model returned neither a reply nor a tool call.")
            return assistant_message.content

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in assistant_message.tool_calls
                ],
            }
        )

        for call in assistant_message.tool_calls:
            print(f"\nTool call: {call.function.name}({call.function.arguments})")
            result = execute_tool(call.function.name, call.function.arguments)
            print(f"Tool result: {result}")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )

    raise RuntimeError(f"The agent reached its limit of {MAX_TURNS} model turns.")


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "Set OPENAI_API_KEY in your environment before running the agent."
        )

    question = input("Ask the agent a question: ").strip()
    if not question:
        raise SystemExit("Please enter a question.")

    answer = run_agent(OpenAI(), question)
    print(f"\nAnswer: {answer}")


if __name__ == "__main__":
    main()
