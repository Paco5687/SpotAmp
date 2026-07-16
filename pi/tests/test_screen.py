"""Headless render smoke tests for the multi-view screen UI.

Each view must draw without raising and actually paint something. Also covers
view switching and the touch hit-testing of the tab strip.
"""

import pygame
import pytest

from spotamp.library import BrowseState
from spotamp.models import PlaybackStatus, PlayerState, Track
from spotamp.spotify_web import Playlist
from spotamp.ui import skin
from spotamp.ui.screen import VIEWS, ScreenUI


@pytest.fixture(scope="module")
def surface():
    pygame.init()
    return pygame.display.set_mode((720, 720))


@pytest.fixture()
def state():
    st = PlayerState()
    st.status = PlaybackStatus.PLAYING
    st.track = Track("Midnight City", "M83", "Hurry Up, We're Dreaming", 241000)
    st.position_ms = 96000
    st.battery_percent = 72.0
    st.queue = [Track("Digital Love", "Daft Punk", "Discovery", 301000)]
    return st


@pytest.fixture()
def browse():
    br = BrowseState()
    br.playlists = [
        Playlist("1", "Late Night Drive", "spotify:playlist:1", 47, None, True),
        Playlist("2", "Discover Weekly", "spotify:playlist:2", 0, None, False),
    ]
    return br


def painted(surface) -> bool:
    """True if the frame contains any non-background pixels."""
    seen = pygame.transform.average_color(surface)[:3]
    return seen != skin.BG


@pytest.mark.parametrize("view", [v[0] for v in VIEWS])
def test_each_view_renders(surface, state, browse, view):
    actions = []
    ui = ScreenUI(surface, on_action=lambda a, **k: actions.append((a, k)))
    ui.set_view(view)
    ui.update(state, 0.03)
    ui.draw(state, browse)
    assert ui.view == view
    assert painted(surface)


def test_views_render_with_empty_state(surface):
    """No track, no playlists, no battery — nothing may crash."""
    ui = ScreenUI(surface, on_action=lambda a, **k: None)
    empty = PlayerState()
    for name, *_ in VIEWS:
        ui.set_view(name)
        ui.draw(empty, BrowseState())


def test_set_view_rejects_unknown(surface):
    ui = ScreenUI(surface, on_action=lambda a, **k: None)
    ui.set_view("nonsense")
    assert ui.view == "now_playing"


def test_cycle_view_wraps(surface):
    ui = ScreenUI(surface, on_action=lambda a, **k: None)
    names = [v[0] for v in VIEWS]
    for expected in names[1:] + names[:1]:
        ui.cycle_view(1)
        assert ui.view == expected


def test_tab_tap_switches_view(surface, state, browse):
    ui = ScreenUI(surface, on_action=lambda a, **k: None)
    ui.draw(state, browse)                      # draw computes tab rects
    tab = ui._tab_rects["queue"]
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(tab.cx, tab.cy))
    ui.handle_event(ev, state, browse)
    assert ui.view == "queue"


def test_playlist_tap_emits_open_action(surface, state, browse):
    actions = []
    ui = ScreenUI(surface, on_action=lambda a, **k: actions.append((a, k)))
    ui.set_view("playlists")
    ui.draw(state, browse)                      # draw computes row rects
    row, idx = ui._row_rects[0]
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(row.cx, row.cy))
    ui.handle_event(ev, state, browse)
    assert ("open_playlist", {"index": idx}) in actions
