# Troubleshooting

> **Placeholder** — to grow as issues surface.

## Spotify
- **403 on `/v1/me`** → add your account under Dashboard → **User Management** (Dev Mode allowlist).
- **403 on playlist tracks** → expected for playlists you don't own (Feb-2026 Dev Mode rule); you can still *play* them with `backend = "webapi"`.
- **"No active Spotify device"** → open the Spotify app or start go-librespot so there's a device to play on.

## App
- **`[library] …` in console** → the browser fell back to the demo list; the message says why.
- Album art stays a gradient → the image is still downloading, or JPEG decode is unavailable in your pygame build.

## Hardware
- Fader oscillates/hunts → tune the PID gains (start low `Kp`, add `Kd`).
- Audio whine → separate motor-current wiring from the DAC lines; check grounding.
- Random reboots under load → 5 V rail sagging on motor spikes; add bulk caps (see [Power and Battery](Power-and-Battery)).
