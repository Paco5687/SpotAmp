# Contributing

Thanks for your interest in **SpotAmp**! This is an open
(MIT-licensed) hardware + software project meant to be reproducible by anyone.

## Ground rules

- **Never commit credentials.** No Spotify client secrets, tokens, or
  `credentials.json`. Local secrets live in gitignored files:
  - `pi/config.toml` — copy from [`pi/config.example.toml`](pi/config.example.toml)
  - `pi/spotify_token.json` — created by `python -m spotamp.authorize`
  - go-librespot `credentials.json` — lives on the Pi in `~/.config/go-librespot/`
  If you think you committed a secret, rotate it immediately (Spotify dashboard).
- **Bring your own Spotify Premium** account and developer app to run/test.

## Repo layout

| Path | What |
|---|---|
| [`pi/`](pi/) | Raspberry Pi player app (Python/Pygame) |
| [`firmware/`](firmware/) | RP2040 controls firmware (PlatformIO) |
| [`hardware/`](hardware/) | BOM, wiring, [power design](hardware/power.md), enclosure |
| [`docs/`](docs/) | Architecture, serial protocol, Spotify setup |
| [`wiki/`](wiki/) | Source for the GitHub Wiki |
| [`config/`](config/) | Config templates (e.g. go-librespot) |

## Dev quickstart

```bash
cd pi && pip install -r requirements.txt && python -m spotamp   # mock UI, no hardware
```

## Pull requests

- Keep changes focused; match the surrounding style.
- Update the relevant doc/wiki page when you change behavior or parts.
- For hardware changes, note what you actually tested on real hardware vs. designed.
