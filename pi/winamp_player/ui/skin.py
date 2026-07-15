"""Skin: the WinAmp-inspired look, rebuilt from scratch (no ripped bitmaps).

Colors and layout live here so the renderer stays about drawing, not constants.
The classic cues we recreate: brushed dark-gray metal, a black LCD readout with
phosphor-green text, thin beveled edges, and a green spectrum analyzer.

Layout is portrait to match the physical unit (5" wide × 8" tall). Regions are
tagged PHYSICAL (a real knob/button/fader on the device) or SCREEN (drawn on the
color touchscreen), so the mock can shade them and you can see the industrial
design at a glance.
"""

from __future__ import annotations

from dataclasses import dataclass

# -- palette ---------------------------------------------------------------- #
BG = (28, 30, 34)
METAL = (54, 57, 63)
METAL_HI = (78, 82, 90)
METAL_LO = (34, 36, 40)
BEVEL_LIGHT = (96, 100, 110)
BEVEL_DARK = (18, 19, 22)

LCD_BG = (8, 18, 12)
LCD_GREEN = (44, 255, 120)
LCD_GREEN_DIM = (28, 130, 70)
LCD_AMBER = (255, 190, 60)

SPECTRUM_TOP = (120, 255, 160)
SPECTRUM_BOT = (28, 150, 90)
SPECTRUM_PEAK = (220, 255, 220)

TEXT = (210, 214, 222)
TEXT_DIM = (130, 135, 145)
ACCENT = (44, 255, 120)

# Region shading in the mock (RGBA over the panel).
PHYSICAL_TINT = (90, 130, 255, 26)   # cool = real hardware
SCREEN_TINT = (255, 170, 40, 22)     # warm = the LCD touchscreen


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    def contains(self, px: int, py: int) -> bool:
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2


@dataclass(frozen=True)
class Layout:
    """All widget rectangles, computed from the window size (portrait)."""

    W: int
    H: int

    def __post_init__(self) -> None:
        pass

    # -- top: title + LCD readout + transport (PHYSICAL region) ----------- #
    @property
    def title_bar(self) -> Rect:
        return Rect(0, 0, self.W, 30)

    @property
    def main_panel(self) -> Rect:
        return Rect(0, 30, self.W, 180)

    @property
    def lcd(self) -> Rect:
        return Rect(14, 44, self.W - 28, 74)

    @property
    def spectrum(self) -> Rect:
        return Rect(14, 122, self.W - 28, 46)

    @property
    def transport(self) -> Rect:
        # Row of transport buttons. Buttons laid out by the renderer.
        return Rect(14, 174, self.W - 28, 30)

    # -- middle: the color LCD touchscreen (SCREEN region) ---------------- #
    @property
    def screen(self) -> Rect:
        return Rect(0, 210, self.W, self.H - 210 - 200)

    @property
    def album_art(self) -> Rect:
        s = self.screen
        size = min(s.w - 24, 150)
        return Rect(s.x + 12, s.y + 12, size, size)

    @property
    def playlist(self) -> Rect:
        s = self.screen
        top = self.album_art.y + self.album_art.h + 12
        return Rect(s.x + 12, top, s.w - 24, s.y + s.h - top - 12)

    # -- lower: EQ faders (PHYSICAL region) ------------------------------- #
    @property
    def eq_panel(self) -> Rect:
        return Rect(0, self.H - 200, self.W, 130)

    # -- bottom: volume + seek faders (PHYSICAL region) ------------------- #
    @property
    def bottom_panel(self) -> Rect:
        return Rect(0, self.H - 70, self.W, 70)

    @property
    def volume_fader(self) -> Rect:
        return Rect(14, self.H - 54, (self.W - 40) // 2, 18)

    @property
    def seek_fader(self) -> Rect:
        w = (self.W - 40) // 2
        return Rect(self.W - 14 - w, self.H - 54, w, 18)
