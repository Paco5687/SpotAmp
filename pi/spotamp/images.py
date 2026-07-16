"""Async album-art loader with caching.

Downloads album/playlist artwork on background threads (network) and hands the
bytes to the main thread, which decodes them into pygame surfaces (pygame image
ops must stay on the main thread). Widgets call ``get(url, size)`` each frame and
get ``None`` until the image is ready — then a scaled, cached surface.
"""

from __future__ import annotations

import io
import queue
import threading

import pygame


class ImageCache:
    def __init__(self) -> None:
        self._raw: dict[str, pygame.Surface] = {}          # url -> full surface
        self._scaled: dict[tuple[str, int, int], pygame.Surface] = {}
        self._pending: set[str] = set()
        self._done: queue.Queue[tuple[str, bytes | None]] = queue.Queue()

    def get(self, url: str | None, size: tuple[int, int]) -> pygame.Surface | None:
        """Return a scaled surface for ``url``, or None if not ready yet."""
        if not url:
            return None
        w, h = int(size[0]), int(size[1])
        key = (url, w, h)
        if key in self._scaled:
            return self._scaled[key]
        if url in self._raw:
            scaled = pygame.transform.smoothscale(self._raw[url], (w, h))
            self._scaled[key] = scaled
            return scaled
        self._request(url)
        return None

    def _request(self, url: str) -> None:
        if url in self._pending:
            return
        self._pending.add(url)
        threading.Thread(target=self._fetch, args=(url,), daemon=True).start()

    def _fetch(self, url: str) -> None:
        data: bytes | None = None
        try:
            import requests

            data = requests.get(url, timeout=10).content
        except Exception:  # noqa: BLE001 — a missing image must never crash the UI
            data = None
        self._done.put((url, data))

    def pump(self) -> None:
        """Decode any freshly downloaded images. Call on the main thread each frame."""
        while not self._done.empty():
            url, data = self._done.get()
            self._pending.discard(url)
            if not data:
                continue
            try:
                surf = pygame.image.load(io.BytesIO(data)).convert_alpha()
                self._raw[url] = surf
            except Exception:  # noqa: BLE001
                pass
