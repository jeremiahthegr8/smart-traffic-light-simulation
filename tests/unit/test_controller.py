from trafficlight.domain.adaptive import AdaptiveController
from trafficlight.domain.enums import Approach, Colour, Phase
from trafficlight.domain.fixed_time import FixedTimeController
from trafficlight.domain.models import DemandSnapshot, TimingConfig
from trafficlight.domain.safety import assert_no_conflicting_greens
from trafficlight.simulation.signals import SimulatedSignalDriver


def demand(ns: float = 0, ew: float = 0) -> DemandSnapshot:
    return DemandSnapshot(north=ns, south=ns, east=ew, west=ew)


def test_controller_starts_all_red() -> None:
    signals = SimulatedSignalDriver()
    controller = FixedTimeController(signals, TimingConfig(fixed_green_s=8))

    status = controller.status()

    assert status.phase is Phase.ALL_RED_TO_NS
    assert all(colour is Colour.RED for colour in status.signal_state.colours.values())


def test_fixed_time_controller_uses_clearance_sequence() -> None:
    signals = SimulatedSignalDriver()
    controller = FixedTimeController(
        signals,
        TimingConfig(min_green_s=2, fixed_green_s=2, max_green_s=4, amber_s=1, all_red_s=1),
    )

    phases = []
    for _ in range(10):
        status = controller.tick(1, demand())
        phases.append(status.phase)
        assert_no_conflicting_greens(status.signal_state)

    assert phases[:6] == [
        Phase.NS_GREEN,
        Phase.NS_GREEN,
        Phase.NS_AMBER,
        Phase.ALL_RED_TO_EW,
        Phase.EW_GREEN,
        Phase.EW_GREEN,
    ]


def test_adaptive_controller_never_exceeds_max_green() -> None:
    signals = SimulatedSignalDriver()
    controller = AdaptiveController(
        signals,
        TimingConfig(min_green_s=2, fixed_green_s=2, max_green_s=4, amber_s=1, all_red_s=1),
    )

    controller.tick(1, demand(ns=20, ew=0))
    assert controller.status().phase is Phase.NS_GREEN

    for _ in range(5):
        status = controller.tick(1, demand(ns=20, ew=0))

    assert status.phase is not Phase.NS_GREEN


def test_adaptive_target_green_increases_with_active_demand() -> None:
    signals = SimulatedSignalDriver()
    controller = AdaptiveController(
        signals,
        TimingConfig(min_green_s=10, fixed_green_s=10, max_green_s=40, amber_s=1, all_red_s=1),
    )

    controller.tick(1, demand(ns=30, ew=5))
    status = controller.tick(1, demand(ns=30, ew=5))

    assert status.target_green_s is not None
    assert status.target_green_s > 25
    assert status.signal_state.colour_for(Approach.NORTH) is Colour.GREEN
    assert status.signal_state.colour_for(Approach.EAST) is Colour.RED


def test_adaptive_reports_early_transition_reason() -> None:
    signals = SimulatedSignalDriver()
    controller = AdaptiveController(
        signals,
        TimingConfig(min_green_s=2, fixed_green_s=2, max_green_s=8, amber_s=1, all_red_s=1),
    )

    controller.tick(1, demand(ns=10, ew=0))
    controller.tick(1, demand(ns=10, ew=0))
    status = controller.tick(1, demand(ns=0, ew=10))

    assert status.phase is Phase.NS_AMBER
    assert status.reason == "no_active_demand"
