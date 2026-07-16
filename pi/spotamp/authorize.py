"""One-time Spotify authorization.

    python -m spotamp.authorize

Reads client id + redirect from config.toml, runs the loopback PKCE flow, and
caches the refresh token. Run this once on the device (or your laptop) after
creating a Spotify app and adding the redirect URI it prints below.
"""

from __future__ import annotations

import sys

from .config import Config
from .spotify_auth import Authorizer


def main() -> int:
    cfg = Config.load()
    if not cfg.spotify_client_id:
        print("Set spotify_client_id in config.toml first "
              "(create an app at https://developer.spotify.com/dashboard).")
        return 1
    print(f"Redirect URI to register in the Spotify dashboard:\n"
          f"  {cfg.spotify_redirect_uri}\n")
    auth = Authorizer(cfg.spotify_client_id, cfg.spotify_redirect_uri, cfg.token_path())
    try:
        auth.authorize_interactive()
    except Exception as e:  # noqa: BLE001
        print(f"Authorization failed: {e}")
        return 1

    # Prove Web API access with a real call (this is the true test of whether
    # the "Web API" checkbox in the dashboard actually matters).
    try:
        from .spotify_web import SpotifyWeb

        web = SpotifyWeb(auth)
        me = web.me()
        who = me.get("display_name") or me.get("id") or "unknown"
        print(f"\n✓ Web API confirmed — logged in as {who} "
              f"· {web.playlist_count()} playlists.")
        print(f"  Account: {me.get('product', 'unknown')} "
              f"(playback control needs 'premium').")
    except Exception as e:  # noqa: BLE001
        body = getattr(getattr(e, "response", None), "text", "") or ""
        print(f"\n⚠ OAuth succeeded but the Web API call failed:\n  {e}")
        if body:
            print(f"  Spotify says: {body.strip()[:300]}")
        print("  A 403 'User not approved for app' means you must add this "
              "account under\n  Dashboard → your app → User Management, then "
              "re-run this command.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
