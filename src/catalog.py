import json
import re
from itertools import combinations
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'
MEDICINES = json.loads((DATA / 'medicines.json').read_text(encoding='utf-8'))
GENERIC_SOURCE = 'https://www.dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1622f694-4d63-4c56-8737-fae31f0ecfb7'

def normalize(name):
    name = name.strip().casefold()
    for generic, record in MEDICINES.items():
        if name in record['aliases']:
            return generic
    return None

def mentioned(query):
    return [generic for generic, record in MEDICINES.items()
            if any(re.search(r'\b' + re.escape(a) + r'\b', query.casefold()) for a in record['aliases'])]

def drug_info(medicine: str) -> dict:
    key = normalize(medicine)
    return {'medicine': key, **MEDICINES[key]} if key else {
        'status': 'unknown', 'message': 'Not in the limited educational catalogue. Ask a pharmacist; no safety conclusion is available.'}

def check_interaction(medicines: list[str]) -> dict:
    names = list(dict.fromkeys(m.strip().casefold() for m in medicines if m.strip()))
    if len(names) < 2:
        return {'status': 'needs_names', 'message': 'Provide the exact names of at least two medicines. A medicine class such as blood-pressure medication is not enough.'}
    pairs = []
    for a, b in combinations(names, 2):
        normalized = {normalize(a), normalize(b)}
        known = normalized == {'ibuprofen', 'warfarin'}
        duplicate = normalize(a) is not None and normalize(a) == normalize(b)
        pairs.append({'medicines': [a, b], 'status': 'warning' if known or duplicate else 'unknown',
            'message': ('Ibuprofen and warfarin may increase bleeding risk. Ask a pharmacist or clinician to review the combination.' if known else
                        'These names refer to the same active ingredient. Ask a pharmacist to check for duplicate products.' if duplicate else
                        'This pair is not covered by the small dataset. This does NOT mean it is safe.'),
            'source': 'https://www.nhs.uk/medicines/nsaids/' if known else (MEDICINES[normalize(a)]['source'] if duplicate else '')})
    return {'status': 'limited_check', 'pairs': pairs, 'message': 'Do not start, stop or change prescribed medicines based on this prototype. A pharmacist must review the full list, including supplements.'}

def find_generic(brand: str) -> dict:
    if brand.strip().casefold() in ['tylenol regular strength', 'tylenol regular strength tablet']:
        return {'status': 'ingredient_match', 'brand': brand, 'generic': 'acetaminophen (paracetamol)',
                'source': GENERIC_SOURCE, 'message': 'US Regular Strength tablet example only. Ask a pharmacist to match the exact strength, formulation and ingredients. No cheaper price or substitution is guaranteed.'}
    return {'status': 'unknown', 'message': 'Exact brand variant not in the dataset. Provide the complete product name and ask a pharmacist to confirm ingredients. No substitution is recommended.'}
