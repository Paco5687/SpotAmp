# Bill of Materials

Prices are rough USD, mid-2020s, single-unit hobby quantities. This is a
**buildable** BOM for the full build you chose: motorized graphic EQ + motorized
volume + motorized seek, single integrated body.

> ⚠️ **Read the fader note first — it's the biggest cost and space driver.**

## Compute & display

| Part | Notes | ~$ |
|---|---|---|
| **Raspberry Pi 4 Model B (2–4 GB)** | The build target. Ample for Pygame + ALSA EQ + FFT, has a 3.5 mm jack, uses the 15-pin DSI connector, and is easier on the battery than a Pi 5. | 45 |
| microSD 32 GB (A1) | OS + app | 8 |
| RP2040 (Raspberry Pi Pico) | Real-time controls + motor PID. Cheap, 26 GPIO, PIO, 3 ADC. | 4 |
| 4″ IPS capacitive touchscreen, 480×800, MIPI-DSI | The center "playlist/album" color LCD. Portrait native. Use a Pi-4 (15-pin DSI) compatible panel. | 40 |
| I2S DAC (PCM5102 / HiFiBerry DAC2) | Recommended for clean audio. The Pi 4's own 3.5 mm jack works as a fallback (lower quality). | 20 |

## The motorized faders (the expensive part)

Full build = **10 motorized faders**: 7 EQ + 1 preamp + 1 volume + 1 seek.

| Part | Qty | Notes | ~$ ea | ~$ |
|---|---|---|---|---|
| ALPS RSA0N11M9 **60 mm motorized** fader | 10 | 100 mm won't fit a 5″ body — use 60 mm. Each has a motor + a wiper pot for position feedback + a touch-sense pin. | 18 | 180 |
| DRV8833 dual H-bridge motor driver | 5 | One drives two fader motors. | 2 | 10 |
| CD74HC4067 16-ch analog mux | 2 | The Pico has only 3 ADC channels; mux the 10 fader wipers + pots through one ADC. | 1.5 | 3 |

**Why 7-band EQ, not 10:** ten 60 mm faders side-by-side need ~150 mm of width;
the body is ~127 mm. Seven EQ + preamp (8 in the EQ bank) fit across the top;
volume + seek mount horizontally on the bottom strip. See [wiring.md](wiring.md).

**Want to cut cost/scope?** Make only **volume + seek** motorized (2 faders) and
use plain (non-motorized) slide pots for EQ. Saves ~$140 and most of the motor
drivers/PID work. The firmware already separates "motorized" from "read-only"
faders, so this is a config change, not a rewrite.

## Buttons, knobs, encoders

| Part | Qty | Notes | ~$ |
|---|---|---|---|
| Momentary tactile buttons (12 mm) | 9 | prev/play/pause/stop/next/eject/shuffle/repeat/eq | 5 |
| Rotary encoder w/ push (EC11) | 2 | playlist scroll + select; menu | 4 |
| Potentiometer (balance / aux) | 1 | optional | 1 |
| Addressable LED (WS2812) strip/segment | 1 | VU / status glow | 3 |

## Power (handheld) — see [power.md](power.md) for the full design

| Part | Notes | ~$ |
|---|---|---|
| UPS/BMS HAT for Pi (Geekworm X728 or Waveshare UPS HAT B) | 5 V/5 A out, 18650 holders, I2C battery monitoring + safe shutdown. | 30 |
| 18650 Li-ion cells ×4 (3500 mAh, e.g. Samsung 35E) | ~50 Wh ≈ 6 h runtime. Use 2 for ~3 h, 6 for ~9 h. | 40 |
| Bulk caps (1000–2200 µF) + fuse + power switch | Absorb motor-slew spikes at the driver rail. | 5 |

## Body & misc

| Part | Notes | ~$ |
|---|---|---|
| 3D-printed enclosure (book form, ~200×127×25 mm) | PETG/ABS. See [wiring.md](wiring.md) for layout. | 15 |
| Fader knob caps, standoffs, JST wiring, protoboard/PCB | | 20 |

## Rough total

| Group | ~$ |
|---|---|
| Compute & display | 117 |
| Motorized faders + drivers + mux | 193 |
| Buttons/knobs/LEDs | 13 |
| Power (UPS + 4×18650, see [power.md](power.md)) | 75 |
| Body & misc | 35 |
| **Total (full motorized build)** | **≈ 430–480** |
| *Reduced (only volume+seek motorized)* | *≈ 300–330* |

## Sourcing notes

- Motorized faders: Mouser/Digikey for genuine ALPS; budget clones exist on
  AliExpress but wiper quality/backlash varies — buy one and test before ten.
- Confirm the fader's touch-sense wiring; some variants need a capacitive
  touch IC, others expose a conductive-knob pin.
- DSI panel + Pi 4: verify the cable/connector and the panel's `config.txt`
  overlay before committing to the enclosure cutout.
