from __future__ import annotations

from typing import Callable, Protocol

from trafficlight.domain.enums import APPROACHES, Approach, Colour
from trafficlight.domain.models import SignalState
from trafficlight.domain.safety import checked_state
from trafficlight.hardware.pinmap import DEFAULT_SIGNAL_PINS, SignalPin, validate_pinmap


class LedLike(Protocol):
    def on(self) -> None:
        ...

    def off(self) -> None:
        ...

    def close(self) -> None:
        ...


LedFactory = Callable[[int], LedLike]


class GPIOZeroSignalDriver:
    def __init__(
        self,
        pinmap: tuple[SignalPin, ...] = DEFAULT_SIGNAL_PINS,
        *,
        led_factory: LedFactory | None = None,
    ) -> None:
        validate_pinmap(pinmap)
        self._led_factory = led_factory or _gpiozero_led_factory()
        self._leds: dict[tuple[Approach, Colour], LedLike] = {
            (signal_pin.approach, signal_pin.colour): self._led_factory(signal_pin.bcm_pin)
            for signal_pin in pinmap
        }
        self.all_red()

    def apply(self, state: SignalState) -> None:
        checked_state(state)
        for approach in APPROACHES:
            active_colour = state.colour_for(approach)
            for colour in Colour:
                led = self._leds[(approach, colour)]
                if colour is active_colour:
                    led.on()
                else:
                    led.off()

    def all_red(self) -> None:
        self.apply(SignalState.all_red())

    def close(self) -> None:
        try:
            self.all_red()
        finally:
            for led in self._leds.values():
                led.close()


def _gpiozero_led_factory() -> LedFactory:
    try:
        from gpiozero import LED
    except ImportError as exc:
        raise RuntimeError(
            "GPIO Zero is not installed. Install the hardware extra with "
            'python -m pip install -e ".[hardware]".'
        ) from exc
    return LED

