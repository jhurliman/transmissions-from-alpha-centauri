# 091 — visible rock distribution and painted facets

User accepted 090 geometry and requested reference-counted placement plus the supplied warm-top / dark-side art style.

Reference counting is an independent manual estimate of recognizable silhouettes at least four pixels wide at 1448 × 1086. It is not automated segmentation. Road: 120 (90–150 plausible); foundation banks: 240 (180–300 plausible). Subpixel grit, foreground scrap, distant rubble excluded. See count-reference.json for depth and size targets. Original source credits remain in references/manifest.json; UR-01 is the new user-supplied closeup.

The first candidate exposed a world-space sampling bias: 82/120 road stones fell in image y500–599 and only two in y800–899. The second candidate enforces screen-depth quotas 20/48/52 on the road. Bank quotas were adapted to 85/147/8 because the existing narrow foreground apron leaves very little visible area at the near threshold. Candidate visibility uses native scene ray queries; this does not claim every final shaded silhouette remains distinguishable. The bank source favors the right side and uneven depth clusters. Large fragments tilt; smaller fragments remain embedded.

Native materials use sun-direction face bands, medium-scale pigment islands, and narrow bevel faces with selective light tones. Terrain-conforming transparent contact accents provide deliberate painted contact darkening; they are not a claim of ray-traced specular lighting. No reference image is projected onto the scene. Soil geometry, architectural materials, sky and scrap stay fixed.

Pipeline: tools/rocks_091.py → tools/publish_rocks_091.py. scene.blend retains editable masters/materials and placement. First-main.png and first-detail.png preserve the rejected internal first candidate. User review remains pending.
