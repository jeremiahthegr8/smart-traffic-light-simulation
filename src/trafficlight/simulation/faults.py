from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import inf

from trafficlight.domain.enums import Approach
from trafficlight.domain.models import DemandSnapshot


class FaultMode(StrEnum):
    STUCK_HIGH = "stuck_high"
    STUCK_LOW = "stuck_low"


@dataclass(frozen=True)
class SensorFault:
    name: str
    mode: FaultMode
    approaches: tuple[Approach, ...]
    start_s: float = 0.0
    end_s: float = inf
    value: float = 80.0

    def applies_at(self, timestamp_s: float) -> bool:
        return self.start_s <= timestamp_s < self.end_s

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "mode": self.mode.value,
            "approaches": [approach.value for approach in self.approaches],
            "start_s": self.start_s,
            "end_s": None if self.end_s == inf else self.end_s,
            "value": self.value,
        }


def apply_sensor_faults(
    snapshot: DemandSnapshot,
    faults: tuple[SensorFault, ...] = (),
) -> DemandSnapshot:
    values = {
        Approach.NORTH: snapshot.north,
        Approach.EAST: snapshot.east,
        Approach.SOUTH: snapshot.south,
        Approach.WEST: snapshot.west,
    }
    for fault in faults:
        if not fault.applies_at(snapshot.timestamp):
            continue
        for approach in fault.approaches:
            if fault.mode is FaultMode.STUCK_HIGH:
                values[approach] = fault.value
            elif fault.mode is FaultMode.STUCK_LOW:
                values[approach] = 0.0

    return DemandSnapshot(
        north=values[Approach.NORTH],
        east=values[Approach.EAST],
        south=values[Approach.SOUTH],
        west=values[Approach.WEST],
        timestamp=snapshot.timestamp,
    )


def fault_profiles(duration_s: float) -> dict[str, tuple[SensorFault, ...]]:
    halfway = duration_s / 2
    return {
        "none": (),
        "ns-stuck-high": (
            SensorFault(
                name="ns-stuck-high",
                mode=FaultMode.STUCK_HIGH,
                approaches=(Approach.NORTH, Approach.SOUTH),
                start_s=0,
                end_s=duration_s,
                value=80,
            ),
        ),
        "ew-stuck-low": (
            SensorFault(
                name="ew-stuck-low",
                mode=FaultMode.STUCK_LOW,
                approaches=(Approach.EAST, Approach.WEST),
                start_s=0,
                end_s=duration_s,
            ),
        ),
        "all-stuck-low-midrun": (
            SensorFault(
                name="all-stuck-low-midrun",
                mode=FaultMode.STUCK_LOW,
                approaches=(Approach.NORTH, Approach.EAST, Approach.SOUTH, Approach.WEST),
                start_s=halfway,
                end_s=duration_s,
            ),
        ),
    }

