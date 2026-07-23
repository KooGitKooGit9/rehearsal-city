"""FastAPI + WebSocket 실시간 시뮬레이션 스트리밍 + what-if REST 엔드포인트."""
from __future__ import annotations

import asyncio
from dataclasses import asdict

import networkx as nx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.config import DEMO_REGION
from engine.decision.gemini_client import GeminiLLMClient
from engine.network.graph import load_or_build_graph
from engine.population.db_source import load_age_gender_weights
from engine.population.generator import generate_citizens
from engine.population.models import Citizen
from engine.simulation.engine import SimulationEngine
from engine.simulation.poi import load_or_build_pois
from engine.whatif.models import NewStoreSpec
from engine.whatif.service import run_whatif

TICK_INTERVAL_SEC = 0.2
NUM_CITIZENS = 1000

app = FastAPI()

# 개발 중인 웹 대시보드(Vite, localhost:5173)에서 /api/whatif를 호출하려면 CORS 허용 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_world() -> tuple[nx.MultiDiGraph, list[Citizen], list[dict]]:
    graph = load_or_build_graph()
    weights = load_age_gender_weights()
    citizens = generate_citizens(NUM_CITIZENS, weights, graph, seed=42)
    pois = load_or_build_pois(DEMO_REGION, graph)
    return graph, citizens, pois


@app.get("/")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket) -> None:
    await websocket.accept()

    graph, citizens, pois = _load_world()
    sim = SimulationEngine(graph, citizens, pois, seed=7)

    try:
        while True:
            sim.step()
            await websocket.send_json(sim.to_geojson_snapshot())
            await asyncio.sleep(TICK_INTERVAL_SEC)
    except WebSocketDisconnect:
        pass


class WhatIfRequest(BaseModel):
    lon: float
    lat: float
    name: str
    category: str


@app.post("/api/whatif")
def whatif(req: WhatIfRequest) -> dict:
    graph, citizens, pois = _load_world()
    new_store = NewStoreSpec(lon=req.lon, lat=req.lat, name=req.name, category=req.category)
    report = run_whatif(graph, citizens, pois, new_store, GeminiLLMClient(), seed=7)
    return asdict(report)
