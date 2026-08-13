"""
질문을 카테고리·지역·위험도로 분류하는 로직.
이 결과는 (1) 부서 라우팅, (2) 답변 전략 분기, (3) 온도계 대시보드용 로그 로 재사용된다.
"""
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

CLASSIFY_MODEL = "gpt-4o-mini"

CATEGORIES = ["체류/행정", "의료/건강보험", "교육/자녀", "주거/임대차", "금융/은행", "노동/취업", "통신", "교통", "생활/기타"]
REGIONS = ["연수구", "남동구", "서구", "중구", "미상"]

# 정확성이 중요한 카테고리 (틀리면 위험) → RAG 문서 없으면 함부로 답 안 함
HIGH_RISK_CATEGORIES = {"체류/행정", "의료/건강보험", "노동/취업", "교육/자녀", "주거/임대차", "금융/은행"}
# 틀려도 리스크가 낮은 카테고리 → GPT 일반지식으로 답변 가능
LOW_RISK_CATEGORIES = {"통신", "교통", "생활/기타"}


def classify_question(question: str) -> dict:
    """질문을 분류해서 {category, region, risk} 형태로 반환."""
    system_prompt = f"""
너는 질문을 분류하는 분류기야. 아래 JSON 형식으로만 답해.

카테고리는 반드시 다음 중 하나: {CATEGORIES}
지역은 질문에서 유추 가능하면 다음 중 하나, 모르면 "미상": {REGIONS}

{{"category": "...", "region": "..."}}
"""
    response = client.chat.completions.create(
        model=CLASSIFY_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    result = json.loads(response.choices[0].message.content)

    category = result.get("category", "생활/기타")
    region = result.get("region", "미상")
    risk = "고위험" if category in HIGH_RISK_CATEGORIES else "저위험"

    return {"category": category, "region": region, "risk": risk}
