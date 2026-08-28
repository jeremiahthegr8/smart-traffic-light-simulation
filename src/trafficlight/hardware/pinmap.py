from __future__ import annotations

from dataclasses import dataclass

from trafficlight.domain.enums import APPROACHES, Approach, Colour


@dataclass(frozen=True)
class SignalPin:
    approach: Approach
    colour: Colour
    bcm_pin: int


DEFAULT_SIGNAL_PINS: tuple[SignalPin, ...] = (
    SignalPin(Approach.NORTH, Colour.RED, 2),
    SignalPin(Approach.NORTH, Colour.AMBER, 3),
    SignalPin(Approach.NORTH, Colour.GREEN, 4),
    SignalPin(Approach.EAST, Colour.RED, 17),
    SignalPin(Approach.EAST, Colour.AMBER, 27),
    SignalPin(Approach.EAST, Colour.GREEN, 22),
    SignalPin(Approach.SOUTH, Colour.RED, 10),
    SignalPin(Approach.SOUTH, Colour.AMBER, 9),
    SignalPin(Approach.SOUTH, Colour.GREEN, 11),
    SignalPin(Approach.WEST, Colour.RED, 5),
    SignalPin(Approach.WEST, Colour.AMBER, 6),
    SignalPin(Approach.WEST, Colour.GREEN, 13),
)


def validate_pinmap(pinmap: tuple[SignalPin, ...] = DEFAULT_SIGNAL_PINS) -> None:
    expected = {(approach, colour) for approach in APPROACHES for colour in Colour}
    actual = {(pin.approach, pin.colour) for pin in pinmap}
    if actual != expected:
        missing = expected - actual
        extra = actual - expected
        raise ValueError(f"invalid signal pinmap, missing={missing}, extra={extra}")

    bcm_pins = [pin.bcm_pin for pin in pinmap]
    duplicates = sorted({pin for pin in bcm_pins if bcm_pins.count(pin) > 1})
    if duplicates:
        raise ValueError(f"duplicate BCM pins in signal pinmap: {duplicates}")

