"""Web API response parsing (no network)."""

from winamp_player.spotify_web import track_from_item


def test_track_from_full_item():
    t = track_from_item({
        "name": "Digital Love",
        "artists": [{"name": "Daft Punk"}, {"name": "Guest"}],
        "duration_ms": 301000,
        "uri": "spotify:track:y",
        "album": {
            "name": "Discovery",
            "images": [{"url": "http://img/big.jpg"}, {"url": "http://img/small.jpg"}],
        },
    })
    assert t.title == "Digital Love"
    assert t.artist == "Daft Punk, Guest"
    assert t.album == "Discovery"
    assert t.duration_ms == 301000
    assert t.art_url == "http://img/big.jpg"   # first (largest) image


def test_track_from_minimal_item():
    t = track_from_item({})
    assert t.title == "—"
    assert t.artist == ""
    assert t.duration_ms == 0
    assert t.art_url is None


def test_track_display_name():
    t = track_from_item({"name": "Solo", "artists": []})
    assert t.display == "Solo"
    t2 = track_from_item({"name": "Song", "artists": [{"name": "Artist"}]})
    assert t2.display == "Artist - Song"
