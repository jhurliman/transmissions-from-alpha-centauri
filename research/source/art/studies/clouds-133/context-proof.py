import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from clouds_133 import apply
O=R/'art/studies/clouds-133';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-130/scene.blend'));s=bpy.context.scene;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.filepath=str(O/'before-context.png');bpy.ops.render.render(write_still=True);apply(s);s.render.filepath=str(O/'after-context.png');bpy.ops.render.render(write_still=True)
