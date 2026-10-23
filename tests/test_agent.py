import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from agent import run_agent


class RunAgentTests(unittest.TestCase):
    def test_sends_tool_result_back_before_returning_answer(self) -> None:
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="calculate",
                arguments='{"expression":"6 * 7"}',
            ),
        )
        tool_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=None, tool_calls=[tool_call])
                )
            ]
        )
        final_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="42", tool_calls=None)
                )
            ]
        )
        client = MagicMock()
        client.chat.completions.create.side_effect = [tool_response, final_response]

        with contextlib.redirect_stdout(io.StringIO()):
            answer = run_agent(client, "What is 6 times 7?")

        self.assertEqual(answer, "42")
        second_turn_messages = client.chat.completions.create.call_args_list[1].kwargs[
            "messages"
        ]
        self.assertEqual(
            second_turn_messages[-1],
            {"role": "tool", "tool_call_id": "call-1", "content": "42"},
        )


if __name__ == "__main__":
    unittest.main()
