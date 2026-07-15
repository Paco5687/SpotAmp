# Wiring & physical layout

## Front-panel layout (portrait, ≈127 mm wide × 200 mm tall)

Mirrors the Pygame mock's regions so the software and the hardware agree:

```
┌───────────────────────────────────────────┐  ← ~127 mm wide
│  WINAMP · PHYSICAL EDITION       (title)   │
├───────────────────────────────────────────┤
│  0:42        [ LCD readout ]     320 kbps  │   PHYSICAL panel
│  ░░▓▓█�e▓░  spectrum (on LCD strip)  44 kHz │   (buttons + small OLED/LCD
│  |◀  ▶  ▮▮  ■  ▶|  ⏏   (transport buttons) │    readout + tactile buttons)
├───────────────────────────────────────────┤
│                                           │
│   ┌────────┐   1. M83 - Midnight City     │   SCREEN
│   │ album  │   2. Daft Punk - Digital...  │   4″ IPS capacitive
│   │  art   │   3. Massive Attack - Tear.. │   touchscreen
│   └────────┘   4. ...                     │   (playlist + art)
│                                           │
├───────────────────────────────────────────┤
│  EQ:  ▮ ▮ ▮ ▮ ▮ ▮ ▮   ▮(pre)              │   PHYSICAL panel
│      60 150 400 1k 2k4 6k 15k              │   8 motorized 60 mm faders
├───────────────────────────────────────────┤
│  [====VOL====]      [====SEEK====]         │   2 motorized faders (horizontal)
└───────────────────────────────────────────┘
```

## Pico (RP2040) pin plan

> Indicative — adjust to your board revision. The Pico has **3 ADC** channels
> (GP26–28), so all analog fader/pot wipers go through the 16-ch mux.

| Function | Pico pins |
|---|---|
| Mux (CD74HC4067) select | GP2, GP3, GP4, GP5 (S0–S3) |
| Mux common out → ADC | GP26 (ADC0) |
| Second mux (if needed) common | GP27 (ADC1) |
| Motor drivers (DRV8833) IN pins | 2 PWM pins per fader → GP6..GP21 as needed |
| Fader touch-sense lines | digital GPIO (or a touch IC on I²C) |
| Buttons | matrix or direct GPIO (debounced in firmware) |
| Encoders (EC11) | 2 GPIO each + push |
| WS2812 LEDs | 1 GPIO (PIO-driven) |
| USB | to Pi (CDC serial + power) |

Each motorized fader needs **three** connections handled together:
1. **Motor** → an H-bridge channel (2 PWM lines) for drive direction/speed.
2. **Wiper** → a mux input → ADC, for the PID's position feedback.
3. **Touch** → a digital/touch line, so the Pi knows to stop driving it.

## Control loop (firmware)

Per motorized fader, ~1 kHz:

```
error = target - read_position(fader)
if touched(fader):        # user wins
    motor_off(fader); report EV FADER when it settles
else:
    drive = PID(error)    # tune Kp/Ki/Kd per fader
    motor_pwm(fader, clamp(drive))
```

See `firmware/src/main.cpp` for the skeleton.

## Power & audio

- LiPo → power board (5 V boost) → Pi 4; motors get their own regulated rail off
  the same pack (H-bridges draw spikes — decouple well, keep motor ground and
  logic ground joined at one star point).
- I2S DAC on the Pi's I2S pins (or a HAT) → 3.5 mm headphone jack; optional
  PAM8302 + small speaker for a built-in speaker.

## Enclosure

- Book form, ~200 × 127 × 25 mm. Faders and their travel set the depth — 60 mm
  faders + motor bodies are the tallest components; plan ~20 mm behind the panel.
- Print the front panel with slots for fader travel and cutouts for the LCD,
  buttons, and encoders. A kickstand echoes the Yanko concept's EQ-base stand.
- CAD lives here later (`hardware/cad/`), source + STL.
