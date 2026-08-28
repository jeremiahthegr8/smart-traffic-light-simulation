from trafficlight.domain.enums import Approach
from trafficlight.domain.models import SignalState


class SafetyError(RuntimeError):
    """Raised when a signal state violates controller safety rules."""


def assert_no_conflicting_greens(state: SignalState) -> None:
    green = set(state.green_approaches())
    ns_green = bool(green & {Approach.NORTH, Approach.SOUTH})
    ew_green = bool(green & {Approach.EAST, Approach.WEST})
    if ns_green and ew_green:
        raise SafetyError(f"conflicting green approaches: {sorted(green)}")


def checked_state(state: SignalState) -> SignalState:
    assert_no_conflicting_greens(state)
    return state

