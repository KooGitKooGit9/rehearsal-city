"""시민의 틱별 가변 상태."""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.population.models import Citizen

ACTIVITY_HOME = "HOME"
ACTIVITY_COMMUTING = "COMMUTING"
ACTIVITY_WORK = "WORK"
ACTIVITY_LEISURE = "LEISURE"
ACTIVITY_RETURNING = "RETURNING"


@dataclass
class CitizenState:
    citizen: Citizen
    node: int
    lon: float
    lat: float
    activity: str = ACTIVITY_HOME
    path: list[int] = field(default_factory=list)
    edge_progress_m: float = 0.0
    dwell_remaining: int = 0
    habitual_store_node: int | None = None
    decided_new_stores: set[int] = field(default_factory=set)

    @classmethod
    def at_home(cls, citizen: Citizen) -> "CitizenState":
        return cls(citizen=citizen, node=citizen.home_node, lon=citizen.lon, lat=citizen.lat)
