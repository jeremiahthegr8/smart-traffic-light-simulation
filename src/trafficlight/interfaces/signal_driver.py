from typing import Protocol

from trafficlight.domain.models import SignalState


class SignalDriver(Protocol):
    def apply(self, state: SignalState) -> None:
        ...

    def all_red(self) -> None:
        ...

    def close(self) -> None:
        ...

