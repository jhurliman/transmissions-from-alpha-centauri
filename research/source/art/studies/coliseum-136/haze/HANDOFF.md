# Haze 136

Apply `tools/coliseum_haze_136.py::apply(scene)` once to a scene descending from 134. Default D is recommended. Only the dust-volume material assignment changes; geometry and all other materials are untouched. No image overlay is used.

D reduces neutral scattering to 25%, warms scatter color, and adds a native orange atmospheric radiance field rising from zero at Y48 to full at Y205. The source fades from Z2 to zero at Z29. Existing density-gradient spatial shape is retained.

The four diagnostic variants and baseline are 1440×1082 without Freestyle for matched comparisons. Production `main-4k.png` retains native Freestyle and is 3840×2885. The full scene is editable in `scene.blend`.

The reference's broken low city skyline exposes many more orange gaps; this haze pass deliberately does not reshape accepted city geometry. The emissive volume is an artistic approximation of unresolved warm atmospheric lighting. D is an agent recommendation, not user approval.
