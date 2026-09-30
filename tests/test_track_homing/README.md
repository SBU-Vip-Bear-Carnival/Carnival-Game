# test_track_homing — one track, five buttons, two limit switches (Giga R1)

Bench sketch for the **Arduino Giga R1** (not the Mega). No `sketch.yaml`
on purpose: CI builds `--profile mega` for every test folder that has one, and
this does not target the Mega.

```bash
arduino-cli compile --fqbn arduino:mbed_giga:giga tests/test_track_homing
arduino-cli upload  --fqbn arduino:mbed_giga:giga -p /dev/cu.usbmodem101 tests/test_track_homing
```

Startup: home to the home switch, measure the track by driving to the end
switch and counting steps, return to 0, then take buttons. Position is counted
per step; the ends stop by count, and the switches are the backup that re-syncs
the count if it drifts.

⚠ **Untested on hardware as of 2026-09-30.** `HOME_SWITCH` 25 / `END_SWITCH` 23
and `HOME_DIR` are guesses; the button-to-job layout is known to be wrong.

Wiring: STEP 53, DIR 51, TMC2209 `VIO` on the Giga's **3.3V** (3.3 V logic),
`EN` tied to GND. Buttons and switches: pin → switch → GND.
