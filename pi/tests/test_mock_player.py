"""MockPlayer behavior — the simulation the UI is developed against."""

from spotamp.models import PlaybackStatus, RepeatMode, Track
from spotamp.spotify import MockPlayer


def make_player():
    p = MockPlayer()
    assert p.state.playlist, "demo playlist must not be empty"
    return p


def test_initial_state():
    p = make_player()
    assert p.state.status is PlaybackStatus.STOPPED
    assert p.state.playlist_index == 0
    assert not p.real_playback


def test_play_pause_toggles():
    p = make_player()
    p.play_pause()
    assert p.state.status is PlaybackStatus.PLAYING
    p.play_pause()
    assert p.state.status is PlaybackStatus.PAUSED


def test_prev_restarts_track_after_three_seconds():
    p = make_player()
    p.select_track(1)
    p.state.position_ms = 5000
    p.prev()
    assert p.state.playlist_index == 1      # same track…
    assert p.state.position_ms == 0         # …restarted
    p.prev()                                 # within 3s now -> previous track
    assert p.state.playlist_index == 0


def test_select_track_wraps():
    p = make_player()
    n = len(p.state.playlist)
    p.select_track(n + 2)
    assert p.state.playlist_index == 2
    assert p.state.status is PlaybackStatus.PLAYING


def test_track_end_advances():
    p = make_player()
    p.select_track(0)
    p.state.position_ms = p.state.track.duration_ms  # at the very end
    p.poll()
    assert p.state.playlist_index == 1


def test_repeat_track_restarts_same_track():
    p = make_player()
    p.select_track(3)
    p.state.repeat = RepeatMode.TRACK
    p.state.position_ms = p.state.track.duration_ms
    p.poll()
    assert p.state.playlist_index == 3
    assert p.state.position_ms == 0


def test_stop_at_playlist_end_without_repeat():
    p = make_player()
    p.select_track(len(p.state.playlist) - 1)
    p.state.repeat = RepeatMode.OFF
    p.state.position_ms = p.state.track.duration_ms
    p.poll()
    assert p.state.status is PlaybackStatus.STOPPED


def test_load_tracks_replaces_playlist_and_plays():
    p = make_player()
    tracks = [Track("A", "X", "", 1000), Track("B", "Y", "", 2000)]
    p.load_tracks(tracks)
    assert p.state.playlist == tracks
    assert p.state.track.title == "A"
    assert p.state.status is PlaybackStatus.PLAYING
    p.load_tracks([])                       # empty load is a no-op
    assert p.state.playlist == tracks


def test_eq_band_clamped():
    p = make_player()
    p.set_eq_band(0, 99.0)
    assert p.state.eq_bands[0] == 12.0
    p.set_eq_band(0, -99.0)
    assert p.state.eq_bands[0] == -12.0


def test_shuffle_and_repeat_cycle():
    p = make_player()
    p.toggle_shuffle()
    assert p.state.shuffle is True
    p.cycle_repeat()
    assert p.state.repeat is RepeatMode.CONTEXT
    p.cycle_repeat()
    assert p.state.repeat is RepeatMode.TRACK
    p.cycle_repeat()
    assert p.state.repeat is RepeatMode.OFF
