# 193 — whole first-left-building weathering

CPU material candidate for root integration into scene-weathering195. The requested art-direction target is a moderate four-of-ten age level across the whole first building, including previously pristine panels and the rear vertical post. This is not a measured visual score; integrated render inspection remains pending.

## Scope identified from the native scene

The first building is `Front-left section instance`, using `133 Left front facade, one missing panel`. Its108 mesh objects have only that one instance host. The dark rear vertical member is `Service bay portal jamb.001`, a rectangular charcoal-steel service-bay post at approximately x−7.65, y3.10, z0–4.24. Its 4K projected bounds are approximately x648–746/y1003–1682. It is separate from Y supports and service pipes.

The rollout touches104 objects with six private material copies: exposed base/upper panels, sloping shoulder panels, cladding, columns, trims, return faces, louvers and the rear portal post. Deep structural/slot cavities, access-cover fasteners, fracture-depth materials and existing fracture ink are excluded. The exposed utility-panel internals, Y supports, all pipes and all bolt/plate corrosion remain outside this module.

## Treatment

- A quiet coherent age field spans multiple panels.
- Irregular medium-size coating losses connect finer chipped fringes, weighted toward panel bases and edges.
- Gravity-aligned moisture trails taper and become translucent downward; world-space placement prevents a repeated identical pattern on every panel.
- Lighter worn fragments interrupt dark wear, while existing lit color and palette remain underneath.
- The charcoal portal post receives worn-metal tonal breakup rather than the facade's coating tint.

Reference IDs: UCL-01, UP-03, DP-03. Crops are in `reference/`; full credits remain in `references/manifest.json`. UCL-01 is the user's original ChatGPT Images2.5 artwork; the others retain their existing reference-only provenance. No reference images are used in the material.

## Integration and preservation

Use `tools/first_building_weathering_193.py::apply(scene)` on the latest fresh192-derived scene. Do not substitute this study's standalone candidate for root's latest ink/compositing integration.

Private materials are assigned through OBJECT slots. There are no object/collection copies, renames, new helper geometry, changed mesh data, transformed objects or render-setting edits. Existing material graphs remain unchanged. Shared material datablocks retain their original graphs and bindings elsewhere.

`audit.json` verifies identical recursive object inventory, only104 allowed material-binding changes, unchanged geometry/normals/transforms/instances/camera/lights, and zero changes to existing material graphs. `sharing.json` records the single-host family check. The module rejects duplicate application.

`candidate.blend` is an editable CPU study. No independent GPU render was started; root owns the combined195 visual proof.

## V2 projection correction

The first integrated195 render exposed horizontal banding on constant-Y pink panels and the rear portal post. V1 reduced world-space position to Y/Z, making those faces sample a one-dimensional height field. V2 uses all three world-position coordinates for broad, medium and fine wear; gravity-led rain uses both horizontal axes with a slow Z frequency. This repairs the field mapping directly, without adding an overlay to disguise it. The treatment strengths, private-material scope and original scene preservation are unchanged. V1 material, candidate, audit and actual195 closeups are retained under `held-v1/`. The revised material requires the combined195 native proof before visual acceptance.
