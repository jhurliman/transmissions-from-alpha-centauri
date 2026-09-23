# Rock geometry study 090

Reference crops are enlarged from the selected concept image in art/reviews/xenon-001/selected-third.png. US-01 and US-02 guide road scale; DP-08 remains the architectural reference. These are comparison references, not imported geometry.

Observed rock hierarchy:
- Dark road: sparse low wedges, off-center ridges, broad slanted tops, partly buried bases. A few irregular side facets carry the depth.
- Pale soil: dispersed small fragments plus intermediate broken pieces; strongest size concentration close to buildings.
- Foundation fragments: oblong inclined slabs with broad unequal faces and small local corner fractures. Avoid regular cubes, level-topped prisms and uniform triangular tessellation.

Native factory: tools/rock_masters_090.py. Five families, 15 catalogue examples; closed-mesh topology audited. Scatter comes from tools/scatter_rocks_090.py, with visible foundation anchors and numerical welding in tools/refine_rocks_090.py. tools/rock_visibility_090.py supplies simple directional face shading for readable geometry and a separate physically lit neutral clay placement render. This is not the final ground art treatment.

Soil 089 and all previously accepted buildings/sky remain unchanged. The old hidden rock layer remains hidden. Placement raycasts the actual terrain, partly buries bases, rejects architectural footprints, and uses different size distributions on road and pale banks. Review remaining cluster density against the reference before final material work.
