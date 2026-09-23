import bpy,json,sys,time
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-149/geometry';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-148/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1925/3840;s.render.border_max_x=2080/3840;s.render.border_min_y=1-590/2885;s.render.border_max_y=1-435/2885
s.render.filepath=str(O/'before.png');bpy.ops.render.render(write_still=True)
from coliseum_crown_loss_149 import apply
C=bpy.data.collections['110 Coliseum detailed front ruin'];a=apply(C);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'after.png');bpy.ops.render.render(write_still=True)
