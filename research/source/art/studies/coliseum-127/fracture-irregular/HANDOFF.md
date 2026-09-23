# 127 validated irregular negative fracture candidate

## Reusable result
`tools/coliseum_fracture_irregular_127.py::apply_prepared(C)` loads only the audited U8 R mesh from this directory. Tested against125. It preserves current material mappings and all object modifiers, so the shared grouping modifier remains last. It requires the125 authored object transform; do not apply after baking grouping into vertices. Other objects, rods and supports are untouched. No production file was modified.

`apply(C)` is the editable construction routine for a clean voxel R input:18 irregular convex cutter volumes, union, actual Boolean difference and one final0.02m native voxel reconstruction. It does not displace vertices into arbitrary noise. Temporary cutter objects are removed. Shared115 original-position projection and117/118 material attributes are retained/transferred; new deep cut faces use the existing exposed-core material.

## Checks
Final one connected mesh:530,716 vertices/faces,0 nonmanifold edges,0 detected proper triangle crossings, positive volume85.12664484. One8-vertex disconnected voxel speck was removed. Worst reconstruction movement outside cutter neighborhoods≈52mm. Original125 versus final actual4K sky contour changes18 pixels with maximum boundary displacement1pixel. The sky test does not measure interior recesses. Prepared-API audit is included.

## Actual visual outcome
The triangular edge bites read more like fracture than the preceding box-like pockets and now contain real depth. The main-camera improvement remains modest: a few small dark accents, not a solved damage system. The wide exposed crown face is still too quiet. The initial0.04m voxel foundation leaves a fine regular staircase visible in enlarged clay; the final0.02m reconstruction does not undo that inherited quantization. Initial foundation thin-surface removal is still documented in126/volumetric/audit.json (reverse worst1.10m), although the broad exterior remains within1pixel here.

## Proofs
`original-*`:125; `before-*`:clean voxel foundation; `after-*`:irregular cut candidate. Each includes actual4K-camera crop, painted closeup and neutral clay. `geometry.blend` is the production-style candidate; `proof.blend` is the isolated clay review. Images precede deletion of one invisible8-vertex voxel speck (volume~8e-9); geometric validation was repeated afterward.

This is a candidate, not user approval. Keep the main scene unchanged until parent visual assessment.
