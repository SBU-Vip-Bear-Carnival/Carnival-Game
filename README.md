# Carnival Game

Firmware and hardware for an accessible carnival game built by Stony Brook's
**VIP BEAR** team for **United Cerebral Palsy of Long Island**.

A player presses a pressure plate to drive their track forward; first to the end
wins. It is built to be playable by children with limited strength and motor
control, which is why the plate threshold and the Mode 3 drift rate are treated
as accessibility settings rather than difficulty settings.

Arduino Mega 2560 — stepper-driven tracks, pressure-plate input, LED strip and
sound feedback, four game modes.

## Quick start

```bash
git clone https://github.com/<ORG>/Carnival-Game.git
cd Carnival-Game
./tools/setup.sh
arduino-cli compile --profile mega firmware/carnival
```

If that compiles, you have a working setup. You do not need the Arduino IDE.

**Before you write any code, read [`docs/GIT-WORKFLOW.md`](docs/GIT-WORKFLOW.md).**
`main` is protected — all work happens on a branch and merges through a pull
request.

## Game modes

| Mode | Behaviour |
|---|---|
| 0 — Standby | Idle light pattern, motors parked |
| 1 — Single, easy | Each plate release advances the track one subdivision |
| 2 — Two player | Both tracks race |
| 3 — Single, hard | As mode 1, but the track drifts backward between presses |

Mode 3's drift rate is the accessibility knob — see `src/config/tuning.h`.

## Layout

```
firmware/carnival/     the sketch
  sketch.yaml          pinned board core + library versions
  src/config/          pins, tuning, types
  src/hardware/        one header per device
  src/game/            modes and menu
hardware/              CAD, wiring diagrams, BOM
tools/                 host-side scripts
tests/                 single-component bring-up sketches
docs/                  workflow, architecture, decisions
```

## Toolchain

Board core and every library are pinned in `firmware/carnival/sketch.yaml`, so
everyone and CI build the same thing. Adding a library means adding it there
with a version — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

Currently: `arduino:avr 1.8.8`, TMCStepper 0.7.3, AccelStepper 1.64.0,
FastLED 3.10.5, DFRobotDFPlayerMini 1.0.6.

## Status

V1 was delivered to UCP in March 2026. This repo is **V2**, started Fall 2026:
new TPU pressure plates, a 5-button and LCD control panel, and firmware rebuilt
on a structure that more than one person can work in at once.

## History

V1 lived at `ssylviawolf-0/CARNIVALGAME-SOFTWARE` on a team member's personal
account. It is retired — kept read-only for reference, not developed further.
This repo does not carry its history.
