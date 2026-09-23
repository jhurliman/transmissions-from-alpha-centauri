# Alley panel weathering system 145

A reusable native component study based on the creator's original alley reference. Production scene143 is the preserved baseline. The study is not a final95/100 claim or user-approved lock.

The system separates scales and causes:

- A fixed spatial roughness field controls how the actual warm key is picked up. Two connected broad regions lead; restrained medium detail breaks their boundaries. Moving the key changes the response, while aging coordinates remain fixed.
- Damage variants are editable mesh geometry: an edge-connected missing chunk, two unequal closed-bottom pits, a deeper impact aperture, and a finite tapered dark crack. Folded returns and backing are explicit.
- Hardware starts from plausible panel-corner candidates. Approximately70% are occupied after checking that surviving facing supports each washer. Corrosion originates at those anchors and selected upper edges.
- Rust uses compact dark contact stains, unequal fine rain trails, and a few broad runs tapering downward. Sparse ink dots and selected larger marks remain subordinate.

## Native components

`tools/alley_panel_material_145.py::make_panel_material` constructs the light-responsive material with an explicit origin, across/up basis and span.

`tools/alley_damage_145.py::apply` returns a damaged component collection, panel descriptors and a separate clean master asset. Damage is baked into editable mesh variants; the clean master is retained independently.

`tools/alley_surface_details_145.py::apply_panels` creates optional fastener and microink collections and private material layers. Corrosion can be disabled with its group Strength control. No painted reference image is projected on the model.

## Review evidence

- `geometry/`: damage geometry and neutral clay, dimensions and mesh validation.
- `material/`: same-camera moved-key and cool-fill controls. Earlier rejected mask versions are retained in version folders.
- `details/`: matched corrosion/fastener studies and supported-anchor audit.
- `combined/`: combined native4K component proof, clean control, clay and editable kit.
- `actual/`: controlled placement in a copy of scene143; game-camera review remains required.

The reference is a painted image, so roughness, pigment and illumination cannot be uniquely recovered from it. The material is a tested native interpretation. Small ink accents are surface marks, not certified physical recesses. A clean individual-mesh topology check does not certify every possible assembly contact.

UCL-01 is original work by the project creator, made using ChatGPT Images2.5. Additional registered surface/infrastructure references retain their existing provenance. See the configuration and independent reference analysis for studied properties.
