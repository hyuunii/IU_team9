# IU_team9

# 인조이 (INJOY)

외국인 주민·유학생을 위한 AI 다국어 생활정보 안내 서비스
> 초광역 지역문제 해결형 해커톤 · 9조(IU_team9) · 과제 I2. 외국인 주민·유학생 정착과 생활 인프라 격차 · [기획안 v5(최종)](./인조이_기획안_v5_최종.md)

핵심 구조: 검색(RAG)과 생성(GPT)을 분리하고, 위험도(고위험/저위험)에 따라 답변 전략을 다르게 가져가는 3단계 답변 라우팅. 최종 목표는 5탭 구조(홈 / 생활가이드 / AI챗봇 / 내주변 / 마이라이프)이며, 현재 코드는 그 중 홈·AI챗봇의 초기 스켈레톤 단계.

## 팀원별 초기 세팅 (각자 컴퓨터에서 1회)

```bash
# 1. 프로젝트 폴더로 이동
cd IU_team9

# 2. 가상환경 생성 및 활성화 (선택이지만 권장)
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. 패키지 설치
pip install -r requirements.txt

# 4. API 키 설정
cp .env.example .env
# .env 파일 열어서 OPENAI_API_KEY=배부받은_팀_API_키 로 수정

# 5. FAQ 임베딩 생성 (팀에서 한 명만 실행하고, 결과 파일을 나머지가 공유받아도 됨)
python embed_faq.py
# → data/faq_embeddings.npy 생성됨 (이 파일이 있어야 챗봇이 RAG로 작동)

# 6. 앱 실행
streamlit run app.py
```

## 폴더 구조

```
IU_team9/
├── app.py                    # Streamlit 메인 (현재: 홈/챗봇 2탭 → 추후 5탭으로 확장 예정)
├── embed_faq.py               # FAQ 임베딩 생성 스크립트 (최초 1회 실행)
├── generate_heatmap.py        # 발표용 히트맵 이미지 생성 (앱 외부 B2G 산출물)
├── data/
│   ├── faq.json                # FAQ 32건 (완료)
│   ├── faq_embeddings.npy      # embed_faq.py 실행 후 생성됨 (gitignore 처리)
│   ├── dept_routing.json       # 4개 구 부서 정보 (⚠️ 전화번호 TODO)
│   ├── support_policies.json   # 지원정책 큐레이션 6건 (⚠️ 아직 미생성)
│   └── logs.csv                # 질문 로그, 앱 실행하면 자동 생성 (gitignore 처리)
├── utils/
│   ├── rag.py                  # 임베딩 검색(코사인 유사도)
│   ├── classify.py             # 질문 분류(카테고리/지역/위험도)
│   └── routing.py              # 부서 라우팅
├── .env                        # API 키 (git에 올리면 안 됨, .gitignore에 포함됨)
├── .env.example                # .env 템플릿
└── requirements.txt
```

## 주의사항

- API 키는 절대 코드에 직접 쓰거나 GitHub에 올리지 않기 (`.env` 파일만 사용, `.gitignore`에 이미 포함됨)
- `data/faq_embeddings.npy`는 `embed_faq.py`를 실행해야 생성됨 — 이 파일 없으면 챗봇이 RAG 없이 일반지식으로만 답함 (앱이 자동으로 감지해서 폴백함)
- 마이라이프의 체크리스트·스크랩은 로그인 없이 `st.session_state`로만 유지되는 세션 기반 프로토타입 — 새로고침하면 초기화됨 (실서비스 확장 시 로그인+DB 필요, 로드맵 참고)
