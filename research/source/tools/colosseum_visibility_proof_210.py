import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from colosseum_scale_210 import guards
O=R/'art/studies/colosseum-scale-210/70'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;guards(s,False)
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=590/1920;s.render.border_max_x=1360/1920;s.render.border_min_y=1-675/1442;s.render.border_max_y=1
s.render.filepath=str(O/'visibility-proof.png');start=time.time();bpy.ops.render.render(write_still=True)
print('VISIBILITY_PROOF_DONE',time.time()-start,flush=True)
