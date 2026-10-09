from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from src.safety import screen, DISCLAIMER, EMERGENCY
from src.catalog import mentioned
from src.mcp_client import call
from src.retrieval import retrieve
from src.research import run_react, web_search

class State(TypedDict, total=False):
    query: str
    route: str
    medicines: list[str]
    brand: str
    documents: list[dict]
    facts: list[dict]
    trace: list[str]
    research: dict
    web: dict
    answer: str
    warnings: list[str]
    mode: str

def render(state):
    lines = []
    for item in state.get('facts', []):
        result = item['result']
        if item['tool'] == 'drug_info' and result.get('medicine'):
            lines.append('### ' + result['medicine'].title())
            for key, label in [('uses', 'Uses'), ('side_effects', 'Possible side effects'), ('warnings', 'Warnings')]:
                lines.append(f"**{label}:** {result[key]}")
            lines.append(f"[Medicine source]({result['source']})")
        elif item['tool'] == 'find_generic' and result.get('generic'):
            lines.append(f"**Ingredient example:** {result['generic']}. {result['message']}\n\n[Product label]({result['source']})")
        elif item['tool'] == 'check_interaction':
            for pair in result.get('pairs', []):
                lines.append(f"**{' + '.join(pair['medicines'])} — {pair['status'].upper()}:** {pair['message']}")
                if pair.get('source'):
                    lines.append(f"[Interaction source]({pair['source']})")
            lines.append(result['message'])
        else:
            lines.append(result.get('message', 'No supported information found.'))
    docs = state.get('documents', [])
    if docs:
        lines.append('### Retrieved educational information')
        for doc in docs:
            lines.append(f"{doc['text']} [{doc['id']}]({doc['url']})")
    elif not lines:
        lines.append('I do not have sufficient relevant evidence in this small knowledge base. Ask about paracetamol, ibuprofen, warfarin, medication safety, or an exact brand variant. For personal symptoms, consult a healthcare professional.')
    web = state.get('web', {})
    if web.get('status') == 'searched':
        lines.append('### Current-source search')
        lines.append('Search results are reading links, not a confirmed recall or outbreak assessment. Check dates and jurisdiction on each page.')
        for item in web.get('results', []):
            # Avoid rendering untrusted titles as Markdown.
            lines.append(f"- [Official source]({item['url']})")
        if not web.get('results'):
            lines.append('No matching official results returned. This does not establish the absence of a recall or advisory.')
    for warning in state.get('warnings', []):
        lines.append('**Notice:** ' + warning)
    lines.append('---\n' + DISCLAIMER)
    return '\n\n'.join(lines)

