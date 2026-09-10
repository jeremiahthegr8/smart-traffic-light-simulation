import random

from trafficlight.domain.adaptive import AdaptiveController
from trafficlight.domain.fixed_time import FixedTimeController
from trafficlight.domain.models import TimingConfig
from trafficlight.simulation.engine import ApproachQueue, SimulationEngine
from trafficlight.simulation.scenarios import SCENARIOS
from trafficlight.simulation.signals import SimulatedSignalDriver


def run(controller_name: str):
    signals = SimulatedSignalDriver()
    timing = TimingConfig(min_green_s=4, fixed_green_s=12, max_green_s=24, amber_s=2, all_red_s=1)
    controller = (
        FixedTimeController(signals, timing)
        if controller_name == "fixed"
        else AdaptiveController(signals, timing)
    )
    return SimulationEngine(
        SCENARIOS["ns-heavy"],
        controller_name,
        controller,
        duration_s=180,
        step_s=0.5,
        seed=7,
    ).run()


def test_simulation_records_zero_conflicting_greens() -> None:
    summary = run("adaptive")

    assert summary.conflicting_green_violations == 0
    assert summary.arrivals > 0
    assert summary.completed > 0


def test_adaptive_is_comparable_to_fixed_on_same_seed() -> None:
    fixed = run("fixed")
    adaptive = run("adaptive")

    assert fixed.arrivals == adaptive.arrivals
    assert fixed.conflicting_green_violations == 0
    assert adaptive.conflicting_green_violations == 0


def test_arrival_generation_matches_configured_rate_over_many_runs() -> None:
    duration_s = 3600
    step_s = 1
    rate_per_minute = 18
    expected = rate_per_minute * (duration_s / 60)
    totals = []

    for seed in range(50):
        queue = ApproachQueue()
        rng = random.Random(seed)
        elapsed = 0.0
        while elapsed < duration_s:
            queue.add_arrivals(rate_per_minute, step_s, rng, elapsed)
            elapsed += step_s
        totals.append(queue.total_arrivals)

    observed = sum(totals) / len(totals)
    assert abs(observed - expected) / expected < 0.05


def test_reported_mean_wait_is_completed_vehicle_wait() -> None:
    summary = run("adaptive")

    assert 0 <= summary.mean_wait_s <= summary.duration_s
    assert sum(summary.final_queues.values()) == summary.arrivals - summary.completed
