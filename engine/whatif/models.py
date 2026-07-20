"""what-if 입력/출력 모델."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NewStoreSpec:
    lon: float
    lat: float
    name: str
    category: str


@dataclass
class WhatIfReport:
    daily_average_visits: float
    switched_citizens: int
    source_breakdown: dict[str, int] = field(default_factory=dict)
    hourly_distribution: dict[int, int] = field(default_factory=dict)
