"""
인조이 (INJOY) - 외국인 주민·유학생을 위한 AI 다국어 생활정보 안내 서비스
실행: streamlit run app.py
"""
import json
import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # utils/*.py가 import 시점에 OpenAI() 클라이언트를 만들기 때문에,
                # .env 로딩은 반드시 그 import들보다 먼저 실행돼야 함

from openai import OpenAI

from utils.rag import load_faq_data, load_embeddings, search_top_k, is_covered_by_faq
from utils.classify import classify_question
from utils.routing import load_dept_routing, get_department_info

client = OpenAI()

CHAT_MODEL = "gpt-4o-mini"
LOG_PATH = "data/logs.csv"

st.set_page_config(page_title="인조이", page_icon="🏘️")

# ── 온보딩 항목 ────────────────────────────────────────────
# 필수: 닉네임, 나이, 외국인등록증 여부, 거주지역, 체류기간, 언어
# 선택: 이름, 본국, 인천 거주 여부, 한국 전화번호, 한국 계좌 여부, 체류목적
ONBOARD_PURPOSES = ["개인", "가정", "노동자", "유학생", "기타"]
ONBOARD_DURATIONS = ["1개월 미만", "1개월~6개월", "6개월~1년", "1년 이상"]
YES_NO = ["예", "아니오"]

# 다누리콜센터(1577-1366) 지원 언어 기준 — FAQ 통역 안내와 실제로 맞는 언어 세트
LANGUAGES = [
    ("🇰🇷", "한국어"),
    ("🇺🇸", "English"),
    ("🇨🇳", "中文"),
    ("🇻🇳", "Tiếng Việt"),
    ("🇵🇭", "Filipino"),
    ("🇰🇭", "ខ្មែរ"),
    ("🇲🇳", "Монгол"),
    ("🇷🇺", "Русский"),
    ("🇯🇵", "日本語"),
    ("🇹🇭", "ไทย"),
    ("🇺🇿", "Oʻzbekcha"),
    ("🇳🇵", "नेपाली"),
    ("🇱🇦", "ລາວ"),
]
LANGUAGE_LABELS = [f"{flag} {name}" for flag, name in LANGUAGES]

# 생활가이드 3x3 카테고리 그리드 (Lovable 프로토타입 정보구조 기준)
# faq.json의 category 값과 그리드 라벨이 1:1로 안 맞는 경우가 있어서(예: "은행·금융" ↔
# 실제 데이터의 "금융/은행") id를 키로 하는 매핑 테이블로 관리한다.
CATEGORY_GRID = [
    {"id": "transport", "icon": "🚌", "label": "교통", "categories": ["교통"]},
    {"id": "medical", "icon": "🏥", "label": "의료", "categories": ["의료/건강보험"]},
    {"id": "finance", "icon": "💳", "label": "은행·금융", "categories": ["금융/은행"]},
    {"id": "housing", "icon": "🏠", "label": "주거", "categories": ["주거/임대차"]},
    {"id": "telecom", "icon": "📱", "label": "통신·인터넷", "categories": ["통신"]},
    {"id": "daily", "icon": "🗑️", "label": "일상생활", "categories": ["생활/기타", "교육/자녀"]},
    {"id": "job", "icon": "💼", "label": "직장·노동", "categories": ["노동/취업"]},
    {"id": "admin", "icon": "🏛️", "label": "행정·비자", "categories": ["체류/행정"]},
    {"id": "emergency", "icon": "🚨", "label": "긴급상황", "categories": []},
]

# 홈 "당신을 위한 추천" / 생활가이드 목록에 공통으로 쓰는 "생활 팁" 큐레이션.
# 마지막 값은 CATEGORY_GRID의 id — 생활가이드 탭 필터 칩과 연결하기 위함.
# (추후 프로필 기반 개인화로 고도화 예정)
HOME_TIPS = [
    ("🚌", "터미널 가기 전에 미리 예매하기", "시외·고속버스는 '고속버스티머니', '버스타고' 앱으로 미리 예매할 수 있어요.", "transport"),
    ("📶", "유심은 공항·편의점에서도 구매 가능", "외국인등록증 발급 전이라면 선불폰·알뜰폰 유심으로 임시 이용할 수 있어요.", "telecom"),
    ("🏥", "다국어 통역이 필요하면 1577-1366", "다누리콜센터가 병원·약국 통역을 무료로 연결해줘요 (13개 언어 지원).", "medical"),
]

EMERGENCY_INFO = [
    ("🚑", "응급/화재 신고", "119"),
    ("🈳", "다국어 통역 지원", "다누리콜센터 1577-1366"),
    ("👮", "외국인종합안내센터", "1345"),
    ("🗣️", "BBB코리아 통역 서비스", "1588-5644"),
]


