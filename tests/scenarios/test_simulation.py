from trafficlight.domain.adaptive import AdaptiveController
from trafficlight.domain.fixed_time import FixedTimeController
from trafficlight.domain.models import TimingConfig
from trafficlight.simulation.engine import SimulationEngine
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

