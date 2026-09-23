# 195 — first-building weathering, feathered beam rust, visible plate runoff

Integrated over192's native ink repairs. Source geometry, normals, transforms, lighting and camera remain unchanged. Weathering uses private editable materials and attached surface-fitted pigment geometry. All preexisting material graphs remain intact.

-193: moderate wear across104 first-left-building/portal-post pieces; fullXYZ mapping prevents height-only banding.
-194: inward-pointing fine rust bristles grouped into uneven edge-rooted brush swathes.
-193 service contrast: lighter slate backing separates cable loops; rightY rust contribution multiplied by0.5 only.
-195 runoff: wider translucent faceplate water stains around selected bolt seats, with tapered short tails.135 selected plate heads across42 assemblies retain the previous80% selection policy. Old192 runoff is retained but hidden;189 heavy washes remain.
-192 ink: pigment geometry is absent from the matching native ink view layer. Specific covered backing/fold edges are hidden behind the actual side return. No old rendered image is overlaid.

`held-v1/` preserves the rejected first combined render: too-regular beam teeth, horizontal wall banding and under-visible ordinary runoff. The final pass addresses each directly.

Native full render: run `tools/scene_weathering_build_195.py -- render` in Blender. The source file embeds the native visibility guards. Publication crops come from the full render via `tools/publish_scene_weathering_195.py`.

The Colosseum crumbling study remains separate at review190. User approval is not implied by internal reviews.
