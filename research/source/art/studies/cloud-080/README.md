# Native cloud system 080

Reference direction: UC-01, UC-02, DP-08. No reference image is projected into the scene.

Selected candidate: contour frequency 20, seeded per-cloud variation ±14%, inset frequency ratio 0.42. Four independently seeded broad mass bodies establish a stable shape before boundary frequency is applied. Native contour meshes describe the outer bank and a smoother, subtly darker interior. Small clouds occasionally use a seeded warm palette variation.

`tools/cloud_system_080.py` exports `apply(scene, config=None)`. Apply to a scene derived from079, before saving/rendering. It disables the075 camera-visible cloud mask, preserving its sky gradient, sun and non-camera lighting. New layers live in `080 Native cloud banks`. Re-run from a clean079scene to change generation parameters. Existing collection makes the helper idempotent.

These are editable distant planar cloud contours for a painted background, not volumetric cloud simulation. The interior layer is separated by5m at800m distance to avoid depth-buffer artifacts. Layers are excluded from architectural ink and do not cast shadows.

## Review evidence

- `main.png`: native whole-scene main-camera proof.
- `detail.png`: perspective sky-only proof with the same camera-visible world.
- `mask.png`: native silhouette-only proof.
- `low.png`, `high.png`: frequency10 and30 using the same final generator and macro seed/layout.
- `scene.blend`: main scene saved with default20 cloud layers and all base scene content.
- Earlier rejected proofs retained with `rejected-` names. Raw frequency20/30 trials are preserved separately; `frequency-20-rounded` is the selected frequency-normalized development proof.

The first method generated mountains from upper/lower graph curves and was rejected. The second implicit-mass method initially made smooth capsules; boundary bumps were being buried inside macro bodies. Sampling the actual contour boundary corrected that. Higher frequency originally made serrated teeth; widening bump overlap and reducing amplitude with frequency restored rounded shoulders. Parent-body placement was adjusted to expose the irregular part in the main camera.