def build_graph(mode='Offline demo', gemini_key='', tavily_key='', model_name='gemini-2.5-flash'):
    def guardrail(state):
        # Structured form inputs are screened too; no route bypass.
        q = ' '.join([state['query'], state.get('brand', ''), *state.get('medicines', [])])
        route = screen(q)
        if route == 'info' and state.get('medicines'):
            route = 'interaction'
        return {'route': route, 'trace': ['Guardrail Agent'], 'warnings': [], 'facts': [], 'documents': [], 'mode': mode}

    def escalation(state):
        # Guidance is in the interrupt payload and appears BEFORE acknowledgement.
        interrupt({'message': EMERGENCY + '\n\n' + DISCLAIMER,
                   'sources': ['https://112.gov.in/', 'https://www.nhs.uk/conditions/heart-attack/'],
                   'action': 'Acknowledge and close this query; normal medicine flow will not resume.'})
        return {'answer': EMERGENCY + '\n\n' + DISCLAIMER,
                'trace': state['trace'] + ['Escalation Node', 'User acknowledgement → END']}

    def restricted(state):
        return {'answer': 'I cannot diagnose a condition, prescribe treatment, recommend a dose or tell you to change medicines. A doctor or pharmacist can review your personal situation. You can ask for general uses, side effects or source information.\n\n' + DISCLAIMER,
                'trace': state['trace'] + ['Scope boundary → END']}

    def collect(state, interaction=False):
        q = state['query']
        requests = []
        if interaction:
            # Unknown medicine names must be entered in the exact-names form.
            names = state.get('medicines') or mentioned(q)
            requests.append(('check_interaction', {'medicines': names}))
        else:
            requests.extend(('drug_info', {'medicine': n}) for n in mentioned(q))
            if state.get('brand') or any(w in q.casefold() for w in ['generic', 'brand', 'cheaper', 'tylenol']):
                brand = state.get('brand') or ('Tylenol Regular Strength' if 'tylenol regular strength' in q.casefold() else '')
                requests.append(('find_generic', {'brand': brand}))
        facts, warnings = [], []
        for name, args in requests:
            try:
                facts.append({'tool': name, 'result': call(name, args)})
            except Exception:
                warnings.append('The MCP medicine tool was unavailable. No tool finding is claimed; consult a pharmacist.')
        return {'facts': facts, 'documents': retrieve(q), 'warnings': warnings,
                'trace': state['trace'] + [('Interaction Agent' if interaction else 'Info Agent'),
                                         *['MCP: ' + r['tool'] for r in facts], 'RAG: TF-IDF retrieval']}

    def info(state):
        return collect(state)

    def interaction(state):
        return collect(state, True)

    def research(state):
        warnings = list(state.get('warnings', []))
        trace = list(state['trace'])
        web = {}
        if mode == 'Gemini + Tavily':
            if gemini_key:
                try:
                    research_result = run_react(state['query'], gemini_key, tavily_key, model_name)
                except Exception:
                    research_result = {'status': 'provider_error', 'trace': [], 'records': []}
                trace.append('Research Agent: ' + research_result['status'])
                if research_result['status'] != 'completed':
                    warnings.append('Gemini research did not complete (' + research_result['status'] + '). Showing only available source-backed evidence. Check the model name, API key and quota.')
                for record in research_result.get('records', []):
                    if record['tool'] == 'tavily_health_search':
                        web = record['result']
            else:
                research_result = {'status': 'missing_key', 'trace': [], 'records': []}
                warnings.append('Gemini API key missing. Only the local evidence path ran.')
            # A deterministic search fallback makes current-query behavior reliable even
            # when the model chooses not to search or Gemini is unavailable.
            if any(w in state['query'].casefold() for w in ['latest', 'current', 'recall', 'outbreak', 'advisory', 'recent']):
                if web.get('status') != 'searched':
                    web = web_search(state['query'], tavily_key)
                trace.append('Tavily: ' + web.get('status', 'unknown'))
            if web.get('status') in ['error', 'disabled']:
                warnings.append(web['message'])
        else:
            research_result = {'status': 'offline', 'trace': [], 'records': []}
            trace.append('Research Agent: offline (Gemini/Tavily not called)')
            if any(w in state['query'].casefold() for w in ['latest', 'current', 'recall', 'outbreak', 'advisory', 'recent']):
                warnings.append('Offline mode cannot verify current advisories, outbreaks or recalls. Enable live mode and configure Tavily.')
        return {'research': research_result, 'web': web, 'warnings': warnings, 'trace': trace}

    def response(state):
        return {'answer': render(state), 'trace': state['trace'] + ['Evidence Response Agent']}

    graph = StateGraph(State)
    for name, node in [('guardrail', guardrail), ('escalation', escalation), ('restricted', restricted),
                       ('info', info), ('interaction', interaction), ('research', research), ('response', response)]:
        graph.add_node(name, node)
    graph.add_edge(START, 'guardrail')
    graph.add_conditional_edges('guardrail', lambda s: s['route'],
                                {'emergency': 'escalation', 'restricted': 'restricted', 'info': 'info', 'interaction': 'interaction'})
    graph.add_edge('escalation', END)
    graph.add_edge('restricted', END)
    graph.add_edge('info', 'research')
    graph.add_edge('interaction', 'research')
    graph.add_edge('research', 'response')
    graph.add_edge('response', END)
    return graph.compile(checkpointer=InMemorySaver())
