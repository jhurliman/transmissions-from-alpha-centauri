import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/rubble-transition-236';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rubble-extension-236/scene.blend'))
from rubble_depth_finish_236 import apply
s=bpy.context.scene;a=apply(s);(O/'finish-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
print('236 INTEGRATION SAVED',flush=True)
