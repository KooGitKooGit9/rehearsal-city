"""틱 루프를 실제로 굴리는 시뮬레이션 엔진."""
from __future__ import annotations

import random

import networkx as nx

from engine.population.models import Citizen
from engine.simulation.clock import TICKS_PER_DAY, tick_to_clock_str
from engine.simulation.consumption import pick_store
from engine.simulation.movement import advance_along_path
from engine.simulation.scheduler import decide_activity, generate_schedule
from engine.simulation.state import ACTIVITY_HOME, ACTIVITY_LEISURE, CitizenState


class SimulationEngine:
    def __init__(
        self,
        graph: nx.MultiDiGraph,
        citizens: list[Citizen],
        pois: list[dict],
        seed: int | None = None,
    ) -> None:
        self.graph = graph
        self.pois = pois
        self.rng = random.Random(seed)
        self.tick = 0
        self.store_visit_counts: dict[int, int] = {}

        self.states = [CitizenState.at_home(c) for c in citizens]
        self.schedules = [generate_schedule(c.home_node, graph, self.rng) for c in citizens]

    def _pick_store(self, lon: float, lat: float, rng: random.Random) -> tuple[int, float, float]:
        return pick_store(lon, lat, self.pois, rng)

    def step(self) -> None:
        for state, schedule in zip(self.states, self.schedules):
            was_leisure = state.activity == ACTIVITY_LEISURE
            decide_activity(state, schedule, self.tick, self.graph, self._pick_store, self.rng)
            if state.activity == ACTIVITY_LEISURE and not was_leisure:
                self._log_visit(state)

            advance_along_path(state, self.graph)

        self.tick += 1
        if self.tick >= TICKS_PER_DAY:
            self.tick = 0
            self._reset_day()

    def _log_visit(self, state: CitizenState) -> None:
        store_node = state.path[-1] if state.path else state.node
        self.store_visit_counts[store_node] = self.store_visit_counts.get(store_node, 0) + 1

    def _reset_day(self) -> None:
        for state in self.states:
            state.node = state.citizen.home_node
            state.lon = state.citizen.lon
            state.lat = state.citizen.lat
            state.activity = ACTIVITY_HOME
            state.path = []
            state.edge_progress_m = 0.0
            state.dwell_remaining = 0

    def to_geojson_snapshot(self) -> dict:
        return {
            "type": "FeatureCollection",
            "tick": self.tick,
            "clock": tick_to_clock_str(self.tick),
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [s.lon, s.lat]},
                    "properties": {
                        "citizen_id": s.citizen.citizen_id,
                        "gender": s.citizen.gender,
                        "age_band": s.citizen.age_band,
                        "activity": s.activity,
                    },
                }
                for s in self.states
            ],
        }
