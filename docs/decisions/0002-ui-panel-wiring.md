# 0002 — UI panel pins, and three problems in the wiring table

**Date:** 2026-09-02
**Status:** proposed — three items need a decision at the next electronics meeting

## Context

The team circulated a wiring table covering the TMC2209 drivers, the five UI
buttons and the LCD. It settles two things that were blocking:

- The display is a **parallel HD44780 16-pin module in 4-bit mode**, not I²C.
- There are **five buttons on digital pins with a common ground**, so
  `INPUT_PULLUP` and no external resistors.

The table gives the *module* pinout but says only "digital pin" on the Arduino
side, so the actual assignment is still open. This ADR proposes it, and records
three problems in the table that will cost an afternoon each if they reach the
bench unexamined.

## ⚠ Problem 1 — `EN` tied to GND contradicts the firmware

The table wires the TMC2209's `EN` to **GND**. That hardwires both drivers
permanently enabled.

`pins.h` says otherwise: `ENBL_PIN1 = 7`, `ENBL_PIN2 = 13`, and `MyTrack` drives
them constantly — `digitalWrite(enPin, LOW)` before a move, `HIGH` when the move
finishes, plus `updateDriverState()` which releases the driver whenever the
stepper is idle.

If `EN` goes to GND instead:

- Both motors stay **energised at all times**, drawing holding current through
  every idle minute of a showcase and running hot with no thermal relief.
- Every `digitalWrite(enPin, …)` in `MyTrack` becomes a no-op, so the code reads
  as if it manages the drivers when it does not.

**Recommendation: keep `EN` on a digital pin.** It costs one wire per driver and
it is already what the firmware and `pins.h` assume. Tying it to GND is a change
to the software, not just to the harness.

## ⚠ Problem 2 — there is no UART pin, so the TMC settings are dead

The table lists `EN`, `STEP`, `DIR`, `VM`, `VIO`, `GND` — and no `PDN_UART`.

Without that wire, the TMC2209 cannot be configured in software. `MyTrack::begin()`
calls `driver.begin()`, `driver.rms_current(600)`, `driver.microsteps(2)` and
`en_spreadCycle(0)`, and **every one of those writes goes nowhere.** Nothing
errors; the settings simply never arrive. Current is then whatever the Vref
trimpot on the board is set to, and microstepping is whatever MS1/MS2 are
strapped to.

This confirms the warning already in `tuning.h` and **reverses what the V2 plan
said** — porting `track.h` from V1 does *not* deliver working TMC control,
because the control channel was never wired.

Two honest options:

| | cost | result |
|---|---|---|
| **Wire `PDN_UART`** | one wire + one 1 kΩ resistor per driver, one spare serial port | current, microstepping and StealthChop set in code and under version control |
| **Delete the UART code** | none | settings live on a trimpot nobody wrote down — which is how V1's motors ended up at an unknown current |

**Recommendation: wire it.** A current limit that exists only as a screw position
is not a setting, it is a rumour. If it is not wired, the TMC calls must be
deleted rather than left in place looking authoritative.

## ⚠ Problem 3 — the LCD is missing a data line

The table lists LCD module pins 12, 13 and 14 going to digital pins, and leaves
**11 blank**.

4-bit mode needs **D4, D5, D6, D7 = module pins 11, 12, 13, 14**. Three data
lines will not drive an HD44780; the display will stay blank or print garbage,
and it will look like a firmware fault.

Module pins 7–10 (D0–D3) being unused is correct — that is what 4-bit mode means.

## Also worth fixing

- **Contrast on a fixed 12 kΩ resistor.** The table's own comment says
  *"technically supposed to be pot."* It is right. A fixed divider usually lands
  outside the readable window and the screen shows either nothing or solid
  blocks — and the first instinct is always to blame the code. A 10 kΩ trim pot
  is about a dollar and it is a one-time adjustment.
- **Backlight at 320 Ω** is safe but dim, roughly 10 mA. 150–220 Ω is the usual
  range if it needs to be readable under the lights at a showcase.
- **`RW` (module pin 5) to GND is correct** — write-only, which is what
  `LiquidCrystal` expects.

## Decision — the pin assignment

Chosen to avoid every pin already in `pins.h`, plus pin 13 (built-in LED), 0/1
(USB serial) and 14–19 (hardware serial ports). Contiguous blocks so the ribbon
cable follows the header order.

| Function | Arduino pin | Goes to |
|---|---|---|
| LCD `RS` | 30 | module pin 4 |
| LCD `E` | 31 | module pin 6 |
| LCD `D4` | 32 | module pin 11 |
| LCD `D5` | 33 | module pin 12 |
| LCD `D6` | 34 | module pin 13 |
| LCD `D7` | 35 | module pin 14 |
| Button 1 — up | 40 | button, other leg to GND |
| Button 2 — down | 41 | " |
| Button 3 — select | 42 | " |
| Button 4 — back | 43 | " |
| Button 5 — start | 44 | " |

Six pins for the display and five for the buttons. The Mega has the room —
this brings the total to 28 of 54 digital pins.

⚠ **Do not wire an LCD data line to Arduino pin 13.** The module's own pin 13 is
D6; the Arduino's pin 13 is the built-in LED and is already `ENBL_PIN2`. The two
numbering schemes collide in conversation, and that is exactly the kind of thing
that gets miswired once and debugged for an hour.

## Consequences

- Added to `pins.h` behind `#ifndef` guards, like the pins already there, so a
  bench override still works.
- `LiquidCrystal` must be added to `sketch.yaml` with a pinned version before any
  menu code lands, or CI will not have it.
- The five buttons keep the existing `MyButton` class unchanged — it is already
  `INPUT_PULLUP` with tap and hold detection.
- The old single start button on pin 48 stays wired during the transition. Button
  5 duplicates it deliberately; remove 48 only once the panel is trusted.
