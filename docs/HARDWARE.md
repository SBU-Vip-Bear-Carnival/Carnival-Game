# Hardware

Arduino **Mega 2560**. The Mega is required, not incidental — the pin count and
the extra hardware serial ports (the DFPlayer uses `Serial1`) do not fit on a Uno.

## Pin map

This table mirrors `firmware/carnival/src/config/pins.h`. **If you move a wire,
change both** — a pin map that only exists in documentation is how someone
spends an afternoon debugging a fault that is not there.

| Function | Pin | Notes |
|---|---|---|
| Stepper 1 STEP | 3 | track 1 |
| Stepper 1 DIR | 2 | |
| Stepper 1 ENABLE | 7 | LOW = enabled (TMC2209) |
| Stepper 2 STEP | 9 | track 2 |
| Stepper 2 DIR | 8 | |
| Stepper 2 ENABLE | 13 | |
| Pressure plate 1 | A0 | analog |
| Pressure plate 2 | A1 | analog |
| Track 1 limit — start | 25 | `INPUT_PULLUP` |
| Track 1 limit — end | 23 | |
| Track 2 limit — start | 29 | |
| Track 2 limit — end | 27 | |
| Start button | 48 | `INPUT_PULLUP` |
| Start button LED | 53 | |
| Indicator LED 1 | 45 | |
| Indicator LED 2 | 37 | |
| WS2812B data | 6 | addressable strip, 40 LEDs |
| DFPlayer Mini | Serial1 (18/19) | TX/RX |

Not yet wired — the V2 5-button panel and LCD. Add them to `pins.h` behind
`#ifndef` guards when they exist.

## Drivers and motors

TMC2209 stepper drivers over UART. Configured in `tuning.h`:
sense resistor 0.11 Ω, 600 mA RMS per motor, 2 microsteps.

The 2-microstep setting is a deliberate trade — more microstepping is quieter
but loses torque, and the tracks need torque more than they need silence.

## Pressure plates — the accessibility part

The plates are the whole point of the project. A plate that needs adult body
weight excludes the children the game is for.

- Read as analog on A0/A1; a press is a reading below `PRESSURE_THRESHOLD`.
- Must be held for `PLATE_MIN_PRESS_MS` (250 ms) to count, which rejects
  brushes and stumbles.
- `PLATE_DEBOUNCE_MS` (50 ms) filters contact bounce.

**Re-measure `PRESSURE_THRESHOLD` whenever the plate material changes.** TPU and
PLA do not read the same, and the threshold is not transferable between them.

## V1 lessons — do not rediscover these

- **PLA plates failed.** Printed in PLA they were too thick and too stiff to
  step on. This is why V2 is TPU. See `docs/decisions/`.
- **The printed button plate was abandoned** for a moulded rubber TV-remote-style
  pad, which worked better than anything printed.

## Bench setup

Testing on your own board with different pins? Do not edit `pins.h`:

```bash
cd firmware/carnival/src/config
cp pins.local.example.h pins.local.h
```

Override only the pins that differ. The file is gitignored, CI never sees it,
and deleting it returns you to the cabinet's real wiring.
