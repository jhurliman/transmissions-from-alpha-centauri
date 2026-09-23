# 190 — distributed colosseum wall-face crumbling

First native prototype requested by the user, kept separate from retained 188 and alley rust 189. This study is not yet accepted or integrated.

## Reference basis

Reference crops and notes are in `reference/`. UCL-01 and UCL-02 are the user's original artwork made with ChatGPT Images 2.5. DP-03 is Darius Puia / BakaArts, retained as reference-only. The selected property is recurring irregular dark masonry loss and subordinate heavy cracking across repeated bays, with quiet intact spans. Deep arch shadows are not classified as surface loss.

## Current native candidate

`candidate.blend` retains the source scene, camera, lighting, architecture and non-colosseum systems. It contains 68 primary shallow recess clusters, 106 smaller companion chips and 10 narrow jagged fracture cuts over 20 wall objects: all three continuous arcade walls and 17 upper-wall pieces. Depth is 0.075–0.22 scene meters. Primary radii are 0.55–1.3 meters with independent aspect and jagged outlines. The whole-landmark proof, rather than these counts, determines whether the scale and frequency read correctly.

Each primary cut has a sloped irregular rim and smaller recessed floor. Floor and rim materials are independent copies of the effective current wall material, inheriting its lighting and palette. There is no artwork projection, billboard damage plane, or full-frame overlay.

Original wall meshes are retained as fake-user native mesh datablocks named `190 SOURCE …`; editable cutter objects remain in the hidden `190 Editable cutters hidden from render` collection. The visible Boolean result is baked into each wall. Face attributes carry explicit material provenance to avoid Blender's duplicate-slot remapping, and output slots are DATA-linked. Existing material graphs are not edited.

The repeatable entry point is `tools/colosseum_crumbling_190.py::apply(collection, config=None)`, called on a fresh 188-derived colosseum collection. Configuration controls seed, cluster count, upper-wall probability, scale, depth, fracture probability and rim/substrate gains. Calling twice on a scene is rejected. The module does not touch alley rust; root integration can apply it to 189 after visual acceptance.

## Scope and limits

Native auditing verifies the allowed wall-only changes and unchanged old material graphs. Visibility counts use colosseum occlusion only; foreground alley and city may hide additional patches. Existing overlapping wall/pier surfaces remain a source-topology ambiguity, not a global clean-mesh certificate. This is a first broad distribution proof; final full-frame retention and any revised placement follow visual review.

## First painted proof — held

The first whole-landmark crop is `landmark-painted.png`, with `baseline-landmark.png` for context. The pockets remain too restrained and too often occluded to meet the requested broad visual impact. Do not integrate this version. The next change should create fewer, larger connected groups on verified visible faces, rather than raising the small-pit count. See `review.json`. The baseline is resized from4K while the candidate is a native50% proof, so fine line antialiasing is not pixel-comparable.

The material-provenance table and DATA links validate after reopening, but65 nearest-surface samples on two lower arcade meshes still disagree with the source. Treat that as unresolved before integration, rather than assuming source overlap explains it.
