import bpy
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/lines-095';bpy.ops.wm.open_mainfile(filepath=str(O/'scene-structural.blend'));s=bpy.context.scene;o=bpy.data.objects['095 Structural intersection ink']
# Maintain camera-scale ink thickness rather than a vanishing fixed world width.
for f in o.data.layers[0].frames:
 for st in f.drawing.strokes:
  for p in st.points:
   pos=Vector(p.position);a=world_to_camera_view(s,s.camera,pos);b=world_to_camera_view(s,s.camera,pos+s.camera.matrix_world.to_quaternion()@Vector((1,0,0)));ppm=abs(b.x-a.x)*s.render.resolution_x
   p.radius=.8/max(ppm,1)
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.69;s.render.border_max_x=.79;s.render.border_min_y=.43;s.render.border_max_y=.53;s.render.resolution_percentage=100
for key in ['before','after']:
 o.hide_render=key=='before';s.render.filepath=str(O/f'tune-{key}.png');bpy.ops.render.render(write_still=True)
o.hide_render=False;s.render.use_freestyle=True;s.render.use_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene-structural.blend'))
