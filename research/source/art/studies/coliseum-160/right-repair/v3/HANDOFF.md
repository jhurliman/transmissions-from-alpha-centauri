# U15R V3: explicit masonry-step domains — held

One bounded candidate used eight pre112 masonry-step domains and exact paired corner vertices, with constrained edges separating adjacent domains. This avoids the V2 whole-profile correspondence. The same13 source corner-fan faces are the only additional skin exceptions.

Protected triangle loss remains zero across1120 faces; candidate topology is closed and has no zero-area faces. However, strict float64 validation finds81 crossings:16 preserved/reconstructed and65 reconstructed/reconstructed. New return vertices deviate at most0.163071m from the old surface; retained vertices do not move.

This fails the required zero-crossing gate. Candidate.blend is diagnostic only. No GPU render or integration was requested. U10L,161guard and retained scenes are unchanged.

The prescribed piecewise construction alone is insufficient. Further subdivisions or tolerance relaxation must not be used to mask this. Pause pending a different solid-domain construction strategy; do not present fewer source crossings as success. Exact pairs/world triangles are in shape-audit.json and explicit domain anchors in strip-candidate-audit.json.
