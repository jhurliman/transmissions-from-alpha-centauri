#134 editable centerpiece study

Source: standalone/scene.blend, a primary-scene-identical copy of133 with obsolete linked scenes removed.

Build from the repository root with Blender5.2.1:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/coliseum_integration_134.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/coliseum_integration_134.py -- render
python3 tools/publish_coliseum_134.py
```

The recipe applies two proven pre-layout tessellation repairs, one unique connected crown reconstruction, then weathering at strength1.0. Each module uses deterministic coordinates/settings; no random runtime sampling is introduced. Configs: config/coliseum-134.json, config/coliseum-weathering-134.json, fracture handoff. Weathering construction currently reads the versioned114 original transform; the saved scene and kit contain the resulting native materials and need no linked scene.

Outputs: scene.blend, kit.blend, main-4k.png, generation.json, preservation.json, performance.json, matched crops and review134. Fracture clay comparisons are in fracture/. Actual references are in analysis/independent/.

Limits: this is a localized improvement, not a finished whole-landmark topology certificate or final user-approved lock. See completion audit and independent reviews. Damaged surfaces elsewhere still contain inherited within-component folds.
