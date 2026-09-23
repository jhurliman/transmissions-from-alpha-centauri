# 226 · Taller marked buildings and a narrower far street

The user markup is registered to the native camera at1.5native pixels per markup pixel, offset(1155,−4.5), using an unmarked tower patch (normalized correlation0.991). Magenta aligns with the visible stepped prefabs at83m left and89m right, not the more forward48/51m pair hidden behind foreground architecture.

Each selected stepped prefab gets its own private container. Two additional full2.18m panel courses raise it4.36m. Existing panels and complete service routes retain their dimensions. Roof slabs and matching cap bands move together; new structural courses support the added height. Native panel courses also finish both end returns. Other copies of the prefab are unaffected.

The final three rows per side move inward progressively. The farthest facade edges project to1811/2022px versus the approximate green targets1802/2034px. The left pipe reaches1833px, intentionally beyond the facade footprint. The new roof tops project to809/819px versus magenta targets800/833px. Complete native courses take priority over stretching parts to the exact boundary of a thick marker stroke.

`projected-before-targets.png` and `projected-after-targets.png` are diagnostic bounding-box overlays on the baseline image, not candidate renders or acceptance artwork.

The dedicated110contact ink is restored from its preserved unclipped source, clipped against the new external geometry, and then passed through225's removed-sill-owner cleanup. The tunnel floors are not lowered again. Foreground096ink, near architecture,221haze,222entrances,223dust,224soil,225thresholds and selected217characters remain fixed. Dedicated215distant ink includes the new native mesh IDs.

API: `tools/far_building_layout_226.py::apply(scene,reclip=True)`. Root owns the final native render and publication. `audit.json`, `projected-target-comparison.json` and `preservation-check.json` record construction and CPU checks. Independent actual-image review remains required; no user approval is implied.
