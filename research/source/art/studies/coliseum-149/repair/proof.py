import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_149 import apply
O=R/'art/studies/coliseum-149/repair';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-148/scene.blend'));s=bpy.context.scene;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.resolution_percentage=100;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1925/3840;s.render.border_max_x=2080/3840;s.render.border_min_y=1-590/2885;s.render.border_max_y=1-435/2885;s.render.threads_mode='FIXED';s.render.threads=3
s.render.filepath=str(O/'before.png');bpy.ops.render.render(write_still=True);C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library);d=apply(C);s.render.filepath=str(O/'after.png');bpy.ops.render.render(write_still=True);(O/'proof-audit.json').write_text(json.dumps(d,indent=2))
