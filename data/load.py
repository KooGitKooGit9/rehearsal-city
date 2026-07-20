"""idempotent 적재 — 같은 (기준일, 시간대, 행정동)을 재실행해도 갱신만 되고 중복되지 않는다."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.dialects.postgresql import insert

from data.db import engine
from data.models import LivingPopulationDong


def _to_row(raw: dict) -> dict:
    return {
        "stdr_de_id": datetime.strptime(raw["STDR_DE_ID"], "%Y%m%d").date(),
        "tmzon_pd_se": int(raw["TMZON_PD_SE"]),
        "adstrd_code_se": raw["ADSTRD_CODE_SE"],
        "tot_lvpop_co": float(raw["TOT_LVPOP_CO"]),
        "raw": raw,
    }


def upsert_living_population(rows: list[dict]) -> int:
    if not rows:
        return 0

    values = [_to_row(row) for row in rows]
    stmt = insert(LivingPopulationDong).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["stdr_de_id", "tmzon_pd_se", "adstrd_code_se"],
        set_={"tot_lvpop_co": stmt.excluded.tot_lvpop_co, "raw": stmt.excluded.raw},
    )

    with engine.begin() as conn:
        conn.execute(stmt)

    return len(values)
