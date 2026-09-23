import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_frame_extension_131 import apply
O=R/'art/studies/coliseum-131/frame';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-130/scene.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));s=bpy.context.scene;s.render.use_freestyle=False
for o in s.objects:
 if o.type=='GREASEPENCIL' and 'Landmark' in o.name:o.hide_render=True
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=2040/3840;s.render.border_max_x=2180/3840;s.render.border_min_y=1-575/2885;s.render.border_max_y=1-355/2885;s.render.filepath=str(O/'main-crop.png');bpy.ops.render.render(write_still=True)
