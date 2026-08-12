"""
온동네 (On-Dongne) - 외국인 주민·유학생을 위한 AI 다국어 생활정보 안내 서비스
실행: streamlit run app.py
"""
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from utils.rag import load_faq_data, load_embeddings, search_top_k, is_covered_by_faq
from utils.classify import classify_question
from utils.routing import load_dept_routing, get_department_info

load_dotenv()
client = OpenAI()

CHAT_MODEL = "gpt-4o-mini"
LOG_PATH = "data/logs.csv"

st.set_page_config(page_title="온동네", page_icon="🏘️")


# ── 데이터 로드 (캐싱해서 매번 다시 안 읽도록) ──────────────────────────
@st.cache_resource
def load_all_data():
    faq_data = load_faq_data()
    faq_embeddings = load_embeddings() if os.path.exists("data/faq_embeddings.npy") else None
    dept_data = load_dept_routing()
    return faq_data, faq_embeddings, dept_data


faq_data, faq_embeddings, dept_data = load_all_data()


# ── 로그 저장 (온도계 대시보드용 산출물 데이터) ──────────────────────────
def log_question(question: str, category: str, region: str, risk: str, source: str):
    row = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "category": category,
        "region": region,
        "risk": risk,
        "answer_source": source,  # "FAQ" | "일반지식" | "웹서치"
    }
    df_row = pd.DataFrame([row])
    if os.path.exists(LOG_PATH):
        df_row.to_csv(LOG_PATH, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df_row.to_csv(LOG_PATH, mode="w", header=True, index=False, encoding="utf-8-sig")


# ── 답변 생성 (위험도별 3단계 라우팅) ────────────────────────────────
def generate_answer(question: str) -> str:
    # 1단계: RAG 검색
    if faq_embeddings is not None:
        top_docs, top_score = search_top_k(question, faq_data, faq_embeddings, k=3)
    else:
        top_docs, top_score = [], 0.0

    classification = classify_question(question)
    category, region, risk = classification["category"], classification["region"], classification["risk"]

    if faq_embeddings is not None and is_covered_by_faq(top_score):
        # FAQ 문서 기반 답변
        context = "\n".join(f"- {d['question']} {d['answer']}" for d in top_docs)
        system_prompt = f"""너는 인천 거주 외국인을 돕는 다국어 안내 챗봇이야. 사용자가 사용한 언어로 답해.
아래 참고 문서에 근거해서만 답변해. 문서에 없는 내용은 추측하지 마.

[참고 문서]
{context}"""
        source = "FAQ"

    elif risk == "저위험":
        # GPT 일반지식으로 답변 (교통/통신/생활꿀팁 등)
        system_prompt = "너는 인천 거주 외국인을 돕는 다국어 안내 챗봇이야. 사용자가 사용한 언어로, 한국 생활에 대한 일반적인 지식을 바탕으로 친절하게 답해."
        source = "일반지식"

    else:
        # 고위험 + FAQ 미커버 → 웹서치 폴백 (선택 기능, 실패해도 안전하게 처리)
        try:
            web_response = client.responses.create(
                model=CHAT_MODEL,
                tools=[{"type": "web_search"}],
                input=f"인천 거주 외국인 관점에서: {question}",
            )
            answer = web_response.output_text
            source = "웹서치"
            log_question(question, category, region, risk, source)
            return answer
        except Exception:
            # 웹서치 실패 시 안전하게 공식 안내로 폴백
            system_prompt = "너는 인천 거주 외국인을 돕는 다국어 안내 챗봇이야. 확실하지 않은 정보는 지어내지 말고, 정확한 정보는 하이코리아(hikorea.go.kr) 또는 외국인종합안내센터(1345)에서 확인하라고 안내해."
            source = "안내(폴백)"

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    answer = response.choices[0].message.content

    # 부서 라우팅 정보 덧붙이기 (지역이 특정됐고, 행정 관련 카테고리일 때만)
    dept_note = get_department_info(region, dept_data)
    if dept_note and category in ("체류/행정", "의료/건강보험", "노동/취업"):
        answer += f"\n\n📍 {dept_note}"

    log_question(question, category, region, risk, source)
    return answer


# ── 화면 구성 ────────────────────────────────────────────────
st.title("온동네 🏘️")

tab_home, tab_chat = st.tabs(["홈", "챗봇"])

with tab_home:
    st.subheader("정착 체크리스트")
    st.caption("3가지만 알려주시면 놓치기 쉬운 정보를 먼저 보여드려요")

    col1, col2, col3 = st.columns(3)
    with col1:
        region_input = st.selectbox("거주지역", list(dept_data.keys()))
    with col2:
        purpose_input = st.selectbox("체류목적", ["근로", "유학", "동반가족"])
    with col3:
        transport_input = st.selectbox("주 이동수단", ["대중교통", "자차", "도보·자전거"])

    if st.button("시작하기"):
        st.info("궁금한 게 있으면 언제든 '챗봇' 탭에서 물어보세요!")

    st.divider()
    st.subheader("카테고리")
    categories = sorted(set(d["category"] for d in faq_data))
    cols = st.columns(3)
    for i, cat in enumerate(categories):
        with cols[i % 3]:
            with st.expander(cat):
                items = [d for d in faq_data if d["category"] == cat]
                for item in items:
                    st.markdown(f"**{item['question']}**")
                    st.caption(item["answer"])

with tab_chat:
    st.caption("궁금한 걸 자유롭게 물어보세요 (다국어 지원)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("예: 외국인등록은 어떻게 하나요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.spinner("답변 준비 중..."):
            answer = generate_answer(prompt)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
