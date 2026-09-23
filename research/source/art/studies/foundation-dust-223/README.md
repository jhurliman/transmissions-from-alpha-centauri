# 223 — pale foundation dust

CPU-prepared native material pass; actual visual inspection will use the combined222/224 proof. No independent environment render was launched.

Scope was inventoried before edits:410stones tagged with `rock_family` and `scatter_zone=bank`,158left and252right, using8material variants. All120tagged road stones and unrelated foreground junk are excluded. Native geometry, transforms and original mesh material tables remain unchanged; bank objects receive private OBJECT-level material overrides.

The dust color is the actual existing pale-bank branch of `Street foundation` → `092 painted earth B` → `Mix (Legacy).006`, which feeds input2 of the soil region mixture. Its upstream shader is cloned into an editable node group, not replaced with a guessed tan or sampled screenshot color. Soil itself is unchanged.

Original slate/violet/ochre/ridge graphs remain underneath. Nominal deposit blend is about52% on upward faces and16% on ordinary sides, with fine broken coverage and a small0.18m ambient-occlusion crevice bonus. Final blend is capped65%, retaining at least35% of the original stone color everywhere. Ink is not edited.

API: `foundation_dust_223.apply(scene)`. Integration order:222architecture, then224pale right alley/new small stones, then223dust. New224stones must retain the bank tags and native091-family emission palette materials to inherit the pass. CPU replay was tested on221; the candidate is `scene.blend`, with per-object material inventory in `audit.json`.

References and specific properties are recorded in config/foundation-dust-223.json. UCL-01 is the user's original ChatGPT Images2.5 artwork; DP-08 and UP-03 retain their registered project provenance. This CPU audit does not imply visual approval.
