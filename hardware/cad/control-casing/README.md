# control-casing — the UI panel enclosure, as received

Five STLs dropped in the team Discord on **2026-09-21** by **Jerry Wu**, who drew
them, committed here **verbatim**: the bytes and the filenames are exactly as
shared, nothing was re-exported, renamed or repaired. Same policy as the two bench sketches in
[`tests/`](../../../tests) — these are a record of what someone actually drew,
and a tidied version of that is worth less.

⚠ **This deliberately breaks the naming rule in [`../README.md`](../README.md)**
("name by what the part is, not by version"). That rule is for source CAD we
maintain; `casing body` vs `case_body` is how the files arrived, and renaming
them would destroy the only evidence of what supersedes what. Apply the rule to
the `.f3d`/`.step` when it lands — see *What is missing* below.

> [!important] The next drop is versioned: `v<main>.<major>.<minor>`
> Agreed in Discord on 2026-09-21 — main version, major change, minor change.
> Jerry already numbers internally (the assembly is `ControlCasing**2**`, and the
> next revision is **v2.4**); it just never reached the filenames. So
> `control-casing-v2.4-body.stl`, not `case_body.stl`.
>
> **Both rules are right, for different files.** `../README.md`'s "git holds the
> versions" is correct for source CAD the team maintains **in this repo**. It is
> wrong for STL exports arriving from one person's private CAD, where git holds
> only what we were sent and the filename is the only ordering information that
> travels with it. These are the second kind.

## They are one part, in one coordinate frame

Not five parts. Every file shares the same world origin and the same
**230.0 × 100.0 mm** outline, and each sits at its assembled height rather than
dropped to Z=0 — so they can be loaded together and they land in position.

| File | Dropped | Z range | Thickness | What it is |
|---|---|---|---|---|
| `ControlCasing2-Stem.stl` | 16:17 | 0 → 30 | — | **the whole assembly** as one closed mesh |
| `casing lid.stl` | 16:23 | 25 → 30 | 5.0 | face plate, rev A |
| `casing body.stl` | 16:24 | 0 → 23 | 5.0 wall | tray, rev A |
| `case_lid.stl` | 16:59 | 28 → 30 | 2.0 | face plate, rev B |
| `case_body.stl` | 16:59 | 0 → 28 | 2.0 wall | frame, rev B |

**Rev B is the newest** (16:59) and is the one to print if you print anything.
The revision went **5 mm walls → 2 mm** and the body from a closed tray to an
open frame, keeping the 30 mm overall height.

> [!note] Rev A does not close
> `casing body` tops out at Z=23 and `casing lid` starts at Z=25 — a **2 mm gap**
> with nothing in it. Either a lip is missing from the tray or the lid was moved
> and not re-mated. Rev B has no gap (28 → 28), so this looks like the bug rev B
> was drawn to fix. Left as-is; it is part of the record.

## Measured features

Taken off the mesh, not off a drawing. All ±0.1 mm, from cross-sections at
Z = 29.0 (lid) and Z = 1.0 / 14.0 (body).

- **Rectangular window — 80.2 × 36.4 mm**, in the left half of the face.
- **Square aperture — 30.2 × 30.2 mm**, to its right.
- **4 × ⌀15.0 mm through-holes**, centres inset **15.0 mm from both edges** at
  each corner, counterbored on the body.
- **Body opening — 170.0 mm** wide between the end flanges, which are 30 mm
  wide and carry the corner holes.

## ✅ The window confirms the display, independently

**80.2 × 36.4 mm is a 16×2 HD44780 module PCB (80 × 36 mm) with 0.2 mm
clearance.** Nobody had to say so — the geometry only fits that part.

That is a third independent confirmation of the display decided in ADR 0002
(`docs/decisions/0002-ui-panel-wiring.md`, which is **on PR #2 / `hw/ui-panel-pins`,
not yet on `main`** — hence no link from this branch): the team's wiring table
said parallel HD44780, the `test_track_panel` bench sketch ran one, and now the
enclosure is cut for one. **The 16×2-vs-20×4 and
I²C-vs-parallel question is closed.** A 20×4 is 98 × 60 mm and does not fit this
opening.

