import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/awning-runoff-251';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/base-weather-249/scene.blend'));s=bpy.context.scene
from awning_runoff_251 import apply
a=apply(s);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
