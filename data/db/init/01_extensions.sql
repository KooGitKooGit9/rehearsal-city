-- PostGIS 확장 활성화 (컨테이너 최초 기동 시 1회 자동 실행)
-- 공간 컬럼(geometry/geography)과 공간 인덱스, 최단경로 연산에 필요.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
