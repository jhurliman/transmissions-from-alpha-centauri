import bpy,json,sys
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/city-transition-133'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-131/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_compositing=False
for ls in s.view_layers[0].freestyle_settings.linesets:ls.show_render=True
from city_transition_133 import apply
a=apply(s);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'after.png');bpy.ops.render.render(write_still=True)
