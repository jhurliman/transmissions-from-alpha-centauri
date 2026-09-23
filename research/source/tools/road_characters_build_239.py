import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/road-characters-239';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rubble-variation-237/scene.blend'));s=bpy.context.scene
from character_shadows_239 import apply
shadow=apply(s)
(O/'shadow-audit.json').write_text(json.dumps(shadow,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'shadow-test.blend'))
s.render.use_freestyle=False
for vl in s.view_layers:
 if vl.name!='ViewLayer':vl.use=False
s.render.resolution_percentage=100;s.render.filepath=str(O/'shadow-test.png');bpy.ops.render.render(write_still=True)
