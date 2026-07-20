# 리허설시티 (RehearsalCity)

## 프로젝트 개요
가게를 열기 전 결과를 미리 확인하는 창업 시뮬레이션 서비스.
공공데이터 기반 합성 인구(AI 시민)가 가상 동네에서 출근·이동·소비하며 생활하고,
사용자가 신규 매장(위치·업종·가격)을 주입하면 예상 방문 수, 경쟁 매장 이탈률,
시간대별 방문 패턴, 위치 대안 비교를 산출한다.

- 데모 지역: 서울 성수동 (config로 관리, 하드코딩 금지)
- 제출 목표: 졸업작품(캡스톤) + 오픈소스 개발자대회(인공지능/자유과제) + 앱 공모전
- 상세 배경과 서비스 정의: docs/SERVICE.md
- 현재 진행 단계: docs/PLAN.md 에서 확인 후 작업할 것

## 아키텍처 (4층)
```
web/     React + deck.gl 지도 대시보드 (시민 렌더링, what-if 입력, 결과 차트)
api/     FastAPI + WebSocket (시뮬레이션 실행 요청, 진행상황 실시간 스트리밍)
engine/  시뮬레이션 코어 (합성 인구, 틱 루프, 규칙 기반 행동, LLM 의사결정)
data/    공공 API 수집 → PostgreSQL + PostGIS 적재 (docs/DATA.md 참조)
validation/  백테스트 (실제 매장 재현 → 공개 매출 통계와 오차 측정)
```
engine은 web/api 없이 단독 실행 가능한 Python 패키지로 유지한다
(오픈소스대회 제출 시 라이브러리로 분리하기 위함).

## 핵심 설계 원칙 (위반 금지)
1. LLM 호출은 "전환점 결정"에만 사용한다 (예: 신규 매장 발견 → 전환 여부).
   일상 행동(경로, 습관적 소비)은 규칙 + 확률 모델로 처리한다. 비용 통제 목적.
2. LLM 응답은 프로파일 단위 캐싱 + 다건 배칭을 필수로 구현한다.
3. 시뮬레이션 시간은 10분 단위 틱 루프로 진행한다.
4. 개별 에이전트의 정확성을 주장하지 않는다. 목표는 집단 수준 재현이며,
   근거는 validation/의 백테스트 수치다.
5. Phase 2(규칙 기반 코어)가 완성되기 전에 LLM 통합을 시작하지 않는다.

## 기술 스택
- Python 3.12, FastAPI, PostgreSQL + PostGIS (docker-compose로만 실행)
- OSMnx (도로망 그래프), GeoPandas, numpy
- React, deck.gl
- LLM API (교체 가능한 클라이언트 구조, 현재 Gemini 사용)

## 개발 규칙
- 커밋 메시지: 한국어, conventional commits (feat:, fix:, docs:, chore:)
- 새 Python 의존성 추가 시 requirements.txt 갱신 필수
- DB는 docker-compose up으로만 실행. 로컬 직접 설치 금지
- 시크릿(API 키)은 .env로 관리, 커밋 금지 (.gitignore 확인)
- 주요 설계 결정을 바꾸기 전에 docs/DECISIONS.md 확인. 뒤집으려면 사유를 기록
- 의미 있는 작업 단위가 끝나면 커밋까지 완료한다 (커밋 전 변경 파일 목록 보고)
- 커밋 후에는 자동으로 origin에 푸시한다
