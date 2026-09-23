# 216 — sun one diameter right

This is a bounded native position comparison requested after the user selected the 21070 Colosseum scale. It is not a sky redesign.

The visible sun is not a mesh: it is the existing `075 Sun angular distance` / `075 Low pale amber sun` procedural disc in the camera-only world shader. It has infinite world-background depth. The helper preserves that native representation rather than introducing a billboard, reference projection or raster edit.

`tools/sun_position_216.py` exposes `apply(scene, move_right=True)` and returns the audit. `move_right=False` measures and preserves the original. Start each variant from the same source; repeat application is rejected. The moved variant uses a private copy of the world, with four native vector nodes affecting only the existing sun test input. The original sun direction constant, angular threshold, color and all other branches stay unchanged. Every object transform and scene light is asserted unchanged.

At 3840×2885 the original full apparent horizontal diameter is 105.501709 px. The analytic ellipse center moves from (2250.762634, 211.306118) to (2356.264343, 211.306118). At the half-size preview this is 52.750854 px right. A separate 360-sample boundary transport check finds at most 0.000229 full-resolution pixel error; the apparent shape and dimensions stay fixed. The native world sun's infinite depth remains infinite.

CPU candidate `sun-right-cpu.blend` uses the selected 21070 scene and its existing visibility-clipped contact drawing, solely to preserve an inspectable module result. It is not the eventual 215 street integration and is not a final comparison render. Final actual original/moved images should be rendered only after the new shorter alley and characters are integrated, with all native ink guards active.

Before changing the foreground alley, restore the original dedicated landmark contact drawing using `landmark_contact_visibility_210.restore_unclipped(scene, source_digest)`, then reclip against the new external geometry. The expected source digest is `84e3787b91152c4f17587b201a6808531ae69a1e5a96d71e8eda62c2e5da8358`. The retained fake-user drawing is found by digest, not assumed from its name; the scaled object's transform stays fixed. Restoration has been CPU-tested against 21070.

Reference properties are recorded in `config/sun-position-216.json`: UCL-01 (user's original ChatGPT Images 2.5 artwork), DP-05 (Darius Puia / BakaArts, mass and negative space), and HM-03 (Heavy Metal 1981, distant architectural silhouette). Credits and source links remain in the project reference manifest. No reference artwork is used as a scene asset.
