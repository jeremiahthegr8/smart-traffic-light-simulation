from typing import Protocol

from trafficlight.domain.models import DemandSnapshot


class Detector(Protocol):
    def read_demand(self) -> DemandSnapshot:
        ...

