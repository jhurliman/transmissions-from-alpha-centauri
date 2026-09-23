# Bay8 fracture source audit

The reported 11/23 crossings are not all false positives. An independent pass added strict triangle-interior barycentric and opposite-plane-side tests to the existing BVH/segment test. It found 11 left-wall and18 right-wall crossings in119; five right-wall flags were rejected as edge/tolerance cases. No flagged pair belongs to the same polygon, so these are not merely different triangles of one n-gon. Several penetrations have millimetre-to-centimetre plane distances. Floating-point checks are evidence of defects, not an exact-arithmetic certification of every intersection.

| Native scene | Left strict pairs | Right strict pairs |
| --- | ---: | ---: |
|111|0|0|
|112|11|9|
|114|11|9|
|116|11|13|
|119 geometry proof|11|18|

The first defect appears in112, before119's breach. `coliseum_fracture_112.py` subdivides all mesh edges, triangulates and displaces exposed-surface vertices with three-dimensional roughness. Its projection against an adjacent intact face prevents movement normal to that face but does not prevent tangential movement from folding thin triangles. The acceptance check tests manifoldness and positive volume only. A closed mesh can self-intersect and still satisfy both. Later deformation/cutting adds or exposes further crossings; the present check does not isolate every later cause.

## Recommended bounded repair

1. Use111's crossing-free source as a topology template for the affected crown strip. Preserve the accepted current macro contour and later approved position/curvature; do not roll back the whole landmark or erase119's aperture.
2. Build an ordered authored-space contour for the current coarse break. Add clustered short chip notches along its arc length, bounded to a narrow strip. Give front and rear contours explicit correspondence and shared vertices. Keep the intact wall boundary fixed.
3. Triangulate the front patch and through-thickness strip explicitly. Use constrained planar triangulation for planar patches; divide curved portions into locally well-shaped patches before warping. Avoid large nonplanar n-gons and avoid independent displacement of all XYZ components.
4. Add relief along a controlled local surface direction. Limit amplitude using local edge spacing and clearance, then backtrack any update that flips a triangle or creates a strict crossing. Small irregularity belongs on exposed fracture faces; it should not move the intact wall field.
5. Replay the existing aperture/recess cuts only after the repaired base passes checks. Validate each cut immediately. Reject self-intersections, inverted/degenerate triangles and unwanted connected components as well as nonmanifold edges. Maintain an outside-strip surface-distance guard and compare the main-camera silhouette and sky rays.

This changes the failure-prone substrate rather than decorating it. The120 attached facets are separate closed objects and did not cause these inherited crossings, but they cannot repair the underlying folded shell. No scene geometry was changed during this investigation.

Machine evidence is in `source-crossing-audit.json` and the four versioned audit JSON files alongside this note. Test script used: `/tmp/critic_cross121.py`; historical sweep: `/tmp/critic_provenance121.py`.
