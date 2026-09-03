# Hardware

Arduino **Mega 2560**. The Mega is required, not incidental — the pin count and
the extra hardware serial ports (the DFPlayer uses `Serial1`) do not fit on a Uno.

See [`hardware/wiring/SCHEMATIC.md`](../hardware/wiring/SCHEMATIC.md) for the same
information as a diagram.

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
| Stepper 2 ENABLE | 13 | ⚠ see below |
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

### ⚠ Pin 13 is a real defect, not a documentation error

`ENBL_PIN2` is on pin 13, which is the Mega's **built-in LED pin**. The
bootloader toggles it for roughly a second on every reset and every upload, and
the TMC2209's enable is active-LOW — so stepper driver 2 receives spurious
enable pulses at every power-up and every flash. The onboard LED and its series
resistor also load that line.

This is inherited from V1 and is documented here as the machine actually is.
**Moving it is a hardware change**, so it needs a rewire and a matching `pins.h`
edit in the same PR. Any free digital pin that is not 13 will do. Worth doing
before V2 ships; harmless to leave while bench testing.

### The V2 panel — assigned, not yet wired

Pins are now in `pins.h`: LCD `RS/E/D4-D7` on 30-35, buttons on 40-44. The
display is a **parallel HD44780 in 4-bit mode**, not I²C.

⚠ **Three problems in the team's wiring table need answering before anyone
solders** — `EN` tied to GND contradicts the firmware, there is no `PDN_UART`
line so every TMC setting is dead, and the LCD is missing a data line. All three
are written up in [`docs/decisions/0002-ui-panel-wiring.md`](decisions/0002-ui-panel-wiring.md).

## Drivers and motors

TMC2209 stepper drivers. `tuning.h` carries the intended settings — sense
resistor 0.11 Ω, 600 mA RMS per motor, 2 microsteps — and 2 microsteps is a
deliberate trade, since more microstepping is quieter but loses torque and the
tracks need torque more than silence.

⚠ **None of that is applied yet.** No `TMC2209Stepper` is ever constructed, so
those three constants have no readers and the drivers run at their hardware and
jumper defaults. Wiring up UART control is V2 work. Until it lands, do not
assume the motors are current-limited to 600 mA.

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
