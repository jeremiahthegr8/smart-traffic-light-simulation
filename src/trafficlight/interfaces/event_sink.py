from typing import Protocol

from trafficlight.domain.models import ControllerStatus, DemandSnapshot


class SimulationEventSink(Protocol):
    def start_run(self, config: dict) -> int:
        ...

    def record_step(
        self,
        *,
        run_id: int,
        timestamp: float,
        demand: DemandSnapshot,
        status: ControllerStatus,
        queues: dict[str, int],
        completed_vehicles: int,
        mean_wait_s: float | None,
    ) -> None:
        ...

    def finish_run(self, run_id: int, summary: dict) -> None:
        ...

