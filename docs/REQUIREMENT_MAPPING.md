# Requirement-to-code mapping

| Supplied requirement | Implementation | Demonstration / limitation |
|---|---|---|
| Custom MCP server, 3+ tools | mcp_server.py; src/mcp_client.py | Actual stdio ClientSession calls, three named tools |
| At least 2 additional LangChain tools | src/research.py: search_knowledge, tavily_health_search | @tool definitions used by live researcher |
| RAG with citations | src/retrieval.py; data/knowledge.json; src/workflow.py: render | Seven chunks, TF-IDF, cosine retrieval, extractive generation, URL citations |
| Tavily web search | src/research.py: web_search | Current advisory queries; requires Tavily key/network |
| ReAct with iteration limit | src/research.py: run_react | Four model turns, two tool executions per turn; live mode only |
| LangGraph, 3+ agents | src/workflow.py | Guardrail, Info, Interaction, Research, Evidence Response |
| Shared state / conditional routing | State TypedDict; add_conditional_edges | Inspect workflow audit and route |
| drug_info | MCP tool | Three medicine records |
| check_interaction | MCP tool | One known pair and duplicate-ingredient check; unknown never means safe |
| find_generic | MCP tool | Exact Tylenol Regular Strength US label example; no price guarantee |
| WHO / leaflet / emergency knowledge | data/knowledge.json | Original short source-linked summaries, not full copyrighted documents |
| Guardrail before every query | Guardrail Agent | Screens structured fields as well as question |
| Emergency human-in-the-loop interrupt | escalation node; app.py | Immediate guidance, interrupt, acknowledgement → END; no actual clinician handoff |
| No diagnosis or prescription | src/safety.py and constrained response rendering | Rule-based limits are not clinical validation |
| Disclaimer on every answer | src/safety.py: DISCLAIMER | Ordinary, restricted, error and emergency paths |
| Optional red-flag evaluation | evaluate.py | Includes false positives and false negatives |
| Plain-language sourced output | render and app.py | Curated facts and extractive passages; unrestricted Gemini medical prose not rendered |

Only the two supplied pages were available. The separate “Capstone Tasks and Evaluation Rubric” referenced in the introduction was not attached; compliance with any unseen requirements cannot be verified.
