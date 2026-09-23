#138 native delivery and reproduction

This is the current integrated study, not a final approved or globally clean landmark. Fresh138 critique scores95/95/90/91/93/94; final user approval is absent. See `delivery-audit.json`, `critic.json`, and the root completion audit for remaining requirements.

## Open and inspect

`scene.blend` is a standalone full scene. `kit.blend` is a native collection library: append **110 Coliseum detailed front ruin** into a Blender scene. Opening the kit directly may show an empty default scene because the collection is not a scene; that is expected, not a missing asset.

Fresh reopen checks found no actual linked datablocks in138 scene,138 kit or135 kit-proof scene. The fullscene's nine file-backed pigment images are packed; all recorded source paths also exist. The kit has no file-image dependencies. Saved native outputs do not need the historical build inputs below to open or render.

All3533 landmark objects in the138 kit and saved135 kit-proof scene exactly match138 main in evaluated mesh positions/topology/material indices/corner normals, world transforms and material assignments. Therefore the four existing135 kit proofs remain applicable to the landmark:

- `../coliseum-135/kit-proof/bay-tower-painted.png`
- `../coliseum-135/kit-proof/bay-tower-clay.png`
- `../coliseum-135/kit-proof/crown-painted.png`
- `../coliseum-135/kit-proof/crown-clay.png`

Those isolated proofs omit environmental geometry and atmosphere. Use138 `main-4k.png`, `after-street.png` and `after-rust.png` for the current haze and alley material changes.

## Reproduce current output

Run from the repository root using Blender5.2.1. The following commands overwrite the versioned study outputs; they are documented here, not executed by the delivery audit.

```sh
cd /PATH/TO/transmissions-from-alpha-centauri
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/scene_integration_138.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/scene_integration_138.py -- render
python3 tools/publish_scene_138.py
```

The builder always starts from135, applies136E atmosphere and137 private bolt/seam-led rust materials, then saves138 scene/kit and preservation/generation reports. The render command freshly opens saved138 and writes3840×2885 at line thickness3840/1440. Recorded138 full-render time is113.85seconds on the current host; this is not a performance guarantee. The builder uses fixed136 parameters and seed137 for rust anchors. It rejects unexpected object/geometry/normal/light/camera/transform changes and changes to existing material graphs.

Required direct inputs: `art/studies/coliseum-135/scene.blend`, `tools/scene_integration_138.py`, `tools/coliseum_haze_136.py`, and `tools/alley_rust_137.py`. `config/scene-studies-138.json` records intent; effective parameters are the versioned code and `generation.json`.

## Rebuild135 source when necessary

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/coliseum_integration_135.py
```

This starts from `art/studies/coliseum-134/scene.blend`, applies frozen135 fracture **v2** and strength1.0 broken-cornice weathering, and saves135 scene/kit. It does not use the rejected fracture/v1 candidate. Additional construction dependencies are:

- `tools/coliseum_fracture_135.py`, `tools/coliseum_weathering_135.py`
- `tools/coliseum_arch_ratio_125.py` (coordinate mapping)
- `tools/coliseum_crown_repair_123.py` (strict crossing checks)
- `config/coliseum-weathering-135.json`
- `art/studies/coliseum-114/scene.blend` (mapping anchor)
- `art/studies/coliseum-perspective-115/E/audit.json` (exact affine transform)
- `art/studies/coliseum-116/generation-settings.json` (yaw transform)

These historical paths are construction inputs, not live links in the delivered138 files. Rebuilding134 and earlier history is a separate dependency chain; see134/README.md. This recipe is a deterministic incremental reproduction from the recorded134/135 baselines, not a claim that one script regenerates every alley asset from nothing.

## Recheck delivery or regenerate isolated kit proofs

The audit command opens the files, evaluates the landmark in memory and writes only its JSON report. It does not save or modify any scene/kit:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/coliseum_delivery_audit_138.py
```

To make new138-specific isolated proofs from the unchanged current kit:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/coliseum_kit_proof.py -- scene-details-138
```

That command appends the kit into a fresh empty scene, verifies native equivalence, appends the source camera/lights/world, and renders four matched painted/clay crops. It creates138/kit-proof outputs; it does not modify138 main scene or kit.

## Limits that remain

There are36 non-column objects with inherited within-component crossing findings, plus54 previously classified column assembly overlaps.135's three repaired walls are clean under their local raw/evaluated checks; this does not certify the whole landmark. Current139 triangulation probes were rejected and saved no scene changes: U9head remains80crossings, U9R trial still2, U10head156with2zero-area faces. See139/triangulation-probes.json.

Full contact/support/normal validation remains partial. Existing linked intact meshes are documented, but transformed-shape sharing opportunities are not exhaustively resolved. Current critic's remaining scene-scale damage/surface/integration/linework gaps and final user approval remain delivery gates. No new general LOD system is claimed or required by this audit.
