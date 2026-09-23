# 123 crossing-free crown foundation

Reusable entry point: `tools/coliseum_crown_repair_123.py::apply_prepared(C)`.
Only replaces mesh data for:
- `COL110 U8 fractured upper wall L`
- `COL110 U8 fractured upper wall R`

Preserves current object transforms, properties, and material slots. It intentionally does not integrate the entire saved study scene. Current sill wall, drains, frames, tower cavities, cornices, colors, and other components remain owned by the current integration.

## Validation

Both final repaired meshes: zero numerical strict triangle crossings, zero nonmanifold edges, positive signed volume. L:50 vertices/35 faces; R:231 vertices/199 faces. Every accepted119 cutter replay has zero outside-cutter surface error. These checks are numerical evidence, not exact-arithmetic certification.

Main camera3840×2885 silhouette masks preserve coarse outline and aperture:98.943% IoU,102 changed pixels, median boundary distance0px,p95 1px,maximum1.414px. See contour-overlay.png and contour-comparison.json. Before/after-clay.png use the same neutral view.

## Foundation and aperture preservation

Recover crossing-free111 source; apply exact115E angular/radial warp plus affine and116yaw; replay119 existing feature outlines. Only the119 cutter's intermediate-ring du/dz jitter is disabled. Exact front/back outlines, radial ring positions, ring scales, and rear rise4.2 are retained. Original jitter introduces4 new crossings even on clean substrate. The clean replay produces none.

## Attributes and material roles

Both meshes have POINT vector `115 Original world position`, POINT float `117 Damage proximity`, FACE float `118 Recess interior`.
R also has FACE float `117 Exposed core`. L lacks that field because its119 replay only generates recess faces; a downstream generator may create a zero-filled field where needed.

Source L material index0:wall,35 faces; index1 unused/null.
Source R index0:wall,34 faces; index1 unused/null; index2:fracture,165 faces.
`apply_prepared` preserves target material slots by index and clamps indexes to available slots. Caller must confirm current target role mapping, especially fracture/core treatment. It does not recreate legacy materials.

Object roles:coliseum_role=wall,tier=3,bay=8. Replacement sets `123 repaired crown base`=true. Exact inspected metadata is handoff-data.json.

## Attached detail

Remove/regenerate120 attached facets only where `120 owner` equals one of the two target names. Their old surface attachment cannot be assumed after foundation replacement. Preserve facets owned by sill walls or other components.

This repair deliberately restores a simple safe foundation. Fine contour damage is a separate study, tools/coliseum_fine_chips_123.py; it uses strictly checked convex negative cuts. No claim that the foundation alone solves final fracture fidelity.
