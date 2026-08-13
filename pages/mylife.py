"""마이라이프 탭 — /mylife (저장한 생활가이드 + 준비 중인 체크리스트)"""
import streamlit as st

import common

profile = common.require_profile()

st.subheader("마이라이프")
st.caption(f"체류기간 {profile['duration']} 기준 체크리스트 · 스크랩")

saved_ids = st.session_state.get("saved_guide_ids", set())
saved_items = [common.GUIDE_ITEMS_BY_ID[i] for i in saved_ids if i in common.GUIDE_ITEMS_BY_ID]
if saved_items:
    st.markdown('<div class="injoy-section-title">저장한 생활가이드</div>', unsafe_allow_html=True)
    for item in saved_items:
        if common.render_guide_item_card(item):
            st.session_state.guide_detail_id = item["id"]
            st.switch_page(common.PAGES["guide"])
    st.markdown('<div class="injoy-spacer"></div>', unsafe_allow_html=True)

st.info(
    "🚧 체류기간 기준 체크리스트는 준비 중이에요. "
    "(로그인 없이 st.session_state로만 유지 — 새로고침하면 초기화됩니다)"
)
