"""Battery monitoring + safe-shutdown hook.

Abstracts the battery behind ``BatterySource`` so the UI can show a meter and the
Pi can shut down cleanly on low battery:

* ``MockBattery``  — a simulated drain/charge cycle, for developing the UI on a
  laptop (no hardware).
* ``X728Battery`` — reads a Geekworm X728 UPS (MAX17040 fuel gauge at I2C 0x36).
  UNTESTED here — register math must be verified on real hardware.

See hardware/power.md. Real I2C reads + safe shutdown are exercised only on the
Pi with the UPS board; on a laptop use ``battery = "mock"``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol


@dataclass
class BatteryState:
    percent: float           # 0..100
    charging: bool = False
    voltage: float = 0.0


class BatterySource(Protocol):
    def read(self) -> BatteryState | None: ...


class MockBattery:
    """Simulated battery for UI development: slow drain, then 'recharge'."""

    def __init__(self, start: float = 87.0) -> None:
        self._pct = start
        self._charging = False
        self._last = time.monotonic()

    def read(self) -> BatteryState:
        now = time.monotonic()
        dt = now - self._last
        self._last = now
        if self._charging:
            self._pct = min(100.0, self._pct + dt * (100 / 120))   # ~2 min to full
            if self._pct >= 100:
                self._charging = False
        else:
            self._pct = max(0.0, self._pct - dt * (100 / 600))     # ~10 min to empty
            if self._pct <= 15:
                self._charging = True
        return BatteryState(round(self._pct, 1), self._charging, 3.3 + 0.9 * self._pct / 100)


class X728Battery:
    """Geekworm X728 UPS via its MAX17040 fuel gauge (I2C 0x36).

    UNTESTED in this repo — verify the register scaling against the X728 docs and
    a multimeter before trusting the numbers. Charging/AC-loss detection on the
    X728 is a GPIO (not I2C); left as a TODO.
    """

    ADDR = 0x36

    def __init__(self, bus: int = 1) -> None:
        import smbus2  # lazy: only present on the Pi

        self._bus = smbus2.SMBus(bus)

    def _read_word(self, reg: int) -> int:
        raw = self._bus.read_word_data(self.ADDR, reg)
        return ((raw & 0xFF) << 8) | (raw >> 8)  # byte-swap

    def read(self) -> BatteryState | None:
        try:
            vcell = self._read_word(0x02) * 1.25 / 1000 / 16  # volts
            soc = self._read_word(0x04) / 256.0               # percent
        except Exception:  # noqa: BLE001 — never let an I2C hiccup crash the UI
            return None
        return BatteryState(max(0.0, min(100.0, soc)), False, vcell)


def make_battery(cfg) -> BatterySource | None:
    kind = getattr(cfg, "battery", "none")
    if kind == "mock":
        return MockBattery()
    if kind == "x728":
        try:
            return X728Battery(getattr(cfg, "battery_i2c_bus", 1))
        except Exception:  # noqa: BLE001
            return None
    return None
