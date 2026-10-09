import asyncio
import uuid
import pytest
from langgraph.types import Command
from langchain_core.messages import AIMessage
from src.safety import screen, DISCLAIMER
from src.catalog import check_interaction, find_generic
from src.mcp_client import call_many
from src.retrieval import retrieve
from src.workflow import build_graph
from src.research import run_react, web_search

@pytest.mark.parametrize('q', ['I have chest pain and my left arm feels numb', 'I cannot breathe',
    'My tongue is swelling', 'He is unconscious', 'I took too many pills', 'I want to kill myself'])
def test_red_flags(q):
    assert screen(q) == 'emergency'

@pytest.mark.parametrize('q', ['Diagnose my headache', 'What dose should I take?', 'Prescribe tablets',
                              'What medicine should I take for fever?'])
def test_boundaries(q):
    assert screen(q) == 'restricted'

def test_unknown_never_safe():
    result = check_interaction(['unknown tablet', 'ibuprofen', 'warfarin'])
    assert len(result['pairs']) == 3
    assert [p['status'] for p in result['pairs']].count('unknown') == 2
    assert result['pairs'][-1]['status'] == 'warning'

def test_duplicate():
    assert check_interaction(['paracetamol', 'acetaminophen'])['pairs'][0]['status'] == 'warning'

def test_brand_variant():
    assert find_generic('Tylenol')['status'] == 'unknown'
    assert find_generic('Tylenol Regular Strength')['status'] == 'ingredient_match'

def test_rag():
    assert retrieve('ibuprofen side effects')[0]['id'] == 'K2'
    assert retrieve('galaxy astronomy black hole') == []

def test_real_mcp_transport():
    results = asyncio.run(call_many([('drug_info', {'medicine': 'paracetamol'}),
        ('check_interaction', {'medicines': ['ibuprofen', 'warfarin']}),
        ('find_generic', {'brand': 'Tylenol Regular Strength'})]))
    assert results[0]['medicine'] == 'paracetamol'
    assert results[1]['pairs'][0]['status'] == 'warning'
    assert results[2]['status'] == 'ingredient_match'

def config():
    return {'configurable': {'thread_id': str(uuid.uuid4())}}

def test_emergency_interrupt_and_terminal_resume():
    graph = build_graph()
    c = config()
    result = graph.invoke({'query': 'I have chest pain'}, c)
    assert result['__interrupt__']
    assert '112' in result['__interrupt__'][0].value['message']
    assert result['facts'] == []
    result = graph.invoke(Command(resume=True), c)
    assert DISCLAIMER in result['answer']
    assert 'research' not in result
    assert not graph.get_state(c).next

def test_form_cannot_bypass_guardrail():
    g = build_graph()
    r = g.invoke({'query': 'generic', 'brand': 'chest pain'}, config())
    assert r['__interrupt__']

def test_workflow_info():
    r = build_graph().invoke({'query': 'What is paracetamol used for?'}, config())
    assert r['facts'][0]['result']['medicine'] == 'paracetamol'
    assert DISCLAIMER in r['answer']
    assert r['research']['status'] == 'offline'

def test_needs_exact_names():
    r = build_graph().invoke({'query': 'Can I take ibuprofen with my blood pressure medication?'}, config())
    assert r['facts'][0]['result']['status'] == 'needs_names'

def test_missing_live_keys_visible():
    r = build_graph('Gemini + Tavily').invoke({'query': 'Latest medicine recall'}, config())
    assert r['research']['status'] == 'missing_key'
    assert r['web']['status'] == 'disabled'
    assert r['warnings']

class LoopModel:
    def bind_tools(self, tools):
        self.tools = tools
        return self
    def invoke(self, messages):
        return AIMessage(content='', tool_calls=[{'id': str(len(messages)), 'name': 'search_knowledge',
                                                  'args': {'query': 'paracetamol'}}])

def test_react_iteration_limit_and_tool_observations():
    m = LoopModel()
    result = run_react('paracetamol', '', '', '', model=m)
    assert result['status'] == 'iteration_limit'
    assert len(result['trace']) == 4
    assert len(result['records']) == 4
    assert {t.name for t in m.tools} == {'drug_info','check_interaction','find_generic','search_knowledge','tavily_health_search'}

def test_web_missing_key():
    assert web_search('recall', '')['status'] == 'disabled'
