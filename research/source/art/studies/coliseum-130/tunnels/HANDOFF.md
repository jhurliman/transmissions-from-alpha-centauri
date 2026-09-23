# Editable ground-level tunnels

Frozen module: `tools/coliseum_tunnels_130.py`, `apply(C, length=30., bend_radius=6., outlet_length=5., wall_thickness=.65, roof_extra=.65)`. Apply once to the corrected129 collection; returns an audit dictionary. Adds two meshes and two copied native materials only.

T0 B8 and B9 attach to their exact evaluated rear arch curves. Their floor elevations match the actual doubled platform top (authored4.58062m; world approximately2.49m). The existing platform cap extends to authored radius66.90m, beyond the rear wall at67m, so the new floor overlaps the existing threshold. The first shell station embeds0.12m into the rear connection.

Parallel +Y paths avoid converging facade normals. Each has30m straight travel, a6m-radius outward90degree bend, and5m open exit:44.42478m total centerline. Both end cross-sections remain open; no caps, backdrop planes or new lights. A further0.65m of outer roof mass at the crown blocks the last three upper B7sliver rays while retaining the exact inner section.

Checks: zero nonmanifold edges on both solids; positive volume; no overlap pairs between the two tunnel meshes; open entrance/bend and exit rays; all127/4720/2697 baseline-visible sky pixel rays for B7/B8/B9 blocked at native4K sampling. This pixel test is specific to the locked camera and selected baseline-sky regions.

Native original-position and actual arch-depth attributes remain populated. Materials are copied from existing rear-return and platform materials; source graphs unchanged. Main-camera crop is a geometry/material proof with old landmark contact ink hidden and Freestyle disabled. Integration must regenerate landmark ink. Current lighting is the existing native shader response, not a claim of physically simulated indirect bounce.

Proofs: `main-crop.png`, `geometry.png`, `top.png`, `open-exits.png`; audits: `audit.json`, `sightlines.json`, `geometry-validation.json`.
