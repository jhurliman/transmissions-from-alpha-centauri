# Concrete support damage family

Approved visual basis: iteration 045 (user approval after review). Iteration 046 tests sparse placement and separate material wear; its render is pending user review.

## Assembly rules

- Keep the clean support master. Damage lives in a per-instance collection with editable Boolean cutters and recessed crack interiors.
- Use an authored hierarchy: a few primary spalls, smaller corner losses, and short connected fracture paths. Do not scatter cracks independently across the whole surface.
- Crack destinations must be explicit: real component edges or spall cavities. Shift destinations and their associated cavities together.
- High-frequency bounded walks add jaggedness between destinations. Closed ribbon cutters avoid self-intersection from tightly bent tube cutters.
- Translate damage along the sloped surface (equal local Y and Z displacement). Mirror across the width when useful. Do not stretch the support geometry to vary damage.
- Keep adjacent quiet instances: the first distribution damages three of five supports, including a low-severity member next to a clean one. This is an authored placement decision, not a universal 60% damage target.
- Preserve bearing heads and feet. Audit evaluated concrete for one connected component, no non-manifold edges, and positive volume. These checks verify mesh integrity, not structural engineering.

## Separate processes

Concrete runoff begins beneath the bearing joint and fades downward. Pipe corrosion stays near declared joints; occasional exposed steel has lower roughness and higher metallic response than rust. Do not reuse the facade coating mask on services.

## Review at two scales

Use closeups to assess crack endpoints, cavity depth, corner continuity, and material response. Use the fixed alley camera and grayscale toggle to assess restraint and repeated motifs. Clean masters, source scripts, baked beam collections and audits remain alongside the saved iterations.

Current limitation: mirrored/translated motifs are an initial distribution test. Larger deployments need more seeded path and spall variants; do not repeat this small catalog across every facade.
