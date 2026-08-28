from enum import StrEnum


class Approach(StrEnum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"


class MovementGroup(StrEnum):
    NORTH_SOUTH = "north_south"
    EAST_WEST = "east_west"


class Colour(StrEnum):
    RED = "red"
    AMBER = "amber"
    GREEN = "green"


class Phase(StrEnum):
    ALL_RED_TO_NS = "all_red_to_ns"
    NS_GREEN = "ns_green"
    NS_AMBER = "ns_amber"
    ALL_RED_TO_EW = "all_red_to_ew"
    EW_GREEN = "ew_green"
    EW_AMBER = "ew_amber"


APPROACHES: tuple[Approach, ...] = (
    Approach.NORTH,
    Approach.EAST,
    Approach.SOUTH,
    Approach.WEST,
)

GROUP_APPROACHES: dict[MovementGroup, tuple[Approach, Approach]] = {
    MovementGroup.NORTH_SOUTH: (Approach.NORTH, Approach.SOUTH),
    MovementGroup.EAST_WEST: (Approach.EAST, Approach.WEST),
}


def group_for_phase(phase: Phase) -> MovementGroup | None:
    if phase in {Phase.NS_GREEN, Phase.NS_AMBER, Phase.ALL_RED_TO_EW}:
        return MovementGroup.NORTH_SOUTH
    if phase in {Phase.EW_GREEN, Phase.EW_AMBER, Phase.ALL_RED_TO_NS}:
        return MovementGroup.EAST_WEST
    return None


def opposing_group(group: MovementGroup) -> MovementGroup:
    if group is MovementGroup.NORTH_SOUTH:
        return MovementGroup.EAST_WEST
    return MovementGroup.NORTH_SOUTH

