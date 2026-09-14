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

    profiles = client.get("/api/fault-profiles").json()
    assert "ns-stuck-high" in profiles


def test_create_simulation_persists_run_and_metrics(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "api.sqlite"))

    response = client.post(
        "/api/simulations",
        json={
            "controller": "adaptive",
            "scenario": "balanced",
            "fault_profile": "ew-stuck-low",
            "duration_s": 20,
            "step_s": 1,
            "seed": 5,
        },
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["conflicting_green_violations"] == 0
    assert summary["sensor_faults"][0]["name"] == "ew-stuck-low"

    runs = client.get("/api/runs").json()
    assert len(runs) == 1
    assert runs[0]["scenario"] == "balanced"

    metrics = client.get(f"/api/runs/{runs[0]['id']}/metrics").json()
    assert len(metrics) > 0


def test_create_custom_simulation_uses_dashboard_arrival_rates(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "api.sqlite"))

    response = client.post(
        "/api/simulations",
        json={
            "controller": "adaptive",
            "scenario": "custom-dashboard",
            "duration_s": 30,
            "step_s": 1,
            "seed": 5,
            "persist": False,
            "custom_arrivals_per_minute": {
                "north": 24,
                "east": 2,
                "south": 22,
                "west": 2,
            },
        },
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["scenario"] == "custom-dashboard"
    assert summary["arrivals"] > 0
    assert summary["conflicting_green_violations"] == 0


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
        "/ws/simulation?controller=adaptive&scenario=balanced&duration_s=5&step_s=1&seed=1&fault_profile=ns-stuck-high"
    ) as websocket:
        first = websocket.receive_json()
        assert first["type"] == "step"
        assert first["phase"]
        assert first["demand"]["north"] == 80

        message = first
        while message["type"] != "summary":
            message = websocket.receive_json()

    assert message["summary"]["conflicting_green_violations"] == 0


def test_websocket_stream_accepts_custom_rates(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "api.sqlite"))

    with client.websocket_connect(
        "/ws/simulation?controller=adaptive&scenario=custom-dashboard&duration_s=5&step_s=1&seed=1&persist=false"
        "&custom_north=30&custom_east=0&custom_south=30&custom_west=0"
    ) as websocket:
        first = websocket.receive_json()
        assert first["type"] == "step"
        assert set(first["queues"]) == {"north", "east", "south", "west"}

        message = first
        while message["type"] != "summary":
            message = websocket.receive_json()

    assert message["summary"]["scenario"] == "custom-dashboard"
