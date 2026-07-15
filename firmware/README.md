# Firmware (RP2040 / Raspberry Pi Pico)

Owns all physical I/O and the real-time motor loops for the motorized faders.
Talks to the Pi over USB serial using the [serial protocol](../docs/serial-protocol.md).

## Build

Uses [PlatformIO](https://platformio.org/) with the Arduino core for RP2040
(`earlephilhower/arduino-pico`):

```bash
cd firmware
pio run                 # build
pio run -t upload       # flash (hold BOOTSEL on first flash, or use the reset)
pio device monitor      # watch the serial link
```

## What it does

- Reads buttons (debounced), encoders, pots, and all fader wiper positions
  (through a CD74HC4067 analog mux, since the Pico has only 3 ADC channels).
- Runs a per-fader **PID loop** at ~1 kHz driving each motorized fader toward the
  target the Pi last sent (`FADER <id> <pos>`), and yields the motor while the
  user is touching that fader.
- Emits `EV …` events upstream (button presses, user fader moves, touch, encoders).

`src/main.cpp` is a well-commented skeleton — the structure and protocol are
real; pin numbers and PID gains are placeholders to tune on the bench. Start by
getting **one** fader tracking a target smoothly, then replicate.

## Bring-up order

1. Serial echo: reply `PONG` to `PING`. Confirm the Pi sees it.
2. Read one fader's wiper through the mux; stream `EV FADER 8 <pos>`.
3. Drive one motor open-loop both directions.
4. Close the loop: PID one fader to a target from the Pi. Tune Kp/Ki/Kd.
5. Add touch-sense → `EV TOUCH`; verify the Pi stops driving when grabbed.
6. Scale to all faders + buttons + encoders.
