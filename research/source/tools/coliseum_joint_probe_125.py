import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-125/joints';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-124/B/scene.blend'));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.425;s.render.border_max_x=.565;s.render.border_min_y=.69;s.render.border_max_y=.82
for ob in s.objects:
 if ob.type=='GREASEPENCIL':ob.hide_render=True
s.render.filepath=str(O/'baseline-noink.png');bpy.ops.render.render(write_still=True)
lights=[]
for ob in s.objects:
 if ob.type=='LIGHT':lights.append({'name':ob.name,'use_shadow':ob.data.use_shadow});ob.data.use_shadow=False
s.render.filepath=str(O/'no-cast-shadow-noink.png');bpy.ops.render.render(write_still=True)
(O/'probe.json').write_text(json.dumps({'scope':'Unsaved causal light-shadow test only. No primary source or final light setting changed.','lights':lights},indent=2))
