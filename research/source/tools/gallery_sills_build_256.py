import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/gallery-sills-256'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/duct-infill-255/scene.blend'));s=bpy.context.scene
from gallery_sills_256 import apply
(O/'audit.json').write_text(json.dumps(apply(s),indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
