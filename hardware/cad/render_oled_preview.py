"""SpotAmp — OLED aperture interface preview.

Simulates what the firmware draws on the 256x64 SSD1322 and what the user
actually SEES through the four front-panel apertures. Two outputs:

  oled-buffer.png  — the full framebuffer with aperture rects outlined
                     (everything outside them is hidden behind aluminum)
  oled-through-panel.png — the top 48 mm of the panel with the lit regions
                     composited through their apertures

Geometry sources (keep all three in sync):
  * aperture mm rects .... generate_panel.py (CUTOUTS in the OLED cluster)
  * pixel regions ........ firmware/src/config.h (REG_VIS/TITLE/KBPS/KHZ)
  * AA offset in module .. datasheets/nhd-3.12-25664 PDF: PCB 89.2x44.0,
                           active area 76.78x19.18 at (+6.21, +12.20)

Run:  python render_oled_preview.py
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

pygame.init()

# ---- geometry (mirrors config.h + generate_panel.py) ------------------------ #
PCB_XY = (3.5, 3.5)                    # OLED PCB top-left on the panel, mm
AA_OFF = (6.21, 12.20)                 # active-area offset within the PCB, mm
AA_MM = (76.78, 19.18)                 # active area, mm
AA_XY = (PCB_XY[0] + AA_OFF[0], PCB_XY[1] + AA_OFF[1])   # (9.71, 15.70)
PX_MM = (256 / AA_MM[0], 64 / AA_MM[1])                  # ~3.334 px/mm

APERTURES = {                          # panel mm rects, from generate_panel.py
    "vis":   (10.5, 16.5, 26.0, 17.5),
    "title": (40.0, 16.5, 44.5, 7.5),
    "kbps":  (40.0, 26.0, 13.0, 6.0),
    "khz":   (56.0, 26.0, 13.0, 6.0),
}
REGIONS = {                            # OLED px rects, from firmware config.h
    "vis":   (3, 3, 86, 58),
    "title": (101, 3, 148, 24),
    "kbps":  (101, 35, 43, 19),
    "khz":   (155, 35, 42, 19),
}
PAD = 2                                # REGION_PAD in config.h

AMBER = (255, 176, 56)
AMBER_DIM = (150, 96, 24)

# ---- render the firmware framebuffer (mirrors taskDisplay()) ----------------- #
buf = pygame.Surface((256, 64))
buf.fill((0, 0, 0))
F_TIME = pygame.font.SysFont("consolas", 30, bold=True)   # ~logisoso22_tn
F_TITLE = pygame.font.SysFont("consolas", 15, bold=True)  # ~7x13B
F_PILL = pygame.font.SysFont("consolas", 15, bold=True)


def draw_region(name, painter):
    r = pygame.Rect(REGIONS[name])
    sub = buf.subsurface(r)            # hard clip, like u8g2 setClipWindow
    painter(sub, r)


def paint_vis(s, r):
    t = F_TIME.render("0:42", True, AMBER)
    s.blit(t, (PAD, PAD - 4))
    bar_w, gap, spec_h = 4, 2, 26
    for i in range(14):                # SPEC_BARS placeholder sway
        v = 3 + ((42000 // 90 + i * 5) % 11)
        h = 1 + (v * (spec_h - 1)) // 15
        pygame.draw.rect(s, AMBER if i % 3 else AMBER_DIM,
                         (PAD + i * (bar_w + gap), r.h - PAD - h, bar_w, h))


def paint_title(s, r):
    t = F_TITLE.render("M83 - MIDNIGHT CITY", True, AMBER)
    s.blit(t, (PAD, (r.h - t.get_height()) // 2))


def paint_pill(text):
    def p(s, r):
        t = F_PILL.render(text, True, AMBER)
        s.blit(t, ((r.w - t.get_width()) // 2, (r.h - t.get_height()) // 2))
    return p


draw_region("vis", paint_vis)
draw_region("title", paint_title)
draw_region("kbps", paint_pill("320"))
draw_region("khz", paint_pill("44"))

out_dir = os.path.dirname(os.path.abspath(__file__))

# ---- output 1: framebuffer with aperture outlines ----------------------------- #
S1 = 4
fb = pygame.transform.scale(buf, (256 * S1, 64 * S1))
for name, r in REGIONS.items():
    pygame.draw.rect(fb, (70, 130, 90),
                     (r[0] * S1, r[1] * S1, r[2] * S1, r[3] * S1), 1)
frame = pygame.Surface((256 * S1 + 40, 64 * S1 + 40))
frame.fill((24, 25, 28))
frame.blit(fb, (20, 20))
pygame.image.save(frame, os.path.join(out_dir, "oled-buffer.png"))

# ---- output 2: composite through the panel ------------------------------------ #
S2 = 8                                                    # px per mm
panel = pygame.Surface((127 * S2, 48 * S2))
for y in range(panel.get_height()):                       # brushed-metal sheen
    g = 36 + int(6 * math.sin(y / panel.get_height() * math.pi))
    pygame.draw.line(panel, (g, g, g + 3), (0, y), (panel.get_width(), y))

# scaled framebuffer positioned at the AA's true panel location
aa_px = (int(AA_XY[0] * S2), int(AA_XY[1] * S2))
aa_scaled = pygame.transform.scale(
    buf, (int(AA_MM[0] * S2), int(AA_MM[1] * S2)))

for name, (ax, ay, aw, ah) in APERTURES.items():
    dest = pygame.Rect(int(ax * S2), int(ay * S2), int(aw * S2), int(ah * S2))
    pygame.draw.rect(panel, (10, 11, 13), dest.inflate(10, 10),
                     border_radius=10)                    # recessed well
    src = dest.move(-aa_px[0], -aa_px[1])                 # panel -> AA space
    panel.blit(aa_scaled, dest, src)
    pygame.draw.rect(panel, (60, 62, 68), dest.inflate(10, 10), 2,
                     border_radius=10)

F_ENG = pygame.font.SysFont("segoeui", 13)
for text, cx in (("KBPS", 46.5), ("KHZ", 62.5)):
    t = F_ENG.render(text, True, (150, 152, 158))
    panel.blit(t, (int(cx * S2) - t.get_width() // 2, int(34.5 * S2)))
for i, lab in enumerate(["NOW", "PL", "QUE"]):            # view toggles
    c = (int((98 + i * 11) * S2), int(20 * S2))
    pygame.draw.circle(panel, (12, 13, 15), c, int(3.6 * S2))
    pygame.draw.circle(panel, (52, 54, 60), c, int(3.0 * S2))
    t = F_ENG.render(lab, True, (150, 152, 158))
    panel.blit(t, (c[0] - t.get_width() // 2, int(26.5 * S2)))

pygame.image.save(panel, os.path.join(out_dir, "oled-through-panel.png"))
print("wrote oled-buffer.png + oled-through-panel.png")
