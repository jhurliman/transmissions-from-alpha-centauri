# Optional radial joint shading correction

API: `tools/coliseum_joint_shading_129.py::apply(C, strength=1.0, actual_diffuse=False, reduce_ao=True)` on the current129 scene, once. Native geometry and material attributes only. No primary files modified.

Exact collection-only rays identify the apparent overshoot as real radial stone end faces (e.g. B07 outer stone06 face12 at close-crop300,84), not flush-wall triangles. Broad orientation contributes the dark painted color; local AO contributes the remaining dark end-face stripe. True geometric normal substitution did not remove the problem. Correcting actual diffuse normals adds no useful improvement and is disabled.

The optional treatment tags only radial end faces, then uses the analytic facade broad normal in the broad painting branch and reduces AO only on those tagged end faces. All vertices, gaps, physical normals, glossy response, true tunnel depth and other faces' AO remain unchanged. It intentionally softens directional contrast on masonry joint ends; this is a localized artistic shading correction, not a geometry/normal-topology repair.

`current129.png` and `corrected129.png` are matched native crops rendered from the current129 main scene with its regenerated contact ink and original Freestyle setting. `final-audit.json` records the applied option. Earlier fill/diffuse/AO/no-ink proofs are diagnostic, not current-scene deliverables.
