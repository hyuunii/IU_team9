"""마이 라이프 — 체류기간별 체크리스트, 저장 정보, 미질문 정보 추천."""
from html import escape

import streamlit as st

import common

profile = common.require_profile()

CHECKLISTS = {
    "1개월 미만": [
        ("transport", "대중교통 이용법 익히기", "transport"),
        ("phone", "휴대폰 개통하기", "telecom"),
        ("bank", "은행 기본 이해하기", "finance"),
        ("hospital", "병원 이용법 알기", "medical"),
        ("waste", "쓰레기 배출 방법 알아보기", "daily"),
        ("support", "가까운 외국인 지원기관 찾기", "admin"),
        ("apps", "한국 생활 필수 앱 알아보기", "daily"),
    ],
    "1개월~6개월": [
        ("address", "주소 변경 신고 방법 확인하기", "admin"),
        ("insurance", "건강보험 가입 상태 확인하기", "medical"),
        ("contract", "근로계약서와 급여명세서 확인하기", "job"),
        ("banking", "인터넷·모바일뱅킹 익히기", "finance"),
        ("korean", "가까운 한국어 교육기관 찾기", "daily"),
        ("lease", "임대차 계약과 관리비 확인하기", "housing"),
        ("emergency", "긴급 연락처 저장하기", "emergency"),
    ],
    "6개월~1년": [
        ("visa", "체류기간 만료일과 연장 절차 확인하기", "admin"),
        ("tax", "세금과 연말정산 기본 알아보기", "job"),
        ("checkup", "건강검진 대상 여부 확인하기", "medical"),
        ("housing", "주거 계약 갱신 조건 확인하기", "housing"),
        ("fraud", "금융사기 예방수칙 익히기", "finance"),
        ("career", "취업·직업훈련 지원 알아보기", "job"),
        ("community", "지역 커뮤니티와 지원기관 활용하기", "daily"),
    ],
    "1년 이상": [
        ("renewal", "장기 체류 갱신 일정을 점검하기", "admin"),
        ("pension", "국민연금 가입·환급 조건 확인하기", "job"),
        ("housing_support", "주거지원 제도 알아보기", "housing"),
        ("family", "가족·자녀 교육 지원 알아보기", "daily"),
        ("health", "정기검진과 예방접종 일정 관리하기", "medical"),
        ("finance_plan", "저축·신용관리 방법 점검하기", "finance"),
        ("participation", "지역사회 참여 프로그램 찾아보기", "daily"),
    ],
}

QUESTION_KEYWORDS = {
    "transport": ("교통", "버스", "지하철", "교통카드"),
    "telecom": ("휴대폰", "유심", "통신", "본인인증"),
    "finance": ("은행", "계좌", "금융", "송금"),
    "medical": ("병원", "의료", "건강", "보험"),
    "housing": ("주거", "집", "임대", "계약"),
    "job": ("직장", "노동", "근로", "취업", "급여"),
    "admin": ("행정", "비자", "체류", "등록증", "주소"),
    "daily": ("쓰레기", "한국어", "생활", "교육", "앱"),
}


def related_guide_item(cat_id: str):
    return next((item for item in common.GUIDE_ITEMS if item["cat_id"] == cat_id), None)


def open_guide(item: dict):
    st.session_state.guide_detail_id = item["id"]
    st.switch_page(common.PAGES["guide"])


def edit_profile():
    del st.session_state["profile"]
    st.rerun()


