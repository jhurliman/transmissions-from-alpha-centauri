# Scene-wide approved ink

Base: user-locked soil094C and accepted scene geometry/materials.

Rebuild with Blender using `tools/intersection_rollout_096.py`. It reads the native scene and generates two editable Grease Pencil drawings: face intersections and geometric damage material boundaries. All render-visible solids participate in occlusion. Sky and the reserved landmark retain their existing linework.

Widths are normalized to the accepted main camera: contacts 0.6 px radius, prior footing contacts 0.8 px, damage 0.45 px. Pigment-only weathering remains unchanged.

The baked drawings are camera-dependent. Regenerate after moving the camera or changing geometry; ordinary renders of the saved scene reuse the baked drawings. Source meshes are never altered by this stage. True tangency/coplanarity is not a face intersection.

The 095 sample scenes remain available. See `audit.json` for scene-wide coverage and timings and `review.json` for visual verification.
