# 082 Native billows and flat pigment

Candidate, not user approved. Strict target remains95; the independently assessed main frame reaches87 overall. Palette reaches95 after final-pipeline calibration.

The cloud masters are unequal ellipsoid masses fused into closed editable meshes. Medium shoulder volumes and shallow displacement enrich their silhouettes. A separate stored macro-normal field keeps illumination simpler than the outer boundary. Three unequal authored banks and a thin wisp family frame the existing sun; placement is deterministic, not uniform random scatter.

## Editable sources and derived assets

- `assets/arch-master.blend`: selected morph3 billow/channel profile.
- `assets/shoulder-master.blend`: complementary bank profile.
- `assets/wisp-master.blend`: long narrow wisp.
- `assets/wisp2-master.blend`: stepped taper with raised shoulder.
- Each corresponding `.png` is derived only from its native render. `-cropped.png` removes empty alpha margins; `-pigment.png` contains final-pipeline color calibration.
- `scene.blend` contains the final main scene, packed image assets, and separate cloud collection.
- `tools/cloud_system_082.py` provides the native generator `apply(scene, config)` and final scene integration `apply_flat(scene)`.

The user explicitly authorized native3D-to2D cloud flattening. No reference pixels or generated artwork enter the assets. References UC-01, UC-02 and DP-08 guide morphology and palette only.

## Flattening and color

The original native alpha remains intact. Native illumination is normalized by alpha and smoothed with Gaussian sigma8 pixels. The lowest23% illumination becomes selective shadow; the brightest13% becomes light. Tiny isolated shadow regions are removed, then the interior boundary is smoothed at2.5 pixels and clipped to native alpha. This retains detailed silhouettes with broader contiguous interior strokes.

Source sRGB body is204/83/62, shadow198/79/61, light210/88/64. The existing full-scene pipeline initially shifted body to204/98/76. Subtracting21 from the cloud asset green/blue channels before rendering restores the measured final body to204/83/62–205/84/63. This compensation applies only to cloud pigment assets. Sky gradient, sun, scene lighting and all noncloud materials remain unchanged. Cloud layers are camera-visible only and excluded from architectural ink.

## Review and remaining decisions

See `critic.json` for independent strict scores. The best main frame is substantially closer than080, but is not95 across all axes. The remaining gap is richer irregular overlap and branching banks; a few cap arcs and thin tails are simpler than reference. Morph4's extra neck/top masses did not produce a clear benefit, so morph3 stays selected. Further progress should compare deliberately different cloud-group compositions rather than add uniform detail or inflate scores. Previous component trials and composition-v1 remain available for comparison.
