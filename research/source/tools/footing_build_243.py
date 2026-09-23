import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/footing-243';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/final-geometry-242/scene.blend'))
from footing_revision_243 import apply
r=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
