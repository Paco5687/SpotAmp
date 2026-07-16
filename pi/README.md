# Pi app — `spotamp`

The Python/Pygame application: the WinAmp-style UI, Spotify control, and the
bridge to the microcontroller. Runs **fully mocked on a laptop** so you can build
the UI with no hardware and no Spotify account.

## Run (mock mode — default)

```bash
cd pi
pip install -r requirements.txt   # pygame is all you need for mock mode
python -m spotamp
```

Requires **Python 3.11+** (uses the stdlib `tomllib`).

A square (720×720) **multi-view** window opens — the device screen: **Now Playing**,
**Playlists**, **Up Next**. On the real device these views are switched by dedicated
physical buttons; transport/EQ/faders are hardware, not on screen.

**Controls in the window (dev):**

| Input | Action |
|---|---|
| Tabs / `1` `2` `3` / `Tab` | switch view (Now Playing / Playlists / Up Next) |
| Tap a playlist row | open + play that playlist |
| `space` | play/pause |
| `←` / `→` | prev / next |
| `↑` / `↓` | volume |
| `s` | stop · `q` / `Esc` quit |

## Connect Spotify (Web API — playlists & album art)

No website or hosting needed — it uses a **loopback redirect + PKCE**.

1. Create an app at https://developer.spotify.com/dashboard.
2. Add this **exact** redirect URI (Spotify banned `localhost`; loopback HTTP is fine):
   ```
   http://127.0.0.1:8888/callback
   ```
3. Put the app's **Client ID** in `config.toml` as `spotify_client_id` (no secret needed).
4. Authorize once:
   ```bash
   python -m spotamp.authorize
   ```
   A browser opens, you approve, and a refresh token is cached to
   `pi/spotify_token.json` (gitignored). The device refreshes tokens forever after that.

`go-librespot` (the audio playback) authenticates **separately and standalone** —
using its own one-time **interactive OAuth** login (no phone required; a phone via
Spotify Connect is only an optional alternative). It needs Premium. See
[../docs/spotify-setup.md](../docs/spotify-setup.md) for both one-time logins.

## Run against real hardware

Copy `config.example.toml` → `config.toml` and set:

```toml
backend  = "librespot"      # needs a running go-librespot + Spotify Premium
controls = "serial"         # needs the RP2040 flashed and connected
serial_port = "/dev/ttyACM0"
fullscreen = true           # on the device LCD
```

`requests` and `pyserial` (in `requirements.txt`) are only needed for real
hardware; they're imported lazily so mock mode doesn't require them.

## Layout

```
spotamp/
├── __main__.py      # python -m spotamp (also: `authorize` subcommand)
├── app.py           # main loop, action routing, MOTOR SYNC, queue/battery polls
├── config.py        # config.toml loader (zero-config defaults)
├── models.py        # PlayerState / Track — the source of truth
├── spotify.py       # MockPlayer / WebApiPlayer / LibrespotPlayer (PlayerBackend)
├── spotify_web.py   # Web API client: playlists, queue, playback control
├── spotify_auth.py  # loopback PKCE OAuth + token cache
├── library.py       # async playlist browsing (BrowseState)
├── images.py        # async album-art download + cache
├── power.py         # battery sources (mock / Geekworm X728)
├── controls.py      # serial protocol + MockControls / SerialControls
└── ui/
    ├── skin.py      # palette + Rect drawing helper
    └── screen.py    # the multi-view screen UI (Now Playing / Playlists / Up Next)
```

Tests live in [`tests/`](tests/) — run `python -m pytest tests` from `pi/`.
See [../docs/architecture.md](../docs/architecture.md) for how it all fits.

## Playback backends

Set `backend` in `config.toml`:

| `backend` | What plays the audio | Use it for |
|---|---|---|
| `mock` (default) | nothing — simulated playback of a demo/owned playlist | UI dev on a laptop |
| `librespot` | **go-librespot on this machine** (the device path) | the real device |
| `webapi` | any active Spotify Connect device via the Web API | laptop dev with real audio |

Tapping a playlist plays it **by context URI**, which works for owned *and*
followed/editorial playlists (Dev Mode only restricts *reading* their track
lists, not playing them). The **Up Next** view shows the live playback queue
(`GET /me/player/queue`), so you still get a tracklist for anything playing.

## Notes / TODO

- **Album art** is real (fetched + cached async in `images.py`); a drawn
  placeholder shows until each image lands.
- **Spectrum analyzer** returns in Phase 4 with the real FFT audio tap.
- **EQ** currently just stores band gains; the ALSA software-EQ pipeline that
  applies them is Phase 4 (see the project board).
