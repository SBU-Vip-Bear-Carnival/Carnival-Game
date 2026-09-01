# Architecture

## The shape of it

```
carnival.ino          setup() and loop(); dispatches on the current mode
  src/config/         what the machine IS
    pins.h              wiring
    tuning.h            calibration
    types.h             enums, per-mode state structs
  src/hardware/       how to talk to each device -- one header per device
  src/game/           what the game DOES -- modes, menu
```

Arduino compiles everything under a sketch's `src/` recursively, so the nesting
is free.

## Why it is split this way

V1 had a single `config.h` holding pins, tuning constants and type definitions
together. Every change touched that one file, so every change conflicted, and two
people refactoring in parallel produced two half-versions of the project that were
never reconciled.

The split follows how often things change:

- `pins.h` — changes when a wire moves. Rare, and always paired with a hardware
  change.
- `tuning.h` — changes constantly during bring-up. Expect churn here.
- `types.h` — should almost never change.

Keeping them apart means a wiring fix and a calibration tweak do not land in the
same file and fight.

## Control flow

`loop()` dispatches on `currentMode`:

| Mode | Function |
|---|---|
| `MODE_STANDBY` | `runStandby()` |
| `MODE_SINGLE_EASY` | `runSingleEasy()` |
| `MODE_TWO_PLAYER` | `runTwoPlayer()` |
| `MODE_SINGLE_HARD` | `runSingleHard()` |

Each mode owns a state struct in `types.h` (`Mode1State`, `Mode2State`,
`Mode3State`) with a `reset()`. Modes are non-blocking — they check state and
return. **Nothing calls `delay()` in a game loop**; a blocked loop means a plate
press gets missed, which reads to a player as the game ignoring them.

## Mode 3 and accessibility

Mode 3 drifts the track backward between presses. The drift constants in
`tuning.h` are the difficulty knob for the entire game, and difficulty here is an
accessibility setting: `DRIFT_GRACE_PERIOD_MS` is how long a player gets after a
press before the track starts pulling back. A player who cannot press quickly is
excluded by a short grace period.

Change these with a real player in mind, not a fast one.

## What V2 adds

- TPU pressure plates (PLA failed — see `docs/decisions/`)
- A 5-button UI panel with an LCD, replacing the single start button
- Audio via DFPlayer Mini on `Serial1` — see `src/hardware/audio.h`
- Possibly a HUB75 RGB matrix; V1 had a working demo but it never merged

## Where V1's code went

This repo does not carry V1's history. The audio system here is ported from it
with a compile error fixed. If you need to look something up, the old repo is
`ssylviawolf-0/CARNIVALGAME-SOFTWARE`, retired and read-only.
