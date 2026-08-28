from trafficlight.domain.models import SignalState


class SimulatedSignalDriver:
    def __init__(self) -> None:
        self.state = SignalState.all_red()
        self.history: list[SignalState] = []

    def apply(self, state: SignalState) -> None:
        self.state = state.copy()
        self.history.append(self.state.copy())

    def all_red(self) -> None:
        self.apply(SignalState.all_red())

    def close(self) -> None:
        self.all_red()

