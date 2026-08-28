from __future__ import annotations

from trafficlight.domain.enums import Colour, MovementGroup, Phase, opposing_group
from trafficlight.domain.models import ControllerStatus, DemandSnapshot, SignalState, TimingConfig
from trafficlight.domain.safety import checked_state
from trafficlight.interfaces.signal_driver import SignalDriver


class BasePhaseController:
    def __init__(self, signals: SignalDriver, timing: TimingConfig | None = None) -> None:
        self.signals = signals
        self.timing = timing or TimingConfig()
        self.phase = Phase.ALL_RED_TO_NS
        self.phase_elapsed_s = 0.0
        self.last_reason = "startup"
        self.target_green_s: float | None = None
        self._apply_phase()

    def tick(self, dt_s: float, demand: DemandSnapshot) -> ControllerStatus:
        if dt_s <= 0:
            raise ValueError("dt_s must be positive")

        self.phase_elapsed_s += dt_s
        if self._should_transition(demand):
            self._transition(demand)
        else:
            self.last_reason = "hold"

        state = self._apply_phase()
        return ControllerStatus(
            phase=self.phase,
            phase_elapsed_s=self.phase_elapsed_s,
            target_green_s=self.target_green_s,
            signal_state=state.copy(),
            reason=self.last_reason,
        )

    def status(self) -> ControllerStatus:
        state = self._apply_phase()
        return ControllerStatus(
            phase=self.phase,
            phase_elapsed_s=self.phase_elapsed_s,
            target_green_s=self.target_green_s,
            signal_state=state.copy(),
            reason=self.last_reason,
        )

    def _should_transition(self, demand: DemandSnapshot) -> bool:
        return self.phase_elapsed_s >= self._phase_duration(demand)

    def _phase_duration(self, demand: DemandSnapshot) -> float:
        raise NotImplementedError

    def _transition(self, demand: DemandSnapshot) -> None:
        previous = self.phase
        self.phase = {
            Phase.ALL_RED_TO_NS: Phase.NS_GREEN,
            Phase.NS_GREEN: Phase.NS_AMBER,
            Phase.NS_AMBER: Phase.ALL_RED_TO_EW,
            Phase.ALL_RED_TO_EW: Phase.EW_GREEN,
            Phase.EW_GREEN: Phase.EW_AMBER,
            Phase.EW_AMBER: Phase.ALL_RED_TO_NS,
        }[self.phase]
        self.phase_elapsed_s = 0.0
        self.last_reason = f"{previous.value}_complete"
        self._set_target_green(demand)

    def _set_target_green(self, demand: DemandSnapshot) -> None:
        if self.phase is Phase.NS_GREEN:
            self.target_green_s = self._target_green_for(MovementGroup.NORTH_SOUTH, demand)
        elif self.phase is Phase.EW_GREEN:
            self.target_green_s = self._target_green_for(MovementGroup.EAST_WEST, demand)
        else:
            self.target_green_s = None

    def _target_green_for(self, group: MovementGroup, demand: DemandSnapshot) -> float:
        return self.timing.fixed_green_s

    def _apply_phase(self) -> SignalState:
        if self.phase is Phase.NS_GREEN:
            state = SignalState.for_group(MovementGroup.NORTH_SOUTH, Colour.GREEN)
        elif self.phase is Phase.NS_AMBER:
            state = SignalState.for_group(MovementGroup.NORTH_SOUTH, Colour.AMBER)
        elif self.phase is Phase.EW_GREEN:
            state = SignalState.for_group(MovementGroup.EAST_WEST, Colour.GREEN)
        elif self.phase is Phase.EW_AMBER:
            state = SignalState.for_group(MovementGroup.EAST_WEST, Colour.AMBER)
        else:
            state = SignalState.all_red()

        checked_state(state)
        self.signals.apply(state)
        return state


class FixedTimeController(BasePhaseController):
    def _phase_duration(self, demand: DemandSnapshot) -> float:
        if self.phase in {Phase.NS_GREEN, Phase.EW_GREEN}:
            return self.timing.fixed_green_s
        if self.phase in {Phase.NS_AMBER, Phase.EW_AMBER}:
            return self.timing.amber_s
        return self.timing.all_red_s


class AdaptiveController(BasePhaseController):
    def _should_transition(self, demand: DemandSnapshot) -> bool:
        if self.phase in {Phase.NS_GREEN, Phase.EW_GREEN}:
            if self.phase_elapsed_s < self.timing.min_green_s:
                self.last_reason = "minimum_green"
                return False
            if self.phase_elapsed_s >= self.timing.max_green_s:
                self.last_reason = "maximum_green"
                return True
            active_group = (
                MovementGroup.NORTH_SOUTH
                if self.phase is Phase.NS_GREEN
                else MovementGroup.EAST_WEST
            )
            opposing = demand.for_group(opposing_group(active_group))
            active = demand.for_group(active_group)
            if active <= 0 and opposing > 0:
                self.last_reason = "no_active_demand"
                return True
        return self.phase_elapsed_s >= self._phase_duration(demand)

    def _phase_duration(self, demand: DemandSnapshot) -> float:
        if self.phase in {Phase.NS_GREEN, Phase.EW_GREEN}:
            active_group = (
                MovementGroup.NORTH_SOUTH
                if self.phase is Phase.NS_GREEN
                else MovementGroup.EAST_WEST
            )
            self.target_green_s = self._target_green_for(active_group, demand)
            return self.target_green_s
        if self.phase in {Phase.NS_AMBER, Phase.EW_AMBER}:
            return self.timing.amber_s
        return self.timing.all_red_s

    def _target_green_for(self, group: MovementGroup, demand: DemandSnapshot) -> float:
        active = max(demand.for_group(group), 0.0)
        opposing = max(demand.for_group(opposing_group(group)), 0.0)
        total = active + opposing
        if total <= 0:
            return self.timing.min_green_s

        pressure = active / total
        span = self.timing.max_green_s - self.timing.min_green_s
        target = self.timing.min_green_s + (pressure * span)
        return min(max(target, self.timing.min_green_s), self.timing.max_green_s)

