"""
FAQ 데이터를 임베딩 벡터로 변환해서 저장하는 스크립트.
FAQ 내용이 바뀔 때마다 한 번씩만 실행하면 됨 (매 챗봇 실행마다 돌릴 필요 없음).

사용법: python embed_faq.py
"""
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"


def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def main():
    with open("data/faq.json", encoding="utf-8") as f:
        faq_data = json.load(f)

    print(f"{len(faq_data)}개 FAQ 임베딩 생성 중...")
    embeddings = []
    for i, item in enumerate(faq_data):
        # 질문+답변을 합쳐서 임베딩 (질문만 넣으면 표현이 다를 때 검색 정확도가 떨어짐)
        combined = f"{item['question']} {item['answer']}"
        vec = embed_text(combined)
        embeddings.append(vec)
        print(f"  [{i+1}/{len(faq_data)}] {item['id']} 완료")

    embeddings_array = np.array(embeddings, dtype=np.float32)
    np.save("data/faq_embeddings.npy", embeddings_array)
    print(f"저장 완료: data/faq_embeddings.npy (shape={embeddings_array.shape})")


if __name__ == "__main__":
    main()
