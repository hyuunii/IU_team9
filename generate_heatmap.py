"""
앱 외부 확장 산출물: 챗봇 질문 로그를 구x카테고리 히트맵으로 집계.
이건 사용자용 앱 기능이 아니라, 발표 슬라이드에 넣을 이미지를 만드는 용도.

사용법: python generate_heatmap.py
결과물: heatmap_output.png (발표 슬라이드에 삽입)
"""
import pandas as pd
import matplotlib.pyplot as plt

LOG_PATH = "data/logs.csv"


def main():
    df = pd.read_csv(LOG_PATH, encoding="utf-8-sig")

    # 지역 미상은 히트맵에서 제외 (구별 분석이 목적이므로)
    df = df[df["region"] != "미상"]

    pivot = df.pivot_table(index="category", columns="region", values="question", aggfunc="count", fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(pivot.values, cmap="YlOrBr", aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            ax.text(j, i, int(pivot.values[i, j]), ha="center", va="center", fontsize=9)

    ax.set_title("지역사회 온도계 — 구x카테고리별 문의 현황\n(🟠 실데이터/시뮬레이션 구분은 발표 시 별도 표기)")
    fig.colorbar(im, ax=ax, label="문의 건수")
    plt.tight_layout()
    plt.savefig("heatmap_output.png", dpi=150)
    print("저장 완료: heatmap_output.png")


if __name__ == "__main__":
    main()
