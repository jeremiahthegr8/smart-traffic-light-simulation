import json

from trafficlight.domain.adaptive import AdaptiveController
from trafficlight.domain.models import TimingConfig
from trafficlight.simulation.engine import SimulationEngine
from trafficlight.simulation.scenarios import SCENARIOS
from trafficlight.simulation.signals import SimulatedSignalDriver
from trafficlight.storage.database import connect_database
from trafficlight.storage.repository import SQLiteSimulationLogger, row_counts


def test_simulation_writes_run_samples_events_and_summary(tmp_path) -> None:
    connection = connect_database(tmp_path / "trafficlight.sqlite")
    logger = SQLiteSimulationLogger(connection, sample_interval_s=1.0)
    signals = SimulatedSignalDriver()
    controller = AdaptiveController(
        signals,
        TimingConfig(min_green_s=4, fixed_green_s=8, max_green_s=12, amber_s=2, all_red_s=1),
    )

    summary = SimulationEngine(
        SCENARIOS["balanced"],
        "adaptive",
        controller,
        duration_s=30,
        step_s=0.5,
        seed=11,
        logger=logger,
    ).run()

    run = connection.execute("SELECT * FROM runs").fetchone()
    assert run["status"] == "completed"
    assert run["scenario"] == "balanced"
    assert run["controller"] == "adaptive"
    assert json.loads(run["config_json"])["seed"] == 11
    assert json.loads(run["summary_json"])["arrivals"] == summary.arrivals

    counts = row_counts(connection, int(run["id"]))
    assert counts["detector_samples"] > 0
    assert counts["traffic_metrics"] > 0
    assert counts["signal_events"] > 0

