# Spotify setup — fully standalone (no phone)

The device authenticates to Spotify **by itself**. No phone, no companion app in
the loop — just a network connection and a Spotify **Premium** account. There
are two one-time browser authorizations during setup; after that the device
runs autonomously and reconnects on cached credentials forever.

```
                       ONE-TIME SETUP                         EVERY BOOT AFTER
  ┌────────────────────────────────────────┐      ┌───────────────────────────┐
  │ 1. go-librespot interactive OAuth       │      │ go-librespot reconnects   │
  │    → caches credentials.json            │ ───▶ │  (cached creds)           │
  │ 2. Web API PKCE (authorize.py)          │      │ app lists YOUR playlists  │
  │    → caches spotify_token.json          │      │ tap one → it plays        │
  └────────────────────────────────────────┘      └───────────────────────────┘
        (browser once — Pi screen or laptop)              (no phone, ever)
```

Why two logins? They're two different jobs:

| | **go-librespot** | **Web API** (`spotify_web.py`) |
|---|---|---|
| Job | Streams + decodes the actual audio | Lists playlists, album art, "play this" |
| Auth | Interactive OAuth → `credentials.json` | PKCE → `spotify_token.json` |
| Needs Premium | ✅ | (uses same account) |
| Needs a phone | ❌ | ❌ |

---

## 1. go-librespot (the audio engine)

Install go-librespot on the Pi (see its
[README](https://github.com/devgianlu/go-librespot) for the current binary/build
steps), then configure it for standalone interactive login.

`~/.config/go-librespot/config.yml` (representative — verify key names against
the go-librespot README, which is the source of truth):

```yaml
device_name: "SpotAmp"
device_type: computer

credentials:
  type: interactive          # one-time browser OAuth, then cached — NOT zeroconf

audio_backend: alsa          # on the Pi; routes into our EQ chain → I2S DAC

server:                      # the HTTP/WebSocket API our app talks to
  enabled: true
  address: 127.0.0.1
  port: 3678
```

First run does the login:

```bash
go-librespot            # prints an auth URL; approve in a browser, once
```

- If you run it **on the Pi** (touchscreen browser), the loopback callback closes
  the loop right there.
- If you run it **on a laptop** first, copy the resulting `credentials.json` from
  `~/.config/go-librespot/` to the same path on the Pi.

After this, it reconnects headless on every boot. Point our app at it with
`backend = "librespot"` and `librespot_url = "http://127.0.0.1:3678"` in
`config.toml`.

## 2. Web API (browse + control)

This is the flow already built into the app:

1. Create an app at https://developer.spotify.com/dashboard.
2. Add redirect URI **exactly**: `http://127.0.0.1:8888/callback`
3. Put the **Client ID** in `pi/config.toml` (`spotify_client_id`). No secret — PKCE.
4. `python -m spotamp.authorize` → approve once → `spotify_token.json` cached.

See [../pi/README.md](../pi/README.md#connect-spotify-web-api--playlists--album-art).

---

## Do we even need the Web API to *start* playback?

Not strictly — go-librespot's own HTTP API can start a context (playlist/album)
URI and reports now-playing metadata + album art. But the Web API is what lets us
**browse your whole playlist library** on the touchscreen (go-librespot can't list
your playlists). So: **browse via Web API, play via librespot.** Both authorized
standalone, both cached, no phone.

## Caveats (the honest ones)

- **Premium required** — librespot won't stream on free accounts.
- **One browser step per login, once.** Spotify removed password auth, so the
  initial OAuth can't be fully headless — but it's a setup-time cost only.
- **librespot is unofficial** (reverse-engineered). Reliable and widely used, but
  not sanctioned by Spotify.

## Development Mode limitation (Feb 2026 migration)

Spotify's Feb 2026 Web API change (enforced 2026-03-09) means a **Development
Mode** app can only read the **tracks** of playlists you **own or collaborate
on**. For Spotify-owned/editorial playlists (Discover Weekly, Daily Mix, "Today's
Top Hits", etc.) the Web API returns metadata only — the UI flags these as
*"dev-mode locked."* Also note: `GET /playlists/{id}/tracks` was removed; use
`GET /playlists/{id}/items` (track field renamed `track` → `item`).

**Important nuance:** this only limits *reading a track list* over the Web API.
It does **not** limit **playback** — go-librespot can play *any* playlist by its
context URI, and reports now-playing metadata itself. So on the real device we
can still play editorial playlists; we just show now-playing from librespot
instead of a pre-fetched track list. Getting full track-list access for all
playlists would require Spotify **Extended Quota Mode** (a manual approval), which
isn't worth it for a personal build.
