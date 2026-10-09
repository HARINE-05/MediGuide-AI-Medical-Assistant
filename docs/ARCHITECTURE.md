# Architecture

```mermaid
flowchart TD
    U[Streamlit input] --> G[Guardrail Agent]
    G -->|Emergency| E[Escalation interrupt]
    E --> A[Human acknowledgement]
    A --> Z[End query]
    G -->|Restricted| B[Scope response]
    G -->|Information| I[Info Agent]
    G -->|Interaction| X[Interaction Agent]
    I --> R[Research Agent]
    X --> R
    R --> O[Evidence Response Agent]
    O --> C[Cited answer]
```

```mermaid
flowchart TD
    A[Info / Interaction] --> M[MCP client]
    M --> S[Custom stdio server]
    S --> D[Curated medicine data]
    A --> K[TF-IDF RAG]
    K --> J[Cited knowledge chunks]
    R[Gemini ReAct researcher] --> T[Five LangChain tool wrappers]
    T --> M
    T --> K
    T --> W[Tavily official-source search]
```

The ReAct loop performs model → tool call → observation → model, with at most four model turns. The outer LangGraph runs with a recursion limit of 15 in the UI. MCP transport timeout is 35 seconds; Gemini has a per-call timeout of 30 seconds and no retries; Tavily timeout is 20 seconds. No external calls are required after package installation in Offline demo.
