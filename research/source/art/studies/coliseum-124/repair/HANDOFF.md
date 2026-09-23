# 124 R crown triangle foundation

**Study only; frozen123 integration/tools remain unchanged.**

`tools/coliseum_r_normalize_124.py::apply(C)` changes only `COL110 U8 fractured upper wall R` and preserves material assignments and four shared115/117/118 attributes. Run against the repaired123 polygon source, before new cuts.

The apparent four nonmanifold edges are not boundary holes. Each has four incident triangles because source faces11/171,17/170,and18/193 tessellate into four exact reversed triangle pairs. These internal doubled sheets pass a simple polygon-edge manifold test and a strict non-coplanar triangle crossing test. They become obvious only in the explicit rendered triangle mesh.

The normalization copies the exact existing render triangles, cancels only exact matching triples with opposite normals, and preserves all vertex positions. It does not weld vertices, fill holes, move a surface, or invent a coarse shape.

Validation:
- 4 reversed pairs removed (8 triangles).
- Final231vertices,450triangles.
- Zero nonmanifold edges and zero numerical strict crossings.
- All vertex positions unchanged exactly.
- Positive rendered signed volume84.69669852714318, delta from original rendered triangles -9.95e-14.
- Original polygon BMesh volume84.794740 is not the actual rendered volume; compare against its triangulated baseline instead.

Artifacts:diagnosis.json identifies every edge/polygon/triangle and positions;normalization-audit.json records acceptance;normalized.blend contains the editable source study;before/after-clay.png,painted.png,andmain4k.png are matched rendered proofs. Actual renders inspected: no visible coarse shape/material change. Main4K crop differs by at most1 channel level on a0–255 scale; mean absolute RGB delta0.0000119. Painted closeup maximum1 level; clay maximum4 levels with only2 pixels exceeding3. See render-comparison.json.

Next:use normalized triangle source as explicit baseline for future small convex negative cuts. Revalidate strict crossings,closedness,positive/decreasing rendered volume,and outside-cutter preservation after every cut. Do not relax acceptance thresholds to force a chip through.
