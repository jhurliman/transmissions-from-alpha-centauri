# Scene-generation and rendering performance audit — 089

Read-only investigation requested by the user on 2026-09-12. No production renderer, scene, material, geometry, or approved art settings were changed. The one diagnostic image deliberately omits ink and is not an art candidate.

## Measurements

| Operation | Observed duration | Measurement boundary |
| --- | ---: | --- |
| 087 A/B/C integration + main image | 59.4 / 58.0 / 61.4 s | Blender log differences from scene read to saved main image; includes scene assembly and saving |
| 088 datum integration + main image | 50.9 s | Same boundary |
| 088 neutral detail images | 13.6 / 12.3 / 19.7 s | Blender log first save, then successive save differences; first includes setup |
| 089 dense mesh build | approximately 132 s | Log file birth 21:23:02 through final write 21:25:14; approximate whole-script wall time, no stage timers. Subsequent weld is additional and not separately timed. |
| 089 integration + main image | 76.6 s | Blender elapsed timestamp at image save; includes loading, mesh ingestion, saving, and full rendering |
| 089 saved-scene load | 4.80 s | `perf_counter` around `open_mainfile` in isolated probe |
| 089 same-camera beauty without Freestyle | **13.27 s** | `perf_counter` around render/write; identical saved scene, 1440×1082, same EEVEE/material/compositor settings, only Freestyle disabled |
| 089 entire isolated no-ink probe | 18.09 s | Load + inspection + render/write |

The ~58-second difference between the 76.6-second integration and 18.1-second probe is an **upper bound**, not an achieved ink optimization. The production run includes mesh replacement/save that the probe does not. A clean paired render with Freestyle on/off from the same saved scene is needed to isolate its exact cost. The source remains unchanged; the diagnostic is `no-freestyle.png`.

## Direct evidence of the bottleneck

A one-second OS stack sample of the active production render, around 58 seconds after process launch, caught the main thread in:

`Freestyle → ComputeViewMap → ComputeEdgesVisibility → ComputeCumulativeVisibility → ray/triangle intersections`

Other sampled worker threads were waiting. This identifies visibility/occlusion work in the line renderer at that moment, not shader compilation or EEVEE rasterization. One short sample does not establish its fraction of the entire render. The process had a reported 16.3 GB physical footprint on a 32 GB, 12-logical-core machine. Raising the current four-thread setting alone will not fix this sampled serial phase.

Scene inventory:

- 13,344 objects; 12,716 mesh objects, 5,544 not individually hidden for rendering (collection visibility is not evaluated in that count).
- 211 materials.
- 2,361,089 raw mesh vertices, 4,163,052 raw polygons across mesh datablocks.
- Ground alone: 1,866,106 vertices, 3,691,646 triangles — about 89% of raw polygons.
- Saved scene grew from about 20 MB in 088 to 94 MB in 089.
- Both active line sets exclude the soil collection **for line selection**. This does not exclude that geometry from Freestyle's visibility calculation.
- 089 render log contains 34,268 degenerate-triangle and 20,230 duplicate-edge correction warnings. 088 already contained 34,268 and 9,251 respectively. They deserve an isolated geometry audit, but warning counts do not measure their runtime cost; do not broadly repair approved architecture to chase warnings.

## Recommended order

1. **Keep generation, beauty, and ink as separate cached stages.** The current NPZ/BLEND intermediates already make this feasible. Material/palette changes should not regenerate the ~2-minute native terrain. Reuse the dense mesh. Add explicit elapsed timers for relief generation, crack clipping, mesh welding, compression, Blender ingestion, saving, beauty, and ink so the next decision uses real stage costs. Low effort, zero art risk when invalidation is correct.
2. **Benchmark a separate ink pass using a coarse terrain occlusion proxy.** Preserve the full dense soil for the beauty render. The ink pass only needs enough terrain shape to correctly hide building/support/rock lines; the soil itself is excluded from line selection. A lower-resolution copy should substantially reduce the dominant triangle set. Exact improvement is not measured. Risk: contact-edge occlusion and crack/foreground intersections; compare those crops and keep a full-geometry final verification. Do not simply delete the ground from the ink pass, because hidden edges could show through.
3. **Cache ink for strictly material-only iterations with conservative invalidation.** Camera, resolution, scene geometry, visible occluders, line settings, and any line-relevant material changes must invalidate it. While changing terrain heights, keep the proxy current and periodically verify full geometry. Maximum theoretical opportunity is most of the ~58-second gap; it is not a promised speedup.
4. **Only then reduce dense geometry where it is subpixel.** Current mesh already increases longitudinal spacing from 1.4 cm to 8 cm with distance, but keeps 1.4 cm transverse spacing everywhere. A screen-error-driven grid could reduce memory and occlusion costs further. This carries more art risk than an ink-only proxy because it can remove accepted grain silhouettes/normals. Retain full-detail masters and prove equivalence at delivery resolution before changing beauty meshes.
5. **Defer broad rewrites, engine swaps, or hardware tuning.** EEVEE beauty is already ~13 seconds. Current illustrated shaders use Shader-to-RGB, so switching the full scene to Cycles is not a drop-in speed improvement. The neutral isolated studies use Cycles and are a different workload. Thread/GPU experiments can be benchmarked later but are not supported as the biggest lever by this evidence.

## Decision

Worth a bounded optimization pass: a geometry iteration currently costs minutes, not one or two seconds. Start with stage timing/cache discipline and one coarse-terrain ink-pass experiment. Avoid spending days rewriting procedural generators before testing that high-leverage hypothesis.

Evidence: `probe.py`, `probe.json`, `probe.log`, `render-stack.txt`, and existing ground-087/088/089 logs. No claimed acceleration has been implemented in this audit.
