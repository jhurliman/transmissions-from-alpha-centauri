# Native ruined-building bridge study133

Separate unapproved prototype; no primary mutation. API `tools/city_transition_133.py::apply(scene)` is deterministic, additive and requires a fresh source with no133 collection. Current scene source is131; all existing alley, ground, rubble, city, landmark, camera and lights remain unchanged. Later selected132 haze is deliberately not included in this comparison.

## Reference-first findings
Primary: UCL-01 original project artwork (`references/user-coliseum/coliseum.png`), cropped in `UCL01-transition-{left,right,whole}.png`. Supporting older selected-third composition also cropped. UCL-02 and DP-03 support architectural erosion/scale. See `reference-analysis.json` and `reference-entries.json` (for root manifest merge; shared manifest not edited).

Native alley ends at y32m; nearest approved towers begin y48m. Reference bridges this gap with connected broken wall/floor fabric and variable-height stumps that overlap taller tower bases. It does not bridge it with only stones or uniformly spaced skyscrapers.

## Construction
Six roofless L-shell remnants occupy y33.4–49.6m, heights2.7–7.4m. Actual thick closed wall meshes have broken crown profiles and Boolean window voids; surviving floors connect to wall edges and partial ribs; fallen floor plates contact ground/walls. Three camera-facing cross-walls counteract the edge-on street-wall silhouette. The central route stays clear; exact closest new vertex is in audit.json. No existing tower moves, no generic pebble layer, no hidden backing panels or image materials. Every new raw mesh passes closed-edge test; this is not a full cross-solid intersection certificate (joined kit pieces intentionally overlap at supports).

Dedicated dusty violet/blue-gray native materials preserve quiet broad face families, dark AO at joints/interiors, restrained pigment and sparse warm exposed fracture faces. First pale inherited-material prototype preserved as `after-v1-pale.png`; intermediate street-parallel silhouette preserved as `after-v2-parallel.png`.

## Proof pipeline
`before.png`/`after.png` are matched1440×1082 scene-camera renders. `before-transition.png`/`after-transition.png` are enlarged crops of those renders, not new camera views. Current proof disables compositing and enables all primary native Freestyle linesets; no stale linked128 foreground-ink overlay can overdraw new structures. Saved scene uses these explicit proof settings. Primary integration must regenerate appropriate current-geometry foreground ink; do not assume the130 sync helper adds geometry (it only synchronizes render dimensions/border/line thickness).

This is a bounded architectural-placement prototype, not a claim that ruined-building fracture fidelity is finished. Existing far-city body destruction and small-scale breach detail remain separate possible work.

## Final inspection
Independent critic finds no blocker for this bounded composition/geometry pass: broad blue-gray facades and feet buried in existing rubble bridge the transition while preserving open street. Middle-left face remains plain; straight fracture outlines and obscured lower apertures remain detail gaps.57 closed raw meshes; measured clear central width11.8m. Ready for user review, not approved final fidelity.
