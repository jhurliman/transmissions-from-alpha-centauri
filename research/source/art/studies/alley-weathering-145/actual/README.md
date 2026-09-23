# Actual alley placement145

Import `alley_weathering_placement_145.apply(scene, damage=True)` after opening latest source143. The function imports the current `alley_damage_145` builder at runtime. It returns `panels`, `objects`, JSON-safe `audit`, `ink_cleanup`, and `requires_foreground_ink_refresh`. Panel descriptors contain world-space origin/across/up/normal and native width/height; actual meshes are directly in main-scene collections, suitable for the145 material/detail APIs.

Three factory hosts receive private instance collections. Only their selected face, four returns and eight old screw/slot objects are unlinked from each private instance. Original shared collections and all their objects remain unchanged. No new cavity backing is added: retained backing is92mm behind the front /68mm behind the24mm sheet.

`damage=False` creates clean parameterized replacements for a matched control. Existing services, camera, sky and landmark are untouched. Local old096GP points are muted only at removed surfaces.

Planning command (read-only; no render):
```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/alley_weathering_placement_145.py
```

See placement-validation.json for native14-mesh checks, placement-plan.json for exact dimensions/transforms/projectedbounds, and feature-visibility.json for actual feature-center rays. `geometry-only-placement.blend` is an isolated smoke artifact, not a production integration or material-approved render.
