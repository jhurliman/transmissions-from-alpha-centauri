# 240 lower atmosphere variance study

CPU candidate from the final239 scene. The existing two-scale centered noise field receives7.5× contrast and symmetric saturation at±.94, yielding density factors .06–1.94. The current2.8 global scatter gain and original near-clear/far-dense envelope remain unchanged. Contrast fades back to the original field between worldZ12–25m, preserving the upper landmark. Orange radiance is unchanged. Dense pockets receive only18% muted darker orange pigment; no extra pale emission.

Actual isolated native shader measurement (Cycles CPU, four world-depth planes) reports mean factor .958–.998 and standard deviation .451–.488. At each plane, roughly7–8% of samples exceed1.7 and9–12% fall below.3; these are useful realized pockets, not merely theoretical extrema. Native EXR probes and native-field-probe.json retain the evidence. These are spatial density measurements, not projected opacity or final beauty approval.

No full-scene render was performed in this lane. Root integrates with240 lighting work and checks actual ground-arcade flattening. All geometry, nonhaze materials, lights, world, compositor and ink layers are preserved. Landmark contour/fine-crease lines belong to ViewLayer/192;215 atmosphere-free ink targets distant components and broken walls. If native full proof retains inappropriate ink detail in dense pockets, root should assess a scoped landmark-only attenuation rather than changing global ink.

Replay: tools/haze_variance_240.py::apply(scene). Do not apply twice. Original239 scene/material retained. User approval pending.
