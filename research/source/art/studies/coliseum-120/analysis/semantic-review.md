# Low-variation regions: visual interpretation

The detector measures local color variation, not artistic quality. The geometry mask excludes sky and foreground. In the 119 baseline, 35.9% of visible landmark pixels fall below the local contrast threshold, but only 554 pixels belong to exactly constant 3×3 neighborhoods.

## Highest-value changes

- Long projecting tower faces (regions13,23,10): broad smooth strips dominate their silhouette. Future detail should be shallow architectural channels, interrupted masonry joints and localized wear.
- Upper wall fields (regions8,14,18): the central damaged bay now has relief, but nearby panels retain simpler surfaces. Extend architectural variation selectively rather than distributing identical random scars.
- Continuous cornice undersides: repeated supported blocks are the current response. These add real shadow and depth at the main camera.
- Exposed broken core faces: keep the broad damage path and add validated shallow relief. Reject self-intersecting microgeometry.

## Quiet regions to preserve

The largest components (including regions1,2,4,6) often lie inside arch returns. They are intentionally darker and should retain broad painted color. The user-selected lighter front half/darker rear half gives these surfaces depth without blanket grain. Do not use the analysis fraction as an optimization target or claim that all low-variation pixels are defects.
