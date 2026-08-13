"""내주변 탭 — 지도, 카테고리 필터, 도움처 카드."""
import html
import json
from pathlib import Path
from urllib.parse import quote

import folium
import streamlit as st
from streamlit_folium import st_folium

import common


profile = common.require_profile()
CATEGORIES = ["전체", "외국인 지원", "노동 상담", "의료", "한국어", "행정 서비스", "교통"]
INCHEON_CENTER = (37.4563, 126.7052)


@st.cache_data
def load_places():
    path = Path(__file__).parents[1] / "data" / "nearby_places.json"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def safe(value):
    return html.escape(str(value))


places = load_places()
st.session_state.setdefault("nearby_category", "전체")
active_category = st.session_state.nearby_category
filtered_places = [p for p in places if active_category == "전체" or p["category"] == active_category]

# 페이지 파일은 Streamlit이 변경 즉시 다시 실행하므로, 실행 중 common 모듈 캐시와
# 무관하게 내 주변 화면의 스타일이 항상 최신 상태로 적용된다.
st.markdown(
    """
    <style>
    /* app.py의 공용 타이틀은 Lovable 모바일 화면에 없으므로 이 탭에서만 숨긴다. */
    [data-testid="stMainBlockContainer"] h1 { display:none !important; }
    .injoy-nearby-header { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; padding:18px 4px 14px; }
    .injoy-nearby-title { font-size:22px; font-weight:800; color:#2A1B11; line-height:1.25; }
    .injoy-nearby-sub { margin-top:5px; font-size:13px; color:#76695D; }
    .injoy-sample-badge { display:inline-flex; flex-shrink:0; padding:5px 10px; border-radius:999px; background:#F4F1EB; border:1px dashed #DDD5CA; color:#76695D; font-size:10.5px; font-weight:700; }
    .st-key-nearby_map_wrap { overflow:hidden; border-radius:29px; margin-bottom:12px; }
    .st-key-nearby_map_wrap iframe { display:block; border:0; border-radius:29px; }
    .st-key-nearby_filters.st-key-nearby_filters[data-testid="stHorizontalBlock"] { display:flex !important; flex-wrap:nowrap !important; gap:8px !important; overflow-x:auto !important; overflow-y:hidden !important; padding:4px 0 14px !important; }
    .st-key-nearby_filters [data-testid="stElementContainer"], .st-key-nearby_filters [data-testid="stColumn"] { flex:0 0 auto !important; width:auto !important; }
    .st-key-nearby_filters button { width:auto !important; min-height:auto !important; padding:8px 16px !important; border-radius:999px !important; border:1px solid #E3DDD3 !important; background:#FFF !important; color:#4E270D !important; white-space:nowrap !important; font-size:12.5px !important; box-shadow:none !important; }
    .st-key-nearby_filters button[data-testid="stBaseButton-primary"] { background:#008F91 !important; border-color:#008F91 !important; color:#FFF !important; }
    .injoy-place-card { background:#FFF; border-radius:25.6px 25.6px 0 0; box-shadow:0 8px 24px -12px rgba(92,65,44,.25); padding:15px 16px 7px; margin-top:2px; }
    .injoy-place-heading { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; }
    .injoy-place-name { color:#2A1B11; font-size:14px; font-weight:800; line-height:1.35; }
    .injoy-place-meta { color:#76695D; font-size:11px; font-weight:600; line-height:1.4; margin-top:2px; }
    .injoy-place-desc { color:#3C2B20; font-size:12.5px; line-height:1.5; margin-top:9px; }
    .injoy-place-tags { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }
    .injoy-place-lang, .injoy-place-audience { display:inline-flex; border-radius:999px; padding:3px 8px; background:#F6EDE0; color:#4E3B2E; font-size:9.5px; font-weight:800; }
    .injoy-place-audience { background:#D5F4E2; color:#0B764D; }
    [data-testid="stHorizontalBlock"][class*="st-key-nearby_actions_"] { background:#FFF; border-radius:0 0 25.6px 25.6px; box-shadow:0 14px 24px -18px rgba(92,65,44,.35); padding:4px 16px 14px; margin-bottom:10px; justify-content:flex-start; gap:8px !important; }
    [class*="st-key-nearby_actions_"] [data-testid="stColumn"], [class*="st-key-nearby_actions_"] [data-testid="stElementContainer"] { flex:0 0 auto !important; width:auto !important; }
    [class*="st-key-nearby_actions_"] button, [class*="st-key-nearby_actions_"] a { width:auto !important; min-height:auto !important; border-radius:999px !important; padding:8px 13px !important; font-size:11.5px !important; font-weight:700 !important; white-space:nowrap !important; }
    [class*="st-key-nearby_actions_"] a { background:#008F91 !important; border-color:#008F91 !important; color:#FFF !important; }
    .injoy-nearby-footer { color:#76695D; font-size:10px; padding:10px 4px 2px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="injoy-nearby-header">'
    '<div><div class="injoy-nearby-title">내 주변</div>'
    '<div class="injoy-nearby-sub">실제로 도움을 받을 수 있는 곳들.</div></div>'
    '<span class="injoy-sample-badge">샘플 데이터</span></div>',
    unsafe_allow_html=True,
)

map_center = INCHEON_CENTER
if filtered_places:
    map_center = (filtered_places[0]["latitude"], filtered_places[0]["longitude"])

nearby_map = folium.Map(
    location=map_center,
    zoom_start=11 if len(filtered_places) > 1 else 13,
    tiles="CartoDB positron",
    control_scale=False,
)
marker_html = """
<div style="width:36px;height:36px;border-radius:50%;background:#008f91;border:3px solid white;
box-shadow:0 5px 12px rgba(0,90,92,.30);display:grid;place-items:center;color:white;font-size:20px">⌖</div>
"""
for place in filtered_places:
    folium.Marker(
        location=(place["latitude"], place["longitude"]),
        tooltip=place["name"],
        popup=folium.Popup(f"<b>{safe(place['name'])}</b><br>{safe(place['category'])}", max_width=240),
        icon=folium.DivIcon(html=marker_html, icon_size=(36, 36), icon_anchor=(18, 18)),
    ).add_to(nearby_map)

if len(filtered_places) > 1:
    nearby_map.fit_bounds([(p["latitude"], p["longitude"]) for p in filtered_places], padding=(28, 28))

with st.container(key="nearby_map_wrap"):
    st_folium(
        nearby_map,
        height=255,
        use_container_width=True,
        key=f"nearby_map_{active_category}",
        returned_objects=[],
    )

with st.container(key="nearby_filters", horizontal=True, gap=None):
    for category in CATEGORIES:
        if st.button(
            category,
            key=f"nearby_filter_{category}",
            type="primary" if active_category == category else "secondary",
        ):
            st.session_state.nearby_category = category
            st.rerun()

if not filtered_places:
    st.info("이 카테고리에는 아직 등록된 도움처가 없어요.")

for place in filtered_places:
    language_tags = "".join(f'<span class="injoy-place-lang">{safe(lang)}</span>' for lang in place.get("languages", []))
    audience = f'<span class="injoy-place-audience">{safe(place["audience"])}</span>' if place.get("audience") else ""
    sample_badge = '<span class="injoy-sample-badge">샘플 데이터</span>' if place.get("sample") else ""
    st.markdown(
        f'<div class="injoy-place-card">'
        f'<div class="injoy-place-heading"><div class="injoy-place-name">{safe(place["name"])}</div>{sample_badge}</div>'
        f'<div class="injoy-place-meta">{place["distance_km"]:.1f} km · {safe(place["category"])} · {safe(place["hours"])}</div>'
        f'<div class="injoy-place-desc">{safe(place["description"])}</div>'
        f'<div class="injoy-place-tags">{language_tags}{audience}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    with st.container(key=f"nearby_actions_{place['id']}", horizontal=True, gap=None):
        if st.button("이곳에 대해 AI에게 질문", key=f"nearby_ask_{place['id']}"):
            st.session_state.chat_prefill_topic = place["name"]
            st.switch_page(common.PAGES["chat"])
        directions_url = f"https://map.naver.com/p/search/{quote(place['name'])}"
        st.link_button("⌁ 길찾기", directions_url, type="primary")

st.markdown(
    '<div class="injoy-nearby-footer">최신 정보는 반드시 공식 기관에서 확인해 주세요.</div>',
    unsafe_allow_html=True,
)
