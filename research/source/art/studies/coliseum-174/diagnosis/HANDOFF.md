#174 U4 aperture-head return repair feasibility

The single robust crossing687/711 lies in a hidden rear angular-end cap, radius67.0–68.37 and authoredz73.78–73.99. It is over3.6m above the niche-head bottom and roughly18m behind visibleU4R at the locked camera. It is not the front lintel or opening boundary.

A two-face diagonal flip is numerically sufficient: replace shared edge304–83 of faces711/4612 with1263–82. The four boundary vertices remain fixed; crossing face687 and all other5476 triangles remain unchanged. Full numeric crossing count drops1→0 and all edge incidences remain2. New hidden triangle centroids differ3.76–4.18mm from the old folded surface, so rendered triangle geometry is deliberately different inside this tiny domain even though coordinates are exact.

This is only a read-only array feasibility test, with no Blender mesh creation or scene mutation. Future implementation must first prove raw/evaluated face correspondence, preserve the127 layout modifier, all POINT attributes and every unaffected polygon/corner normal, then rerun native topology and protected-surface checks. Reject rather than widen the domain if the two-face operation cannot pass. No broader170 carving or small fallback is authorized by this proposal.

See repair-domain-proposal.json, head-domain.json, diagonal-feasibility.json and explicit protected-face-ids.json. No GPU render occurred.
