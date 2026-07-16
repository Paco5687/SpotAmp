# Software Setup

> **Placeholder** — see [pi/README.md](https://github.com/Paco5687/SpotAmp/blob/main/pi/README.md).

## Try the UI on a laptop (no hardware)
```bash
cd pi
pip install -r requirements.txt
python -m spotamp
```
Requires Python 3.11+. Opens the WinAmp-style UI with a demo playlist.

## On the Raspberry Pi 4 B

The full, tested procedure lives in
**[docs/pi-bringup.md](https://github.com/Paco5687/SpotAmp/blob/main/docs/pi-bringup.md)**:

1. Flash Raspberry Pi OS (64-bit, Desktop); enable SSH.
2. Install [go-librespot](https://github.com/devgianlu/go-librespot) (audio) as a
   systemd service; one-time standalone OAuth ([Spotify Setup](Spotify-Setup)).
3. HyperPixel 4.0 Square display: **disable I2C/SPI** (DPI uses all GPIO), add the
   `vc4-kms-dpi-hyperpixel4sq` overlay; rotate at the compositor level.
4. Clone the repo, `pip install -r pi/requirements.txt` in a venv, copy
   `config.example.toml` → `config.toml` (`backend = "librespot"`).
5. Kiosk autostart via the systemd user service in `deploy/` — boots straight
   into the UI. Audio: 3.5 mm jack for bring-up, USB DAC for the real build.
6. Later: flash the [Firmware](Firmware) to the RP2040 for physical controls.
