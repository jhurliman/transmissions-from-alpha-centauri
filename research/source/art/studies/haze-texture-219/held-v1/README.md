# 219 — faint spatial haze

One restrained native comparison against final218/current-sun. The reference's faint irregularity is interpreted as spatial density variation within the existing warm volume, not distinct sky clouds or a colored facade wash.

The previous material varied only with world depth and height. This study introduces two centered3D noise scales, shared by scattering density and orange volume radiance. Nominal multiplier mean is1; theoretical bounds0.78–1.22, with typical deviations much smaller. Noise is faded in between worldY48–78m, preserving the nearest haze exactly. The established near-clear/far5x envelope, broad low luminous bank and rear cutoff remain upstream and unchanged.

The density mean is centered parametrically; exact camera-view mean is not asserted from shader settings. `pixel-check.json` records the actual native image comparison and exact preservation of the selected217 character pixels. Actual image review is required to decide whether the texture is appropriately visible and still restrained.

The native candidate changes only a private material on `Distant dust volume - real lighting`. Object transforms, bounds, source material graph, lights, sky, camera, compositor and view-layer exclusions are preserved. In particular the volume stays excluded ONLY from the dedicated215 distant-ink pass. The original192 behavior is unchanged. The candidate render uses the same final218 callbacks and full3840×2885 compositing. Standard outputs are `scene.blend` and `main-4k.png`; no source218 files are modified.

References and studied properties are recorded in config/haze-texture-219.json: UCL-01 is user-created ChatGPT Images2.5 original work, DP-05 is Darius Puia/BakaArts, HM-03 is Heavy Metal1981. Existing reference credits/source links remain authoritative; none of this reference artwork is used as a release asset.
