# INJOY

인천 생활 정보 서비스의 Next.js 프론트엔드입니다. 기존 Streamlit 구현은 제거되었으며, 모든 화면과 로컬 데이터는 `frontend/`에 있습니다.

## 로컬 실행

```bash
./run_frontend.sh
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 엽니다.

## AI 답변 설정

`frontend/.env.local`에 다음 값을 설정하면 OpenAI 답변을 사용합니다.

```env
OPENAI_API_KEY=your_api_key
```

키가 없어도 FAQ 검색 기반 답변과 나머지 화면은 정상 작동합니다.

## 주요 경로

- `/` — 온보딩
- `/home` — 홈
- `/guide` — 생활 가이드
- `/ask` — AI 질문
- `/nearby` — 내 주변 지도
- `/my` — 마이 라이프
