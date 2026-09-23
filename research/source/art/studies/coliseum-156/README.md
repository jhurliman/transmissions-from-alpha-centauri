# 156 — Connected crown thickness and masonry age

This working candidate combines the independently retained 154V2 crown geometry, 153V3 cornice pigment adjustment and 155 spandrel-age placement on the retained 152 scene. It also removes 14 exactly collapsed faces from five separate meshes while preserving every nonzero evaluated triangle, normal and material assignment on those cleanup targets.

The crown preserves the substantial left facing ridge and split, with a deeper central loss and a shorter, differently oriented right return. The first 154 version was rejected because it removed a useful depth cue; it remains archived in `coliseum-154/geometry/v1`. The second version passed local independent review, but its smooth broad face and modest scene-scale effect still need judgment in the full render. No automatic score increase or user approval is implied.

The material changes preserve lighting, AO and ink. Five private cornice receivers reduce diagnosed procedural pigment clumping after nonlinear shader thresholds. One existing age lobe moves onto the mapped lit spandrel. There is no global brightness change, new texture layer or new noise strength. All current alley systems, including 3× bottom splatter, remain part of the source scene.

## Native delivery

The integration script saves `scene.blend`, `kit.blend`, `generation.json` and `preservation.json`. Rendering uses the final native ink and the saved 149 geometric visibility guard. The guard is embedded in the scene; direct rendering of that file requires running its saved text or trusting script execution for this file. The integration render command applies the guard explicitly without changing global preferences.

`delivery-manifest.json`, generated after verification, pins the exact incremental source, scripts, configurations and output assets by SHA-256. This is an incremental rebuild from the retained 152 native scene, not a rebuild from no historical inputs. Fresh reopen verifies no linked IDs, all nine full-scene pigment images packed, and exact correspondence of all 3,533 landmark objects between scene and kit under evaluated geometry, normals, transforms and material assignments. The kit is also appended into an empty scene for isolated proofs under the source camera and lights.

## Geometry limits

The new 154 cuts are closed and strictly subtractive. L and head have no robust detected intersections; R retains the same five exact inherited crossing pairs and adds none. Small solver residuals are recorded under simultaneous 0.5 mm world / 0.02 native-pixel bounds; protected lower framing is unchanged.

The broader inherited asset is not certified globally free of folds. The finite 43-object audit in `preflight/crossing-disposition-v2.json` confirms 2,291 crossing pairs in 34 candidate objects, all within connected components. Seven objects have current-camera visibility candidates, with the largest projected intersection segment below 0.5 pixels at 4K. Those samples do not prove all shadow or other-view consequences absent. U10L and U15R also retain collapsed faces entangled with folded returns. The five safe numerical cleanups address only 14 zero-area faces and do not repair these inherited folds.

## References and review

UCL-01 is the project creator's original artwork made using ChatGPT Images 2.5; UCL-02 is its registered detail. DP-03 supplies the second-source study of quiet structural planes. These are inspected references, not image layers projected onto the native geometry.

The actual 3840×2885 full render took 130 seconds. Independent `critic.json` retains the landmark as a working candidate at 95 / 95 / 92 / 93 / 93 / 94, unchanged from 152. Small local improvements do not close the scene-scale damage and age hierarchy. The target remains 95 or above on all six coliseum axes; final user acceptance remains separate.

The corrected native full render is now promoted. The additional embedded foreground visibility guard checks five exact source/receiver pairs using actual 3D depth; it suppressed 145 of 351 sampled segments only where all three points were behind the receiver by more than 2 cm. The earlier apparent missing crack was a rubble outline leaking through the plinth, so no false replacement line was added. Both embedded visibility texts must run when rendering the saved scene directly. The versioned integration script installs both guards explicitly.

All 20,490 native object fingerprints and material graphs match the unguarded 156 scene. The corrected render is intentionally not pixel-identical to 152: hidden ink is removed. Every meaningful outside difference group was visually inspected. Small residual shading differences also occur outside the corrected strokes: one door-frame grain region has 617 pixels over four channel units, maximum 31, and 161 landmark pixels exceed four, maximum 21. Their cause is not established as ordinary run noise. No changed visible architectural outline was observed in those residual regions. This is a disclosed raster limitation, not a claim of exact pixel preservation. Full evidence is in `regression/correction-review.json` and `regression/CORRECTION-HANDOFF.md`.
