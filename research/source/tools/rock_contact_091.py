import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/rocks-091';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.get('scatter_zone')=='bank':
  v=ob.data.vertices;w=max(a.co.x for a in v)-min(a.co.x for a in v);h=max(a.co.z for a in v)-min(a.co.z for a in v)
  if w>.38:ob.location.z-=h*.19
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_freestyle=True;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.03;s.render.border_max_x=.43;s.render.border_min_y=.15;s.render.border_max_y=.51;s.render.filepath=str(O/'detail.png');bpy.ops.render.render(write_still=True)
