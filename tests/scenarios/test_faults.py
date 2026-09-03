from trafficlight.domain.enums import Approach
from trafficlight.domain.models import DemandSnapshot
from trafficlight.simulation.faults import FaultMode, SensorFault, apply_sensor_faults, fault_profiles
from trafficlight.simulation.runner import run_simulation


def test_sensor_faults_modify_detector_demand_without_changing_timestamp() -> None:
    snapshot = DemandSnapshot(north=4, east=5, south=6, west=7, timestamp=12)
    faults = (
        SensorFault(
            name="north-high",
            mode=FaultMode.STUCK_HIGH,
            approaches=(Approach.NORTH,),
            value=80,
        ),
        SensorFault(
            name="east-low",
            mode=FaultMode.STUCK_LOW,
            approaches=(Approach.EAST,),
        ),
    )

    faulted = apply_sensor_faults(snapshot, faults)

    assert faulted.timestamp == 12
    assert faulted.north == 80
    assert faulted.east == 0
    assert faulted.south == 6
    assert faulted.west == 7


def test_faulted_adaptive_runs_keep_zero_conflicting_greens() -> None:
    profiles = fault_profiles(duration_s=60)

    for name, faults in profiles.items():
        summary = run_simulation(
            controller_name="adaptive",
            scenario_name="ns-heavy",
            duration_s=60,
            step_s=1,
            seed=3,
            db_path=None,
            sensor_faults=faults,
        )

        assert summary["sensor_faults"] == [fault.to_dict() for fault in faults]
        assert summary["conflicting_green_violations"] == 0, name
        assert summary["arrivals"] > 0

