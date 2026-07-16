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

- Reads buttons (via MCP23017), encoders, the balance pot, and all fader wiper
  positions (through a CD74HC4067 analog mux, since the Pico has only 3 ADC
  channels).
- Runs a per-fader **PID loop** at ~1 kHz driving each motorized fader toward the
  target the Pi last sent (`FADER <id> <pos>`), and yields the motor while the
  user is touching that fader (MPR121 touch electrodes).
- Drives the **amber OLED readout** (SSD1322 over SPI) from `DISP` commands the
  Pi streams (title / time / stream info).
- Emits `EV …` events upstream (button presses, user fader moves, touch, encoders).

> **I/O architecture:** motor PWM goes through **2× PCA9685** and buttons/touch
> through **MCP23017/MPR121**, all on one I2C bus — direct-wiring doesn't fit the
> Pico's 26 GPIO. Full pin budget in [../hardware/wiring.md](../hardware/wiring.md).
> The `main.cpp` skeleton still drives one fader on direct pins for bring-up;
> switch to the PCA9685 when scaling past one.

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
