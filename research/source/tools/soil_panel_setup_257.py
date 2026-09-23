import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/soil-panel-257'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/gallery-sills-256/scene.blend'));s=bpy.context.scene
from soil_panel_257 import apply
(O/'audit.json').write_text(json.dumps(apply(s),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.use_freestyle=False;s.render.use_compositing=False
for vl in s.view_layers:vl.use=vl.name=='ViewLayer'
s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=2700/3840;s.render.border_max_x=3500/3840;s.render.border_min_y=1-1910/2885;s.render.border_max_y=1-1500/2885
s.eevee.taa_render_samples=32;s.eevee.shadow_pool_size='1024'
