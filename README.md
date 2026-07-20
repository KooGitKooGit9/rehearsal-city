# 리허설시티 (RehearsalCity)

> 가게를 열기 전에, 미리 열어보세요.

공공데이터 기반 합성 인구(AI 시민)가 살아가는 가상 동네에 신규 매장을 주입하고,
예상 방문 수·경쟁 이탈·시간대 패턴을 시뮬레이션하는 창업 사전검증 서비스입니다.

## 구조
- `engine/` — 시뮬레이션 코어 (합성 인구, 틱 루프, LLM 의사결정) · 단독 실행 가능
- `data/` — 공공 API 수집 → PostgreSQL + PostGIS 적재
- `api/` — FastAPI + WebSocket
- `web/` — React + deck.gl 대시보드
- `validation/` — 실제 매장 백테스트
- `docs/` — 서비스 정의, 로드맵, 데이터 명세, 설계 결정 기록

## 시작하기 (팀원 온보딩)
```bash
git clone <repo-url>
cd rehearsal-city
docker-compose up -d          # PostGIS DB 실행
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # API 키 입력

# 실시간 시뮬레이션 대시보드 (터미널 2개 필요)
uvicorn api.main:app --reload           # 터미널 1: FastAPI + WebSocket
cd web && npm install && npm run dev     # 터미널 2: React + deck.gl
```

## 문서
- [서비스 정의](docs/SERVICE.md)
- [개발 로드맵](docs/PLAN.md)
- [데이터 소스 명세](docs/DATA.md)
- [설계 결정 기록](docs/DECISIONS.md)

## 라이선스
MIT
