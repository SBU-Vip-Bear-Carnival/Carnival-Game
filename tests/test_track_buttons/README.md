# test_track_buttons — one track, five buttons, no display

The stripped companion to [`../test_track_panel`](../test_track_panel): the same
five buttons driving the same single TMC2209, with **no LCD, no LED strip and no
libraries** — `digitalWrite` and `micros()`, reporting over Serial at 9600.

Both came out of the team Discord in the same drop on 2026-09-08, this one
posted about half a minute earlier, and both are committed **verbatim**. Only
the file and folder were renamed to match the `tests/` convention.

## Why keep both

This is the sketch to reach for first. It is the smallest thing that proves the
driver, the wiring and the buttons work, so when the panel version misbehaves it
tells you which half is at fault — track or panel. That is the whole reason
`tests/` exists.

It is also **the one that actually responds to a button press.** `test_track_panel`
blocks inside `rainbowCycle()` for ~13 s per pass, so it samples input once a
cycle; this one has a real `loop()` and reacts immediately.

```bash
arduino-cli compile --profile mega tests/test_track_buttons
```

## ⚠ It reverses direction without stopping the motor

The reverse button flips `DIR` while `motorRunning` is still true:

```c
digitalWrite(DIR_PIN, LOW);
motorRunning = true;
```

There is no deceleration and no pause — at speed, a stepper carrying a moving
track will skip steps or stall outright, and it loses position silently, which
matters because the game counts subdivisions along the track.

**`test_track_panel` already fixes this** and is worth copying from: it sets
`motorRunning = false`, waits 50 ms, changes `DIR`, waits 10 ms, then restarts.
Whichever sketch gets ported into `track.h`, take the reversal from that one.
Better still, `AccelStepper` is already pinned in the firmware and ramps for you.

## ⚠ Two speed models, and they disagree

| | here | `test_track_panel` |
|---|---|---|
| what the buttons change | `stepDelay` directly | a `speedLevel` 1–10 |
| step | 200 µs, linear | `map(level, 1, 10, 5000, 500)` |
| fastest | **300 µs** | 500 µs |
| slowest | 5000 µs | 5000 µs |

Only one can survive the port. The 1–10 level is the better fit for the panel,
since it is what the LCD speed bar renders and what a player can be told. But
note this sketch goes **200 µs faster at the top end** than the level model can
express — if 300 µs is a speed the track actually needs, the map has to change,
not just the display. Nobody has said which is right; it wants a bench answer.

## Pins

Bench layout, not the cabinet. Only two collide with `pins.h` on `main`, both
with **track 2**:

| Pin | Here | `pins.h` |
|---|---|---|
| 3 | `STEP` | `STEP_PIN1` — agrees |
| 4 | `DIR` | free (`DIR_PIN1` is 2) |
| 8 | GO / forward | `DIR_PIN2` |
| 9 | stop | `STEP_PIN2` |
| 10–12 | slower / faster / reverse | free |

As with the panel sketch, there is no `EN` and no `PDN_UART` — step/dir only, so
the driver runs at whatever its Vref trimpot is set to.
