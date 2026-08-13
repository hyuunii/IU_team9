"""홈 탭 화면 — /home

st.Page(file_path=...)로 등록되기 때문에 이 파일은 매 rerun마다 처음부터 다시 실행되는
"진짜 스크립트"다 (import된 모듈처럼 캐싱되지 않음).
"""
import streamlit as st

import common

profile = common.require_profile()

purpose_note = f" · {profile['purpose']}" if profile.get("purpose") else ""
dept_note = common.get_department_info(profile["region"], common.dept_data)

hero_html = (
    '<div class="injoy-hero">'
    f'<div class="injoy-hero-title">{profile["nickname"]}님, 인천에 오신 것을 환영해요</div>'
    f'<div class="injoy-hero-sub">{profile["region"]} · 체류기간 {profile["duration"]}{purpose_note}</div>'
)
if dept_note:
    hero_html += f'<div class="injoy-hero-note">📍 {dept_note}</div>'
if not profile.get("has_arc"):
    hero_html += (
        '<div class="injoy-hero-warn">⚠️ 외국인등록증이 없으신 경우, '
        '관련 절차는 AI에게 질문 탭에서 물어보세요.</div>'
    )
hero_html += "</div>"
st.markdown(hero_html, unsafe_allow_html=True)

st.markdown('<div class="injoy-spacer"></div>', unsafe_allow_html=True)

if "home_selected_group" in st.session_state:
    selected = next(c for c in common.CATEGORY_GRID if c["id"] == st.session_state.home_selected_group)
    common.render_category_detail(selected, state_key="home_selected_group")
else:
    common.render_home_category_grid()

    st.markdown('<div class="injoy-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="injoy-section-title">당신을 위한 추천</div>', unsafe_allow_html=True)
    for icon, title, desc, _cat_id in common.HOME_TIPS:
        common.render_guide_card(icon, title, desc, badge="tip")
    st.caption("더 많은 정보는 **생활가이드** 탭에서 카테고리별로 볼 수 있어요.")
