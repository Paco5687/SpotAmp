# SpotAmp

A handheld, book-sized Spotify player styled after classic WinAmp — color LCD
touchscreen for the playlist, real physical buttons, pots, and **motorized
faders** for a graphic EQ plus volume and a seek fader that follows the song.

**Open source (MIT).** Build one yourself — this wiki has everything you need.

> ⚠️ **Placeholder wiki.** Content is being filled in as the build progresses.

## Start here
- **[Bill of Materials](Bill-of-Materials)** — every part + rough cost (~$430–480)
- **[Assembly](Assembly)** — wiring, enclosure, putting it together
- **[Power and Battery](Power-and-Battery)** — battery sizing, safe shutdown
- **[Software Setup](Software-Setup)** — flash, install, run
- **[Spotify Setup](Spotify-Setup)** — standalone auth (no phone needed)
- **[Firmware](Firmware)** — the RP2040 controls board
- **[Troubleshooting](Troubleshooting)**

## What it does
- Plays **Spotify** playlists (Premium) fully standalone — network + account only.
- WinAmp-style UI: green LCD readout, spectrum analyzer, album art, playlist.
- Motorized faders that physically track playback and EQ presets.

## Status
The core device works: a Pi 4 B that **boots straight into its own multi-view UI**
on a HyperPixel 4.0 Square touchscreen and plays Spotify **standalone** (no phone).
In progress: physical controls (RP2040), motorized faders, EQ + spectrum, battery,
enclosure. See the [project board](https://github.com/users/Paco5687/projects/4)
and [repo README](https://github.com/Paco5687/SpotAmp).
