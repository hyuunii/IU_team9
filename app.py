"""
인조이 (INJOY) - 외국인 주민·유학생을 위한 AI 다국어 생활정보 안내 서비스
실행: streamlit run app.py

이 파일은 "라우터" 역할만 한다 — 탭별 실제 내용은 pages/*.py에, 공용 로직/데이터는
common.py에 있다. 다 같이 app.py 하나에서 작업하면 git 충돌이 잦아서, 탭별로
파일을 분리했다 — 팀원들은 각자 자기가 맡은 pages/*.py만 건드리면 된다.
"""
import streamlit as st

import common

st.set_page_config(page_title="인조이", page_icon="🏘️")

if "profile" not in st.session_state:
    # 온보딩도 독립된 엔드포인트(/onboarding)로 분리
    onboarding_nav = st.navigation(
        [st.Page(common.render_onboarding, title="온보딩", url_path="onboarding", default=True)],
        position="hidden",
    )
    onboarding_nav.run()
    st.stop()

profile = st.session_state.profile

common.inject_css()
st.title("인조이 🏘️")

with st.sidebar:
    st.caption(
        f"{profile.get('language_flag', '')} {profile['nickname']}님 · "
        f"{profile['region']} · 체류기간 {profile['duration']}"
    )
    if st.button("프로필 다시 설정"):
        del st.session_state["profile"]
        st.rerun()

# ── 5개 탭을 진짜 별도 엔드포인트(URL) + 별도 파일로 분리 ────────────────
# st.Page에 파일 경로를 주면 각 탭이 실제 URL(/home, /guide, /chat, /nearby, /mylife)을
# 가지면서, 동시에 pages/*.py 파일로 코드도 분리된다.
pages_by_id = {
    tab_id: st.Page(f"pages/{tab_id}.py", title=label, icon=icon, url_path=tab_id, default=(tab_id == "home"))
    for tab_id, label, icon in common.NAV_ITEMS
}
common.PAGES.update(pages_by_id)  # pages/*.py에서 st.switch_page(common.PAGES["chat"]) 형태로 참조

current_page = st.navigation(list(pages_by_id.values()), position="hidden")
current_page.run()

with st.container(key="bottom_nav", horizontal=True, gap=None):
    for tab_id, label, icon in common.NAV_ITEMS:
        is_active = current_page.url_path == tab_id
        if st.button(
            f"{icon}\n{label}",
            key=f"nav_{tab_id}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.switch_page(pages_by_id[tab_id])
