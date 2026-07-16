#!/usr/bin/env python3
"""Front-panel cutout drawing generator — WinAmp Physical Edition.

Emits, from ONE parametric geometry description:
  * front-panel.dxf — layered DXF (mm) for SketchUp Pro / any CAD
  * front-panel.svg — mm-accurate SVG for Blender (native curve import) / web

Every dimension is a named constant traceable to a datasheet (see
hardware/datasheets/). Coordinates are laid out top-left-origin in mm and
flipped to DXF's Y-up at emit time.

Layers:
  OUTLINE   panel outline (cut)
  CUTOUTS   windows + slots (cut through)
  HOLES     drilled holes (cut through; circles carry true diameter)
  GRILLE    speaker grille hole pattern (cut through)
  ENGRAVE   labels (engrave/laser, not cut)
  REF       component body outlines BEHIND the panel (do not cut — placement aid)
  DIM       dimension callouts (text; delete after import if unwanted)

Run:  python generate_panel.py     (writes into this directory)
"""

from __future__ import annotations

import math

import ezdxf

# =========================================================================== #
# Parameters — all mm. Sources noted. VERIFY marked items before cutting metal.
# =========================================================================== #

PANEL_W = 175.0
PANEL_H = 280.0
WALL = 3.0                     # enclosure wall thickness (interior = panel - 2*WALL)
CORNER_R = 4.0                 # panel corner radius (machinable)

# ALPS RS60N11M9A0F motorized fader — datasheets/alps-rs60n-motorized-fader.pdf
FADER_BODY_LEN = 106.5         # overall body length (54 + 52.5 top view)
FADER_BODY_W = 18.5            # body width -> min pitch ~19
FADER_M3_SPAN = 80.0           # M3 mounting holes, center-to-center  (VERIFY p.2)
FADER_SLOT_LEN = 62.0          # 60 travel + lever clearance
FADER_SLOT_W = 3.0
FADER_M3_DIA = 3.4             # M3 clearance
FADER_PITCH = 19.0             # EQ bank pitch (bodies 18.5 -> 0.5 gap)

# HyperPixel 4.0 Square — product page (VERIFY against physical part)
SCREEN_WIN = 73.0              # active area 72x72 + 0.5 reveal
SCREEN_BOARD_W = 85.0
SCREEN_BOARD_H = 85.5

# NHD-3.12-25664 OLED — datasheets/nhd-3.12-25664-oled-module.pdf (VERIFY)
OLED_WIN_W, OLED_WIN_H = 78.0, 20.5      # active 76.78 x 19.18 + reveal
OLED_MOD_W, OLED_MOD_H = 88.0, 27.8

BTN_DIA = 13.0                 # 12 mm tactile cap clearance
ENC_DIA = 7.4                  # Bourns PEC11 bushing (7.0 + clearance)
LED_SLIT_W, LED_SLIT_H = 52.0, 4.0       # NeoPixel stick 8 (51.1 x 10.2 board)
BAL_SLOT_LEN, BAL_SLOT_W = 32.0, 2.5     # 45 mm slide pot, 30 mm travel (VERIFY)
BAL_M_SPAN, BAL_M_DIA = 41.0, 2.4        # slide-pot mount (VERIFY vs actual pot)

GRILLE_HOLE_D = 2.0            # speaker grille drill
GRILLE_PITCH = 4.5             # hex pattern pitch

# ---- vertical stack (top-of-panel = 0) ------------------------------------ #
Y_TOP_MODULE = 0.0             # OLED + LED + transport + aux buttons
Y_VOLUME = 46.0                # horizontal motorized volume row
Y_SCREEN = 66.0                # screen module (window centered below)
Y_SEEK = 143.0                 # horizontal motorized seek row
Y_EQ = 163.0                   # vertical EQ bank to bottom

CX = PANEL_W / 2.0             # 87.5


# =========================================================================== #
# Geometry model: lists of primitives per layer
# =========================================================================== #
rects: list[tuple[str, float, float, float, float]] = []    # layer, x, y, w, h
circles: list[tuple[str, float, float, float]] = []          # layer, cx, cy, dia
texts: list[tuple[str, float, float, str, float]] = []       # layer, x, y, s, h


def rect(layer, x, y, w, h):
    rects.append((layer, x, y, w, h))


def circle(layer, cx, cy, dia):
    circles.append((layer, cx, cy, dia))


def text(layer, x, y, s, h=2.5):
    texts.append((layer, x, y, s, h))


