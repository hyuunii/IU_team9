"""내주변 탭 — /nearby (준비 중 플레이스홀더)"""
import streamlit as st

import common

profile = st.session_state.profile

st.subheader("내주변")
st.caption(f"{profile['region']} 기준으로 준비 중이에요.")
st.info(
    "🚧 Google Places API 연동 예정 (병원·은행 등 리스트 + 지도 링크). "
    "외국인지원센터·노동상담소 등 특화기관은 팀 조사 데이터로 보완할 계획이에요."
)
