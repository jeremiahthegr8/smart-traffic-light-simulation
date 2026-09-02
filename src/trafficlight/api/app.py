from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi import Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from trafficlight.simulation.benchmark import (
    aggregate_benchmark,
    benchmark_rows_to_dicts,
    run_benchmark,
)
from trafficlight.simulation.scenarios import SCENARIOS
from trafficlight.simulation.runner import run_simulation
from trafficlight.storage.database import connect_database
from trafficlight.storage.repository import get_run, list_metrics, list_runs


DASHBOARD_DIR = Path(__file__).resolve().parents[1] / "dashboard"


class SimulationRequest(BaseModel):
    controller: str = Field(default="adaptive", pattern="^(fixed|adaptive)$")
    scenario: str = "ns-heavy"
    duration_s: float = Field(default=300.0, gt=0, le=7200)
    step_s: float = Field(default=0.5, gt=0, le=10)
    seed: int = 42
    persist: bool = True


class BenchmarkRequest(BaseModel):
    scenarios: list[str] = Field(default_factory=lambda: list(SCENARIOS))
    seeds: list[int] = Field(default_factory=lambda: [42])
    duration_s: float = Field(default=300.0, gt=0, le=7200)
    step_s: float = Field(default=0.5, gt=0, le=10)


def create_app(db_path: str | Path = "trafficlight.db") -> FastAPI:
    app = FastAPI(title="Smart Traffic-Light API", version="0.1.0")
    app.state.db_path = Path(db_path)
    app.mount("/static", StaticFiles(directory=DASHBOARD_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(DASHBOARD_DIR / "index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/scenarios")
    def scenarios() -> dict:
        return {
            name: {
                "description": scenario.description,
                "arrivals_per_minute": {
                    approach.value: rate
                    for approach, rate in scenario.arrivals_per_minute.items()
                },
                "demand_windows": [
                    {
                        "start_s": window.start_s,
                        "end_s": window.end_s,
                        "arrivals_per_minute": {
                            approach.value: rate
                            for approach, rate in window.arrivals_per_minute.items()
                        },
                    }
                    for window in scenario.demand_windows
                ],
            }
            for name, scenario in SCENARIOS.items()
        }

    @app.post("/api/simulations")
    def create_simulation(request: SimulationRequest) -> dict:
        if request.scenario not in SCENARIOS:
            raise HTTPException(status_code=404, detail="Unknown scenario")
        return run_simulation(
            controller_name=request.controller,
            scenario_name=request.scenario,
            duration_s=request.duration_s,
            step_s=request.step_s,
            seed=request.seed,
            db_path=app.state.db_path if request.persist else None,
        )

    @app.post("/api/benchmarks")
    def create_benchmark(request: BenchmarkRequest) -> dict:
        try:
            rows = run_benchmark(
                scenarios=request.scenarios,
                seeds=request.seeds,
                duration_s=request.duration_s,
                step_s=request.step_s,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "rows": benchmark_rows_to_dicts(rows),
            "aggregates": aggregate_benchmark(rows),
        }

    @app.get("/api/runs")
    def runs(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
        with connect_database(app.state.db_path) as connection:
            return list_runs(connection, limit=limit)

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: int) -> dict:
        with connect_database(app.state.db_path) as connection:
            run = get_run(connection, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return run

    @app.get("/api/runs/{run_id}/metrics")
    def run_metrics(
        run_id: int,
        limit: int = Query(default=500, ge=1, le=5000),
    ) -> list[dict]:
        with connect_database(app.state.db_path) as connection:
            if get_run(connection, run_id) is None:
                raise HTTPException(status_code=404, detail="Run not found")
            return list_metrics(connection, run_id, limit=limit)

    @app.websocket("/ws/simulation")
    async def simulation_stream(
        websocket: WebSocket,
        controller: str = "adaptive",
        scenario: str = "ns-heavy",
        duration_s: float = 60.0,
        step_s: float = 1.0,
        seed: int = 42,
        persist: bool = True,
    ) -> None:
        await websocket.accept()
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[dict] = asyncio.Queue()

        def publish(message: dict) -> None:
            loop.call_soon_threadsafe(queue.put_nowait, message)

        def execute() -> None:
            try:
                summary = run_simulation(
                    controller_name=controller,
                    scenario_name=scenario,
                    duration_s=duration_s,
                    step_s=step_s,
                    seed=seed,
                    db_path=app.state.db_path if persist else None,
                    on_step=publish,
                )
                publish({"type": "summary", "summary": summary})
            except ValueError as exc:
                publish({"type": "error", "detail": str(exc)})

        task = loop.run_in_executor(None, execute)
        try:
            while True:
                message = await queue.get()
                if message["type"] == "error":
                    await websocket.send_json(message)
                    await websocket.close(code=1008)
                    break
                await websocket.send_json(message)
                if message["type"] == "summary":
                    break
            await task
        except WebSocketDisconnect:
            task.cancel()

    @app.websocket("/ws/simulation/replay")
    async def simulation_replay(
        websocket: WebSocket,
        controller: str = "adaptive",
        scenario: str = "ns-heavy",
        duration_s: float = 60.0,
        step_s: float = 1.0,
        seed: int = 42,
    ) -> None:
        await websocket.accept()
        try:
            messages: list[dict] = []
            summary = run_simulation(
                controller_name=controller,
                scenario_name=scenario,
                duration_s=duration_s,
                step_s=step_s,
                seed=seed,
                db_path=None,
                on_step=messages.append,
            )
            for message in messages:
                await websocket.send_json(message)
            await websocket.send_json({"type": "summary", "summary": summary})
        except (ValueError, WebSocketDisconnect):
            await websocket.close(code=1008)

    return app


app = create_app()
