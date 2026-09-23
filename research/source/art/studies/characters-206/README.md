# Airam and Miranda — character study 206

Two static rear-view treatments derived from the user's photographs. The comparisons use the corrected209 scene. The former scale figure and its eight residual contact-ink strokes are hidden only in the separate study scene.

## Pixel deliverables

Primary: `pixel/airam-49h-24c.png` and `pixel/miranda-47h-24c.png`.

Airam's painted silhouette is22×49 logical pixels, in a24×51 canvas. Miranda is16×47, in an18×49 canvas. Each contains exactly24 opaque RGB colors plus one transparent index.16-color alternatives and double-detail98/94-pixel-high alternatives are included. No dithering or partial alpha. Dimensions and complete palettes are in `pixel/exports.json`.

Display source pixels with height1.2×width to reproduce the DOS appearance. Previews enlarge10×horizontally and12×vertically. Do not smooth the final sprite. The original-scale and double-detail scene composites use identical integer-scaled body sizes and feet positions.

The Xenon screenshot's drawn silhouette is17×49 logical pixels. Its exact original palette cannot be recovered from the supplied JPEG-derived capture.24 colors is a deliberate working budget, not a claimed measurement of the game's original sprite palette. See `reference-analysis/findings.json`.

The generated artwork preserves the photographed clothes/hair/back view but interprets proportions for a standing game figure; it is not an exact silhouette trace of the high-angle photographs. Tiny hearts become red motifs at native scale. The double-detail option preserves more shape. Original generated images and prompts are retained for revision.

## Anime deliverables

`anime/airam-anime.png` and `anime/miranda-anime.png` are full-resolution transparent illustrations. The separate native lighting feasibility study uses actual scene camera/lights on flat textured cards. See `anime/README.md` and `anime/native-proof-audit.json` for the measured response and limits. This is generated2D character artwork, not accepted editable3D character geometry.

## Provenance and scope

Source photos by the user, copied intact to `private/character-sources/`. Artwork generated with the built-in image tool; pixel finishing uses the explicitly requested strict grid/palette quantization. Prompt sets and raw outputs are preserved. No original Roger sprite is composited into these assets. No animation, movement directions, collision, or rigging are claimed.

Review: `prototype/review-206.html`. User artistic acceptance remains pending.