> [!warning] It is cut for the **PCB**, not the bezel
> 80 × 36 is the whole board, including the mounting ears and the header. The
> visible glass is about 64.5 × 16 mm and sits roughly centred. So this window
> shows the board, not just the screen, unless something covers the margin. Worth
> a look before it is printed — it may be intended, but a 0.2 mm clearance hole
> for a whole PCB also has nowhere to screw down.

## ❌❌ Rev B has no floor — and rev A did

**This is a regression, not a gap.** Cross-sections taken just above the base:

| File | At z = 1 mm | Verdict |
|---|---|---|
| `casing body` (rev A) | solid across the full width | **5 mm floor**, z 0→5 |
| `case_body` (rev B) | open through the middle | **no floor at all** |

Rev B — the newest, the one anyone would print — **deleted the base rev A had.**
It is an open frame, through from front to back.

⚠ **The panel mounts vertically**, so "down" for anything inside is toward the
open back, not toward a floor. Raised in Discord on 2026-09-21 (*"you put the
arduino in, there is nothing supporting it behind"*) and confirmed here against
the meshes. As it stands the contents are held in by the lid and by friction.

### Depth pulls the other way

| Revision | Clear internal depth | Floor? |
|---|---|---|
| Rev A | **~18 mm** (floor top z=5 → body top z=23) | ✅ |
| Rev B | **28 mm** (no floor → lid underside z=28) | ❌ |

Also asked in the same exchange — *"are you sure the box is deep enough for all
the headers and stuff"* — and the two revisions answer in opposite directions.
**Rev A is the one that is probably too shallow; rev B is the one deep enough.**
So the fix is **rev A's floor at rev B's depth**, not a choice between them.

⚠ **Nobody has measured the actual board.** For scale only: a Mega 2560 is ~1.6 mm
of PCB with ~3 mm of solder-side lead, a stacked female header stands ~8.5 mm
proud, and dupont housings on that header add roughly another 14–15 mm — call it
~20 mm before bend radius on the wire leaving the connector. **Those are
catalogue figures, not measurements of our hardware.** Put a caliper on the real
board with its jumpers fitted before cutting v2.4; it is the number this turns on.

## ❌ There are no button holes. Not one.

The face has the LCD window, the 30.2 mm square, and the four corner holes. That
is every opening in every one of the five files — checked on the meshes, not by
eye.

**The panel task on the team's list asks for a printed face carrying 5 buttons
and an LCD cut-out.** This is the LCD half only. Three readings, and the
repo cannot tell them apart:

1. **Unfinished** — the buttons are the next revision.
2. **The 30.2 mm square is the button cluster**, expecting a separate module or
   keypad behind it. 30.2 mm is too small for five 12 mm tactile switches with
   any spacing, so this only works if the buttons are a sub-assembly.
3. **The buttons are not on this panel at all** and mount elsewhere on the
   cabinet.

⚠ **This blocks printing either way**, and it collides with the *other* open
panel question: PR #2's `pins.h` names the five buttons `BTN_UP / DOWN / SELECT /
BACK / START` (a menu) while the bench sketch drives them as forward / stop /
slower / faster / reverse (direct motor control). **The legends go on this face.**
Whichever reading is right, the button semantics have to be settled before this
part is printed, not after.

## What the 30.2 mm square is, is unknown

Nothing in the repo describes a 30 mm square part. Candidates nobody has
confirmed: a 30 × 30 fan, a panel-mount connector, a keypad module, or — given
the `-Stem` in the assembly filename — a **30 mm square tube the panel mounts
on**, which would suit a height-adjustable panel for a seated player. **This is
speculation from a filename**, and it did **not** come up in the 2026-09-21
review, which covered mounting, depth and naming only. Still open; asked on the PR.

## What is missing

- **No source CAD.** `../README.md` asks for the `.f3d`/`.step` beside the
  export, because an STL can only be replaced, not modified. Five STLs and no
  editable file means **only Jerry can revise this** — which is worth saying out
  loud now that a revision is due the week of Sept 28.
- **No material, no print settings**, and no note of which printer. Note that
  [ADR 0001](../../../docs/decisions/0001-tpu-pressure-plates.md) governs the plates, not
  this — but the TPU printer request is still unanswered, so do not assume a
  machine is available.
- **No fit check against real hardware.** The LCD window is 0.2 mm on a PCB
  dimension read off a datasheet, not off the module the team owns.
