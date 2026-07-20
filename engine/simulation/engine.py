"""틱 루프를 실제로 굴리는 시뮬레이션 엔진."""
from __future__ import annotations

import math
import random

import networkx as nx

from engine.decision.cache import DecisionCache
from engine.decision.client import LLMClient
from engine.decision.decider import decide_batch_with_cache
from engine.decision.models import DecisionRequest
from engine.network.routing import path_length_m
from engine.population.models import Citizen
from engine.simulation.clock import TICKS_PER_DAY, tick_to_clock_str
from engine.simulation.consumption import NEAREST_CANDIDATE_COUNT, pick_store
from engine.simulation.movement import advance_along_path
from engine.simulation.scheduler import decide_activity, generate_schedule
from engine.simulation.state import ACTIVITY_HOME, ACTIVITY_LEISURE, ACTIVITY_WORK, CitizenState


def _euclidean(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    return math.hypot(lon2 - lon1, lat2 - lat1)


class SimulationEngine:
    def __init__(
        self,
        graph: nx.MultiDiGraph,
        citizens: list[Citizen],
        pois: list[dict],
        seed: int | None = None,
        new_store: dict | None = None,
        llm_client: LLMClient | None = None,
        decision_cache: DecisionCache | None = None,
    ) -> None:
        self.graph = graph
        self.pois = pois
        self.rng = random.Random(seed)
        self.tick = 0
        self.store_visit_counts: dict[int, int] = {}
        self.visit_log: list[tuple[int, int]] = []  # (store_node, tick)

        # what-if 전용 (기본값 None이면 Phase 2와 동일하게 동작 — 회귀 없음)
        self.new_store = new_store
        self.llm_client = llm_client
        self.decision_cache = decision_cache or DecisionCache()
        self.switch_log: list[dict] = []

        self.states = [CitizenState.at_home(c) for c in citizens]
        self.schedules = [generate_schedule(c.home_node, graph, self.rng) for c in citizens]

    def _pick_store(self, lon: float, lat: float, rng: random.Random) -> tuple[int, float, float]:
        return pick_store(lon, lat, self.pois, rng)

    def step(self) -> None:
        if self.new_store is not None and self.llm_client is not None:
            self._process_turning_points()

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
        self.visit_log.append((store_node, self.tick))

    def _reset_day(self) -> None:
        for state in self.states:
            state.node = state.citizen.home_node
            state.lon = state.citizen.lon
            state.lat = state.citizen.lat
            state.activity = ACTIVITY_HOME
            state.path = []
            state.edge_progress_m = 0.0
            state.dwell_remaining = 0

        # 여가 여부·출퇴근 시각을 매일 새로 뽑아 하루하루의 방문 패턴에 변화를 준다
        # (기존에는 하루치 스케줄을 그대로 재사용해 매일 똑같은 시간에만 외출했음)
        self.schedules = [
            generate_schedule(state.citizen.home_node, self.graph, self.rng) for state in self.states
        ]

    def _poi_by_node(self, node: int | None) -> dict | None:
        if node is None:
            return None
        if self.new_store is not None and node == self.new_store["node"]:
            return self.new_store
        for poi in self.pois:
            if poi["node"] == node:
                return poi
        return None

    def _poi_label(self, node: int | None) -> str:
        poi = self._poi_by_node(node)
        if poi is None:
            return "알 수 없음"
        return poi.get("name") or f"{poi.get('category', '알 수 없음')} 매장"

    def _new_store_is_candidate(self, state: CitizenState) -> bool:
        candidates = self.pois + [self.new_store]
        ranked = sorted(candidates, key=lambda p: _euclidean(state.lon, state.lat, p["lon"], p["lat"]))
        return any(p["node"] == self.new_store["node"] for p in ranked[:NEAREST_CANDIDATE_COUNT])

    def _build_decision_request(self, state: CitizenState) -> DecisionRequest:
        habitual_poi = self._poi_by_node(state.habitual_store_node)
        return DecisionRequest(
            citizen_id=state.citizen.citizen_id,
            gender=state.citizen.gender,
            age_band=state.citizen.age_band,
            new_store_name=self.new_store.get("name") or "신규 매장",
            new_store_category=self.new_store["category"],
            distance_to_new_store_m=path_length_m(self.graph, state.node, self.new_store["node"]) or 0.0,
            current_store_category=habitual_poi["category"] if habitual_poi else None,
            distance_to_current_store_m=(
                path_length_m(self.graph, state.node, state.habitual_store_node) if habitual_poi else None
            ),
        )

    def _process_turning_points(self) -> None:
        eligible_states = [
            state
            for state, schedule in zip(self.states, self.schedules)
            if (
                state.activity == ACTIVITY_WORK
                and self.tick >= schedule.leave_work_tick
                and schedule.has_leisure_stop
                and state.habitual_store_node is not None
                and self.new_store["node"] not in state.decided_new_stores
                and self._new_store_is_candidate(state)
            )
        ]

        if not eligible_states:
            return

        requests = [self._build_decision_request(s) for s in eligible_states]
        results = decide_batch_with_cache(self.llm_client, self.decision_cache, requests)

        for state, result in zip(eligible_states, results):
            state.decided_new_stores.add(self.new_store["node"])
            if result.switch_to_new_store:
                self.switch_log.append(
                    {
                        "citizen_id": state.citizen.citizen_id,
                        "from_store": self._poi_label(state.habitual_store_node),
                        "tick": self.tick,
                    }
                )
                state.habitual_store_node = self.new_store["node"]

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
