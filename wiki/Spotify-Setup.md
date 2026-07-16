# Spotify Setup

> **Placeholder** — full guide: [docs/spotify-setup.md](https://github.com/Paco5687/SpotAmp/blob/main/docs/spotify-setup.md)

Fully **standalone** — network + a Spotify **Premium** account, **no phone**.
Two one-time browser logins, both loopback (no website/hosting):

1. **go-librespot** (audio) — interactive OAuth → caches `credentials.json`.
2. **Web API** (browse/control) — PKCE → `python -m spotamp.authorize`.
   Register redirect URI `http://127.0.0.1:8888/callback` in the Spotify dashboard.

Notes:
- Add your account under **User Management** in the Spotify dashboard (Dev Mode).
- Dev Mode can't read the *tracklist* of playlists you don't own, but you can
  still **play** any followed/editorial playlist.
