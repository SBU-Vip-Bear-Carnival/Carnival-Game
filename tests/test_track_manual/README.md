# test_track_manual — drive one track by hand (Mega)

Five buttons drive the stepper: FORWARD 8, STOP 9, SLOWER 10, FASTER 11,
REVERSE 12 (pin → button → GND). TMC2209 STEP 3 / DIR 4. The 16x2 LCD
(RS 2, E 5, D4–D7 on 6, 7, A1, A2) shows mode and a 1–10 speed bar, and the
74-LED WS2812B strip on pin 13 runs a rainbow. Mode changes and speed also print to
Serial at 9600.

```bash
arduino-cli compile --profile mega tests/test_track_manual
```

These pins are this bench rig's, not the cabinet's `pins.h`.

⚠ `loop()` calls `rainbowCycle(10)` first, which blocks for ~13 s
(1280 frames × 10 ms) before the buttons are read or the motor steps. Make
the rainbow non-blocking before trusting the button or speed behaviour.
