#152 native preflight for final156 integration

Read-only CPU audit; no scene or canonical material writes and no render.

- 3,527 current mesh objects. 54 intentionally assembled round columns are exactly unchanged since135 and separately excluded.
- 3,464 non-column evaluated meshes/world transforms exactly match135 SHA256 signatures. Nine changed meshes were freshly tested, all with zero strict crossings.
- 34 inherited non-column objects still contain2,229 strict triangle-crossing pairs. These are not a clean whole-landmark certificate. Current visibility is not inferred from old135 camera samples.
- Eight raw issue objects contain349 faces below1e-10 local square units;348 are below1e-14. Every in-memory face-only deletion trial introduces boundary/nonmanifold edges. Do not remove these faces blindly. Safe repair needs local edge/vertex reconstruction followed by topology, preservation and native render checks.

## Remaining crossing objects

- COL110 T2 band07 profile4: 4 pairs (unchanged135 geometry).
- COL110 T2 band10 profile0: 2 pairs (unchanged135 geometry).
- COL110 T2 band10 profile1: 7 pairs (unchanged135 geometry).
- COL110 T2 band10 profile2: 4 pairs (unchanged135 geometry).
- COL110 T2 band10 profile3: 3 pairs (unchanged135 geometry).
- COL110 T2 band10 profile4: 6 pairs (unchanged135 geometry).
- COL110 U0 fractured upper wall R: 11 pairs (unchanged135 geometry).
- COL110 U1 fractured upper wall L: 13 pairs (unchanged135 geometry).
- COL110 U1 aperture head: 10 pairs (unchanged135 geometry).
- COL110 U2 fractured upper wall L: 20 pairs (unchanged135 geometry).
- COL110 U2 aperture head: 13 pairs (unchanged135 geometry).
- COL110 U3 fractured upper wall R: 10 pairs (unchanged135 geometry).
- COL110 U3 aperture head: 20 pairs (unchanged135 geometry).
- COL110 U4 aperture head: 1 pairs (unchanged135 geometry).
- COL110 U6 fractured upper wall L: 13 pairs (unchanged135 geometry).
- COL110 U6 aperture head: 15 pairs (unchanged135 geometry).
- COL110 U7 fractured upper wall L: 2 pairs (unchanged135 geometry).
- COL110 U7 aperture head: 20 pairs (unchanged135 geometry).
- COL110 U8 aperture head: 10 pairs (unchanged135 geometry).
- COL110 U10 fractured upper wall L: 292 pairs (unchanged135 geometry).
- COL110 U10 aperture head: 156 pairs (unchanged135 geometry).
- COL110 U11 aperture head: 6 pairs (unchanged135 geometry).
- COL110 U12 fractured upper wall L: 9 pairs (unchanged135 geometry).
- COL110 U12 aperture head: 39 pairs (unchanged135 geometry).
- COL110 U13 fractured upper wall L: 6 pairs (unchanged135 geometry).
- COL110 U14 fractured upper wall R: 61 pairs (unchanged135 geometry).
- COL110 U14 aperture head: 24 pairs (unchanged135 geometry).
- COL110 U15 fractured upper wall R: 1323 pairs (unchanged135 geometry).
- COL110 U15 aperture head: 10 pairs (unchanged135 geometry).
- COL110 U16 aperture head: 14 pairs (unchanged135 geometry).
- COL110 U17 aperture head: 8 pairs (unchanged135 geometry).
- COL110 Tower4 broken crown: 4 pairs (unchanged135 geometry).
- COL110 Tower7 broken crown: 51 pairs (unchanged135 geometry).
- COL110 Tower13 broken crown: 42 pairs (unchanged135 geometry).

## Tiny/collapsed-face cleanup evidence

- COL110 T2 band10 profile2: 1 faces; deleting only faces changes boundary edges 0→3, nonmanifold edges 0→3.
- COL110 U3 fractured upper wall R: 2 faces; deleting only faces changes boundary edges 0→4, nonmanifold edges 0→5.
- COL110 U10 fractured upper wall L: 101 faces; deleting only faces changes boundary edges 0→83, nonmanifold edges 0→193.
- COL110 U10 aperture head: 2 faces; deleting only faces changes boundary edges 0→4, nonmanifold edges 0→5.
- COL110 U14 fractured upper wall R: 2 faces; deleting only faces changes boundary edges 0→4, nonmanifold edges 0→5.
- COL110 U15 fractured upper wall R: 233 faces; deleting only faces changes boundary edges 0→315, nonmanifold edges 0→507.
- COL110 Tower7 broken crown: 4 faces; deleting only faces changes boundary edges 0→4, nonmanifold edges 0→8.
- COL110 Tower13 broken crown: 4 faces; deleting only faces changes boundary edges 0→4, nonmanifold edges 0→8.

## Final-delivery gaps beyond scores

- Resolve or explicitly disposition34 remaining inherited non-column strict crossing objects and8 raw collapsed/tiny-face issue objects; local clean patches do not establish global clean geometry.
- Whole-landmark contact/support/floating fragment and evaluated-normal review remains partial. Strict self-crossings do not validate these.
- Fresh final main-camera clay/untextured view and final matched bay/tower/crown/flat-wall comparisons must reflect the delivered revision;152 contains grayscale but no current full-clay artifact. Older sample proofs establish only their historical state.
- Refresh final scene/kit, fresh-reopen dependency/evaluated equality checks, full4K render, reference comparisons and preservation after pending153–155 integration. Current152 certificates do not automatically cover later edits.
- Consolidate final deterministic settings and required historical input assets in a final reproduction manifest. Current documented incremental build is real; a clean build from nothing is not demonstrated and must not be implied.
- Final user approval of integrated centerpiece before marking locked.

## Already verified — avoid stale pending claims

- Native3840x2885 main render and grayscale/before-after comparisons.
- Scene and kit freshly reopened:3533object evaluated geometry/normals/materials/transforms match; no actual linked IDs; nine scene images packed.
- 20,490-entry preservation against150; only authorized2crown meshes and36receiver assignments; unrelated native scene unchanged.
- Outside-landmark pixel difference max2RGB, none over4.
- Incremental reproduction recipe, timing, source references and current review page exist.

The completion-audit document retains historical tables. Its old fresh-reopen/dependency and current-kit concerns are resolved for152 by fresh-native-delivery-check.json; they become new checks only after subsequent integration. No final user approval is present.

Strict helper limitations: shared-vertex and coplanar contacts, near-parallel intersections and tiny penetrations are omitted. Hash reuse proves unchanged geometric inputs, not harmlessness or current visibility.
