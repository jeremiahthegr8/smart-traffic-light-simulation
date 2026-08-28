import pytest

from trafficlight.domain.enums import Approach, Colour, MovementGroup
from trafficlight.domain.models import SignalState
from trafficlight.domain.safety import SafetyError, assert_no_conflicting_greens


def test_all_red_is_safe() -> None:
    assert_no_conflicting_greens(SignalState.all_red())


def test_single_movement_group_green_is_safe() -> None:
    assert_no_conflicting_greens(
        SignalState.for_group(MovementGroup.NORTH_SOUTH, Colour.GREEN)
    )


def test_conflicting_greens_are_rejected() -> None:
    state = SignalState.all_red()
    state.colours[Approach.NORTH] = Colour.GREEN
    state.colours[Approach.EAST] = Colour.GREEN

    with pytest.raises(SafetyError):
        assert_no_conflicting_greens(state)

