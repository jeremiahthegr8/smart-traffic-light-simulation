from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Callable

from trafficlight.domain.adaptive import AdaptiveController
from trafficlight.domain.enums import Approach
from trafficlight.domain.fixed_time import FixedTimeController
from trafficlight.domain.models import TimingConfig
from trafficlight.simulation.engine import SimulationEngine
from trafficlight.simulation.faults import SensorFault
from trafficlight.simulation.scenarios import SCENARIOS, Scenario
from trafficlight.simulation.signals import SimulatedSignalDriver
from trafficlight.storage.database import connect_database
from trafficlight.storage.repository import SQLiteSimulationLogger


StepObserver = Callable[[dict], None]


def build_controller(controller_name: str, timing: TimingConfig, signals: SimulatedSignalDriver):
    if controller_name == "fixed":
        return FixedTimeController(signals, timing)
    if controller_name == "adaptive":
        return AdaptiveController(signals, timing)
    raise ValueError(f"unknown controller: {controller_name}")


def run_simulation(
    *,
    controller_name: str,
    scenario_name: str,
    duration_s: float,
    step_s: float,
    seed: int,
    db_path: Path | None = None,
    sample_interval_s: float = 1.0,
    on_step: StepObserver | None = None,
    sensor_faults: tuple[SensorFault, ...] = (),
    custom_arrivals_per_minute: dict[str, float] | None = None,
) -> dict:
    scenario = _resolve_scenario(scenario_name, custom_arrivals_per_minute)
    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    if step_s <= 0:
        raise ValueError("step_s must be positive")

    signals = SimulatedSignalDriver()
    timing = TimingConfig()
    controller = build_controller(controller_name, timing, signals)

    connection = None
    logger = None
    if db_path is not None:
        connection = connect_database(db_path)
        logger = SQLiteSimulationLogger(connection, sample_interval_s=sample_interval_s)

    try:
        engine = SimulationEngine(
            scenario,
            controller_name,
            controller,
            duration_s=duration_s,
            step_s=step_s,
            seed=seed,
            logger=logger,
            on_step=on_step,
            sensor_faults=sensor_faults,
        )
        return asdict(engine.run())
    finally:
        if connection is not None:
            connection.close()


def _resolve_scenario(
    scenario_name: str,
    custom_arrivals_per_minute: dict[str, float] | None,
) -> Scenario:
    if custom_arrivals_per_minute is None:
        if scenario_name not in SCENARIOS:
            raise ValueError(f"unknown scenario: {scenario_name}")
        return SCENARIOS[scenario_name]

    arrivals = {}
    for approach in Approach:
        if approach.value not in custom_arrivals_per_minute:
            raise ValueError(f"missing custom arrival rate for {approach.value}")
        rate = float(custom_arrivals_per_minute[approach.value])
        if rate < 0:
            raise ValueError("custom arrival rates must be non-negative")
        arrivals[approach] = rate

    return Scenario(
        name=scenario_name,
        description="Custom dashboard scenario.",
        arrivals_per_minute=arrivals,
    )
