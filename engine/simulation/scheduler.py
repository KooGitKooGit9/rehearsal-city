"""규칙 기반 일과 스케줄러: 집→직장→(여가)→집 활동 전이.

LLM을 쓰지 않는다 — 시각은 정규분포 지터링, 여가 여부는 확률로 결정한다 (CLAUDE.md 원칙 1).
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

import networkx as nx

from engine.network.routing import shortest_path_between_nodes
from engine.simulation.clock import TICKS_PER_DAY
from engine.simulation.state import (
    ACTIVITY_COMMUTING,
    ACTIVITY_HOME,
    ACTIVITY_LEISURE,
    ACTIVITY_RETURNING,
    ACTIVITY_WORK,
    CitizenState,
)

LEISURE_STOP_PROBABILITY = 0.3
LEISURE_DWELL_TICKS = 3  # 30분 체류

# 출퇴근 시각 지터링 기준(틱). 08:00=48틱, 18:00=108틱
LEAVE_HOME_MEAN_TICK = 48
LEAVE_HOME_JITTER_TICKS = 6
LEAVE_WORK_MEAN_TICK = 108
LEAVE_WORK_JITTER_TICKS = 6

# (lon, lat, rng) -> (store_node, store_lon, store_lat)
PickStoreFn = Callable[[float, float, random.Random], tuple[int, float, float]]


@dataclass(frozen=True)
class DailySchedule:
    leave_home_tick: int
    leave_work_tick: int
    workplace_node: int
    has_leisure_stop: bool


def generate_schedule(home_node: int, graph: nx.MultiDiGraph, rng: random.Random) -> DailySchedule:
    leave_home_tick = _clamp_tick(round(rng.gauss(LEAVE_HOME_MEAN_TICK, LEAVE_HOME_JITTER_TICKS)))
    leave_work_tick = _clamp_tick(round(rng.gauss(LEAVE_WORK_MEAN_TICK, LEAVE_WORK_JITTER_TICKS)))
    leave_work_tick = max(leave_work_tick, leave_home_tick + 1)

    workplace_node = rng.choice([n for n in graph.nodes if n != home_node])
    has_leisure_stop = rng.random() < LEISURE_STOP_PROBABILITY

    return DailySchedule(
        leave_home_tick=leave_home_tick,
        leave_work_tick=leave_work_tick,
        workplace_node=workplace_node,
        has_leisure_stop=has_leisure_stop,
    )


def _clamp_tick(tick: int) -> int:
    return max(0, min(TICKS_PER_DAY - 1, tick))


def decide_activity(
    state: CitizenState,
    schedule: DailySchedule,
    tick: int,
    graph: nx.MultiDiGraph,
    pick_store: PickStoreFn,
    rng: random.Random,
) -> None:
    """활동 전이 규칙. 한 틱 안에서 이동(movement.advance_along_path)보다 먼저 호출한다."""
    arrived = len(state.path) <= 1

    if state.activity == ACTIVITY_HOME and tick >= schedule.leave_home_tick:
        state.path = shortest_path_between_nodes(graph, state.node, schedule.workplace_node) or [state.node]
        state.activity = ACTIVITY_COMMUTING

    elif state.activity == ACTIVITY_COMMUTING and arrived:
        state.activity = ACTIVITY_WORK

    elif state.activity == ACTIVITY_WORK and tick >= schedule.leave_work_tick:
        if schedule.has_leisure_stop:
            store_node, _, _ = pick_store(state.lon, state.lat, rng)
            state.path = shortest_path_between_nodes(graph, state.node, store_node) or [state.node]
            state.activity = ACTIVITY_LEISURE
            state.dwell_remaining = LEISURE_DWELL_TICKS
        else:
            state.path = shortest_path_between_nodes(graph, state.node, state.citizen.home_node) or [state.node]
            state.activity = ACTIVITY_RETURNING

    elif state.activity == ACTIVITY_LEISURE and arrived:
        if state.dwell_remaining > 0:
            state.dwell_remaining -= 1
        else:
            state.path = shortest_path_between_nodes(graph, state.node, state.citizen.home_node) or [state.node]
            state.activity = ACTIVITY_RETURNING

    elif state.activity == ACTIVITY_RETURNING and arrived:
        state.activity = ACTIVITY_HOME
