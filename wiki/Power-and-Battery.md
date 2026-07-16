# Power and Battery

> **Placeholder** — full design + tradeoffs in the repo:
> **[hardware/power.md](https://github.com/Paco5687/SpotAmp/blob/main/hardware/power.md)**

TL;DR:
- ~**6.5 W average**, ~**20 W peak** (motor slews) → design the 5 V rail for **5 A**.
- Use a **Pi UPS/BMS HAT** (Geekworm X728 / Waveshare UPS HAT B) + **18650 cells**.
- **Runtime:** 2 cells ≈ 3 h · 4 cells ≈ 6 h · 6 cells ≈ 9 h.
- Keep total **under 100 Wh** if it needs to fly.
- Bulk caps at the motor-driver rail; I2C battery monitoring drives a safe
  shutdown + an on-screen battery meter.

See the repo doc for the 18650-vs-LiPo form-factor tradeoff and charging notes.
