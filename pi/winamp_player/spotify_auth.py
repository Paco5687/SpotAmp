"""Spotify Web API auth — Authorization Code + PKCE over a loopback redirect.

No client secret, no hosted website. A one-time authorization spins up a tiny
local HTTP server on 127.0.0.1:<port>, catches Spotify's redirect, exchanges the
code for tokens (PKCE), and caches a **refresh token**. After that the device
refreshes access tokens forever, headless.

Run the one-time flow with:  ``python -m winamp_player.authorize``

Spotify rules this satisfies (as of the Nov 2025 OAuth migration):
  * loopback redirect with an explicit IP (``127.0.0.1``, not ``localhost``)
  * plain HTTP allowed *because* it's loopback
  * PKCE instead of an embedded client secret
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Everything the player needs: read profile/playlists/library, drive playback.
SCOPES = [
    "user-read-private",              # read account product (premium?) + country
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-library-read",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "streaming",
]


@dataclass
class Token:
    access_token: str
    refresh_token: str
    expires_at: float  # epoch seconds

    @property
    def expired(self) -> bool:
        return time.time() >= self.expires_at - 30  # refresh a bit early

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2)

    @staticmethod
    def from_json(text: str) -> "Token":
        return Token(**json.loads(text))


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


class _CallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    state: str | None = None
    error: str | None = None

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        _CallbackHandler.code = (params.get("code") or [None])[0]
        _CallbackHandler.state = (params.get("state") or [None])[0]
        _CallbackHandler.error = (params.get("error") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = ("Authorization failed: " + _CallbackHandler.error
               if _CallbackHandler.error else
               "Winamp · Physical Edition is authorized. You can close this tab.")
        self.wfile.write(f"<html><body style='font-family:sans-serif;background:#1c1e22;"
                         f"color:#2cff78;padding:3em'>{msg}</body></html>".encode())

    def log_message(self, *_args) -> None:  # silence the default logging
        pass


class Authorizer:
    def __init__(self, client_id: str, redirect_uri: str, token_path: Path) -> None:
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.token_path = Path(token_path)

    # -- one-time interactive flow ---------------------------------------- #
    def authorize_interactive(self) -> Token:
        import requests

        verifier, challenge = _pkce_pair()
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(SCOPES),
            "code_challenge_method": "S256",
            "code_challenge": challenge,
            "state": state,
        }
        url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
        port = int(urllib.parse.urlparse(self.redirect_uri).port or 80)

        print("Opening browser to authorize Spotify...")
        print(f"If it doesn't open, visit:\n  {url}\n")
        webbrowser.open(url)

        server = HTTPServer(("127.0.0.1", port), _CallbackHandler)
        while _CallbackHandler.code is None and _CallbackHandler.error is None:
            server.handle_request()
        server.server_close()

        if _CallbackHandler.error:
            raise RuntimeError(f"Spotify auth error: {_CallbackHandler.error}")
        if _CallbackHandler.state != state:
            raise RuntimeError("State mismatch — possible CSRF; aborting.")

        resp = requests.post(TOKEN_URL, data={
            "grant_type": "authorization_code",
            "code": _CallbackHandler.code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": verifier,
        }, timeout=10)
        resp.raise_for_status()
        token = self._token_from_response(resp.json())
        self.save(token)
        print(f"Authorized. Token cached at {self.token_path}")
        return token

    # -- refresh ---------------------------------------------------------- #
    def refresh(self, token: Token) -> Token:
        import requests

        resp = requests.post(TOKEN_URL, data={
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": self.client_id,
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Spotify may or may not return a new refresh token; keep the old if not.
        data.setdefault("refresh_token", token.refresh_token)
        new = self._token_from_response(data)
        self.save(new)
        return new

    def load_valid(self) -> Token | None:
        """Return a fresh access token, refreshing/loading from disk as needed."""
        if not self.token_path.exists():
            return None
        token = Token.from_json(self.token_path.read_text(encoding="utf-8"))
        if token.expired:
            token = self.refresh(token)
        return token

    # -- helpers ---------------------------------------------------------- #
    def _token_from_response(self, data: dict) -> Token:
        return Token(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=time.time() + int(data.get("expires_in", 3600)),
        )

    def save(self, token: Token) -> None:
        self.token_path.write_text(token.to_json(), encoding="utf-8")
