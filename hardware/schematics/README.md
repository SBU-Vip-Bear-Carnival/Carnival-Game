# Carnival Game schematics (GIGA R1 WiFi, two tracks)

Two versions of the same wiring:

| Folder | What it is |
|---|---|
| `full/` | **One A1 wiring diagram.** Every part drawn like the real hardware (the GIGA board with **every header pin** from Arduino's ABX00063 full pinout, TMC2209 StepSticks, NEMA17s, lever microswitches, 16x2 LCD module, MP3-TF-16P, WS2812B strip, buck, PSU) and **every connection drawn as a real wire**; ground is the ground symbol at each pin. A dot is a joint; lines that cross without a dot do not touch. Every used GIGA pin has its signal name on its lead, and signal groups are colour-coded. |
| `simplified/` | One page, only the pins in use. Same connections as `full/`. |

Open `full/carnival_full.kicad_pro` or `simplified/carnival_simple.kicad_pro` in KiCad 10. PDFs sit next to them.

**Wire colours:** motor coil A = black (A1) + green (A2), coil B = red (B1) + blue (B2), from the team's wiring table. +12V orange, +5V red, +3V3 purple. Buttons teal, LCD brown, limit switches pink, STEP/DIR gold, MP3 serial navy, LED data cyan.

**Limit microswitches:** pins in order C, NC, NO. The middle pin (NC) is unused; C goes to ground, NO to the GIGA.

**Pins not yet confirmed on hardware:** Track 1 limits 25/23 (guessed), Track 2 STEP 49 / DIR 47 / limits 29/27, LCD 22-32 (even), MP3 on Serial1 D0/D1. Confirmed on the bench 2026-09-30: buttons 35-43, Track 1 STEP 53 / DIR 51.

## generator/

`python3 gen5.py <outdir>/full` rebuilds the wiring diagram: it places the parts, then routes every net pin to pin on a 2.54 mm grid (`wiring.py`), so wires of different nets never share a segment and only cross at right angles. `expected_full.json` is the intended connection list; check a build with

```bash
kicad-cli sch export netlist --format kicadxml -o full.xml full/carnival_full.kicad_sch
python3 generator/checkflat.py full.xml generator/expected_full.json   # every net exact, no shorts
```

(The previous 11-page hierarchical version is in git history, commit 2c3b86f.)

The schematics are generated. `python3 gen4.py <outdir>` rebuilds both versions. `checknets.py` compares an exported netlist against the intended connection list:

```bash
kicad-cli sch export netlist --format kicadxml -o full.xml full/carnival_full.kicad_sch
python3 generator/checknets.py full.xml full    # needs num.json, which gen4.py's GIGA section produces
```

If you edit a schematic by hand in KiCad, the generator will overwrite that edit. Pick one or the other.
