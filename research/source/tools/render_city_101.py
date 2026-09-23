import bpy,sys,os,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));V=os.environ.get('CITY_VARIANT','A');O=R/'art/studies/city-101'/V
bpy.ops.wm.open_mainfile(filepath=str(O/'placement.blend'));s=bpy.context.scene
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
ink=add_intersection_ink(bpy.data.collections['101 Original city layout study'],'101 '+V+' city contacts',radius=.004)
n=bake_intersection_ink(ink);right=s.camera.matrix_world.to_quaternion()@Vector((1,0,0))
for f in ink.data.layers[0].frames:
 for st in f.drawing.strokes:
  for p in st.points:
   a=world_to_camera_view(s,s.camera,Vector(p.position));b=world_to_camera_view(s,s.camera,Vector(p.position)+right);p.radius=.6/max(abs(b.x-a.x)*s.render.resolution_x,1)
from filter_city_101 import apply
filtered=apply(s)
(O/'ink.json').write_text(json.dumps({'new_city_strokes':n,'filtered_city_only_strokes':filtered,'near_ink':'preserved, old y>42 city strokes removed'},indent=2))
s.render.use_freestyle=True;s.render.resolution_percentage=100;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));
if os.environ.get('CITY_BAKE_ONLY')!='1':bpy.ops.render.render(write_still=True)
