"""AI에게 질문 탭 — /chat"""
from html import escape

import streamlit as st

import common

profile = st.session_state.profile


def build_chat_suggestions() -> list[str]:
    suggestions = []
    if profile.get("has_arc"):
        suggestions.append("외국인등록증 주소 변경은 어떻게 하나요?")
    else:
        suggestions.append("외국인등록증은 언제까지 신청해야 하나요?")
    if profile.get("has_korean_phone"):
        suggestions.append("한국 휴대폰 번호로 본인인증이 안 될 때는 어떻게 해야 하나요?")
    else:
        suggestions.append("외국인도 선불 유심을 바로 살 수 있나요?")
    if profile.get("has_korean_account"):
        suggestions.append("외국인이 계좌를 유지할 때 조심해야 할 점이 있나요?")
    else:
        suggestions.append("외국인이 은행 계좌를 만들 때 필요한 서류는 뭐예요?")
    suggestions.extend(
        [
            f"{profile['region']}에서 외국인 민원 상담은 어디로 가면 돼요?",
            "입국 후 첫 한 달에 꼭 해야 할 일은 뭐예요?",
        ]
    )
    return suggestions[:5]


def format_chat_text(text: str) -> str:
    return escape(text).replace("\n", "<br>")


def queue_chat_prompt(prompt: str | None = None):
    draft = (prompt if prompt is not None else st.session_state.get("chat_draft", "")).strip()
    if not draft:
        return
    st.session_state.chat_prompt_to_send = draft
    st.session_state.chat_draft = ""


def render_chat_message(msg: dict):
    content = format_chat_text(msg["content"])
    if msg["role"] == "user":
        st.markdown(
            f'<div class="injoy-chat-user-row"><div class="injoy-chat-user-bubble">{content}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="injoy-chat-assistant-card">
                <div class="injoy-chat-answer-label">✦ AI 답변</div>
                <div class="injoy-chat-answer-text">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_chat_composer():
    with st.container(key="chat_composer"):
        input_col, send_col = st.columns([1, 0.13], gap="small")
        with input_col:
            st.text_input(
                "질문 입력",
                key="chat_draft",
                label_visibility="collapsed",
                placeholder="무엇이든 물어보세요...",
                on_change=queue_chat_prompt,
            )
        with send_col:
            st.button("↑", key="chat_send", on_click=queue_chat_prompt)
        st.markdown(
            '<div class="injoy-chat-verify">중요한 행정·의료 정보는 공식 기관에서 한 번 더 확인해 주세요.</div>',
            unsafe_allow_html=True,
        )


# 생활가이드 상세페이지의 "AI에게 질문" 버튼에서 넘어온 경우, 질문 예시를 안내
prefill_topic = st.session_state.pop("chat_prefill_topic", None)
if prefill_topic:
    st.info(f"💡 이렇게 물어보면 돼요: \"{prefill_topic}에 대해 더 자세히 알려줘\"")

if "messages" not in st.session_state:
    st.session_state.messages = []
st.session_state.setdefault("chat_draft", "")

pending_prompt = st.session_state.get("chat_prompt_to_send")
if pending_prompt is not None:
    del st.session_state["chat_prompt_to_send"]
    st.session_state.messages.append({"role": "user", "content": pending_prompt})
else:
    pending_prompt = None

st.markdown(
    """
    <div class="injoy-chat-header">
        <div class="injoy-chat-header-title">AI에게 질문</div>
        <div class="injoy-chat-header-sub">답변과 함께 몰라서 못 물어본 생활 정보까지 챙겨드릴게요.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown(
        f"""
        <div class="injoy-chat-hero">
            <div class="injoy-chat-hero-icon">✦</div>
            <div class="injoy-chat-kicker">Life Navigator</div>
            <div class="injoy-chat-title">{profile['nickname']}님, 한국 생활에서 막히는 걸 편하게 물어보세요</div>
            <div class="injoy-chat-sub">
                {profile.get('language', '선택한 언어')}로 답변하고, 행정·의료·은행·통신처럼
                처음엔 놓치기 쉬운 정보도 함께 안내해요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    render_chat_message(msg)

if pending_prompt:
    with st.spinner("생각 중..."):
        answer = common.generate_answer(pending_prompt)
    answer_msg = {"role": "assistant", "content": answer}
    st.session_state.messages.append(answer_msg)
    render_chat_message(answer_msg)

st.markdown('<div class="injoy-chat-section">추천 질문</div>', unsafe_allow_html=True)
with st.container(key="chat_suggestions"):
    for i, question in enumerate(build_chat_suggestions()):
        st.button(
            question,
            key=f"chat_suggestion_{i}",
            on_click=queue_chat_prompt,
            args=(question,),
        )
st.markdown('<div class="injoy-chat-bottom-space"></div>', unsafe_allow_html=True)

render_chat_composer()
