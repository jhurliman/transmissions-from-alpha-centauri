# Sheet-metal damage specimen

Iteration 047 develops one right-side ground-level bay. Approval applies to 046; 047 remains a candidate until reviewed by the user.

- Retain the building's existing coating shader. Append independent, panel-local masks for seam loss and fastener corrosion.
- Keep most seams intact. Use interrupted chip clusters with two scales of variation, restricted to selected edges.
- A bent corner needs attachment logic: retain nearby fixings, omit the fixing at the lifted corner, and cut an empty bore.
- Model thin sheet and folded returns as continuous geometry. Split the surface at the exact crease before deformation so the bend does not inherit grid-shaped shading artifacts.
- Move the return with the face. Keep the rest of the panel attached and planar.
- Use short, narrow gravity-directed stains anchored to actual fixing coordinates. Never distribute rust trails independently of hardware.
- Do not use concrete-style cavities or random fracture lines on intact sheet metal. Later variants may use tears beginning at a bore or an edge, with separate topology and attachment checks.

Specimen values: lower tray 6 mm thick, maximum corner displacement 85 mm, seven captive fixings and one empty bore across the two-panel bay. These are art-directed prototype dimensions, not construction specifications.

Validation: matching native before/after cameras, corner closeup, fixed game camera and grayscale comparison. Source and geometry audits live with the iteration.
