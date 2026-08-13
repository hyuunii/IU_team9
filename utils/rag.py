"""
RAG 검색 로직.
검색(유사도 계산)은 여기서 우리가 직접 하고, GPT는 답변 생성만 담당한다.
"""
import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"

# 이 값보다 유사도가 낮으면 "FAQ에 없는 질문"으로 간주하고 다른 답변 전략으로 넘어감
SIMILARITY_THRESHOLD = 0.75


def load_faq_data(path: str = "data/faq.json") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_embeddings(path: str = "data/faq_embeddings.npy") -> np.ndarray:
    return np.load(path)


def get_query_embedding(text: str) -> np.ndarray:
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return np.array(response.data[0].embedding, dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search_top_k(question: str, faq_data: list[dict], faq_embeddings: np.ndarray, k: int = 3):
    """질문과 가장 유사한 FAQ top-k를 찾아서 반환.
    반환값: (선택된 FAQ 리스트, 최고 유사도 점수)
    """
    q_emb = get_query_embedding(question)
    scores = [cosine_similarity(q_emb, doc_emb) for doc_emb in faq_embeddings]
    top_indices = np.argsort(scores)[-k:][::-1]

    selected = [faq_data[i] for i in top_indices]
    top_score = scores[top_indices[0]]
    return selected, top_score


def is_covered_by_faq(top_score: float) -> bool:
    return top_score >= SIMILARITY_THRESHOLD
