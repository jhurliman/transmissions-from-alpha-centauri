#189 · Scene-wide fastener and beam corrosion

Source: retained188. This pass applies a reusable native rust treatment across the alley rather than refining an isolated image patch.

## User request and coverage

-3,253 of4,066 logical bolt-head occurrences receive corrosion:80.005%, the nearest whole-head count to80%.
-4 of42 real four-bolt plates are heavily weathered:9.52%, the nearest whole-plate count to10%. They are the left Y splice, right Y splice, middle-left wall shoe and deeper-left wall shoe.
-Their emitted, receiver-supported broad wash areas are51.88%,43.90%,40.65% and65.92% of the plate face. All16 associated bolts receive additional radial and/or drip rust.
-3,022 treated bolts have receiver-fitted root/trickle geometry;231 occluded or receiver-rejected heads have an oxide spot fitted directly to their own head face. None has zero applied rust.2,088 selected centers project inside the frame; this is not an occlusion-visibility count.
-Paired shanks and washers are not counted again. Fresh audit finds no hidden object, parent, instancer or scene-collection paths among eligible heads.

## Beam treatment

Both Y assemblies use private materials on18 arm/stem surfaces. Flat140/143 camouflage islands are replaced with finely broken edge corrosion, granular dark oxide/sienna/ochre variation, interrupted wetting runs and narrow gravity-directed streaking. The initial native proof revealed overly continuous edge stripes; one bounded revision introduced wider gaps and unequal widths before integration. Initial proof/module/candidate are preserved under `beam/v1`.

The obsolete137 rust on both splice plates and eight bolt heads is bypassed through private copies so it does not stack underneath this pass. Their original material graphs remain preserved.

## Native implementation and preservation

`tools/beam_rust_189.py::apply(scene)` supplies the beam finish. `tools/bolt_rust_189.py::apply(scene)` deterministically builds the fastener pass; `append_payload(scene)` appends the frozen fitted layer and performs the matching splice material reset. The cached layer is tied to188 geometry and must be rebuilt if that geometry moves.

One mesh contains46,613 thin native pigment faces, using one translucent native material with bounded actual-light oxide emission. Vertex opacity makes the downward tails fade. Heavy wash boundaries use continuous shared-vertex opacity rather than binary cells; alpha-weighted coverage is33.17%,27.62%,25.37%,42.70%. Each mark is fitted against an actual receiver; face rejection prevents bridging depth steps. Direct head spots are fitted to the source head face. Pigment faces are excluded from Freestyle outlines through a saved union retaining all5,947 previous exclusions. Fresh reopening confirms allfiveactive line filters exclude the pigment object. No photographic texture or projected reference artwork is used.

The integrated scene preserves all20,488 original recursive object entries, their geometry, normals, transforms, camera and lights.28 objects receive private material assignments; one weathering mesh is added. All existing material graphs and the separate colosseum contact ink remain unchanged. Accepted147 bottom splatter, colosseum, sky, haze, ground and service routes are preserved.

## Rendering and reproduction

Use Blender5.2.1 from the project root:

```sh
blender -b -t4 --python tools/bolt_rust_189.py
blender -b -t8 --python tools/scene_rust_build_189.py
blender -b -t8 --python tools/scene_rust_build_189.py -- render
python3 tools/publish_scene_rust_189.py
```

The saved scene is self-contained. Render through the versioned script, or run its embedded149/156/161 native visibility guard texts first. No global trust preference change is needed. The colosseum kit remains the unchanged188 kit; the new reusable weathering is in the two189 modules and fastener payload collection.

## References and review

RS-01(AlamyCXYC2N),RS-02(Stockcake rusty metal beams) andRS-03(Bigstock255633313) are the user-supplied morphology references, registered with URLs and hashes in `references/manifest.json`. UP-03 supplies the existing illustrated surface-treatment context. Original photo watermarks and source links are preserved; reference images are not release assets.

Visual disposition is recorded in `review.json` and independent `critic.json` after the actual native render. Numerical coverage audits are not substitutes for visual review or user approval. The previous colosseum95 criterion is not a score for this new rust pass.

## Final visual disposition

Root and independent critic retain189 for user review after actual4K whole-frame, both-beam and four-plate inspection. Bolt rust remains deliberately subtle at normal viewing size. The broad distribution is real, but no dramatic whole-scene transformation or new95 score is claimed. User approval remains pending.
