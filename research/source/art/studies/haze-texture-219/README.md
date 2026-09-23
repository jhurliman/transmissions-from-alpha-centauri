# 219 — faint spatial haze

One restrained native comparison against final218/current-sun. The reference's faint irregularity is interpreted as spatial density variation within the existing warm volume, not distinct sky clouds or a colored facade wash.

The previous material varied only with world depth and height. This study introduces two centered3D noise scales, shared by scattering density and orange volume radiance. Nominal multiplier mean is1; theoretical bounds0.40–1.60, with typical deviations much smaller. Noise is faded in between worldY48–78m, preserving the nearest haze exactly. The established near-clear/far5x envelope, broad low luminous bank and rear cutoff remain upstream and unchanged.

The density mean is centered parametrically; exact camera-view mean is not asserted from shader settings. `pixel-check.json` records the actual native image comparison and exact preservation of the selected217 character pixels. Actual image review is required to decide whether the texture is appropriately visible and still restrained.

The native candidate changes only a private material on `Distant dust volume - real lighting`. Object transforms, bounds, source material graph, lights, sky, camera, compositor and view-layer exclusions are preserved. In particular the volume stays excluded ONLY from the dedicated215 distant-ink pass. The original192 behavior is unchanged. The candidate render uses the same final218 callbacks and full3840×2885 compositing. Standard outputs are `scene.blend` and `main-4k.png`; no source218 files are modified.

References and studied properties are recorded in config/haze-texture-219.json: UCL-01 is user-created ChatGPT Images2.5 original work, DP-05 is Darius Puia/BakaArts, HM-03 is Heavy Metal1981. Existing reference credits/source links remain authoritative; none of this reference artwork is used as a release asset.

Revision2 preserves the first proof in held-v1. V1 was too subtle at actual output: warm-bank red standard deviation1.17/255 and mean drift−0.39. The bounded revision raises centered density variance and halves horizontal/vertical feature scales while retaining long depth correlation. It does not raise overall haze density uniformly. Final actual native metrics and inspection determine whether it succeeds.

V2 native proof is complete. Actual warm-bank RGB mean deltas are(−0.483,−0.186,−0.091) with red centered standard deviation2.235 (V1:1.175); whole-street mean red delta−0.050. Both217 characters remain pixel-exact. Distant ink count matches218:4744strokes/72649visiblepoints. Nativebefore/after crops and full frames show a deliberately understated texture candidate, with no separate cloud silhouettes. This is an unapproved comparison, not a claimed major fidelity improvement.
