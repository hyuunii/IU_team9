"""생활가이드 탭 — /guide

목록(필터 칩 + 카드) 화면과 개별 항목 상세 화면을 함께 관리한다.
st.session_state.guide_detail_id가 있으면 상세 화면, 없으면 목록 화면.
"""
import streamlit as st

import common

profile = st.session_state.profile


def render_detail(item: dict):
    """생활가이드 개별 항목 상세 페이지. Lovable 원본 구성 그대로:
    뒤로가기 → 아이콘+배지 → 제목/부제 → 액션 버튼 3개(저장/AI에게 질문/가까운 도움처)
    → 왜 중요한가요 → 이렇게 하면 돼요 → (있으면) 도움이 되는 서비스 → 주의할 점
    → 관련 정보 → 하단 안내 문구.
    구체적 사실을 지어내지 않고: "왜 중요한가요"/"주의할 점"은 일반적인 안내 문구이고,
    "이렇게 하면 돼요"는 실제 FAQ/팁 텍스트를 문장 단위로 재구성한 것,
    "도움이 되는 서비스"는 실제 부서 라우팅 데이터가 있을 때만 보여준다."""
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
            st.switch_page(common.PAGES["chat"])
        if st.button("📍 가까운 도움처", key="detailaction_nearby"):
            st.switch_page(common.PAGES["nearby"])

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

    steps = common.split_into_steps(item["desc"])
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

    dept_note = common.get_department_info(profile["region"], common.dept_data)
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

    related = [g for g in common.GUIDE_ITEMS if g["cat_id"] == item["cat_id"] and g["id"] != item["id"]][:2]
    if related:
        st.markdown(
            '<div class="injoy-related-title">관련 정보</div>'
            '<div class="injoy-related-sub">이것도 알아두면 좋아요</div>',
            unsafe_allow_html=True,
        )
        for rel in related:
            if common.render_guide_item_card(rel):
                st.session_state.guide_detail_id = rel["id"]
                st.rerun()

    st.markdown(
        f'<div class="injoy-detail-footer">최신 정보는 반드시 공식 기관에서 확인해 주세요. '
        f'({len(common.GUIDE_ITEMS)}개 항목 · 샘플 데이터)</div>',
        unsafe_allow_html=True,
    )


detail_id = st.session_state.get("guide_detail_id")
if detail_id and detail_id in common.GUIDE_ITEMS_BY_ID:
    render_detail(common.GUIDE_ITEMS_BY_ID[detail_id])
else:
    st.markdown(
        '<div class="injoy-guide-header">'
        '<div class="injoy-guide-title">생활가이드</div>'
        '<div class="injoy-guide-sub">긴 문서가 아니라, 실행 가능한 단계로 정리했어요.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.session_state.setdefault("guide_filter", "all")

    with st.container(key="guide_filters", horizontal=True, gap=None):
        for filter_id, filter_icon, filter_label in common.GUIDE_FILTERS:
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
    for item in common.GUIDE_ITEMS:
        if active_filter in ("all", item["cat_id"]):
            if common.render_guide_item_card(item):
                st.session_state.guide_detail_id = item["id"]
                st.rerun()
            shown += 1

    if shown == 0:
        st.caption("아직 등록된 정보가 없어요.")
