"""합성 인구 생성 CLI.

실행: python -m engine.generate_population [N]
인자를 생략하면 1000명을 생성한다.
"""
from __future__ import annotations

import json
import sys

from engine.config import DEMO_REGION
from engine.network.graph import load_or_build_graph
from engine.population.db_source import load_age_gender_weights
from engine.population.generator import generate_citizens


def _to_geojson(citizens) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [c.lon, c.lat]},
                "properties": {
                    "citizen_id": c.citizen_id,
                    "gender": c.gender,
                    "age_band": c.age_band,
                    "home_node": c.home_node,
                },
            }
            for c in citizens
        ],
    }


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    print("도로망 그래프 로드 중...")
    graph = load_or_build_graph()

    print("연령·성별 분포 집계 중...")
    weights = load_age_gender_weights()

    print(f"{n}명 생성 중...")
    citizens = generate_citizens(n, weights, graph, seed=42)

    output_path = DEMO_REGION.citizens_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(_to_geojson(citizens), ensure_ascii=False, indent=2))

    print(f"{len(citizens)}명의 합성 시민 생성 완료 → {output_path}")


if __name__ == "__main__":
    main()
