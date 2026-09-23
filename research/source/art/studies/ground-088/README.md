# 088 · Packed soil geometry

User direction: preserve C's relative broad relief with A's mean elevation; remove separate road rocks during heightfield development. Work on convincing native dirt geometry before stylization.

## Placement correction

`scene.blend` keeps the alley intact and hides the road scatter objects. `datum-audit.json` records the sampled means and hidden object names. The recentering subtracts 9.7396 mm inside the road, smoothly fading at the boundary. It preserves interior slopes and height differences rather than scaling their amplitude.

## Geometry study

`detail-scene.blend` is a separate neutral-clay packed soil surface, not yet integrated throughout the alley. The mesh uses a 7.5 mm sample spacing over 6 × 6 m. The procedural model combines macro relief, compressed pockets, shallow connected accumulation ridges, embedded aggregate and small depressions. These are modeling rules inspired by soil processes, not a calibrated physical simulation.

References: US-01 / US-02 in the project's user soil collection, DP-08 by Darius Puia / BakaArts, and [Gravel Road](https://polyhaven.com/a/gravel_road) by Amal Kumar / Poly Haven (CC0). The external scan is a benchmark for real compacted surface structure, not imported scene geometry. No reference image is projected onto the study.

The separate critic's findings and revised evaluation are in `critic.json`; no agent assessment constitutes user approval.
