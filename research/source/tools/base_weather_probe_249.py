import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/base-weather-249'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ruin-ink-248/scene.blend'));s=bpy.context.scene
from step_weather_249 import apply
apply(s)
if (R/'tools/column_weather_249.py').exists():
 from column_weather_249 import apply as column
 column(s)
s.render.use_freestyle=False;s.render.use_compositing=False
for vl in s.view_layers:vl.use=vl.name=='ViewLayer'
s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=1600/3840;s.render.border_max_x=2250/3840;s.render.border_min_y=1-1200/2885;s.render.border_max_y=1-860/2885
s.eevee.taa_render_samples=32;s.eevee.shadow_pool_size='1024';s.render.filepath=str(O/'probe.png');bpy.ops.render.render(write_still=True)
