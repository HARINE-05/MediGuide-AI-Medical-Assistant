import os
import json
import uuid
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from langgraph.types import Command
from src.workflow import build_graph
from src.safety import DISCLAIMER
from src.catalog import DATA

load_dotenv(Path(__file__).parent / '.env')
st.set_page_config(page_title='MediGuide | Medicine information', page_icon='💊', layout='wide')
st.markdown('''<style>
.stApp {background: #f5f8fb;} h1,h2,h3 {color:#163b4a;}
[data-testid="stMetric"] {background:white;border:1px solid #dbe7eb;border-radius:14px;padding:16px;}
[data-testid="stSidebar"] {background:#eaf2f4;}
</style>''', unsafe_allow_html=True)
st.caption('AGENTIC SYSTEMS CAPSTONE  •  TASK 05')
st.title('💊 MediGuide')
st.markdown('### Clear medicine information. Sources you can inspect.')
st.caption('Educational prototype • English queries • Small, curated dataset • Not a clinical service')
st.warning(DISCLAIMER)

with st.sidebar:
    st.header('Settings')
    mode = st.radio('Run mode', ['Offline demo', 'Gemini + Tavily'])
    key = st.text_input('Gemini API key', value=os.getenv('GEMINI_API_KEY', ''), type='password')
    tavily = st.text_input('Tavily API key', value=os.getenv('TAVILY_API_KEY', ''), type='password')
    model = st.text_input('Gemini model ID', value=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'))
    consent = st.checkbox('Allow this query to be sent to Gemini / Tavily', value=False)
    st.caption('Live mode sends query text to external providers. Use fictional demo queries; omit personal identifiers. Keys entered here stay in this session.')
    st.divider()
    st.markdown('**Supported medicine examples**\n\nParacetamol (acetaminophen), ibuprofen, warfarin.')
    st.caption('Generic example: Tylenol Regular Strength, US tablet label only.')
    if st.button('Clear session results'):
        for name in ['result', 'pending', 'graph', 'config']:
            st.session_state.pop(name, None)
        st.rerun()

cols = st.columns(3)
cols[0].metric('Custom MCP tools', '3')
cols[1].metric('Additional LangChain tools', '2')
cols[2].metric('Maximum ReAct turns', '4')

def show_result(result):
    if result.get('__interrupt__'):
        payload = result['__interrupt__'][0].value
        st.error(payload['message'])
        for url in payload['sources']:
            st.link_button('Emergency information source', url)
        st.info('Normal medicine processing is paused. The acknowledgement below only closes this query; it does not contact a clinician or emergency service.')
        if st.button('I have read the guidance — close this query'):
            finished = st.session_state.graph.invoke(Command(resume=True), st.session_state.config)
            st.session_state.result = finished
            st.session_state.pending = False
            st.rerun()
        return
    st.markdown(result.get('answer', 'No answer is available.'))
    with st.expander('Workflow and tool evidence'):
        st.write(' → '.join(result.get('trace', [])))
        st.json({'route': result.get('route'), 'mode': result.get('mode'),
                 'react_status': result.get('research', {}).get('status'),
                 'react_turns': result.get('research', {}).get('trace', []),
                 'mcp_findings': result.get('facts', []), 'web': result.get('web', {})})
        st.caption('This is a tool execution audit, not private model reasoning. Gemini research prose is not shown as medical advice.')
    st.download_button('Download this answer', result.get('answer', ''), 'mediguide_answer.md', 'text/markdown')

tab1, tab2, tab3 = st.tabs(['Ask MediGuide', 'Knowledge & sources', 'Project guide'])
with tab1:
    with st.form('question_form'):
        query = st.text_area('Your question', placeholder='What is paracetamol used for and what are its side effects?', max_chars=2000)
        a, b = st.columns(2)
        medicines = a.text_input('Interaction check: exact medicine names, separated by commas', placeholder='ibuprofen, warfarin')
        brand = b.text_input('Generic lookup: exact brand variant', placeholder='Tylenol Regular Strength')
        submitted = st.form_submit_button('Find information', type='primary', disabled=st.session_state.get('pending', False))
    st.caption('Examples: “Can I take ibuprofen with my blood pressure medication?” • “Latest medicine recall notices” • Emergency demo: “I have chest pain and my left arm feels numb.”')
    if submitted:
        # Screen locally even if live consent/key setup is incomplete.
        from src.safety import screen
        combined = ' '.join([query, medicines, brand])
        route = screen(combined)
        if not combined.strip():
            st.error('Enter a question, medicine names or a brand variant.')
        elif mode == 'Gemini + Tavily' and not consent and route not in ['emergency', 'restricted']:
            st.error('Enable the external-query checkbox or choose Offline demo.')
        else:
            question = query.strip() or ('Check interactions' if medicines.strip() else 'Find generic ingredient')
            graph = build_graph(mode, key, tavily, model)
            config = {'configurable': {'thread_id': str(uuid.uuid4())}, 'recursion_limit': 15}
            st.session_state.graph, st.session_state.config = graph, config
            with st.spinner('Screening and gathering source-backed information…'):
                try:
                    result = graph.invoke({'query': question,
                        'medicines': [m.strip() for m in medicines.split(',') if m.strip()][:10],
                        'brand': brand.strip()}, config)
                    st.session_state.result = result
                    st.session_state.pending = bool(result.get('__interrupt__'))
                    st.rerun()
                except Exception:
                    st.session_state.result = {'answer': 'The workflow could not complete. Restart the app and check the installation. No medical conclusion is available.\n\n' + DISCLAIMER}
    if 'result' in st.session_state:
        show_result(st.session_state.result)

with tab2:
    st.markdown('### Curated knowledge base')
    st.write('Short, original educational summaries—not full copied leaflets. TF-IDF retrieves relevant passages and preserves their source links. Content review date: 28 September 2026.')
    for doc in json.loads((DATA / 'knowledge.json').read_text(encoding='utf-8')):
        with st.expander(doc['id'] + ' · ' + doc['title']):
            st.write(doc['text'])
            st.link_button('Read original source', doc['url'])
    st.info('Only one known interaction pair is included: ibuprofen + warfarin, plus duplicate-ingredient checks. Missing pairs remain unknown. This is not a complete interaction database.')

with tab3:
    st.markdown('''### Demo in five steps
1. Ask about paracetamol and inspect its source links.
2. Enter ibuprofen and warfarin in the interaction field.
3. Enter Tylenol Regular Strength in the generic field.
4. Try the chest-pain example to show the LangGraph interrupt.
5. Configure your keys, enable live mode and ask for current recall notices.

### How it works
Guardrail screening runs first. The Info or Interaction Agent gathers evidence through MCP and RAG. In live mode, the Gemini Research Agent uses a bounded ReAct tool loop. The Evidence Response Agent renders sourced records and retrieved passages. Emergencies interrupt the graph and end after acknowledgement.

### Scope
No diagnosis, prescriptions, personalised dosing, automatic substitutions or emergency dispatch. Rule-based English screening can miss paraphrases and overflag quoted or negated symptoms. Human acknowledgement is a UI demonstration, not a clinical handoff. API key and model access are needed to demonstrate the live ReAct path.
''')
