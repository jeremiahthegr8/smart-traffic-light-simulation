from dataclasses import dataclass

from trafficlight.domain.enums import Approach


@dataclass(frozen=True)
class DemandWindow:
    start_s: float
    end_s: float
    arrivals_per_minute: dict[Approach, float]

    def includes(self, timestamp_s: float) -> bool:
        return self.start_s <= timestamp_s < self.end_s


@dataclass(frozen=True)
class Scenario:
    name: str
    arrivals_per_minute: dict[Approach, float]
    description: str = ""
    demand_windows: tuple[DemandWindow, ...] = ()

    def arrival_rate_for(self, approach: Approach, timestamp_s: float) -> float:
        for window in self.demand_windows:
            if window.includes(timestamp_s):
                return window.arrivals_per_minute.get(
                    approach,
                    self.arrivals_per_minute[approach],
                )
        return self.arrivals_per_minute[approach]


SCENARIOS: dict[str, Scenario] = {
    "balanced": Scenario(
        name="balanced",
        description="Similar demand on all four approaches.",
        arrivals_per_minute={
            Approach.NORTH: 10,
            Approach.SOUTH: 10,
            Approach.EAST: 10,
            Approach.WEST: 10,
        },
    ),
    "ns-heavy": Scenario(
        name="ns-heavy",
        description="North/South demand is much higher than East/West demand.",
        arrivals_per_minute={
            Approach.NORTH: 18,
            Approach.SOUTH: 17,
            Approach.EAST: 6,
            Approach.WEST: 5,
        },
    ),
    "ew-heavy": Scenario(
        name="ew-heavy",
        description="East/West demand is much higher than North/South demand.",
        arrivals_per_minute={
            Approach.NORTH: 6,
            Approach.SOUTH: 5,
            Approach.EAST: 18,
            Approach.WEST: 17,
        },
    ),
    "ns-burst": Scenario(
        name="ns-burst",
        description="A short North/South demand surge appears during otherwise moderate traffic.",
        arrivals_per_minute={
            Approach.NORTH: 8,
            Approach.SOUTH: 8,
            Approach.EAST: 7,
            Approach.WEST: 7,
        },
        demand_windows=(
            DemandWindow(
                start_s=60,
                end_s=180,
                arrivals_per_minute={
                    Approach.NORTH: 28,
                    Approach.SOUTH: 26,
                    Approach.EAST: 6,
                    Approach.WEST: 6,
                },
            ),
        ),
    ),
    "alternating-peak": Scenario(
        name="alternating-peak",
        description="Demand shifts from North/South to East/West halfway through the run.",
        arrivals_per_minute={
            Approach.NORTH: 8,
            Approach.SOUTH: 8,
            Approach.EAST: 8,
            Approach.WEST: 8,
        },
        demand_windows=(
            DemandWindow(
                start_s=0,
                end_s=150,
                arrivals_per_minute={
                    Approach.NORTH: 22,
                    Approach.SOUTH: 20,
                    Approach.EAST: 5,
                    Approach.WEST: 5,
                },
            ),
            DemandWindow(
                start_s=150,
                end_s=300,
                arrivals_per_minute={
                    Approach.NORTH: 5,
                    Approach.SOUTH: 5,
                    Approach.EAST: 22,
                    Approach.WEST: 20,
                },
            ),
        ),
    ),
}
