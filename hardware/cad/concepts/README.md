# Layout concepts (exploration — not the authoritative drawing)

**concept-c — "the in-between" (220 × 280 mm)**: the vibe-keeper. Screen stays
**centered** (classic stacked-module composition), full **10-band EQ + preamp**,
and **symmetric stereo grille fields** flanking the screen (L/R where stereo
wants them). No pot column. Button columns cleared of the HyperPixel board edge
(3D check). Owner feedback path: A = vibe but 7-band · B = 10-band but vibe lost
· **C = both**.


**concept-b** (225 × 280 mm): screen offset left, right-hand pot column
(HP-vol / brightness / 2 assignable), one large speaker-grille field, and the
**full classic 10-band EQ + preamp** (11 motorized faders). Generated from a
variant of [`../generate_panel.py`](../generate_panel.py); if chosen, the
variant becomes the main generator's parameters and this folder is cleaned up.

I/O check at 11 faders: 22/32 PCA9685 PWM · 11/12 MPR121 electrodes · 14/16 mux
channels — fits the existing architecture. Cost delta ≈ +$65–70.

Print the SVG at 100 % scale for the paper test (same as the main panel).
