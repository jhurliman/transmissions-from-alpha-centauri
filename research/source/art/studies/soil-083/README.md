# Soil relief 083 — candidate for aesthetic review

A.png, B.png and clay.png prove native mesh relief with different light directions. scene.blend contains the editable physical patch. The hierarchy combines compacted quieter areas, finite tapered ridges, small deposits and several microclod scales.

main.png and main-scene.blend show the same procedural height field transferred through a packed EXR into scene bump shading. This diagnostic does not displace the entire road mesh. Architecture, rocks and the repaired 081 road cracks remain intact. No reference image is projected into the material.

Direct light maps into the calibrated brown palette. A restrained continuous ambient normal response keeps cast shadows brown without the false broad ribbon bands caused by hard palette thresholds. Fine texture remains less readable in distant shadows than the physical closeup.

## Bounded intermediate-scale test

intermediate-A.png and intermediate-shadow.png add 95 sparse clods per 3.8 m patch, radii 2–4 cm and heights 1–3 mm. The original fine grain and palette remain unchanged. At the shadow camera crop, mean absolute RGB change is 0.015/255; only 0.128% of pixels change by more than 1. This produces no useful camera-scale gain, so the baseline remains selected. Higher density or height risks changing compacted soil into pebbled coverage. The variant remains available for comparison, not selected integration.

Detailed settings, scores and remaining limitations are in review.json. This is a candidate, not a final reference-match or user-approval claim.

Independent critic confirmed the baseline decision; shadow visibility score remains 76. The intermediate closeup does not introduce a coarse-pebble regression, but its negligible camera benefit does not justify integration.
