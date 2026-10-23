"""Small local tools the agent is allowed to use."""

import ast
import json
import operator
from datetime import date
from typing import Callable

NOTES = {
    "Apache Airflow": (
        "Apache Airflow is an open-source platform for authoring, scheduling, "
        "and monitoring workflows as directed acyclic graphs (DAGs)."
    ),
    "Apache Spark": (
        "Apache Spark is an engine for large-scale data processing. It supports "
        "batch and streaming workloads."
    ),
    "AWS Glue": (
        "AWS Glue is a serverless data integration service. It can discover, "
        "prepare, and move data for analytics."
    ),
}

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[int | float, int | float], int | float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[int | float], int | float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_arithmetic(node: ast.expr) -> int | float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_arithmetic(node.left)
        right = _evaluate_arithmetic(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent must be between -100 and 100.")
        result = _BINARY_OPERATORS[type(node.op)](left, right)
        if abs(result) > 1_000_000_000_000:
            raise ValueError("The result is too large.")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_arithmetic(node.operand))
    raise ValueError("Use numbers and basic arithmetic operators only.")


def _calculate(arguments: dict[str, object]) -> str:
    expression = arguments.get("expression")
    if not isinstance(expression, str):
        raise ValueError("'expression' must be a string.")
    try:
        syntax = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("The expression is not valid arithmetic.") from error
    return str(_evaluate_arithmetic(syntax.body))


def _search_notes(arguments: dict[str, object]) -> str:
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("'query' must be a non-empty string.")

    terms = {term.strip(".,?!:;()[]{}").casefold() for term in query.split()}
    matches = [
        f"{title}: {note}"
        for title, note in NOTES.items()
        if terms.intersection(
            word.strip(".,?!:;()[]{}").casefold()
            for word in f"{title} {note}".split()
        )
    ]
    return "\n".join(matches) if matches else "No matching notes were found."


def _get_today_date(arguments: dict[str, object]) -> str:
    if arguments:
        raise ValueError("This tool takes no arguments.")
    return date.today().isoformat()


_HANDLERS: dict[str, Callable[[dict[str, object]], str]] = {
    "calculate": _calculate,
    "search_notes": _search_notes,
    "get_today_date": _get_today_date,
}


def execute_tool(name: str, arguments_json: str) -> str:
    """Validate and run a tool requested by the model."""
    handler = _HANDLERS.get(name)
    if handler is None:
        raise ValueError(f"Unknown tool: {name}")

    arguments = json.loads(arguments_json)
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object.")
    return handler(arguments)
