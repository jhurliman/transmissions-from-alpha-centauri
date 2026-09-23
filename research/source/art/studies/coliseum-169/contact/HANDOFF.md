#169 scoped native contact correction — frozen for root review

Apply `tools/coliseum_contact_clip_169.py::apply(C)` to the saved168 scene. It validates the original GP attribute digest and every recorded removal sample against current evaluated nearby solid geometry, copies only the named GP data, and preserves all1931 unrelated strokes exactly. The immutable payload lives beside this handoff. No source scene was changed.

15 original strokes contain16 unsupported intervals. Seven supported runs remain; total1946→1938 strokes.1378 native samples verify that removed ink had original166 support within2cm and has no current solid within3cm. Candidate sampling is at most2.5cm; transitions use22 bisections. The stricter all-solid check preserves contacts that still have neighboring support. No global thinning, new outlines, raster masks, or changed widths.

The helper handles only the proven167 loss. It does not repair unrelated inherited contact ink. Original bake code is `intersection_ink_095.py`, last reconstructed by `coliseum_finalize_129.py` and subsequently clipped by `coliseum_ink_occlusion_110.py`. The complete GP attribute hash is identical in129,166,167 before this correction. The object is only in the root Scene Collection, so portable kit export must explicitly include it.

Inspect `comparison-3x.png` and native `before.png` / `after.png`: the stale projecting collar/rib outline disappears from the cavity. The valid nearby ledges and the inherited arch-crown backing remain. This local matched crop uses actual168 geometry/materials/light and visible native GP, with Freestyle off. Root still must inspect the final full native-ink render; no user approval or global95 claim is implied.

Evidence: `correction-audit.json`, `clip-summary.json`, `clip-payload.json`, `all-solid-support.json`, `support-diagnosis.json`, and `provenance.json`. Corrected isolated scene: `corrected-study.blend`. Frozen167 geometry and all canonical scenes remain untouched.

## Additive certification

The frozen16 removed intervals are now covered continuously, not just by discrete support samples.174 original straight pieces subdivide to214 leaves. For each leaf, midpoint-to-nearest-solid distance minus half its world length minus a0.1mm numerical margin exceeds20mm; the minimum certified bound is21.0693mm. Exact endpoints and clip payload are unchanged. `continuous-support-certificate.json` contains every bound. The helper repeats this check against current geometry. `source-transform.json` binds the original GP world matrix to the existing attribute digest; an exact matrix match is now required. This adds no visual or scene changes.