def hfader(cx_, cy_, label):
    """Horizontal motorized fader: slot + M3s + REF body."""
    rect("CUTOUTS", cx_ - FADER_SLOT_LEN / 2, cy_ - FADER_SLOT_W / 2,
         FADER_SLOT_LEN, FADER_SLOT_W)
    circle("HOLES", cx_ - FADER_M3_SPAN / 2, cy_, FADER_M3_DIA)
    circle("HOLES", cx_ + FADER_M3_SPAN / 2, cy_, FADER_M3_DIA)
    rect("REF", cx_ - FADER_BODY_LEN / 2, cy_ - FADER_BODY_W / 2,
         FADER_BODY_LEN, FADER_BODY_W)
    text("ENGRAVE", cx_ - FADER_SLOT_LEN / 2, cy_ + 6.5, label)


def vfader(cx_, cy_, label):
    """Vertical motorized fader (EQ bank)."""
    rect("CUTOUTS", cx_ - FADER_SLOT_W / 2, cy_ - FADER_SLOT_LEN / 2,
         FADER_SLOT_W, FADER_SLOT_LEN)
    circle("HOLES", cx_, cy_ - FADER_M3_SPAN / 2, FADER_M3_DIA)
    circle("HOLES", cx_, cy_ + FADER_M3_SPAN / 2, FADER_M3_DIA)
    rect("REF", cx_ - FADER_BODY_W / 2, cy_ - FADER_BODY_LEN / 2,
         FADER_BODY_W, FADER_BODY_LEN)
    text("ENGRAVE", cx_ - 3.2, cy_ - FADER_BODY_LEN / 2 - 1.5, label, 2.2)


def button(cx_, cy_, label=None, label_dy=9.5):
    circle("CUTOUTS", cx_, cy_, BTN_DIA)
    if label:
        text("ENGRAVE", cx_ - len(label) * 1.05, cy_ + label_dy, label, 2.2)


def grille(x0, y0, x1, y1):
    """Hex-packed grille holes filling the rect, honoring edge margin."""
    m = GRILLE_HOLE_D
    row_h = GRILLE_PITCH * math.sqrt(3) / 2
    j = 0
    y = y0 + m
    while y <= y1 - m:
        x = x0 + m + (GRILLE_PITCH / 2 if j % 2 else 0)
        while x <= x1 - m:
            circle("GRILLE", x, y, GRILLE_HOLE_D)
            x += GRILLE_PITCH
        y += row_h
        j += 1


# =========================================================================== #
# Layout
# =========================================================================== #

# ---- top module ------------------------------------------------------------ #
# OLED window (module REF behind)
oled_cx, oled_cy = 10 + OLED_WIN_W / 2, 7.5 + OLED_WIN_H / 2    # (49, 17.75)
rect("CUTOUTS", 10, 7.5, OLED_WIN_W, OLED_WIN_H)
rect("REF", oled_cx - OLED_MOD_W / 2, oled_cy - OLED_MOD_H / 2, OLED_MOD_W, OLED_MOD_H)
text("ENGRAVE", 10, 6.0, "OLED 256x64", 2.0)

# LED VU slit, top right (right of the OLED module, above the balance pot)
rect("CUTOUTS", 95.0, 8.0, LED_SLIT_W, LED_SLIT_H)

# balance slide pot, under the LED slit
bal_cx, bal_cy = 121.0, 22.0
rect("CUTOUTS", bal_cx - BAL_SLOT_LEN / 2, bal_cy - BAL_SLOT_W / 2,
     BAL_SLOT_LEN, BAL_SLOT_W)
circle("HOLES", bal_cx - BAL_M_SPAN / 2, bal_cy, BAL_M_DIA)
circle("HOLES", bal_cx + BAL_M_SPAN / 2, bal_cy, BAL_M_DIA)
text("ENGRAVE", bal_cx - 5, bal_cy + 6.5, "L  BAL  R", 2.0)

# encoders, below balance
circle("CUTOUTS", 108.0, 36.0, ENC_DIA)
circle("CUTOUTS", 130.0, 36.0, ENC_DIA)
text("ENGRAVE", 103.0, 45.0, "SCROLL", 2.0)
text("ENGRAVE", 126.0, 45.0, "MENU", 2.0)

# right aux button column
button(155.0, 10.0, "SHUF")
button(155.0, 27.0, "LOOP")
button(155.0, 44.0, "AUX")

# transport row (5)
for i, lab in enumerate(["PREV", "PLAY", "PAUSE", "STOP", "NEXT"]):
    button(14.0 + i * 17.5, 39.5, lab)

