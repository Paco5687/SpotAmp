# Software Setup

> **Placeholder** — see [pi/README.md](https://github.com/Paco5687/WinAmpPlayer/blob/main/pi/README.md).

## Try the UI on a laptop (no hardware)
```bash
cd pi
pip install -r requirements.txt
python -m winamp_player
```
Requires Python 3.11+. Opens the WinAmp-style UI with a demo playlist.

## On the Raspberry Pi 4 B (outline — TODO expand)
1. Flash Raspberry Pi OS (64-bit); enable I2C/SPI/serial.
2. Install [go-librespot](https://github.com/devgianlu/go-librespot) (audio engine).
3. Configure ALSA + I2S DAC; add the software EQ chain.
4. `pip install -r pi/requirements.txt`; copy `config.example.toml` → `config.toml`.
5. [Spotify Setup](Spotify-Setup) for the two one-time logins.
6. Run fullscreen on boot (kiosk). Flash the [Firmware](Firmware) to the RP2040.
