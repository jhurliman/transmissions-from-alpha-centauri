import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/lines-095';sys.path.insert(0,str(R/'tools'))
from intersection_details_current_095 import add_selected_rock_contacts,add_selected_weathering_boundaries
bpy.ops.wm.open_mainfile(filepath=str(O/'scene-structural.blend'));s=bpy.context.scene
old=[(o,o.lineart.usage) for o in bpy.data.objects if hasattr(o,'lineart')];counts={}
for fn,px in [(add_selected_rock_contacts,.6),(add_selected_weathering_boundaries,.45)]:
 ob,n=fn();counts[ob.name]=n
 for frame in ob.data.layers[0].frames:
  for st in frame.drawing.strokes:
   for p in st.points:
    pos=Vector(p.position);a=world_to_camera_view(s,s.camera,pos);b=world_to_camera_view(s,s.camera,pos+s.camera.matrix_world.to_quaternion()@Vector((1,0,0)));p.radius=px/max(abs(b.x-a.x)*s.render.resolution_x,1)
for o,usage in old:o.lineart.usage=usage
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_border=False;s.render.resolution_percentage=100;s.render.use_freestyle=True
(O/'expanded-audit.json').write_text(json.dumps(counts,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene-expanded.blend'))
if '--render' in sys.argv:
 s.render.filepath=str(O/'main-expanded.png');bpy.ops.render.render(write_still=True)
