# CAD

Source CAD and exported meshes for printed parts.

- Keep the **editable source** (`.f3d`, `.step`) next to the export (`.stl`).
  An STL alone cannot be modified, only replaced.
- Name by what the part is, not by version: `pressure-plate.f3d`, not
  `plate_v3_final.f3d`. Git holds the versions.
- Note the material and any print settings that matter in the PR.

Current work: TPU pressure plates and the 5-button UI panel. See
`docs/decisions/0001-tpu-pressure-plates.md` before printing anything.
