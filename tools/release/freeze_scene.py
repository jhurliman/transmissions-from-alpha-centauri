"""Freeze approved 258 without altering its source or visual content."""
import bpy, json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
D=R/'releases/v1.0.0'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/crack-lift-258/scene.blend'))
assert not bpy.data.libraries
for im in bpy.data.images:
    if im.source == 'FILE':
        assert im.packed_file or im.packed_files, im.name
        im.filepath='//packed/'+Path(im.filepath).name
    elif im.source not in {'VIEWER','GENERATED'}:
        raise RuntimeError('Unsupported external image: '+im.name)
for t in bpy.data.texts:
    t.use_module=False
s=bpy.context.scene
s.render.filepath='//output/main-4k.png'
s.render.use_border=False
s.render.use_crop_to_border=False
bpy.ops.wm.save_as_mainfile(filepath=str(D/'scene.blend'))
