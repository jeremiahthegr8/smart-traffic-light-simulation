from __future__ import annotations

from dataclasses import dataclass, field

from trafficlight.domain.enums import APPROACHES, GROUP_APPROACHES, Approach, Colour, MovementGroup, Phase


@dataclass(frozen=True)
class DemandSnapshot:
    north: float
    east: float
    south: float
    west: float
    timestamp: float = 0.0

    def for_approach(self, approach: Approach) -> float:
        return {
            Approach.NORTH: self.north,
            Approach.EAST: self.east,
            Approach.SOUTH: self.south,
            Approach.WEST: self.west,
        }[approach]

    def for_group(self, group: MovementGroup) -> float:
        return sum(self.for_approach(approach) for approach in GROUP_APPROACHES[group])


@dataclass(frozen=True)
class TimingConfig:
    min_green_s: float = 8.0
    fixed_green_s: float = 20.0
    max_green_s: float = 45.0
    amber_s: float = 3.0
    all_red_s: float = 2.0

    def __post_init__(self) -> None:
        if self.min_green_s <= 0:
            raise ValueError("min_green_s must be positive")
        if self.fixed_green_s < self.min_green_s:
            raise ValueError("fixed_green_s must be >= min_green_s")
        if self.max_green_s < self.min_green_s:
            raise ValueError("max_green_s must be >= min_green_s")
        if self.amber_s <= 0:
            raise ValueError("amber_s must be positive")
        if self.all_red_s <= 0:
            raise ValueError("all_red_s must be positive")


@dataclass(frozen=True)
class ControllerStatus:
    phase: Phase
    phase_elapsed_s: float
    target_green_s: float | None
    signal_state: "SignalState"
    reason: str = "hold"


@dataclass
class SignalState:
    colours: dict[Approach, Colour] = field(
        default_factory=lambda: {approach: Colour.RED for approach in APPROACHES}
    )

    @classmethod
    def all_red(cls) -> "SignalState":
        return cls()

    @classmethod
    def for_group(cls, group: MovementGroup, colour: Colour) -> "SignalState":
        state = cls.all_red()
        for approach in GROUP_APPROACHES[group]:
            state.colours[approach] = colour
        return state

    def colour_for(self, approach: Approach) -> Colour:
        return self.colours[approach]

    def green_approaches(self) -> tuple[Approach, ...]:
        return tuple(
            approach for approach, colour in self.colours.items() if colour is Colour.GREEN
        )

    def copy(self) -> "SignalState":
        return SignalState(dict(self.colours))