st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display:none !important; }
    [data-testid="stHeader"] { display:none !important; }
    [data-testid="stMainBlockContainer"] { max-width:520px !important; margin:0 auto !important; padding-top:0 !important; }
    [data-testid="stElementContainer"]:has(h1) { display:none !important; }
    .injoy-life-header { display:flex; align-items:center; justify-content:space-between; height:68px; margin-top:-32px; padding:24px 4px 12px; }
    .injoy-life-title { color:oklch(24% .03 55); font-size:24px; font-weight:800; line-height:32px; }
    .injoy-life-lang { display:inline-flex; border:1px solid #E3DDD3; border-radius:999px; overflow:hidden; font-size:10px; color:#76695D; }
    .injoy-life-lang span { padding:5px 10px; } .injoy-life-lang .active { background:#008F91; color:#FFF; font-weight:800; }
    .st-key-mylife_profile_card { box-sizing:border-box !important; position:relative !important; display:block !important; width:488px !important; height:68px !important; min-height:68px !important; background:#FFF; border-radius:29.6px; box-shadow:0 8px 24px -12px oklch(40% .05 60/.25); padding:0 !important; margin-bottom:0; }
    .st-key-mylife_profile_card > [data-testid="stElementContainer"]:first-child { position:absolute !important; left:16px !important; right:118px !important; top:16px !important; width:auto !important; height:36px !important; min-width:0 !important; overflow:hidden !important; }
    .st-key-mylife_profile_card > [data-testid="stElementContainer"]:last-child { position:absolute !important; right:16px !important; top:19px !important; width:auto !important; height:30px !important; }
    .injoy-profile-card { padding:0; }
    .injoy-profile-meta { color:oklch(24% .03 55); font-size:14px; font-weight:800; line-height:20px; }
    .injoy-profile-progress { color:oklch(53% .025 65); font-size:12px; line-height:16px; margin-top:0; }
    .st-key-mylife_profile_card button { width:auto !important; height:30px !important; min-height:30px !important; padding:6px 12px !important; border-radius:999px !important; font-size:12px !important; line-height:16px !important; background:#FFF !important; border:1px solid #E3DDD3 !important; }
    .injoy-life-section { margin:8px 4px 12px; } .injoy-life-section-title { color:oklch(24% .03 55); font-size:18px; font-weight:800; line-height:28px; }
    .injoy-life-section-sub { color:oklch(53% .025 65); font-size:12px; line-height:16px; margin-top:0; }
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] { box-sizing:border-box !important; position:relative !important; display:block !important; height:56px !important; min-height:56px !important; max-height:56px !important; overflow:hidden; background:#FFF; border-radius:25.6px; box-shadow:0 8px 24px -12px oklch(40% .05 60/.25); padding:0 !important; margin-bottom:8px; }
    /* 자동 정렬 대신 56px 카드 안에서 중심 좌표를 px로 고정한다. */
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] > [data-testid="stElementContainer"]:first-child { position:absolute !important; left:14px !important; top:9px !important; width:28px !important; height:28px !important; }
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] > [data-testid="stElementContainer"]:nth-child(2) { position:absolute !important; left:54px !important; right:89px !important; top:18px !important; width:auto !important; height:20px !important; min-width:0 !important; overflow:hidden !important; }
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] > [data-testid="stElementContainer"]:last-child { position:absolute !important; right:14px !important; top:14.5px !important; width:auto !important; height:16px !important; }
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] > [data-testid="stElementContainer"]:nth-child(2) [data-testid="stMarkdown"],
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] > [data-testid="stElementContainer"]:nth-child(2) [data-testid="stMarkdownContainer"] { display:block !important; height:20px !important; min-height:20px !important; }
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] p { margin:0 !important; padding:0 !important; line-height:inherit !important; }
    [class*="st-key-lifecheck_"] button { min-height:auto !important; box-shadow:none !important; }
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] > [data-testid="stElementContainer"]:first-child button { width:28px !important; min-width:28px !important; height:28px !important; padding:0 !important; border-radius:50% !important; background:#FFF !important; border:2px solid #E3DDD3 !important; color:#008F91 !important; caret-color:transparent !important; outline:none !important; font-size:14px !important; }
    [data-testid="stHorizontalBlock"][class*="st-key-lifecheck_"] > [data-testid="stElementContainer"]:last-child button { width:auto !important; height:16px !important; min-height:16px !important; padding:0 !important; border:0 !important; border-radius:0 !important; background:transparent !important; color:oklch(55% .15 195) !important; font-size:12px !important; line-height:16px !important; font-weight:700 !important; }
    .injoy-check-title { color:oklch(24% .03 55); font-size:14px; font-weight:600; line-height:20px; }
    .injoy-check-title.done { color:#9A9188; text-decoration:line-through; }
    .injoy-empty { color:#76695D; font-size:12px; padding:2px 4px 18px; }
    [data-testid="stElementContainer"][class*="st-key-mylife_saved_"] button,
    [data-testid="stElementContainer"][class*="st-key-mylife_unknown_"] button { width:100% !important; min-height:auto !important; text-align:left !important; white-space:pre-line !important; padding:13px 38px 13px 15px !important; margin-bottom:8px !important; border:0 !important; border-radius:22px !important; background:#FFF !important; color:#2A1B11 !important; box-shadow:0 8px 22px -14px rgba(92,65,44,.28) !important; font-size:11px !important; line-height:1.5 !important; position:relative !important; }
    [data-testid="stElementContainer"][class*="st-key-mylife_saved_"] button::first-line,
    [data-testid="stElementContainer"][class*="st-key-mylife_unknown_"] button::first-line { font-size:13px !important; font-weight:800 !important; }
    [data-testid="stElementContainer"][class*="st-key-mylife_saved_"] button::after,
    [data-testid="stElementContainer"][class*="st-key-mylife_unknown_"] button::after { content:'›'; position:absolute; right:16px; top:50%; transform:translateY(-50%); color:#008F91; font-size:18px; }
    .injoy-life-gap { height:18px; }
    </style>
    """,
    unsafe_allow_html=True,
)

duration = profile.get("duration", "1개월 미만")
checklist = CHECKLISTS.get(duration, CHECKLISTS["1개월 미만"])
completed = st.session_state.setdefault("completed_checklist_ids", set())
saved_ids = st.session_state.setdefault("saved_guide_ids", set())

st.markdown(
    '<div class="injoy-life-header"><div class="injoy-life-title">마이 라이프</div>'
    '<div class="injoy-life-lang"><span>EN</span><span class="active">한국어</span></div></div>',
    unsafe_allow_html=True,
)
with st.container(key="mylife_profile_card", horizontal=True):
    st.markdown(
        f'<div class="injoy-profile-card">'
        f'<div class="injoy-profile-meta">{escape(profile.get("region", "인천"))} · 체류기간 {escape(duration)}</div>'
        f'<div class="injoy-profile-progress">{len(completed)}/{len(checklist)} 완료 · {len(saved_ids)}개 저장</div></div>',
        unsafe_allow_html=True,
    )
    st.button("프로필 수정", key="mylife_edit_profile", on_click=edit_profile)

st.markdown(
    f'<div class="injoy-life-section"><div class="injoy-life-section-title">나의 체크리스트</div>'
    f'<div class="injoy-life-section-sub">{escape(duration)} · 한국 생활 시작하기</div></div>',
    unsafe_allow_html=True,
)

for item_id, title, cat_id in checklist:
    is_done = item_id in completed
    with st.container(key=f"lifecheck_{item_id}", horizontal=True, vertical_alignment="center"):
        if st.button("✓" if is_done else "", key=f"lifecheck_toggle_{item_id}"):
            completed.discard(item_id) if is_done else completed.add(item_id)
            st.rerun()
        st.markdown(
            f'<div class="injoy-check-title{" done" if is_done else ""}">{escape(title)}</div>',
            unsafe_allow_html=True,
        )
        guide_item = related_guide_item(cat_id)
        if st.button("자세히 보기", key=f"lifecheck_detail_{item_id}", disabled=guide_item is None):
            open_guide(guide_item)

st.markdown('<div class="injoy-life-gap"></div>', unsafe_allow_html=True)
st.markdown('<div class="injoy-life-section"><div class="injoy-life-section-title">저장한 정보</div><div class="injoy-life-section-sub">생활가이드에서 스크랩한 정보</div></div>', unsafe_allow_html=True)
saved_items = [item for item in common.GUIDE_ITEMS if item["id"] in saved_ids]
if not saved_items:
    st.markdown('<div class="injoy-empty">아직 저장한 정보가 없어요.</div>', unsafe_allow_html=True)
for item in saved_items:
    if st.button(f'{item["icon"]} {item["title"]}\n{item["desc"][:72]}', key=f'mylife_saved_{item["id"]}'):
        open_guide(item)

# 질문한 분야와 완료한 체크리스트 분야는 이미 접한 정보로 보고 추천에서 제외한다.
asked_text = " ".join(
    msg.get("content", "") for msg in st.session_state.get("messages", []) if msg.get("role") == "user"
)
asked_categories = {
    cat_id for cat_id, keywords in QUESTION_KEYWORDS.items() if any(word in asked_text for word in keywords)
}
completed_categories = {cat_id for item_id, _title, cat_id in checklist if item_id in completed}
excluded_categories = asked_categories | completed_categories
unknown_items = []
seen_categories = set()
for item in common.GUIDE_ITEMS:
    if item["id"] in saved_ids or item["cat_id"] in excluded_categories or item["cat_id"] in seen_categories:
        continue
    unknown_items.append(item)
    seen_categories.add(item["cat_id"])
    if len(unknown_items) == 3:
        break

st.markdown('<div class="injoy-life-gap"></div>', unsafe_allow_html=True)
st.markdown('<div class="injoy-life-section"><div class="injoy-life-section-title">아직 모를 수 있는 것들</div><div class="injoy-life-section-sub">질문·체크리스트 기록을 바탕으로 골랐어요</div></div>', unsafe_allow_html=True)
if not unknown_items:
    st.markdown('<div class="injoy-empty">추천할 새로운 정보를 찾고 있어요.</div>', unsafe_allow_html=True)
for item in unknown_items:
    if st.button(f'{item["icon"]} {item["title"]}\n{item["desc"][:72]}', key=f'mylife_unknown_{item["id"]}'):
        open_guide(item)
