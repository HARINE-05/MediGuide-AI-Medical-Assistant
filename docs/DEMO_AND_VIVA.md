# Five-minute demonstration

1. **Introduction:** “My project is MediGuide, a medicine information assistant. It gives educational information with sources. It does not diagnose or prescribe.”
2. **Medicine information:** Ask about paracetamol. “The Info Agent calls my custom MCP server. It also retrieves relevant information from the local knowledge base.” Open the source and workflow panels.
3. **Interactions:** Enter ibuprofen and warfarin in the exact-name field. “The tool checks each pair. If the pair is unknown, it does not say that the medicines are safe.” Demonstrate an unknown name.
4. **Generic example:** Enter Tylenol Regular Strength. “This is an ingredient lookup from a specific product label. A pharmacist must confirm the exact product before substitution.”
5. **Emergency:** Enter the chest-pain example. “The Guardrail Agent runs first. LangGraph pauses here with an interrupt. Guidance is already visible. Acknowledgement closes the query.”
6. **Live mode:** Enter your keys privately, select a valid model and allow external queries. Ask for current medicine recalls. Open the audit. “Gemini can choose tools in a ReAct loop. The loop has a fixed limit. Tavily searches official health sites.” If the API fails, show its honest error state; do not claim the live call succeeded.

# Viva questions

**What is MCP?** A standard way for an AI application to discover and call tools. Here, a separate server exposes three medicine tools.

**What is RAG?** Retrieval-Augmented Generation. We first retrieve relevant passages, then use them to construct an answer with sources. This project uses constrained extractive response construction.

**Why TF-IDF?** It is simple, local and inexpensive. It works for this small text collection without an embedding API. It is weaker for synonyms and paraphrases.

**What is LangGraph?** A library that runs a stateful workflow as connected nodes. Our nodes share state and take different paths depending on the query.

**What is ReAct?** A loop where the model chooses an action, calls a tool, observes its result and decides the next step. This project permits four model turns.

**What are the two extra LangChain tools?** search_knowledge and tavily_health_search. They are separate from the three MCP medicine tools.

**Why use Tavily?** The local knowledge base cannot answer what changed today. Tavily supplies current-source search links, but results still need date and jurisdiction checks.

**What does the interrupt do?** It saves workflow state and pauses execution. Guidance appears before the pause is acknowledged. Resuming ends the query.

**Does a human doctor review it?** No. The project demonstrates a human acknowledgement step. There is no staffed clinical service.

**Can the system diagnose disease?** No. It is an informational prototype. It declines diagnosis, prescribing and dosing requests.

**What happens if a key is wrong?** The live research status reports a failure. The app only shows evidence already available and does not pretend the API worked.

**Does a missing interaction mean safe?** No. Our dataset is incomplete, so missing pairs are explicitly unknown.

**How is it tested?** The project includes real MCP transport tests, graph/interrupt tests, a bounded ReAct test with a fake model, and Streamlit UI tests. Live provider requests require separately configured keys.

**Is the red-flag accuracy clinically meaningful?** No. It is a small hand-written illustration and includes missed cases and false alarms. See the evaluation JSON.

**What would you improve next?** Larger reviewed drug data, better retrieval, independent safety evaluation, multilingual support and a real staffed escalation process.
