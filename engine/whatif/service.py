"""신규 매장을 주입해 N일치 시뮬레이션을 돌리고 리포트를 집계한다."""
from __future__ import annotations

import networkx as nx

from engine.decision.cache import DecisionCache
from engine.decision.client import LLMClient
from engine.network.routing import nearest_node
from engine.population.models import Citizen
from engine.simulation.clock import TICKS_PER_DAY, tick_to_hour
from engine.simulation.engine import SimulationEngine
from engine.whatif.models import NewStoreSpec, WhatIfReport

DEFAULT_SIMULATION_DAYS = 7


def _new_store_poi(graph: nx.MultiDiGraph, spec: NewStoreSpec) -> dict:
    return {
        "node": nearest_node(graph, spec.lon, spec.lat),
        "lon": spec.lon,
        "lat": spec.lat,
        "name": spec.name,
        "category": spec.category,
    }


def run_whatif(
    graph: nx.MultiDiGraph,
    citizens: list[Citizen],
    pois: list[dict],
    new_store: NewStoreSpec,
    llm_client: LLMClient,
    days: int = DEFAULT_SIMULATION_DAYS,
    seed: int | None = None,
) -> WhatIfReport:
    new_store_poi = _new_store_poi(graph, new_store)
    engine = SimulationEngine(
        graph,
        citizens,
        pois,
        seed=seed,
        new_store=new_store_poi,
        llm_client=llm_client,
        decision_cache=DecisionCache(),
    )

    for _ in range(TICKS_PER_DAY * days):
        engine.step()

    return _build_report(engine, new_store_poi["node"], days)


def _build_report(engine: SimulationEngine, new_store_node: int, days: int) -> WhatIfReport:
    total_visits = sum(1 for store_node, _ in engine.visit_log if store_node == new_store_node)

    hourly: dict[int, int] = {}
    for store_node, tick in engine.visit_log:
        if store_node == new_store_node:
            hour = tick_to_hour(tick)
            hourly[hour] = hourly.get(hour, 0) + 1

    source_breakdown: dict[str, int] = {}
    for entry in engine.switch_log:
        source_breakdown[entry["from_store"]] = source_breakdown.get(entry["from_store"], 0) + 1

    return WhatIfReport(
        daily_average_visits=total_visits / days,
        switched_citizens=len(engine.switch_log),
        source_breakdown=source_breakdown,
        hourly_distribution=hourly,
    )
