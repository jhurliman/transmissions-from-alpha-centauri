# Bounded numerical-degeneracy cleanup feasibility

Five objects support a conservative follow-up proof: U3 fractured upper wall R, U10 aperture head, U14 fractured upper wall R, Tower7 broken crown and Tower13 broken crown. Component-restricted dissolve-degenerate at1µm world-equivalent tolerance removes14 true zero-area faces total. Every nonzero source triangle remains coordinate-identical; no vertex moves;115 material coordinates remain exact; closure/orientation and raw crossing counts are unchanged. This cleans numerical faces only, not inherited folds.

Custom corner normals are not automatically guaranteed by BMesh conversion. Source face/vertex lineage survives, so each remaining corner can recover its original normal by source-face and source-corner correspondence. A next isolated proof must restore these, verify evaluated modifier output/attributes, and compare a native render before integration.

Three objects do not pass the bounded approach:

- T2 band10 profile2: one tiny nonzero face remains unchanged at1µm and10µm. No arbitrary larger tolerance was tried. It is a slender triangle, not an exactly duplicate face that can simply be dropped.
- U10 fractured upper wall L: simple merges produce49–59 nonmanifold edges. Dissolve at1µm leaves2 tiny faces and increases raw crossings327→334;10µm closes/removes degeneracies but perturbs surviving triangles, with about46µm vertex motion and changed normals/material coordinates. It is not an exact cleanup certificate. Existing folds require dedicated local repair rather than a blind merge.
- U15 fractured upper wall R: merges produce22–24 nonmanifold edges. Dissolve leaves9/2 tiny faces at1/10µm and produces large local face-normal changes (up to125° in this raw lineage comparison). Increasing tolerance is not justified; degeneracies are entangled with folded return topology.

The numerical surface-distance control matters: untouched source→itself BVH distances already reach3mm around degenerate/sliver triangles. These are not claimed geometry motion. Exact surviving triangle-coordinate sets prove the five conservative candidates; the audit retains both measures. Neither global fold repair nor render preservation is claimed.

Only temporary in-memory meshes were made. No scene, primary geometry or materials were written; no render was performed. Full per-trial evidence is in degenerate-cleanup-feasibility.json.
