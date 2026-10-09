import json
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.catalog import DATA

@lru_cache(maxsize=1)
def index():
    docs = json.loads((DATA / 'knowledge.json').read_text(encoding='utf-8'))
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    vectors = vectorizer.fit_transform(d['title'] + ' ' + d['text'] for d in docs)
    return docs, vectorizer, vectors

def retrieve(query: str, k: int = 3) -> list[dict]:
    docs, vectorizer, vectors = index()
    scores = cosine_similarity(vectorizer.transform([query]), vectors).ravel()
    return [{**docs[i], 'score': round(float(scores[i]), 3)}
            for i in scores.argsort()[::-1][:k] if scores[i] >= 0.10]
