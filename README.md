# MediGuide — Medicine & Symptom Information Assistant

Complete local Python project for **Agentic Systems Course, Task 5**, based on the two supplied requirement images. Educational capstone prototype, not a clinical service.

## Start on Windows

1. Install **Python 3.11 or 3.12** from https://www.python.org/downloads/ (select “Add Python to PATH”). Python 3.12 is the tested environment.
2. Extract this ZIP completely. Open the extracted `MediGuide` folder.
3. Double-click **start_windows.bat**. First launch installs packages and needs internet access.
4. Open **http://localhost:8501** if the browser does not open automatically.
5. Start with **Offline demo**. No keys are required for this mode.

Do not run inside the ZIP viewer. Keep the terminal open while using the app. Press Ctrl+C to stop it.

Manual commands, from this folder:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-tested.txt
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

macOS/Linux: run `bash start_mac_linux.sh` with Python 3.11/3.12 installed.

## Connect Gemini and Tavily

Use the sidebar password fields, or copy `.env.example` to `.env` and fill in:

```dotenv
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
GEMINI_MODEL=your_available_text_model_id
```

- Gemini key/account: https://aistudio.google.com/apikey
- Available model IDs: https://ai.google.dev/gemini-api/docs/models
- Tavily key/account: https://app.tavily.com/
- Choose **Gemini + Tavily**, set an available model ID and tick the external-query checkbox.
- Ask `What is paracetamol used for?`, then inspect **Workflow and tool evidence** for actual ReAct tool calls.
- Ask `Latest medicine recall notices in India` to exercise Tavily. Results are restricted to the configured official health domains; coverage is not exhaustive or India-specific. Open the original pages and verify dates/jurisdiction.

The default model is `gemini-2.5-flash` for existing projects; availability depends on your account. Change it if Google reports it unavailable. Free access and quotas are controlled by providers and are not guaranteed. Do not share your keys, upload `.env`, or enter real patient identifiers. Live mode sends query text and selected evidence to Google and search queries to Tavily. No provider calls run in Offline demo.

## Included capabilities

- Streamlit UI, source panels, answer download and tool audit.
- Genuine **MCP stdio server** with `drug_info`, `check_interaction`, `find_generic`; the app calls it through `ClientSession`, not direct function substitution.
- Two additional **LangChain tools**: `search_knowledge` and `tavily_health_search`.
- TF-IDF retrieval over seven source-linked, short educational summaries. Evidence-based response construction preserves citations. No embedding key or model download needed.
- Gemini tool-calling **ReAct loop**, up to four model turns and two tool executions per turn, with observations returned as `ToolMessage`s.
- LangGraph shared state and conditional routing: Guardrail, Info, Interaction, Research and Evidence Response agents; a separate escalation node calls `interrupt()`.
- Emergency guidance appears immediately in the interrupt payload. Acknowledgement resumes only to END; it never unlocks medical advice. This is a UI human-in-the-loop demonstration, not a staffed clinical service.
- Diagnosis, prescription and dosing requests are declined by a conservative English rule layer.
- A disclaimer on every answer; missing evidence, missing keys and provider failures are explicit.
- Tests, reproducible screening evaluation, report, architecture and viva/demo notes.

## Demonstration queries

| Feature | Input | Expected behavior |
|---|---|---|
| Medicine information | What is paracetamol used for and what are its side effects? | MCP record, RAG passages and source links |
| Known interaction | Exact medicine names: `ibuprofen, warfarin` | Limited-dataset bleeding-risk warning |
| Unknown interaction | Exact medicine names: `ibuprofen, unknown tablet` | Unknown; no safety assurance |
| Missing medicine name | Can I take ibuprofen with my blood pressure medication? | Request exact medicine names |
| Generic example | Exact brand variant: `Tylenol Regular Strength` | US label ingredient, pharmacist confirmation required |
| Emergency interrupt | I have chest pain and my left arm feels numb. | Immediate guidance and interrupt; no normal research |
| Scope boundary | Diagnose my headache | Decline diagnosis |
| Live search | Latest medicine recall notices | Tavily results or an explicit availability error |

## Test and evaluate

From the project folder after installation:

```bat
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe evaluate.py
```

On macOS/Linux replace `.venv\Scripts\python.exe` with `.venv/bin/python`.
See `docs/VALIDATION.md` for what was actually tested. Live calls require your own keys; no successful provider request is claimed in the delivered validation.

## Project layout

```text
MediGuide/
  app.py                   Streamlit interface
  mcp_server.py            Three-tool custom MCP server
  src/safety.py            Red flags and scope screening
  src/catalog.py           Small medicine and interaction catalogue
  src/mcp_client.py        Real stdio MCP client
  src/retrieval.py         TF-IDF index and ranked retrieval
  src/research.py          Gemini ReAct, LangChain tools, Tavily
  src/workflow.py          LangGraph routing, interrupts and response
  data/                    Medicine records and cited knowledge
  tests/                   Integration, safety and UI tests
  docs/                    Report, mapping, architecture and evaluation
  evaluate.py              Reproducible guardrail evaluation
  requirements-tested.txt  Tested direct dependency versions
  requirements.txt         Compatible dependency ranges
  .env.example             Key template, no real credentials
  start_windows.bat        Windows setup and launcher
  start_mac_linux.sh       macOS/Linux setup and launcher
```

## Troubleshooting

- **`streamlit` not recognized:** use `python -m streamlit` with the virtual-environment executable as shown above.
- **`No module named ...`:** install requirements using that same executable. Avoid mixing multiple Python installations.
- **Windows Store opens for Python:** install Python from python.org and use `py -3`.
- **Gemini 404/model unavailable:** copy an available text-model ID from your AI Studio account into the model field. Do not append `models/` unless your provider requires it.
- **401/403:** check the relevant key, account access and API restrictions. **429:** quota/rate limit; wait or change your provider plan. Do not bypass limits.
- **MCP unavailable:** run `python -m pytest tests/test_project.py -q` from this folder using the same virtual environment. The server is auto-started by the app; no second terminal is required.
- **Blank browser/port in use:** reopen http://localhost:8501 or add `--server.port 8502` to the launch command.
- **Emergency button disabled normal submission:** acknowledge to close the query, or clear session results. Emergency help must not wait for this UI.

## Important limitations

Three generic medicine records, one brand example and one known interaction pair are deliberately limited. Generic lookup does not establish therapeutic equivalence or price savings. RAG summaries are not complete medicine leaflets. The prototype does not diagnose symptoms. Rules can miss emergencies, misunderstand negation, and do not support multilingual triage. The included evaluation deliberately exposes false positives and missed paraphrases. Do not deploy for patient care.

Live Gemini gathers evidence with tools; its unrestricted final prose is deliberately not displayed as medical advice. The response agent renders curated MCP fields, retrieved passages and official-source links. This constrained approach demonstrates orchestration while reducing unsupported output; it does not guarantee clinical safety. ReAct is live-mode only—offline mode is explicitly a deterministic demonstration.

No personal records are written to disk by the application. Results and the in-memory LangGraph checkpoint live in the session; downloaded answers persist wherever the user saves them. Provider retention policies apply to live mode. The local launcher binds to 127.0.0.1, not a public interface.
