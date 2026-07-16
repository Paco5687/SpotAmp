"""LibrespotPlayer /status parsing — the mapping that bit us on real hardware.

Regression tests for the two bugs found on the device (2026-07-15):
live position lives at track.position (not top-level), and volume is scaled
by volume_steps (0-100), not 0-65535.
"""

from spotamp.models import PlaybackStatus
from spotamp.spotify import LibrespotPlayer

STATUS = {
    "username": "user",
    "paused": False,
    "stopped": False,
    "buffering": False,
    "volume": 50,
    "volume_steps": 100,
    "shuffle_context": True,
    "track": {
        "name": "Midnight City",
        "artist_names": ["M83"],
        "album_name": "Hurry Up, We're Dreaming",
        "duration": 241000,
        "position": 96000,
        "uri": "spotify:track:x",
        "album_cover_url": "http://img/cover.jpg",
    },
}


def make_player():
    return LibrespotPlayer("http://localhost:3678")


def test_position_read_from_track_object():
    p = make_player()
    p._apply_status(STATUS)
    assert p.state.position_ms == 96000


def test_volume_scaled_by_volume_steps():
    p = make_player()
    p._apply_status(STATUS)
    assert abs(p.state.volume - 0.5) < 1e-6
    # A hypothetical 16-step device still maps to 0..1.
    p._apply_status({**STATUS, "volume": 8, "volume_steps": 16})
    assert abs(p.state.volume - 0.5) < 1e-6


def test_track_metadata_and_art():
    p = make_player()
    p._apply_status(STATUS)
    t = p.state.track
    assert t.title == "Midnight City"
    assert t.artist == "M83"
    assert t.duration_ms == 241000
    assert t.art_url == "http://img/cover.jpg"


def test_status_mapping():
    p = make_player()
    p._apply_status(STATUS)
    assert p.state.status is PlaybackStatus.PLAYING
    assert p.state.shuffle is True
    p._apply_status({**STATUS, "paused": True})
    assert p.state.status is PlaybackStatus.PAUSED
    p._apply_status({**STATUS, "stopped": True})
    assert p.state.status is PlaybackStatus.STOPPED


def test_empty_status_is_safe():
    p = make_player()
    p._apply_status({})
    assert p.state.track.title == "—"
    assert p.state.position_ms == 0
