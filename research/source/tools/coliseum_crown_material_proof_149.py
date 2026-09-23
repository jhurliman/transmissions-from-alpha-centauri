import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-149/material';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-149/geometry/scene.blend'));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
from coliseum_crown_material_149 import apply
result=apply(C);s.render.use_freestyle=True;s.render.use_compositing=False
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'after.png');t=time.time();bpy.ops.render.render(write_still=True);result['render_seconds']=time.time()-t;(O/'audit.json').write_text(json.dumps(result,indent=2))
