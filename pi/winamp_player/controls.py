"""Physical controls bridge (Pi side).

The microcontroller owns all the physical I/O and the real-time motor loops.
The Pi talks to it over a newline-delimited ASCII serial protocol — chosen over
binary because it's trivial to debug with a serial monitor.

This module defines the protocol, an event model, and two sources:

* ``MockControls`` — yields nothing; the on-screen UI provides input instead.
* ``SerialControls`` — reads/writes the real link to the microcontroller.

The canonical protocol spec lives in docs/serial-protocol.md. Keep the two in
sync (and the mirror in firmware/src/main.cpp).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Protocol


class ControlEventType(Enum):
    BUTTON = "BTN"     # id, pressed(0/1)
    FADER = "FADER"    # id, position(0..1023) — user moved a fader
    TOUCH = "TOUCH"    # id, touched(0/1) — user grabbed a motorized fader
    ENCODER = "ENC"    # id, delta(int)
    POT = "POT"        # id, value(0..1023)


# Stable control ids. Faders are the motorized ones the Pi commands back.
class FaderId(Enum):
    EQ0 = 0
    EQ1 = 1
    EQ2 = 2
    EQ3 = 3
    EQ4 = 4
    EQ5 = 5
    EQ6 = 6
    PREAMP = 7
    VOLUME = 8
    SEEK = 9


class ButtonId(Enum):
    PREV = 0
    PLAY = 1
    PAUSE = 2
    STOP = 3
    NEXT = 4
    EJECT = 5
    SHUFFLE = 6
    REPEAT = 7
    EQ_TOGGLE = 8


FADER_MAX = 1023  # 10-bit ADC range on the microcontroller


@dataclass(frozen=True)
class ControlEvent:
    type: ControlEventType
    id: int
    value: int


def parse_event(line: str) -> ControlEvent | None:
    """Parse one inbound line: ``EV <TYPE> <id> <value>``. Returns None if junk."""
    parts = line.strip().split()
    if len(parts) != 4 or parts[0] != "EV":
        return None
    try:
        etype = ControlEventType(parts[1])
        return ControlEvent(etype, int(parts[2]), int(parts[3]))
    except (ValueError, KeyError):
        return None


def cmd_fader_target(fader: FaderId, position: int) -> str:
    """Drive a motorized fader to a target position (0..FADER_MAX)."""
    position = max(0, min(FADER_MAX, int(position)))
    return f"FADER {fader.value} {position}\n"


def cmd_fader_release(fader: FaderId) -> str:
    """Cut motor power so the user can move the fader freely."""
    return f"FADER_RELEASE {fader.value}\n"


def cmd_led(index: int, r: int, g: int, b: int) -> str:
    return f"LED {index} {r} {g} {b}\n"


class ControlsSource(Protocol):
    def read_events(self) -> Iterator[ControlEvent]: ...
    def send(self, command: str) -> None: ...
    def close(self) -> None: ...


class MockControls:
    """No hardware: the on-screen widgets provide input instead."""

    def read_events(self) -> Iterator[ControlEvent]:
        return iter(())

    def send(self, command: str) -> None:  # swallow motor commands
        pass

    def close(self) -> None:
        pass


class SerialControls:
    """Real microcontroller link over USB serial (pyserial)."""

    def __init__(self, port: str, baud: int) -> None:
        import serial  # lazy import so mock mode needs no pyserial

        self._ser = serial.Serial(port, baud, timeout=0)
        self._buf = b""

    def read_events(self) -> Iterator[ControlEvent]:
        self._buf += self._ser.read(4096)
        while b"\n" in self._buf:
            line, self._buf = self._buf.split(b"\n", 1)
            ev = parse_event(line.decode("ascii", "ignore"))
            if ev is not None:
                yield ev

    def send(self, command: str) -> None:
        self._ser.write(command.encode("ascii"))

    def close(self) -> None:
        self._ser.close()


def make_controls(cfg) -> ControlsSource:
    if cfg.controls == "serial":
        return SerialControls(cfg.serial_port, cfg.serial_baud)
    return MockControls()
