# Firmware (RP2040)

> **Placeholder** — see [firmware/README.md](https://github.com/Paco5687/SpotAmp/blob/main/firmware/README.md)
> and the [serial protocol](https://github.com/Paco5687/SpotAmp/blob/main/docs/serial-protocol.md).

The RP2040 (Raspberry Pi Pico) owns real-time I/O and the motorized-fader PID
loops, and talks to the Pi over a simple ASCII serial protocol.

- Build with PlatformIO (`arduino-pico` core): `cd firmware && pio run -t upload`.
- Bring-up order and pin map: see the firmware README.
