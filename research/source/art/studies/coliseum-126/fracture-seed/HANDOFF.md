# 126 profile-first fracture study — HOLD

Primary125 is unchanged. This is not approved or integration-ready geometry.

## Native construction
Clean111 control crown profiles are retained as the coarse height graph. Irregular clustered negative rim notches and shallow core depressions are modeled into a closed structured mesh before the exact accepted perspective/yaw transform. There are no attached chip objects, shader bump, or arbitrary XYZ noise. The 119 main breach and recesses are then replayed under proper triangle-intersection guards. Only the two U8 fractured L/R wall mesh data are swapped into a copy of125 for proof; existing rods, cornices and architecture are untouched.

## Result and limit
Both seeds and retained outputs are closed, positive volume and zero detected proper triangle crossings. The primary breach replays. Two secondary R changes fail the guard: short rear ledge loss and connected field loss. Those cuts roll back, so this does NOT preserve all accepted macro damage. An alternate Manifold solver additionally rejected the primary breach and was discarded. Prepared API refuses default integration; incomplete-study opt-in is required.

The first visual proof has clearly fractured rim geometry in close clay, but roughly1px main-camera difference on the exposed left rim. Larger v2 uses wider/deeper rim cuts and stronger rear-rim damage to test visibility. Its validation limits remain the same. Full broad exposed core still has too much planar area; narrow triangles can read stretched rather than chipped stone.

## Files
`tools/coliseum_fracture_seed_126.py`, source and reusable held API. `fracture-seed-v2` is the stronger scale study. Both have matched before/after clay, painted and actual4K-camera cropped renders, geometry.blend and numerical audits. No main-camera zoom is substituted for the scene-scale proof.

## Recommended next foundation
Keep the accepted current lower wall and breach topology, and replace only an isolated crown strip with a conforming triangulated patch. Match the patch perimeter exactly to current mesh vertices, then apply ordered-height erosion within that strip. This avoids replaying already accepted macro booleans against a newly dense full wall. Validate the resulting seam, crossings and volume before any new artistic microdetail. Do not continue accumulating failed tiny Boolean cuts.
