import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from trafficlight.api.app import create_app


def test_health_and_scenarios(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "api.sqlite"))

    assert client.get("/").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}

    scenarios = client.get("/api/scenarios").json()
    assert "ns-heavy" in scenarios
    assert scenarios["ns-heavy"]["arrivals_per_minute"]["north"] > 0


def test_create_simulation_persists_run_and_metrics(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "api.sqlite"))

    response = client.post(
        "/api/simulations",
        json={
            "controller": "adaptive",
            "scenario": "balanced",
            "duration_s": 20,
            "step_s": 1,
            "seed": 5,
        },
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["conflicting_green_violations"] == 0

    runs = client.get("/api/runs").json()
    assert len(runs) == 1
    assert runs[0]["scenario"] == "balanced"

    metrics = client.get(f"/api/runs/{runs[0]['id']}/metrics").json()
    assert len(metrics) > 0


def test_create_benchmark_compares_fixed_and_adaptive(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "api.sqlite"))

    response = client.post(
        "/api/benchmarks",
        json={"scenarios": ["ns-heavy"], "seeds": [3], "duration_s": 40, "step_s": 1},
    )

    assert response.status_code == 200
    rows = response.json()["rows"]
    assert [row["controller"] for row in rows] == ["fixed", "adaptive"]
    assert rows[0]["arrivals"] == rows[1]["arrivals"]
    assert rows[1]["mean_wait_improvement_pct"] is not None


def test_websocket_stream_sends_steps_and_summary(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "api.sqlite"))

    with client.websocket_connect(
        "/ws/simulation?controller=adaptive&scenario=balanced&duration_s=5&step_s=1&seed=1"
    ) as websocket:
        first = websocket.receive_json()
        assert first["type"] == "step"
        assert first["phase"]

        message = first
        while message["type"] != "summary":
            message = websocket.receive_json()

    assert message["summary"]["conflicting_green_violations"] == 0
