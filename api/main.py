"""FastAPI + WebSocket 실시간 시뮬레이션 스트리밍."""
from __future__ import annotations

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from engine.config import DEMO_REGION
from engine.network.graph import load_or_build_graph
from engine.population.db_source import load_age_gender_weights
from engine.population.generator import generate_citizens
from engine.simulation.engine import SimulationEngine
from engine.simulation.poi import load_or_build_pois

TICK_INTERVAL_SEC = 0.2
NUM_CITIZENS = 1000

app = FastAPI()


@app.get("/")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket) -> None:
    await websocket.accept()

    graph = load_or_build_graph()
    weights = load_age_gender_weights()
    citizens = generate_citizens(NUM_CITIZENS, weights, graph, seed=42)
    pois = load_or_build_pois(DEMO_REGION, graph)
    sim = SimulationEngine(graph, citizens, pois, seed=7)

    try:
        while True:
            sim.step()
            await websocket.send_json(sim.to_geojson_snapshot())
            await asyncio.sleep(TICK_INTERVAL_SEC)
    except WebSocketDisconnect:
        pass
