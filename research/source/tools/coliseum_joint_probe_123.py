import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-123/joints';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-122/scene.blend'));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.425;s.render.border_max_x=.565;s.render.border_min_y=.69;s.render.border_max_y=.82
s.render.use_freestyle=False;s.render.filepath=str(O/'contact-only.png');bpy.ops.render.render(write_still=True)
g=bpy.data.objects.get('110 Landmark contact ink')
if g:g.hide_render=True
s.render.use_freestyle=True;s.render.filepath=str(O/'freestyle-only.png');bpy.ops.render.render(write_still=True)
(O/'crop.json').write_text(json.dumps({'resolution':[3840,2885],'border':[.425,.565,.69,.82]},indent=2))
