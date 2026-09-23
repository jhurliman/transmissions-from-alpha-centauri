#154 isolated crown continuation — held prototype

API: `tools/coliseum_crown_continuation_154.py::apply(C)` on local152 landmark collection. Three target names are returned in `targets[].object`. No primary scene was changed.

Native scene and matched painted/clay4K crops are in this folder. `painted-compare-4x.png`, `clay-compare-4x.png` and the true1800-display-size crops show the result. Freestyle and compositor are disabled equally in these proofs. No full render or ink approval is claimed.

**Creator recommendation: hold for shape review.** The broad event is visible, but the single retained plane is still flat and removing the old L front split reduces an existing depth cue. This should not be integrated merely because geometry validation passes.

## Geometry evidence
L/head have zero float64 intersections before/after. R contains five inherited lower-return intersection pairs under an invariant float64 test; every pair is identical in source/candidate. No new intersections. All three remain closed and lose volume. Legacy float32 counts had depended on temporary-object transform updates; diagnostics now use the actual fixed source matrix.

R uses an upper-only Boolean above worldZ48.15; its lower source triangles are reattached unchanged. Native render tessellation is frozen. New exposed faces have `154 Exposed crown core` and existing151 warm/violet material. Classification requires actual cutter-surface membership and >0.5mm offset, preventing retessellated original planes being relabeled. Retained normals are interpolated from the source, original-position data preserved/interpolated.

Maximum accepted numeric outside residual is0.229mm world /0.00296native pixels, below the documented simultaneous0.5mm/.02px budgets. Lower source vertices have zero nearest-surface error.16,441 non-target mesh geometry/material-index/corner-normal hashes are unchanged. This is not a global geometry-clean certificate.

`float64-source.json` and `float64-candidate.json` retain the inherited issue evidence; `legacy-float32-identical-pairs.json` records the misleading old test. Historical `*-failure.json` artifacts describe rejected attempts, not the saved candidate.
