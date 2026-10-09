"""Conservative English-only screening, not a medical triage classifier."""
import re

DISCLAIMER = 'Educational information only—not a diagnosis or prescription. Consult a doctor or pharmacist about your medicines. This prototype cannot rule out an emergency.'
EMERGENCY = ('Possible emergency: contact your local emergency services now (India: 112). '
             'Do not wait for this app or drive yourself. Ask someone nearby to help and follow the emergency operator’s instructions. '
             'This app has not contacted emergency services.')
RED_FLAGS = [r'chest\s+(pain|pressure|tightness)', r'pain\s+in\s+(my|the|his|her)\s+chest',
             r'(can.?t|cannot|unable to)\s+breathe', r'(severe|difficulty|trouble)\s+(breathing|breath)',
             r'short(ness)?\s+of\s+breath', r'(face|facial)\s+droop', r'slurred\s+speech',
             r'(sudden|one.sided)\s+(weakness|numbness)', r'unconscious|unresponsive|passed out',
             r'overdos(e|ed)|too many (pills|tablets)', r'(throat|tongue)\s+(is\s+)?swell',
             r'swell\w*\s+(of\s+)?(my\s+|the\s+)?(throat|tongue)', r'coughing (up )?blood',
             r'(vomit\w*|throwing up)\s+blood', r'(kill myself|suicid|end my life)',
             r'(severe|heavy|uncontrolled)\s+bleeding', r'\bseizure\b']
RESTRICTED = [r'\bdiagnos', r'what (disease|illness|condition) do i have', r'\bprescri',
              r'\bdos(age|e|ing)\b', r'how (much|many|often).*(take|tablet|pill|medicine)',
              r'what (medicine|medication|drug|tablet).*(should|can) i take',
              r'which (medicine|medication|drug|tablet).*(should|can) i take',
              r'(stop|start|increase|decrease|change) (taking |my )?(medication|medicine|dose|treatment)']

def screen(query: str) -> str:
    q = query.casefold().replace('’', "'")
    # Deliberately conservative: even quoted/negated red flags escalate.
    if any(re.search(p, q) for p in RED_FLAGS):
        return 'emergency'
    if any(re.search(p, q) for p in RESTRICTED):
        return 'restricted'
    if any(t in q for t in ['interaction', 'together', 'combine', 'can i take', 'with my', 'with warfarin']):
        return 'interaction'
    return 'info'
