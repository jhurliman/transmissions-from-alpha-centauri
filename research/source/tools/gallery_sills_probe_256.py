import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/gallery-sills-256'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/gallery-sills-256/scene.blend'));s=bpy.context.scene
s.render.use_freestyle=False;s.render.use_compositing=False
for vl in s.view_layers:vl.use=vl.name=='ViewLayer'
s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=2710/3840;s.render.border_max_x=3260/3840;s.render.border_min_y=1-1200/2885;s.render.border_max_y=1-40/2885
s.eevee.taa_render_samples=32;s.eevee.shadow_pool_size='1024';s.render.filepath=str(O/'probe.png');bpy.ops.render.render(write_still=True)