# ---- volume row -------------------------------------------------------------- #
hfader(60.0, 56.0, "VOLUME")

# ---- screen ------------------------------------------------------------------ #
scr_cy = Y_SCREEN + 4 + SCREEN_WIN / 2          # window y 70..143
rect("CUTOUTS", CX - SCREEN_WIN / 2, Y_SCREEN + 4, SCREEN_WIN, SCREEN_WIN)
rect("REF", CX - SCREEN_BOARD_W / 2, scr_cy - SCREEN_BOARD_H / 2,
     SCREEN_BOARD_W, SCREEN_BOARD_H)
text("ENGRAVE", CX - 22, Y_SCREEN + 2.5, "HYPERPIXEL 4.0 SQUARE", 2.0)

# view buttons right of screen; EQ toggles left of screen
button(155.0, 85.0, "NOW", 11)
button(155.0, 106.5, "LIST", 11)
button(155.0, 128.0, "QUEUE", 11)
button(20.0, 85.0, "EQ", 11)
button(20.0, 106.5, "PRESET", 11)

# speaker grilles flank the seek row (fader body spans x 34..141 there)
grille(6.0, 145.0, 30.0, 161.0)
grille(PANEL_W - 30.0, 145.0, PANEL_W - 6.0, 161.0)

# ---- seek row ----------------------------------------------------------------- #
hfader(CX, 153.0, "SEEK")

# ---- EQ bank ------------------------------------------------------------------- #
eq_cy = Y_EQ + 3.75 + FADER_BODY_LEN / 2        # body y 166.75..273.25
labels = ["PRE", "60", "150", "400", "1K", "2K4", "6K", "15K"]
xs = [16.0] + [44.0 + i * FADER_PITCH for i in range(7)]
for x, lab in zip(xs, labels):
    vfader(x, eq_cy, lab)

# ---- outline + dims -------------------------------------------------------------- #
text("DIM", 2, PANEL_H + 4, f"PANEL {PANEL_W:.0f} x {PANEL_H:.0f} mm — units: mm", 3.5)
text("DIM", 2, PANEL_H + 9,
     "EQ pitch 19.0 · fader slots 62x3 / M3 span 80 · screen win 73x73 · VERIFY-marked dims vs datasheets before cutting", 2.5)

# =========================================================================== #
# Sanity checks — fail loudly rather than emit a bad drawing
# =========================================================================== #
def check():
    inner = (WALL, WALL, PANEL_W - WALL, PANEL_H - WALL)
    problems = []
    for layer, x, y, w, h in rects:
        if layer in ("CUTOUTS", "REF"):
            if x < inner[0] - 1e-6 or y < inner[1] - 1e-6 or \
               x + w > inner[2] + 1e-6 or y + h > inner[3] + 1e-6:
                problems.append(f"{layer} rect out of interior: {x},{y} {w}x{h}")
    for layer, cx_, cy_, d in circles:
        r = d / 2
        if layer in ("CUTOUTS", "HOLES", "GRILLE"):
            if cx_ - r < inner[0] or cy_ - r < inner[1] or \
               cx_ + r > inner[2] or cy_ + r > inner[3]:
                problems.append(f"{layer} circle out of interior: {cx_},{cy_} d{d}")
    # NO two cut features may come within CLEAR mm of each other, any shape.
    CLEAR = 1.5
    cut_circles = [(cx_, cy_, d / 2) for (ly, cx_, cy_, d) in circles
                   if ly in ("CUTOUTS", "HOLES", "GRILLE")]
    cut_rects = [(x, y, w, h) for (ly, x, y, w, h) in rects if ly == "CUTOUTS"]

    def circ_circ(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1]) - a[2] - b[2]

    def rect_circ(r, c):
        qx = max(r[0], min(c[0], r[0] + r[2]))
        qy = max(r[1], min(c[1], r[1] + r[3]))
        return math.hypot(c[0] - qx, c[1] - qy) - c[2]

    def rect_rect(a, b):
        dx = max(a[0] - (b[0] + b[2]), b[0] - (a[0] + a[2]), 0)
        dy = max(a[1] - (b[1] + b[3]), b[1] - (a[1] + a[3]), 0)
        return math.hypot(dx, dy)

    for i in range(len(cut_circles)):
        for j in range(i + 1, len(cut_circles)):
            a, b = cut_circles[i], cut_circles[j]
            near_grille = any(abs(a[2] - GRILLE_HOLE_D / 2) < .01 for _ in [0]) and \
                          abs(b[2] - GRILLE_HOLE_D / 2) < .01
            if circ_circ(a, b) < (0.8 if near_grille else CLEAR):
                problems.append(f"circles too close: {a} & {b}")
    for r in cut_rects:
        for c in cut_circles:
            if rect_circ(r, c) < CLEAR:
                problems.append(f"rect/circle too close: {r} & {c}")
    for i in range(len(cut_rects)):
        for j in range(i + 1, len(cut_rects)):
            if rect_rect(cut_rects[i], cut_rects[j]) < CLEAR:
                problems.append(f"rects too close: {cut_rects[i]} & {cut_rects[j]}")
    if problems:
        raise SystemExit("GEOMETRY ERRORS:\n  " + "\n  ".join(problems))
    print(f"geometry ok: {len(rects)} rects, {len(circles)} circles, "
          f"{len(texts)} labels")


