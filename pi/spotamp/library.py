"""Browsing layer: the user's Spotify playlists, loaded off the UI thread.

Separate from playback (``PlayerBackend``): this is the *metadata/browse* side,
backed by the Web API. Network calls run on background threads and results are
delivered through a queue the app drains each frame, so the UI never blocks.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field

from .models import Track
from .spotify_web import Playlist, SpotifyWeb


@dataclass
class BrowseState:
    """Library state the screen UI renders (distinct from PlayerState)."""

    playlists: list[Playlist] = field(default_factory=list)
    loading: bool = False
    error: str = ""


class Library:
    """Async access to the user's playlists and their tracks."""

    def __init__(self, web: SpotifyWeb) -> None:
        self._web = web
        self._events: queue.Queue[tuple[str, object]] = queue.Queue()

    def start(self) -> None:
        threading.Thread(target=self._load_playlists, daemon=True).start()

    def open_playlist(self, playlist: Playlist) -> None:
        threading.Thread(target=self._load_tracks, args=(playlist,), daemon=True).start()

    def poll(self) -> list[tuple[str, object]]:
        """Drain completed loads. Returns ('playlists', list) / ('tracks', (pl, list))
        / ('error', str)."""
        out = []
        while not self._events.empty():
            out.append(self._events.get())
        return out

    # -- background workers ----------------------------------------------- #
    def _load_playlists(self) -> None:
        try:
            self._events.put(("playlists", self._web.playlists()))
        except Exception as e:  # noqa: BLE001
            self._events.put(("error", f"playlists: {e}"))

    def _load_tracks(self, playlist: Playlist) -> None:
        try:
            tracks: list[Track] = self._web.playlist_tracks(playlist.id)
            self._events.put(("tracks", (playlist, tracks)))
        except Exception as e:  # noqa: BLE001
            self._events.put(("error", f"tracks: {e}"))


def make_library(web: SpotifyWeb | None) -> tuple[Library | None, str]:
    """Build a Library from a shared web client (or None if unauthorized)."""
    if web is None:
        return None, "no Spotify token — run `python -m spotamp.authorize`"
    return Library(web), "ok"