def inject_css():
    st.markdown(
        """
        <style>
        /* Lovable(incheon-life-compass) 디자인 토큰에서 그대로 가져온 값들:
           --background: #FDFAF4, --card: #FFFFFF, --foreground: #2A1B11,
           --muted-foreground: #76695D, --border: #E3DDD3, --radius: 1.1rem(17.6px),
           rounded-2xl = radius+8px = 25.6px, shadow-card = 0 8px 24px -12px rgba(92,65,44,.25),
           font-display/font-body = 'Plus Jakarta Sans' */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"] * {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* 전체 배경 */
        [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FDFAF4;
        }

        /* Lovable 원본처럼 앱을 모바일 폭(520px)으로 고정하고 가운데 정렬.
           (원본: <div class="mx-auto flex min-h-screen w-full max-w-[520px] ...">)
           이걸 해야 카드 3등분 비율이 원본처럼 좁고 정사각형에 가깝게 나온다. */
        [data-testid="stMainBlockContainer"] {
            max-width: 520px;
            margin: 0 auto;
            padding-left: 16px;
            padding-right: 16px;
            padding-bottom: 100px; /* 하단 고정 네비게이션(pb-28=112px 상당)에 가려지지 않도록 */
        }

        /* 홈 상단 히어로 배너 — Lovable 원본(rounded-b-[2rem] bg-gradient-hero
           px-5 pt-8 pb-7 text-primary-foreground)과 동일. 그라데이션은 실제 사이트 CSS에서
           뽑은 --gradient-hero 값(oklch 58%/.14/200 → 52%/.13/235)을 hex로 변환한 것.
           좌우로만 -16px bleed해서 520px 프레임 안에서 모서리까지 꽉 차게 함. */
        .injoy-hero {
            margin: -16px -16px 0;
            padding: 32px 20px 28px;
            border-radius: 0 0 32px 32px;
            background: linear-gradient(160deg, #008b91, #00729f);
            color: #f8fdfd;
        }
        .injoy-hero-title { font-size: 20px; font-weight: 800; margin-bottom: 6px; line-height: 1.3; }
        .injoy-hero-sub { font-size: 13px; opacity: 0.85; }
        .injoy-hero-note {
            margin-top: 12px;
            background: rgba(255,255,255,0.16);
            border-radius: 14px;
            padding: 10px 14px;
            font-size: 12.5px;
            line-height: 1.4;
        }
        .injoy-hero-warn {
            margin-top: 8px;
            font-size: 12px;
            opacity: 0.9;
        }

        /* 섹션 사이 여백 — Lovable의 pt-7(28px)과 동일. 실제 컨텐츠를 감싸는 대신
           (st.markdown 호출마다 별도 DOM 조각이라 감싸기가 안 먹힘) 구분선 대신 쓰는 spacer */
        .injoy-spacer { height: 28px; }

        /* "당신을 위한 추천" 카드 — Lovable 실제 카드 구조 그대로:
           size-11(44px) 아이콘 버블(bg-secondary #F6EDE0) + 제목/설명 + tip 배지(#D5F4E2/#0B764D) + 화살표.
           rounded-3xl = radius(17.6px)+12px = 29.6px, gap-3=12px, p-4=16px, space-y-2.5=10px */
        .injoy-tip-card {
            display: grid;
            grid-template-columns: 44px 1fr auto;
            align-items: center;
            gap: 12px;
            background: #FFFFFF;
            border-radius: 29.6px;
            box-shadow: 0 8px 24px -12px rgba(92,65,44,0.25);
            padding: 16px;
            margin-bottom: 10px;
        }
        .injoy-tip-icon {
            width: 44px; height: 44px;
            border-radius: 25.6px;
            background: #F6EDE0;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
        }
        .injoy-tip-title { font-weight: 700; color: #2A1B11; font-size: 15px; margin-bottom: 2px; }
        .injoy-tip-desc { color: #76695D; font-size: 12.5px; line-height: 1.4; margin-bottom: 6px; }
        .injoy-tip-badge {
            display: inline-flex; align-items: center; gap: 4px;
            background: #D5F4E2; color: #0B764D;
            font-size: 11px; font-weight: 700;
            padding: 4px 10px; border-radius: 999px;
        }
        .injoy-tip-chevron { color: #C9BFB2; font-size: 20px; }
        /* "공식 정보" 배지 — 생활 팁(mint)과 구분되는 primary 톤 변형 */
        .injoy-tip-badge.injoy-badge-official { background: #E3F5F5; color: #007A7A; }

        /* 생활가이드 탭 헤더 — Lovable 원본(px-5 pt-6 pb-3) */
        .injoy-guide-header { padding: 20px 0 4px; margin: 0 -16px; padding-left: 20px; padding-right: 20px; }
        .injoy-guide-title { font-size: 20px; font-weight: 800; color: #2A1B11; }
        .injoy-guide-sub { font-size: 12.5px; color: #76695D; margin-top: 4px; }

        /* 생활가이드 필터 칩 — 가로 스크롤 pill 버튼 행. .st-key-guide_filters로 스코핑해서
           카테고리 그리드(tertiary 버튼)나 다른 버튼 스타일과 절대 안 겹치게 함.
           주의: Streamlit은 st-key-<key> 클래스와 data-testid="stHorizontalBlock"을
           "같은" 엘리먼트에 같이 붙인다 (자식이 아님!). 그래서 셀렉터에 공백을 넣으면
           (자손 선택자) 절대 매칭이 안 된다 — 이게 스크롤이 안 먹혔던 진짜 원인.
           .st-key-X[data-testid=...] 처럼 공백 없이 같은 엘리먼트로 셀렉팅해야 함. */
        .st-key-guide_filters.st-key-guide_filters[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            gap: 8px !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            padding: 6px 2px 10px !important;
            -webkit-overflow-scrolling: touch;
        }
        .st-key-guide_filters.st-key-guide_filters [data-testid="stElementContainer"],
        .st-key-guide_filters.st-key-guide_filters [data-testid="stColumn"] {
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: 0 !important;
            display: inline-block !important;
        }
        .st-key-guide_filters.st-key-guide_filters button {
            border-radius: 999px !important;
            border: 1px solid #E3DDD3 !important;
            background: #FFFFFF !important;
            color: #4E270D !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 8px 16px !important;
            white-space: nowrap !important;
            box-shadow: none !important;
            min-height: auto !important;
            width: auto !important;
        }
        .st-key-guide_filters.st-key-guide_filters button[data-testid="stBaseButton-primary"] {
            background: #008282 !important;
            border-color: #008282 !important;
            color: #FFFFFF !important;
        }

        /* 생활가이드 목록의 개별 카드 — 실제 클릭 가능한 st.button으로 구현.
           카드마다 key가 달라서(guidecard_0, guidecard_1 ...) 공통 클래스가 없기 때문에,
           class 속성에 "st-key-guidecard_"가 "포함"되는지로 스코핑한다
           ([class*=...]는 부분 문자열 매칭이라 접두어가 같은 모든 카드에 한 번에 적용됨). */
        [data-testid="stElementContainer"][class*="st-key-guidecard_"] button {
            background: #FFFFFF !important;
            border: none !important;
            border-radius: 29.6px !important;
            box-shadow: 0 8px 24px -12px rgba(92,65,44,0.25) !important;
            padding: 16px 40px 16px 16px !important;
            text-align: left !important;
            white-space: pre-line !important;
            min-height: auto !important;
            width: 100% !important;
            position: relative !important;
            color: #2A1B11 !important;
            font-size: 12.5px !important;
            font-weight: 500 !important;
            line-height: 1.5 !important;
        }
        [data-testid="stElementContainer"][class*="st-key-guidecard_"] {
            margin-bottom: 10px !important;
        }
        [data-testid="stElementContainer"][class*="st-key-guidecard_"] button::first-line {
            font-size: 15px !important;
            font-weight: 800 !important;
        }
        [data-testid="stElementContainer"][class*="st-key-guidecard_"] button::after {
            content: '›';
            position: absolute;
            right: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: #C9BFB2;
            font-size: 20px;
        }
        [data-testid="stElementContainer"][class*="st-key-guidecard_"] button:hover {
            box-shadow: 0 10px 28px -10px rgba(92,65,44,0.35) !important;
        }

        /* 생활가이드 상세 페이지 */
        .injoy-detail-icon-row { display: flex; align-items: center; gap: 10px; margin: 4px 0 14px; }
        .injoy-detail-icon { font-size: 40px; line-height: 1; }
        .injoy-detail-title { font-size: 23px; font-weight: 800; color: #2A1B11; margin-bottom: 8px; line-height: 1.35; }
        .injoy-detail-sub { font-size: 13.5px; color: #76695D; margin-bottom: 18px; line-height: 1.55; }

        .injoy-detail-card {
            background: #FFFFFF;
            border-radius: 29.6px;
            box-shadow: 0 8px 24px -12px rgba(92,65,44,0.25);
            padding: 20px;
            margin-bottom: 14px;
        }
        .injoy-detail-card-title { font-size: 15px; font-weight: 800; color: #2A1B11; margin-bottom: 12px; }
        .injoy-detail-card-body { font-size: 13px; color: #4E3B2E; line-height: 1.6; }

        .injoy-step-row { display: flex; gap: 12px; margin-bottom: 12px; align-items: flex-start; }
        .injoy-step-row:last-child { margin-bottom: 0; }
        .injoy-step-num {
            flex-shrink: 0; width: 26px; height: 26px; border-radius: 50%;
            background: #E3F5F5; color: #007A7A; font-weight: 800; font-size: 12.5px;
            display: flex; align-items: center; justify-content: center;
        }
        .injoy-step-text { font-size: 13px; color: #4E3B2E; line-height: 1.6; padding-top: 2px; }

        .injoy-service-card { background: #D5F4E2; border-radius: 20px; padding: 18px; margin-bottom: 14px; }
        .injoy-service-title { font-size: 14px; font-weight: 800; color: #0B764D; margin-bottom: 6px; }
        .injoy-service-body { font-size: 12.5px; color: #0B764D; line-height: 1.5; opacity: 0.9; }

        .injoy-warning-card {
            background: #FEE3C5; border-radius: 20px; padding: 16px 18px; margin-bottom: 20px;
            display: flex; gap: 10px; align-items: flex-start;
        }
        .injoy-warning-title { font-size: 13.5px; font-weight: 800; color: #4E270D; margin-bottom: 4px; }
        .injoy-warning-body { font-size: 12.5px; color: #4E270D; line-height: 1.5; opacity: 0.9; }

        .injoy-related-title { font-size: 17px; font-weight: 800; color: #2A1B11; margin-bottom: 2px; }
        .injoy-related-sub { font-size: 12px; color: #76695D; margin-bottom: 12px; }
        .injoy-detail-footer { font-size: 11px; color: #B0A99C; margin: 18px 0 4px; line-height: 1.5; }

        /* 상세 페이지 액션 버튼 행 (저장 / AI에게 질문 / 가까운 도움처) — 필터 칩과
           같은 가로 스크롤 패턴, st.container(key="detail_actions")로 스코핑 */
        .st-key-detail_actions.st-key-detail_actions[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 8px !important;
            overflow-x: auto !important;
            width: 100% !important;
            padding: 4px 2px 20px !important;
        }
        .st-key-detail_actions [data-testid="stElementContainer"],
        .st-key-detail_actions [data-testid="stColumn"] {
            flex: 0 0 auto !important;
        }
        .st-key-detail_actions button {
            border-radius: 999px !important;
            border: 1px solid #E3DDD3 !important;
            background: #FFFFFF !important;
            color: #4E270D !important;
            font-size: 12.5px !important;
            font-weight: 700 !important;
            padding: 8px 14px !important;
            white-space: nowrap !important;
            box-shadow: none !important;
            min-height: auto !important;
            width: auto !important;
        }
        .st-key-detail_actions button[data-testid="stBaseButton-primary"] {
            background: #008282 !important;
            border-color: #008282 !important;
            color: #FFFFFF !important;
        }

        /* 뒤로가기(← 생활가이드) 버튼 — 화살표만 흐리게, 텍스트는 진하게 */
        [data-testid="stElementContainer"][class*="st-key-guideback_"] button {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            padding: 4px 0 !important;
            color: #2A1B11 !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            min-height: auto !important;
        }

        /* 하단 고정 네비게이션 — Lovable 원본(fixed bottom-0 left-1/2 w-full max-w-[520px]
           -translate-x-1/2 border-t bg-card/95 backdrop-blur)과 동일한 위치·크기.
           st.container(key="bottom_nav")로 명확하게 스코핑 — 카테고리 그리드 등
           다른 st.columns() 블록에는 절대 영향 없음. (:last-of-type은 Streamlit이
           각 요소를 별도 wrapper로 감싸서 "그 wrapper 안에서 마지막"이면 전부 걸려버려
           카테고리 그리드까지 같이 고정/축소되는 버그가 있었음 — 그래서 폐기함) */
        .st-key-bottom_nav {
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 520px;
            margin: 0;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(8px);
            border-top: 1px solid #E3DDD3;
            padding: 8px 16px 10px;
            z-index: 40;
        }
        .st-key-bottom_nav[data-testid="stHorizontalBlock"] {
            gap: 0 !important;
        }
        .st-key-bottom_nav [data-testid="stColumn"],
        .st-key-bottom_nav [data-testid="stElementContainer"] {
            flex: 1 1 0;
        }
        .st-key-bottom_nav button {
            width: 100% !important;
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            color: #76695D !important;
            font-weight: 600 !important;
            font-size: 10px !important;
            line-height: 1.3 !important;
            white-space: pre-line !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 4px 0 !important;
            min-height: auto !important;
        }
        .st-key-bottom_nav button::first-line {
            font-size: 22px !important;
        }
        .st-key-bottom_nav button[data-testid="stBaseButton-primary"] {
            color: #008282 !important;
        }
        /* 챗봇 탭에서 Streamlit 기본 채팅 입력창이 하단 네비게이션에 가리지 않도록 살짝 띄움 */
        [data-testid="stChatInput"] {
            bottom: 66px !important;
            max-width: 520px !important;
        }

        /* 일반 버튼(뒤로가기 등) 스타일 */
        div[data-testid="stButton"] button {
            border-radius: 12px;
            border: 1px solid #E3DDD3;
            font-weight: 600;
            color: #2A1B11;
        }

        /* 정보 카드(FAQ 상세, 추천 등) */
        .injoy-card {
            background: #FFFFFF;
            border-radius: 25.6px;
            box-shadow: 0 8px 24px -12px rgba(92,65,44,0.25);
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .injoy-card-title { font-weight: 700; margin-bottom: 4px; color: #2A1B11; }
        .injoy-card-desc { color: #76695D; font-size: 0.9rem; }

        /* 섹션 제목 */
        .injoy-section-title {
            font-size: 20px;
            font-weight: 700;
            color: #2A1B11;
            margin-bottom: 14px;
        }

        /* 3x3 카테고리 카드 그리드 버튼 — Lovable 실제 카드에서 뽑은 정확한 값
           (devtools 검사 결과): 125x74px 카드, p-3(12px), 아이콘 text-2xl(24px),
           라벨 text-[11px] font-bold leading-tight, mt-1(4px).
           type="tertiary"로 지정해서 stBaseButton-tertiary 로만 스코핑 —
           뒤로가기/프로필 버튼(secondary)에는 영향 없음. 너비·높이는 여전히 안 건드림. */
        div[data-testid="stButton"] button[data-testid="stBaseButton-tertiary"] {
            background: #FFFFFF;
            border: none;
            border-radius: 25.6px;
            box-shadow: 0 8px 24px -12px rgba(92,65,44,0.25);
            padding: 12px;
            font-weight: 700;
            font-size: 11px;
            line-height: 1.25;
            white-space: pre-line;
            color: #2A1B11;
            min-height: 74px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        /* 그리드 칸 사이 여백을 Lovable 원본(gap-2.5 = 10px)과 맞춤 */
        div[data-testid="stHorizontalBlock"] {
            gap: 10px;
        }
        div[data-testid="stButton"] button[data-testid="stBaseButton-tertiary"]::first-line {
            font-size: 24px;
        }
        div[data-testid="stButton"] button[data-testid="stBaseButton-tertiary"]:hover {
            box-shadow: 0 10px 28px -10px rgba(92,65,44,0.35);
            color: #2A1B11;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_category_grid():
    """생활가이드 3x3 카테고리 카드 그리드. 카드 클릭 시 상세 화면으로 전환.
    st.columns()의 기본 균등폭 동작만 그대로 쓰고, 폭/높이는 커스텀 CSS로 건드리지 않는다."""
    st.markdown('<div class="injoy-section-title">생활가이드</div>', unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    for i, cat in enumerate(CATEGORY_GRID):
        with cols[i % 3]:
            if st.button(
                f"{cat['icon']}\n{cat['label']}",
                key=f"catbtn_{cat['id']}",
                width="stretch",
                type="tertiary",
            ):
                st.session_state.selected_group = cat["id"]
                st.rerun()


def render_home_category_grid():
    """홈 탭용 카테고리 3x3 그리드. render_category_grid와 동일한 방식이지만
    생활가이드 탭의 selected_group과 분리된 별도 상태(home_selected_group)를 써서
    두 탭이 서로 영향을 주지 않게 한다."""
    st.markdown('<div class="injoy-section-title">카테고리</div>', unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    for i, cat in enumerate(CATEGORY_GRID):
        with cols[i % 3]:
            if st.button(
                f"{cat['icon']}\n{cat['label']}",
                key=f"homecatbtn_{cat['id']}",
                width="stretch",
                type="tertiary",
            ):
                st.session_state.home_selected_group = cat["id"]
                st.rerun()


# ── 데이터 로드 (캐싱해서 매번 다시 안 읽도록) ──────────────────────────
@st.cache_resource
def load_all_data():
    faq_data = load_faq_data()
    faq_embeddings = load_embeddings() if os.path.exists("data/faq_embeddings.npy") else None
    dept_data = load_dept_routing()
    return faq_data, faq_embeddings, dept_data


faq_data, faq_embeddings, dept_data = load_all_data()


# ── 온보딩 (최초 1회, 세션 기반 — 로그인/DB 없이 st.session_state로만 유지) ──
def render_onboarding():
    # 언어 선택 — 페이지에서 가장 먼저 보이도록 최상단에, 좁게 왼쪽 정렬
    lang_col, _spacer = st.columns([1, 3])
    with lang_col:
        language_label = st.selectbox("🌐 언어", LANGUAGE_LABELS, index=0, key="onboarding_language")

    st.title("인조이 🏘️")
    st.subheader("환영해요! 몇 가지만 알려주세요")
    st.caption("입력한 정보는 이 세션에서만 사용되고, 로그인 없이 브라우저 새로고침 전까지만 유지돼요.")

    with st.form("onboarding_form"):
        st.markdown("**필수 정보**")
        nickname = st.text_input("닉네임 *")
        age = st.number_input("나이 *", min_value=1, max_value=120, step=1, value=25)
        region = st.selectbox("거주지역 (인천) *", list(dept_data.keys()))
        duration = st.selectbox("체류기간 *", ONBOARD_DURATIONS)
        has_arc = st.radio("외국인등록증을 가지고 있나요? *", YES_NO, horizontal=True)

        with st.expander("선택 정보 (몰라도, 안 채워도 괜찮아요)"):
            name = st.text_input("이름")
            home_country = st.text_input("본국")
            is_incheon_resident = st.radio("현재 인천에 거주 중인가요?", YES_NO, horizontal=True)
            purpose = st.selectbox("체류목적", ONBOARD_PURPOSES)
            phone_number = st.text_input("한국 전화번호 (있으면 입력)")
            has_korean_account = st.radio("한국 계좌가 있나요?", YES_NO, horizontal=True)

        submitted = st.form_submit_button("시작하기")

    if submitted:
        if not nickname.strip():
            st.warning("닉네임을 입력해주세요.")
            return
        language = language_label.split(" ", 1)[1]
        language_flag = language_label.split(" ", 1)[0]
        st.session_state.profile = {
            "nickname": nickname.strip(),
            "age": int(age),
            "region": region,
            "duration": duration,
            "has_arc": has_arc == "예",
            "name": name.strip(),
            "home_country": home_country.strip(),
            "is_incheon_resident": is_incheon_resident == "예",
            "purpose": purpose,
            "phone_number": phone_number.strip(),
            "has_korean_phone": bool(phone_number.strip()),
            "has_korean_account": has_korean_account == "예",
            "language": language,
            "language_flag": language_flag,
        }
        st.rerun()


if "profile" not in st.session_state:
    # 온보딩도 독립된 엔드포인트(/onboarding)로 분리 — st.navigation을 쓰면
    # Streamlit이 자동으로 URL 라우팅을 붙여준다. position="hidden"이라
    # 기본 사이드바 네비 UI는 안 보이고, 온보딩 화면만 그대로 그려진다.
    onboarding_nav = st.navigation(
        [st.Page(render_onboarding, title="온보딩", url_path="onboarding", default=True)],
        position="hidden",
    )
    onboarding_nav.run()
    st.stop()

profile = st.session_state.profile


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

    answer_language = st.session_state.get("profile", {}).get("language", "사용자가 사용한 언어")

    if faq_embeddings is not None and is_covered_by_faq(top_score):
        # FAQ 문서 기반 답변
        context = "\n".join(f"- {d['question']} {d['answer']}" for d in top_docs)
        system_prompt = f"""너는 인천 거주 외국인을 돕는 다국어 안내 챗봇이야. {answer_language}로 답해.
아래 참고 문서에 근거해서만 답변해. 문서에 없는 내용은 추측하지 마.

[참고 문서]
{context}"""
        source = "FAQ"

    elif risk == "저위험":
        # GPT 일반지식으로 답변 (교통/통신/생활꿀팁 등)
        system_prompt = f"너는 인천 거주 외국인을 돕는 다국어 안내 챗봇이야. {answer_language}로, 한국 생활에 대한 일반적인 지식을 바탕으로 친절하게 답해."
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


# ── 화면 구성 (5탭: 홈 / 생활가이드 / AI에게 질문 / 내주변 / 마이라이프) ──────
inject_css()
st.title("인조이 🏘️")

with st.sidebar:
    st.caption(
        f"{profile.get('language_flag', '')} {profile['nickname']}님 · {profile['region']} · 체류기간 {profile['duration']}"
    )
    if st.button("프로필 다시 설정"):
        del st.session_state["profile"]
        st.rerun()


def render_category_detail(cat: dict, state_key: str = "selected_group"):
    """카테고리 클릭 → 카드 리스트 화면 (기획안 3장: 뒤로가기 + 챗봇 CTA).
    state_key로 어느 탭(홈/생활가이드)의 선택 상태인지 구분해서 서로 독립적으로 동작한다."""
    if st.button("← 뒤로가기", key=f"back_{state_key}"):
        del st.session_state[state_key]
        st.rerun()

    st.subheader(f"{cat['icon']} {cat['label']}")

    if not cat["categories"]:
        # 긴급상황: FAQ 매칭 없이 고정 연락처 안내
        for icon, title, desc in EMERGENCY_INFO:
            st.markdown(
                f'<div class="injoy-card"><div class="injoy-card-title">{icon} {title}</div>'
                f'<div class="injoy-card-desc">{desc}</div></div>',
                unsafe_allow_html=True,
            )
    else:
        items = [d for d in faq_data if d["category"] in cat["categories"]]
        if not items:
            st.caption("아직 등록된 정보가 없어요.")
        for item in items:
            st.markdown(
                f'<div class="injoy-card"><div class="injoy-card-title">{item["question"]}</div>'
                f'<div class="injoy-card-desc">{item["answer"]}</div></div>',
                unsafe_allow_html=True,
            )

    st.info("원하는 답을 못 찾으셨나요? 하단의 **AI에게 질문** 탭에서 자유롭게 물어보세요!")


def render_guide_card(icon: str, title: str, desc: str, badge: str = "tip"):
    """'당신을 위한 추천' / 생활가이드 목록 카드 — Lovable 원본 구조
    (아이콘 버블 + 텍스트 + 배지 + 화살표) 그대로. badge="tip"(생활 팁, mint) 또는
    badge="official"(공식 정보, teal) 두 종류를 그대로 재현."""
    if badge == "official":
        badge_html = '<span class="injoy-tip-badge injoy-badge-official">✓ 공식 정보</span>'
    else:
        badge_html = '<span class="injoy-tip-badge">✦ 생활 팁</span>'
    st.markdown(
        f'<div class="injoy-tip-card">'
        f'<span class="injoy-tip-icon">{icon}</span>'
        f'<div><div class="injoy-tip-title">{title}</div>'
        f'<div class="injoy-tip-desc">{desc}</div>'
        f'{badge_html}</div>'
        f'<span class="injoy-tip-chevron">›</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_home():
    purpose_note = f" · {profile['purpose']}" if profile.get("purpose") else ""
    dept_note = get_department_info(profile["region"], dept_data)

    hero_html = (
        '<div class="injoy-hero">'
        f'<div class="injoy-hero-title">{profile["nickname"]}님, 인천에 오신 것을 환영해요</div>'
        f'<div class="injoy-hero-sub">{profile["region"]} · 체류기간 {profile["duration"]}{purpose_note}</div>'
    )
    if dept_note:
        hero_html += f'<div class="injoy-hero-note">📍 {dept_note}</div>'
    if not profile.get("has_arc"):
        hero_html += '<div class="injoy-hero-warn">⚠️ 외국인등록증이 없으신 경우, 관련 절차는 AI에게 질문 탭에서 물어보세요.</div>'
    hero_html += "</div>"
    st.markdown(hero_html, unsafe_allow_html=True)

    st.markdown('<div class="injoy-spacer"></div>', unsafe_allow_html=True)

    if "home_selected_group" in st.session_state:
        selected = next(c for c in CATEGORY_GRID if c["id"] == st.session_state.home_selected_group)
        render_category_detail(selected, state_key="home_selected_group")
    else:
        render_home_category_grid()

        st.markdown('<div class="injoy-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="injoy-section-title">당신을 위한 추천</div>', unsafe_allow_html=True)
        for icon, title, desc, _cat_id in HOME_TIPS:
            render_guide_card(icon, title, desc, badge="tip")
        st.caption("더 많은 정보는 **생활가이드** 탭에서 카테고리별로 볼 수 있어요.")


# 생활가이드 필터 칩 목록: "전체" + CATEGORY_GRID 각 카테고리
GUIDE_FILTERS = [("all", "🗂️", "전체")] + [(c["id"], c["icon"], c["label"]) for c in CATEGORY_GRID]


def build_guide_items() -> list[dict]:
    """생활가이드 목록에 나오는 모든 항목(생활 팁 + FAQ 공식 정보)을 하나의 리스트로 합친다.
    각 항목에 고유 id를 부여해서 카드 클릭 → 상세 페이지 라우팅에 쓴다."""
    items = []
    for idx, (icon, title, desc, cat_id) in enumerate(HOME_TIPS):
        items.append({
            "id": f"tip-{idx}", "icon": icon, "title": title, "desc": desc,
            "badge": "tip", "cat_id": cat_id,
        })
    idx = 0
    for cat in CATEGORY_GRID:
        for item in faq_data:
            if item["category"] in cat["categories"]:
                items.append({
                    "id": f"faq-{idx}", "icon": cat["icon"], "title": item["question"],
                    "desc": item["answer"], "badge": "official", "cat_id": cat["id"],
                })
                idx += 1
    return items


GUIDE_ITEMS = build_guide_items()
GUIDE_ITEMS_BY_ID = {it["id"]: it for it in GUIDE_ITEMS}


def render_guide_item_card(item: dict) -> bool:
    """생활가이드 목록의 클릭 가능한 카드. 실제 st.button이라 진짜로 클릭돼서 상세 페이지로 넘어간다."""
    badge_icon = "✦" if item["badge"] == "tip" else "✓"
    badge_label = "생활 팁" if item["badge"] == "tip" else "공식 정보"
    label = f"{item['icon']} **{item['title']}**\n{badge_icon} {badge_label} · {item['desc']}"
    return st.button(label, key=f"guidecard_{item['id']}", type="tertiary", width="stretch")


def split_into_steps(text: str) -> list[str]:
    """FAQ 답변 텍스트를 문장 단위로 쪼개서 번호가 매겨진 단계처럼 보여주기 위한 헬퍼.
    새로운 내용을 지어내는 게 아니라 실제 답변 텍스트를 그대로 문장 단위로 재구성하는 것."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    return parts or [text.strip()]


def render_guide_detail(item: dict):
    """생활가이드 개별 항목 상세 페이지 — Lovable 원본 구성 그대로:
    뒤로가기 → 아이콘+배지 → 제목/부제 → 액션 버튼 3개 → 왜 중요한가요 → 이렇게 하면 돼요
    → (있으면) 도움이 되는 서비스 → 주의할 점 → 관련 정보 → 하단 안내 문구."""
    if st.button("← 생활가이드", key=f"guideback_{item['id']}"):
        del st.session_state["guide_detail_id"]
        st.rerun()

    badge_icon = "✦" if item["badge"] == "tip" else "✓"
    badge_label = "생활 팁" if item["badge"] == "tip" else "공식 정보"
    badge_class = "" if item["badge"] == "tip" else "injoy-badge-official"
    st.markdown(
        f'<div class="injoy-detail-icon-row">'
        f'<span class="injoy-detail-icon">{item["icon"]}</span>'
        f'<span class="injoy-tip-badge {badge_class}">{badge_icon} {badge_label}</span>'
        f'</div>'
        f'<div class="injoy-detail-title">{item["title"]}</div>'
        f'<div class="injoy-detail-sub">{item["desc"][:60]}{"..." if len(item["desc"]) > 60 else ""}</div>',
        unsafe_allow_html=True,
    )

    with st.container(key="detail_actions", horizontal=True, gap=None):
        saved_ids = st.session_state.setdefault("saved_guide_ids", set())
        is_saved = item["id"] in saved_ids
        if st.button(
            f"{'🔖' if is_saved else '📑'} {'저장됨' if is_saved else '저장'}",
            key="detailaction_save",
            type="primary" if is_saved else "secondary",
        ):
            if is_saved:
                saved_ids.discard(item["id"])
                st.toast("저장을 취소했어요.")
            else:
                saved_ids.add(item["id"])
                st.toast("저장했어요! 마이라이프 탭에서 모아볼 수 있어요.", icon="🔖")
            st.rerun()
        if st.button("❓ AI에게 질문", key="detailaction_ask"):
            st.session_state.chat_prefill_topic = item["title"]
            st.switch_page(pages_by_id["chat"])
        if st.button("📍 가까운 도움처", key="detailaction_nearby"):
            st.switch_page(pages_by_id["nearby"])

    # 왜 중요한가요 — 일반적인 맥락 설명 (구체적 사실을 지어내지 않고, 안내 성격의 문구)
    why_text = (
        "생활하면서 미리 알아두면 시간과 시행착오를 줄일 수 있는 정보예요."
        if item["badge"] == "tip"
        else "잘못 알고 있으면 시간과 비용을 낭비하거나 다시 절차를 밟아야 할 수 있어요."
    )
    st.markdown(
        f'<div class="injoy-detail-card">'
        f'<div class="injoy-detail-card-title">왜 중요한가요</div>'
        f'<div class="injoy-detail-card-body">{why_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 이렇게 하면 돼요 — 실제 FAQ/팁 답변 내용을 문장 단위로 재구성 (내용을 새로 지어내지 않음)
    steps = split_into_steps(item["desc"])
    steps_html = "".join(
        f'<div class="injoy-step-row"><span class="injoy-step-num">{i}</span>'
        f'<span class="injoy-step-text">{step}</span></div>'
        for i, step in enumerate(steps, start=1)
    )
    st.markdown(
        f'<div class="injoy-detail-card">'
        f'<div class="injoy-detail-card-title">이렇게 하면 돼요</div>'
        f'{steps_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 도움이 되는 서비스 — 실제 부서 라우팅 데이터가 있을 때만 표시 (없는 서비스명 지어내지 않음)
    dept_note = get_department_info(profile["region"], dept_data)
    if dept_note and item["cat_id"] in ("admin", "medical", "job"):
        st.markdown(
            f'<div class="injoy-service-card">'
            f'<div class="injoy-service-title">도움이 되는 서비스</div>'
            f'<div class="injoy-service-body">📍 {dept_note}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    warn_text = (
        "실제 상황에 따라 다를 수 있어요. 최신 정보는 직접 한 번 더 확인해 주세요."
        if item["badge"] == "tip"
        else "안내를 위한 요약이에요. 정확한 사항은 관련 기관 공식 채널에서 다시 확인해 주세요."
    )
    st.markdown(
        f'<div class="injoy-warning-card">'
        f'<span>⚠️</span>'
        f'<div><div class="injoy-warning-title">주의할 점</div>'
        f'<div class="injoy-warning-body">{warn_text}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    related = [g for g in GUIDE_ITEMS if g["cat_id"] == item["cat_id"] and g["id"] != item["id"]][:2]
    if related:
        st.markdown(
            '<div class="injoy-related-title">관련 정보</div>'
            '<div class="injoy-related-sub">이것도 알아두면 좋아요</div>',
            unsafe_allow_html=True,
        )
        for rel in related:
            if render_guide_item_card(rel):
                st.session_state.guide_detail_id = rel["id"]
                st.rerun()

    st.markdown(
        f'<div class="injoy-detail-footer">최신 정보는 반드시 공식 기관에서 확인해 주세요. '
        f'({len(GUIDE_ITEMS)}개 항목 · 샘플 데이터)</div>',
        unsafe_allow_html=True,
    )


def render_guide():
    """생활가이드 탭 — Lovable 원본처럼 상단 필터 칩(가로 스크롤) + 카드 리스트 구조.
    카드를 클릭하면 상세 페이지(render_guide_detail)로 전환된다.
    카테고리 3x3 미니 그리드(render_category_grid)는 홈 탭 전용으로 남겨두고,
    이 탭은 완전히 새로운 '전체 목록 + 필터 + 상세' 화면으로 만든다."""
    detail_id = st.session_state.get("guide_detail_id")
    if detail_id and detail_id in GUIDE_ITEMS_BY_ID:
        render_guide_detail(GUIDE_ITEMS_BY_ID[detail_id])
        return

    st.markdown(
        '<div class="injoy-guide-header">'
        '<div class="injoy-guide-title">생활가이드</div>'
        '<div class="injoy-guide-sub">긴 문서가 아니라, 실행 가능한 단계로 정리했어요.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.session_state.setdefault("guide_filter", "all")

    with st.container(key="guide_filters", horizontal=True, gap=None):
        for filter_id, filter_icon, filter_label in GUIDE_FILTERS:
            is_active = st.session_state.guide_filter == filter_id
            if st.button(
                f"{filter_icon} {filter_label}",
                key=f"guidefilter_{filter_id}",
                type="primary" if is_active else "secondary",
            ):
                st.session_state.guide_filter = filter_id
                st.rerun()

    active_filter = st.session_state.guide_filter
    shown = 0
    for item in GUIDE_ITEMS:
        if active_filter in ("all", item["cat_id"]):
            if render_guide_item_card(item):
                st.session_state.guide_detail_id = item["id"]
                st.rerun()
            shown += 1

    if shown == 0:
        st.caption("아직 등록된 정보가 없어요.")


def render_chat():
    st.caption(f"궁금한 걸 자유롭게 물어보세요 ({profile.get('language', '다국어 지원')})")

    prefill_topic = st.session_state.pop("chat_prefill_topic", None)
    if prefill_topic:
        st.info(f"💡 이렇게 물어보면 돼요: \"{prefill_topic}에 대해 더 자세히 알려줘\"")

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


def render_nearby():
    st.subheader("내주변")
    st.caption(f"{profile['region']} 기준으로 준비 중이에요.")
    st.info(
        "🚧 Google Places API 연동 예정 (병원·은행 등 리스트 + 지도 링크). "
        "외국인지원센터·노동상담소 등 특화기관은 팀 조사 데이터로 보완할 계획이에요."
    )


def render_mylife():
    st.subheader("마이라이프")
    st.caption(f"체류기간 {profile['duration']} 기준 체크리스트 · 스크랩")

    saved_ids = st.session_state.get("saved_guide_ids", set())
    saved_items = [GUIDE_ITEMS_BY_ID[i] for i in saved_ids if i in GUIDE_ITEMS_BY_ID]
    if saved_items:
        st.markdown('<div class="injoy-section-title">저장한 생활가이드</div>', unsafe_allow_html=True)
        for item in saved_items:
            if render_guide_item_card(item):
                st.session_state.guide_detail_id = item["id"]
                st.switch_page(pages_by_id["guide"])
        st.markdown('<div class="injoy-spacer"></div>', unsafe_allow_html=True)

    st.info(
        "🚧 체류기간 기준 체크리스트는 준비 중이에요. "
        "(로그인 없이 st.session_state로만 유지 — 새로고침하면 초기화됩니다)"
    )


# ── 5개 탭을 진짜 별도 엔드포인트(URL)로 분리 ────────────────────────
# st.navigation + st.Page를 쓰면 각 탭이 실제 URL(/home, /guide, /chat, /nearby,
# /mylife)을 가지게 된다 — 새로고침해도 같은 탭 유지, 북마크/공유, 브라우저
# 뒤로가기까지 전부 됨. position="hidden"으로 기본 사이드바 네비 UI는 숨기고,
# 화면 하단의 커스텀 네비(Lovable 스타일)에서 st.switch_page로 이동시킨다.
NAV_ITEMS = [
    ("home", "홈", "🏠"),
    ("guide", "생활가이드", "📖"),
    ("chat", "AI에게 질문", "❓"),
    ("nearby", "내주변", "📍"),
    ("mylife", "마이라이프", "👤"),
]
PAGE_RENDERERS = {
    "home": render_home,
    "guide": render_guide,
    "chat": render_chat,
    "nearby": render_nearby,
    "mylife": render_mylife,
}

pages_by_id = {
    tab_id: st.Page(
        PAGE_RENDERERS[tab_id],
        title=label,
        icon=icon,
        url_path=tab_id,
        default=(tab_id == "home"),
    )
    for tab_id, label, icon in NAV_ITEMS
}

current_page = st.navigation(list(pages_by_id.values()), position="hidden")
current_page.run()

with st.container(key="bottom_nav", horizontal=True, gap=None):
    for tab_id, label, icon in NAV_ITEMS:
        is_active = current_page.url_path == tab_id
        if st.button(
            f"{icon}\n{label}",
            key=f"nav_{tab_id}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.switch_page(pages_by_id[tab_id])
