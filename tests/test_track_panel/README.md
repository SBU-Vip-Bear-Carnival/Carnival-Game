# test_track_panel — one track, five buttons, an LCD and a strip

Shared in the team Discord on 2026-09-08 as `trackAndButtonAndLCD.ino`, and
committed here **verbatim** — only the file and folder were renamed to match the
`tests/` convention. Nothing in the sketch has been edited, including the two
problems described below. It is a record of what was actually run on a bench,
which is worth more than a tidied version of it.

Its stripped companion is [`../test_track_buttons`](../test_track_buttons) — the
same track and buttons with no display and no libraries, from the same Discord
drop. Reach for that one first when something is wrong; it isolates the track
from the panel, and unlike this sketch it responds to a button immediately.

It is the first thing we have that drives the **track and the V2 UI panel
together**: five buttons pick forward / stop / reverse and step a speed level
1–10, the LCD shows the mode and a ten-box speed bar, and a WS2812B strip runs a
rainbow.

## Running it

```bash
arduino-cli compile --profile mega tests/test_track_panel
```

## ⚠ This is bench wiring, not the cabinet

The pins in this sketch are a breadboard layout on low pin numbers. **Nine of
them collide with `pins.h`.** Do not flash this to the cabinet expecting the
cabinet's behaviour, and do not copy these numbers into `pins.h`.

| Pin | Here | `pins.h` on `main` |
|---|---|---|
| 2 | LCD `RS` | `DIR_PIN1` |
| 3 | `STEP` | `STEP_PIN1` — the one that agrees |
| 4 | `DIR` | free |
| 5 | LCD `E` | free |
| 6 | LCD `D4` | `DATA_PIN` — WS2812B data |
| 7 | LCD `D5` | `ENBL_PIN1` |
| 8 | forward button | `DIR_PIN2` |
| 9 | stop button | `STEP_PIN2` |
| 10–12 | slower / faster / reverse | free |
| 13 | NeoPixel data | `ENBL_PIN2` — and the Mega's built-in LED |
| A1 | LCD `D6` | `PRES2` — pressure plate 2 |
| A2 | LCD `D7` | free |

The cabinet's answer to the same hardware is already decided and sitting in
PR #2 (`hw/ui-panel-pins`): **LCD on 30–35, buttons on 40–44**, chosen to avoid
every pin above. See `docs/decisions/0002-ui-panel-wiring.md`. When this sketch
is ported into the firmware, those are the numbers to use.

## ⚠ `rainbowCycle()` blocks for about 13 seconds

`rainbowCycle(10)` is the first line of `loop()`, and it runs to completion
before anything else happens: 1280 iterations × `delay(10)` ≈ **12.8 s of
`delay()`**, closer to 15 s once the strip writes are counted.

Nothing else in `loop()` runs during that time. Two consequences on the bench,
both of which look like broken hardware:

- **Buttons are sampled once every ~13 s.** The edge detection compares against
  `lastForwardState`, so a press has to be *held* across a sample to be seen at
  all. Tapping a button does nothing.
- **The motor cannot step while the rainbow runs.** The stepper block is at the
  bottom of `loop()`, so a "running" motor moves in bursts ~13 s apart.

The fix is the standard one — drive the strip from a `millis()` state machine
advancing one frame per pass instead of looping inside `loop()` — but that is a
rewrite of the animation, so it is left alone here and noted instead.

## The TMC2209s are step/dir only

There is no `EN` and no `PDN_UART` in this sketch — it toggles `STEP` and `DIR`
and nothing else, so the drivers run at whatever current their Vref trimpot is
set to. That matches the third fault found in the team's wiring table: without
`PDN_UART` there is no UART channel, so `rms_current()` and `microsteps()` have
nothing to write to. Not a defect in this sketch; just don't read it as evidence
that UART control works.

## Where this should end up

`firmware/carnival/src/hardware/track.h` and `button.h` already exist on PR #1,
and `lightstrip.h` drives WS2812B with **FastLED**, not Adafruit NeoPixel. So the
port is: keep the panel/LCD behaviour, move it onto the panel pins, and drop this
sketch's strip code in favour of the FastLED one rather than adding a second LED
library to the firmware build.
