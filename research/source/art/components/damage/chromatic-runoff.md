# Chromatic runoff layer

Iteration 048 studies the user's reference observation: vertical weathering reads as color differences, not black line art.

## Visual hierarchy

- Cluster trails beneath selected seams and bearing edges; leave quiet gaps between clusters.
- Mix long faint washes with shorter stronger streaks. Use unequal lengths and widths within each group.
- Keep paths almost vertical. Tiny lateral wandering and fine width variation prevent ruler-straight stripes.
- Allow a small number of coherent paths to continue across a panel seam. Avoid resetting the pattern at every component boundary.
- Change tint against the local coating: warm over cool, cool over warm; use a darker version of the local color for a separate subset.
- Do not replace these trails with black curves or apply the facade's broad paint-flaking system to services.

## Native implementation

The 048 node group takes the existing base color, world position and a strength value. It contains 20 finite paths, with declared sources at the bay's upper edge or horizontal seam. Its horizontal mapping is currently calibrated to the right gallery at world Y=11.6. Reposition that mapping and its source heights for another facade; do not stamp these exact coordinates everywhere.

The shared world-position mask lets trails cross the selected panels without a UV reset. Only two facade materials receive the new layer. Geometry, roughness, approved seam chips and earlier support/service treatments remain intact.

This is art-directed surface weathering, not a fluid simulation. The exact pattern remains a visual-review candidate until the user approves it.
