"""Skin: the WinAmp-inspired palette + drawing primitives (no ripped bitmaps).

Colors and the ``Rect`` helper live here so the screen UI stays about drawing,
not constants. The classic cues we keep: dark metal panels, phosphor-green
accents, amber warnings, thin beveled edges. Themes will layer on top of this
later (planned: swappable palettes).
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

# Spectrum analyzer colors (returns in Phase 4 with the real FFT tap).
SPECTRUM_TOP = (120, 255, 160)
SPECTRUM_BOT = (28, 150, 90)
SPECTRUM_PEAK = (220, 255, 220)

TEXT = (210, 214, 222)
TEXT_DIM = (130, 135, 145)
ACCENT = (44, 255, 120)


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
