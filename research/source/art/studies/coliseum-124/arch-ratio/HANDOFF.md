# 124 arch-to-wall ratio study

Frozen entry point: `tools/coliseum_arch_ratio_124.py::apply(C, reduction)`, accepting0.05,0.10,0.20. Source123/scene.blend. Run before or after the independent column replacement; ownership is disjoint.

All three variants successfully change53 of54 actual see-through arcade openings. Clear authored width and clear height are both multiplied by0.95/0.90/0.80. Height is anchored at the existing sill-top level; crown and spring move downward. Outer floor tops and bay widths remain fixed. Full-depth side masonry is joined to the existing deformed spandrel using its exact shared endpoint vertices. There are no dark panels or false opening masks.

1590 associated archivolt/jamb/impost pieces follow each variant. Archivolt molding thickness is retained while its inner radius follows the smaller arch. Original-world paint coordinates are updated on both wall and trim geometry. Existing arch-depth attributes/materials preserve front-quarter versus rear-three-quarter treatment; new side return faces reuse the existing depth material and authored radial depth.

Solid piers, boundary pilasters, plinth/capital stacks, and bedding joints are excluded from this operation; those belong to the independent columns124 agent. Floor/cornice bands are not deformed.

## Deliberate exception

`COL110 T2 B10 loadbearing arch tunnel` retains its123 shape and trim in all three variants. Its previously fractured end topology has124 candidate side faces, rather than two intact end caps. It was safely skipped instead of rebuilding that damaged section. This is one visible/partly occluded exception nearTower10; do not claim54/54.

## Verification

Each variant:53 successful joined wall meshes,zero nonmanifold edges,zero strict triangle crossings,positive volume. summary.json and05/10/20/audit.json contain counts and dimensions.05/10/20/geometry.blend are independent editable variants.

10/clay.png and10/painted.png are matched close proofs of several actual openings: inspected, continuous wall-to-infill join,attached moldings,and visible tunnel depth. No tears observed. Primary integration owns final three-way main-camera renders. No additional05/20 isolated renders are required for handoff.

This is a user-choice proportion study, not user approval of any ratio. Preserve all three alternatives until selection.
