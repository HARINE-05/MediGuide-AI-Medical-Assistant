# Validation record

Environment: Python 3.12, Linux. Direct dependency versions are recorded in requirements-tested.txt.

## Executed checks

- Command: `python -m pytest -q MediGuide/tests` from the parent directory (the included pytest.ini also supports running inside the project).
- Result: **24 passed in 5.18 seconds**.
- The actual MCP stdio server was started and all three tools were called through ClientSession.
- LangGraph emergency interrupt, immediate guidance payload, acknowledgement and terminal graph state passed.
- Unknown medicine pairs and duplicate ingredient behavior passed.
- Relevant retrieval and no-match retrieval passed.
- The ReAct loop was tested with a deterministic fake model: actual LangChain retrieval tools ran, observations returned and the loop stopped at four turns.
- Missing Gemini/Tavily keys produced visible fallback states.
- Streamlit AppTest exercised medicine answers, result clearing, emergency display, disabled submission while interrupted, and acknowledgement.
- An initial UI test found stale button state after escalation; the app now reruns after committing the result. The complete suite passed after this fix.

## Guardrail evaluation

`python evaluate.py` ran 20 hand-authored illustrative cases:

| Metric | Result |
|---|---:|
| Accuracy | 80% |
| Emergency recall | 83.33% |
| Emergency precision | 83.33% |
| True positives | 10 |
| True negatives | 6 |
| False positives | 2 |
| False negatives | 2 |

The full queries and labels are in guardrail_evaluation.json. Negated/academic mentions were overflagged. Two indirect emergency descriptions were missed. This small developer-authored set is not independent evidence of medical safety.

## Not verified

- Successful Gemini or Tavily requests with real API keys; no credentials were supplied.
- Windows/macOS launchers on those operating systems; the Python app and tests ran on Linux.
- Exhaustive clinical correctness, all medicine interactions, multilingual emergencies, production privacy/security, or regulatory suitability.
- Visual browser screenshot review; UI functionality was checked with Streamlit's testing API.

The ZIP contains no virtual environment, API keys, dependency binaries, or provider response claims. Dependencies install on first launch. This is an educational source project, not a standalone Windows executable.
