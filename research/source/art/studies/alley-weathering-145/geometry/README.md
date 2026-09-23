# 145 editable panel damage pilot

Run from repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --python tools/alley_damage_145.py
```

The builder creates an isolated four-panel row and a separate clean master asset. It does not load or overwrite the production scene. `apply(scene)` returns the study collection, native panel descriptors and clean asset collection. Descriptors use X across, Z up, outward −Y; normalized damage footprints accompany actual panel objects for support ray tests.

See handoff.json for dimensions, reference interpretation, limitations and topology checks. Fastener and weathering studies are separate.
