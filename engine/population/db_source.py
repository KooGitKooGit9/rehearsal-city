"""living_population_dong에서 연령·성별 분포 가중치를 집계한다."""
from __future__ import annotations

from sqlalchemy import select

from data.db import engine as db_engine
from data.models import LivingPopulationDong


def aggregate_age_gender(raw_rows: list[dict]) -> dict[tuple[str, str], float]:
    weights: dict[tuple[str, str], float] = {}
    for raw in raw_rows:
        for key, value in raw.items():
            if key == "TOT_LVPOP_CO" or not key.endswith("_LVPOP_CO"):
                continue
            gender, age_band = key.removesuffix("_LVPOP_CO").split("_", 1)
            weights[(gender, age_band)] = weights.get((gender, age_band), 0.0) + float(value)
    return weights


def load_age_gender_weights() -> dict[tuple[str, str], float]:
    with db_engine.connect() as conn:
        raw_rows = list(conn.execute(select(LivingPopulationDong.raw)).scalars())
    return aggregate_age_gender(raw_rows)
