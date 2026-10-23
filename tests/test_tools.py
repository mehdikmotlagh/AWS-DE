import json
import unittest
from datetime import date

from tools import execute_tool


class ExecuteToolTests(unittest.TestCase):
    def test_search_notes_finds_matching_topic(self) -> None:
        result = execute_tool("search_notes", json.dumps({"query": "What is AWS Glue?"}))
        self.assertIn("AWS Glue is a serverless data integration service", result)

    def test_search_notes_reports_no_match(self) -> None:
        result = execute_tool("search_notes", json.dumps({"query": "unlisted topic"}))
        self.assertEqual(result, "No matching notes were found.")

    def test_calculate_evaluates_arithmetic(self) -> None:
        result = execute_tool("calculate", json.dumps({"expression": "(12 + 3) * 4"}))
        self.assertEqual(result, "60")

    def test_calculate_rejects_code(self) -> None:
        with self.assertRaisesRegex(ValueError, "basic arithmetic"):
            execute_tool(
                "calculate",
                json.dumps({"expression": "__import__('os').system('echo unsafe')"}),
            )

    def test_calculate_limits_large_exponents(self) -> None:
        with self.assertRaisesRegex(ValueError, "Exponent"):
            execute_tool("calculate", json.dumps({"expression": "2 ** 101"}))

    def test_get_today_date_returns_iso_date(self) -> None:
        result = execute_tool("get_today_date", "{}")
        self.assertEqual(date.fromisoformat(result).isoformat(), result)

    def test_rejects_unknown_tool(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown tool"):
            execute_tool("not_a_tool", "{}")

    def test_rejects_non_object_arguments(self) -> None:
        with self.assertRaisesRegex(ValueError, "JSON object"):
            execute_tool("search_notes", "[]")


if __name__ == "__main__":
    unittest.main()
