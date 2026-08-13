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

# 모든 URL을 인증 상태와 관계없이 먼저 등록한다. 그래야 /mylife 같은 주소에서
# 새로고침할 때 profile이 아직 없는 순간에도 Streamlit의 Page not found가 뜨지 않는다.
has_profile = "profile" in st.session_state
onboarding_page = st.Page(
    common.render_onboarding,
    title="온보딩",
    url_path="onboarding",
    default=not has_profile,
)
pages_by_id = {
    tab_id: st.Page(
        f"pages/{tab_id}.py",
        title=label,
        icon=icon,
        url_path=tab_id,
        default=has_profile and tab_id == "home",
    )
    for tab_id, label, icon in common.NAV_ITEMS
}
common.PAGES.update(pages_by_id)

current_page = st.navigation([onboarding_page, *pages_by_id.values()], position="hidden")

# 프로필이 없는 새 세션에서 /mylife 같은 주소를 직접 열어도 해당 URL은 이미
# 등록되어 있으므로 Not Found가 뜨지 않는다. 이때 강제 리디렉션은 Streamlit에서
# 재실행 루프를 만들 수 있어, 현재 URL을 유지한 채 온보딩을 바로 렌더한다.
if not has_profile and current_page.url_path != "onboarding":
    common.render_onboarding()
    st.stop()
if has_profile and current_page.url_path == "onboarding":
    st.switch_page(pages_by_id["home"])

if not has_profile:
    current_page.run()
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
        st.switch_page(onboarding_page)

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
