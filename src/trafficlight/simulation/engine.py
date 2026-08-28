from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from trafficlight.domain.enums import APPROACHES, Approach, Colour
from trafficlight.domain.models import DemandSnapshot
from trafficlight.domain.safety import assert_no_conflicting_greens
from trafficlight.interfaces.event_sink import SimulationEventSink
from trafficlight.simulation.scenarios import Scenario


StepObserver = Callable[[dict], None]


@dataclass
class ApproachQueue:
    arrival_rate_per_minute: float
    queue: int = 0
    total_arrivals: int = 0
    total_departures: int = 0
    total_wait_s: float = 0.0
    _arrival_credit: float = 0.0
    _discharge_credit: float = 0.0

    def add_arrivals(self, dt_s: float, rng: random.Random) -> None:
        self._arrival_credit += (self.arrival_rate_per_minute / 60.0) * dt_s
        whole = int(self._arrival_credit)
        self._arrival_credit -= whole
        extra = 1 if rng.random() < self._arrival_credit else 0
        arrivals = whole + extra
        if extra:
            self._arrival_credit = 0.0
        self.queue += arrivals
        self.total_arrivals += arrivals

    def discharge(self, dt_s: float, headway_s: float) -> None:
        if self.queue <= 0:
            self._discharge_credit = 0.0
            return
        self._discharge_credit += dt_s / headway_s
        departures = min(self.queue, int(self._discharge_credit))
        if departures:
            self.queue -= departures
            self.total_departures += departures
            self._discharge_credit -= departures

    def accumulate_wait(self, dt_s: float) -> None:
        self.total_wait_s += self.queue * dt_s


@dataclass(frozen=True)
class SimulationSummary:
    scenario: str
    controller: str
    duration_s: float
    arrivals: int
    completed: int
    throughput_veh_per_min: float
    mean_wait_s: float
    max_queue: int
    conflicting_green_violations: int
    final_queues: dict[str, int] = field(default_factory=dict)


class SimulationEngine:
    def __init__(
        self,
        scenario: Scenario,
        controller_name: str,
        controller,
        *,
        duration_s: float = 300.0,
        step_s: float = 0.5,
        seed: int = 42,
        discharge_headway_s: float = 2.2,
        logger: SimulationEventSink | None = None,
        on_step: StepObserver | None = None,
    ) -> None:
        self.scenario = scenario
        self.controller_name = controller_name
        self.controller = controller
        self.duration_s = duration_s
        self.step_s = step_s
        self.seed = seed
        self.rng = random.Random(seed)
        self.discharge_headway_s = discharge_headway_s
        self.logger = logger
        self.on_step = on_step
        self.queues = {
            approach: ApproachQueue(scenario.arrivals_per_minute[approach])
            for approach in APPROACHES
        }
        self.max_queue = 0
        self.conflicting_green_violations = 0

    def run(self) -> SimulationSummary:
        run_id = self._start_logged_run()
        elapsed = 0.0
        while elapsed < self.duration_s:
            for queue in self.queues.values():
                queue.add_arrivals(self.step_s, self.rng)

            demand = self._demand_snapshot(elapsed)
            status = self.controller.tick(self.step_s, demand)
            try:
                assert_no_conflicting_greens(status.signal_state)
            except Exception:
                self.conflicting_green_violations += 1

            for approach, queue in self.queues.items():
                if status.signal_state.colour_for(approach) is Colour.GREEN:
                    queue.discharge(self.step_s, self.discharge_headway_s)
                queue.accumulate_wait(self.step_s)

            self.max_queue = max(self.max_queue, *(queue.queue for queue in self.queues.values()))
            self._record_logged_step(run_id, elapsed, demand, status)
            self._notify_step(elapsed, demand, status)
            elapsed += self.step_s

        arrivals = sum(queue.total_arrivals for queue in self.queues.values())
        completed = sum(queue.total_departures for queue in self.queues.values())
        total_wait = sum(queue.total_wait_s for queue in self.queues.values())
        mean_wait = total_wait / completed if completed else 0.0
        summary = SimulationSummary(
            scenario=self.scenario.name,
            controller=self.controller_name,
            duration_s=self.duration_s,
            arrivals=arrivals,
            completed=completed,
            throughput_veh_per_min=completed / (self.duration_s / 60.0),
            mean_wait_s=mean_wait,
            max_queue=self.max_queue,
            conflicting_green_violations=self.conflicting_green_violations,
            final_queues={approach.value: queue.queue for approach, queue in self.queues.items()},
        )
        if self.logger is not None and run_id is not None:
            self.logger.finish_run(run_id, summary.__dict__)
        return summary

    def _demand_snapshot(self, timestamp: float) -> DemandSnapshot:
        return DemandSnapshot(
            north=float(self.queues[Approach.NORTH].queue),
            east=float(self.queues[Approach.EAST].queue),
            south=float(self.queues[Approach.SOUTH].queue),
            west=float(self.queues[Approach.WEST].queue),
            timestamp=timestamp,
        )

    def _start_logged_run(self) -> int | None:
        if self.logger is None:
            return None
        return self.logger.start_run(
            {
                "scenario": self.scenario.name,
                "controller": self.controller_name,
                "duration_s": self.duration_s,
                "step_s": self.step_s,
                "seed": self.seed,
                "discharge_headway_s": self.discharge_headway_s,
            }
        )

    def _record_logged_step(
        self,
        run_id: int | None,
        timestamp: float,
        demand: DemandSnapshot,
        status,
    ) -> None:
        if self.logger is None or run_id is None:
            return
        completed = sum(queue.total_departures for queue in self.queues.values())
        total_wait = sum(queue.total_wait_s for queue in self.queues.values())
        mean_wait = total_wait / completed if completed else None
        self.logger.record_step(
            run_id=run_id,
            timestamp=timestamp,
            demand=demand,
            status=status,
            queues={approach.value: queue.queue for approach, queue in self.queues.items()},
            completed_vehicles=completed,
            mean_wait_s=mean_wait,
        )

    def _notify_step(self, timestamp: float, demand: DemandSnapshot, status) -> None:
        if self.on_step is None:
            return
        completed = sum(queue.total_departures for queue in self.queues.values())
        total_wait = sum(queue.total_wait_s for queue in self.queues.values())
        self.on_step(
            {
                "type": "step",
                "timestamp": timestamp,
                "phase": status.phase.value,
                "phase_elapsed_s": status.phase_elapsed_s,
                "target_green_s": status.target_green_s,
                "reason": status.reason,
                "signals": {
                    approach.value: colour.value
                    for approach, colour in status.signal_state.colours.items()
                },
                "demand": {
                    "north": demand.north,
                    "east": demand.east,
                    "south": demand.south,
                    "west": demand.west,
                },
                "queues": {
                    approach.value: queue.queue for approach, queue in self.queues.items()
                },
                "completed_vehicles": completed,
                "mean_wait_s": total_wait / completed if completed else None,
            }
        )