# =========================================================================== #
# Emit DXF
# =========================================================================== #
LAYER_COLORS = {"OUTLINE": 7, "CUTOUTS": 1, "HOLES": 2, "GRILLE": 3,
                "ENGRAVE": 4, "REF": 8, "DIM": 9}


def fy(y):           # top-left layout -> DXF Y-up
    return PANEL_H - y


def emit_dxf(path="front-panel.dxf"):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4                     # millimeters
    msp = doc.modelspace()
    for name, color in LAYER_COLORS.items():
        doc.layers.add(name, color=color)

    # outline with corner radius
    r, w, h = CORNER_R, PANEL_W, PANEL_H
    pl = msp.add_lwpolyline(
        [(r, 0), (w - r, 0), (w, r), (w, h - r), (w - r, h), (r, h), (0, h - r), (0, r)],
        format="xy", dxfattribs={"layer": "OUTLINE", "closed": True})
    # bulge the 4 corners (arc segments): set bulge on the vertex leading into each arc
    b = math.tan(math.radians(90) / 4)
    for idx in (1, 3, 5, 7):
        x, y, *_ = pl[idx]
        pl[idx] = (x, y, 0, 0, b)

    for layer, x, y, rw, rh in rects:
        msp.add_lwpolyline(
            [(x, fy(y)), (x + rw, fy(y)), (x + rw, fy(y + rh)), (x, fy(y + rh))],
            format="xy", dxfattribs={"layer": layer, "closed": True})
    for layer, cx_, cy_, d in circles:
        msp.add_circle((cx_, fy(cy_)), d / 2, dxfattribs={"layer": layer})
    for layer, x, y, s, hgt in texts:
        msp.add_text(s, dxfattribs={"layer": layer, "height": hgt,
                                    "insert": (x, fy(y))})
    doc.saveas(path)
    print("wrote", path)


# =========================================================================== #
# Emit SVG (mm-accurate: width/height in mm, viewBox 1 unit = 1 mm)
# =========================================================================== #
SVG_STYLE = {"OUTLINE": ("#222", 0.5), "CUTOUTS": ("#c00", 0.35),
             "HOLES": ("#c60", 0.35), "GRILLE": ("#080", 0.25),
             "ENGRAVE": ("#06c", 0.2), "REF": ("#999", 0.25), "DIM": ("#666", 0.2)}


def emit_svg(path="front-panel.svg"):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PANEL_W}mm" '
           f'height="{PANEL_H + 14}mm" viewBox="0 0 {PANEL_W} {PANEL_H + 14}" '
           f'font-family="monospace">',
           f'<rect x="0" y="0" width="{PANEL_W}" height="{PANEL_H}" rx="{CORNER_R}" '
           f'fill="none" stroke="#222" stroke-width="0.5"/>']
    for layer, x, y, w, h in rects:
        col, sw = SVG_STYLE[layer]
        dash = ' stroke-dasharray="1.5 1"' if layer == "REF" else ""
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                   f'stroke="{col}" stroke-width="{sw}"{dash}/>')
    for layer, cx_, cy_, d in circles:
        col, sw = SVG_STYLE[layer]
        out.append(f'<circle cx="{cx_}" cy="{cy_}" r="{d / 2}" fill="none" '
                   f'stroke="{col}" stroke-width="{sw}"/>')
    for layer, x, y, s, hgt in texts:
        col, _ = SVG_STYLE[layer]
        out.append(f'<text x="{x}" y="{y}" font-size="{hgt}" fill="{col}">{s}</text>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    check()
    emit_dxf()
    emit_svg()
