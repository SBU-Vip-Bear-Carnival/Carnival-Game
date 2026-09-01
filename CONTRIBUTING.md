# Contributing

New to git? Read [`docs/GIT-WORKFLOW.md`](docs/GIT-WORKFLOW.md) first — it is
written for someone who has never used it, and it has a recovery section for
when things go wrong.

## The short version

1. Branch off `main` — `type/short-description`
2. Commit small, push, open a PR
3. CI must be green
4. One approval, squash merge, branch auto-deletes

`main` is protected. It always compiles. That is the one invariant this repo has.

## Where code goes

| Path | What belongs there |
|---|---|
| `firmware/carnival/src/config/` | pins, tuning constants, enums and structs |
| `firmware/carnival/src/hardware/` | one header per physical device |
| `firmware/carnival/src/game/` | game modes, menu — logic, not drivers |
| `hardware/` | CAD, wiring diagrams, BOM |
| `tools/` | host-side scripts that run on a laptop, not the Mega |
| `tests/` | bring-up sketches for one component at a time |
| `docs/decisions/` | why we chose something — see below |

The split between `config/`, `hardware/` and `game/` is deliberate. V1 had one
`config.h` holding pins, tuning and type definitions together, so every change
touched the same file and every change conflicted.

## The three config files

- **`pins.h`** — the cabinet's wiring. Editing it says the hardware changed.
- **`tuning.h`** — calibration. Committed on purpose: one machine, one set of
  numbers, and they need to be reviewable. When you change one, say in the PR
  what you measured.
- **`types.h`** — enums and structs. Should almost never change.

Working on your own breadboard? `cp pins.local.example.h pins.local.h` and
override there. It is gitignored, CI never sees it, and it cannot break the
cabinet for anyone else.

## Adding a library

Add it to `firmware/carnival/sketch.yaml` **with an exact version**, or CI will
not have it and your branch will not build:

```bash
arduino-cli lib search <name>     # find the version
```

Never rely on what happens to be installed in your Arduino IDE. That is the
problem this file exists to prevent.

## Before you open a PR

```bash
arduino-cli compile --profile mega firmware/carnival
```

If it does not compile locally it will not compile in CI, and CI is not a
build service — it is a backstop.

Say in the PR whether you tested on the real cabinet or only compiled. Both are
fine. Silently implying the first when you did the second is not.

## Commit messages

Present tense, say what changed and why it matters:

```
Raise the plate threshold to 450 — the TPU prototype reads lower than PLA
```

not

```
Update config
```

## Hardware changes

A wiring change is a code change. If you move a wire, update `pins.h` **and**
`hardware/wiring/` in the same PR, or the next person debugs a fault that is
only in the documentation.

## Decisions worth writing down

If you chose between two real options — a material, a sensor, a library — add a
short note in `docs/decisions/`. Say what you picked, what you rejected, and
why. The PLA-versus-TPU plate question cost a semester; it should not have to be
rediscovered.

## AI assistance

Not prohibited, but disclose it: add a trailer to the commit, e.g.
`Co-Authored-By: <tool>`. VIP has no written AI policy, so the safe default is
being able to say exactly what you wrote. If in doubt, ask Chan or McKenna
before leaning on it for something graded.
