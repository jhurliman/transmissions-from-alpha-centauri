# 225 · Open ground arcade thresholds

CPU candidate; visual acceptance remains pending the root's combined native render.

All 18 ground-level125 masonry platforms and18 underlying110 sill strips are hidden. Upper-level platforms and sills, columns, jambs, arch roofs and the whole-building structural foundation are preserved.

The220 tunnel floors previously matched the tops of those removed platforms. Only their lowest profile vertices are lowered about1.7781m to the actual foundation surface, avoiding a floating floor behind each removed wall. The crowns and all other vertices stay exact. Each route retains30m straight, then30m at45degrees downward, with its open outlet. Entry-to-foundation height error is zero at both native sides. This is continuity at the existing foundation elevation, not a new street-to-plinth access ramp.

V2 removes15 obsolete native contact-ink intervals. Each interval is continuously certified within2cm of a removed platform/sill face. The former intersection loses that owner even when its other owner, such as a tunnel wall, remains; the V1 nearest-surviving-surface test incorrectly retained these phantom contact lines. Unrelated jamb contours remain native geometry/Freestyle, and all unaffected Grease Pencil attributes stay exact. V1 is archived in held-v1.

Use `tools/arcade_sills_225.py::apply(scene)` after the combined scene's other scoped additions. `audit.json` records construction, floor matching and contact certification; `preservation-check.json` records independent save/reopen geometry comparison and tunnel pair intersections. No standalone render was made.
