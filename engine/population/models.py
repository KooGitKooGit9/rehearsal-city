"""합성 시민 데이터 모델."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Citizen:
    citizen_id: int
    gender: str
    age_band: str
    home_node: int
    lon: float
    lat: float
