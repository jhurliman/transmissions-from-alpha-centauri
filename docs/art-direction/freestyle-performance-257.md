# Freestyle performance investigation — 257

Observed in256: a live process sample placed the one-core plateau in `Freestyle::Controller::ComputeViewMap`, including winged-edge geometry cleanup. It was not the Metal compiler or a lack of available CPU threads. The scene has two enabled Freestyle layers: architecture and distant/detail ink. Both had camera culling and view-map caching disabled; smoothness was already disabled.

First trial: enable `use_culling` only on the two ink layers. Keep styles, line weights, selection, visibility guards and geometry unchanged except the user-requested lower-panel repair. Compare the complete native output against256, especially all image borders and silhouette occlusion. Record total render timing, but do not attribute an entire timing difference to culling: the warm session and scene edit are additional variables.

Further candidates, not yet implemented:

1. Export and reuse the actual native ink passes when geometry, camera and occlusion are unchanged. Material-only soil/weathering edits could then bypass Freestyle. Cache keys must include geometry/modifiers, camera, line styles, exclusion collections and custom visibility guards. Never reuse a pass across a changed crack or silhouette.
2. Build lighter ink-only geometry while retaining the silhouettes and occluders. Merely excluding a collection from a line set does not guarantee a smaller view-map workload. Remove fully irrelevant geometry from the ink view layer; do not remove hidden objects that still occlude lines or cast necessary shadows in the beauty layer.
3. Test independent ink layers in separate processes to use additional cores, constrained by RAM. The current layers are not trivially interchangeable: each has intentional exclusions and visibility rules.
4. View-map cache can help consecutive renders of unchanged geometry in a single ink layer, but Blender documents one shared cache that is replaced by another view layer. Enabling it alone is not a solution for this two-layer pipeline.

Sources: [Blender Freestyle view-layer documentation](https://docs.blender.org/manual/en/5.3/render/freestyle/view_layer/freestyle.html). Local process sample `/tmp/ink256sample.txt`; layer inventory `/tmp/audit257.log`.

During257, a later live sample showed `Controller::DrawStrokes` → `Operators::select` → `Director_BPy_UnaryPredicate1D` and Python `all`/`any` predicates. Thus view-map construction is not the only bottleneck. The distant layer has many separate rubble/detail line sets; consolidating compatible sets while preserving per-group width/opacity is another concrete candidate. It requires a style-preservation comparison and is not implemented in257. Evidence: `/tmp/sample257ink.txt`.


Result:257native full render1362.5seconds, versus256approximately1108seconds. This trial did not demonstrate an overall speedup and was not controlled for warm-session reuse or the scene edits. Small stroke differences outside the two edit regions were visually inspected; no material silhouette regression found. Do not promote culling as a proven speed fix.
