"""WinAmp physical media player — Raspberry Pi application.

A handheld, book-sized Spotify player styled after the classic WinAmp UI.
This package drives the color LCD (playlist / album art / spectrum), talks to
Spotify via go-librespot, and bridges to a microcontroller that owns the
physical controls (buttons, pots, encoders, and motorized faders).

Run it on a laptop with everything mocked:

    cd pi
    pip install -r requirements.txt
    python -m winamp_player
"""

__version__ = "0.1.0"
