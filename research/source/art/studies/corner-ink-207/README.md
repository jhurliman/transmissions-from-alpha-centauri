# 207 — upper course native ink visibility

The user reported the remaining upper diagonal course crossing `Building side return.002`. The earlier205 proof started at full-frame y100 and did not include this y26–60 defect.

CPU projected-edge/depth inspection identified the upper panel and adjacent fold edges. The actual native Freestyle capture proves that the offending visible stroke is owned by **145 Panel 03 impact**, distinct from the three205 lower-course owners.207 suppressed136 native segments from that shape after checking both endpoints and midpoint against the actual side-return BVH. Recorded representative hidden depths are approximately0.35–0.90m, safely beyond the0.02m threshold. Adjacent upper fold/sheet edges have the same CPU-proven occluder relationship and are guarded conservatively; they produced no additional hidden-segment changes in this native proof.

`architecture_ink_visibility_207.apply(scene, embed=True)` adds an independent guard. Preserve149/156/161/192/205 and install207 after them. Each eligible stroke is resampled at no more than1px spacing before native endpoint/midpoint visibility tests; visible continuation is retained. There is no image-space trimming, image erasure, geometry edit, material edit, global line-width adjustment or scene layout change.

The actual proof (`before-top-native.png` / `after-top-native.png`) covers full-frame[300,0,620,450]. The hidden upper stub is gone; the exposed continuation starts at the corner. `native-strokes.json` records source ownership before207, and `native-guard-audit.json` records hidden segments. `preservation.json` verifies20,501 recursive native objects and603 original material graphs unchanged, including geometry, normals, transforms, instances, camera, lights and render settings.

Root will integrate207 with208 in209 and inspect one full-height corner crop from y0–800, checking all three courses together. The207 module is frozen after this local native proof. No separate207 full scene render is needed.
