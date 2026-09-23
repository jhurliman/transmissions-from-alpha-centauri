# 221 — stronger orange-to-peach atmospheric volume

This comparison starts from final220, including its descending arcade tunnels and selected219V2 multiscale density field. It does not modify220.

The user requested greater haze opacity and a warmer lower/paler upper transition. The existing native Volume Scatter density is multiplied by2.8, a real optical-density change rather than another noise-only revision. The near-clear/far5x relative envelope, world-height falloff, low luminous-bank shape and rear cutoff remain upstream and unchanged. The existing two-scale field remains fixed.

Both scattering color and existing atmospheric radiance grade smoothly from their retained coral/orange base toward muted warm peach between worldZ1.5m and17m. Neither upper endpoint is white. The native volume geometry and unrelated sky remain fixed; nearest objects sit in front of the main haze bank. A private material preserves the source graph.

The CPU audit verifies unchanged geometry, transforms, visibility, non-atmosphere material bindings, final220 tunnels, world, scene lights, camera,217 compositor, and all view-layer exclusions. The215 distant ink pass still excludes only the atmospheric container. The full3840×2885 proof uses the established149/156/161/192/205/207/218 native callbacks and retains a multilayer EXR.

`tools/haze_texture_221.py::apply(scene)` is the reusable material change. Standard native outputs are `scene.blend` and `main-4k.png`. `tools/haze_texture_check_221.py` compares against final220 and verifies the selected217 character pixels exactly. Actual render review remains the acceptance gate; shader values alone are not a visual result.

Reference properties and credits are recorded in config/haze-texture-221.json: UCL-01 is original user-created work made with ChatGPT Images2.5; DP-05 is Darius Puia/BakaArts; HM-03 is Heavy Metal1981. The inspected UCL street crop shows a coral base fading upward toward muted peach/tan rather than literal white. No reference image becomes a scene asset.

The native4K proof is complete and inspected at street and full-frame scales. The new warm bank is visibly more opaque, with an orange base and muted peach higher; facade ink and nearest clarity remain legible. Selected217 pixels are exact; the sky crop is unchanged; the near-left crop differs only in four one-level rounding pixels. Distant215 ink matches final220:4744strokes/74309visiblepoints. Warm-bank mean RGB change is(+6.34,+14.11,+14.20), an intentional opacity/color increase. This is a candidate pending independent/user review, not an approved replacement.
