# Native foreground ink visibility correction

The T-shaped regression is not painted into the material. Isolating ink selection to `Y arm back flange.010` and `Deck cross joist web.038` reproduces it. These real structural members lie behind opaque `Folded fascia.005`; ray tests find a 0.11–0.44 m depth gap. 148/149 Freestyle settings, camera, and evaluated fascia geometry compare exactly. View-map caching was already disabled. Culling did not fix the leak. The internal reason a distant landmark edit changed Freestyle's quantitative visibility remains unproven.

`tools/coliseum_ink_regression_149.py::apply(scene, embed=True)` installs an additional native Freestyle StrokeShader via Blender's built-in post-stylization callback. Only segments belonging to the two exact named structural view-shapes are eligible. The callback transforms their camera-space 3D sample positions to world coordinates and tests both endpoints and midpoint against the evaluated fascia BVH. A segment is marked invisible only when all three samples are more than 0.02 m behind that opaque surface. Other shapes, visible parts of the same members, geometry, materials, and all original line widths/selectors remain unchanged. No screen-coordinate mask is used.

The first native crop proof hides seven segments (two flange, five joist) and removes the false T while retaining the rust trail. `guard-audit.json` records actual depths. `visibility-guard.png` uses the original 4K camera, [230,830,290,880] border. No-Freestyle and suspect-only controls are also present. Comparing a cropped render to a full-frame crop can have sampling/border differences; use the fresh matched control for final pixel evidence.

## Reopen / render persistence

`apply(scene, embed=True)` creates self-contained text `149 Native fascia visibility guard.py` with `use_module=True` and an idempotent render-pre handler. Save normally. On reopening, Blender must allow trusted Python auto-execution (CLI `--enable-autoexec`), or the user must explicitly run the embedded text once. No repository module is needed after save. Every render rebuilds the evaluated occluder BVH, so it does not reuse stale camera/instance coordinates.

A deterministic build/render wrapper may instead import the module and call `apply(scene)` after loading the scene, regardless of auto-run preferences. Reapplying replaces the previous guard handler/callback rather than stacking duplicates. This is the recommended pipeline path for the 150 candidate. No canonical 149 files were overwritten.

Scope limitation: this addresses the demonstrated foreground visibility regression; it is not a global Freestyle or mesh-cleanliness certification. The opaque-fascia assumption is specific to this accepted scene. If that material later becomes transparent, the guard must be disabled or updated.

## Final verification — frozen

Fresh matched unguarded versus guarded crop changes106 pixels above3/255, within full-frame x248–267,y832–857.101 belong to the T region;5 are an adjacent tip on the same occluded joist. `matched-compare-8x.png` preserves nearby intentional outlines and rust.

A new Blender process reopened the saved isolated scene with `--enable-autoexec`, without importing this repository module or manually reapplying it. The embedded render-pre handler ran, hid the same7 geometrically occluded segments, and produced a **bit-identical** guarded crop. See `persistence.json`, `reopened-guard-audit.json`, and `reopened-guard.png`.

The module and isolated scene are frozen for150 integration. Apply using `guard.apply(scene, embed=True)` after loading/building the candidate and before saving. The root render wrapper can call it again after reload for deterministic operation independent of UI auto-run preferences. For auditing a full render, native callback audit dictionaries are available after rendering as `f._guard_149_audit` for callbacks in `parameter_editor.callbacks_modifiers_post` with `_guard_149` true.
