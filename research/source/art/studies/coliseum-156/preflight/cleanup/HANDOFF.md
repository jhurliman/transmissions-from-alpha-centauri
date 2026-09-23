#156 conservative zero-face cleanup — frozen

Reusable `tools/coliseum_degenerate_cleanup_156.py::apply(C)` returns a dictionary with `targets` object rows and removed-face totals. Source proof is152; replay touches only the five exact named objects and their copied mesh datablocks. Original material graphs, assignments, unrelated objects and geometry are untouched.

Targets: U3 fractured upper wall R (2faces), U10 aperture head (2), U14 fractured upper wall R (2), Tower7 broken crown (4), Tower13 broken crown (4). The1µm world-equivalent dissolve removes14 exact zero-area faces. Source vertex coordinates and every nonzero raw/evaluated triangle remain exact. All retained source corner normals are restored with zero error. Evaluated nonzero triangles also match exactly including per-corner normals and material indices. Point/face attributes are restored and checked by retained lineage. Closure/orientation and raw/evaluated strict crossing counts are unchanged.

Historical raw near-zero count349→335. The remaining count includes334 collapsed faces on U10L/U15R and one tiny but nonzero band10 profile2 triangle. This is numerical cleanup only;34 inherited non-column crossing objects remain and no global clean-geometry claim is made.

Isolated `study.blend`, `audit.json` and `proof.py` are included. No canonical scene saved and no GPU render performed. Final156 native-ink render remains root verification. Module is frozen for integration.
