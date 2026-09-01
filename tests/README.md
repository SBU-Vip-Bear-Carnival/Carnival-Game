# Bring-up sketches

One sketch per component, each proving a single piece of hardware works before
it goes anywhere near the game loop. When something breaks on the cabinet, these
are how you find out whether it is the wiring or the logic.

Each test is its own sketch folder — the folder name must match the `.ino`:

```
tests/test_pressure_plate/test_pressure_plate.ino
```

**Give each one its own `sketch.yaml`** (copy `firmware/carnival/sketch.yaml`
and trim it to the libraries that test needs). CI compiles every test that has
one and skips those that do not, so a test without a pinned profile is a test
nobody is checking.

Worth having: pressure plate, limit switch, single stepper, LED strip, DFPlayer,
LCD, button panel.
