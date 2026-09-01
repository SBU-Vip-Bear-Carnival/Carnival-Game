# 0001 — TPU pressure plates instead of PLA

**Date:** Fall 2026
**Status:** accepted, pending material approval

## Context

V1's pressure plates were 3D printed in PLA. In use they were **too thick and too
stiff to step on** — which for a game whose players are children with cerebral
palsy is not a rough edge, it is the product failing at its one job.

A printed button plate was also tried and abandoned; a moulded rubber
TV-remote-style pad worked better than anything printed.

## Decision

Print V2 plates in **TPU**. Flexible filament gives travel and a lower actuation
force at the same geometry.

## Consequences

- **`PRESSURE_THRESHOLD` in `tuning.h` must be re-measured.** TPU and PLA do not
  read the same on the analog pin. Carrying the V1 number over would silently
  reproduce the V1 problem.
- Blocked on a TPU material request (asked 2026-08-31). **Do not slice anything
  for TPU until that is approved.**
- TPU needs a direct-drive extruder; not every printer available will do it.

## Rejected

- **Thinner PLA** — reduces stiffness but cracks under a stepped load.
- **Keep PLA, lower the threshold in firmware** — treats a mechanical problem as
  a software one. The plate would still be stiff; the sensor would just be
  twitchier.
