import pytest

from trafficlight.domain.enums import Approach, Colour, MovementGroup
from trafficlight.domain.models import SignalState
from trafficlight.domain.safety import SafetyError
from trafficlight.hardware.gpio_signals import GPIOZeroSignalDriver
from trafficlight.hardware.pinmap import DEFAULT_SIGNAL_PINS, SignalPin, validate_pinmap


class FakeLed:
    def __init__(self, pin: int) -> None:
        self.pin = pin
        self.active = False
        self.closed = False
        self.events: list[str] = []

    def on(self) -> None:
        self.active = True
        self.events.append("on")

    def off(self) -> None:
        self.active = False
        self.events.append("off")

    def close(self) -> None:
        self.closed = True
        self.events.append("close")


def make_driver() -> tuple[GPIOZeroSignalDriver, dict[int, FakeLed]]:
    leds: dict[int, FakeLed] = {}

    def factory(pin: int) -> FakeLed:
        led = FakeLed(pin)
        leds[pin] = led
        return led

    return GPIOZeroSignalDriver(led_factory=factory), leds


def pin_for(approach: Approach, colour: Colour) -> int:
    for signal_pin in DEFAULT_SIGNAL_PINS:
        if signal_pin.approach is approach and signal_pin.colour is colour:
            return signal_pin.bcm_pin
    raise AssertionError(f"missing pin for {approach}/{colour}")


def test_default_pinmap_has_one_unique_pin_for_each_lamp() -> None:
    validate_pinmap()


def test_gpio_driver_applies_green_group_and_red_opposing_group() -> None:
    driver, leds = make_driver()

    driver.apply(SignalState.for_group(MovementGroup.NORTH_SOUTH, Colour.GREEN))

    assert leds[pin_for(Approach.NORTH, Colour.GREEN)].active
    assert leds[pin_for(Approach.SOUTH, Colour.GREEN)].active
    assert leds[pin_for(Approach.EAST, Colour.RED)].active
    assert leds[pin_for(Approach.WEST, Colour.RED)].active
    assert not leds[pin_for(Approach.NORTH, Colour.RED)].active
    assert not leds[pin_for(Approach.EAST, Colour.GREEN)].active


def test_gpio_driver_rejects_conflicting_green_state() -> None:
    driver, _ = make_driver()
    state = SignalState.all_red()
    state.colours[Approach.NORTH] = Colour.GREEN
    state.colours[Approach.EAST] = Colour.GREEN

    with pytest.raises(SafetyError):
        driver.apply(state)


def test_gpio_driver_all_red_and_close() -> None:
    driver, leds = make_driver()
    driver.apply(SignalState.for_group(MovementGroup.EAST_WEST, Colour.GREEN))

    driver.all_red()

    assert all(leds[pin_for(approach, Colour.RED)].active for approach in Approach)
    assert all(not leds[pin_for(approach, Colour.GREEN)].active for approach in Approach)

    driver.close()

    assert all(led.closed for led in leds.values())


def test_pinmap_rejects_duplicate_bcm_pins() -> None:
    bad_pinmap = (
        SignalPin(Approach.NORTH, Colour.RED, 2),
        SignalPin(Approach.NORTH, Colour.AMBER, 2),
    )

    with pytest.raises(ValueError):
        validate_pinmap(bad_pinmap)

