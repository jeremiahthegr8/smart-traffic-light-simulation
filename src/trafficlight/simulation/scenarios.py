from dataclasses import dataclass

from trafficlight.domain.enums import Approach


@dataclass(frozen=True)
class Scenario:
    name: str
    arrivals_per_minute: dict[Approach, float]


SCENARIOS: dict[str, Scenario] = {
    "balanced": Scenario(
        name="balanced",
        arrivals_per_minute={
            Approach.NORTH: 10,
            Approach.SOUTH: 10,
            Approach.EAST: 10,
            Approach.WEST: 10,
        },
    ),
    "ns-heavy": Scenario(
        name="ns-heavy",
        arrivals_per_minute={
            Approach.NORTH: 18,
            Approach.SOUTH: 17,
            Approach.EAST: 6,
            Approach.WEST: 5,
        },
    ),
    "ew-heavy": Scenario(
        name="ew-heavy",
        arrivals_per_minute={
            Approach.NORTH: 6,
            Approach.SOUTH: 5,
            Approach.EAST: 18,
            Approach.WEST: 17,
        },
    ),
}

