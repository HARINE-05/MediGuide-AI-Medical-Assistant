from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')

def test_ui_info_and_clear():
    at = AppTest.from_file(APP, default_timeout=45).run()
    assert not at.exception
    at.text_area[0].set_value('What is paracetamol used for?')
    next(b for b in at.button if b.label == 'Find information').click().run()
    assert not at.exception
    assert any('Relieves pain' in m.value for m in at.markdown)
    next(b for b in at.button if b.label == 'Clear session results').click().run()
    assert 'result' not in at.session_state

def test_ui_emergency_acknowledgement():
    at = AppTest.from_file(APP, default_timeout=45).run()
    at.text_area[0].set_value('I have chest pain and my left arm feels numb')
    next(b for b in at.button if b.label == 'Find information').click().run()
    assert not at.exception
    assert any('112' in e.value for e in at.error)
    assert next(b for b in at.button if b.label == 'Find information').disabled
    next(b for b in at.button if b.label.startswith('I have read')).click().run()
    assert not at.exception
    assert not next(b for b in at.button if b.label == 'Find information').disabled
