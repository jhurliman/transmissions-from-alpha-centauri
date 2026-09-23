# 190 — distributed colosseum face crumbling

**Current candidate: v2, exact native audit passed; painted proof pending.** This is a separate user-requested weathering study, not yet integrated or approved. The inadequate first version is preserved under `held-v1/`.

## Reference and visual scope

UCL-01 and UCL-02 are the user's original artwork made with ChatGPT Images 2.5. DP-03 is Darius Puia / BakaArts, reference-only. Crops and observations are in `reference/`. The studied property is recurring dark, irregular exposed masonry around wall/arch shoulders and upper openings, with quiet intact spans. Deep arch shadows are not classified as surface loss.

The first prototype dispersed too many tiny pockets behind trim. V2 instead has **30 larger connected groups**: seven on each arcade tier and nine on upper walls. Each group combines two or three unequal jagged lobes. All group centers were verified against actual scene occlusion from the unchanged game camera. Their projected span is x1445–2278, y495–1133 at 4K. The painted proof still determines whether their visible impact and shape hierarchy are sufficient.

## Native implementation

`candidate-v2.blend` starts from retained188. `tools/colosseum_crumbling_190.py::apply(collection, config=None)` is reusable on a fresh188-derived collection, including root's later192 integration. The module changes geometry/materials only and does not replace the current rendering/compositing setup.

Recesses use constrained triangulation inside affected source faces, with 0.13–0.28 meter depth, darker floor materials and sloping fractured rims. Original wall vertices and original face boundaries stay fixed. Every new face carries its exact source-face identity; original materials are copied from effective object slots. Untouched faces retain their original geometry, material, attributes and edge marks. Original source meshes remain editable native datablocks named `190 SOURCE …`.

Only new recess materials are independent copies. Existing material graphs are unchanged. There is no image projection or damage billboard. Configuration controls the seed, visible group count, lobe scale, depth, and rim/substrate tone.

## Exact preservation and resolution of v1's65 cases

V1's whole-wall Boolean regularized nearly coplanar horizontal wall/pier cap faces far from the requested recesses. Its65 material sample disagreements were not safely explained by nearest-surface approximation.

V2 avoids that global operation. All65 flagged cases now resolve to source faces retained with their **exact original vertex sequence and material**, proven by explicit source-face identity. The issue is fixed in v2, not outstanding.

`native-audit-v2.json` records:

- 36,348 non-cut output face material bindings checked against exact source-face identity;
- 30,049 untouched face geometry checks;
- all original wall vertices preserved exactly;
- 20,476 non-target scene/instance entries and every existing material graph unchanged;
- maximum untouched custom-normal storage delta0.000576, from normal encoding.

This is a scoped preservation audit, not a claim that inherited scene topology is globally clean. Final native painted review and root integration remain pending.

## Painted v2 review and standalone delivery

The painted proof is `landmark-v2-painted.png`; `detail-v2.png` enlarges the wall damage and `comparison-v2.png` places baseline beside current. Root judged this a legitimate broader first pass and requested standalone delivery while independent review continues. It is not integrated into192 and has no final score or user approval. The page is http://127.0.0.1:8765/prototype/review-190.html.

`payload-v2.blend` plus `payload-v2.json` freeze the exact12 changed meshes. After acceptance, call `replay(collection)` from the main module to apply those exact meshes onto an unchanged colosseum in a later scene. Replay asserts original mesh/material/transform identities and preserves camera, lights and rendering/compositing setup. `replay-audit-v2.json` records a successful fresh188 replay. This avoids re-running visibility-dependent placement against newer alley weathering.
