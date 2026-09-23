# Rear Roger pixel reference analysis

The drawn sprite is approximately **17 ×49 logical pixels** in this scene. The320×200 logical display occupies about1024×768 capture pixels:3.2× horizontally and3.84× vertically, giving the classic1.2 pixel-height correction. Pixel-edge periodicity independently supports this. A correct integer preview can scale5× horizontally and6× vertically. Original cel canvas dimensions, transparent margins and any in-game depth scaling are not recoverable from this capture.

The file named xenon-opening-cd.png is actually **JPEG**. It is also tagged with a display ICC profile; the enlarged clipboard reference is a separate DisplayP3 screenshot. Thus raw RGB triples are not original indexed-game palette entries. The tightcapture rectangle contains4,938colors includingground, the approximate silhouette mask3,461colors, and523logical center samples still contain400distinct triples.

An exact original sprite-palette count cannot be defended.20–24 deliberatecolors is a reasonable new-art working budget:20cluster representatives approximate the noisy center samples at4.90RGB RMSE;24reduce that to3.86. These are approximation measurements, not evidence that the original sprite used20or24colors.

Artifacts include a tight unresampled capture crop,17×49 center-sampled analyst mask, square-pixel andDOS-aspect inspection enlargements, and a20representative capture-color palette. All remain reference-analysis evidence, not a recovered original resource or a production sprite. The source display profile is retained on the sampled inspection/palette PNGs. See findings.json for exact count scopes and scaling evidence.
