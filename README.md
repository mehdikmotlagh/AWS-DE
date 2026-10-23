# A Tiny Tool-Using AI Agent

A small command-line project for learning how an AI agent works. You give it a
question; a language model can choose from three local tools, see their results,
and decide what to do next:

- `search_notes` looks up a few built-in notes about data engineering.
- `get_today_date` returns the computer's local date.
- `calculate` evaluates basic arithmetic without executing Python code.

The agent uses the OpenAI Python SDK. The tools themselves are ordinary Python
functions, so you can read and test them without an API key.

## Run it

You need Python 3.14 and an OpenAI API key. Create the virtual environment
with `python3.14` so it uses the intended interpreter:

```bash
python3.14 -m venv .venv314
.venv314/bin/python -m pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
.venv314/bin/python agent.py
```

If `python3.14` is not found, install Python 3.14 first. Check the selected
version with `python3.14 --version`.

Enter a question such as:

```text
What is Apache Airflow, and how many minutes are in 3 hours?
```

The model is `gpt-4o-mini` by default. To use another model supported by your
account, set `OPENAI_MODEL` before starting the app.

## Follow the agent loop

1. `agent.py` sends your question and the tool descriptions to the model.
2. The model either replies directly or asks to call a tool.
3. `tools.py` checks the requested tool and its arguments, then runs the local
   Python function.
4. The agent sends the tool result back to the model. The model can answer or
   request another tool, up to five model turns.
5. The app prints the tool calls and their results so you can see the loop.

The model chooses **whether** and **when** to use tools; Python controls **which**
tools are available and **what** they are allowed to do. This example does not
let the model run arbitrary Python or access the network through a tool.

## Run the tests

The tool tests use only Python's standard library and do not make API calls:

```bash
.venv314/bin/python -m unittest discover -s tests -v
```

Try changing a note in `tools.py`, adding a question that uses it, or writing a
new tested tool. To make it available to the model, add its description to
`TOOLS` in `agent.py` and register its handler in `tools.py`.
