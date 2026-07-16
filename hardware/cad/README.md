# CAD — front panel

**`front-panel.dxf`** (SketchUp Pro / any CAD) and **`front-panel.svg`**
(Blender-native curve import) are both generated from
[`generate_panel.py`](generate_panel.py) — one parametric source of truth where
every dimension is a named constant traced to a datasheet. **Don't hand-edit the
DXF/SVG; edit the parameters and regenerate** (`python generate_panel.py`).

Current envelope: **175 × 280 × 32 mm** (see the height/width findings in
[../enclosure.md](../enclosure.md) — the fader mounting span drives everything).

## Layers

| Layer | Meaning | Action in CAD |
|---|---|---|
| `OUTLINE` | panel perimeter (R4 corners) | cut |
| `CUTOUTS` | windows + fader/pot slots + button holes | cut through |
| `HOLES` | mounting screw holes (true diameters: M3 clearance 3.4, pot mounts 2.4) | drill |
| `GRILLE` | speaker grille pattern (ø2, hex pitch 4.5) | drill |
| `ENGRAVE` | labels | engrave/laser — **do not cut** |
| `REF` | component bodies **behind** the panel (faders, OLED, HyperPixel) | placement aid — **delete before cutting** |
| `DIM` | notes | delete after import |

## Import

**SketchUp Pro**: File → Import → DXF, units **millimeters**. Each layer arrives
as a tag. To make the 3D panel: select the outline + cut layers → Push/Pull to
panel thickness (2–3 mm), using `REF` to position the component models. The ALPS
fader **STEP model** is downloadable from the ALPS product page (link in
[../datasheets/README.md](../datasheets/README.md)).

**Blender**: File → Import → SVG (native). Curves arrive true-to-mm (1 unit =
1 mm at default SVG import scale — verify with the 175 mm outline). Extrude the
curves for the panel solid.

## Before cutting anything

- Cross-check every **VERIFY**-marked constant in `generate_panel.py` against the
  physical part (fader M3 span & slot, HyperPixel bezel, OLED window, slide-pot
  mounts) — datasheet revisions and clone parts vary.
- The checker enforces 2D clearances only. Two known **3D stacking questions**
  for CAD: (1) transport-button PCB vs the volume fader body (~0.75 mm apart
  behind the panel), (2) grille back-volume vs the seek fader motor. Both have
  room to shift a few mm if needed — change the constant, regenerate.
- Grille zones are modest (24×16 mm each); the side walls can carry additional
  grille if the speakers want more open area — that's a body decision, not a
  panel one.

## Sanity checks built into the generator

Bounds (everything inside the walls) + all-pairs clearance between every cut
feature (circle/rect/rect-circle, ≥1.5 mm). The generator **refuses to emit** a
drawing that fails — extend the checks rather than bypassing them.
